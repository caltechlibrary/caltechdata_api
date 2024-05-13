import argparse
import requests
import s3fs
from caltechdata_api import caltechdata_write, caltechdata_edit
from .md_to_json import parse_readme_to_json
import json
import os
from cryptography.fernet import Fernet

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

home_directory = os.path.expanduser("~")
caltechdata_directory = os.path.join(home_directory, ".caltechdata")


if not os.path.exists(caltechdata_directory):
    os.makedirs(caltechdata_directory)


def generate_key():
    return Fernet.generate_key()


# Load the key from a file or generate a new one if not present
def load_or_generate_key():
    key_file = os.path.join(caltechdata_directory, "key.key")
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    else:
        key = generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        return key


# Encrypt the token
def encrypt_token(token, key):
    f = Fernet(key)
    return f.encrypt(token.encode())


# Decrypt the token
def decrypt_token(encrypted_token, key):
    f = Fernet(key)
    return f.decrypt(encrypted_token).decode()


# Function to get or set token
def get_or_set_token():
    key = load_or_generate_key()
    token_file = os.path.join(caltechdata_directory, "token.txt")
    try:
        with open(token_file, "rb") as f:
            encrypted_token = f.read()
            token = decrypt_token(encrypted_token, key)
            return token
    except FileNotFoundError:
        while True:
            token = input("Enter your CaltechDATA token: ").strip()
            confirm_token = input("Confirm your CaltechDATA token: ").strip()
            if token == confirm_token:
                encrypted_token = encrypt_token(token, key)
                with open(token_file, "wb") as f:
                    f.write(encrypted_token)
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
        if user_input.lower() == "y":
            return True
        elif user_input.lower() == "n":
            print("Upload canceled.")
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def check_award_number(award_number):
    response = requests.get(
        f"https://data.caltech.edu/api/awards?q=number:{award_number}"
    )
    data = response.json()
    total_hits = data.get("hits", {}).get("total", 0)
    return total_hits > 0


def get_funding_entries():
    while True:
        try:
            num_entries = int(
                input("How many funding entries do you want to provide? ")
            )
            if num_entries >= 0:
                return num_entries
            else:
                print("Please enter a non-negative integer.")
        except ValueError:
            print("Please enter a valid integer.")


def validate_funder_identifier(funder_identifier):
    response = requests.get(f"https://api.ror.org/organizations/{funder_identifier}")
    if response.status_code == 200:
        return True
    else:
        return False


def get_funding_details():
    award_number = get_user_input("Enter the award number for funding: ")
    award_exists = check_award_number(award_number)
    if not award_exists:
        print(
            f"""Error: No award with number '{award_number}' found in
              CaltechDATA. You will need to provide more details about the
              funding."""
        )
    award_title = get_user_input("Enter the award title for funding: ")
    while True:
        funder_identifier = get_user_input("Enter the funder ROR (https://ror.org): ")
        if validate_funder_identifier(funder_identifier):
            break
        else:
            print(
                """This funder identifier is not a ROR. Please enter a valid
                  ROR identifier (without the url). For example the ROR for the
                  NSF is 021nxhr62."""
            )
    print("-" * 10)
    return {
        "awardNumber": award_number,
        "awardTitle": award_title,
        "funderIdentifier": funder_identifier,
        "funderIdentifierType": "ROR",
    }


