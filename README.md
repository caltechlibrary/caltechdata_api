# CaltechDATA API Python Library

[![DOI](https://img.shields.io/badge/dynamic/json.svg?label=DOI&query=$.pids.doi.identifier&uri=https://data.caltech.edu/api/records/wfjr5-kw507/versions/latest)](https://data.caltech.edu/records/wfjr5-kw507/latest)

The `caltechdata_api` Python library provides a convenient interface for interacting with the CaltechDATA API. It allows users to write files, create DataCite 4 standard JSON records, edit existing records, and retrieve metadata from the CaltechDATA repository.

## Features

### Writing and Editing Records
- `caltechdata_write`: Writes files and a DataCite 4 standard JSON record to the CaltechDATA repository.
- `caltechdata_edit`: Edits existing records in CaltechDATA.

### Metadata Operations
- `get_metadata`: Retrieves metadata from CaltechDATA records.

## Requirements

- Python 3.6+

## Installation

Install the library via pip:

```shell
pip install caltechdata_api
```

## Examples

There are some example python scripts in the GitHub repository.

### Create a record:

```shell
python write.py example.json -fnames logo.gif
# Output: pbkn6-m9y63 (unique identifier)
```
> The response will be the unique identifier for the record. You can put this at
the end of a url to visit the record (e.g.
https://data.caltechlibrary.dev/records/pbkn6-m9y63)

### Edit a record 
Make changes to the example.json file to see a change)
```
python edit.py example.json -id pbkn6-m9y63
10.33569/pbkn6-m9y63
```
> The response is the DOI for the record, which includes the unique identifier
for the record in the default configuration.

## Using Custom DOIs 
Some groups have worked with the library to create custom DOIs. These can be
passed in the metadata like:

```shell
python write.py example_custom.json -fnames logo.gif
m6zxz-p4j22
```

And then you can edit with
```
python edit.py example_custom.json -id m6zxz-p4j22
10.5281/inveniordm.1234
```

This returns the custom DOI of the record if it is successful.


## Setup and Authentication

1. Acquire a personal access token from your CaltechDATA account (found under "Applications" at the top right of your screen).
2. Copy the token to a file named token.bash.
3. Load the token in the command line using source token.bash.

## Note on Testing

Only test your application on the test repository (`data.caltechlibrary.dev`).  Testing the API on the public 
repository will generate junk records that are annoying to delete.

## Using the Command Line Interface

If you would like to interact with the CaltechDATA API using the Command line Interface (CLI), please [see the detailed documentation](https://caltechlibrary.github.io/caltechdata_api/caltechdata_api/cli-documentation-for-users).
