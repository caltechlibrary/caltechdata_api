import argparse
import csv
import json
import os

import requests
from datacite import schema43


def get_metadata(idv, production=True, validate=True, emails=False, schema="43"):
    # Returns just DataCite metadata or DataCite metadata with emails

    if production == True:
        url = "https://data.caltech.edu/api/records/"
        verify = True
    else:
        url = "https://data.caltechlibrary.dev/api/records/"
        verify = True

    headers = {
        "accept": "application/vnd.datacite.datacite+json",
    }

    response = requests.get(url + idv, headers=headers, verify=verify)
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        metadata = response.json()

        if validate:
            if schema == "43":
                try:
                    assert schema43.validate(metadata)
                except AssertionError:
                    v = schema43.validator.validate(metadata)
                    errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
                    for error in errors:
                        print(error.message)

    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="get_metadata queries the caltechDATA (Invenio 3) API\
    and returns DataCite-compatable metadata"
    )
    parser.add_argument(
        "ids",
        metavar="ID",
        type=str,
        nargs="+",
        help="The CaltechDATA ID for each record of interest",
    )
    parser.add_argument("-test", dest="production", action="store_false")
    parser.add_argument("-xml", dest="save_xml", action="store_true")
    parser.add_argument(
        "-skip_validate",
        dest="skip_validate",
        action="store_true",
        help="skip validation of metadata",
    )
    parser.add_argument("-schema", default="43", help="Schema Version")

    args = parser.parse_args()

    production = args.production
    schema = args.schema
    skip_validate = args.skip_validate
    if skip_validate:
        validate = False
    else:
        validate = True

    for idv in args.ids:
        metadata = get_metadata(idv, production, validate, schema)
        outfile = open(str(idv) + ".json", "w")
        outfile.write(json.dumps(metadata, indent=4))
        outfile.close()
        if args.save_xml == True:
            xml = schema40.tostring(metadata)
            outfile = open(str(idv) + ".xml", "w", encoding="utf8")
            outfile.write(xml)
