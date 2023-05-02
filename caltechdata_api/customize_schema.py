# Convert a DataCite 4 or 4.3 standard schema json record to the customized internal
# schema used by TIND in CaltechDATA
import argparse
import json
from datetime import date
import yaml
from pathlib import Path
import requests


def grid_to_ror(grid):
    # Temporary until InvenioRDM stops spitting out GRIDS
    # We manually handle some incorrect/redundant GRID Ids
    if grid == "grid.451078.f":
        ror = "00hm6j694"
    elif grid == "grid.5805.8":
        ror = "02en5vm52"
    else:
        url = f"https://api.ror.org/organizations?query.advanced=external_ids.GRID.all:{grid}"
        results = requests.get(url)
        ror = results.json()["items"][0]["id"]
        ror = ror.split("ror.org/")[1]
    return ror


def get_vocabularies():
    """Returns dictionary of vocabularies"""
    path = Path(__file__).parent
    vocab_file = path / "vocabularies.yaml"
    vocabularies = {}
    with open(vocab_file) as f:
        data = yaml.safe_load(f) or {}
        for id_, yaml_entry in data.items():
            individual_vocab = {}
            vocab_id = yaml_entry["pid-type"]
            data_file = path / yaml_entry["data-file"]
            with open(data_file) as fp:
                # Allow empty files
                data = yaml.safe_load(fp) or []
                for entry in data:
                    props = entry["props"]
                    if "datacite_general" in props:
                        # Resource type two layer vocab
                        datacite = (
                            props["datacite_general"] + ";" + props["datacite_type"]
                        )
                    else:
                        datacite = props["datacite"]
                    individual_vocab[datacite] = entry["id"]
            vocabularies[vocab_id] = individual_vocab
    return vocabularies


def customize_schema(json_record, schema="43"):

    if schema == "43":
        return customize_schema_rdm(json_record)
    else:
        raise ValueError(f"Error: We currently only support schema 43")


def change_label(json, from_label, to_label):
    if from_label in json:
        json[to_label] = json.pop(from_label)


def rdm_creators_contributors(person_list, peopleroles):
    new = []
    for cre in person_list:
        new_cre = {}
        if "nameType" in cre:
            ntype = cre.pop("nameType")
            if ntype == "Personal":
                cre["type"] = "personal"
            elif ntype == "Organizational":
                cre["type"] = "organizational"
            else:
                print(f"Name type {ntype} not known")
        else:
            # We default to organizational if not known
            cre["type"] = "personal"
        change_label(cre, "givenName", "given_name")
        change_label(cre, "familyName", "family_name")
        if "name" not in cre:
            cre["name"] = cre["family_name"] + "," + cre["given_name"]
        change_label(cre, "nameIdentifiers", "identifiers")
        if "identifiers" in cre:
            new_id = []
            for ide in cre["identifiers"]:
                change_label(ide, "nameIdentifier", "identifier")
                change_label(ide, "nameIdentifierScheme", "scheme")
                ide["scheme"] = ide["scheme"].lower()
                # We don't support researcher id at this time
                if ide["scheme"] != "researcherid":
                    new_id.append(ide)
            cre["identifiers"] = new_id
        if "affiliation" in cre:
            aff_all = []
            # Not all ROR identifiers are available in InvenioRDM
            missing = ["05sy8gb82"]
            for aff in cre.pop("affiliation"):
                new_aff = {}
                keep = True
                if "affiliationIdentifierScheme" in aff:
                    identifier = aff["affiliationIdentifier"]
                    if aff["affiliationIdentifierScheme"] == "ROR":
                        if "ror.org/" in identifier:
                            identifier = identifier.split("ror.org/")[1]
                        if identifier not in missing:
                            new_aff["id"] = identifier
                        # We retain the name, since it might be different than
                        # the ROR version
                        new_aff["name"] = aff["name"]
                    elif aff["affiliationIdentifierScheme"] == "N/A":
                        print("Discarding affiliation with N/A scheme")
                        keep = False
                if new_aff == {}:
                    new_aff["name"] = aff["name"]
                if aff["name"] == "":
                    keep = False
                if keep:
                    aff_all.append(new_aff)
            new_cre["affiliations"] = aff_all
        if "contributorType" in cre:
            new_cre["role"] = {"id": peopleroles[cre.pop("contributorType")]}
        new_cre["person_or_org"] = cre
        new.append(new_cre)
    return new


