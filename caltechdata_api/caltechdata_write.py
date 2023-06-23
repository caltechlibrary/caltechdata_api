import copy
import json
import os, requests

import s3fs
from requests import session
from json.decoder import JSONDecodeError
from caltechdata_api import customize_schema
from caltechdata_api.utils import humanbytes


def write_files_rdm(files, file_link, headers, f_headers, s3=None):
    f_json = []
    f_list = {}
    fnames = []
    for f in files:
        split = f.split("/")
        filename = split[-1]
        if filename in fnames:
            # We can't have a duplicate filename
            # Assume that the previous path value makes a unique name
            filename = f"{split[-2]}-{split[-1]}"
        fnames.append(filename)
        f_json.append({"key": filename})
        f_list[filename] = f
    # Now we see if any existing draft files need to be replaced
    result = requests.get(file_link, headers=f_headers)
    if result.status_code == 200:
        ex_files = result.json()["entries"]
        for ex in ex_files:
            if ex["key"] in f_list:
                result = requests.delete(ex["links"]["self"], headers=f_headers)
                if result.status_code != 204:
                    raise Exception(result.text)
    # Create new file upload links
    result = requests.post(file_link, headers=headers, json=f_json)
    if result.status_code != 201:
        raise Exception(result.text)
    # Now we have the upload links
    for entry in result.json()["entries"]:
        self = entry["links"]["self"]
        link = entry["links"]["content"]
        commit = entry["links"]["commit"]
        name = entry["key"]
        if name in f_list:
            if s3:
                print("Downloading", f_list[name])
                s3.download(f_list[name], name)
                infile = open(name, "rb")
            else:
                infile = open(f_list[name], "rb")
            # size = infile.seek(0, 2)
            # infile.seek(0, 0)  # reset at beginning
            result = requests.put(link, headers=f_headers, data=infile)
            if result.status_code != 200:
                raise Exception(result.text)
            result = requests.post(commit, headers=headers)
            if result.status_code != 200:
                raise Exception(result.text)
        else:
            # Delete any files not included in this write command
            result = requests.delete(self, headers=f_headers)
            if result.status_code != 204:
                raise Exception(result.text)


def add_file_links(
    metadata, file_links, file_descriptions=[], additional_descriptions="", s3_link=None
):
    # Currently configured for OSN S3 links
    link_string = ""
    endpoint = "https://renc.osn.xsede.org/"
    s3 = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint})
    index = 0
    for link in file_links:
        file = link.split("/")[-1]
        path = link.split(endpoint)[1]
        size = s3.info(path)["size"]
        size = humanbytes(size)
        try:
            desc = file_descriptions[index] + ","
        except IndexError:
            desc = ""
        if link_string == "":
            if s3_link:
                link_string = f"Files available via S3 at {s3_link}&lt;/p&gt;</p>"
            else:
                cleaned = link.strip(file)
                link_string = f"Files available via S3 at {cleaned}&lt;/p&gt;</p>"
        link_string += f"""{file}, {desc} {size}  
        <p>&lt;a role="button" class="ui compact mini button" href="{link}"
        &gt; &lt;i class="download icon"&gt;&lt;/i&gt; Download &lt;/a&gt;</p>&lt;/p&gt;</p>
        """
        index += 1
    # Tack on any additional descriptions
    if additional_descriptions != "":
        link_string += additional_descriptions

    description = {"description": link_string, "descriptionType": "files"}
    metadata["descriptions"].append(description)
    return metadata


def send_to_community(review_link, data, headers, publish, community, message=None):

    if not message:
        message = "This record is submitted automatically with the CaltechDATA API"

    data = {
        "receiver": {"community": community},
        "type": "community-submission",
    }
    result = requests.put(review_link, json=data, headers=headers)
    if result.status_code != 200:
        raise Exception(result.text)
    submit_link = review_link.replace('/review','/actions/submit-review')
    data = comment = {
        "payload": {
            "content": message,
            "format": "html",
        }
    }
    result = requests.post(submit_link, json=data, headers=headers)
    if result.status_code != 202:
        raise Exception(result.text)
    if publish:
        accept_link = result.json()["links"]["actions"]["accept"]
        data = comment = {
            "payload": {
                "content": "This record is accepted automatically with the CaltechDATA API",
                "format": "html",
            }
        }
        result = requests.post(accept_link, json=data, headers=headers)
        if result.status_code != 200:
            raise Exception(result.text)
    return result


