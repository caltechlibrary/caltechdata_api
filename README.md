# caltechdata_api

[![DOI](https://data.caltech.edu/badge/87960443.svg)](https://data.caltech.edu/badge/latestdoi/87960443)

Python library for using the CaltechDATA API

- caltechdata_write write files and a DataCite 4 standard json record to CaltechDATA repository
- caltechdata_edit edits records in CaltechDATA
- get_metadata gets metadata from CaltechDATA records

Requires Python 3 (Recommended via Anaconda https://www.anaconda.com/download) with reqests library.

## Examples

There are some example python scripts in the GitHub repository.

Create a record:

```shell
python example.py example.json -fnames logo.gif
Successfully created record https://cd-sandbox.tind.io/records/352.  
```

Edit a record (make changes to the example.json file to see a change)
```
python edit.py example.json -ids 352 -fnames logo.gif
Successfully modified record https://cd-sandbox.tind.io/records/352
```

## Setup 

Install by typing 'pip install caltechdata_api'

## Usage

Write API access is controlled by repository staff.  Email us at data@caltech.edu 
with your request if you want to use the write API.

You need to acquire a personal access token from your CaltechDATA account
(find it at the top right of your screen under "Applications").
Make sure you include the "deposit_api:write" and "file_manager:upload"
scopes.  Then copy the token to token.bash.  Type source token.bash in 
the command line to load the token.  

Only test your application on the test repository.  Testing the API on the public 
repository will generate junk records that are annoying to delete.

## TODO

Handle incorrect token on file upload
