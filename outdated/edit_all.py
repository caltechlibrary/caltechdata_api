import argparse, os, json
from caltechdata_api import caltechdata_edit

parser = argparse.ArgumentParser(
    description="Write files and a DataCite 4 standard json record\
        to CaltechDATA repository"
)
parser.add_argument(
    "json_file", nargs=1, help="file name for json DataCite metadata file"
)
parser.add_argument("-fnames", nargs="*", help="New Files")
args = parser.parse_args()

# Get access token from TIND set as environment variable with source token.bash
token = os.environ["TINDTOK"]

metaf = open(args.json_file[0], "r")
metadata = json.load(metaf)

production = False

ids = range(1, 717)
response = caltechdata_edit(token, ids, metadata, args.fnames, {"pdf"}, production)
print(response)
