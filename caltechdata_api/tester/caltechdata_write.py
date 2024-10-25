import copy
import json
import os
import requests
import s3fs
from requests import session
from json.decoder import JSONDecodeError
from caltechdata_api import customize_schema
from caltechdata_api.utils import humanbytes


def write_files_rdm(files, file_link, headers, f_headers, s3=None, keepfiles=False):
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
            result = requests.put(link, headers=f_headers, data=infile)
            if result.status_code != 200:
                raise Exception(result.text)
            result = requests.post(commit, headers=headers)
            if result.status_code != 200:
                raise Exception(result.text)
        else:
            # Delete any files not included in this write command
            if keepfiles == False:
                result = requests.delete(self, headers=f_headers)
                if result.status_code != 204:
                    raise Exception(result.text)


def add_file_links(
    metadata, file_links, file_descriptions=[], additional_descriptions="", s3_link=None
):
    # Currently configured for S3 links, assuming all are at the same endpoint
    link_string = ""
    endpoint = "https://" + file_links[0].split("/")[2]
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
    submit_link = review_link.replace("/review", "/actions/submit-review")
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

def caltechdata_write(metadata, token=None, files=[], production=False, schema="43", publish=False, file_links=[],
                      s3=None, community=None, authors=False, file_descriptions=[], s3_link=None,
                      default_preview=None, review_message=None):
    metadata = copy.deepcopy(metadata)

    if not token:
        token = os.environ["RDMTOK"]

    if isinstance(files, str):
        files = [files]

    if file_links:
        metadata = add_file_links(metadata, file_links, file_descriptions, s3_link=s3_link)

    url = "https://data.caltech.edu/" if production else "https://data.caltechlibrary.dev/"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-type": "application/json",
    }
    f_headers = {
        "Authorization": f"Bearer {token}",
        "Content-type": "application/octet-stream",
    }

    if not files:
        metadata["files"] = {"enabled": False}

    result = requests.post(f"{url}api/records", headers=headers, json=metadata)
    if result.status_code != 201:
        raise Exception(result.text)

    idv = result.json()["id"]
    record_url = f"{url}records/{idv}"

    if files:
        file_link = result.json()["links"]["files"]
        write_files_rdm(files, file_link, headers, f_headers, s3)

    if community:
        review_link = result.json()["links"]["review"]
        send_to_community(review_link, metadata, headers, publish, community, review_message)
    elif publish:
        publish_link = result.json()["links"]["publish"]
        result = requests.post(publish_link, json=metadata, headers=headers)
        if result.status_code != 202:
            raise Exception(result.text)

    return record_url


def main():
    parser = argparse.ArgumentParser(description="Upload files to CaltechDATA with metadata")
    parser.add_argument("--metadata", required=True, type=str, help="Path to JSON file with metadata")
    parser.add_argument("--token", default=os.environ.get("RDMTOK"), type=str, help="API token for authentication (defaults to RDMTOK environment variable)")
    parser.add_argument("--files", nargs="*", default=[], help="List of file paths to upload (default: empty list)")
    parser.add_argument("--production", action="store_true", help="Use production environment (default: False)")
    parser.add_argument("--schema", default="43", help="Metadata schema version (default: '43')")
    parser.add_argument("--publish", action="store_true", help="Publish the record after upload (default: False)")
    parser.add_argument("--file_links", nargs="*", default=[], help="List of file links to add (default: empty list)")
    parser.add_argument("--community", type=str, default=None, help="Community ID for submission (default: None)")
    parser.add_argument("--file_descriptions", nargs="*", default=[], help="Descriptions for each file link (default: empty list)")
    parser.add_argument("--s3_link", type=str, default=None, help="Link to S3 bucket (default: None)")
    parser.add_argument("--review_message", type=str, default="This record is submitted automatically with the CaltechDATA API", help="Message for review process (default message)")

    args = parser.parse_args()

    with open(args.metadata, "r") as f:
        metadata = json.load(f)

    record_url = caltechdata_write(
        metadata=metadata,
        token=args.token,
        files=args.files,
        production=args.production,
        schema=args.schema,
        publish=args.publish,
        file_links=args.file_links,
        community=args.community,
        file_descriptions=args.file_descriptions,
        s3_link=args.s3_link,
        review_message=args.review_message,
    )

    print(f"Record created with URL: {record_url}")

if __name__ == "__main__":
    main()