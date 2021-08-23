# Convert a internal TIND CaltechDATA record into a  DataCite 4 or 4.3 standard schema json record
import argparse
import json


def decustomize_schema(
    json_record, pass_emails=False, pass_media=False, pass_owner=False, schema="4"
):
    if schema == "4":
        return decustomize_schema_4(json_record, pass_emails, pass_media, pass_owner)
    elif schema == "40":
        return decustomize_schema_4(json_record, pass_emails, pass_media, pass_owner)
    elif schema == "43":
        return decustomize_schema_43(json_record, pass_emails, pass_media, pass_owner)
    else:
        raise ValueError(f"Error: schema {schema} not defined")


def decustomize_standard(json_record, pass_emails, pass_media, pass_owner):

    # If passed a direct API json blob, extract metadata section
    if "metadata" in json_record:
        json_record = json_record["metadata"]

    # Extract subjects to single string
    if "subjects" in json_record:
        if isinstance(json_record["subjects"], str):
            subjects = json_record["subjects"].split(",")
            array = []
            for s in subjects:
                array.append({"subject": s})
            json_record["subjects"] = array
        else:
            array = []
            for s in json_record["subjects"]:
                array.append({"subject": s})
            json_record["subjects"] = array

    # Extract title
    if "title" in json_record:
        json_record["titles"] = [{"title": json_record["title"]}]
        del json_record["title"]

    # Change related identifier labels
    if "relatedIdentifiers" in json_record:
        for listing in json_record["relatedIdentifiers"]:
            listing["relationType"] = listing.pop("relatedIdentifierRelation")
            listing["relatedIdentifierType"] = listing.pop("relatedIdentifierScheme")

    # Publication is effectivly a related identifier
    if "publications" in json_record:
        if "publicationIDs" in json_record["publications"]:
            doi = json_record["publications"]["publicationIDs"]["publicationIDNumber"]
            relation = {
                "relatedIdentifier": doi,
                "relatedIdentifierType": "DOI",
                "relationType": "IsSupplementTo",
            }
            if "relatedIdentifiers" in json_record:
                existing = False
                for rec in json_record["relatedIdentifiers"]:
                    if doi == rec["relatedIdentifier"]:
                        existing = True
                if existing == False:
                    json_record["relatedIdentifiers"].append(relation)
            else:
                json_record["relatedIdentifiers"] = [relation]
        del json_record["publications"]

    # format
    if "format" in json_record:
        if isinstance(json_record["format"], list):
            json_record["formats"] = json_record.pop("format")
        else:
            json_record["formats"] = [json_record.pop("format")]

    # dates
    datetypes = set()
    # Save set of types for handling publicationDate
    if "relevantDates" in json_record:
        dates = json_record["relevantDates"]
        for d in dates:
            d["date"] = d.pop("relevantDateValue")
            d["dateType"] = d.pop("relevantDateType")
            datetypes.add(d["dateType"])
        json_record["dates"] = json_record.pop("relevantDates")

    # Set publicationYear and save publicationDate
    if "publicationDate" in json_record:
        # If 'Issued' date type was not manually set in metadata
        # the system created publicationDate is correct
        if "Issued" not in datetypes:
            if "dates" in json_record:
                json_record["dates"].append(
                    {"date": json_record["publicationDate"], "dateType": "Issued"}
                )
            else:
                json_record["dates"] = [
                    {"date": json_record["publicationDate"], "dateType": "Issued"}
                ]
            year = json_record["publicationDate"].split("-")[0]
            json_record["publicationYear"] = year
        # Otherwise pick 'Issued' date for publicationYear
        else:
            for d in json_record["dates"]:
                if d["dateType"] == "Issued":
                    year = d["date"].split("-")[0]
                    json_record["publicationYear"] = year

        del json_record["publicationDate"]

    else:
        print(
            "No publication date set - something is odd with the record ", json_record
        )

    # Funding
    if "fundings" in json_record:
        # Metadata changes and all should all be DataCite standard
        # Clean out any residual issues
        # Legacy funding information (fundings) not transferred
        del json_record["fundings"]

    # Publisher
    if "publishers" in json_record:
        if isinstance(json_record["publishers"], list):
            json_record["publisher"] = json_record["publishers"][0]["publisherName"]
        else:
            json_record["publisher"] = json_record["publishers"]["publisherName"]
        del json_record["publishers"]
    else:
        json_record["publisher"] = "CaltechDATA"

    # description
    if "descriptions" in json_record:
        for d in json_record["descriptions"]:
            if "descriptionValue" in d:
                d["description"] = d.pop("descriptionValue")

    # change rightsList into array
    if "rightsList" in json_record:
        if not isinstance(json_record["rightsList"], list):
            json_record["rightsList"] = [json_record["rightsList"]]

    # Handle file info
    if pass_media == False:
        if "electronic_location_and_access" in json_record:
            del json_record["electronic_location_and_access"]

    others = [
        "files",
        "id",
        "control_number",
        "_oai",
        "_form_uuid",
        "access_right",
        "embargo_date",
        "license",
        "brief_authors",
        "brief_information_bar",
        "brief_subtitle",
        "brief_title",
        "brief_summary",
        "resource_type",
        "final_actions",
    ]
    if pass_owner == False:
        others.append("owners")
    for v in others:
        if v in json_record:
            del json_record[v]

    return json_record


