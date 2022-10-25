import copy, os, json

import requests
from requests import session

from caltechdata_api import customize_schema, write_files_rdm


def caltechdata_unembargo(token, ids, production=False):
    print("caltechdaua_unembargo is not yet re-implemented")


def caltechdata_edit(
    ids,
    metadata={},
    token=None,
    files={},
    delete={},
    production=False,
    schema="43",
    publish=False,
):
    """Including files will only replaces files if they have the same name
    The delete option will delete any existing files with a given file extension
    There are more file operations that could be implemented"""

    # If no token is provided, get from RDMTOK environment variable
    if not token:
        token = os.environ["RDMTOK"]

    # If files is a string - change to single value array
    if isinstance(files, str) == True:
        files = [files]
    if isinstance(ids, int):
        ids = [str(ids)]
    if isinstance(ids, str):
        ids = [ids]

    data = customize_schema.customize_schema(copy.deepcopy(metadata), schema=schema)
    if production == True:
        url = "https://data.caltech.edu"
        verify = True
    else:
        url = "https://data.caltechlibrary.dev"
        verify = True

    headers = {
        "Authorization": "Bearer %s" % token,
        "Content-type": "application/json",
    }
    f_headers = {
        "Authorization": "Bearer %s" % token,
        "Content-type": "application/octet-stream",
    }

    if delete:
        print(
            """WARNING: Delete command is no longer supported; only the
            files listed in the file option will be added to new version of
            record"""
        )

    completed = []

    for idv in ids:
        if files:
            # We need to make new version
            data["files"] = {"enabled": True}
            result = requests.post(
                url + "/api/records/" + idv + "/versions",
                headers=headers,
                verify=verify,
            )
            if result.status_code != 201:
                print(result.text)
                exit()
            # Get the id of the new version
            idv = result.json()["id"]
            # Update metadata
            result = requests.put(
                url + "/api/records/" + idv + "/draft",
                headers=headers,
                json=data,
                verify=verify,
            )

            file_link = result.json()["links"]["files"]
            write_files_rdm(files, file_link, headers, f_headers, verify)

        else:
            # just update metadata
            # result = requests.post(
            #    url + "/api/records/" + idv + "/draft",
            #    headers=headers,
            #    verify=verify,
            # )
            # if result.status_code != 200:
            #    print(result.text)
            #    exit()
            # print(result.json())
            # exit()
            # print(url + "/api/records/" + idv + "/draft")
            result = requests.get(
                url + "/api/records/" + idv,
                headers=headers,
                verify=verify,
            )
            if result.status_code != 200:
                result = requests.get(
                url + "/api/records/" + idv + "/draft",
                headers=headers,
                verify=verify,
                )
                if result.status_code != 200:
                    print(result.text)
                    exit()
            # We want files to stay the same as the existing record
            data["files"] = result.json()["files"]
            print(url + "/api/records/" + idv + "/draft")
            result = requests.put(
                url + "/api/records/" + idv + "/draft",
                headers=headers,
                json=data,
                verify=verify,
            )
            if result.status_code != 200:
                print(result.text)
                exit()

        if publish:
            publish_link = f"{url}/api/records/{idv}/draft/actions/publish"
            print(publish_link)
            result = requests.post(publish_link, headers=headers, verify=verify)
            if result.status_code != 202:
                print(result.text)
                exit()
            doi = result.json()["pids"]["doi"]["identifier"]
            completed.append(doi)
        else:
            completed.append(idv)
    if len(completed) == 1:
        return completed[0]
    else:
        return completed
