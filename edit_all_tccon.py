import argparse, os, json, requests
from caltechdata_api import caltechdata_edit, decustomize_schema

# Get access token from TIND sed as environment variable with source token.bash
token = os.environ["TINDTOK"]

production = True

if production == True:
    url = "https://data.caltech.edu/api/records"
else:
    url = "https://cd-sandbox.tind.io/api/records"

response = requests.get(url + "/?size=1000&q=subjects:TCCON")
hits = response.json()

wiki1 = "https://tccon-wiki.caltech.edu/Network_Policy/Data_Use_Policy/Data_Description"
new1 = "https://tccon-wiki.caltech.edu/Main/DataDescription"
wiki2 = "https://tccon-wiki.caltech.edu/Sites"
new2 = "https://tccon-wiki.caltech.edu/Main/TCCONSites"
site = "http://tccondata.org/"
new3 = "https://tccondata.org"
exsite = "http://tccondata.org"

for h in hits["hits"]["hits"]:
    rid = h["id"]
    print(rid)
    record = decustomize_schema(h["metadata"], True)
    updated = {}
    if "relatedIdentifiers" in record:
        for related in record["relatedIdentifiers"]:
            if related["relatedIdentifier"] == wiki1:
                related["relatedIdentifier"] = new1
            if related["relatedIdentifier"] == wiki2:
                related["relatedIdentifier"] = new2
            if related["relatedIdentifier"] == site:
                related["relatedIdentifier"] = new3
            if related["relatedIdentifier"] == exsite:
                related["relatedIdentifier"] = new3
        updated["relatedIdentifiers"] = record["relatedIdentifiers"]
    response = caltechdata_edit(rid, updated, token, {}, {}, production)
    print(response)