def decustomize_schema_43(json_record, pass_emails, pass_media, pass_owner):
    # Do standard transformations
    json_record = decustomize_standard(json_record, pass_emails, pass_media, pass_owner)

    # Extract identifier and label as DOI
    identifiers = []
    if "doi" in json_record:
        doi = json_record["doi"]
        identifiers.append(
            {
                "identifier": json_record["doi"],
                "identifierType": "DOI",
            }
        )
        del json_record["doi"]

    # Extract resourceType into types
    if "resourceType" in json_record:
        json_record["types"] = json_record["resourceType"]
    if "resourceType" not in json_record["types"]:
        json_record["types"]["resourceType"] = json_record["resourceType"][
            "resourceTypeGeneral"
        ]
    del json_record["resourceType"]

    # Save CaltechDATA ID in all records
    identifiers.append(
        {
            "identifier": json_record["pid_value"],
            "identifierType": "CaltechDATA_Identifier",
        }
    )
    if "alternateIdentifiers" in json_record:
        for altid in json_record["alternateIdentifiers"]:
            if altid["alternateIdentifierType"] != "CaltechDATA_Identifier":
                identifiers.append(
                    {
                        "identifier": altid["alternateIdentifier"],
                        "identifierType": altid["alternateIdentifierType"],
                    }
                )
        del json_record["alternateIdentifiers"]
    del json_record["pid_value"]
    json_record["identifiers"] = identifiers

    # change author formatting
    if "authors" in json_record:
        authors = json_record["authors"]
        newa = []
        for a in authors:
            new = {}
            if "authorAffiliation" in a:
                # Prefer full affiliation block
                if "affiliation" in a:
                    new["affiliation"] = a["affiliation"]
                else:
                    if isinstance(a["authorAffiliation"], list) == False:
                        a["authorAffiliation"] = [a["authorAffiliation"]]
                    affiliation = []
                    for aff in a["authorAffiliation"]:
                        if isinstance(aff, dict):
                            affiliation.append(aff)
                        else:
                            affiliation.append({"name": aff})
                    new["affiliation"] = affiliation
            if "authorIdentifiers" in a:
                idv = []
                if isinstance(a["authorIdentifiers"], list):
                    for cid in a["authorIdentifiers"]:
                        nid = {}
                        nid["nameIdentifier"] = cid.pop("authorIdentifier")
                        nid["nameIdentifierScheme"] = cid.pop("authorIdentifierScheme")
                        idv.append(nid)
                    new["nameIdentifiers"] = idv
                else:
                    print("Author identifiers not an array - please check", doi)
                del a["authorIdentifiers"]
            new["name"] = a["authorName"]
            newa.append(new)
        json_record["creators"] = newa
        del json_record["authors"]

    # contributors
    if "contributors" in json_record:
        contributors = json_record["contributors"]
        newc = []
        for c in contributors:
            new = {}
            if "contributorAffiliation" in c:
                if "affiliation" in c:
                    new["affiliation"] = c["affiliation"]
                else:
                    if isinstance(c["contributorAffiliation"], list) == False:
                        c["contributorAffiliation"] = [c["contributorAffiliation"]]
                    affiliation = []
                    for aff in c["contributorAffiliation"]:
                        if isinstance(aff, dict):
                            affiliation.append(aff)
                        else:
                            affiliation.append({"name": aff})
                    new["affiliation"] = affiliation
            if "contributorIdentifiers" in c:
                if isinstance(c["contributorIdentifiers"], list):
                    newa = []
                    for cid in c["contributorIdentifiers"]:
                        nid = {}
                        nid["nameIdentifier"] = cid.pop("contributorIdentifier")
                        if "contributorIdentifierScheme" in cid:
                            nid["nameIdentifierScheme"] = cid.pop(
                                "contributorIdentifierScheme"
                            )
                        newa.append(nid)
                    new["nameIdentifiers"] = newa
                else:
                    print("Contributor identifier not an array - please check", doi)
                del c["contributorIdentifiers"]
            new["name"] = c["contributorName"]
            new["contributorType"] = c["contributorType"]
            if pass_emails == True:
                if "contributorEmail" in c:
                    new["contributorEmail"] = c["contributorEmail"]
            newc.append(new)
        json_record["contributors"] = newc

    # Geo - as strings
    if "geographicCoverage" in json_record:
        geo = json_record["geographicCoverage"]
        if isinstance(geo, list):
            # We have the correct formatting
            for g in geo:
                if "geoLocationPoint" in g:
                    pt = g["geoLocationPoint"]
                    if isinstance(pt, list):
                        newp = {}
                        newp["pointLatitude"] = pt[0]["pointLatitude"]
                        newp["pointLongitude"] = pt[0]["pointLongitude"]
                        g["geoLocationPoint"] = newp
                    else:
                        pt["pointLatitude"] = pt["pointLatitude"]
                        pt["pointLongitude"] = pt["pointLongitude"]
                if "geoLocationBox" in g:
                    bx = g["geoLocationBox"]
                    newp = {}
                    newp["southBoundLatitude"] = bx["southBoundLatitude"]
                    newp["northBoundLatitude"] = bx["northBoundLatitude"]
                    newp["eastBoundLongitude"] = bx["eastBoundLongitude"]
                    newp["westBoundLongitude"] = bx["westBoundLongitude"]
                    g["geoLocationBox"] = newp
            json_record["geoLocations"] = json_record.pop("geographicCoverage")
        else:
            newgeo = {}
            if "geoLocationPlace" in geo:
                newgeo["geoLocationPlace"] = geo["geoLocationPlace"]
            if "geoLocationPoint" in geo:
                pt = geo["geoLocationPoint"][0]
                newpt = {}
                newpt["pointLatitude"] = pt["pointLatitude"]
                newpt["pointLongitude"] = pt["pointLongitude"]
                newgeo["geoLocationPoint"] = newpt
            json_record["geoLocations"] = [newgeo]
            del json_record["geographicCoverage"]

    # Funding
    if "fundingReferences" in json_record:
        for fund in json_record["fundingReferences"]:
            if "funderIdentifier" in fund:
                identifier = fund.pop("funderIdentifier")
                if "funderIdentifierType" in identifier:
                    fund["funderIdentifierType"] = identifier["funderIdentifierType"]
                if "funderIdentifier" in identifier:
                    fund["funderIdentifier"] = identifier["funderIdentifier"]
            if "awardNumber" in fund:
                number = fund.pop("awardNumber")
                if "awardURI" in number:
                    fund["awardURI"] = number["awardURI"]
                if "awardNumber" in number:
                    fund["awardNumber"] = number["awardNumber"]

    json_record["schemaVersion"] = "http://datacite.org/schema/kernel-4"

    return json_record


