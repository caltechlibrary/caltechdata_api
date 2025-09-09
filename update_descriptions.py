import os, requests, json, math
from caltechdata_api import get_metadata, caltechdata_edit

token = os.environ["RDMTOK"]

url = "https://data.caltech.edu/api/communities/0497183f-f3b1-483d-b8bb-133c731c939a/records"
query = "?q=NOT%20_exists_%3Ametadata.description&f=allversions:true"

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
        result = requests.post(
            "https://data.caltech.edu/api/records/" + idv + "/draft",
            headers=headers,
        )
        if result.status_code != 201:
            raise Exception(result.text)
        metadata = result.json()
        metadata["metadata"]["description"] = hit["metadata"]["title"]
        for desc in metadata["metadata"]["additional_descriptions"]:
            if "title" in desc["type"]:
                desc["type"].pop("title")
        for date in metadata["metadata"]["dates"]:
            if "title" in date["type"]:
                date["type"].pop("title")
        if "icon" in metadata["metadata"]["rights"][0]:
            metadata["metadata"]["rights"][0].pop("icon")
            metadata["metadata"]["rights"][0].pop("title")
            metadata["metadata"]["rights"][0].pop("description")
            metadata["metadata"]["rights"][0].pop("props")
        if "title" in metadata["metadata"]["languages"][0]:
            metadata["metadata"]["languages"][0].pop("title")
        if "title" in metadata["metadata"]["resource_type"]:
            metadata["metadata"]["resource_type"].pop("title")
        result = requests.put(
            "https://data.caltech.edu/api/records/" + idv + "/draft",
            headers=headers,
            json=metadata,
        )
        if result.status_code != 200:
            raise Exception(result.text)
        publish_link = (
            f"https://data.caltech.edu/api/records/{idv}/draft/actions/publish"
        )
        result = requests.post(publish_link, headers=headers)
        if result.status_code != 202:
            raise Exception(result.text)
