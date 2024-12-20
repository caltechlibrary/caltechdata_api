import os
import pytest
import logging
from caltechdata_api import validate_metadata as validator43
from helpers import load_json_path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Dynamically determine the base path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVALID_DATACITE43_DIR = os.path.join(BASE_DIR, "data", "invalid_datacite43")
DATACITE43_DIR = os.path.join(BASE_DIR, "data")


# Function to get all JSON files in the directory
def get_all_json_files(directory):
    return [
        os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")
    ]


# Get list of all valid and invalid JSON files
VALID_DATACITE43_FILES = get_all_json_files(
    os.path.join(BASE_DIR, "data", "datacite43")
)
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

    assert (
        not validation_errors
    ), f"Validation failed for: {valid_file}\nErrors: {validation_errors}"
    print(f"Validation passed for: {valid_file}")


@pytest.mark.parametrize("invalid_file", INVALID_DATACITE43_FILES)
def test_invalid_json(invalid_file):
    """Test that invalid example files do not validate successfully."""
    logger.debug(f"Attempting to validate invalid file: {invalid_file}")

    json_data = load_json_path(invalid_file)

    def validate_wrapper():
        try:
            validation_errors = validator43(json_data)

            logger.debug(f"Validation result for {invalid_file}: {validation_errors}")

            if validation_errors:
                logger.debug(f"Found validation errors in {invalid_file}")
                return

            logger.error(
                f"No validation errors found for supposedly invalid file: {invalid_file}"
            )
            raise ValueError(
                f"Validation did not fail for invalid file: {invalid_file}"
            )

        except Exception as e:
            logger.error(f"Validation exception for {invalid_file}: {str(e)}")
            raise

    with pytest.raises((ValueError, KeyError, AssertionError, TypeError)):
        validate_wrapper()


@pytest.mark.parametrize(
    "missing_field_file",
    [
        {
            "file": os.path.join(DATACITE43_DIR, "missing_creators.json"),
            "missing_field": "creators",
        },
        {
            "file": os.path.join(DATACITE43_DIR, "missing_titles.json"),
            "missing_field": "titles",
        },
    ],
)
def test_missing_required_fields(missing_field_file):
    """Test that JSON files missing required fields fail validation."""
    print(
        f"\nTesting missing field: {missing_field_file['missing_field']} in file: {missing_field_file['file']}"
    )

    # Skip the test if the file doesn't exist
    if not os.path.exists(missing_field_file["file"]):
        pytest.skip(f"Test file not found: {missing_field_file['file']}")

    json_data = load_json_path(missing_field_file["file"])
    with pytest.raises(
        ValueError,
        match=f"Missing required metadata field: {missing_field_file['missing_field']}",
    ):
        validator43(json_data)


@pytest.mark.parametrize(
    "type_error_file",
    [
        {
            "file": os.path.join(DATACITE43_DIR, "type_error_creators.json"),
            "field": "creators",
        },
        {
            "file": os.path.join(DATACITE43_DIR, "type_error_dates.json"),
            "field": "dates",
        },
    ],
)
def test_incorrect_field_types(type_error_file):
    """Test that JSON files with incorrect field types fail validation."""
    print(
        f"\nTesting incorrect type in field: {type_error_file['field']} for file: {type_error_file['file']}"
    )

    # Skip the test if the file doesn't exist
    if not os.path.exists(type_error_file["file"]):
        pytest.skip(f"Test file not found: {type_error_file['file']}")

    json_data = load_json_path(type_error_file["file"])
    with pytest.raises(
        ValueError, match=f"Incorrect type for field: {type_error_file['field']}"
    ):
        validator43(json_data)


def test_multiple_errors():
    """Test JSON file with multiple issues to check all errors are raised."""
    multiple_errors_file = os.path.join(DATACITE43_DIR, "multiple_errors.json")

    # Skip the test if the file doesn't exist
    if not os.path.exists(multiple_errors_file):
        pytest.skip(f"Test file not found: {multiple_errors_file}")

    json_data = load_json_path(multiple_errors_file)
    with pytest.raises(ValueError, match="Multiple validation errors"):
        validator43(json_data)


def test_error_logging(caplog):
    """Test that errors are logged correctly during validation."""
    some_invalid_file = os.path.join(INVALID_DATACITE43_DIR, "some_invalid_file.json")

    # Skip the test if the file doesn't exist
    if not os.path.exists(some_invalid_file):
        pytest.skip(f"Test file not found: {some_invalid_file}")

    json_data = load_json_path(some_invalid_file)
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            validator43(json_data)
    assert "Validation failed" in caplog.text