def decustomize_schema_4(json_record, pass_emails, pass_media, pass_owner):
    # Do standard transformations
    json_record = decustomize_standard(json_record, pass_emails, pass_media, pass_owner)

    # Extract identifier and label as DOI
    if "doi" in json_record:
        doi = json_record["doi"]
        json_record["identifier"] = {
            "identifier": json_record["doi"],
            "identifierType": "DOI",
        }
        del json_record["doi"]

    # change author formatting
    # Could do better with multiple affiliations
    if "authors" in json_record:
        authors = json_record["authors"]
        newa = []
        for a in authors:
            new = {}
            if "authorAffiliation" in a:
                if isinstance(a["authorAffiliation"], list):
                    new["affiliations"] = a["authorAffiliation"]
                else:
                    new["affiliations"] = [a["authorAffiliation"]]
            if "authorIdentifiers" in a:
                idv = []
                if isinstance(a["authorIdentifiers"], list):
                    for cid in a["authorIdentifiers"]:
                        nid = {}
                        nid["nameIdentifier"] = cid.pop("authorIdentifier")
                        nid["nameIdentifierScheme"] = cid.pop("authorIdentifierScheme")
                        idv.append(nid)
                    new["nameIdentifiers"] = idv
                else:
                    print("Author identifiers not an array - please check", doi)
                del a["authorIdentifiers"]
            new["creatorName"] = a["authorName"]
            newa.append(new)
        json_record["creators"] = newa
        del json_record["authors"]

    # contributors
    if "contributors" in json_record:
        for c in json_record["contributors"]:
            if "contributorAffiliation" in c:
                if isinstance(c["contributorAffiliation"], list):
                    c["affiliations"] = c.pop("contributorAffiliation")
                else:
                    c["affiliations"] = [c.pop("contributorAffiliation")]
            if "contributorIdentifiers" in c:
                if isinstance(c["contributorIdentifiers"], list):
                    newa = []
                    for cid in c["contributorIdentifiers"]:
                        nid = {}
                        nid["nameIdentifier"] = cid.pop("contributorIdentifier")
                        if "contributorIdentifierScheme" in cid:
                            nid["nameIdentifierScheme"] = cid.pop(
                                "contributorIdentifierScheme"
                            )
                        newa.append(nid)
                    c["nameIdentifiers"] = newa
                else:
                    print("Contributor identifier not an array - please check", doi)
                del c["contributorIdentifiers"]
            if pass_emails == False:
                if "contributorEmail" in c:
                    del c["contributorEmail"]

    # Geo - as floats
    if "geographicCoverage" in json_record:
        geo = json_record["geographicCoverage"]
        if isinstance(geo, list):
            # We have the correct formatting
            for g in geo:
                if "geoLocationPoint" in g:
                    pt = g["geoLocationPoint"]
                    if isinstance(pt, list):
                        newp = {}
                        newp["pointLatitude"] = float(pt[0]["pointLatitude"])
                        newp["pointLongitude"] = float(pt[0]["pointLongitude"])
                        g["geoLocationPoint"] = newp
                    else:
                        pt["pointLatitude"] = float(pt["pointLatitude"])
                        pt["pointLongitude"] = float(pt["pointLongitude"])
                if "geoLocationBox" in g:
                    bx = g["geoLocationBox"]
                    newp = {}
                    newp["southBoundLatitude"] = float(bx["southBoundLatitude"])
                    newp["northBoundLatitude"] = float(bx["northBoundLatitude"])
                    newp["eastBoundLongitude"] = float(bx["eastBoundLongitude"])
                    newp["westBoundLongitude"] = float(bx["westBoundLongitude"])
                    g["geoLocationBox"] = newp
            json_record["geoLocations"] = json_record.pop("geographicCoverage")
        else:
            newgeo = {}
            if "geoLocationPlace" in geo:
                newgeo["geoLocationPlace"] = geo["geoLocationPlace"]
            if "geoLocationPoint" in geo:
                pt = geo["geoLocationPoint"][0]
                newpt = {}
                newpt["pointLatitude"] = float(pt["pointLatitude"])
                newpt["pointLongitude"] = float(pt["pointLongitude"])
                newgeo["geoLocationPoint"] = newpt
            json_record["geoLocations"] = [newgeo]
            del json_record["geographicCoverage"]

    # Save CaltechDATA ID in all records
    idv = {
        "alternateIdentifier": json_record["pid_value"],
        "alternateIdentifierType": "CaltechDATA_Identifier",
    }
    existing = False
    if "alternateIdentifiers" in json_record:
        for altid in json_record["alternateIdentifiers"]:
            if altid["alternateIdentifierType"] == "CaltechDATA_Identifier":
                existing = True
        if existing == False:
            json_record["alternateIdentifiers"].append(idv)
    else:
        json_record["alternateIdentifiers"] = [idv]
    del json_record["pid_value"]

    return json_record


if __name__ == "__main__":
    # Read in from file for demo purposes

    parser = argparse.ArgumentParser(
        description="decustomize_schema converts a internal TIND CaltechDATA record\
       into a  DataCite 4 standard schema json record"
    )
    parser.add_argument("json_files", nargs="+", help="json file name")
    args = parser.parse_args()

    for jfile in args.json_files:
        infile = open(jfile, "r")
        data = json.load(infile)
        new = decustomize_schema(data)
        with open("formatted.json", "w") as outfile:
            json.dump(new, outfile)
        # print(json.dumps(new))
