import json
import os
import copy

# Directory to store invalid test files
INVALID_DATA_DIR = "../tests/data/invalid_datacite43"
os.makedirs(INVALID_DATA_DIR, exist_ok=True)

# Load the valid metadata as a base
valid_metadata = {
    "contributors": [
        {
            "nameIdentifiers": [
                {
                    "nameIdentifier": "grid.20861.3d",
                    "nameIdentifierScheme": "GRID"
                }
            ],
            "name": "California Institute of Techonolgy, Pasadena, CA (US)",
            "contributorType": "HostingInstitution"
        },
        {
            "affiliation": [
                {
                    "name": "California Institute of Technology, Pasadena, CA (US)"
                }
            ],
            "nameIdentifiers": [
                {
                    "nameIdentifier": "0000-0001-5383-8462",
                    "nameIdentifierScheme": "ORCID"
                }
            ],
            "name": "Roehl, C. M.",
            "contributorType": "DataCurator"
        },
        {
            "affiliation": [
                {
                    "name": "Department of Physics, University of Toronto, Toronto, ON (CA)"
                }
            ],
            "nameIdentifiers": [
                {
                    "nameIdentifier": "0000-0001-9947-1053",
                    "nameIdentifierScheme": "ORCID"
                },
                {
                    "nameIdentifier": "D-2563-2012",
                    "nameIdentifierScheme": "ResearcherID"
                }
            ],
            "name": "Kimberly Strong",
            "contributorType": "ContactPerson"
        },
        {
            "name": "TCCON",
            "contributorType": "ResearchGroup"
        }
    ],
    "descriptions": [
        {
            "descriptionType": "Abstract",
            "description": "<br> The Total Carbon Column Observing Network (TCCON) is a network of ground-based Fourier Transform Spectrometers that record direct solar absorption spectra of the atmosphere in the near-infrared. From these spectra, accurate and precise column-averaged abundances of atmospheric constituents including CO2, CH4, N2O, HF, CO, H2O, and HDO, are retrieved. This data set contains observations from the TCCON station at Eureka, Canada."
        },
        {
            "descriptionType": "Other",
            "description": "<br>Cite this record as:<br>Strong, K., Roche, S., Franklin, J. E., Mendonca, J., Lutsch, E., Weaver, D., \u2026 Lindenmaier, R. (2019). <i>TCCON data from Eureka (CA), Release GGG2014.R3</i> [Data set]. CaltechDATA. <a href=\"https://doi.org/10.14291/tccon.ggg2014.eureka01.r3\">https://doi.org/10.14291/tccon.ggg2014.eureka01.r3</a><br> or choose a <a href=\"https://crosscite.org/?doi=10.14291/tccon.ggg2014.eureka01.R3\"> different citation style.</a><br><a href=\"https://data.datacite.org/application/x-bibtex/10.14291/tccon.ggg2014.eureka01.R3\">Download Citation</a><br>"
        },
        {
            "descriptionType": "Other",
            "description": "<br>Unique Views: 161<br>Unique Downloads: 7<br> between January 31, 2019 and July 02, 2020<br><a href=\"https://data.caltech.edu/stats\">More info on how stats are collected</a><br>"
        }
    ],
    "fundingReferences": [
        {
            "funderName": "Atlantic Innovation Fund"
        },
        {
            "funderName": "Canada Foundation for Innovation",
            "funderIdentifierType": "GRID",
            "funderIdentifier": "grid.439998.6"
        },
        {
            "funderName": "Canadian Foundation for Climate and Atmospheric Sciences"
        },
        {
            "funderName": "Canadian Space Agency",
            "funderIdentifierType": "GRID",
            "funderIdentifier": "grid.236846.d"
        },
        {
            "funderName": "Environment and Climate Change Canada",
            "funderIdentifierType": "GRID",
            "funderIdentifier": "grid.410334.1"
        },
        {
            "funderName": "Government of Canada (International Polar Year funding)",
            "funderIdentifierType": "GRID",
            "funderIdentifier": "grid.451254.3"
        },
        {
            "funderName": "Natural Sciences and Engineering Research Council of Canada",
            "funderIdentifierType": "GRID",
            "funderIdentifier": "grid.452912.9"
        },
        {
            "funderName": "Polar Commission (Northern Scientific Training Program)",
            "funderIdentifierType": "GRID",
            "funderIdentifier": "grid.465477.3"
        },
        {
            "funderName": "Nova Scotia Research Innovation Trust"
        },
        {
            "funderName": "Ministry of Research and Innovation (Ontario Innovation Trust and Ontario Research Fund)",
            "funderIdentifierType": "GRID",
            "funderIdentifier": "grid.451078.f"
        },
        {
            "funderName": "Natural Resources Canada (Polar Continental Shelf Program)",
            "funderIdentifierType": "GRID",
            "funderIdentifier": "grid.202033.0"
        }
    ],
    "language": "eng",
    "relatedIdentifiers": [
        {
            "relatedIdentifier": "10.14291/tccon.ggg2014.documentation.R0/1221662",
            "relationType": "IsDocumentedBy",
            "relatedIdentifierType": "DOI"
        },
        {
            "relatedIdentifier": "10.14291/tccon.ggg2014.eureka01.R0/1149271",
            "relationType": "IsNewVersionOf",
            "relatedIdentifierType": "DOI"
        },
        {
            "relatedIdentifier": "https://tccon-wiki.caltech.edu/Network_Policy/Data_Use_Policy/Data_Description",
            "relationType": "IsDocumentedBy",
            "relatedIdentifierType": "URL"
        },
        {
            "relatedIdentifier": "https://tccon-wiki.caltech.edu/Sites",
            "relationType": "IsDocumentedBy",
            "relatedIdentifierType": "URL"
        },
        {
            "relatedIdentifier": "10.14291/TCCON.GGG2014",
            "relationType": "IsPartOf",
            "relatedIdentifierType": "DOI"
        },
        {
            "relatedIdentifier": "10.14291/tccon.ggg2014.eureka01.R1/1325515",
            "relationType": "IsNewVersionOf",
            "relatedIdentifierType": "DOI"
        },
        {
            "relatedIdentifier": "10.14291/tccon.ggg2014.eureka01.R2",
            "relationType": "IsNewVersionOf",
            "relatedIdentifierType": "DOI"
        }
    ],
    "rightsList": [
        {
            "rights": "TCCON Data License",
            "rightsURI": "https://data.caltech.edu/tindfiles/serve/8298981c-6613-4ed9-9c54-5ef8fb5180f4/"
        }
    ],
    "subjects": [
        {
            "subject": "atmospheric trace gases"
        },
        {
            "subject": "CO2"
        },
        {
            "subject": "CH4"
        },
        {
            "subject": "CO"
        },
        {
            "subject": "N2O"
        },
        {
            "subject": "column-averaged dry-air mole fractions"
        },
        {
            "subject": "remote sensing"
        },
        {
            "subject": "FTIR spectroscopy"
        },
        {
            "subject": "TCCON"
        }
    ],
    "version": "R3",
    "titles": [
        {
            "title": "TCCON data from Eureka (CA), Release GGG2014.R3"
        }
    ],
    "formats": [
        "application/x-netcdf"
    ],
    "dates": [
        {
            "date": "2019-01-31",
            "dateType": "Created"
        },
        {
            "date": "2020-07-01",
            "dateType": "Updated"
        },
        {
            "date": "2010-07-24/2019-08-15",
            "dateType": "Collected"
        },
        {
            "date": "2019-01-31",
            "dateType": "Submitted"
        },
        {
            "date": "2019-01-31",
            "dateType": "Issued"
        }
    ],
    "publicationYear": "2019",
    "publisher": "CaltechDATA",
    "types": {
        "resourceTypeGeneral": "Dataset",
        "resourceType": "Dataset"
    },
    "identifiers": [
        {
            "identifier": "10.14291/tccon.ggg2014.eureka01.R3",
            "identifierType": "DOI"
        },
        {
            "identifier": "1171",
            "identifierType": "CaltechDATA_Identifier"
        },
        {
            "identifier": "GGG2014",
            "identifierType": "Software_Version"
        },
        {
            "identifier": "eu",
            "identifierType": "id"
        },
        {
            "identifier": "eureka01",
            "identifierType": "longName"
        },
        {
            "identifier": "R1",
            "identifierType": "Data_Revision"
        }
    ],
    "creators": [
        {
            "affiliation": [
                {
                    "name": "Department of Physics, University of Toronto, Toronto, ON (CA)"
                }
            ],
            "name": "Strong, K."
        },
        {
            "affiliation": [
                {
                    "name": "Department of Physics, University of Toronto, Toronto, ON (CA)"
                }
            ],
            "name": "Roche, S."
        },
        {
            "affiliation": [
                {
                    "name": "School of Engineering and Applied Sciences, Harvard University, Cambridge, MA (USA)"
                }
            ],
            "name": "Franklin, J. E."
        },
        {
            "affiliation": [
                {
                    "name": "Environment and Climate Change Canada, Downsview, ON (CA)"
                }
            ],
            "name": "Mendonca, J."
        },
        {
            "affiliation": [
                {
                    "name": "Department of Physics, University of Toronto, Toronto, ON (CA)"
                }
            ],
            "name": "Lutsch, E."
        },
        {
            "affiliation": [
                {
                    "name": "Department of Physics, University of Toronto, Toronto, ON (CA)"
                }
            ],
            "name": "Weaver, D."
        },
        {
            "affiliation": [
                {
                    "name": "Department of Physics, University of Toronto, Toronto, ON (CA)"
                }
            ],
            "name": "Fogal, P. F."
        },
        {
            "affiliation": [
                {
                    "name": "Department of Physics & Atmospheric Science, Dalhousie University, Halifax, NS, CA"
                }
            ],
            "name": "Drummond, J. R."
        },
        {
            "affiliation": [
                {
                    "name": "Department of Physics, University of Toronto, Toronto, ON (CA)"
                },
                {
                    "name": "UCAR Center for Science Education, Boulder, CO (US)"
                }
            ],
            "name": "Batchelor, R."
        },
        {
            "affiliation": [
                {
                    "name": "Department of Physics, University of Toronto, Toronto, ON (CA)"
                },
                {
                    "name": "Pacific Northwest National Laboratory, Richland, WA (US)"
                }
            ],
            "name": "Lindenmaier, R."
        }
    ],
    "geoLocations": [
        {
            "geoLocationPlace": "Eureka, NU (CA)",
            "geoLocationPoint": {
                "pointLatitude": "80.05",
                "pointLongitude": "-86.42"
            }
        }
    ],
    "schemaVersion": "http://datacite.org/schema/kernel-4"
}

