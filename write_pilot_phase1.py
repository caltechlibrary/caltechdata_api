import argparse, os, json
import s3fs
from datacite import schema43
from caltechdata_api import caltechdata_write

parser = argparse.ArgumentParser(
    description="Adds S3-stored pilot files and a DataCite 4.3 standard json record\
        to CaltechDATA repository"
)
parser.add_argument("folder", nargs=1, help="Folder")
parser.add_argument(
    "json_file", nargs=1, help="file name for json DataCite metadata file"
)
parser.add_argument("-flinks", nargs="*", help="File Links")

args = parser.parse_args()

# Get access token as environment variable
token = os.environ["TINDTOK"]

endpoint = "https://renc.osn.xsede.org"

# Get metadata and files from bucket
s3 = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint})


path = "ini210004tommorrell/" + args.folder[0] + "/"
meta_path = path + args.json_file[0]
metaf = s3.open(meta_path, "rb")
metadata = json.load(metaf)

# Find the files
files = s3.glob(path + "/*.nc")

description_string = f"Files available via S3 at {endpoint}/{path}<br>"
for link in files:
    fname = link.split("/")[-1]
    link = endpoint + link
    description_string += f"""{fname} <a class="btn btn-xs piwik_download" 
        type="application/octet-stream" href="{link}">
        <i class="fa fa-download"></i> Download</a>    <br>"""

metadata["descriptions"].append(
    {"description": description_string, "descriptionType": "Other"}
)

# valid = schema43.validate(metadata)
# if not valid:
#    v = schema43.validator.validate(metadata)
#    errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
#    for error in errors:
#        print(error.message)
#    exit()

print(metadata)

production = True

response = caltechdata_write(metadata, token, [], production, "43")
print(response)
