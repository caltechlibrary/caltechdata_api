import os, json, csv, argparse
import requests
from caltechdata_api import decustomize_schema

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="get_metadata queries the caltechDATA (Invenio 3) API\
    and returns DataCite-compatable metadata"
    )
    parser.add_argument(
        "output",
        help="Output file name",
    )
    parser.add_argument("-keywords", nargs="*")

    args = parser.parse_args()

    url = 'https://data.caltech.edu/api/records/?size=5000'

    search = ''
    if args.keywords:
        for key in args.keywords:
            if search == '':
                search = f'&q=subjects:"{key}"'
            else:
                search = search+f'+"{key}"'
        url = url + search

    response = requests.get(url)
    hits = response.json()

    outfile = open(args.output,'w')
    writer = csv.writer(outfile)
    writer.writerow(['lat','lon','name'])

    for h in hits['hits']['hits']:
        metadata = decustomize_schema(h['metadata'])
        if 'geoLocations' in metadata:
            geo = metadata['geoLocations']
            for g in geo:
                #if 'geoLocationBox' in g:
                #    box = g['geoLocationBox']
                #    lat=[box['northBoundLatitude'],box['northBoundLatitude'],box['southBoundLatitude'],box['southBoundLatitude']]
                #    lon=[box['eastBoundLongitude'],box['westBoundLongitude'],box['eastBoundLongitude'],box['westBoundLongitude']]
                #    tlon,tlat = transform(from_proj,to_proj,lon,lat)
                #    pt_lat=pt_lat+tlat
                #    pt_lon= pt_lon+tlon
                #    cen = metadata['publicationYear'][1]
                #    dec = metadata['publicationYear'][2]
                #    identifier.append(metadata['identifier']['identifier'])
                #    author.append(metadata['creators'][0]['creatorName'])
                #    title.append(metadata['titles'][0]['title'].split(':')[0])
                #    year.append(metadata['publicationYear'])
                #    color.append(clo)
                #    x0 = x0 + [tlon[0],tlon[2],tlon[0],tlon[1]]
                #    x1 = x1 + [tlon[1],tlon[3],tlon[2],tlon[3]]
                #    y0 = y0 + [tlat[0],tlat[2],tlat[0],tlat[1]]
                #    y1 = y1 + [tlat[1],tlat[3],tlat[2],tlat[3]]
                if 'geoLocationPoint' in g:
                    point = g['geoLocationPoint']
                    #tlon,tlat =\
                            #transform(from_proj,to_proj,point['pointLongitude'],point['pointLatitude'])
                    #pt_lat=pt_lat+[tlat]
                    #pt_lon= pt_lon+[tlon]
                    #identifier=identifier+[metadata['identifier']['identifier']]
                    #author=author+[metadata['creators'][0]['creatorName']]
                    title=metadata['titles'][0]['title'].split(':')[0]
                    lat = point['pointLatitude']
                    lon = point['pointLongitude']
                    writer.writerow([lat,lon,title])
                    #year = year+[metadata['publicationYear']]
                    #cen = metadata['publicationYear'][1]
                    #dec = metadata['publicationYear'][2]