# Function to save invalid files
def save_invalid_file(metadata, filename):
    filepath = os.path.join(INVALID_DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Created: {filepath}")

# Create invalid files

missing_creators = copy.deepcopy(valid_metadata)
missing_creators.pop("creators", None)
save_invalid_file(missing_creators, "missing_creators.json")

type_error_creators = copy.deepcopy(valid_metadata)
type_error_creators["creators"] = "Incorrect type"
save_invalid_file(type_error_creators, "type_error_creators.json")

unmapped_vocab_contributor = copy.deepcopy(valid_metadata)
unmapped_vocab_contributor["contributors"][0]["contributorType"] = "UnknownType"
save_invalid_file(unmapped_vocab_contributor, "unmapped_vocab_contributor.json")

invalid_date_format = copy.deepcopy(valid_metadata)
invalid_date_format["dates"][0]["date"] = "31-01-2019"  # Incorrect format
save_invalid_file(invalid_date_format, "invalid_date_format.json")

missing_publisher = copy.deepcopy(valid_metadata)
missing_publisher.pop("publisher", None)
save_invalid_file(missing_publisher, "missing_publisher.json")

type_error_publication_year = copy.deepcopy(valid_metadata)
type_error_publication_year["publicationYear"] = "Two Thousand Nineteen"
save_invalid_file(type_error_publication_year, "type_error_publication_year.json")

unmapped_vocab_related_identifier = copy.deepcopy(valid_metadata)
unmapped_vocab_related_identifier["relatedIdentifiers"][0]["relatedIdentifierType"] = "UNKNOWN_TYPE"
save_invalid_file(unmapped_vocab_related_identifier, "unmapped_vocab_related_identifier.json")

multiple_errors = copy.deepcopy(valid_metadata)
multiple_errors.pop("creators", None)
multiple_errors["dates"][0]["date"] = "31-01-2019"  # Incorrect format
multiple_errors["titles"][0]["title"] = "A" * 300
save_invalid_file(multiple_errors, "multiple_errors.json")
