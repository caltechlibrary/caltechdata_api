import re
import json
import requests


class ReadmeFormatException(Exception):
    """Custom exception for errors in the README format."""


def camel_case(s):
    """Converts a string to camelCase."""
    s = re.sub(r"(\s|_|-)+", " ", s).title().replace(" ", "")
    return s[0].lower() + s[1:] if s else ""


def expand_special_keys(key, value):
    """Expand special keys into their structured format (affiliation, nameIdentifiers)."""
    if key == "affiliation":
        if "ror.org" not in value:
            raise ValueError("Affiliation Identifier is not a ROR")
        ror = value.split("ror.org/")[1].split("]")[0]
        response = requests.get(f"https://api.ror.org/organizations/{ror}").json()
        return [
            {
                "affiliationIdentifier": ror,
                "affiliationIdentifierScheme": "ROR",
                "name": response["name"],
            }
        ]
    elif key == "nameIdentifiers":
        orcid = value.split("orcid.org/")[1].split("]")[0]
        return [
            {
                "nameIdentifier": orcid,
                "nameIdentifierScheme": "ORCID",
                "schemeUri": f"https://orcid.org/{value}",
            }
        ]
    return value


def parse_readme_to_json(readme_path):
    try:
        with open(readme_path, "r") as file:
            lines = file.read().split("\n")
    except IOError as e:
        raise ReadmeFormatException(f"Failed to open or read the file: {e}")

    json_data = {}
    current_section = None
    current_object = {}

    title_line = lines.pop(0)
    if title_line.startswith("#") == False:
        raise ValueError('README.md needs to start with "# Title"')
    else:
        json_data["titles"] = [{"title": title_line.replace("# ", "")}]

    contributors = []
    identifiers = []
    item_list = []

    section_pattern = re.compile(r"^##\s+(.*)$")
    key_value_pattern = re.compile(r"^-\s+(.*?):\s+(.*)$")
    link_pattern = re.compile(r"\[.*?\]\((.*?)\)")

    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            if item_list and current_section:
                json_data[current_section] = item_list
                item_list = []
            elif current_object and current_section:
                if current_section == "types":
                    json_data[current_section] = current_object
                elif len(current_object) == 1:
                    key, value = next(iter(current_object.items()))
                    if key in ["language", "publicationYear", "publisher", "version"]:
                        json_data[current_section] = value
                    else:
                        json_data[current_section].append(current_object)
                elif current_section in ["creators", "contributors"]:
                    contributors.append(current_object)
                    current_object = {}
                elif current_section == "identifiers":
                    identifiers.append(current_object)
                    current_object = {}
                else:
                    json_data[current_section].append(current_object)
                current_object = {}
            continue

        section_match = section_pattern.match(line)
        if section_match:
            if item_list:
                json_data[current_section] = item_list
            elif current_object:
                if current_section in json_data:
                    if isinstance(json_data[current_section], list):
                        json_data[current_section].append(current_object)
                    elif isinstance(json_data[current_section], dict):
                        json_data[current_section].update(current_object)
                else:
                    json_data[current_section] = (
                        [current_object]
                        if current_section != "types"
                        else current_object
                    )
                current_object = {}

            elif contributors and current_section in ["creators", "contributors"]:
                json_data[current_section] = contributors
                contributors = []
            elif identifiers and current_section == "identifiers":
                json_data[current_section] = identifiers
                identifiers = []

            elif current_section and current_object:
                if current_section == "types":
                    json_data[current_section] = current_object
                elif len(current_object) == 1:
                    key, value = next(iter(current_object.items()))
                    if key in ["language", "publicationYear", "publisher", "version"]:
                        json_data[current_section].append(value)
                    else:
                        json_data[current_section].append(current_object)
                else:
                    json_data[current_section].append(current_object)
                current_object = {}
            current_section = camel_case(section_match.group(1))
            json_data[current_section] = [] if current_section != "types" else {}
            continue

        key_value_match = key_value_pattern.match(line)
        if key_value_match and current_section:
            key, value = key_value_match.groups()
            key = camel_case(key)

            if key in ["affiliation", "nameIdentifiers"]:
                value = expand_special_keys(key, value)
            elif (
                key == "nameType"
                and current_object
                and current_section in ["creators", "contributors"]
            ):
                contributors.append(current_object)
                current_object = {}
            elif current_section in ["subjects"]:
                item_list.append({key: value})
            elif current_section == "dates":
                if key == "date":
                    current_object["date"] = value
                elif key == "dateType":
                    current_object["dateType"] = value
                    item_list.append(current_object)
                    current_object = {}
            else:
                link_match = link_pattern.search(value)
                if link_match:
                    value = link_match.group(1)

            current_object[key] = value

        elif line.strip() and not section_match:
            raise ReadmeFormatException(
                f"Incorrect format detected at line {line_number}: {line}"
            )

    if contributors and current_section in ["creators", "contributors"]:
        json_data[current_section] = contributors
    elif identifiers and current_section == "identifiers":
        json_data[current_section] = identifiers
    elif current_section and current_object:
        if current_section == "types":
            json_data[current_section] = current_object
        elif len(current_object) == 1:
            key, value = next(iter(current_object.items()))
            if key in ["language", "publicationYear", "publisher", "version"]:
                json_data[current_section].append(value)
            else:
                json_data[current_section].append(current_object)
        else:
            json_data[current_section].append(current_object)

    return json_data


if __name__ == "__main__":
    readme_path = "/Users/elizabethwon/downloads/exampleREADME.md"
    try:
        json_data = parse_readme_to_json(readme_path)
        output_json_path = "output1.json"
        with open(output_json_path, "w") as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f"Converted JSON saved to {output_json_path}")
    except ReadmeFormatException as e:
        print(f"Error parsing README file: {e}")
