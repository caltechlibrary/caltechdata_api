import requests
import math
from progressbar import progressbar
from caltechdata_api import caltechdata_edit


def fix_name(metadata, fixed):
    for name in metadata:
        if name["nameType"] == "Personal":
            if "givenName" not in name:
                fixed = True
                given = name["name"].split(",")[1]
                name["givenName"] = given.strip()
    return metadata, fixed


url = 'https://data.caltech.edu/api/records?q=-metadata.related_identifiers.identifier%3A"10.25989%2Fes8t-kswe"'

headers = {
    "accept": "application/vnd.datacite.datacite+json",
}

response = requests.get(f"{url}&search_type=scan&scroll=5m")

total = response.json()["hits"]["total"]
pages = math.ceil(int(total) / 1000)
hits = []  # [{'id':'a7f64-a8k10'}]
print(total)
for c in progressbar(range(1, pages + 1)):
    chunkurl = f"{url}&sort=newest&size=1000&page={c}"
    response = requests.get(chunkurl)
    response = response.json()
    hits += response["hits"]["hits"]


url = 'https://data.caltech.edu/api/records'

for h in progressbar(hits):
    idv = str(h["id"])
    
    response = requests.get(f"{url}/{idv}", headers=headers)
    if response.status_code != 200:
        print(response.text)
        exit()
    else:
        fixed = False
        metadata = response.json()
        metadata["creators"], fixed = fix_name(metadata["creators"], fixed)
        if "contributors" in metadata:
            metadata["contributors"], fixed = fix_name(metadata["contributors"], fixed)
        if fixed:
            print(idv)
            caltechdata_edit(idv, metadata, production=True, publish=True)
