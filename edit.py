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
parser.add_argument("-id", help="CaltechDATA IDs")
parser.add_argument("-fnames", nargs="*", help="New Files")
parser.add_argument("-flinks", nargs="*", help="New File Links")
parser.add_argument("-schema", default="43", help="Metadata Schema")
parser.add_argument("-authors", action="store_true", help="Edit CaltechAUTHORS")
args = parser.parse_args()

# Get access token set as environment variable with source token.bash
token = os.environ["RDMTOK"]

if args.json_file:
    metaf = open(args.json_file, "r")
    metadata = json.load(metaf)
else:
    metadata = {}

production = True
publish = True

response = caltechdata_edit(
    args.id,
    metadata,
    token,
    args.fnames,
    production,
    args.schema,
    publish,
    args.flinks,
    authors=args.authors,
)
print(response)
