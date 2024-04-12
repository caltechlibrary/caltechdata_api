import codecs
import getpass
import os 

README_FILE = '/home/rbhattar/caltechdataapi/caltechdata_api/README.md'

def read_readme():
    title = ''
    description = ''

    try:
        with codecs.open(README_FILE, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if lines:
                title = lines[0].strip()
                if len(lines) > 1:
                    description = lines[1].strip()

    except IOError:
        print("Error: {README_FILE} not found.")

    return title, description

def create_readme(title, description):
    try:
        with codecs.open(README_FILE, 'w', encoding='utf-8') as file:
            file.write("{}\n{}\n".format(title, description))
        print("Created {} with default content.".format(README_FILE))
    except IOError:
        print("Error: Unable to create {}.".format(README_FILE))

def prompt_for_license():
    print("Please choose a data license:")
    print("1. CC0 1.0 Universal (CC0 1.0) Public Domain Dedication")
    print("2. CC BY 4.0 International (CC BY 4.0)")
    print("3. CC BY-SA 4.0 International (CC BY-SA 4.0)")
    print("4. CC BY-NC 4.0 International (CC BY-NC 4.0)")
    
    # Prompt user to enter a number
    while True:
        try:
            license_choice = int(input("Enter the number corresponding to your chosen license: "))
            if 1 <= license_choice <= 4:
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    return license_choice

def get_caltechdata_token():
    token = os.getenv("CALTECHDATA_TOKEN")

    if not token:
        # If token is not set, prompt the user to enter it
        token = getpass.getpass("Enter CaltechDATA Token: ")
        # Save token to environment variable for future runs
        os.environ["CALTECHDATA_TOKEN"] = token

    return token

if __name__ == "__main__":
    # Read existing README.md file
    title, description = read_readme()

    # If not present, create README.md with default content
    if not title or not description:
        create_readme("Default Title", "Default Description")

    print("Title:", title)
    print("Description:", description)

    license_choice = prompt_for_license()
    print("You chose license {}.".format(license_choice))
    token = get_caltechdata_token()
    print(token)
