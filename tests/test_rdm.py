from caltechdata_api import (
    customize_schema,
    caltechdata_write,
    caltechdata_edit,
    get_metadata,
)
import json


def test_datacite_rdm_conversion(full_datacite43_record, full_rdm_record):
    converted = customize_schema(full_datacite43_record, schema="43", pilot=True)

    assert converted == full_rdm_record


def test_datacite_rdm_create_edit(full_datacite43_record):
    doi = caltechdata_write(
        full_datacite43_record, schema="43", pilot=True, publish=True
    )

    assert doi.startswith("10.33569")

    doi = caltechdata_write(
        full_datacite43_record,
        schema="43",
        pilot=True,
        files=["codemeta.json"],
        publish=True,
    )

    assert doi.startswith("10.33569")

    # If we don't publish, don't get back a DOI
    idv = caltechdata_write(full_datacite43_record, schema="43", pilot=True)

    assert idv.startswith("10.33569") == False

    full_datacite43_record["title"] = "Edited"

    print(full_datacite43_record)

    new_idv = caltechdata_edit(
        idv, full_datacite43_record, schema="43", pilot=True, publish=True
    )

    assert new_idv != idv

    new_metadata = get_metadata(idv, production=False, pilot=True)

    print(new_metadata)

    assert new_metadata["title"] == "Edited"
