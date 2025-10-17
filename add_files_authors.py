import requests, os, argparse
from caltechdata_api import write_files_rdm

parser = argparse.ArgumentParser(
    description="Add files to an existing CaltechAUTHORS record."
)
parser.add_argument(
    "idv",
    type=str,
    help="The CaltechAUTHORS record idv to edit.",
)
parser.add_argument(
    "files",
    type=str,
    nargs="+",
    help="The files to upload to the record.",
)
args = parser.parse_args()
idv = args.idv
files = args.files
token = os.environ["RDMTOK"]
url = "https://authors.library.caltech.edu"

headers = {
    "Authorization": "Bearer %s" % token,
    "Content-type": "application/json",
}
f_headers = {
    "Authorization": "Bearer %s" % token,
    "Content-type": "application/octet-stream",
}

existing = requests.get(
    url + "/api/records/" + idv + "/draft",
    headers=headers,
)
if existing.status_code != 200:
    raise Exception(f"Record {idv} does not exist, cannot edit")
data = existing.json()
data["files"] = {"enabled": True}
# Update metadata
result = requests.put(
    url + "/api/records/" + idv + "/draft",
    headers=headers,
    json=data,
)
if result.status_code != 200:
    raise Exception(result.text)
file_link = result.json()["links"]["files"]
write_files_rdm(files, file_link, headers, f_headers)
