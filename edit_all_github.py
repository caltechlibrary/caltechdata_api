import argparse, os, json, requests
from caltechdata_api import caltechdata_edit, decustomize_schema

#Get access token from TIND sed as environment variable with source token.bash
token = os.environ['TINDTOK']

production = True

if production == True:
    url = 'https://data.caltech.edu/api/records'
else:
    url = 'https://cd-sandbox.tind.io/api/records'

response = requests.get(url+'/?size=2000&q=cal_resource_type=software')
hits = response.json()

for h in hits['hits']['hits']:
        rid = h['id']
        print(rid)
        record = decustomize_schema(h['metadata'],True)
        replace = False
        #to_update =\
                #[288,269,295,291,279,284,266,281,286,278,280,293,283,287,210,274,276,290,300,285,270,268,267,302,744,282,272,289]
        #if rid in to_update:
        # Find just GitHub records by title
        if '/' in record['titles'][0]['title']:
            add = True
            for s in record['subjects']:
                subject = s['subject']
                if subject == 'Github':
                    add = False
                if subject == 'GitHub':
                    add = False
                if subject == 'Bitbucket':
                    add = False
            if add == True:
                record['subjects'].append({'subject':'GitHub'})
                print( record['titles'][0]['title'])
                response = caltechdata_edit(token, rid, record, {}, {}, production)
                print(response)