def parse_arguments():
    welcome_message()
    args = {}
    args["title"] = get_user_input("Enter the title of the dataset: ")
    args["description"] = get_user_input(
        "Enter the abstract or description of the dataset: "
    )
    print("License options:")
    print("1. Creative Commons Zero Waiver (cc-zero)")
    print("2. Creative Commons Attribution (cc-by)")
    print("3. Creative Commons Attribution Non Commercial (cc-by-nc)")

    # Prompt user to select a license
    while True:
        license_number = input(
            "Enter the number corresponding to the desired license: "
        )
        if license_number.isdigit() and 1 <= int(license_number) <= 8:
            # Valid license number selected
            args["license"] = {
                "1": "cc0-1.0",
                "2": "cc-by-4.0",
                "3": "cc-by-nc-4.0",
            }[license_number]
            break
        else:
            print("Invalid input. Please enter a number between 1 and 8.")

    while True:
        orcid = get_user_input("Enter your ORCID identifier: ")
        family_name, given_name = get_names(orcid)
        if family_name is not None and given_name is not None:
            args["orcid"] = orcid
            break  # Break out of the loop if names are successfully retrieved
        retry = input("Do you want to try again? (y/n): ")
        if retry.lower() != "y":
            print("Exiting program.")
            return
    # Optional arguments
    num_funding_entries = get_funding_entries()
    funding_references = []
    for _ in range(num_funding_entries):
        funding_references.append(get_funding_details())
    args["fundingReferences"] = funding_references
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
            print(
                f"Error: ORCID identifier not found or invalid. Please check the ORCID identifier and try again."
            )
            return None, None
    return family_name, given_name


def write_s3cmd_config(access_key, secret_key, endpoint):
    configf = os.path.join(home_directory, ".s3cfg")
    if not os.path.exists(key_file):
        with open(configf, "w") as file:
            file.write(
                f"""[default]
            access_key = {access_key}
            host_base = {endpoint}
            host_bucket = %(bucket).{endpoint}
            secret_key = {secret_key}
            """
            )


def upload_supporting_file(record_id=None):
    filepath = ""
    filepaths = []
    file_links = []
    while True:
        choice = get_user_input(
            "Do you want to upload or link data files? (upload/link/n): "
        ).lower()
        if choice == "link":
            endpoint = "sdsc.osn.xsede.org"
            path = "ini230004-bucket01/"
            if not record_id:
                access_key = get_user_input("Enter the access key: ")
                secret_key = get_user_input("Enter the secret key: ")
                write_s3cmd_config(access_key, secret_key, endpoint)
                print("""S3 connection configured.""")
                break
            endpoint = f"https://{endpoint}/"
            s3 = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint})
            # Find the files
            files = s3.glob(path + record_id + "/*")

            for link in files:
                fname = link.split("/")[-1]
                if "." not in fname:
                    # If there is a directory, get files
                    folder_files = s3.glob(link + "/*")
                    for file in folder_files:
                        name = file.split("/")[-1]
                        if "." not in name:
                            level_2_files = s3.glob(file + "/*")
                            for f in level_2_files:
                                name = f.split("/")[-1]
                                if "." not in name:
                                    level_3_files = s3.glob(f + "/*")
                                    for l3 in level_3_files:
                                        file_links.append(endpoint + l3)
                                else:
                                    file_links.append(endpoint + f)
                        else:
                            file_links.append(endpoint + file)
                else:
                    file_links.append(endpoint + link)
            return filepath, file_links
        elif choice == "upload":
            print("Current files in the directory:")
            files = [
                f for f in os.listdir() if not f.endswith(".json") and os.path.isfile(f)
            ]
            print("\n".join(files))
            while True:
                filename = get_user_input(
                    "Enter the filename to upload as a supporting file (or 'n' to finish): "
                )
                if filename == "n":
                    break
                if filename in files:
                    file_size = os.path.getsize(filename)
                    if file_size > 1024 * 1024 * 1024:
                        print(
                            """The file is greater than 1 GB. Please upload the
                        metadata to CaltechDATA, and you'll be provided
                        instructions to upload the files to S3 directly."""
                        )
                    else:
                        filepath = os.path.abspath(filename)
                        filepaths.append(filepath)
                else:
                    print(
                        f"Error: File '{filename}' not found. Please enter a valid filename."
                    )

            add_more = get_user_input("Do you want to add more files? (y/n): ").lower()
            if add_more != "y":
                break

        elif choice == "n":
            break
        else:
            print("Invalid input. Please enter 'link' or 'upload' or 'n'.")

    return filepaths, file_links


