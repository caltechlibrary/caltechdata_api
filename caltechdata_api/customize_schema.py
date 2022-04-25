# Convert a DataCite 4 or 4.3 standard schema json record to the customized internal
# schema used by TIND in CaltechDATA
import argparse
import json
from datetime import date
import yaml
from pathlib import Path


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


def customize_schema(json_record, schema="40", pilot=False):

    if pilot:
        if schema == "43":
            return customize_schema_rdm(json_record)
        else:
            raise ValueError(f"Error: Pilot only supports schema 43")
    else:
        if schema == "40":
            return customize_schema_4(json_record)
        elif schema == "43":
            return customize_schema_43(json_record)
        else:
            raise ValueError(f"Error: schema {schema} not defined")


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
        change_label(cre, "nameIdentifiers", "identifiers")
        if "identifiers" in cre:
            for ide in cre["identifiers"]:
                change_label(ide, "nameIdentifier", "identifier")
                change_label(ide, "nameIdentifierScheme", "scheme")
                ide["scheme"] = ide["scheme"].lower()
        if "affiliation" in cre:
            aff_all = []
            # Using ROR as InvenioRDM ID needs to be verified to not break
            # things
            for aff in cre.pop("affiliation"):
                new_aff = {}
                if "affiliationIdentifierScheme" in aff:
                    identifier = aff["affiliationIdentifier"]
                    if aff["affiliationIdentifierScheme"] == "ROR":
                        if 'ror.org/' in identifier:
                            identifier = identifier.split('ror.org/')[1]
                        new_aff["id"] = identifier
                if new_aff == {}:
                    new_aff["name"] = aff["name"]
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
            date = d["date"]
            #Strip out any time imformation
            if ' ' in date:
                date = date.split(' ')[0]
            # If metadata has Submitted date, this gets priority
            if d["dateType"] == "Submitted":
                json_record["publication_date"] = date
            # If we have an Issued but not a Submitted date, this is
            # publication date
            elif d["dateType"] == "Issued":
                json_record["publication_date"] = date
            else:
                dtype = d.pop("dateType")
                d["type"] = {"id": datetypes[dtype]}
                d['date'] = date
                change_label(d, "dateInformation", "description")
                new.append(d)
        json_record["dates"] = new
    if 'publication_date' not in json_record:
        #A publication date isalways required
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
        #Only known language in data set; so no need to do vocabulary lookup
        if language == 'English':
            language = 'eng'
        json_record["languages"] = [{"id": language}]

    # Need to figure out mapping for system-managed DOIs
    if "identifiers" in json_record:
        identifiers = []
        for identifier in json_record["identifiers"]:
            if identifier["identifierType"] != "DOI":
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
            if "funderIdentifier" in fund:
                funder["identifier"] = fund["funderIdentifier"]
            if "funderIdentifierType" in fund:
                if fund["funderIdentifierType"] == "ROR":
                    funder["scheme"] = "ror"
                else:
                    print(f'Unknown Type mapping {fund["funderIdentifierType"]}')
            if "awardTitle" in fund:
                award["title"] = fund["awardTitle"]
            if "awardNumber" in fund:
                award["number"] = fund["awardNumber"]
            if "awardURI" in fund:
                award["identifier"] = fund["awardURI"]
            if funder != {}:
                combo["funder"] = funder
            if award != {}:
                combo["award"] = award
            new.append(combo)
        json_record["funding"] = new

    if "publicationYear" in json_record:
        json_record.pop("publicationYear")
    if "schemaVersion" in json_record:
        json_record.pop("schemaVersion")

    return {"metadata": json_record}


