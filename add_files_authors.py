import requests, os
from caltechdata_api import write_files_rdm

idv = "tv53y-rqh37"
files = ["1-s2.0-S2590162125000620-main.pdf"]
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
