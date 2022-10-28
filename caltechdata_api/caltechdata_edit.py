import copy, os, json

import requests
from requests import session

from caltechdata_api import (
    customize_schema,
    write_files_rdm,
    add_file_links,
    send_to_community,
)


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
    file_links=[],
    s3=None,
    community=None,
):

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

    if file_links:
        metadata = add_file_links(metadata, file_links)

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
            # Check for existing draft
            result = requests.get(
                url + "/api/records/" + idv + "/draft",
                headers=headers,
                verify=verify,
            )
            if result.status_code != 200:
                draft = False
            else:
                draft = True
            if draft == False:
                result = requests.get(
                    url + "/api/records/" + idv,
                    headers=headers,
                    verify=verify,
                )
                if result.status_code != 200:
                    raise Exception(result.text)
            # We want files to stay the same as the existing record
            data["files"] = result.json()["files"]
            print(url + "/api/records/" + idv + "/draft")
            if draft == True:
                result = requests.put(
                    url + "/api/records/" + idv + "/draft",
                    headers=headers,
                    json=data,
                    verify=verify,
                )
                if result.status_code != 200:
                    raise Exception(result.text)
            else:
                result = requests.post(
                    url + "/api/records/" + idv + "/draft",
                    headers=headers,
                    json=data,
                    verify=verify,
                )
                if result.status_code != 201:
                    raise Exception(result.text)

        if community:
            review_link = result.json()["links"]["review"]
            result = send_to_community(
                review_link, data, headers, verify, publish, community
            )
            doi = result.json()["pids"]["doi"]["identifier"]
            completed.append(doi)
        elif publish:
            publish_link = f"{url}/api/records/{idv}/draft/actions/publish"
            result = requests.post(publish_link, headers=headers, verify=verify)
            if result.status_code != 202:
                raise Exception(result.text)
            doi = result.json()["pids"]["doi"]["identifier"]
            completed.append(doi)
        else:
            completed.append(idv)
    if len(completed) == 1:
        return completed[0]
    else:
        return completed
