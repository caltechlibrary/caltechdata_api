import argparse, os, json, requests
from caltechdata_api import caltechdata_edit, decustomize_schema

#Get access token from TIND sed as environment variable with source token.bash
token = os.environ['TINDTOK']

production = True

if production == True:
    url = 'https://data.caltech.edu/api/records'
else:
    url = 'https://cd-sandbox.tind.io/api/records'

response = requests.get(url+'/?size=1000&q=subjects:TCCON')
hits = response.json()

for h in hits['hits']['hits']:
        rid = h['id']
        print(rid)
        record = decustomize_schema(h['metadata'],True)
        replace = False
        to_update =\
        [288,269,295,291,279,284,266,281,286,278,280,293,283,287,210,274,276,290,300,285,270,268,267,302,744,282,272,289]
        if rid in to_update:
            dates = []
            for d in record['dates']:
                if d['dateType']=='Issued':
                    d['dateType'] = 'Submitted'
                    dates.append(d)
                elif d['dateType']!='Submitted':
                    dates.append(d)
                else:
                    print("Duplicate ",d)
            metadata ={'dates':dates}
            print(metadata)
            response = caltechdata_edit(token, rid, metadata, {}, {}, production)
            print(response)
