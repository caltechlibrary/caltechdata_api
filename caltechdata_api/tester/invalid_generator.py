import json
import os

# Directory to save invalid metadata JSON files
INVALID_DATACITE43_DIR = "../tests/data/invalid_datacite43/"

# Ensure the directory exists
os.makedirs(INVALID_DATACITE43_DIR, exist_ok=True)

# Helper function to save a dictionary as a JSON file
def save_invalid_json(data, filename):
    with open(os.path.join(INVALID_DATACITE43_DIR, filename), 'w') as f:
        json.dump(data, f, indent=4)

# Generate different invalid JSON examples
invalid_metadata_examples = [
    # Missing 'titles' field
    {
        "creators": [{"name": "John Doe"}],
        "publisher": "Caltech",
        "publicationYear": "2023",
        "types": {"resourceTypeGeneral": "Dataset"}
    },
    
    # Empty 'titles' list
    {
        "titles": [],
        "creators": [{"name": "John Doe"}],
        "publisher": "Caltech",
        "publicationYear": "2023",
        "types": {"resourceTypeGeneral": "Dataset"}
    },
    
    # Missing 'creators' field
    {
        "titles": [{"title": "Sample Title"}],
        "publisher": "Caltech",
        "publicationYear": "2023",
        "types": {"resourceTypeGeneral": "Dataset"}
    },
    
    # 'contributors' missing 'name' and 'contributorType'
    {
        "titles": [{"title": "Sample Title"}],
        "creators": [{"name": "John Doe"}],
        "contributors": [{}],
        "publisher": "Caltech",
        "publicationYear": "2023",
        "types": {"resourceTypeGeneral": "Dataset"}
    },

    # Invalid 'descriptions' structure
    {
        "titles": [{"title": "Sample Title"}],
        "creators": [{"name": "John Doe"}],
        "descriptions": [{"description": "Sample Description"}],  # Missing 'descriptionType'
        "publisher": "Caltech",
        "publicationYear": "2023",
        "types": {"resourceTypeGeneral": "Dataset"}
    },
    
    # 'fundingReferences' missing 'funderName'
    {
        "titles": [{"title": "Sample Title"}],
        "creators": [{"name": "John Doe"}],
        "fundingReferences": [{"funderIdentifier": "1234"}],  # Missing 'funderName'
        "publisher": "Caltech",
        "publicationYear": "2023",
        "types": {"resourceTypeGeneral": "Dataset"}
    },
    
    # 'identifiers' missing 'identifier' and 'identifierType'
    {
        "titles": [{"title": "Sample Title"}],
        "creators": [{"name": "John Doe"}],
        "identifiers": [{}],  # Missing 'identifier' and 'identifierType'
        "publisher": "Caltech",
        "publicationYear": "2023",
        "types": {"resourceTypeGeneral": "Dataset"}
    },
    
    # 'dates' missing 'date' and 'dateType'
    {
        "titles": [{"title": "Sample Title"}],
        "creators": [{"name": "John Doe"}],
        "dates": [{}],  # Missing 'date' and 'dateType'
        "publisher": "Caltech",
        "publicationYear": "2023",
        "types": {"resourceTypeGeneral": "Dataset"}
    },
    
    # Missing 'publisher'
    {
        "titles": [{"title": "Sample Title"}],
        "creators": [{"name": "John Doe"}],
        "publicationYear": "2023",
        "types": {"resourceTypeGeneral": "Dataset"}
    },

    # Invalid 'version' type (should be a string)
    {
        "titles": [{"title": "Sample Title"}],
        "creators": [{"name": "John Doe"}],
        "version": 1,  # Incorrect type, should be a string
        "publisher": "Caltech",
        "publicationYear": "2023",
        "types": {"resourceTypeGeneral": "Dataset"}
    }
]

# Save each invalid example as a JSON file
for i, invalid_json in enumerate(invalid_metadata_examples, start=1):
    filename = f"invalid_metadata_{i}.json"
    save_invalid_json(invalid_json, filename)

print(f"Generated {len(invalid_metadata_examples)} invalid metadata files in {INVALID_DATACITE43_DIR}")
