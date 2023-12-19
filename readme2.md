# caltechdata_api

Python library for using the CaltechDATA API

- caltechdata_write write files and a DataCite 4 standard json record to CaltechDATA repository
- caltechdata_edit edits records in CaltechDATA
- get_metadata gets metadata from CaltechDATA records

Requires Python 3 (Recommended via Anaconda https://www.anaconda.com/download) with reqests library.

## Examples

There are some example python scripts in the GitHub repository.

Create a record:

```shell
python write.py example.json -fnames logo.gif
pbkn6-m9y63
```
The response will be the unique identifier for the record. You can put this at
the end of a url to visit the record (e.g.
https://data.caltechlibrary.dev/records/pbkn6-m9y63)

Edit a record (make changes to the example.json file to see a change)
```
python edit.py example.json -id pbkn6-m9y63
10.33569/pbkn6-m9y63
```
The response is the DOI for the record, which includes the unique identifier
for the record in the default configuration.

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

## Setup 

Install by typing 'pip install caltechdata_api'

## Usage

You need to acquire a personal access token from your CaltechDATA account
(find it at the top right of your screen under "Applications").
Then copy the token to token.bash.  Type `source token.bash` in 
the command line to load the token.  

Only test your application on the test repository (data.caltechlibrary.dev).  Testing the API on the public 
repository will generate junk records that are annoying to delete.

