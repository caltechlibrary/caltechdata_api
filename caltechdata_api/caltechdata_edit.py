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


def caltechdata_accept(ids, token=None, production=False):
    # Accept a record into a community

    # If no token is provided, get from RDMTOK environment variable
    if not token:
        token = os.environ["RDMTOK"]

    if production == True:
        url = "https://data.caltech.edu"
    else:
        url = "https://data.caltechlibrary.dev"

    headers = {
        "Authorization": "Bearer %s" % token,
        "Content-type": "application/json",
    }

    for idv in ids:

        result = requests.get(
            url + "/api/records/" + idv + "/draft/review", headers=headers
        )

        accept_link = result.json()["links"]["actions"]["accept"]
        data = comment = {
            "payload": {
                "content": "This record is accepted automatically with the CaltechDATA API",
                "format": "html",
            }
        }
        result = requests.post(accept_link, json=data, headers=headers)
        if result.status_code != 200:
            raise Exception(result.text)


def caltechdata_edit(
    idv,
    metadata={},
    token=None,
    files={},
    production=False,
    schema="43",
    publish=False,
    file_links=[],
    s3=None,
    community=None,
    new_version=False,
):

    # If no token is provided, get from RDMTOK environment variable
    if not token:
        token = os.environ["RDMTOK"]

    # If files is a string - change to single value array
    if isinstance(files, str) == True:
        files = [files]

    if file_links:
        metadata = add_file_links(metadata, file_links)

    # Pull out pid information
    if production == True:
        repo_prefix = "10.22002"
    else:
        repo_prefix = "10.33569"
    pids = {}
    oai = False
    doi = False
    if "identifiers" in metadata:
        for identifier in metadata["identifiers"]:
            if identifier["identifierType"] == "DOI":
                doi = True
                doi = identifier["identifier"]
                prefix = doi.split("/")[0]
                if prefix == repo_prefix:
                    pids["doi"] = {
                        "identifier": doi,
                        "provider": "datacite",
                        "client": "datacite",
                    }
                else:
                    pids["doi"] = {
                        "identifier": doi,
                        "provider": "external",
                    }
            elif identifier["identifierType"] == "oai":
                pids["oai"] = {
                    "identifier": identifier["identifier"],
                    "provider": "oai",
                }
                oai = True
    #Records are not happy without the auto-assigned oai identifier
    if oai == False:
        pids["oai"] = {
            "identifier": f"oai:data.caltech.edu:{idv}",
            "provider": "oai",
        }
    #We do not want to lose the auto-assigned DOI
    #Users with custom DOIs must pass them in the metadata
    if doi == False:
        pids["doi"] = {
                        "identifier": f'{repo_prefix}/{idv}',
                        "provider": "datacite",
                        "client": "datacite",
                    }
    metadata["pids"] = pids

    data = customize_schema.customize_schema(copy.deepcopy(metadata), schema=schema)

    if production == True:
        url = "https://data.caltech.edu"
    else:
        url = "https://data.caltechlibrary.dev"

    headers = {
        "Authorization": "Bearer %s" % token,
        "Content-type": "application/json",
    }
    f_headers = {
        "Authorization": "Bearer %s" % token,
        "Content-type": "application/octet-stream",
    }

    if files or new_version:
        # We need to make new version
        data["files"] = {"enabled": True}
        result = requests.post(
            url + "/api/records/" + idv + "/versions",
            headers=headers,
        )
        if result.status_code != 201:
            raise Exception(result.text)
        # Get the id of the new version
        idv = result.json()["id"]
        # Update metadata
        result = requests.put(
            url + "/api/records/" + idv + "/draft",
            headers=headers,
            json=data,
        )

        file_link = result.json()["links"]["files"]
        write_files_rdm(files, file_link, headers, f_headers)

    else:
        # Check for existing draft
        result = requests.get(
            url + "/api/records/" + idv + "/draft",
            headers=headers,
        )
        if result.status_code != 200:
            # We make a draft
            result = requests.post(
                url + "/api/records/" + idv + "/draft",
                json=data,
                headers=headers,
            )
            if result.status_code != 201:
                raise Exception(result.text)
            result = requests.get(
                url + "/api/records/" + idv,
                headers=headers,
            )
            if result.status_code != 200:
                raise Exception(result.text)
        # We want files to stay the same as the existing record
        data["files"] = result.json()["files"]
        result = requests.put(
            url + "/api/records/" + idv + "/draft",
            headers=headers,
            json=data,
        )
        if result.status_code != 200:
            raise Exception(result.text)

    if community:
        review_link = result.json()["links"]["review"]
        result = send_to_community(review_link, data, headers, publish, community)
        doi = result.json()["pids"]["doi"]["identifier"]
        return doi
    elif publish:
        publish_link = f"{url}/api/records/{idv}/draft/actions/publish"
        result = requests.post(publish_link, headers=headers)
        if result.status_code != 202:
            raise Exception(result.text)
        doi = result.json()["pids"]["doi"]["identifier"]
        return doi
    else:
        return idv
