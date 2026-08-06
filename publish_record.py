import requests
import os

publish_link = (
    "https://authors.library.caltech.edu/api/records/rjcyg-wqy42/draft/actions/publish"
)

token = os.environ["RDMTOK"]

headers = {
    "Authorization": "Bearer %s" % token,
    "Content-type": "application/json",
}

result = requests.post(publish_link, headers=headers)
if result.status_code != 202:
    raise Exception(result.text)
