import os, requests, json, math
from caltechdata_api import get_metadata, caltechdata_edit

token = os.environ["RDMTOK"]

url = "https://data.caltech.edu/api/records"
query = '?q=metadata.additional_descriptions.description:"renc.osn.xsede.org"&allversions=true'

headers = {
    "Authorization": "Bearer %s" % token,
    "Content-type": "application/json",
}

url = url + query
response = requests.get(url, headers=headers)
total = response.json()["hits"]["total"]
pages = math.ceil(int(total) / 10)
for c in range(1, pages + 1):
    chunkurl = f"{url}&size=10&page={c}"
    response = requests.get(chunkurl, headers=headers).json()
    for hit in response["hits"]["hits"]:
        idv = hit["id"]
        print(idv)
        metadata = get_metadata(idv, token=token, validate=False)
        for desc in metadata["descriptions"]:
            desc["description"] = desc["description"].replace(
                "renc.osn.xsede.org",
                "sdsc.osn.xsede.org",
            )
        caltechdata_edit(idv, metadata, token=token, production=True, publish=True)
