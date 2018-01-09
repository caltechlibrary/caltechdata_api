# Convert a internal TIND CaltechDATA record into a  DataCite 4 standard schema json record
import json
import argparse

def decustomize_schema(json_record):

    #Extract subjects to single string
    if "subjects" in json_record:
        if isinstance(json_record['subjects'],str):
            subjects = json_record['subjects'].split(',')
            array = []
            for s in subjects:
                array.append({'subject':s})
            json_record['subjects']=array
        else:
            array = []
            for s in json_record['subjects']:
                array.append({"subject":s})
            json_record['subjects']=array

    #Extract identifier and label as DOI
    if "doi" in json_record:
        json_record['identifier'] = {'identifier':json_record['doi'],
                'identifierType':"DOI"}
        del json_record['doi']

    #Extract title
    if "title" in json_record:
        json_record['titles'] = [{"title":json_record['title']}]
        del json_record['title']

    #Change related identifier labels
    if "relatedIdentifiers" in json_record:
        for listing in json_record['relatedIdentifiers']:
            listing['relationType'] = listing.pop('relatedIdentifierRelation') 
            listing['relatedIdentifierType'] = listing.pop('relatedIdentifierScheme')
    
    #Publication is effectivly a related identifier
    if "publications" in json_record:
        if 'publicationIDs' in json_record['publications']:
            relation = {"relatedIdentifier":
                json_record['publications']['publicationsIDs']['publicationIDNumber'],
                "relatedIdentifierType": "DOI",
                "relatedIdentifierRelation": "IsSupplementTo"}
            if 'relatedIdentifiers' in json_record:
                json_record['relatedIdentifiers'].append(relation)
            else:
                json_record['relatedIdentifiers'] = [relation]
        del json_record['publications']

    #change author formatting
    #Could do better with multiple affiliations
    if "authors" in json_record:
        authors = json_record['authors']
        newa = []
        for a in authors:
            new = {}
            if 'authorAffiliation' in a:
                if isinstance(a['authorAffiliation'],list):
                    new['affiliations'] = a['authorAffiliation']
                else:
                    new['affiliations'] = [a['authorAffiliation']]
            if 'authorIdentifiers' in a:
                idv = []
                for cid in a['authorIdentifiers']:
                    nid = {}
                    nid['nameIdentifier'] =\
                        cid.pop('authorIdentifier')
                    nid['nameIdentifierScheme'] =\
                        cid.pop('authorIdentifierScheme')
                    idv.append(nid)
                new['nameIdentifiers']=idv
                del a['authorIdentifiers']
            new['creatorName'] = a['authorName']
            newa.append(new)
        json_record['creators']=newa
        del json_record['authors']

    #contributors
    if "contributors" in json_record:
        for c in json_record['contributors']:
            if 'contributorAffiliation' in c:
                if isinstance(c['contributorAffiliation'],list):
                    c['affiliations'] = c.pop('contributorAffiliation')
                else:
                    c['affiliations'] = [c.pop('contributorAffiliation')]
            if 'contributorIdentifiers' in c:
                #if isinstance(c['contributorIdentifiers'],list):
                newa = []
                for cid in c['contributorIdentifiers']:
                    new = {}
                    new['nameIdentifier'] =\
                                cid.pop('contributorIdentifier')
                    new['nameIdentifierScheme'] =\
                                cid.pop('contributorIdentifierScheme')
                    newa.append(new)
                c['nameIdentifiers']=newa
                del c['contributorIdentifiers']
                #else:
                #    c['contributorIdentifiers']['nameIdentifier'] =\
                        #    c['contributorIdentifiers'].pop('contributorIdentifier')
                #    c['contributorIdentifiers']['nameIdentifierScheme'] =\
                        #    c['contributorIdentifiers'].pop('contributorIdentifierScheme')
                #    c['nameIdentifiers'] = [c.pop('contributorIdentifiers')]
            if 'contributorEmail' in c:
                del c['contributorEmail']
    #format
    if "format" in json_record:
        if isinstance(json_record['format'],list):
            json_record['formats']=json_record.pop('format')
        else:
            json_record['formats']=[json_record.pop('format')]

    #dates
    datetypes = set()
    #Save set of types for handling publicationDate
    if "relevantDates" in json_record:
        dates = json_record['relevantDates']
        for d in dates:
            d['date']=d.pop('relevantDateValue')
            d['dateType']=d.pop('relevantDateType')
            datetypes.add(d['dateType'])
        json_record['dates']=json_record.pop('relevantDates')

    #set publicationYear
    year = json_record['publicationDate'].split('-')[0]
    json_record['publicationYear'] = year
    #If "Submitted' date type was not manually set in metadata
    #Or 'Issued was not manually set
    #We want to save the entire publicationDate
    if 'Submitted' in datetypes or 'Issued' in datetypes:
        print("Custom Dates Present-Dropping TIND Publication Date")
    else:
        if 'dates' in json_record:
            json_record['dates'].append({"date":json_record['publicationDate'],\
                "dateType": "Submitted"})
        else:
            json_record['dates']=[{"date":json_record['publicationDate'],\
                "dateType": "Submitted"}]
    del json_record['publicationDate']

    #license - no url available
    if 'rightsList' not in json_record:
        if 'license' in json_record:
            json_record['rightsList']=[{"rights":json_record.pop('license')}]
    
    #Funding
    if 'fundings' in json_record:
        #Metadata changes and all should all be DataCite standard
        #Clean out any residual issues
        print("Check funding information")
        del json_record['fundings']

    #Geo
    if 'geographicCoverage' in json_record:
        geo = json_record['geographicCoverage']
        if isinstance(geo,list):
            #We have the correct formatting
            for g in geo:
                if 'geoLocationPoint' in g:
                    pt = g['geoLocationPoint']
                    if isinstance(pt,list):
                        newp = {}
                        newp['pointLatitude'] = float(pt[0]['pointLatitude'])
                        newp['pointLongitude'] = float(pt[0]['pointLongitude'])
                        g['geoLocationPoint'] = newp
                    else:
                        pt['pointLatitude'] = float(pt['pointLatitude'])
                        pt['pointLongitude'] = float(pt['pointLongitude'])
                if 'geoLocationBox' in g:
                    bx = g['geoLocationBox']
                    newp = {}
                    newp['southBoundLatitude'] = float(bx['southBoundLatitude'])
                    newp['northBoundLatitude'] = float(bx['northBoundLatitude'])
                    newp['eastBoundLongitude'] = float(bx['eastBoundLongitude'])
                    newp['westBoundLongitude'] = float(bx['westBoundLongitude'])
                    g['geoLocationBox'] = newp
            json_record['geoLocations']=json_record.pop('geographicCoverage')
        else:
            newgeo = {}
            if 'geoLocationPlace' in geo:
                newgeo['geoLocationPlace'] = geo['geoLocationPlace'] 
            if 'geoLocationPoint' in geo:
                pt = geo['geoLocationPoint'][0]
                newpt = {}
                newpt['pointLatitude'] = float(pt['pointLatitude'])
                newpt['pointLongitude'] = float(pt['pointLongitude'])
                newgeo['geoLocationPoint'] = newpt
            json_record['geoLocations'] = [newgeo]
            del json_record['geographicCoverage']

    #Publisher
    if "publishers" in json_record:
        if isinstance(json_record['publishers'],list):
            json_record['publisher'] = json_record['publishers'][0]['publisherName']
        else:
            json_record['publisher'] = json_record['publishers']['publisherName']
        del json_record['publishers']

    #description
    if "descriptions" in json_record:
        for d in json_record["descriptions"]:
            if 'descriptionValue' in d:
                d["description"] = d.pop("descriptionValue")

    others = ['files', 'id', 'owners', 'pid_value', 'control_number', '_oai',
            '_form_uuid', 'electronic_location_and_access', 'access_right',
            'embargo_date','license']
    for v in others:
        if v in json_record:
            del json_record[v]

    #print(json.dumps(json_record))
    return json_record

if __name__ == "__main__":
    #Read in from file for demo purposes

    parser = argparse.ArgumentParser(description=\
                "decustomize_schema converts a internal TIND CaltechDATA record\
       into a  DataCite 4 standard schema json record")
    parser.add_argument('json_files', nargs='+', help='json file name')
    args = parser.parse_args()

    for jfile in args.json_files:
        infile = open(jfile,'r')
        data = json.load(infile)
        new = customize_schema(data)
        with open('formatted.json','w') as outfile:
            json.dump(new,outfile)
        #print(json.dumps(new))
