import subprocess
import sys
import os
import json
import time
import requests
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from caltechdata_api import customize_schema

class CaltechDataTester:
    def __init__(self):
        # Use GitHub-specific environment variables
        self.github_workspace = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create temporary test directory
        self.test_dir = os.path.join(self.github_workspace, "caltech_test_data")
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
        # Create a dummy CSV file in the test run directory
        csv_path = os.path.join(self.test_run_dir, "test_data.csv")
        with open(csv_path, "w") as f:
            f.write("date,temperature,humidity\n")
            f.write("2023-01-01,25.5,60\n")
            f.write("2023-01-02,26.0,62\n")
            f.write("2023-01-03,24.8,65\n")

        self.log(f"Created test CSV file: {csv_path}")
        return csv_path

    def generate_test_responses(self):
        """Generate test responses for CLI prompts"""
        # Modify to use environment variables or predefined test data
        return {
            "Do you want to create or edit a CaltechDATA record? (create/edit): ": "create",
            "Do you want to use metadata from an existing file or create new metadata? (existing/create): ": "create",
            "Enter the title of the dataset: ": f"Test Dataset {self.timestamp}",
            "Enter the abstract or description of the dataset: ": "This is an automated test dataset containing sample climate data for validation purposes.",
            "Enter the number corresponding to the desired license: ": "1",
            "Enter your ORCID identifier: ": os.environ.get('TEST_ORCID', '0000-0002-1825-0097'),
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
        self.log("Starting test submission process...")

        # Create test files
        test_csv = self.create_test_files()

        # Modify sys.path to import cli module correctly
        cli_path = os.path.join(self.github_workspace, 'caltechdata_api', 'cli.py')
        sys.path.insert(0, os.path.dirname(cli_path))

        try:
            # Import cli module dynamically
            import cli

            # Capture stdout
            import io
            import contextlib

            # Generate test responses
            responses = self.generate_test_responses()

            # Mock input function
            def mock_input(prompt):
                self.log(f"Prompt: {prompt}")
                if prompt in responses:
                    response = responses[prompt]
                    self.log(f"Response: {response}")
                    return response
                return ""

            # Patch input and run main
            with patch('builtins.input', side_effect=mock_input):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    cli.main()

            # Additional validation using customize_schema
            test_metadata = self._extract_metadata_from_output(output.getvalue())
            
            if test_metadata:
                validation_errors = customize_schema.validate_metadata(test_metadata)
                
                if validation_errors:
                    self.log("❌ Metadata validation failed:")
                    for error in validation_errors:
                        self.log(f"  - {error}")
                    return False
                else:
                    self.log("✅ Metadata validation passed successfully")
                    return True
            else:
                self.log("❌ Could not extract metadata from CLI output")
                return False

        except Exception as e:
            self.log(f"Error during test submission: {e}")
            return False
        finally:
            # Cleanup
            if os.path.exists(test_csv):
                os.remove(test_csv)
            self.log("Test files cleaned up")

    def _extract_metadata_from_output(self, output):
        """Extract metadata from CLI output"""
        try:
            # Look for JSON files created during the test run
            json_files = [f for f in os.listdir(self.test_run_dir) if f.endswith('.json')]
            
            if json_files:
                # Use the first JSON file found
                json_path = os.path.join(self.test_run_dir, json_files[0])
                
                with open(json_path, 'r') as f:
                    return json.load(f)
            
            return None
        except Exception as e:
            self.log(f"Error extracting metadata: {e}")
            return None

def main():
    tester = CaltechDataTester()

    success = tester.run_test_submission()

    if success:
        tester.log("\n🎉 Test submission and validation completed successfully!")
        sys.exit(0)  # Exit with success code
    else:
        tester.log("\n❌ Test submission or validation failed - check logs for details")
        sys.exit(1)  # Exit with failure code

if __name__ == "__main__":
    main()
