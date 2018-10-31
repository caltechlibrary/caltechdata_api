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
        rid = str(h['id'])
        print(rid)
        record = decustomize_schema(h['metadata'],True)

        group = {'contributorName':'TCCON','contributorType':'ResearchGroup'}
        new = ''
        if 'contributors' in record:
            existing = False
            for c in record['contributors']:
                if c['contributorName'] == 'TCCON':
                    existing = True
            if existing == False:        
                v = record['contributors']
                v.append(group)
                new = {'contributors':v}
        else:
            new = {'contributors':[group]}
        if new != '':
            response = caltechdata_edit(token, rid, new, {}, {}, production)
            print(response)
