import argparse, os, json
from datacite import DataCiteMDSClient, schema40
from caltechdata_api import caltechdata_write

parser = argparse.ArgumentParser(
    description="Write files and a DataCite 4 standard json record\
        to CaltechDATA repository"
)
parser.add_argument(
    "json_file", nargs=1, help="file name for json DataCite metadata file"
)
parser.add_argument("-ids", nargs="*", help="CaltechDATA IDs")
parser.add_argument("-fnames", nargs="*", help="New Files")
parser.add_argument("-schema", default="40", help="Metadata Schema")

args = parser.parse_args()

# Get access token as environment variable
token = os.environ["TINDTOK"]

metaf = open(args.json_file[0], "r")
metadata = json.load(metaf)

production = False

response = caltechdata_write(metadata, token, args.fnames, production, args.schema)
print(response)