def customize_schema_4(json_record):
    json_record = customize_standard(json_record)
    # Extract identifier and label as DOI
    if "identifier" in json_record:
        identifier = json_record["identifier"]["identifier"]
        # Cound check identifierType for validation
        json_record["doi"] = identifier
        del json_record["identifier"]
        # will delete other ideintifiers in file

    # change author formatting
    # We're dropping URIs
    if "creators" in json_record:
        authors = json_record["creators"]
        newa = []
        for a in authors:
            new = {}
            if "affiliations" in a:
                if isinstance(a["affiliations"], list):
                    new["authorAffiliation"] = a["affiliations"]
                else:
                    new["authorAffiliation"] = [a["affiliations"]]
            new["authorName"] = a["creatorName"]
            if "nameIdentifiers" in a:
                idn = []
                for n in a["nameIdentifiers"]:
                    idn.append(
                        {
                            "authorIdentifier": n["nameIdentifier"],
                            "authorIdentifierScheme": n["nameIdentifierScheme"],
                        }
                    )
                new["authorIdentifiers"] = idn
            newa.append(new)
        json_record["authors"] = newa
        del json_record["creators"]

    # strip creator URI
    if "contributors" in json_record:
        newc = []
        for c in json_record["contributors"]:
            new = {}
            if "nameIdentifiers" in c:
                idn = []
                for n in c["nameIdentifiers"]:
                    idn.append(
                        {
                            "contributorIdentifier": n["nameIdentifier"],
                            "contributorIdentifierScheme": n["nameIdentifierScheme"],
                        }
                    )
                new["contributorIdentifiers"] = idn
            if "affiliations" in c:
                if isinstance(c["affiliations"], list):
                    new["contributorAffiliation"] = c["affiliations"]
                else:
                    new["contributorAffiliation"] = [c["affiliations"]]
            new["contributorName"] = c["contributorName"]
            if "contributorType" in c:
                new["contributorType"] = c["contributorType"]
            if "contributorEmail" in c:
                new["contributorEmail"] = c["contributorEmail"]
            newc.append(new)
        json_record["contributors"] = newc

    return json_record


def customize_schema_43(json_record):
    json_record = customize_standard(json_record)
    # Extract identifiers and label as DOI or alternativeIdentifiers
    if "identifiers" in json_record:
        alt = []
        for identifier in json_record["identifiers"]:
            if identifier["identifierType"] == "DOI":
                json_record["doi"] = identifier["identifier"]
            else:
                alt.append(identifier)
        if alt != []:
            json_record["alternativeIdentifiers"] = alt
        del json_record["identifiers"]

    # change author formatting
    # We're dropping URIs
    if "creators" in json_record:
        authors = json_record["creators"]
        newa = []
        for a in authors:
            new = {}
            if "affiliation" in a:
                affiliations = []
                for aff in a["affiliation"]:
                    affiliations.append(aff["name"])
                new["authorAffiliation"] = affiliations
                new["affiliation"] = a["affiliation"]
            new["authorName"] = a["name"]
            if "nameIdentifiers" in a:
                idn = []
                for n in a["nameIdentifiers"]:
                    idn.append(
                        {
                            "authorIdentifier": n["nameIdentifier"],
                            "authorIdentifierScheme": n["nameIdentifierScheme"],
                        }
                    )
                new["authorIdentifiers"] = idn
            newa.append(new)
        json_record["authors"] = newa
        del json_record["creators"]

    # strip creator URI
    if "contributors" in json_record:
        newc = []
        for c in json_record["contributors"]:
            new = {}
            if "nameIdentifiers" in c:
                idn = []
                for n in c["nameIdentifiers"]:
                    idn.append(
                        {
                            "contributorIdentifier": n["nameIdentifier"],
                            "contributorIdentifierScheme": n["nameIdentifierScheme"],
                        }
                    )
                new["contributorIdentifiers"] = idn
            if "affiliation" in c:
                affiliations = []
                for aff in c["affiliation"]:
                    affiliations.append(aff["name"])
                new["affiliation"] = c["affiliation"]
                new["contributorAffiliation"] = affiliations
            new["contributorName"] = c["name"]
            if "contributorType" in c:
                new["contributorType"] = c["contributorType"]
            if "contributorEmail" in c:
                new["contributorEmail"] = c["contributorEmail"]
            newc.append(new)
        json_record["contributors"] = newc

    # Funding organization
    if "fundingReferences" in json_record:
        for funding in json_record["fundingReferences"]:
            if "awardNumber" in funding:
                funding["awardNumber"] = {"awardNumber": funding["awardNumber"]}
            if "funderIdentifier" in funding:
                funding["funderIdentifier"] = {
                    "funderIdentifier": funding["funderIdentifier"]
                }

    # resourceTypeGeneral
    typeg = json_record["types"]["resourceTypeGeneral"]
    json_record["resourceType"] = {"resourceTypeGeneral": typeg}

    return json_record


