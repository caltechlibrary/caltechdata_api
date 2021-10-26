import argparse, os, json
from caltechdata_api import caltechdata_unembargo

parser = argparse.ArgumentParser(
    description="Write files and a DataCite 4 standard json record\
        to CaltechDATA repository"
)
parser.add_argument("-ids", nargs="*", help="CaltechDATA IDs")
args = parser.parse_args()

# Get access token from TIND set as environment variable with source token.bash
token = os.environ["TINDTOK"]

production = False

response = caltechdata_unembargo(token, args.ids, production)
print(response)
