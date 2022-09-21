import sys, os, json, requests
from caltechdata_api import caltechdata_edit, decustomize_schema

# USAGE: python edit_tccon.py tccon.ggg2014.darwin01.R0.json 269 0 griffith@uow.edu.au

# Get access token from TIND sed as environment variable with source token.bash
token = os.environ["TINDTOK"]

production = True

if production == True:
    url = "https://data.caltech.edu/api/records"
else:
    url = "https://cd-sandbox.tind.io/api/records"

response = requests.get(url + "/?size=1000&q=subjects:TCCON")
hits = response.json()

infile = open(sys.argv[1], "r")
record = json.load(infile)

rid = sys.argv[2]

group = {"contributorName": "TCCON", "contributorType": "ResearchGroup"}
new = ""
for c in record["contributors"]:
    print(c["contributorType"])
    if c["contributorType"] == "HostingInstitution":
        print("YES")
        c["contributorName"] = "California Institute of Techonolgy, Pasadena, CA (US)"
        c["nameIdentifiers"] = [
            {"nameIdentifier": "grid.20861.3d", "nameIdentifierScheme": "GRID"}
        ]
v = record["contributors"]
v.append(group)
contact = record["creators"][int(sys.argv[3])]
contact["contributorName"] = contact.pop("creatorName")
contact["contributorEmail"] = sys.argv[4]
contact["contributorType"] = "ContactPerson"
v.append(contact)
new = {"contributors": v}
print(new)
response = caltechdata_edit(token, rid, new, {}, {}, production)
print(response)
