import argparse
import csv
import json
import os

import requests
from datacite import schema40, schema43

from caltechdata_api import decustomize_schema


def get_files(idv, production=True, output=None):
    # Returns file block or writes csv file

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

    files = metadata["electronic_location_and_access"]

    if output:
        outfile = open(output, "w")
        writer = csv.writer(outfile)
        writer.writerow(["file_name", "file_size", "url", "embargo_status"])
        for filem in files:
            url = filem["uniform_resource_identifier"]
            name = filem["electronic_name"][0]
            writer.writerow([name, filem["file_size"], url, filem["embargo_status"]])

    return files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="get_files queries the caltechDATA (Invenio 3) API\
    and returns file information in a csv file"
    )
    parser.add_argument(
        "ids",
        metavar="ID",
        type=int,
        nargs="+",
        help="The CaltechDATA ID for each record of interest",
    )
    parser.add_argument("-test", dest="production", action="store_false")
    parser.add_argument("-csv", dest="csv_file")

    args = parser.parse_args()

    production = args.production
    csv_file = args.csv_file

    for idv in args.ids:
        metadata = get_files(idv, production, csv_file)
