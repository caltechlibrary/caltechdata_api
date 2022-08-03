import copy
import json
import os, sys, requests

from requests import session
from json.decoder import JSONDecodeError

from caltechdata_api import customize_schema


def write_files_rdm(files, file_link, headers, f_headers, verify):
    f_json = []
    f_list = {}
    for f in files:
        filename = f.split("/")[-1]
        f_json.append({"key": filename})
        f_list[filename] = f
    result = requests.post(file_link, headers=headers, json=f_json, verify=verify)
    if result.status_code != 201:
        print(result.text)
        exit()
    # Now we have the upload links
    for entry in result.json()["entries"]:
        link = entry["links"]["content"]
        commit = entry["links"]["commit"]
        name = entry["key"]
        infile = open(f_list[name], "rb")
        # size = infile.seek(0, 2)
        # infile.seek(0, 0)  # reset at beginning
        result = requests.put(link, headers=f_headers, verify=verify, data=infile)
        if result.status_code != 200:
            print(result.text)
            exit()
        result = requests.post(commit, headers=headers, verify=verify)
        if result.status_code != 200:
            print(result.text)
            exit()


def send_s3(filepath, token, production=False):

    if production == True:
        s3surl = "https://data.caltech.edu/tindfiles/sign_s3/"
        chkurl = "https://data.caltech.edu/tindfiles/md5_s3"
    else:
        s3surl = "https://cd-sandbox.tind.io/tindfiles/sign_s3/"
        chkurl = "https://cd-sandbox.tind.io/tindfiles/md5_s3"

    headers = {"Authorization": "Bearer %s" % token}

    c = session()

    # print(s3surl)
    # print(headers)
    try:
        response = c.get(s3surl, headers=headers)
        jresp = response.json()
        data = jresp["data"]
    except Exception:
        print(f"Incorrect access token: {response}")

    bucket = jresp["bucket"]
    key = data["fields"]["key"]
    policy = data["fields"]["policy"]
    aid = data["fields"]["AWSAccessKeyId"]
    signature = data["fields"]["signature"]
    url = data["url"]

    infile = open(filepath, "rb")
    size = infile.seek(0, 2)
    infile.seek(0, 0)  # reset at beginning

    s3headers = {
        "Host": bucket + ".s3.amazonaws.com",
        "Date": "date",
        "x-amz-acl": "public-read",
        "Access-Control-Allow-Origin": "*",
    }

    form = (
        ("key", key),
        ("acl", "public-read"),
        ("AWSAccessKeyID", aid),
        ("policy", policy),
        ("signature", signature),
        ("file", infile),
    )

    c = session()
    response = c.post(url, files=form, headers=s3headers)
    # print(response)
    if response.text:
        raise Exception(response.text)

    # print(chkurl + "/" + bucket + "/" + key + "/")
    # print(headers)
    response = c.get(chkurl + "/" + bucket + "/" + key + "/", headers=headers)
    # print(response)
    md5 = response.json()["md5"]
    filename = filepath.split("/")[-1]

    fileinfo = {"url": key, "filename": filename, "md5": md5, "size": size}

    return fileinfo


def caltechdata_write(
    metadata,
    token=None,
    files=[],
    production=False,
    schema="40",
    pilot=False,
    publish=False,
):

    # If no token is provided, get from RDMTOK environment variable
    if not token:
        token = os.environ["RDMTOK"]

    # If files is a string - change to single value array
    if isinstance(files, str) == True:
        files = [files]

    if pilot:
        data = customize_schema.customize_schema(
            copy.deepcopy(metadata), schema=schema, pilot=True
        )
        print(json.dumps(data))
        if production == True:
            url = "https://data.caltechlibrary.dev/"
            verify = True
        else:
            url = "https://coda.caltechlibrary.dev/"
            verify = False

        headers = {
            "Authorization": "Bearer %s" % token,
            "Content-type": "application/json",
        }
        f_headers = {
            "Authorization": "Bearer %s" % token,
            "Content-type": "application/octet-stream",
        }

        if not files:
            data["files"] = {"enabled": False}

        # Make draft and publish
        result = requests.post(
            url + "/api/records", headers=headers, json=data, verify=verify
        )
        if result.status_code != 201:
            print(result.text)
            exit()

        idv = result.json()["id"]
        publish_link = result.json()["links"]["publish"]

        if files:
            file_link = result.json()["links"]["files"]
            write_files_rdm(files, file_link, headers, f_headers, verify)

        if publish:
            result = requests.post(publish_link, headers=headers, verify=verify)
            if result.status_code != 202:
                print(result.text)
                exit()
            pids = result.json()["pids"]
            if "doi" in pids:
                idv = pids["doi"]["identifier"]
        return idv

    else:

        fileinfo = []

        newdata = customize_schema.customize_schema(
            copy.deepcopy(metadata), schema=schema
        )

        if files:
            for f in files:
                fileinfo.append(send_s3(f, token, production))
            newdata["files"] = fileinfo

        if production == True:
            url = "https://data.caltech.edu/submit/api/create/"
        else:
            url = "https://cd-sandbox.tind.io/submit/api/create/"

        headers = {
            "Authorization": "Bearer %s" % token,
            "Content-type": "application/json",
        }

        if "doi" not in newdata:
            # We want tind to generate the identifier
            newdata["final_actions"] = [
                {
                    "type": "create_doi",
                    "parameters": {"type": "records", "field": "doi"},
                }
            ]

        dat = json.dumps({"record": newdata})

        c = session()
        response = c.post(url, headers=headers, data=dat)
        return response.text
