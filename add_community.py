import requests, os
from caltechdata_api import get_metadata, caltechdata_edit

token = os.getenv("RDMTOK")

community = "9b91e752-8db6-49e9-8311-6dd6bd4a3064"

completed = []
infile = "completed.txt"
with open(infile, "r") as f:
    for line in f:
        completed.append(line.strip())
outfile = open(infile, "a")

response = requests.get(
    "https://data.caltech.edu/api/records?q=metadata.subjects.subject:thesis AND metadata.subjects.subject:gps&allversions=true&size=1000"
)
records = response.json()
for record in records["hits"]["hits"]:
    recid = record["id"]
    if recid not in completed:
        print(recid)
        metadata = get_metadata(recid)
        caltechdata_edit(recid, metadata, token, production=True, community=community)
        outfile.write(recid + "\n")
