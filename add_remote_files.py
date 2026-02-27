import requests
import os, json

token = os.environ["RDMTOK"]

url = "https://newdata.caltechlibrary.dev/"

headers = {
    "Authorization": "Bearer %s" % token,
    "Content-type": "application/json",
}

response = requests.get(
    "https://newdata.caltechlibrary.dev/api/records/4ky4q-r3b49", headers=headers
)

data = response.json()
data.pop("pids")
data["metadata"]["rights"][0].pop("icon")
data["metadata"]["rights"][0].pop("description")
data["metadata"]["rights"][0].pop("title")
data["metadata"]["rights"][0].pop("props")

result = requests.post(url + "/api/records", headers=headers, json=data)

idv = result.json()["id"]
publish_link = result.json()["links"]["publish"]

file_data = [
    {
        "key": "C5710A-00001Z-01_2018_08_01_00_44_16_VNIRcalib.tar",
        "size": 11408920576,
        "checksum": "md5:076029ee247300fb94a9c8a103f71003-2177",
        "transfer": {
            "type": "R",
            "url": "https://caltech2.osn.mghpcc.org/10.22002/h790j-6ar55/BA4A/VNIR/C5710A-00001Z-01_2018_08_01_00_44_16_VNIRcalib.tar",
        },
    },
]

result = requests.post(
    url + "/api/records/%s/draft/files" % idv, headers=headers, json=file_data
)

print(result.text)

result = requests.post(publish_link, json=data, headers=headers)
if result.status_code != 202:
    raise Exception(result.text)
