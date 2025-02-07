from caltechdata_api import (
    customize_schema,
    caltechdata_write,
    caltechdata_edit,
    get_metadata,
)
import json
import os


def test_datacite_rdm_conversion(full_datacite43_record, full_rdm_record):
    converted = customize_schema(full_datacite43_record, schema="43")

    assert converted == full_rdm_record


def test_datacite_rdm_create_edit(full_datacite43_record):
    env_token = os.environ.get("CALTECHDATA_TOKEN")
    doi = caltechdata_write(
        full_datacite43_record, schema="43", production=False, publish=True, token=env_token
    )

    assert doi.startswith("10.33569")

    doi = caltechdata_write(
        full_datacite43_record,
        schema="43",
        production=False,
        files=["codemeta.json"],
        publish=True,
        token=env_token
    )

    assert doi.startswith("10.33569")

    # If we don't publish, don't get back a DOI
    idv = caltechdata_write(full_datacite43_record, schema="43", production=False, token=env_token)

    assert idv.startswith("10.33569") == False

    full_datacite43_record["publisher"] = "Edited"

    doi = caltechdata_edit(
        idv, full_datacite43_record, schema="43", production=False, publish=True, token=env_token
    )

    assert doi.startswith("10.33569")
    idv = doi.split("/")[1]

    new_metadata = get_metadata(idv, production=False, publish=True)

    assert new_metadata["publisher"] == "Edited"

    full_datacite43_record["publisher"] = "Again!"

    new_doi = caltechdata_edit(
        idv,
        full_datacite43_record,
        files=["codemeta.json"],
        schema="43",
        production=False,
        publish=True,
        token=env_token
    )

    assert new_doi != doi

    idv = new_doi.split("/")[1]

    new_metadata = get_metadata(idv, production=False)

    assert new_metadata["publisher"] == "Again!"
