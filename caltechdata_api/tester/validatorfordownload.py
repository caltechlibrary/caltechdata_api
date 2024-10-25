import subprocess
import requests
import pytest
import json
from customize_schema import validate_metadata as validator43
from helpers import load_json_path

def run_caltechdata_write(metadata_path):
    """Run the caltechdata_write.py script with the given metadata file."""
    try:
        result = subprocess.run(
            ["python", "caltechdata_write.py", "--metadata", metadata_path],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
        record_url = output.split("Record created with URL: ")[1].strip()
        return record_url
    except subprocess.CalledProcessError as e:
        print("Error running caltechdata_write:", e.stderr)
        return None

def fetch_datacite_json(record_url):
    """Fetch the JSON metadata from the export endpoint."""
    try:
        export_url = f"{record_url}/export/datacite-json"
        response = requests.get(export_url)
        response.raise_for_status() 
        return response.json()
    except requests.RequestException as e:
        print("Error fetching JSON data:", e)
        return None

def test_validator(metadata_path):
    """Test the validator by uploading metadata and validating the returned JSON."""
    record_url = run_caltechdata_write(metadata_path)
    if not record_url:
        pytest.fail("Failed to upload metadata and get record URL")

    json_data = fetch_datacite_json(record_url)
    if not json_data:
        pytest.fail("Failed to retrieve JSON data from export endpoint")

    validation_errors = validator43(json_data)
    if validation_errors:
        pytest.fail(f"Validation failed for {record_url}:\n{validation_errors}")
    else:
        print("Validation passed")
        return True

if __name__ == "__main__":
    metadata_file = "1171.json"  
    test_validator(metadata_file)
