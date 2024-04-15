import re
import json

class ReadmeFormatException(Exception):
    """Custom exception for errors in the README format."""

def camel_case(s):
    """Converts a string to camelCase."""
    s = re.sub(r"(\s|_|-)+", " ", s).title().replace(" ", "")
    return s[0].lower() + s[1:] if s else ""

def expand_special_keys(key, value):
    """Expand special keys into their structured format (affiliation, nameIdentifiers)."""
    if key == "affiliation":
        return [
            {
                "affiliationIdentifier": value,
                "affiliationIdentifierScheme": "ROR"
            }
        ]
    elif key == "nameIdentifiers":
        return [
            {
                "nameIdentifier": value,
                "nameIdentifierScheme": "ORCID",
                "schemeUri": f"https://orcid.org/{value}"
            }
        ]
    return value

def parse_readme_to_json(readme_path):
    try:
        with open(readme_path, 'r') as file:
            lines = file.read().split('\n')
    except IOError as e:
        raise ReadmeFormatException(f"Failed to open or read the file: {e}")

    json_data = {}
    current_section = None
    current_object = {}

    section_pattern = re.compile(r'^##\s+(.*)$')
    key_value_pattern = re.compile(r'^-\s+(.*?):\s+(.*)$')
    link_pattern = re.compile(r'\[.*?\]\((.*?)\)')

    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            if current_object and current_section:
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
            continue

        section_match = section_pattern.match(line)
        if section_match:
            if current_section and current_object:
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
                print(value)
            else:
                link_match = link_pattern.search(value)
                if link_match:
                    value = link_match.group(1)

            current_object[key] = value

        elif line.strip() and not section_match:
            raise ReadmeFormatException(f"Incorrect format detected at line {line_number}: {line}")

    if current_section and current_object:
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

readme_path = '/Users/elizabethwon/downloads/exampleREADME.md'
try:
    json_data = parse_readme_to_json(readme_path)
    output_json_path = 'output1.json'
    with open(output_json_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"Converted JSON saved to {output_json_path}")
except ReadmeFormatException as e:
    print(f"Error parsing README file: {e}")
