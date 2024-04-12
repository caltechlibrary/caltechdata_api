import argparse, os, json
import s3fs, requests
from datacite import schema43
from caltechdata_api import caltechdata_edit, get_metadata


parser = argparse.ArgumentParser(
    description="Edits a CaltechDATA record by adding OSN-stored pilot files"
)
parser.add_argument("folder", nargs=1, help="Folder")
parser.add_argument("-id", nargs=1, help="")

args = parser.parse_args()

# Get access token as environment variable
token = os.environ["RDMTOK"]

endpoint = "https://renc.osn.xsede.org/"

# Get metadata and files from bucket
s3 = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint})

folder = args.folder[0]

path = "ini210004tommorrell/" + folder

idv = args.id[0]
try:
    metadata = get_metadata(idv, schema="43")
except:
    url = "https://data.caltech.edu/api/records/"

    headers = {
        "accept": "application/vnd.datacite.datacite+json",
        "Authorization": "Bearer %s" % token,
        }

    response = requests.get(url + idv +'/draft', headers=headers)
    if response.status_code != 200:
        raise Exception(response.text)
    metadata = response.json()

# Find the files
files = s3.glob(path + "/*")

file_links = []
for link in files:
    fname = link.split("/")[-1]
    if "." not in fname:
        # If there is a directory, get files
        folder_files = s3.glob(link + "/*")
        for file in folder_files:
            name = file.split("/")[-1]
            if "." not in name:
                level_2_files = s3.glob(file + "/*")
                for f in level_2_files:
                    name = f.split("/")[-1]
                    if "." not in name:
                        level_3_files = s3.glob(f + "/*")
                        for l3 in level_3_files:
                            file_links.append(endpoint + l3)
                    else:
                        file_links.append(endpoint + f)
            else:
                file_links.append(endpoint + file)
    else:
        file_links.append(endpoint + link)

production = True

response = caltechdata_edit(
    idv, metadata, token, [], production, "43", publish=False, file_links=file_links
)
print(response)
