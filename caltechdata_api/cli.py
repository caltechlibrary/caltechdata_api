import argparse
import requests
import s3fs
from caltechdata_api import caltechdata_write, caltechdata_edit, parse_readme_to_json
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


# Function to get or set token with support for test system.
def get_or_set_token(production=True):
    # First check for environment variable
    env_token = os.environ.get("CALTECHDATA_TOKEN")
    if env_token:
        print("Using token from environment variable")
        return env_token

    key = load_or_generate_key()

    # Use different token files for production and test environment.
    token_filename = "token.txt" if production else "token_test.txt"
    token_file = os.path.join(caltechdata_directory, token_filename)

    try:
        with open(token_file, "rb") as f:
            encrypted_token = f.read()
            token = decrypt_token(encrypted_token, key)
            print(
                "Using saved CaltechDATA production token."
                if production
                else "Using saved CaltechDATA test token."
            )
            return token
    except FileNotFoundError:
        while True:
            token = input(
                f"Enter your {'Production' if production else 'Test'} CaltechDATA token: "
            ).strip()
            confirm_token = input(
                f"Confirm your {'Production' if production else 'Test'} CaltechDATA token: "
            ).strip()
            if token == confirm_token:
                encrypted_token = encrypt_token(token, key)
                with open(token_file, "wb") as f:
                    f.write(encrypted_token)
                return token
            else:
                print("Tokens do not match. Please try again.")


# Delete the saved token file.
def delete_saved_token():
    token_file = os.path.join(caltechdata_directory, "token.txt")
    if os.path.exists(token_file):
        os.remove(token_file)
        print("Token deleted successfully.")
    else:
        print("No token found to delete.")


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
        return response.json().get("name")
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
        name = validate_funder_identifier(funder_identifier)
        if name:
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
        "funderName": name,
        "funderIdentifier": funder_identifier,
        "funderIdentifierType": "ROR",
    }


# Add profile handling functions
def save_profile():
    profile_file = os.path.join(caltechdata_directory, "profile.json")

    # Get ORCID
    while True:
        orcid = get_user_input("Enter your ORCID identifier: ")
        orcid = normalize_orcid(orcid)
        family_name, given_name = get_names(orcid)
        if family_name is not None and given_name is not None:
            break
        retry = input("Do you want to try again? (y/n): ")
        if retry.lower() != "y":
            return None

    # Get funding details
    funding_references = []
    num_funding_entries = get_funding_entries()
    for _ in range(num_funding_entries):
        funding_references.append(get_funding_details())

    profile_data = {
        "orcid": orcid,
        "family_name": family_name,
        "given_name": given_name,
        "funding_references": funding_references,
    }

    with open(profile_file, "w") as f:
        json.dump(profile_data, f, indent=2)

    print("Profile saved successfully!")
    return profile_data


def load_profile():
    profile_file = os.path.join(caltechdata_directory, "profile.json")
    try:
        with open(profile_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def get_or_create_profile():
    profile = load_profile()
    if profile:
        use_saved = input("Use saved profile? (y/n): ").lower()
        if use_saved == "y":
            return profile

    print("Creating new profile...")
    return save_profile()


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
                "1": {
                    "rights": "Creative Commons Zero v1.0 Universal",
                    "rightsIdentifier": "cc0-1.0",
                },
                "2": {
                    "rights": "Creative Commons Attribution v4.0 Universal",
                    "rightsIdentifier": "cc-by-4.0",
                },
                "3": {
                    "rights": "Creative Commons Attribution Non-Commercial v4.0 Universal",
                    "rightsIdentifier": "cc-by-nc-4.0",
                },
            }[license_number]
            break
        else:
            print("Invalid input. Please enter a number between 1 and 8.")
    # Load or create profile
    profile = get_or_create_profile()
    if profile:
        args["orcid"] = profile["orcid"]
        args["family_name"] = profile["family_name"]
        args["given_name"] = profile["given_name"]
        args["fundingReferences"] = profile["funding_references"]
    else:
        print("Failed to load or create profile. Exiting.")
        return None

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


def write_s3cmd_config(endpoint):
    configf = os.path.join(home_directory, ".s3cfg")
    if not os.path.exists(configf):
        access_key = get_user_input("Enter the access key: ")
        secret_key = get_user_input("Enter the secret key: ")
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
    file_link = ""
    file_links = []
    idx = 0
    while True:
        choice = get_user_input(
            "Do you want to upload or link data files? (upload/link/n): "
        ).lower()
        if choice == "link":
            endpoint = "sdsc.osn.xsede.org"
            path = "ini230004-bucket01/"
            if not record_id:
                write_s3cmd_config(endpoint)
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
            idx += 1
            print((f"{idx}/ \n").join(files))
            while True:
                filename = get_user_input(
                    "Enter the filename to upload as a supporting file (or '*' to get all files currently in this directory, or the index number of the file as displayed followed by a /, otherwise 'n' to finish): "
                )
                if filename == "*":
                    for files_name in files:
                        filepath = os.path.abspath(files_name)
                        filepaths.append(filepath)
                    print("All files added successfully")
                elif filename == "n":
                    break
                elif (not len(filename) == 0) and (filename[len(filename) - 1] == "/"):
                    try:
                        files_name = files[int(filename[0]) - 1]
                        filepath = os.path.abspath(files_name)
                        filepaths.append(filepath)
                        print("File added successfully")
                    except ValueError:
                        continue
                elif filename in files:
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
                        print("File added successfully")
                else:
                    print(
                        f"Error: File '{filename}' not found. Please enter a valid filename."
                    )
                add_more = get_user_input(
                    "Do you want to add more files? (y/n): "
                ).lower()
                if add_more != "y":
                    break
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


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="CaltechDATA CLI tool.")
    parser.add_argument(
        "-test", action="store_true", help="Use test mode, sets production to False"
    )
    parser.add_argument(
        "--delete-token", action="store_true", help="Delete the saved token."
    )
    args = parser.parse_args()
    return args


