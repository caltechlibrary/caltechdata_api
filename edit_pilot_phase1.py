import argparse, os, json
import s3fs
from datacite import schema43
from caltechdata_api import caltechdata_edit, get_metadata


def add_description_line(link, endpoint, description_string):
    fname = link.split("/")[-1]
    link = endpoint + link
    link = link.replace(" ", "%20")
    description_string += f"""{fname} <a class="btn btn-xs piwik_download"
        type="application/octet-stream" href="{link}">
        <i class="fa fa-download"></i> Download</a>    <br>"""
    return description_string


parser = argparse.ArgumentParser(
    description="Adds S3-stored pilot files and a DataCite 4.3 standard json record\
        to CaltechDATA repository"
)
parser.add_argument("folder", nargs=1, help="Folder")
parser.add_argument("-id", nargs=1, help="")

args = parser.parse_args()

# Get access token as environment variable
token = os.environ["TINDTOK"]

endpoint = "https://renc.osn.xsede.org/"

# Get metadata and files from bucket
s3 = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint})

path = "ini210004tommorrell/" + args.folder[0] + "/"

idv = args.id[0]
metadata = get_metadata(idv, schema="43")

# Find the files
files = s3.glob(path + "/*")

description_string = f"Files available via S3 at {endpoint}{path}<br>"
for link in files:
    fname = link.split("/")[-1]
    if "." not in fname:
        # If there is a directory, get files
        folder_files = s3.glob(link + "/*")
        for file in folder_files:
            description_string = add_description_line(
                file, endpoint, description_string
            )
    else:
        description_string = add_description_line(link, endpoint, description_string)

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

production = True

response = caltechdata_edit(idv, metadata, token, [], [], production, "43")
print(response)
