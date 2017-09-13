from requests import session
import json
from caltechdata_write import customize_schema
from caltechdata_write import send_s3

def Caltechdata_edit(token,ids,metadata={},files={}):

    #Currently only replaces files
    #There are more file operations that could be implemented

    url = "https://cd-sandbox.tind.io/submit/api/edit/"
    api_url = "https://cd-sandbox.tind.io/api/record/"

    headers = { 'Authorization' : 'Bearer %s' % token }

    if metadata != {}:
        metadata = customize_schema.customize_schema(metadata)

    for idv in ids:

        if files != {}:
            fids = []
            c = session()
            existing = c.get(api_url+idv)
            file_info = existing.json()["metadata"]
            if "files" in file_info:
                file_info = file_info["files"]
                for f in file_info:
                    fids.append(f["id"])
                metadata['files']={'delete':fids}


        metadata['id']=idv

        dat = { 'record': json.dumps(metadata) }

        c = session()
        response = c.post(url,headers=headers,data=dat)
        print(response.text)

        if files != {}:
            #upload new
            fileinfo = []
            for f in files:
                fileinfo.append(send_s3(f,token))

            metadata['files'] = {'new':fileinfo}
            dat = { 'record': json.dumps(metadata) }

            c = session()
            response = c.post(url,headers=headers,data=dat)