def normalize_orcid(val):
    orcid_urls = ["https://orcid.org/", "http://orcid.org/", "orcid.org/"]
    for orcid_url in orcid_urls:
        if val.startswith(orcid_url):
            val = val[len(orcid_url) :]
            break

    val = val.replace("-", "").replace(" ", "")
    if len(val) != 16 or not val.isdigit():
        raise ValueError(f"Invalid ORCID identifier: {val}")
    return "-".join([val[0:4], val[4:8], val[8:12], val[12:16]])


def main():
    args = parse_args()
    production = not args.test
    if args.delete_token:
        delete_saved_token()
    while True:
        choice = get_user_input(
            "What would you like to do? (create/edit/profile/exit): "
        ).lower()

        if choice == "create":
            create_record(production)
        elif choice == "edit":
            edit_record(production)
        elif choice == "profile":
            save_profile()
        elif choice == "exit":
            break
        else:
            print(
                "Invalid choice. Please enter 'create', 'edit', 'profile', or 'exit'."
            )


def create_record(production):
    token = get_or_set_token(production)
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
                        existing_data,
                        token,
                        filepath,
                        production=production,
                        publish=False,
                    )
                elif file_link != "":
                    response = caltechdata_write(
                        existing_data,
                        token,
                        file_links=[file_link],
                        s3_link=file_link,
                        production=True,
                        publish=False,
                    )
                else:
                    response = caltechdata_write(
                        existing_data, token, production=production, publish=False
                    )
                rec_id = response
                print_upload_message(rec_id, production)
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
                "publisher": "CaltechDATA",
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
                    args["license"],
                ],
                "fundingReferences": args["fundingReferences"],
                "schemaVersion": "http://datacite.org/schema/kernel-4",
            }
            filepath, file_link = upload_supporting_file()
            if confirm_upload():
                if filepath != "":
                    response = caltechdata_write(
                        metadata, token, filepath, production=production, publish=False
                    )
                elif file_link != "":
                    response = caltechdata_write(
                        metadata,
                        token,
                        file_links=[file_link],
                        production=production,
                        publish=False,
                    )
                else:
                    response = caltechdata_write(
                        metadata, token, production=production, publish=False
                    )
                rec_id = response

                print_upload_message(rec_id, production)
                with open(response + ".json", "w") as file:
                    json.dump(metadata, file, indent=2)
                exit()
                break
            else:
                break
        else:
            print("Invalid choice. Please enter 'existing' or 'create'.")


def print_upload_message(rec_id, production):
    base_url = (
        "https://data.caltech.edu/uploads/"
        if production
        else "https://data.caltechlibrary.dev/uploads/"
    )
    print(
        f"""You can view and publish this record at
        {base_url}{rec_id}
        If you need to upload large files to S3, you can type
        `s3cmd put DATA_FILE s3://ini230004-bucket01/{rec_id}/`"""
    )


def edit_record(production):
    record_id = input("Enter the CaltechDATA record ID: ")
    token = get_or_set_token(production)
    file_name = download_file_by_id(record_id, token)

    if file_name:
        try:
            # Read the edited metadata file
            with open(file_name, "r") as file:
                metadata = json.load(file)
            response = caltechdata_edit(
                record_id, metadata, token, production=production, publish=False
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
        if production:
            API_URL_TEMPLATE = "https://data.caltech.edu/api/records/{record_id}/files"
            API_URL_TEMPLATE_DRAFT = (
                "https://data.caltech.edu/api/records/{record_id}/draft/files"
            )
        else:
            API_URL_TEMPLATE = (
                "https://data.caltechlibrary.dev/api/records/{record_id}/files"
            )
            API_URL_TEMPLATE_DRAFT = (
                "https://data.caltechlibrary.dev/api/records/{record_id}/draft/files"
            )

        url = API_URL_TEMPLATE.format(record_id=record_id)
        url_draft = API_URL_TEMPLATE_DRAFT.format(record_id=record_id)

        headers = {
            "accept": "application/json",
        }

        if token:
            headers["Authorization"] = "Bearer %s" % token

        response = requests.get(url, headers=headers)
        response_draft = requests.get(url_draft, headers=headers)
        data = response.json()
        data_draft = response_draft.json()
        # Check if 'entries' exists and its length
        if (
            len(data.get("entries", [])) == 0
            and len(data_draft.get("entries", [])) == 0
        ):
            keepfile = False
        else:
            keepfile = (
                input("Do you want to keep existing files? (y/n): ").lower() == "y"
            )

        filepath, file_link = upload_supporting_file(record_id)
        if file_link:
            print(file_link)

        if filepath != "":
            response = caltechdata_edit(
                record_id,
                token=token,
                files=filepath,
                production=production,
                publish=False,
                keepfiles=keepfile,
            )
        elif file_link != "":
            response = caltechdata_edit(
                record_id,
                metadata,
                token=token,
                file_links=file_link,
                production=production,
                publish=False,
                keepfiles=keepfile,
            )

        rec_id = response
        print_upload_message(rec_id, production)


def download_file_by_id(record_id, token=None):
    url = f"https://data.caltech.edu/api/records/{record_id}"

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
                url = f"https://data.caltechlibrary.dev/api/records/{record_id}"
                response = requests.get(
                    url,
                    headers=headers,
                )
                if response.status_code != 200:
                    # Might have a draft
                    response = requests.get(
                        url + "/draft",
                        headers=headers,
                    )
                    if response.status_code != 200:
                        raise Exception(
                            f"Record {record_id} does not exist, cannot edit"
                        )
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
