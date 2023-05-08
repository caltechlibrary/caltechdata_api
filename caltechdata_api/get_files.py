import argparse
import requests


def get_files(idv, production=True):
    # Returns file block

    if production == True:
        api_url = "https://data.caltech.edu/api/records/"
    else:
        api_url = "https://data.caltechlibrary.dev/api/records/"

    r = requests.get(api_url + str(idv) + "/files")
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
    if not "entries" in r_data:
        raise AssertionError("expected as entries property in response, got " + r_data)
    return r_data["entries"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="get_files queries the caltechDATA (Invenio 3) API\
    and returns file information"
    )
    parser.add_argument(
        "ids",
        metavar="ID",
        type=str,
        nargs="+",
        help="The CaltechDATA ID for each record of interest",
    )
    parser.add_argument("-test", dest="production", action="store_false")

    args = parser.parse_args()

    production = args.production

    for idv in args.ids:
        metadata = get_files(idv, production)
        print(metadata)