def customize_schema_rdm(json_record):

    # Get vocabularies used in InvenioRDM
    vocabularies = get_vocabularies()

    peopleroles = vocabularies["crr"]
    resourcetypes = vocabularies["rsrct"]
    descriptiontypes = vocabularies["dty"]
    datetypes = vocabularies["dat"]
    relationtypes = vocabularies["rlt"]
    titletypes = vocabularies["ttyp"]
    identifiertypes = vocabularies["idt"]

    # Resource types are stored in vocabulary as General;Type
    types = json_record.pop("types")
    if "resourceType" in types:
        if types["resourceTypeGeneral"] == types["resourceType"]:
            type_key = types["resourceTypeGeneral"] + ";"
        else:
            type_key = types["resourceTypeGeneral"] + ";" + types["resourceType"]
    else:
        type_key = types["resourceTypeGeneral"] + ";"
    json_record["resource_type"] = {"id": resourcetypes[type_key]}

    creators = json_record.pop("creators")
    json_record["creators"] = rdm_creators_contributors(creators, peopleroles)

    if "contributors" in json_record:
        contributors = json_record.pop("contributors")
        json_record["contributors"] = rdm_creators_contributors(
            contributors, peopleroles
        )

    titles = json_record.pop("titles")
    additional = []
    for title in titles:
        if "titleType" not in title:
            # If there are multiple titles without types, extras will be lost
            json_record["title"] = title["title"]
        else:
            new = {}
            new["type"] = {"id": titletypes[title["titleType"]]}
            new["title"] = title["title"]
            if "lang" in title:
                new["lang"] = {"id": title["lang"]}
            additional.append(new)
    if additional != []:
        json_record["additional_titles"] = additional

    descriptions = json_record.pop("descriptions")
    additional = []
    if len(descriptions) == 1:
        json_record["description"] = descriptions[0]["description"]
    else:
        for description in descriptions:
            if description["descriptionType"] == "Abstract":
                # If there are multiple Abstracts, extras will be lost
                json_record["description"] = description["description"]
            else:
                new = {}
                new["type"] = {"id": descriptiontypes[description["descriptionType"]]}
                new["description"] = description["description"]
                if "lang" in description:
                    new["lang"] = {"id": description["lang"]}
                additional.append(new)
    if additional != []:
        json_record["additional_descriptions"] = additional

    # dates
    if "dates" in json_record:
        dates = json_record["dates"]
        new = []
        for d in dates:
            datev = d["date"]
            # Strip out any time imformation
            if " " in datev:
                datev = datev.split(" ")[0]
            # If metadata has Submitted date, this gets priority
            if d["dateType"] == "Submitted":
                json_record["publication_date"] = datev
            # If we have an Issued but not a Submitted date, this is
            # publication date
            elif d["dateType"] == "Issued":
                json_record["publication_date"] = datev
            else:
                dtype = d.pop("dateType")
                d["type"] = {"id": datetypes[dtype]}
                d["date"] = datev
                change_label(d, "dateInformation", "description")
                new.append(d)
        json_record["dates"] = new
    if "publication_date" not in json_record:
        # A publication date is always required
        if "publicationYear" in json_record:
            json_record["publication_date"] = json_record.pop("publicationYear")
        else:
            json_record["publication_date"] = date.today().isoformat()

    if "subjects" in json_record:
        subjects = json_record.pop("subjects")
        new = []
        for subject in subjects:
            if "valueURI" in subject:
                # We assume the URI is a correct subject id for InvenioRDM
                new.append({"id": subject["valueURI"]})
            else:
                new.append(subject)
        json_record["subjects"] = new

    if "language" in json_record:
        language = json_record.pop("language")
        # Only known language in data set; so no need to do vocabulary lookup
        if language == "English":
            language = "eng"
        json_record["languages"] = [{"id": language}]

    if "identifiers" in json_record:
        identifiers = []
        system_pids = ["DOI", "oai"]
        for identifier in json_record["identifiers"]:
            if identifier["identifierType"] not in system_pids:
                identifier["scheme"] = identifiertypes[identifier.pop("identifierType")]
                identifiers.append(identifier)
        json_record["identifiers"] = identifiers

    if "relatedIdentifiers" in json_record:
        related = json_record.pop("relatedIdentifiers")
        new = []
        for identifier in related:
            change_label(identifier, "relatedIdentifier", "identifier")
            rel = identifier.pop("relatedIdentifierType")
            identifier["scheme"] = identifiertypes[rel]
            rel = identifier.pop("relationType")
            identifier["relation_type"] = {"id": relationtypes[rel]}
            if "resourceTypeGeneral" in identifier:
                rel = identifier.pop("resourceTypeGeneral")
                identifier["resource_type"] = {"id": resourcetypes[rel + ";"]}
            new.append(identifier)
        json_record["related_identifiers"] = new

    if "rightsList" in json_record:
        rights = json_record.pop("rightsList")
        new = []
        for right in rights:
            if "rightsIdentifier" in right:
                new.append({"id": right["rightsIdentifier"]})
            else:
                entry = {"title": {"en": right["rights"]}}
                if "rightsUri" in right:
                    link = right["rightsUri"]
                    entry["link"] = link
                new.append(entry)
        json_record["rights"] = new

    if "geoLocations" in json_record:
        locations = []
        for location in json_record.pop("geoLocations"):
            new = {}
            if "geoLocationPoint" in location:
                lat = location["geoLocationPoint"]["pointLatitude"]
                lon = location["geoLocationPoint"]["pointLongitude"]
                new["geometry"] = {"type": "Point", "coordinates": [lat, lon]}
            if "geoLocationBox" in location:
                south = float(location["geoLocationBox"]["southBoundLatitude"])
                north = float(location["geoLocationBox"]["northBoundLatitude"])
                east = float(location["geoLocationBox"]["eastBoundLongitude"])
                west = float(location["geoLocationBox"]["westBoundLongitude"])
                new["geometry"] = {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [north, east],
                            [north, west],
                            [south, west],
                            [south, east],
                            [north, east],
                        ]
                    ],
                }
            if "geoLocationPlace" in location:
                new["place"] = location["geoLocationPlace"]
        json_record["locations"] = {"features": [new]}

    if "fundingReferences" in json_record:
        funding = json_record.pop("fundingReferences")
        new = []
        for fund in funding:
            combo = {}
            funder = {}
            award = {}
            if "funderName" in fund:
                funder["name"] = fund["funderName"]
            if "funderIdentifierType" in fund:
                if fund["funderIdentifierType"] == "ROR":
                    ror = fund.pop("funderIdentifier")
                    if "ror.org" in ror:
                        ror = ror.split("ror.org/")[1]
                    funder["id"] = ror
                    fund.pop("funderIdentifierType")
                elif fund["funderIdentifierType"] == "GRID":
                    # We need this temporarily to round-trip data
                    ror = grid_to_ror(fund.pop("funderIdentifier"))
                    funder["id"] = ror
                    fund.pop("funderIdentifierType")
                else:
                    print(f'Unknown Type mapping {fund["funderIdentifierType"]}')
            if "awardTitle" in fund:
                award["title"] = {"en": fund["awardTitle"]}
            if "awardNumber" in fund:
                award["number"] = fund["awardNumber"]
            if "awardURI" in fund:
                award["identifier"] = fund["awardURI"]
            if funder != {}:
                combo["funder"] = funder
            if award != {}:
                if "id" not in award:
                    if "title" not in award:
                        award["title"] = {"en": ":unav"}
                    if "number" not in award:
                        award["title"] = ":unav"
                    combo["award"] = award
            new.append(combo)
        json_record["funding"] = new

    if "publicationYear" in json_record:
        json_record.pop("publicationYear")
    if "schemaVersion" in json_record:
        json_record.pop("schemaVersion")

    # Now prep the final structure
    final = {}
    # Not technically DataCite, but owner info neded for record transfer
    parent = {}
    if "owners" in json_record:
        parent = {"access": {"owned_by": [{"user": json_record["owners"][0]}]}}
    # Not technically dataset, but transfer community information
    if "community" in json_record:
        com = json_record.pop("community")
        parent["communities"] = {"ids": [com], "default": com}
    final["parent"] = parent
    # Not technically datacite, but transfer pids information
    if "pids" in json_record:
        final["pids"] = json_record.pop("pids")
    # Not technically datacite, but transfer access information
    if "access" in json_record:
        final["access"] = json_record.pop("access")
    # Now we should just have clear metadata left
    final["metadata"] = json_record

    return final


if __name__ == "__main__":
    # Read in from file for demo purposes

    parser = argparse.ArgumentParser(
        description="customize_schema converts a DataCite 4.3 standard json record\
                to a InvenioRDM schema for CaltechDATA"
    )
    parser.add_argument("json_files", nargs="+", help="json file name")
    args = parser.parse_args()

    for jfile in args.json_files:
        infile = open(jfile, "r")
        data = json.load(infile)
        new = customize_schema(data)
        with open("formatted.json", "w") as outfile:
            json.dump(new, outfile)
        # print(json.dumps(new))
