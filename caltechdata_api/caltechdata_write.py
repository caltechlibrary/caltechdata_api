import copy
import json
import os, requests

import s3fs
from requests import session
from json.decoder import JSONDecodeError

from caltechdata_api import customize_schema


def write_files_rdm(files, file_link, headers, f_headers, s3=None):
    f_json = []
    f_list = {}
    for f in files:
        filename = f.split("/")[-1]
        f_json.append({"key": filename})
        f_list[filename] = f
    result = requests.post(file_link, headers=headers, json=f_json)
    if result.status_code != 201:
        raise Exception(result.text)
    # Now we have the upload links
    for entry in result.json()["entries"]:
        link = entry["links"]["content"]
        commit = entry["links"]["commit"]
        name = entry["key"]
        if s3:
            infile = s3.open(f_list[name], "rb")
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


def add_file_links(metadata, file_links):
    # Currently configured for OSN S3 links
    link_string = ""
    endpoint = "https://renc.osn.xsede.org/"
    s3 = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint})
    for link in file_links:
        file = link.split("/")[-1]
        path = link.split(endpoint)[1]
        try:
            size = s3.info(path)["Size"]
            size = round(size / 1024.0 / 1024.0 / 1024.0, 2)
        except:
            size = 0
        if link_string == "":
            cleaned = link.strip(file)
            link_string = f"Files available via S3 at {cleaned}&lt;/p&gt;</p>"
        link_string += f"""{file} {size} GB 
        <p>&lt;a role="button" class="ui compact mini button" href="{link}"
        &gt; &lt;i class="download icon"&gt;&lt;/i&gt; Download &lt;/a&gt;</p>&lt;/p&gt;</p>
        """

    description = {"description": link_string, "descriptionType": "Other"}
    metadata["descriptions"].append(description)
    return metadata


def send_to_community(review_link, data, headers, publish, community):

    data = {
        "receiver": {"community": community},
        "type": "community-submission",
    }
    result = requests.put(review_link, json=data, headers=headers)
    if result.status_code != 200:
        raise Exception(result.text)
    submit_link = result.json()["links"]["actions"]["submit"]
    data = comment = {
        "payload": {
            "content": "This record is submitted automatically with the CaltechDATA API",
            "format": "html",
        }
    }
    result = requests.post(submit_link, json=data, headers=headers)
    if result.status_code != 200:
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
):
    """
    File links are links to files existing in external systems that will
    be added directly in a CaltechDATA record, instead of uploading the file.

    S3 is a s3sf object for directly opening files
    """
    # If no token is provided, get from RDMTOK environment variable
    if not token:
        token = os.environ["RDMTOK"]

    # If files is a string - change to single value array
    if isinstance(files, str) == True:
        files = [files]

    if file_links:
        metadata = add_file_links(metadata, file_links)

    data = customize_schema.customize_schema(copy.deepcopy(metadata), schema=schema)
    if production == True:
        url = "https://data.caltech.edu/"
    else:
        url = "https://data.caltechlibrary.dev/"

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
    else:
        if "README.txt" in files:
            data["files"] = {"default_preview": "README.txt"}

    # Make draft and publish
    result = requests.post(
        url + "/api/records", headers=headers, json=data
    )
    if result.status_code != 201:
        raise Exception(result.text)
    idv = result.json()["id"]
    publish_link = result.json()["links"]["publish"]

    if files:
        file_link = result.json()["links"]["files"]
        write_files_rdm(files, file_link, headers, f_headers, s3)

    if community:
        review_link = result.json()["links"]["review"]
        send_to_community(review_link, data, headers, publish, community)

    else:
        if publish:
            result = requests.post(publish_link, headers=headers)
            if result.status_code != 202:
                raise Exception(result.text)
    return idv
