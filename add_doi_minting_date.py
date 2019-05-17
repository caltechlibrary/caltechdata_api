import os,requests
from progressbar import progressbar
from caltechdata_api import get_metadata, caltechdata_edit

def get_datacite_dates(prefix):
    '''Get sumbitted date for DataCite DOIs with specific prefix'''
    doi_dates = {}
    doi_urls = {}
    url = 'https://api.datacite.org/dois?query=prefix:'+prefix+'&page[cursor]=1&page[size]=500'
    next_link = url
    meta = requests.get(next_link).json()['meta']
    for j in progressbar(range(meta['totalPages'])):
        r = requests.get(next_link)
        data = r.json()
        for doi in data['data']:
            date = doi['attributes']['registered'].split('T')[0]
            doi_dates[doi['id']] = date
            doi_urls[doi['id']] =  doi['attributes']['url']
        if 'next' in data['links']:
            next_link = data['links']['next']
        else:
            next_link = None
    return doi_dates,doi_urls

token = os.environ['TINDTOK']

doi_dates,doi_urls = get_datacite_dates('10.14291')
for doi in doi_urls:
    if 'data.caltech.edu' in doi_urls[doi]:
        caltech_id = doi_urls[doi].split('/')[-1]
        if caltech_id not in ['252','253','254','255']:
            metadata = get_metadata(caltech_id,emails=True)
            print(caltech_id)
            #print(metadata['dates'])
            for date in metadata['dates']:
                if date['dateType'] == 'Issued':
                    print(date['date'],doi_dates[doi])
                    date['date'] = doi_dates[doi]
            response = caltechdata_edit(token, caltech_id,metadata,production=True)
            print(response)

