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
    writer.writerow(['wkt','name','year','doi'])

    for h in hits['hits']['hits']:
        metadata = decustomize_schema(h['metadata'])
        if 'geoLocations' in metadata:
            doi = 'https://doi.org/'+metadata['identifier']['identifier']
            title=metadata['titles'][0]['title'].split(':')[0]
            geo = metadata['geoLocations']
            year = metadata['publicationYear']
            for g in geo:
                if 'geoLocationBox' in g:
                    box = g['geoLocationBox']
                    p1 = f"{box['eastBoundLongitude']} {box['northBoundLatitude']}"
                    p2 = f"{box['westBoundLongitude']} {box['northBoundLatitude']}"
                    p3 = f"{box['westBoundLongitude']} {box['southBoundLatitude']}"
                    p4 = f"{box['eastBoundLongitude']} {box['southBoundLatitude']}"
                    wkt = f'POLYGON (({p1}, {p2}, {p3}, {p4}, {p1}))'
                    writer.writerow([wkt,title,year,doi])
                    
                if 'geoLocationPoint' in g:
                    point = g['geoLocationPoint']
                    wkt = f"POINT ({point['pointLongitude']} {point['pointLatitude']})"
                    writer.writerow([wkt,title,year,doi])

