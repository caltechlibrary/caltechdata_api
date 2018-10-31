import argparse, os, json
from caltechdata_api import caltechdata_edit

parser = argparse.ArgumentParser(description=\
        "Write files and a DataCite 4 standard json record\
        to CaltechDATA repository")
parser.add_argument('-ids', nargs='*', help='CaltechDATA IDs')
parser.add_argument('-fnames', nargs='*', help='New Files')
parser.add_argument('-delete', nargs='*', help='Files To Delete')
args = parser.parse_args()

#Get access token from TIND sed as environment variable with source token.bash
token = os.environ['TINDTOK']

production = True

print(args.delete)

response = caltechdata_edit(token, args.ids, {}, args.fnames, args.delete, production)
print(response)
