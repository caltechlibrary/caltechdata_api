import argparse, os, json
from datacite import DataCiteMDSClient, schema40
from caltechdata_api import caltechdata_write

parser = argparse.ArgumentParser(
    description="Adds S3-stored pilot files and a DataCite 4.3 standard json record\
        to CaltechDATA repository"
)
parser.add_argument(
    "json_file", nargs=1, help="file name for json DataCite metadata file"
)
parser.add_argument("-flinks", nargs="*", help="File Links")

args = parser.parse_args()

# Get access token as environment variable
token = os.environ["TINDTOK"]

metaf = open(args.json_file[0], "r")
metadata = json.load(metaf)


description_string = ""
for link in args.flinks:
    fname = link.split("/")[-1]
    description_string += f"""{fname} <a class="btn btn-xs piwik_download" 
    type="application/octet-stream" href="{link}">
<i class="fa fa-download"></i> Download</a>    <br>"""


metadata["descriptions"].append(
    {"description": description_string, "descriptionType": "Other"}
)


production = False

response = caltechdata_write(metadata, token, [], production, "43")
print(response)
