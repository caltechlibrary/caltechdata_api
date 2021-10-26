import argparse, os, json, requests, csv, dataset
from caltechdata_api import caltechdata_edit, decustomize_schema

# Get access token from TIND sed as environment variable with source token.bash
token = os.environ["TINDTOK"]

collection = "data/CaltechTHESIS.ds"

production = True

if production == True:
    url = "https://data.caltech.edu/api/records"
else:
    url = "https://cd-sandbox.tind.io/api/records"

response = requests.get(url + "/?size=1000&q=subjects:gps")
hits = response.json()

# Set up dictionary of links between resolver and thesis IDs
available = os.path.isfile("data/record_list.csv")
if available == False:
    print("You need to run update_thesis_file.py")
    exit()
else:
    record_list = {}
    reader = csv.reader(open("data/record_list.csv"))
    for row in reader:
        record_list[row[1]] = row[0]

for h in hits["hits"]["hits"]:
    rid = str(h["id"])
    print(rid)
    record = decustomize_schema(h["metadata"], True)
    if "relatedIdentifiers" in record:
        for r in record["relatedIdentifiers"]:
            if (
                r["relationType"] == "IsSupplementTo"
                and r["relatedIdentifierType"] == "URL"
            ):
                idv = record_list[r["relatedIdentifier"]]
                thesis_metadata, err = dataset.read(collection, idv)
                pub_date = thesis_metadata["date"]
                dates = [{"date": pub_date, "dateType": "Issued"}]
                for date in record["dates"]:
                    if date["dateType"] == "Issued":
                        dates.append({"date": date["date"], "dateType": "Updated"})
                    elif date["dateType"] == "Updated":
                        pass
                    elif date["dateType"] != "Submitted":
                        dates.append(date)
                print(dates)
                metadata = {"dates": dates}
                response = caltechdata_edit(token, rid, metadata, {}, {}, production)
                print(response)
