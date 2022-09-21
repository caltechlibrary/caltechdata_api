import os, json
from requests import session
from caltechdata_api import customize_schema

# fileinfo = [  {"url": , "filename": filename, "md5": md5, "size": size}]

token = os.environ["TINDTOK"]

metaf = open("test_file.json", "r")
metadata = json.load(metaf)

url = "https://cd-sandbox.tind.io/submit/api/create/"

headers = {"Authorization": "Bearer %s" % token, "Content-type": "application/json"}

newdata = customize_schema(metadata)
#    if "doi" not in newdata:
#        # We want tind to generate the identifier
#        newdata["final_actions"] = [
#            {"type": "create_doi", "parameters": {"type": "records", "field": "doi"}}
#        ]

dat = json.dumps({"record": newdata})

c = session()
response = c.post(url, headers=headers, data=dat)
print(response.text)
