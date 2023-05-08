import json
import os
import openai
import glob
import s3fs
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
        contributors.append(split)
    formatted = []
    for c in contributors:
        formatted.append(
            {
                "nameType": "Personal",
                "familyName": c[1].strip("' [']"),
                "givenName": c[0].strip("' [']"),
                "contributorType": "Researcher",
            }
        )
    return formatted


def create_detailed_description(information, annotation):
    keywords = []
    description = "<p>"
    sep = "</p><p>"
    s = "<strong>"
    e = "</strong>"
    if "tiltSeriesDate" in information:
        description += f'{s}Tilt Series Date:{e} {information["tiltSeriesDate"]}{sep}'
    if "dataTakenBy" in information:
        description += (
            f'{s}Data Taken By:{e} {information["dataTakenBy"][0]["fullName"]}{sep}'
        )
    if "species/Specimen" in information:
        species = information["species/Specimen"]
        if "name" in species:
            description += f'{s}Species / Specimen:{e} {information["Species/Specimen"]["name"]}{sep}'
        if "strain" in species:
            description += (
                f'{s}Strain:{e} {information["Species/Specimen"]["strain"]}{sep}'
            )
    if "tiltSeriesCollection" in information:
        settings = ""
        info = information["tiltSeriesCollection"][0]
        if "Tilt Scheme" in info:
            settings += f' {info["Tilt Scheme"]},'
            keywords.append(info["Tilt Scheme"])
        if "tiltRangeMin" in info:
            settings += (
                f' tilt range: ({info["tiltRangeMin"]}°, {info["tiltRangeMax"]}°),'
            )
        if "angularIncrement" in info:
            settings += f' step: {info["angularIncrement"]}°,'
        if "isAngularIncrementConstant" in info:
            if info["isAngularIncrementConstant"] == "yes":
                settings += " constant angular increment,"
            else:
                settings += " variable angular increment,"
        if "dosage" in info:
            settings += f' dosage: {info["dosage"]} eV/Å², '
        if "defocus" in info:
            settings += f' defocus: {info["defocus"]} μm, '
        if "magnification" in info:
            settings += f' magnification: {info["magnification"].split(".")[0]}x. '
        description += f"{s}Tilt Series Settings:{e} {settings}{sep}"
        if "Microscope" in info:
            if info["Microscope"] != "":
                description += f'{s}Microscope:{e} {info["Microscope"]}{sep}'
                keywords.append(info["Microscope"])
        if "acquisitionSoftware" in info:
            description += (
                f'{s}Acquisition Software:{e} {info["acquisitionSoftware"]}{sep}'
            )
            keywords.append(info["acquisitionSoftware"])
    if "uploadMethod" in information:
        description += f'{s}Upload Method:{e} {information["uploadMethod"]}{sep}'
        keywords.append(information["uploadMethod"])
    if "processingSoftwareUsed" in information:
        software = information["processingSoftwareUsed"]
        description += f"{s}Processing Software Used:{e} {software}{sep}"
        if "," in software:
            software = software.split(",")
        else:
            software = [software]
        for soft in software:
            keywords.append(soft)
    if "collaboratorsAndRoles" in annotation:
        description += (
            f'{s}Collaborators and Roles:{e} {annotation["collaboratorsAndRoles"]}{sep}'
        )
    if "purificationGrowthConditionsTreatment" in annotation:
        description += f'{s}Purification / Growth Conditions / Treatment:{e} {annotation["purificationGrowthConditionsTreatment"]}{sep}'
    if "description" in annotation:
        description += f'{s}Notes:{e} {annotation["description"]}{sep}'
    if "samplePreparation" in annotation:
        if annotation["samplePreparation"] != "":
            description += (
                f'{s}Sample Preparation:{e} {annotation["samplePreparation"]}{sep}'
            )
    return description, keywords


