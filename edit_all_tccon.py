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
        replace = False
        if 'relatedIdentifiers' in record:
            for r in record['relatedIdentifiers']:
                if r['relationType']=='IsPreviousVersionOf':
                    description = \
"<br> These data are now obsolete and should be replaced by the most recent data: https://doi.org/"\
                        +r['relatedIdentifier']+' <br><br>'
                    description = description +\
                    record['descriptions'][0]['description']
                    replace = True


        if replace == True:
            metadata =\
            {'descriptions':[{'description':description,'descriptionType':'Abstract'}]}
            response = caltechdata_edit(token, rid, metadata, {}, {}, production)
            print(response)
