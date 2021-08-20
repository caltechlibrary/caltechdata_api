import argparse
import csv
import json
import os

import requests
from datacite import schema40, schema43

from caltechdata_api import decustomize_schema


def get_metadata(idv, production=True, validate=True, emails=False, schema="40"):
    # Returns just DataCite metadata or DataCite metadata with emails

    if production == True:
        api_url = "https://data.caltech.edu/api/record/"
    else:
        api_url = "https://cd-sandbox.tind.io/api/record/"

    r = requests.get(api_url + str(idv))
    r_data = r.json()
    if "message" in r_data:
        raise AssertionError(
            "id "
            + str(idv)
            + " expected http status 200, got "
            + str(r.status_code)
            + " "
            + r_data["message"]
        )
    if not "metadata" in r_data:
        raise AssertionError("expected as metadata property in response, got " + r_data)
    metadata = r_data["metadata"]

    if emails == True:
        metadata = decustomize_schema(metadata, pass_emails=True, schema=schema)
    else:
        metadata = decustomize_schema(metadata, schema=schema)
        if validate:
            if schema == "40":
                try:
                    assert schema40.validate(metadata)
                except AssertionError:
                    v = schema40.validator.validate(metadata)
                    errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
                    for error in errors:
                        print(error.message)
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
        type=int,
        nargs="+",
        help="The CaltechDATA ID for each record of interest",
    )
    parser.add_argument("-emails", dest="emails", action="store_true")
    parser.add_argument("-test", dest="production", action="store_false")
    parser.add_argument("-xml", dest="save_xml", action="store_true")
    parser.add_argument(
        "-skip_validate",
        dest="skip_validate",
        action="store_true",
        help="skip validation of metadata",
    )
    parser.add_argument("-schema", default="40", help="Schema Version")

    args = parser.parse_args()

    production = args.production
    emails = args.emails
    schema = args.schema
    skip_validate = args.skip_validate
    if skip_validate:
        validate = False
    else:
        validate = True

    for idv in args.ids:
        metadata = get_metadata(idv, production, validate, emails, schema)
        outfile = open(str(idv) + ".json", "w")
        outfile.write(json.dumps(metadata))
        outfile.close()
        if args.save_xml == True:
            xml = schema40.tostring(metadata)
            outfile = open(str(idv) + ".xml", "w", encoding="utf8")
            outfile.write(xml)
