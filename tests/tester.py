import os
import pytest
from customize_schema import validate_metadata as validator43
from helpers import load_json_path

# Define the directory containing the test JSON files
VALID_DATACITE43_DIR = "../tests/data/datacite43/"  # Directory for valid JSON files


# Function to get all JSON files in the directory
def get_all_json_files(directory):
    return [
        os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")
    ]


# Get list of all valid JSON files in the directory
VALID_DATACITE43_FILES = get_all_json_files(VALID_DATACITE43_DIR)


@pytest.mark.parametrize("valid_file", VALID_DATACITE43_FILES)
def test_valid_json(valid_file):
    """Test that valid example files validate successfully."""
    print(f"Validating file: {valid_file}")  # Added log for file being tested
    json_data = load_json_path(valid_file)
    validation_errors = None
    try:
        validation_errors = validator43(json_data)
    except ValueError as e:
        pytest.fail(f"Validation failed for: {valid_file}\nErrors: {str(e)}")

    if validation_errors:
        pytest.fail(f"Validation failed for: {valid_file}\nErrors: {validation_errors}")
    else:
        print(f"Validation passed for: {valid_file}")


if __name__ == "__main__":
    # Track failures for manual testing
    failed_files = []

    # Run the tests and print results for each file
    for file in VALID_DATACITE43_FILES:
        try:
            test_valid_json(file)
        except AssertionError as e:
            failed_files.append(file)
            print(f"Error occurred in file: {file}\nError details: {e}")

    # Print a summary of all failed files
    if failed_files:
        print("\nThe following files failed validation:")
        for failed_file in failed_files:
            print(f"- {failed_file}")
    else:
        print("\nAll files passed validation.")
