import argparse
import requests
from caltechdata_api import caltechdata_write, caltechdata_edit
from md_to_json import parse_readme_to_json
import json
import os
import keyring

CALTECHDATA_API = "https://data.caltech.edu/api/names?q=identifiers.identifier:{}"
ORCID_API = "https://orcid.org/"
HEADERS = {"Accept": "application/json"}

name = ""
affiliationIdentifierScheme = ""
affiliation_identifier = ""

awardNumber = ""
awardTitle = ""
funderIdentifier = ""
funderIdentifierType = ""
funderName = ""


def get_or_set_token():
    stored_token = keyring.get_password("caltechdata_cli", "rdmtok")
    if stored_token:
        return stored_token

    # If token is not stored, ask the user for input and store it securely
    while True:
        token = get_user_input("Enter your CaltechDATA token: ")
        confirm_token = get_user_input("Confirm your CaltechDATA token: ")
        if token == confirm_token:
            keyring.set_password("caltechdata_cli", "rdmtok", token)
            return token
        else:
            print("Tokens do not match. Please try again.")


def welcome_message():
    print("Welcome to CaltechDATA CLI")


def get_user_input(prompt, required=True):
    while True:
        user_input = input(prompt)
        if required and not user_input:
            print("This field is required. Please provide a value.")
        else:
            return user_input


def confirm_upload():
    while True:
        user_input = input("Do you want to send this record to CaltechDATA? (y/n): ")
        if user_input.lower() == 'y':
            return True
        elif user_input.lower() == 'n':
            print("Upload canceled.")
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def check_award_number(award_number):
    response = requests.get(f"https://data.caltech.edu/api/awards?q=number:{award_number}")
    data = response.json()
    total_hits = data.get("hits", {}).get("total", 0)
    return total_hits > 0


def get_funding_entries():
    while True:
        try:
            num_entries = int(input("How many funding entries do you want to provide? "))
            if num_entries >= 0:
                return num_entries
            else:
                print("Please enter a non-negative integer.")
        except ValueError:
            print("Please enter a valid integer.")


def validate_funder_identifier(funder_identifier):
    response = requests.get(f"https://api.ror.org/organizations/{funder_identifier}")
    print(response.status_code)
    print(response.url)
    if response.status_code == 200:
        return True
    else:
        return False


def get_funding_details():
    award_number = get_user_input("Enter the award number for funding: ")
    award_exists = check_award_number(award_number)
    if not award_exists:
        print(f"""Error: No award with number '{award_number}' found in
              CaltechDATA. You will need to provide more details about the
              funding.""")
    award_title = get_user_input("Enter the award title for funding: ")
    while True:
        funder_identifier = get_user_input("Enter the funder ROR (https://ror.org): ")
        if validate_funder_identifier(funder_identifier):
            break
        else:
            print("""This funder identifier is not a ROR. Please enter a valid
                  ROR identifier (without the url). For example the ROR for the
                  NSF is 021nxhr62.""")
    print("-" * 10)
    return {
        "awardNumber": award_number,
        "awardTitle": award_title,
        "funderIdentifier": funder_identifier,
        "funderIdentifierType": 'ROR'
    }


def parse_arguments():
    welcome_message()
    args = {}
    args['title'] = get_user_input("Enter the title of the dataset: ")
    args['description'] = get_user_input("Enter the abstract or description of the dataset: ")
    print("License options:")
    print("1. Creative Commons Zero Waiver (cc-zero)")
    print("2. Creative Commons Attribution (cc-by)")
    print("3. Creative Commons Attribution Non Commercial (cc-by-nc)")

    # Prompt user to select a license
    while True:
        license_number = input("Enter the number corresponding to the desired license: ")
        if license_number.isdigit() and 1 <= int(license_number) <= 8:
            # Valid license number selected
            args['license'] = {
                '1': 'cc0-1.0',
                '2': 'cc-by-4.0',
                '3': 'cc-by-nc-4.0',
            }[license_number]
            break
        else:
            print("Invalid input. Please enter a number between 1 and 8.")

    while True:
        orcid = get_user_input("Enter your ORCID identifier: ")
        family_name, given_name = get_names(orcid)
        if family_name is not None and given_name is not None:
            args['orcid'] = orcid
            break  # Break out of the loop if names are successfully retrieved
        retry = input("Do you want to try again? (y/n): ")
        if retry.lower() != 'y':
            print("Exiting program.")
            return
    # Optional arguments
    num_funding_entries = get_funding_entries()
    funding_references = []
    for _ in range(num_funding_entries):
        funding_references.append(get_funding_details())
    args['fundingReferences'] = funding_references
    return args


def query_caltechdata_api(orcid):
    response = requests.get(CALTECHDATA_API.format(orcid), headers=HEADERS)
    return response.json()


def query_orcid_api(orcid):
    response = requests.get(ORCID_API + orcid, headers=HEADERS)
    return response.json()


