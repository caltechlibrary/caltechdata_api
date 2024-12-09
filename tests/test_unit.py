import os
import pytest
from customize_schema import validate_metadata as validator43
from helpers import load_json_path
import logging
from tqdm import tqdm
import sys

# Adjust paths to be more robust across different execution environments
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VALID_DATACITE43_DIR = os.path.join(BASE_DIR, "data", "datacite43")
INVALID_DATACITE43_DIR = os.path.join(BASE_DIR, "data", "invalid_datacite43")

# Function to get all JSON files in the directory
def get_all_json_files(directory):
    return [
        os.path.join(directory, f) 
        for f in os.listdir(directory) 
        if f.endswith(".json")
    ]

# Get list of all valid and invalid JSON files
VALID_DATACITE43_FILES = get_all_json_files(VALID_DATACITE43_DIR)
INVALID_DATACITE43_FILES = get_all_json_files(INVALID_DATACITE43_DIR)

@pytest.mark.parametrize("valid_file", VALID_DATACITE43_FILES)
def test_valid_json(valid_file):
    """Test that valid example files validate successfully."""
    print(f"\nValidating file: {valid_file}")
    json_data = load_json_path(valid_file)
    validation_errors = None
    try:
        validation_errors = validator43(json_data)
    except ValueError as e:
        pytest.fail(f"Validation failed for: {valid_file}\nErrors: {str(e)}")

    assert not validation_errors, f"Validation failed for: {valid_file}\nErrors: {validation_errors}"
    print(f"Validation passed for: {valid_file}")

@pytest.mark.parametrize("invalid_file", INVALID_DATACITE43_FILES)
def test_invalid_json(invalid_file):
    """Test that invalid example files do not validate successfully."""
    print(f"\nValidating file: {invalid_file}")
    json_data = load_json_path(invalid_file)
    
    with pytest.raises((ValueError, AssertionError), 
                       reason=f"Expected validation to fail for: {invalid_file}"):
        validator43(json_data)

@pytest.mark.parametrize(
    "missing_field_file",
    [
        {"file": os.path.join(BASE_DIR, "data", "missing_creators.json"), "missing_field": "creators"},
        {"file": os.path.join(BASE_DIR, "data", "missing_titles.json"), "missing_field": "titles"},
    ],
)
def test_missing_required_fields(missing_field_file):
    """Test that JSON files missing required fields fail validation."""
    print(
        f"\nTesting missing field: {missing_field_file['missing_field']} in file: {missing_field_file['file']}"
    )
    json_data = load_json_path(missing_field_file["file"])
    with pytest.raises(
        ValueError,
        match=f"Missing required metadata field: {missing_field_file['missing_field']}",
    ):
        validator43(json_data)

@pytest.mark.parametrize(
    "type_error_file",
    [
        {"file": os.path.join(BASE_DIR, "data", "type_error_creators.json"), "field": "creators"},
        {"file": os.path.join(BASE_DIR, "data", "type_error_dates.json"), "field": "dates"},
    ],
)
def test_incorrect_field_types(type_error_file):
    """Test that JSON files with incorrect field types fail validation."""
    print(
        f"\nTesting incorrect type in field: {type_error_file['field']} for file: {type_error_file['file']}"
    )
    json_data = load_json_path(type_error_file["file"])
    with pytest.raises(
        ValueError, match=f"Incorrect type for field: {type_error_file['field']}"
    ):
        validator43(json_data)

def test_multiple_errors():
    """Test JSON file with multiple issues to check all errors are raised."""
    json_data = load_json_path(os.path.join(BASE_DIR, "data", "multiple_errors.json"))
    with pytest.raises(ValueError, match="Multiple validation errors"):
        validator43(json_data)

def test_error_logging(caplog):
    """Test that errors are logged correctly during validation."""
    json_data = load_json_path(
        os.path.join(INVALID_DATACITE43_DIR, "some_invalid_file.json")
    )
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            validator43(json_data)
    assert "Validation failed" in caplog.text

# Detailed manual test runner for comprehensive logging
def run_comprehensive_tests():
    """Run comprehensive tests with detailed logging."""
    print("\n🔍 Running Comprehensive Metadata Validation Tests 🔍")
    
    # Validate valid files
    print("\n📝 Validating Valid Metadata Files:")
    failed_valid_files = []
    for file in tqdm(VALID_DATACITE43_FILES, desc="Valid files"):
        try:
            test_valid_json(file)
        except AssertionError as e:
            failed_valid_files.append((file, str(e)))
            print(f"❌ Validation failed for valid file: {file}\nError: {e}")

    # Validate invalid files
    print("\n❌ Validating Invalid Metadata Files:")
    unexpected_valid_files = []
    for file in tqdm(INVALID_DATACITE43_FILES, desc="Invalid files"):
        try:
            test_invalid_json(file)
        except AssertionError:
            unexpected_valid_files.append(file)
            print(f"❌ Invalid file unexpectedly passed validation: {file}")

    # Generate summary
    print("\n📊 Test Summary:")
    if not failed_valid_files:
        print("✅ All valid files passed validation")
    else:
        print("❌ Some valid files failed validation:")
        for file, error in failed_valid_files:
            print(f"  - {file}: {error}")

    if not unexpected_valid_files:
        print("✅ All invalid files correctly rejected")
    else:
        print("❌ Some invalid files unexpectedly passed validation:")
        for file in unexpected_valid_files:
            print(f"  - {file}")

    # Return exit code based on test results
    return 0 if not (failed_valid_files or unexpected_valid_files) else 1

# Allow running as a script or via pytest
if __name__ == "__main__":
    # This allows running the comprehensive tests directly
    sys.exit(run_comprehensive_tests())
