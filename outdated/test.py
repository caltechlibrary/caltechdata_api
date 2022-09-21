from datacite import schema43
import io, json
from os.path import dirname, join


def load_json_path(path):
    """Helper method for loading a JSON example file from a path."""
    path_base = dirname(__file__)
    with io.open(join(path_base, path), encoding="utf-8") as file:
        content = file.read()
    return json.loads(content)


metadata = load_json_path("example43.json")

valid = schema43.validate(metadata)
if valid == False:
    v = schema43.validator.validate(metadata)
    errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
    for error in errors:
        print(error.message)
