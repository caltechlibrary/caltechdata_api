import copy, os, json, time

import requests
from requests import session

from caltechdata_api import (
    customize_schema,
    write_files_rdm,
    add_file_links,
)


def caltechdata_unembargo(token, ids, production=False):
    print("caltechdaua_unembargo is not yet re-implemented")


def caltechdata_accept(ids, token=None, production=False):
    # Accept a record into a community. Only accepts the first community
    # request

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
        if result.status_code != 200:
            result = requests.get(
                url + "/api/records/" + idv + "/requests", headers=headers
            )
            if result.status_code != 200:
                raise Exception(result.text)
            accept_link = result.json()["hits"]["hits"][0]["links"]["actions"]["accept"]
        else:
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


def caltechdata_reject(ids, token=None, production=False, authors=False):
    # Reject a record from a community

    # If no token is provided, get from RDMTOK environment variable
    if not token:
        token = os.environ["RDMTOK"]

    if production == True:
        if authors:
            url = "https://authors.library.caltech.edu"
        else:
            url = "https://data.caltech.edu"
    else:
        if authors:
            url = "https://authors.caltechlibrary.dev"
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
        print(url + "/api/records/" + idv + "/draft/review")
        if result.status_code != 200:
            raise Exception(result.text)
        accept_link = result.json()["links"]["actions"]["decline"]
        data = comment = {
            "payload": {
                "content": "This record was declined automatically with the CaltechDATA API",
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
    schema=None,
    publish=False,
    file_links=[],
    s3=None,
    community=None,
    new_version=False,
    file_descriptions=[],
    s3_link=None,
    default_preview=None,
    authors=False,
    keepfiles=False,
    return_id=False,
    local=False,
):
    # Make a copy of the metadata to make sure our local changes don't leak
    metadata = copy.deepcopy(metadata)

    # If no token is provided, get from RDMTOK environment variable
    if not token:
        token = os.environ["RDMTOK"]

    # If files is a string - change to single value array
    if isinstance(files, str) == True:
        files = [files]

    if authors == False:
        if production == True:
            url = "https://data.caltech.edu/"
        elif local == True:
            url = "https://127.0.0.1:5000/"
        else:
            url = "https://data.caltechlibrary.dev/"
    else:
        if production == True:
            url = "https://authors.library.caltech.edu/"
        elif local == True:
            url = "https://127.0.0.1:5000/"
        else:
            url = "https://authors.caltechlibrary.dev/"

    headers = {
        "Authorization": "Bearer %s" % token,
        "Content-type": "application/json",
    }
    f_headers = {
        "Authorization": "Bearer %s" % token,
        "Content-type": "application/octet-stream",
    }

    # Add to community if provided:
    if community:
        result = requests.post(
            url + "/api/records/" + idv + "/communities",
            headers=headers,
            data=json.dumps({"communities": [{"id": community}]}),
        )
        if result.status_code != 200:
            print(result.url)
            raise Exception(result.text)
        caltechdata_accept([idv], token, production)

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
            # Try back again to the record
            existing = requests.get(
                url + "/api/records/" + idv,
                headers=headers,
            )

            if existing.status_code != 200:
                raise Exception(f"Record {idv} does not exist, cannot edit")

    existing = existing.json()
    status = existing["status"]

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
    # Not currently used for authors
    if production == True:
        if authors == True:
            repo_prefix = "10.7907"
        else:
            repo_prefix = "10.22002"
    else:
        repo_prefix = "10.33569"
    pids = {}
    oai = False
    doi = False
    if "identifiers" in metadata and version == False:
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
    # If we are making a new version, we only want to look for custom DOIs
    if version == True and "identifiers" in metadata:
        for identifier in metadata["identifiers"]:
            if identifier["identifierType"] == "DOI":
                doi = identifier["identifier"]
                prefix = doi.split("/")[0]
                if prefix != repo_prefix:
                    pids["doi"] = {
                        "identifier": doi,
                        "provider": "external",
                    }

    # If no metadata is provided, use existing. Otherwise customize provided
    # metadata
    if metadata == {}:
        data = existing
        if version == True:
            # We want to have the system set new DOIs
            data["pids"] = {}
    else:
        if authors == False and schema == "43":
            metadata["pids"] = pids
            data = customize_schema.customize_schema(metadata, schema=schema)
        elif authors == False:
            # Data using RDM schema, force oai PID
            if "pids" not in metadata:
                metadata["pids"] = {}
            metadata["pids"]["oai"] = {
                "identifier": f"oai:data.caltech.edu:{idv}",
                "provider": "oai",
            }
            data = metadata
        if authors == True:
            # Authors, force oai PID
            if "pids" not in metadata:
                metadata["pids"] = {}
            metadata["pids"]["oai"] = {
                "identifier": f"oai:authors.library.caltech.edu:{idv}",
                "provider": "oai",
            }
            data = metadata

    # Check for existing draft
    result = requests.get(
        url + "/api/records/" + idv + "/draft",
        headers=headers,
    )
    if result.status_code != 200:
        # We make a draft
        result = requests.post(
            url + "/api/records/" + idv + "/draft",
            headers=headers,
        )
        if result.status_code != 201:
            raise Exception(result.text)

    if files or file_links:
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
        file_upload_link = result.json()["links"]["files"]
        if files:
            write_files_rdm(
                files, file_upload_link, headers, f_headers, keepfiles=keepfiles
            )
        if file_links:
            add_file_links(file_upload_link, file_links, headers, keepfiles=keepfiles)

    else:
        # We want files to stay the same as the existing record
        data["files"] = existing["files"]
        if default_preview:
            data["files"]["default_preview"] = default_preview
        # Update metadata
        result = requests.put(
            url + "/api/records/" + idv + "/draft",
            headers=headers,
            json=data,
        )
        if result.status_code != 200:
            time.sleep(3)
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
            time.sleep(3)
            result = requests.post(publish_link, headers=headers)
            if result.status_code != 202:
                raise Exception(result.text)
        if return_id:
            return result.json()["id"]
        else:
            pids = result.json()["pids"]
            if "doi" in pids:
                return pids["doi"]["identifier"]
            else:
                return pids["oai"]["identifier"]
    else:
        return idv
