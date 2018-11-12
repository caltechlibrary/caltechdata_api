import argparse, os, json
from datacite import DataCiteMDSClient,schema40
from caltechdata_api import caltechdata_write

parser = argparse.ArgumentParser(description=\
        "Write files and a DataCite 4 standard json record\
        to CaltechDATA repository")
parser.add_argument('json_file', nargs=1, help=\
            'file name for json DataCite metadata file')
parser.add_argument('-ids', nargs='*', help='CaltechDATA IDs')
parser.add_argument('-fnames', nargs='*', help='New Files')
args = parser.parse_args()

#Get access token from TIND sed as environment variable with source token.bash
token = os.environ['TINDTOK']

metaf = open(args.json_file[0], 'r')
metadata = json.load(metaf)

production = True

response = caltechdata_write(metadata, token, args.fnames, production)
print(response)

#If needed - write out datacite XML

xml = schema40.tostring(metadata)

outname = 'datacite.xml'
outfile = open(outname,'w',encoding='utf8')
outfile.write(xml)