def caltechdata_write(
    metadata,
    token=None,
    files=[],
    production=False,
    schema="43",
    publish=False,
    file_links=[],
    s3=None,
    community=None,
    authors=False,
    file_descriptions=[],
    s3_link=None,
    default_preview=None,
    review_message=None,
):
    """
    File links are links to files existing in external systems that will
    be added directly in a CaltechDATA record, instead of uploading the file.

    S3 is a s3sf object for directly opening files
    """
    # Make a copy so that none of our changes leak out
    metadata = copy.deepcopy(metadata)

    # If no token is provided, get from RDMTOK environment variable
    if not token:
        token = os.environ["RDMTOK"]

    # If files is a string - change to single value array
    if isinstance(files, str) == True:
        files = [files]

    if file_links:
        metadata = add_file_links(
            metadata, file_links, file_descriptions, s3_link=s3_link
        )

    # Pull out pid information
    if production == True:
        repo_prefix = "10.22002"
    else:
        repo_prefix = "10.33569"
    pids = {}
    identifiers = []
    if "metadata" in metadata:
        # we have rdm schema
        if "identifiers" in metadata["metadata"]:
            identifiers = metadata["metadata"]["identifiers"]
    elif "identifiers" in metadata:
        identifiers = metadata["identifiers"]
    for identifier in identifiers:
        if "identifierType" in identifier:
            if identifier["identifierType"] == "DOI":
                doi = identifier["identifier"]
                prefix = doi.split("/")[0]
            elif identifier["identifierType"] == "oai":
                pids["oai"] = {
                    "identifier": identifier["identifier"],
                    "provider": "oai",
                }
            else:
                doi = False
        elif "scheme" in identifier:
            # We have RDM internal metadata
            if identifier["scheme"] == "doi":
                doi = identifier["identifier"]
                prefix = doi.split("/")[0]
            else:
                doi = False
        else:
            doi = False
        if doi != False:
            if prefix == repo_prefix:
                pids["doi"] = {
                    "identifier": doi,
                    "provider": "datacite",
                    "client": "datacite",
                }
            else:
                pids["doi"] = {
                    "identifier": doi,
                    "provider": "external",
                }

    if "pids" not in metadata:
        metadata["pids"] = pids

    if authors == False:
        data = customize_schema.customize_schema(metadata, schema=schema)
        if production == True:
            url = "https://data.caltech.edu/"
        else:
            url = "https://data.caltechlibrary.dev/"
    else:
        data = metadata
        if production == True:
            url = "https://authors.caltech.edu/"
        else:
            url = "https://authors.caltechlibrary.dev/"

    headers = {
        "Authorization": "Bearer %s" % token,
        "Content-type": "application/json",
    }
    f_headers = {
        "Authorization": "Bearer %s" % token,
        "Content-type": "application/octet-stream",
    }

    if not files:
        data["files"] = {"enabled": False}
    elif default_preview:
        data["files"] = {"enabled": True, "default_preview": default_preview}

    # Make draft and publish
    result = requests.post(url + "/api/records", headers=headers, json=data)
    if result.status_code != 201:
        raise Exception(result.text)
    idv = result.json()["id"]
    publish_link = result.json()["links"]["publish"]

    if files:
        file_link = result.json()["links"]["files"]
        write_files_rdm(files, file_link, headers, f_headers, s3)

    if community:
        review_link = result.json()["links"]["review"]
        send_to_community(
            review_link, data, headers, publish, community, review_message
        )

    else:
        if publish:
            result = requests.post(publish_link, json=data, headers=headers)
            if result.status_code != 202:
                raise Exception(result.text)
    return idv