def get_names(orcid):
    caltechdata_response = query_caltechdata_api(orcid)
    global affiliationIdentifierScheme, affiliation_identifier, name
    if caltechdata_response.get("hits", {}).get("hits"):
        hit = caltechdata_response["hits"]["hits"][0]
        family_name = hit.get("family_name", "")
        given_name = hit.get("given_name", "")
        affiliation_identifier = "05dxps055"
        affiliationIdentifierScheme = "ROR"
        name = "California Institute of Technology"

    else:
        orcid_link = "https://orcid.org/"
        headers = {"Accept": "application/json"}
        orcid_response = requests.get(orcid_link + orcid, headers=headers)
        try:
            orcid_data = orcid_response.json()
            name_info = orcid_data.get("person", {}).get("name", {})
            family_name = name_info.get("family-name", {}).get("value", "")
            given_name = name_info.get("given-names", {}).get("value", "")
        except json.decoder.JSONDecodeError:
            print(f"Error: ORCID identifier not found or invalid. Please check the ORCID identifier and try again.")
            return None, None
    return family_name, given_name


def upload_supporting_file():
    filepath = ""
    file_link = ""
    while True:
        choice = get_user_input("Do you want to upload an additional supporting file? (y/n): ").lower()
        if choice == 'y':
            print("Current files in the directory:")
            files = [f for f in os.listdir() if not f.endswith('.json') and os.path.isfile(f)]
            print("\n".join(files))
            filename = get_user_input("Enter the filename to upload as a supporting file: ")
            if filename in files:
                file_size = os.path.getsize(filename)
                if file_size > 1024 * 1024:  
                    file_link = get_user_input("Enter the S3 link to the file (File size is more than 1MB): ")
                    if file_link:
                        return filepath, file_link
                    else:
                        print("Link is required for files larger than 1MB.")
                        continue
                else:
                    filepath = os.path.abspath(filename)
                    break
            else:
                print(f"Error: File '{filename}' not found. Please enter a valid filename.")
        elif choice == 'n':
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
    
    return filepath, file_link


def upload_data_from_file():
    while True:
        print("Current JSON files in the directory:")
        files = [f for f in os.listdir() if f.endswith('.json') and os.path.isfile(f)]
        print("\n".join(files))

        filename = get_user_input("Enter a README.md or JSON filename to upload to CaltechDATA (or type 'exit' to go back): ")

        if filename.lower() == 'exit':
            return None

        if filename == 'README.md':
            data = parse_readme_to_json(filename)
            print(json.dumps(data))
            return data
        else:
            try:
                with open(filename, 'r') as file:
                    data = json.load(file)
                return data

            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON format in the file '{filename}'. {str(e)}")


def main():
    choice = get_user_input("Do you want to create or edit a CaltechDATA record? (create/edit): ").lower()
    if choice == 'create':
        create_record()
    elif choice == 'edit':
        edit_record()
    else:
        print("Invalid choice. Please enter 'create' or 'edit'.")


def create_record():
    token = get_or_set_token()
    print("Using CaltechDATA token:", token)
    while True:
        choice = get_user_input("Do you want to use metadata from an existing file or create new metadata? (existing/create): ").lower()
        if choice == 'existing':
            existing_data = upload_data_from_file()
            filepath, file_link = upload_supporting_file()
            if existing_data:
                if filepath != "":
                    response = caltechdata_write(existing_data, token, filepath, production=False, publish=True)
                elif file_link != "":
                    response = caltechdata_write(existing_data, token, s3=file_link, s3_link=file_link, production=False, publish=True)
                else:
                    response = caltechdata_write(existing_data, token, production=False, publish=True)
                print(response)
                break
            else:
                print("Going back to the main menu.")
        elif choice == 'create':
            args = parse_arguments()
            family_name, given_name = get_names(args['orcid'])
            metadata = {
                "titles": [{"title": args['title']}],
                "descriptions": [{"description": args['description'], "descriptionType": "Abstract"}],
                "creators": [
                    {
                        "affiliation": [
                            {
                                "affiliationIdentifier": affiliation_identifier,
                                "affiliationIdentifierScheme": affiliationIdentifierScheme,
                                "name": name
                            }
                        ],
                        "familyName": family_name,
                        "givenName": given_name,
                        "name": f"{family_name}, {given_name}",
                        "nameIdentifiers": [
                            {
                                "nameIdentifier": args['orcid'],
                                "nameIdentifierScheme": "ORCID",
                            }
                        ],
                        "nameType": "Personal",
                    }
                ],
                "types": {"resourceType": "", "resourceTypeGeneral": "Dataset"},
                "rightsList": [
                    {
                        "rightsIdentifier": args['license'],
                    }
                ],
                "fundingReferences": args['fundingReferences'],
                "schemaVersion": "http://datacite.org/schema/kernel-4",
            }
            filepath, file_link = upload_supporting_file()
            if confirm_upload():
                if filepath != "":
                    response = caltechdata_write(metadata, token, filepath, production=False, publish=True)
                elif file_link != "":
                    response = caltechdata_write(metadata, token, s3=file_link, s3_link=file_link, production=False, publish=True)
                else:
                    response = caltechdata_write(metadata, token, production=False, publish=True)
                print(response)
                print(family_name, given_name)
                with open(response + ".json", "w") as file:
                    json.dump(metadata, file, indent=2)
                break
            else:
                break
        else:
            print("Invalid choice. Please enter 'existing' or 'create'.")


