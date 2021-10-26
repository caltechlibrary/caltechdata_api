import argparse, os, json
from caltechdata_api import caltechdata_edit

parser = argparse.ArgumentParser(
    description="Write files and a DataCite 4 standard json record\
        to CaltechDATA repository"
)
parser.add_argument(
    "json_file",
    nargs="?",
    default=None,
    help="file name for json DataCite metadata file",
)
parser.add_argument("-ids", nargs="*", help="CaltechDATA IDs")
parser.add_argument("-fnames", nargs="*", help="New Files")
parser.add_argument("-schema", default="40", help="Metadata Schema")
parser.add_argument(
    "-delete", nargs="*", default="{}", help="Filename or extension to delete"
)
args = parser.parse_args()

# Get access token from TIND set as environment variable with source token.bash
token = os.environ["TINDTOK"]

if args.json_file:
    metaf = open(args.json_file, "r")
    metadata = json.load(metaf)
else:
    metadata = {}

production = True

response = caltechdata_edit(
    token, args.ids, metadata, args.fnames, args.delete, production, args.schema
)
print(response)
