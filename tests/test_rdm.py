from caltechdata_api import customize_schema, caltechdata_write
import json

def test_datacite_rdm_conversion(full_datacite43_record,full_rdm_record):
    converted = customize_schema(full_datacite43_record, schema='43', pilot=True)

    assert converted == full_rdm_record

def test_datacite_rdm_create(full_datacite43_record):
    doi = caltechdata_write(full_datacite43_record,schema="43",pilot=True)

    assert doi.startswith('10.33569')

    doi = caltechdata_write(full_datacite43_record,schema="43",pilot=True,
            files=['codemeta.json'])

    assert doi.startswith('10.33569')
