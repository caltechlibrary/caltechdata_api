from requests import session
import json
from caltechdata_api import customize_schema
from caltechdata_api import send_s3

def caltechdata_edit(token,ids,metadata={},files={},delete={},production=False):

    #Including files will only replaces files if they have the same name
    #The delete option will delete any existing files with a given file
    #extension
    #There are more file operations that could be implemented

    #If files is a string - change to single value array
    if isinstance(files, str) == True:
        files = [files]
    if isinstance(ids, int):
        ids = [str(ids)]
    if isinstance(ids, str):
        ids = [ids]

    if production == True:
        url = "https://data.caltech.edu/submit/api/edit/"
        api_url = "https://data.caltech.edu/api/record/"
    else:
        url = "https://cd-sandbox.tind.io/submit/api/edit/"
        api_url = "https://cd-sandbox.tind.io/api/record/"

    headers = {
        'Authorization' : 'Bearer %s' % token,
        'Content-type': 'application/json'
    }

    if metadata:
        metadata = customize_schema.customize_schema(metadata)

    for idv in ids:
        metadata['id'] = idv

        if files:
            # Files to delete
            fjson = {}
            c = session()
            existing = c.get(api_url + idv)
            file_info = existing.json()["metadata"]
            fids = []
            for f in files: #Check if new files match existing
                if 'electronic_location_and_access' in file_info:
                    for ex in file_info["electronic_location_and_access"]:
                        name = ex['electronic_name'][0]
                        fu = ex['uniform_resource_identifier'].split('/')[-2]
                        if name == f:
                            fids.append(fu)
                        for d in delete:
                            if name == d:
                                fids.append(fu)
                            if name.split('.')[-1] == d:
                                fids.append(fu)
            if len(fids) > 0:
                fjson = {'delete': fids}

            # upload new
            print(files)
            fileinfo = [send_s3(f, token, production) for f in files]

            fjson['new'] = fileinfo
            metadata['files'] = fjson

        dat = json.dumps({'record': metadata})

        #outf = open('out.json','w')
        #outf.write(dat)

        c = session()
        response = c.post(url, headers=headers, data=dat)
        return response.text

def caltechdata_add(token,ids,metadata={},files={},production=False):

    #Adds file

    #If files is a string - change to single value array
    if isinstance(ids, int):
        ids = [str(ids)]
    if isinstance(ids, str):
        ids = [ids]

    if production == True:
        url = "https://data.caltech.edu/submit/api/edit/"
        api_url = "https://data.caltech.edu/api/record/"    
    else:
        url = "https://cd-sandbox.tind.io/submit/api/edit/"
        api_url = "https://cd-sandbox.tind.io/api/record/"

    headers = {
        'Authorization' : 'Bearer %s' % token,
        'Content-type': 'application/json'
    }

    if metadata:
        metadata = customize_schema.customize_schema(metadata)

    fjson = {}

    for idv in ids:
        metadata['id'] = idv

        if files:
            # upload new
            fileinfo = [send_s3(f, token, production) for f in files]

            fjson['new'] = fileinfo
            metadata['files'] = fjson

        dat = json.dumps({'record': metadata})

        #outf = open('out.json','w')
        #outf.write(dat)

        c = session()
        response = c.post(url, headers=headers, data=dat)
        return response.text

