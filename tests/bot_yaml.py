import subprocess
import time
from unittest.mock import patch
import sys
import os
import json
import requests
from datetime import datetime
import pytest
import importlib.util
import traceback


class CaltechDataTester:
    def __init__(self):
        # Use GitHub Actions environment or create a local test directory
        self.test_dir = os.environ.get(
            "GITHUB_WORKSPACE", os.path.join(os.getcwd(), "caltech_test_data")
        )
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Ensure test directory exists
        os.makedirs(self.test_dir, exist_ok=True)

        # Create test run directory
        self.test_run_dir = os.path.join(self.test_dir, f"test_run_{self.timestamp}")
        os.makedirs(self.test_run_dir, exist_ok=True)

        # Initialize logging
        self.log_file = os.path.join(self.test_run_dir, "test_log.txt")

    def log(self, message):
        """Log message to both console and file"""
        print(message)
        with open(self.log_file, "a") as f:
            f.write(f"{datetime.now()}: {message}\n")

    def create_test_files(self):
        """Create necessary test files"""
        csv_path = os.path.join(self.test_run_dir, "test_data.csv")
        with open(csv_path, "w") as f:
            f.write("date,temperature,humidity\n")
            f.write("2023-01-01,25.5,60\n")
            f.write("2023-01-02,26.0,62\n")
            f.write("2023-01-03,24.8,65\n")

        self.log(f"Created test CSV file: {csv_path}")
        return csv_path

    def import_cli_module(self):
        """Dynamically import cli module from the correct path"""
        cli_path = os.path.join(
            os.environ.get("GITHUB_WORKSPACE", os.getcwd()), "caltechdata_api", "cli.py"
        )
        spec = importlib.util.spec_from_file_location("cli", cli_path)
        cli_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli_module)
        return cli_module
        
    def generate_test_responses(self):
            """Generate test responses for CLI prompts"""
            return {
                "What would you like to do? (create/edit/profile/exit): ": "create",
                "Do you want to use metadata from an existing file or create new metadata? (existing/create): ": "create",
                "Enter the title of the dataset: ": f"Test Dataset {self.timestamp}",
                "Enter the abstract or description of the dataset: ": "This is an automated test dataset containing sample climate data for validation purposes.",
                "Enter the number corresponding to the desired license: ": "1",
                "Use saved profile? (y/n): ": "n",
                "Enter your ORCID identifier: ": os.environ.get(
                    "TEST_ORCID", "0000-0002-1825-0097"
                ),
                "How many funding entries do you want to provide? ": "1",
                "Enter the award number for funding: ": "NSF-1234567",
                "Enter the award title for funding: ": "Automated Testing Grant",
                "Enter the funder ROR (https://ror.org): ": "021nxhr62",
                "Do you want to upload or link data files? (upload/link/n): ": "upload",
                "Enter the filename to upload as a supporting file (or 'n' to finish): ": "test_data.csv",
                "Do you want to add more files? (y/n): ": "n",
                "Do you want to send this record to CaltechDATA? (y/n): ": "y",
            }
    
    def run_test_submission(self):
        """Run the complete test submission process"""
        try:
            self.log("Starting test submission process...")

            # Create test files
            test_csv = self.create_test_files()

            # Dynamically import cli module
            cli_module = self.import_cli_module()

            # Generate responses
            responses = self.generate_test_responses()

            # Setup output capture
            class OutputCapture:
                def __init__(self):
                    self.output = []

                def write(self, text):
                    self.output.append(text)
                    sys.__stdout__.write(text)

                def flush(self):
                    pass

                def get_output(self):
                    return "".join(self.output)

            output_capture = OutputCapture()
            sys.stdout = output_capture

            # Mock input and run CLI
            def mock_input(prompt):
                self.log(f"Prompt: {prompt}")
                if prompt in responses:
                    response = responses[prompt]
                    self.log(f"Response: {response}")
                    return response
                return ""

            with patch("builtins.input", side_effect=mock_input):
                # Use -test flag to use test mode
                sys.argv = [sys.argv[0], "-test"]
                cli_module.main()

            # Restore stdout
            sys.stdout = sys.__stdout__

            return True

        except Exception as e:
            self.log(f"Error in test submission: {e}")
            traceback.print_exc()
            return False
        finally:
            # Cleanup
            if "test_csv" in locals() and os.path.exists(test_csv):
                os.remove(test_csv)
            self.log("Test files cleaned up")


def main():
    tester = CaltechDataTester()

    success = tester.run_test_submission()

    if success:
        tester.log("\n🎉 Test submission completed successfully!")
        sys.exit(0)
    else:
        tester.log("\n❌ Test submission failed - check logs for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