def upload_data_from_file():
    while True:
        print("Current JSON files in the directory:")
        files = [f for f in os.listdir() if f.endswith(".json") and os.path.isfile(f)]
        print("\n".join(files))

        filename = get_user_input(
            "Enter a README.md or JSON filename to upload to CaltechDATA (or type 'exit' to go back): "
        )

        if filename.lower() == "exit":
            return None

        if filename == "README.md":
            data = parse_readme_to_json(filename)
            return data
        else:
            try:
                with open(filename, "r") as file:
                    data = json.load(file)
                return data

            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON format in the file '{filename}'. {str(e)}")


def main():
    choice = get_user_input(
        "Do you want to create or edit a CaltechDATA record? (create/edit): "
    ).lower()
    if choice == "create":
        create_record()
    elif choice == "edit":
        edit_record()
    else:
        print("Invalid choice. Please enter 'create' or 'edit'.")


def create_record():
    token = get_or_set_token()
    print("Using CaltechDATA token:", token)
    while True:
        choice = get_user_input(
            "Do you want to use metadata from an existing file or create new metadata? (existing/create): "
        ).lower()
        if choice == "existing":
            existing_data = upload_data_from_file()
            filepath, file_link = upload_supporting_file()
            if existing_data:
                if filepath != "":
                    response = caltechdata_write(
                        existing_data, token, filepath, production=False, publish=False
                    )
                elif file_link != "":
                    response = caltechdata_write(
                        existing_data,
                        token,
                        file_links=[file_link],
                        s3_link=file_link,
                        production=False,
                        publish=False,
                    )
                else:
                    response = caltechdata_write(
                        existing_data, token, production=False, publish=False
                    )
                rec_id = response
                print(
                    f"""You can view and publish this record at https://data.caltechlibrary.dev/uploads/{rec_id}
                    If you need to upload large files to S3, you can type
                    `s3cmd put DATA_FILE s3://ini230004-bucket01/{rec_id}/"""
                )
                break
            else:
                print("Going back to the main menu.")
        elif choice == "create":
            args = parse_arguments()
            family_name, given_name = get_names(args["orcid"])
            metadata = {
                "titles": [{"title": args["title"]}],
                "descriptions": [
                    {"description": args["description"], "descriptionType": "Abstract"}
                ],
                "creators": [
                    {
                        "affiliation": [
                            {
                                "affiliationIdentifier": affiliation_identifier,
                                "affiliationIdentifierScheme": affiliationIdentifierScheme,
                                "name": name,
                            }
                        ],
                        "familyName": family_name,
                        "givenName": given_name,
                        "name": f"{family_name}, {given_name}",
                        "nameIdentifiers": [
                            {
                                "nameIdentifier": args["orcid"],
                                "nameIdentifierScheme": "ORCID",
                            }
                        ],
                        "nameType": "Personal",
                    }
                ],
                "types": {"resourceType": "", "resourceTypeGeneral": "Dataset"},
                "rightsList": [
                    {
                        "rightsIdentifier": args["license"],
                    }
                ],
                "fundingReferences": args["fundingReferences"],
                "schemaVersion": "http://datacite.org/schema/kernel-4",
            }
            filepath, file_link = upload_supporting_file()
            if confirm_upload():
                if filepath != "":
                    response = caltechdata_write(
                        metadata, token, filepath, production=False, publish=False
                    )
                elif file_link != "":
                    response = caltechdata_write(
                        metadata,
                        token,
                        file_links=[file_link],
                        production=False,
                        publish=False,
                    )
                else:
                    response = caltechdata_write(
                        metadata, token, production=False, publish=False
                    )
                rec_id = response
                print(
                    f"""You can view and publish this record at https://data.caltechlibrary.dev/uploads/{rec_id}
                    If you need to upload large files to S3, you can type
                    `s3cmd put DATA_FILE s3://ini230004-bucket01/{rec_id}/"""
                )
                with open(response + ".json", "w") as file:
                    json.dump(metadata, file, indent=2)
                break
            else:
                break
        else:
            print("Invalid choice. Please enter 'existing' or 'create'.")


