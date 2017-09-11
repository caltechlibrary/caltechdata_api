import argparse, os, json
from caltechdata_write import Caltechdata_edit

parser = argparse.ArgumentParser(description=\
        "Write files and a DataCite 4 standard json record\
        to CaltechDATA repository")
parser.add_argument('json_file',nargs=1, help=\
            'file name for json DataCite metadata file')
parser.add_argument('-ids',nargs='+', help='CaltechDATA IDs')
args = parser.parse_args()

#Get access token from TIND sed as environment variable with source token.bash
token = os.environ['TINDTOK']

metaf = open(args.json_file[0],'r')
metadata = json.load(metaf)

Caltechdata_edit(metadata,token,args.ids)
