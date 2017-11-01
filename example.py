import argparse
import os,json
from caltechdata_write import Caltechdata_write

parser = argparse.ArgumentParser(description=\
        "Write files and a DataCite 4 standard json record\
        to CaltechDATA repository")
parser.add_argument('json_file',nargs=1, help=\
            'file name for json DataCite metadata file')
parser.add_argument('-fnames',nargs='*', help='files to attach')
args = parser.parse_args()

#Get access token from TIND sed as environment variable with source token.bash
token = os.environ['TINDTOK']

metaf = open(args.json_file[0],'r')
metadata = json.load(metaf)

files = args.fnames
if files == None:
    files={}

response = Caltechdata_write(metadata,token,files,False)
print(response)
