import requests, os

token = os.environ["RDMTOK"]

url = "https://data.caltechlibrary.dev/"

headers = {
            "Authorization": "Bearer %s" % token,
            "Content-type": "application/json",
        }

data = {
  "payload": {
    "content": "I want this record to be in!", 
    "format": "html"
  }
}

result = requests.post(
            url + "/api/records/cxc6m-bef55/draft/actions/submit-review", headers=headers, json=data
        )

print(result.status_code)
print(result.text)
#if result.status_code != 201:
#            print(result.text)
#            exit()