def edit_record():
    record_id = input("Enter the CaltechDATA record ID: ")
    token = get_or_set_token()
    file_name = download_file_by_id(record_id, token)
    if file_name:
        try:
            # Read the edited metadata file
            with open(file_name, "r") as file:
                metadata = json.load(file)
            response = caltechdata_edit(
                record_id, metadata, token, production=False, publish=False
            )
            if response:
                print("Metadata edited successfully.")
            else:
                print("Failed to edit metadata.")
        except Exception as e:
            print(f"An error occurred during metadata editing: {e}")
    else:
        print("No metadata file found.")
    choice = get_user_input("Do you want to add files? (y/n): ").lower()
    if choice == "y":
        filepath, file_link = upload_supporting_file(record_id)
        print(file_link)
        if filepath != "":
            response = caltechdata_edit(
                record_id, token=token, files=filepath, production=False, publish=False
            )
        elif file_link != "":
            response = caltechdata_edit(
                record_id,
                metadata,
                token=token,
                file_links=file_link,
                production=False,
                publish=False,
            )
        rec_id = response
        print(
            f"You can view and publish this record at https://data.caltechlibrary.dev/uploads/{rec_id}\n"
        )


def download_file_by_id(record_id, token=None):
    url = f"https://data.caltechlibrary.dev/api/records/{record_id}"

    headers = {
        "accept": "application/vnd.datacite.datacite+json",
    }

    if token:
        headers["Authorization"] = "Bearer %s" % token

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            # Might have a draft
            response = requests.get(
                url + "/draft",
                headers=headers,
            )
            if response.status_code != 200:
                raise Exception(f"Record {record_id} does not exist, cannot edit")
        file_content = response.content
        file_name = f"downloaded_data_{record_id}.json"
        with open(file_name, "wb") as file:
            file.write(file_content)
        print(f"Metadata downloaded successfully: {file_name}")
        with open(file_name, "r") as file:
            metadata = json.load(file)
            while True:
                print("Fields:")
                for i, field in enumerate(metadata.keys()):
                    print(f"{i + 1}. {field}")

                field_choice = int(
                    input(
                        "Enter the number of the field you want to edit (or 0 to skip, 'exit' to exit): "
                    )
                )

                if field_choice == 0:
                    break

                selected_field = list(metadata.keys())[field_choice - 1]

                if isinstance(metadata[selected_field], list):
                    while True:
                        print(f"Items in {selected_field}:")
                        for i, item in enumerate(metadata[selected_field]):
                            print(f"{i + 1}. {item}")

                        item_choice = int(
                            input(
                                "Enter the number of the item you want to edit (or 0 to go back): "
                            )
                        )

                        if item_choice == 0:
                            break

                        selected_item = metadata[selected_field][item_choice - 1]

                        while True:
                            print(f"Subfields for {selected_field}:")
                            for i, subfield in enumerate(selected_item.keys()):
                                print(f"{i + 1}. {subfield}")

                            subfield_choice = int(
                                input(
                                    "Enter the number of the subfield you want to edit (or 0 to go back): "
                                )
                            )

                            if subfield_choice == 0:
                                break

                            selected_subfield = list(selected_item.keys())[
                                subfield_choice - 1
                            ]

                            new_value = input(
                                f"Enter the new value for {selected_subfield}: "
                            )

                            metadata[selected_field][item_choice - 1][
                                selected_subfield
                            ] = new_value

                            with open(file_name, "w") as file:
                                json.dump(metadata, file, indent=2)

                            print(f"File updated successfully.")

                else:
                    while True:
                        print(f"Subfields for {selected_field}:")
                        for i, subfield in enumerate(metadata[selected_field].keys()):
                            print(f"{i + 1}. {subfield}")

                        subfield_choice = int(
                            input(
                                "Enter the number of the subfield you want to edit (or 0 to go back): "
                            )
                        )

                        if subfield_choice == 0:
                            break

                        selected_subfield = list(metadata[selected_field].keys())[
                            subfield_choice - 1
                        ]

                        new_value = input(
                            f"Enter the new value for {selected_subfield}: "
                        )

                        metadata[selected_field][selected_subfield] = new_value

                        with open(file_name, "w") as file:
                            json.dump(metadata, file, indent=2)

                        print(f"File updated successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
    return file_name


if __name__ == "__main__":
    main()
