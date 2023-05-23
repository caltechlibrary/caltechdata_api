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
    file_descriptions=[],
    s3_link=None,
    default_preview=None,
):
    # Make a copy of the metadata to make sure our local changes don't leak
    metadata = copy.deepcopy(metadata)

    # If no token is provided, get from RDMTOK environment variable
    if not token:
        token = os.environ["RDMTOK"]

    # If files is a string - change to single value array
    if isinstance(files, str) == True:
        files = [files]

    # Check if file links were provided in the metadata
    descriptions = []
    for d in metadata["descriptions"]:
        if d["description"].startswith("Files available via S3"):
            ex_file_links = []
            file_text = d["description"]
            file_list = file_text.split('href="')
            # Loop over links in description, skip header text
            for file in file_list[1:]:
                ex_file_links.append(file.split('"\n')[0])
        else:
            descriptions.append(d)
    # We remove file link descriptions, and re-add below
    metadata["descriptions"] = descriptions

    # If user has provided file links as a cli option, we add those
    if file_links:
        metadata = add_file_links(
            metadata, file_links, file_descriptions, s3_link=s3_link
        )
    # Otherwise we add file links found in the mtadata file
    elif ex_file_links:
        metadata = add_file_links(
            metadata, ex_file_links, file_descriptions, s3_link=s3_link
        )

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

    # Check status
    existing = requests.get(
        url + "/api/records/" + idv,
        headers=headers,
    )
    if existing.status_code != 200:
        # Might have a draft
        existing = requests.get(
            url + "/api/records/" + idv + "/draft",
            headers=headers,
        )
        if existing.status_code != 200:
            raise Exception(f"Record {idv} does not exist, cannot edit")

    status = existing.json()["status"]

    # Determine whether we need a new version
    version = False
    if status == "published" and files:
        version = True

    if new_version:
        version = True

    if version:
        # We need to make new version
        result = requests.post(
            url + "/api/records/" + idv + "/versions",
            headers=headers,
        )
        if result.status_code != 201:
            raise Exception(result.text)
        # Get the id of the new version
        idv = result.json()["id"]

    print(idv)
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
    # Existing records are not happy without the auto-assigned oai identifier
    if oai == False and version == False:
        pids["oai"] = {
            "identifier": f"oai:data.caltech.edu:{idv}",
            "provider": "oai",
        }
    # We do not want to lose the auto-assigned DOI
    # Users with custom DOIs must pass them in the metadata
    if doi == False and version == False:
        pids["doi"] = {
            "identifier": f"{repo_prefix}/{idv}",
            "provider": "datacite",
            "client": "datacite",
        }
    metadata["pids"] = pids

    data = customize_schema.customize_schema(metadata, schema=schema)

    if files:
        if default_preview:
            data["files"] = {"enabled": True, "default_preview": default_preview}
        else:
            data["files"] = {"enabled": True}
        # Update metadata
        result = requests.put(
            url + "/api/records/" + idv + "/draft",
            headers=headers,
            json=data,
        )
        if result.status_code != 200:
            raise Exception(result.text)
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
        data["files"] = existing.json()["files"]
        if default_preview:
            data["files"]["default_preview"] = default_preview
        # Update metadata
        result = requests.put(
            url + "/api/records/" + idv + "/draft",
            headers=headers,
            json=data,
        )
        if result.status_code != 200:
            raise Exception(result.text)

    if publish:
        publish_link = f"{url}/api/records/{idv}/draft/actions/publish"
        result = requests.post(publish_link, headers=headers)
        if result.status_code != 202:
            raise Exception(result.text)
        doi = result.json()["pids"]["doi"]["identifier"]
        return doi
    else:
        return idv
