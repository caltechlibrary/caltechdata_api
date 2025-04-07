from caltechdata_api import (
    customize_schema,
    caltechdata_write,
    caltechdata_edit,
    get_metadata,
)
import json
import os


def test_datacite_rdm_conversion(full_datacite43_record, full_rdm_record):

    # Remove DOI from full_datacite43_record
    # since it's prcessed by caltechdata_write or caltechdata_edit
    identifiers = []
    for identifier in full_datacite43_record["identifiers"]:
        if identifier["identifierType"] != "DOI":
            identifiers.append(identifier)
    full_datacite43_record["identifiers"] = identifiers

    converted = customize_schema(full_datacite43_record, schema="43")

    assert converted == full_rdm_record


def test_datacite_rdm_create_edit(full_datacite43_record):
    env_token = os.environ.get("RDMTOK")

    # Remove DOI from full_datacite43_record
    # since we want the test system to create one
    identifiers = []
    for identifier in full_datacite43_record["identifiers"]:
        if identifier["identifierType"] != "DOI":
            identifiers.append(identifier)
    full_datacite43_record["identifiers"] = identifiers

    recid = caltechdata_write(
        full_datacite43_record,
        schema="43",
        production=False,
        publish=True,
        token=env_token,
    )

    assert len(recid) == 11

    recid = caltechdata_write(
        full_datacite43_record,
        schema="43",
        production=False,
        files=["helpers.py"],
        publish=True,
        token=env_token,
    )

    assert len(recid) == 11

    full_datacite43_record["publisher"] = "Edited"

    doi = caltechdata_edit(
        recid,
        full_datacite43_record,
        schema="43",
        production=False,
        publish=True,
        token=env_token,
    )

    assert doi.startswith("10.33569")

    # Validate is false until geolocation points are fixed/we move to 4.6
    new_metadata = get_metadata(recid, production=False, validate=False)

    assert new_metadata["publisher"] == "Edited"

    full_datacite43_record["publisher"] = "Again!"

    new_doi = caltechdata_edit(
        recid,
        full_datacite43_record,
        files=["helpers.py"],
        schema="43",
        production=False,
        publish=True,
        token=env_token,
    )

    assert new_doi != doi

    recid = new_doi.split("/")[1]

    # Validate is false until geolocation points are fixed/we move to 4.6
    new_metadata = get_metadata(recid, production=False, validate=False)

    assert new_metadata["publisher"] == "Again!"
