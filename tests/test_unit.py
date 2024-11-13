import os
import pytest
from customize_schema import validate_metadata as validator43
from helpers import load_json_path
import logging
from tqdm import tqdm

# Directories for valid and invalid JSON files
VALID_DATACITE43_DIR = "../tests/data/datacite43/"
INVALID_DATACITE43_DIR = "../tests/data/invalid_datacite43/"


# Function to get all JSON files in the directory
def get_all_json_files(directory):
    return [
        os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")
    ]


# Get list of all valid JSON files in the directory
VALID_DATACITE43_FILES = get_all_json_files(VALID_DATACITE43_DIR)
INVALID_DATACITE43_FILES = get_all_json_files(INVALID_DATACITE43_DIR)


@pytest.mark.parametrize("valid_file", VALID_DATACITE43_FILES)
def test_valid_json(valid_file):
    """Test that valid example files validate successfully."""
    print(f"\nValidating file: {valid_file}")  # Log for file being tested
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
    print(f"\nValidating file: {invalid_file}")  # Log for file being tested
    json_data = load_json_path(invalid_file)
    validation_errors = None
    try:
        validation_errors = validator43(json_data)
    except ValueError:
        print(f"Validation failed as expected for: {invalid_file}")
        return  # Test passes if validation raises a ValueError

    if validation_errors:
        print(f"Validation failed as expected for: {invalid_file}")
    else:
        pytest.fail(f"Validation passed unexpectedly for: {invalid_file}")


@pytest.mark.parametrize(
    "missing_field_file",
    [
        {"file": "../tests/data/missing_creators.json", "missing_field": "creators"},
        {"file": "../tests/data/missing_titles.json", "missing_field": "titles"},
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
        {"file": "../tests/data/type_error_creators.json", "field": "creators"},
        {"file": "../tests/data/type_error_dates.json", "field": "dates"},
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
    json_data = load_json_path("../tests/data/multiple_errors.json")
    with pytest.raises(ValueError, match="Multiple validation errors"):
        validator43(json_data)


def test_error_logging(caplog):
    """Test that errors are logged correctly during validation."""
    json_data = load_json_path(
        "../tests/data/invalid_datacite43/some_invalid_file.json"
    )
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            validator43(json_data)
    assert "Validation failed" in caplog.text


if __name__ == "__main__":
    # Manual test runner for valid files
    failed_valid_files = []
    print("\nRunning validation for valid files...")
    for file in tqdm(VALID_DATACITE43_FILES, desc="Valid files"):
        try:
            test_valid_json(file)
        except AssertionError as e:
            failed_valid_files.append(file)
            print(f"Error occurred in valid file: {file}\nError details: {e}")

    if not failed_valid_files:
        print("\n✅ All valid files passed validation. Test complete.")
    else:
        print("\n❌ The following valid files failed validation:")
        for failed_file in failed_valid_files:
            print(f"- {failed_file}")

    # Manual test runner for invalid files
    passed_invalid_files = []
    print("\nRunning validation for invalid files...")
    for file in tqdm(INVALID_DATACITE43_FILES, desc="Invalid files"):
        try:
            test_invalid_json(file)
        except AssertionError as e:
            passed_invalid_files.append(file)
            print(f"Error occurred in invalid file: {file}\nError details: {e}")

    if not passed_invalid_files:
        print(
            "\n✅ All invalid files failed validation as expected. Test is a success."
        )
    else:
        print("\n❌ The following invalid files unexpectedly passed validation:")
        for passed_file in passed_invalid_files:
            print(f"- {passed_file}")