def edit_record():
    choice = get_user_input("Do you want to edit metadata or files? (metadata/files): ").lower()
    if choice == 'metadata':
        edit_metadata()
    elif choice == 'files':
        upload_file()
    else:
        print("Invalid choice. Please enter 'metadata' or 'files'.")

def edit_metadata():
    file_name, record_id = download_file_by_id()
    if file_name:
        try:
            # Read the edited metadata file
            with open(file_name, "r") as file:
                metadata = json.load(file)
            token = get_or_set_token()
            response = caltechdata_edit(record_id, metadata, token, production=False, publish=True)
            if response:
                print("Metadata edited successfully.")
            else:
                print("Failed to edit metadata.")
        except Exception as e:
            print(f"An error occurred during metadata editing: {e}")
    else:
        print("No metadata file found.")

def upload_file():
    id = get_user_input("Enter the record ID: ")
    if id:
        files = [f for f in os.listdir() if not f.endswith('.json') and os.path.isfile(f)]
        print("\n".join(files))
        file_names = get_user_input("Enter the filename to upload as a supporting file: ")
        if file_names:
            token = get_or_set_token()
            url = f"https://data.caltechlibrary.dev/records/{id}/export/datacite-json"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    file_content = response.content
                    file_name = f"metadata_{id}.json"
                    with open(file_name, "wb") as file:
                        file.write(file_content)
                    with open(file_name, "r") as file:
                        metadata = json.load(file)
                    # Check file size
                    file_size = os.path.getsize(file_names)
                    if file_size > 1024 * 1024:  # 1 MB
                        file_link = input("File larger than 1MB. Please put the S3 link: ")
                        response = caltechdata_edit(id, metadata, token, s3=file_link, s3_link=file_link, production=False, publish=True)
                    else:
                        with open(file_names, "rb") as file:
                            response = caltechdata_edit(id, metadata, token, file_names, production=False, publish=True)
                    
                    if response:
                        print("File uploaded successfully.")
                    else:
                        print("Failed to upload metadata.")
                else:
                    print(f"Failed to download metadata. Status code: {response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Filename is required.")
    else:
        print("Record ID is required.")


def download_file_by_id():
    while True:
        record_id = input("Enter the ID (or 'exit' to quit): ")
        if record_id.lower() == 'exit':
            print("Exiting the program.")
            break
        record_ids = record_id

        url = f"https://data.caltechlibrary.dev/records/{record_id}/export/datacite-json"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_content = response.content
                file_name = f"downloaded_data_{record_id}.json"
                with open(file_name, "wb") as file:
                    file.write(file_content)
                print(f"File downloaded successfully: {file_name}")
                with open(file_name, "r") as file:
                    metadata = json.load(file)
                while True:
                    print("Fields:")
                    for i, field in enumerate(metadata.keys()):
                        print(f"{i + 1}. {field}")

                    field_choice = int(input("Enter the number of the field you want to edit (or 0 to skip, 'exit' to exit): "))

                    if field_choice == 0:
                        break

                    selected_field = list(metadata.keys())[field_choice - 1]

                    if isinstance(metadata[selected_field], list):
                        while True:
                            print(f"Items in {selected_field}:")
                            for i, item in enumerate(metadata[selected_field]):
                                print(f"{i + 1}. {item}")

                            item_choice = int(input("Enter the number of the item you want to edit (or 0 to go back): "))

                            if item_choice == 0:
                                break

                            selected_item = metadata[selected_field][item_choice - 1]

                            while True:
                                print(f"Subfields for {selected_field}:")
                                for i, subfield in enumerate(selected_item.keys()):
                                    print(f"{i + 1}. {subfield}")

                                subfield_choice = int(input("Enter the number of the subfield you want to edit (or 0 to go back): "))

                                if subfield_choice == 0:
                                    break

                                selected_subfield = list(selected_item.keys())[subfield_choice - 1]

                                new_value = input(f"Enter the new value for {selected_subfield}: ")

                                metadata[selected_field][item_choice - 1][selected_subfield] = new_value

                                with open(file_name, "w") as file:
                                    json.dump(metadata, file, indent=2)

                                print(f"File updated successfully.")

                    else:
                        while True:
                            print(f"Subfields for {selected_field}:")
                            for i, subfield in enumerate(metadata[selected_field].keys()):
                                print(f"{i + 1}. {subfield}")

                            subfield_choice = int(input("Enter the number of the subfield you want to edit (or 0 to go back): "))

                            if subfield_choice == 0:
                                break

                            selected_subfield = list(metadata[selected_field].keys())[subfield_choice - 1]

                            new_value = input(f"Enter the new value for {selected_subfield}: ")

                            metadata[selected_field][selected_subfield] = new_value

                            with open(file_name, "w") as file:
                                json.dump(metadata, file, indent=2)

                            print(f"File updated successfully.")

            else:
                print(f"Failed to download file. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred: {e}")
    return file_name, record_ids

if __name__ == "__main__":
    main()
