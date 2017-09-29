from requests import session
import json
from caltechdata_write import customize_schema
from caltechdata_write import send_s3

def Caltechdata_edit(token,ids,metadata={},files={}):

    #Currently only replaces files
    #There are more file operations that could be implemented

    #If files is a string - change to single value array
    if isinstance(ids, int):
        ids = [str(ids)]
    if isinstance(ids, str):
        ids = [ids]

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
            if "files" in file_info:
                fids = []
                for f in file_info["files"]:
                    if 'id' in f:
                        fids.append(f["id"])
                fjson = {'delete': fids}
                metadata['files'] = fjson
                met = {'files': fjson}

            # upload new
            fileinfo = [send_s3(f, token) for f in files]

            fjson['new'] = fileinfo
            metadata['files'] = fjson

        dat = json.dumps({'record': metadata})

        outf = open('out.json','w')
        outf.write(dat)

        print(dat)
        c = session()
        response = c.post(url, headers=headers, data=dat)
        print(response.text)
