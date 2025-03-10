import pytest

@pytest.fixture(scope="function")
def full_datacite43_record():
    return {
        "types": {"resourceTypeGeneral": "Dataset", "resourceType": ""},
        "creators": [
            {
                "name": "Reid-McLaughlin, Auden",
                "nameType": "Personal",
                "givenName": "Auden",
                "familyName": "Reid-McLaughlin",
                "nameIdentifiers": [
                    {
                        "nameIdentifier": "0009-0004-5513-2817",
                        "nameIdentifierScheme": "ORCID",
                    }
                ],
                "affiliation": [
                    {
                        "name": "California Institute of Technology",
                        "affiliationIdentifier": "05dxps055",
                        "affiliationIdentifierScheme": "ROR",
                    }
                ],
            }
        ],
        "titles": [
            {
                "title": "South Pole Shot Stacks for Constraining Temperature and Sedimentary Conditions under the South Pole with Distributed Acoustic Sensing (Reid-McLaughlin et al.)"
            }
        ],
        "publisher": "CaltechDATA",
        "publicationYear": "2025",
        "dates": [
            {"date": "2025-03-06", "dateType": "Issued"}
        ],
        "identifiers": [
            {"identifier": "10.22002/6x9nn-n3559", "identifierType": "DOI"},
            {"identifier": "oai:data.caltech.edu:6x9nn-n3559", "identifierType": "oai"},
        ],
        "rightsList": [
            {
                "rights": "Creative Commons Zero v1.0 Universal",
                "rightsIdentifier": "cc0-1.0",
                "rightsIdentifierScheme": "spdx",
                "rightsUri": "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
            }
        ],
        "descriptions": [
            {
                "description": "Stacked_SP1_1-1066.mat: 1066 Shots Stacked at Shot Point 1\nStacked_SP1_1-40.mat: 40 Shots Stacked at Shot Point 1",
                "descriptionType": "Abstract",
            }
        ],
        "schemaVersion": "http://datacite.org/schema/kernel-4",
    }

@pytest.fixture(scope="function")
def full_rdm_record():
    return {
        "metadata": {
            "resource_type": {"id": "dataset"},
            "creators": [
                {
                    "person_or_org": {
                        "name": "Reid-McLaughlin, Auden",
                        "type": "personal",
                        "given_name": "Auden",
                        "family_name": "Reid-McLaughlin",
                        "identifiers": [
                            {
                                "scheme": "orcid",
                                "identifier": "0009-0004-5513-2817",
                            }
                        ],
                    },
                    "affiliations": [{"id": "05dxps055"}],
                }
            ],
            "title": "South Pole Shot Stacks for Constraining Temperature and Sedimentary Conditions under the South Pole with Distributed Acoustic Sensing (Reid-McLaughlin et al.)",
            "publisher": "CaltechDATA",
            "publication_date": "2025-03-06",
            "identifiers": [
                {"identifier": "10.22002/6x9nn-n3559", "scheme": "doi"},
                {
                    "identifier": "oai:data.caltech.edu:6x9nn-n3559",
                    "scheme": "oai",
                },
            ],
            "rights": [
                {"id": "cc0-1.0"},
            ],
            "description": "Stacked_SP1_1-1066.mat: 1066 Shots Stacked at Shot Point 1\nStacked_SP1_1-40.mat: 40 Shots Stacked at Shot Point 1",
            "parent": {},
        },
    }
