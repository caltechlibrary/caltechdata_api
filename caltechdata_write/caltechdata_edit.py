from requests import session
import json
from caltechdata_write import customize_schema

def Caltechdata_edit(metadata,token,ids):

    #If files is a int - change to single value array
    if isinstance(ids, int) == True:
        files = [ids]

    #fileinfo=[]
    #
    #for f in files:
    #    fileinfo.append(send_s3(f,token))

    url = "https://cd-sandbox.tind.io/submit/api/edit/"

    headers = { 'Authorization' : 'Bearer %s' % token }

    newdata = customize_schema.customize_schema(metadata)
    for idv in ids:
        newdata['id']=idv

        dat = { 'record': json.dumps(newdata) }

        c = session()
        response = c.post(url,headers=headers,data=dat)
        print(response.text)