def customize_standard(json_record):

    # Extract subjects to single string
    if "subjects" in json_record:
        subjects = json_record["subjects"]
        subs = []
        for s in subjects:
            subs.append(s["subject"])
        json_record["subjects"] = subs

    # Extract description
    if "descriptions" in json_record:
        for d in json_record["descriptions"]:
            d["descriptionValue"] = d["description"]
            del d["description"]

    # Extract title
    if "titles" in json_record:
        titles = json_record["titles"]
        for t in titles:
            if "titleType" not in t:
                json_record["title"] = t["title"]
        del json_record["titles"]

    # Language - only translating english
    if "language" in json_record:
        if json_record["language"] == "en":
            json_record["language"] = "eng"

    # Change related identifier labels
    if "relatedIdentifiers" in json_record:
        for listing in json_record["relatedIdentifiers"]:
            listing["relatedIdentifierRelation"] = listing.pop("relationType")
            listing["relatedIdentifierScheme"] = listing.pop("relatedIdentifierType")

    # format
    if "formats" in json_record:
        json_record["format"] = json_record.pop("formats")

    # dates
    if "publicationYear" in json_record:
        json_record["publicationDate"] = str(json_record.pop("publicationYear"))

    if "dates" in json_record:
        dates = json_record["dates"]
        for d in dates:
            # If metadata has Submitted date, we can get a full date in TIND
            if d["dateType"] == "Submitted":
                json_record["publicationDate"] = d["date"]
            # If we have an Issued but not a Submitted date, save full date
            elif d["dateType"] == "Issued":
                json_record["publicationDate"] = d["date"]
            d["relevantDateValue"] = str(d.pop("date"))
            d["relevantDateType"] = d.pop("dateType")
        json_record["relevantDates"] = json_record.pop("dates")
    else:
        json_record["publicationDate"] = date.today().isoformat()

    # license
    if "rightsList" in json_record:
        licenses = json_record["rightsList"]
        # Should check acceptable licenses
        # if licenses[0]['rights'] == 'TCCON Data Use Policy':
        #    json_record['license'] = 'other-license'
        # else:
        # if licenses[0]['rights'] == 'public-domain':
        #    licenses[0]['rights'] = 'other'
        #Only transfer the first license
        lic = licenses[0]
        if 'rightsUri' in lic:
            #4.3 capitalization correction
            lic['rightsURI'] = lic.pop('rightsUri')
        json_record["rightsList"] = lic
        # Only transfers first license

    # Geo
    if "geoLocations" in json_record:
        for g in json_record["geoLocations"]:
            if "geoLocationPoint" in g:
                g["geoLocationPoint"]["pointLatitude"] = str(
                    g["geoLocationPoint"]["pointLatitude"]
                )
                g["geoLocationPoint"]["pointLongitude"] = str(
                    g["geoLocationPoint"]["pointLongitude"]
                )
            if "geoLocationBox" in g:
                g["geoLocationBox"]["northBoundLatitude"] = str(
                    g["geoLocationBox"]["northBoundLatitude"]
                )
                g["geoLocationBox"]["southBoundLatitude"] = str(
                    g["geoLocationBox"]["southBoundLatitude"]
                )
                g["geoLocationBox"]["eastBoundLongitude"] = str(
                    g["geoLocationBox"]["eastBoundLongitude"]
                )
                g["geoLocationBox"]["westBoundLongitude"] = str(
                    g["geoLocationBox"]["westBoundLongitude"]
                )
        json_record["geographicCoverage"] = json_record.pop("geoLocations")

    # Publisher
    if "publisher" in json_record:
        publisher = {}
        publisher["publisherName"] = json_record.pop("publisher")
        json_record["publishers"] = publisher

    # print(json.dumps(json_record))
    return json_record


if __name__ == "__main__":
    # Read in from file for demo purposes

    parser = argparse.ArgumentParser(
        description="customize_schema converts a DataCite 4 or 4.3 standard json record\
                to TIND customized internal schema in CaltechDATA"
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