def get_formats(files, embargoed):
    formats = []
    file_paths = []
    file_links = []
    file_descriptions = []
    additional_description = ""
    upload = ["mp4", "jpg", "jpeg"]
    for f in files:
        name = f["fileName"]
        location = f["fileLocation"]
        desc = ""
        s3path = location.replace(
            "/jdatabase/tomography/data/",
            "https://renc.osn.xsede.org/ini210004tommorrell/tomography_archive/",
        )
        fpath = location.replace(
            "/jdatabase/tomography/data/",
            "ini210004tommorrell/tomography_archive/",
        )
        formatn = name.split(".")[-1]
        formats.append(formatn)
        if formatn in upload:
            if embargoed:
                os.system(
                    'scp "%s:%s%s" "%s"'
                    % ("jcontrol3.jensen.caltech.edu", location, name, name)
                )
                file_paths.append(name)
            else:
                file_paths.append(f"{fpath}{name}")
                if "fileNote" in f:
                    if f["fileNote"] != "":
                        additional_description += f' {name}: {f["fileNote"]}'
        else:
            file_links.append(f"{s3path}{name}")
            if "reconstruction" in f:
                rec = f["reconstruction"]
                if "pixelSize(nm)" in rec:
                    desc += f' Reconstruction (Pixel Size {rec["pixelSize(nm)"]} nm)'
                else:
                    desc += f" Reconstruction"
            if "rawTiltSeries" in f:
                raw = f["rawTiltSeries"]
                if "pixelSize(nm)" in raw:
                    desc += f' Tilt Series (Pixel Size {raw["pixelSize(nm)"]} nm)'
                else:
                    desc += f" Tilt Series"
            if "fileNote" in f:
                desc += f' {f["fileNote"]}'
            file_descriptions.append(desc)
    return formats, file_paths, file_links, file_descriptions, additional_description


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
        idv = annotation["tiltSeriesID"]
        # Pull out restricted records
        embargoed = False
        year = idv[3:7]
        if year == "2021" or year == "2022":
            print("embargoed")
            metadata["access"] = {
                "record": "public",
                "files": "restricted",
                "embargo": {"active": True, "until": "2024-06-01"},
            }
            embargoed = True
        metadata["identifiers"] = [{"identifier": idv, "identifierType": "tiltid"}]
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
        title = annotation["descriptiveTitle"]
        description, keywords = create_detailed_description(information, annotation)
        (
            formats,
            files,
            file_links,
            file_descriptions,
            additional_description,
        ) = get_formats(files, embargoed)
        descriptions = [
            {
                "descriptionType": "Abstract",
                "description": f"{description} {additional_description} </p>",
            }
        ]
        metadata["descriptions"] = descriptions
        if embargoed:
            # We don't add in file links
            f_text = "The fllowing raw files are currently embargoed:"
            index = 0
            for link in file_links:
                file = link.split("/")[-1]
                pathf = link.split("ini210004tommorrell/")[1]
                try:
                    desc = file_descriptions[index]
                except IndexError:
                    desc = ""
                f_text += f" {file}, {desc}, {pathf};"
                index += 1
            descriptions.append(
                {"descriptionType": "TechnicalInfo", "description": f_text}
            )
            file_links = []
        metadata["formats"] = formats
        metadata["fundingReferences"] = funding
        metadata["language"] = "eng"
        metadata["publicationYear"] = "2023"
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
            if k != "":
                subjects.append({"subject": k})
        metadata["subjects"] = subjects
        metadata["titles"] = [{"title": title}]
        community = "fe1c8afc-38eb-4634-85af-43cdad391d79"
        token = os.environ["RDMTOK"]
        endpoint = "https://renc.osn.xsede.org/"
        osn_s3 = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint})
        if embargoed:
            osn_s3 = None
        s3_link = (
            f"https://renc.osn.xsede.org/ini210004tommorrell/tomography_archive/{idv}"
        )
        result = caltechdata_write(
            metadata,
            token,
            files=files,
            s3=osn_s3,
            production=False,
            publish=True,
            file_links=file_links,
            file_descriptions=file_descriptions,
            community=community,
            s3_link=s3_link,
        )
        print(result)
