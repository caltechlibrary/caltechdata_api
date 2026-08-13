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
