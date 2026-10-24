import argparse, os
import s3fs, requests
from caltechdata_api import caltechdata_edit, get_metadata

parser = argparse.ArgumentParser(
    description="Edits a CaltechDATA record by adding OSN-stored files"
)
parser.add_argument("bucket", nargs=1, help="S3 bucket name")
parser.add_argument("-id", nargs=1, help="")
parser.add_argument("-test", action="store_true", help="Test mode")
parser.add_argument("-pod", nargs=1, default=["caltech2"], help="Pod name")

args = parser.parse_args()

# Get access token as environment variable
token = os.environ["RDMTOK"]

endpoint = f"https://{args.pod[0]}.osn.mghpcc.org/"

# Get metadata and files from bucket
s3 = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint})

path = f"{args.bucket[0]}"

idv = args.id[0]
try:
    metadata = get_metadata(idv, production=not args.test)
except:
    if args.test:
        url = "https://data.caltechlibrary.dev/api/records/"
    else:
        url = "https://data.caltech.edu/api/records/"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer %s" % token,
    }

    response = requests.get(url + idv + "/draft", headers=headers)
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

# File names must be unique within a record, so the folders inside the bucket
# are included in the name of each file
prefix = endpoint + path + "/"
file_links = [
    (link.split(prefix)[1].replace("/", "_"), link) for link in file_links
]

response = caltechdata_edit(
    idv, metadata, token, [], production=not args.test, publish=False, file_links=file_links
)
print(response)
