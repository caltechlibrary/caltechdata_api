# Convert a DataCite 4 standard schema json record to the customized internal
# schema used by TIND in CaltechDATA
import json
import argparse

def customize_schema(json_record):

    #Extract subjects to single string
    if "subjects" in json_record:
        subjects = json_record['subjects']
        subs = []
        for s in subjects:
            subs.append(s['subject'])
        json_record['subjects']=subs

    #Extract identifier and label as DOI
    if "identifier" in json_record:
        identifier = json_record['identifier']['identifier']
        #Cound check identifierType for validation
        json_record['doi'] = identifier
        del json_record['identifier']
        #will delete other ideintifiers in file

    #Extract description
    if "descriptions" in json_record:
        for d in json_record["descriptions"]:
            d['descriptionValue']=d['description']
            del d['description']

    #Extract title
    if "titles" in json_record:
        titles = json_record['titles']
        for t in titles:
            if 'titleType' not in t:
                json_record['title']=t['title']
        del json_record['titles']

    #Language - only translating english
    if "language" in json_record:
        if json_record["language"] == 'en':
            json_record["language"] = 'eng'

    #Change related identifier labels
    if "relatedIdentifiers" in json_record:
        for listing in json_record['relatedIdentifiers']:
            listing['relatedIdentifierRelation'] = listing.pop('relationType')
            listing['relatedIdentifierScheme'] = listing.pop('relatedIdentifierType')

    #change author formatting
    #We're dropping URIs
    if "creators" in json_record:
        authors = json_record['creators']
        newa = []
        for a in authors:
            new = {}
            if 'affiliations' in a:
                if isinstance(a['affiliations'], list):
                    new['authorAffiliation'] = a['affiliations']
                else:
                    new['authorAffiliation'] = [a['affiliations']]
            new['authorName'] = a['creatorName']
            if 'nameIdentifiers' in a:
                idn = []
                for n in a['nameIdentifiers']:
                    idn.append({"authorIdentifier":n["nameIdentifier"],
                        "authorIdentifierScheme": n["nameIdentifierScheme"]})
                new['authorIdentifiers'] = idn
            newa.append(new)
        json_record['authors']=newa
        del json_record['creators']

    #strip creator URI
    if "contributors" in json_record:
        newc = []
        for c in json_record['contributors']:
            new = {}
            if 'nameIdentifiers' in c:
                idn = []
                for n in c['nameIdentifiers']:
                    idn.append({"contributorIdentifier":n["nameIdentifier"],
                    "contributorIdentifierScheme":n['nameIdentifierScheme']})
                new['contributorIdentifiers'] = idn
            if 'affiliations' in c:
                if isinstance(c['affiliations'], list):
                    new['contributorAffiliation'] = c['affiliations']
                else:
                    new['contributorAffiliation'] = [c['affiliations']]
            new['contributorName'] = c['contributorName']
            if 'contributorType' in c:
                new['contributorType'] = c['contributorType']
            if 'contributorEmail' in c:
                new['contributorEmail'] = c['contributorEmail']
            newc.append(new)
        json_record['contributors'] = newc

    #format
    if "formats" in json_record:
        json_record['format']=json_record.pop('formats')

    #dates
    if "publicationYear" in json_record:
        json_record["publicationDate"]=str(json_record.pop("publicationYear"))

    if "dates" in json_record:
        dates = json_record['dates']
        priority = False
        for d in dates:
            #If metadata has Submitted date, we can get a full date in TIND
            if d['dateType']=='Submitted':
                json_record["publicationDate"]=d['date']
                priority = True
            #If we have an Issued but not a Submitted date, save full date 
            if d['dateType']=='Issued':
                if priority == False:
                    json_record["publicationDate"]=d['date']
            d['relevantDateValue']=str(d.pop('date'))
            d['relevantDateType']=d.pop('dateType')
        json_record['relevantDates']=json_record.pop('dates')


    #license
    if 'rightsList' in json_record:
        licenses = json_record['rightsList']
        #Should check acceptable licenses
        #if licenses[0]['rights'] == 'TCCON Data Use Policy':
        #    json_record['license'] = 'other-license'
        #else:
        #if licenses[0]['rights'] == 'public-domain':
        #    licenses[0]['rights'] = 'other'
        json_record['rightsList']=licenses[0]
        #Only transfers first license
    
    #Geo
    if 'geoLocations' in json_record:
        for g in json_record['geoLocations']:
            if 'geoLocationPoint' in g:
                g['geoLocationPoint']['pointLatitude'] = str(g['geoLocationPoint']['pointLatitude'])
                g['geoLocationPoint']['pointLongitude'] = str(g['geoLocationPoint']['pointLongitude'])
            if 'geoLocationBox' in g:
                g['geoLocationBox']['northBoundLatitude']=str(g['geoLocationBox']['northBoundLatitude'])
                g['geoLocationBox']['southBoundLatitude']=str(g['geoLocationBox']['southBoundLatitude'])
                g['geoLocationBox']['eastBoundLongitude']=str(g['geoLocationBox']['eastBoundLongitude'])
                g['geoLocationBox']['westBoundLongitude']=str(g['geoLocationBox']['westBoundLongitude'])
        json_record['geographicCoverage'] = json_record.pop('geoLocations')

    #Publisher
    if "publisher" in json_record:
        publisher = {}
        publisher['publisherName'] = json_record.pop('publisher')
        json_record['publishers'] = publisher

    #print(json.dumps(json_record))
    return json_record

if __name__ == "__main__":
    #Read in from file for demo purposes

    parser = argparse.ArgumentParser(description=\
                "customize_schema converts a DataCite 4 standard json record\
                to TIND customized internal schema in CaltechDATA")
    parser.add_argument('json_files', nargs='+', help='json file name')
    args = parser.parse_args()

    for jfile in args.json_files:
        infile = open(jfile,'r')
        data = json.load(infile)
        new = customize_schema(data)
        with open('formatted.json','w') as outfile:
            json.dump(new,outfile)
        #print(json.dumps(new))
