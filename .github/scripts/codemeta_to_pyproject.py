"""Sync package metadata from codemeta.json into pyproject.toml.

Run by the CodeMeta2CFF workflow whenever codemeta.json changes. tomlkit is used
rather than a plain rewrite so that comments, key order, and formatting in
pyproject.toml survive the update.
"""

import json

import tomlkit

CODEMETA = "codemeta.json"
PYPROJECT = "pyproject.toml"


def people(entries):
    """Convert codemeta Person entries into PEP 621 name/email tables."""
    if isinstance(entries, dict):
        entries = [entries]
    array = tomlkit.array().multiline(True)
    for person in entries or []:
        names = (person.get("givenName"), person.get("familyName"))
        name = " ".join(part for part in names if part)
        if not name:
            continue
        entry = tomlkit.inline_table()
        entry["name"] = name
        if person.get("email"):
            entry["email"] = person["email"]
        array.append(entry)
    return array


def main():
    with open(CODEMETA) as handle:
        codemeta = json.load(handle)

    with open(PYPROJECT) as handle:
        document = tomlkit.parse(handle.read())

    project = document["project"]

    for key in ("name", "version", "description"):
        if codemeta.get(key):
            project[key] = codemeta[key]

    for key, source in (("authors", "author"), ("maintainers", "maintainer")):
        values = people(codemeta.get(source))
        if len(values):
            project[key] = values

    urls = project.get("urls")
    if urls is not None:
        repository = codemeta.get("codeRepository") or codemeta.get("url")
        if repository:
            urls["Homepage"] = repository
            urls["Repository"] = repository
        if codemeta.get("issueTracker"):
            urls["Issues"] = codemeta["issueTracker"]

    with open(PYPROJECT, "w") as handle:
        handle.write(tomlkit.dumps(document))


if __name__ == "__main__":
    main()
