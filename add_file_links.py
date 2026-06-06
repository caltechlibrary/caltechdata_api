import argparse, os
from caltechdata_api import get_metadata, caltechdata_edit

token = os.getenv("RDMTOK")

parser = argparse.ArgumentParser(description="Add file links to a CaltechDATA record")
parser.add_argument("recid", nargs=1, help="CaltechDATA Record ID")
parser.add_argument("-flinks", nargs="*", help="File links")

args = parser.parse_args()
recid = args.recid[0]

metadata = get_metadata(recid)
caltechdata_edit(
    recid, metadata, token, production=True, publish=True, file_links=args.flinks
)
