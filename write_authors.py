import argparse, os, json
from caltechdata_api import caltechdata_write

parser = argparse.ArgumentParser(
    description="Write files and a DataCite 4 standard json record\
        to CaltechDATA repository"
)
parser.add_argument(
    "json_file", nargs=1, help="file name for json DataCite metadata file"
)
parser.add_argument("-fnames", nargs="*", help="New Files")
parser.add_argument("-schema", default="43", help="Metadata Schema")

args = parser.parse_args()

# Get access token as environment variable
token = os.environ["RDMTOK"]

metaf = open(args.json_file[0], "r")
metadata = json.load(metaf)

production = False
publish = True
authors = True
community = "bbb4cf12-be6e-42db-a8e1-114edfff5500"

response = caltechdata_write(
    metadata,
    token,
    args.fnames,
    production,
    args.schema,
    publish,
    community=community,
    authors=authors,
)
print(response)
