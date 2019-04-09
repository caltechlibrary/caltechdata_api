import os,subprocess,json,csv
import dataset
from ames.harvesters import get_caltechfeed

if os.path.isdir('data') == False:
    os.mkdir('data')
os.chdir('data')

get_caltechfeed('thesis')

record_list = {}
collection = 'CaltechTHESIS.ds'
keys = dataset.keys(collection)
count = 0
for k in keys:
    count = count + 1
    if count % 100 == 0:
        print(count)
    metadata,err = dataset.read(collection,k)
    if err != '':
        print("Error on read ",err)
        exit()
    if metadata != {}:
        if 'official_url' in metadata:
            record_list[k]=metadata['official_url']
        else:
            print("Missing URL",metadata)
    else:
        print("Bad Record: "+k)
        print(metadata)
with open('record_list.csv','w') as f:
    w = csv.writer(f)
    w.writerows(record_list.items())
