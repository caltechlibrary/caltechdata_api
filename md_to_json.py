import re
import json


def parse_readme_to_json(readme_path):
    with open(readme_path, 'r') as file:
        lines = file.read().split('\n')
    
    json_data = {}
    current_section = None
    current_object = {}

    section_pattern = re.compile(r'^##\s+(.*)$')
    key_value_pattern = re.compile(r'^-\s+(.*?):\s+(.*)$')
    link_pattern = re.compile(r'\[.*?\]\((.*?)\)')

    for line in lines:
        section_match = section_pattern.match(line)
        if section_match:
            if current_section:
                json_data[current_section].append(current_object)
            current_section = section_match.group(1).lower().replace(' ', '_')
            json_data[current_section] = []
            current_object = {}
            continue

        key_value_match = key_value_pattern.match(line)
        if key_value_match and current_section:
            key, value = key_value_match.groups()
            key = key.replace(' ', '')

            link_match = link_pattern.match(value)
            if link_match:
                value = link_match.group(1)

            current_object[key] = value

    if current_section and current_object:
        json_data[current_section].append(current_object)

    return json_data

if __name__ == '__main__':

    readme_path = '/Users/elizabethwon/downloads/exampleREADME.md'
    json_data = parse_readme_to_json(readme_path)

    output_json_path = 'output2.json'
    with open(output_json_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"Converted JSON saved to {output_json_path}")

