import requests
import math
from progressbar import progressbar

url = "https://data.caltech.edu/api/records"

headers = {
            "accept": "application/vnd.datacite.datacite+json",
        }

response = requests.get(f"{url}")

total = response.json()["hits"]["total"]
pages = math.ceil(int(total) / 1000)
hits = []
print(total)
for c in progressbar(range(1,2)):#, pages + 1)):
    chunkurl = (
            f"{url}?&sort=newest&size=1000&page={c}"
    )
    response = requests.get(chunkurl).json()
    
    hits += response["hits"]["hits"]

for h in progressbar(hits):
    rid = str(h["id"])
    print(rid)
