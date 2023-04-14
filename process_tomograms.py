import json
import os
import openai
import glob
from caltechdata_api import caltechdata_write
from iga.name_utils import split_name

openai.api_key = os.getenv("OPENAI_API_KEY")


def parse_collaborators(collaborator_string):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"""Take the string '{collaborator_string}', find the names and
    contributions, split the names into first and last names, and return in
    the format [ first_name ; last_name ; contribution , ... ]  :""",
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    contributors = []
    raw = response["choices"][0]["text"].split("\n\n")[1]
    for line in raw.split(","):
        split = line.strip("[]").split(";")
        contributors.append(split)
    formatted = []
    for c in contributors:
        formatted.append(
            {
                "nameType": "Personal",
                "familyName": c[1],
                "givenName": c[0],
                "contributorType": "Researcher",
            }
        )
    return formatted


directory = "jensen"
dataset = "gca2021-09-10-347"

files = glob.glob(f"{directory}/*.json")

for f in files:
    print(f)
    with open(f, "r") as infile:
        source = json.load(infile)
        annotation = source["annotation"][0]
        information = source["information"][0]

        metadata = {}
        metadata["identifiers"] = [
            {"identifier": annotation["tiltSeriesID"], "identifierType": "tiltid"}
        ]
        metadata["contributors"] = parse_collaborators(
            annotation["collaboratorsAndRoles"]
        )
        creators = []
        for name in information["dataTakenBy"]:
            creator = {
                "nameType": "Personal",
                "affiliation": [
                    {
                        "name": "Caltech",
                        "affiliationIdentifier": "https://ror.org/05dxps055",
                        "affiliationIdentifierScheme": "ROR",
                    }
                ],
            }
            clean = split_name(name["fullName"])
            creator["givenName"] = clean[0]
            creator["familyName"] = clean[1]
            creators.append(creator)
        metadata["creators"] = creators
        dates = []
        if "tiltSeriesDate" in information:
            dates.append(
                {"date": information["tiltSeriesDate"], "dateType": "Collected"}
            )
        if "timeAdded" in information:
            dates.append(
                {"date": information["timeAdded"].split(" ")[0], "dateType": "Created"}
            )
        if "lastModified" in information:
            dates.append(
                {
                    "date": information["lastModified"].split(" ")[0],
                    "dateType": "Updated",
                }
            )
        metadata["dates"] = dates
        descriptions = []
        title = annotation["descriptiveTitle"]
        descriptions.append(
            {
                "descriptionType": "Abstract",
                "description": f"Electron tomography files of {title} ",
            }
        )
        metadata["descriptions"] = descriptions
        print(metadata)
