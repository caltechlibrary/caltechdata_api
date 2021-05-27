# Convert a DataCite 4 or 4.3 standard schema json record to the customized internal
# schema used by TIND in CaltechDATA
import argparse
import json
from datetime import date


def customize_schema(json_record, schema="40"):

    if schema == "40":
        return customize_schema_4(json_record)
    elif schema == "43":
        return customize_schema_43(json_record)
    else:
        raise ValueError(f"Error: schema {schema} not defined")


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
                json_record["doi"] = identifier['identifier']
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
            if "affiliation" in a:
                affiliations = []
                for aff in a["affiliation"]:
                    affiliations.append(aff["name"])
                new["affiliation"] = a["affiliation"]
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
            if 'funderIdentifier' in funding:
                funding['funderIdentifier'] = {'funderIdentifier':
                        funding['funderIdentifier']}


    # resourceTypeGeneral
    typeg = json_record["types"]["resourceTypeGeneral"]
    json_record["resourceType"] = {"resourceTypeGeneral": typeg}

    print(json_record)

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
        json_record["rightsList"] = licenses[0]
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
