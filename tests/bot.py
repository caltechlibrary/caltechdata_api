import subprocess
import time
from unittest.mock import patch
import sys
import os
import json
import requests
from datetime import datetime
import pytest
from customize_schema import validate_metadata as validator43  # Import validator

class CaltechDataTester:
    def __init__(self):
        self.test_dir = "caltech_test_data"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        
        # Create test data directory with timestamp
        self.test_run_dir = os.path.join(self.test_dir, f"test_run_{self.timestamp}")
        os.makedirs(self.test_run_dir)
        
        # Initialize logging
        self.log_file = os.path.join(self.test_run_dir, "test_log.txt")
        
    def log(self, message):
        """Log message to both console and file"""
        print(message)
        with open(self.log_file, "a") as f:
            f.write(f"{datetime.now()}: {message}\n")

    def create_test_files(self):
        """Create necessary test files"""
        # Create a dummy CSV file
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
        return {
            "Do you want to create or edit a CaltechDATA record? (create/edit): ": "create",
            "Do you want to use metadata from an existing file or create new metadata? (existing/create): ": "create",
            "Enter the title of the dataset: ": f"Test Dataset {self.timestamp}",
            "Enter the abstract or description of the dataset: ": "This is an automated test dataset containing sample climate data for validation purposes.",
            "Enter the number corresponding to the desired license: ": "1",
            "Enter your ORCID identifier: ": "0000-0002-1825-0097",
            "How many funding entries do you want to provide? ": "1",
            "Enter the award number for funding: ": "NSF-1234567",
            "Enter the award title for funding: ": "Automated Testing Grant",
            "Enter the funder ROR (https://ror.org): ": "021nxhr62",
            "Do you want to upload or link data files? (upload/link/n): ": "upload",
            "Enter the filename to upload as a supporting file (or 'n' to finish): ": "test_data.csv",
            "Do you want to add more files? (y/n): ": "n",
            "Do you want to send this record to CaltechDATA? (y/n): ": "y",
        }

    def extract_record_id(self, output_text):
        """Extract record ID from CLI output"""
        try:
            for line in output_text.split('\n'):
                if 'uploads/' in line:
                    return line.strip().split('/')[-1]
        except Exception as e:
            self.log(f"Error extracting record ID: {e}")
        return None

    def download_and_validate_record(self, record_id):
        """Download and validate the record"""
        try:
            # Wait for record to be available
            time.sleep(5)
            
            # Download metadata
            url = f"https://data.caltech.edu/records/{record_id}/export/datacite-json?preview=1"
            response = requests.get(url)
            response.raise_for_status()
            
            # Save metadata
            json_path = os.path.join(self.test_run_dir, f"{record_id}.json")
            with open(json_path, 'w') as f:
                json.dump(response.json(), f, indent=2)
            
            self.log(f"Downloaded metadata to: {json_path}")
            
            # Validate metadata using the imported validator
            validation_errors = validator43(response.json())
            
            if validation_errors:
                self.log("❌ Validation errors found:")
                for error in validation_errors:
                    self.log(f"  - {error}")
                return False
            else:
                self.log("✅ Validation passed successfully")
                return True
                
        except Exception as e:
            self.log(f"Error in download and validation: {e}")
            return False

    def run_test_submission(self):
        """Run the complete test submission process"""
        try:
            self.log("Starting test submission process...")
            
            # Create test files
            test_csv = self.create_test_files()
            
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
                    return ''.join(self.output)
            
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
            
            with patch('builtins.input', side_effect=mock_input):
                try:
                    import cli
                    cli.main()
                except Exception as e:
                    self.log(f"Error during CLI execution: {e}")
                    return False
            
            # Restore stdout
            sys.stdout = sys.__stdout__
            
            # Get output and extract record ID
            cli_output = output_capture.get_output()
            record_id = self.extract_record_id(cli_output)
            
            if not record_id:
                self.log("Failed to extract record ID")
                return False
            
            self.log(f"Successfully created record with ID: {record_id}")
            
            # Validate the record
            return self.download_and_validate_record(record_id)
            
        except Exception as e:
            self.log(f"Error in test submission: {e}")
            return False
        finally:
            # Cleanup
            if os.path.exists(test_csv):
                os.remove(test_csv)
            self.log("Test files cleaned up")

def main():
    tester = CaltechDataTester()
    
    success = tester.run_test_submission()
    
    if success:
        tester.log("\n🎉 Test submission and validation completed successfully!")
    else:
        tester.log("\n❌ Test submission or validation failed - check logs for details")
    
    tester.log(f"\nTest logs available at: {tester.log_file}")

if __name__ == "__main__":
    main()
