import os
import pytest
from customize_schema import validate_metadata as validator43
from helpers import load_json_path

# Directories for valid and invalid JSON files
VALID_DATACITE43_DIR = "../tests/data/datacite43/"  # Directory for valid JSON files
INVALID_DATACITE43_DIR = "../tests/data/invalid_datacite43/"  # Directory for invalid JSON files

# Function to get all JSON files in the directory
def get_all_json_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]

# Get list of all valid JSON files in the directory
VALID_DATACITE43_FILES = get_all_json_files(VALID_DATACITE43_DIR)
INVALID_DATACITE43_FILES = get_all_json_files(INVALID_DATACITE43_DIR)

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

@pytest.mark.parametrize("invalid_file", INVALID_DATACITE43_FILES)
def test_invalid_json(invalid_file):
    """Test that invalid example files do not validate successfully."""
    print(f"Validating file: {invalid_file}")  # Added log for file being tested
    json_data = load_json_path(invalid_file)
    validation_errors = None
    try:
        validation_errors = validator43(json_data)
    except ValueError:
        print(f"Validation failed as expected for: {invalid_file}")
        return  # Test passes if validation raises a ValueError
    
    # If no errors, the test fails because the file is expected to be invalid
    if validation_errors:
        print(f"Validation failed as expected for: {invalid_file}")
    else:
        pytest.fail(f"Validation passed unexpectedly for: {invalid_file}")

if __name__ == "__main__":
    # Manual test runner for valid files
    failed_valid_files = []
    for file in VALID_DATACITE43_FILES:
        try:
            test_valid_json(file)
        except AssertionError as e:
            failed_valid_files.append(file)
            print(f"Error occurred in valid file: {file}\nError details: {e}")
    
    if not failed_valid_files:
        print("\nAll valid files passed validation. Test complete.")
    else:
        print("\nThe following valid files failed validation:")
        for failed_file in failed_valid_files:
            print(f"- {failed_file}")
    
    # Manual test runner for invalid files
    passed_invalid_files = []
    for file in INVALID_DATACITE43_FILES:
        try:
            test_invalid_json(file)
        except AssertionError as e:
            passed_invalid_files.append(file)
            print(f"Error occurred in invalid file: {file}\nError details: {e}")
    
    if not passed_invalid_files:
        print("\nAll invalid files failed validation as expected. Test is a success.")
    else:
        print("\nThe following invalid files unexpectedly passed validation:")
        for passed_file in passed_invalid_files:
            print(f"- {passed_file}")
