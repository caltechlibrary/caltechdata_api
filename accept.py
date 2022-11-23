import argparse, os
from caltechdata_api import caltechdata_accept

parser = argparse.ArgumentParser(
    description="Accept records to a community in the CaltechDATA repository"
)
parser.add_argument("ids", nargs="*", help="CaltechDATA IDs")
args = parser.parse_args()

# Get access token set as environment variable with source token.bash
token = os.environ["RDMTOK"]

production = True

caltechdata_accept(
    args.ids,
    token,
    production,
)
print('Completed')
