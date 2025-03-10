import pytest

@pytest.fixture(scope="function")
def full_rdm_record():
    """Full record data from DataCite as dict coming from the external world."""
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
            "additional_titles": [
                {
                    "title": "a research data management platform",
                    "type": {"id": "subtitle"},
                    "lang": {"id": "eng"},
                }
            ],
            "publisher": "CaltechDATA",
            "publication_date": "2025-03-06",
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
                            {
                                "scheme": "orcid",
                                "identifier": "0000-0001-8135-3489",
                            }
                        ],
                    },
                    "role": {"id": "other"},
                    "affiliations": [{"id": "01ggx4157"}],
                }
            ],
            "dates": [
                {
                    "date": "2025-03-06",
                    "type": {"id": "issued"},
                }
            ],
            "languages": [{"id": "dan"}],
            "identifiers": [
                {
                    "identifier": "10.22002/6x9nn-n3559",
                    "scheme": "doi"
                },
                {
                    "identifier": "oai:data.caltech.edu:6x9nn-n3559",
                    "scheme": "oai"
                }
            ],
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
                    "title": {"en": "Creative Commons Zero v1.0 Universal"},
                    "id": "cc0-1.0",
                    "link": "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
                },
                {
                    "title": {"en": "No rightsUri license"},
                },
                {"id": "cc-by-4.0"},
            ],
            "description": "Stacked_SP1_1-1066.mat: 1066 Shots Stacked at Shot Point 1\nStacked_SP1_1-40.mat: 40 Shots Stacked at Shot Point 1",
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
                        "identifier": "1234",
                        "scheme": "ror",
                    },
                    "award": {
                        "title": "OpenAIRE",
                        "number": "246686",
                        "identifier": ".../246686",
                    },
                }
            ],
        },
    }
