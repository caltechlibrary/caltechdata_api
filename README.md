# caltechdata_read

Write files and a DataCite 4 standard json record to CaltechDATA repository

In development-Only usable by staff. Requires python requests library. 

Final Actions (New DOI Generation) not yet implemented

## Usage

You need to acquire a personal access token from your CaltechDATA account
(find it at the top right of your screen under "Applications").
Make sure you include the "deposit_api:write" and "file_manager:upload"
scopes.  Then copy the token to token.bash.  Type source token.bash in 
the command line to load the token.  You can now use caltechdata_write
to access the repository!

```shell
   usage: python caltechdata_write.py [-h] [-fnames FNAMES [FNAMES ...]] json_file
```

positional arguments:
  json_file                     file name for json DataCite metadata file

optional arguments:
  -h, --help                    show this help message and exit
  -fnames FNAMES [FNAMES ...]   files to attach

## Example

Only test your application on the test repository with permission of CaltechDATA 
repository staff (email data@caltech.edu).  Testing the API on the public 
repository will generate junk records that are annoying to delete.

python caltechdata_write.py example.json -fnames logo.gif

