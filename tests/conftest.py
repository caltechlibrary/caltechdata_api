import pytest


@pytest.fixture(scope="function")
def full_datacite43_record():
    return {
        "types": {"resourceTypeGeneral": "Image", "resourceType": "Photo"},
        "creators": [
            {
                "name": "Nielsen, Lars Holm",
                "nameType": "Personal",
                "givenName": "Lars Holm",
                "familyName": "Nielsen",
                "nameIdentifiers": [
                    {
                        "nameIdentifier": "0000-0001-8135-3489",
                        "nameIdentifierScheme": "ORCID",
                    }
                ],
                "affiliation": [
                    {"name": "free-text"},
                    {
                        "name": "CERN",
                        "affiliationIdentifier": "01ggx4157",
                        "affiliationIdentifierScheme": "ROR",
                    },
                ],
            }
        ],
        "titles": [
            {"title": "InvenioRDM"},
            {
                "title": "a research data management platform",
                "titleType": "Subtitle",
                "lang": "eng",
            },
        ],
        "publisher": "InvenioRDM",
        "publicationYear": "2018",
        "subjects": [
            {"subject": "custom"},
            {
                "subject": "Abdominal Injuries",
                "subjectScheme": "MeSH",
                "valueURI": "http://id.nlm.nih.gov/mesh/A-D000007",
            },
        ],
        "contributors": [
            {
                "name": "Nielsen, Lars Holm",
                "nameType": "Personal",
                "contributorType": "Other",
                "givenName": "Lars Holm",
                "familyName": "Nielsen",
                "nameIdentifiers": [
                    {
                        "nameIdentifier": "0000-0001-8135-3489",
                        "nameIdentifierScheme": "ORCID",
                    }
                ],
                "affiliation": [
                    {
                        "name": "CERN",
                        "affiliationIdentifier": "01ggx4157",
                        "affiliationIdentifierScheme": "ROR",
                    }
                ],
            }
        ],
        "dates": [
            {"date": "2018/2020-09", "dateType": "Issued"},
            {"date": "1939/1945", "dateType": "Other", "dateInformation": "A date"},
        ],
        "language": "dan",
        "identifiers": [
            {"identifier": "10.5281/inveniordm.1234", "identifierType": "DOI"},
            {"identifier": "1924MNRAS..84..308E", "identifierType": "bibcode"},
        ],
        "relatedIdentifiers": [
            {
                "relatedIdentifier": "10.1234/foo.bar",
                "relatedIdentifierType": "DOI",
                "relationType": "IsCitedBy",
                "resourceTypeGeneral": "Dataset",
            }
        ],
        "sizes": ["11 pages"],
        "formats": ["application/pdf"],
        "version": "v1.0",
        "rightsList": [
            {
                "rights": "A custom license",
                "rightsUri": "https://customlicense.org/licenses/by/4.0/",
            },
            {"rights": "No rightsUri license"},
            {
                "rights": "Creative Commons Attribution 4.0 International",
                "rightsIdentifierScheme": "spdx",
                "rightsIdentifier": "cc-by-4.0",
                "rightsUri": "https://creativecommons.org/licenses/by/4.0/" "legalcode",
            },
        ],
        "descriptions": [
            {
                "description": "<h1>A description</h1> <p>with HTML tags</p>",
                "descriptionType": "Abstract",
            },
            {"description": "Bla bla bla", "descriptionType": "Methods", "lang": "eng"},
        ],
        "geoLocations": [
            {
                "geoLocationPoint": {
                    "pointLatitude": -32.94682,
                    "pointLongitude": -60.63932,
                },
                "geoLocationPlace": "test location place",
            }
        ],
        "fundingReferences": [
            {
                "funderName": "European Commission",
                "funderIdentifier": "00k4n6c32",
                "funderIdentifierType": "ROR",
                "awardTitle": "OpenAIRE",
                "awardNumber": "246686",
                "awardURI": ".../246686",
            }
        ],
        "schemaVersion": "http://datacite.org/schema/kernel-4",
    }


@pytest.fixture(scope="function")
def full_rdm_record():
    """Full record data from DataCite as dict coming from the external world."""
    return {
        "metadata": {
            "resource_type": {"id": "image-photo"},
            "creators": [
                {
                    "person_or_org": {
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                        "given_name": "Lars Holm",
                        "family_name": "Nielsen",
                        "identifiers": [
                            {"scheme": "orcid", "identifier": "0000-0001-8135-3489"}
                        ],
                    },
                    "affiliations": [{"name": "free-text"}, {"id": "01ggx4157"}],
                }
            ],
            "title": "InvenioRDM",
            "additional_titles": [
                {
                    "title": "a research data management platform",
                    "type": {"id": "subtitle"},
                    "lang": {"id": "eng"},
                }
            ],
            "publisher": "InvenioRDM",
            "publication_date": "2018/2020-09",
            "subjects": [
                {"subject": "custom"},
                {"id": "http://id.nlm.nih.gov/mesh/A-D000007"},
            ],
            "contributors": [
                {
                    "person_or_org": {
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                        "given_name": "Lars Holm",
                        "family_name": "Nielsen",
                        "identifiers": [
                            {"scheme": "orcid", "identifier": "0000-0001-8135-3489"}
                        ],
                    },
                    "role": {"id": "other"},
                    "affiliations": [{"id": "01ggx4157"}],
                }
            ],
            "dates": [
                {"date": "1939/1945", "type": {"id": "other"}, "description": "A date"}
            ],
            "languages": [{"id": "dan"}],
            "identifiers": [{"identifier": "1924MNRAS..84..308E", "scheme": "bibcode"}],
            "related_identifiers": [
                {
                    "identifier": "10.1234/foo.bar",
                    "scheme": "doi",
                    "relation_type": {"id": "iscitedby"},
                    "resource_type": {"id": "dataset"},
                }
            ],
            "sizes": ["11 pages"],
            "formats": ["application/pdf"],
            "version": "v1.0",
            "rights": [
                {
                    "title": {"en": "A custom license"},
                    "link": "https://customlicense.org/licenses/by/4.0/",
                },
                {
                    "title": {"en": "No rightsUri license"},
                },
                {"id": "cc-by-4.0"},
            ],
            "description": "<h1>A description</h1> <p>with HTML tags</p>",
            "additional_descriptions": [
                {
                    "description": "Bla bla bla",
                    "type": {"id": "methods"},
                    "lang": {"id": "eng"},
                }
            ],
            "locations": {
                "features": [
                    {
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-32.94682, -60.63932],
                        },
                        "place": "test location place",
                    }
                ]
            },
            "funding": [
                {
                    "funder": {
                        "name": "European Commission",
                        "identifier": "00k4n6c32",
                        "scheme": "ror",
                    },
                    "award": {
                        "title": "OpenAIRE",
                        "number": "246686",
                        "identifier": ".../246686",
                    },
                }
            ],
        }
    }
