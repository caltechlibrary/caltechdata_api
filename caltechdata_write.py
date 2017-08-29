from requests import session
from customize_schema import customize_schema
import json
import argparse
import os

def send_s3(filename,token):
    s3surl = "https://cd-sandbox.tind.io/tindfiles/sign_s3/"
    chkurl = "https://cd-sandbox.tind.io/tindfiles/md5_s3"

    headers = { 'Authorization' : 'Bearer %s' % token }

    c = session()

    response = c.get(s3surl,headers=headers)
    jresp = response.json()
    data = jresp['data']

    fname = 'logo.gif' #Hard coding  
    bucket = jresp['bucket']
    key = data['fields']['key']
    policy = data['fields']['policy']
    aid = data['fields']['AWSAccessKeyId']
    signature = data['fields']['signature']
    url = data['url']

    infile = open(filename,'rb')
    size = infile.seek(0,2)
    infile.seek(0,0) #reset at beginning

    s3headers = { 'Host' : bucket+'.s3.amazonaws.com',\
            'Date' : 'date',\
            'x-amz-acl' : 'public-read',\
            'Access-Control-Allow-Origin' : '*' }

    form = ( ( 'key', key )
            , ("acl", "public-read")
            , ('AWSAccessKeyID', aid)
            , ('policy', policy)
            , ('signature', signature)
            , ('file', infile ))

    c = session()
    response = c.post(url,files=form, headers=s3headers)
    if(response.text):
        raise Exception(response.text)

    #print(chkurl+'/'+bucket+'/'+key)
    response = c.get(chkurl+'/'+bucket+'/'+key,headers=headers)
    md5 = response.json()["md5"]
    #print(size)

    fileinfo = { "url" : key,\
            "filename" : filename,\
            "md5" : md5,"size" : size }

    return(fileinfo)

def write_record(metadata,token,files=[]):

    fileinfo=[]

    for f in files:
        fileinfo.append(send_s3(f,token))

    url = "https://cd-sandbox.tind.io/submit/api/create/"

    headers = { 'Authorization' : 'Bearer %s' % token }

    metaf = open(metadata,'r')
    data = json.load(metaf)
    
    newdata = customize_schema(data)
    newdata['files']=fileinfo

    dat = { 'record': json.dumps(newdata) }

    c = session()
    response = c.post(url,headers=headers,data=dat)
    print(response.text)

if  __name__ == "__main__":

    parser = argparse.ArgumentParser(description=\
        "Write files and a DataCite 4 standard json record\
        to CaltechDATA repository")
    parser.add_argument('json_file',nargs=1, help=\
            'file name for json DataCite metadata file')
    parser.add_argument('-fnames',nargs='+', help='files to attach')
    args = parser.parse_args()

    #Get access token from TIND sed as environment variable with source token.bash
    token = os.environ['TINDTOK']

    write_record(args.json_file[0],token,args.fnames)
