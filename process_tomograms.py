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
    the format [ first_name ; last_name ; contribution ]  :""",
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
        print(split)
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


def create_detailed_description(information, files):
    keywords = []
    description = "Details of data collection: "
    keyword_labels = ["Microscope", "Tilt Scheme", "acquisitionSoftware"]
    if "tiltSeriesCollection" in information:
        info = information["tiltSeriesCollection"]
        for key in info:
            if key in keyword_labels:
                keywords.append({"subject": info[key]})
                description += f"{key}: {info[key]}"
    if "uploadMethod" in information:
        description += f'uploadMethod: {information["uploadMethod"]}'
        keywords.append(information["uploadMethod"])
    if "processingSoftwareUsed" in information:
        description += f'uploadMethod: {information["processingSoftwareUsed"]}'
        keywords.append(information["processingSoftwareUsed"])
    for f in files:
        if "reconstruction" in f:
            rec = f["reconstruction"]
            if "pixelSize(nm)" in rec:
                description += f'reconstructionPixelSize(nm): {rec["pixelSize(nm)"]}'
        if "rawTiltSeries" in f:
            raw = f["rawTiltSeries"]
            if "pixelSize(nm)" in raw:
                description += f'rawPixelSize(nm): {raw["pixelSize(nm)"]}'
    return description, keywords


def get_formats(files):
    formats = []
    for f in files:
        formats.append(f["fileName"].split(".")[-1])
    return formats


funding = [
    {"funderName": "NIH"},
    {"funderName": "HHMI"},
    {"funderName": "Beckman Institute"},
    {
        "funderIdentifier": "grid.452959.6",
        "funderIdentifierType": "GRID",
        "funderName": "Gordon and Betty Moore Foundation",
    },
    {
        "funderIdentifier": "grid.410514.5",
        "funderIdentifierType": "GRID",
        "funderName": "Agouron Institute",
    },
    {
        "funderIdentifier": "grid.452951.e",
        "funderIdentifierType": "GRID",
        "funderName": "John Templeton Foundation",
    },
]

directory = "jensen"

files = glob.glob(f"{directory}/*.json")

for f in files:
    print(f)
    with open(f, "r") as infile:
        source = json.load(infile)
        annotation = source["annotation"][0]
        information = source["information"][0]
        files = source["Files"]

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
        description, keywords = create_detailed_description(information, files)
        descriptions.append({"descriptionType": "Other", "description": description})
        metadata["descriptions"] = descriptions
        metadata["formats"] = get_formats(files)
        metadata["fundingReferences"] = funding
        metadata["language"] = "eng"
        metadata["publicationYear"] = 2023
        metadata["publisher"] = "CaltechDATA"
        metadata["types"] = {
            "resourceTypeGeneral": "Dataset",
            "resourceType": "Dataset",
        }
        metadata["rightsList"] = [{"rights": "cc-by-nc-4.0"}]
        if "species/Specimen" in information:
            for s in information["species/Specimen"]:
                keywords.append(s["name"])
        subjects = []
        for k in keywords:
            subjects.append({"subject": k})
        metadata["subjects"] = subjects
        metadata["titles"] = [{"title": title}]
        print(json.dumps(metadata))
