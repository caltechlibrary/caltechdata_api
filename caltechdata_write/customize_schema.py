# Convert a DataCite 4 standard schema json record to the customized internal
# schema used by TIND in CaltechDATA
import json
import argparse

def customize_schema(json_record):

    #Extract subjects to single string
    if "subjects" in json_record:
        subjects = json_record['subjects']
        #substr = ''
        subs = []
        for s in subjects:
            subs.append(s['subject'])
            #if substr != '':
            #    substr = substr + ', '
            #substr = substr+s['subject']
        json_record['subjects']=subs#tr
        #print(substr)
        #del json_record['subjects']

    #Extract identifier and label as DOI
    if "identifier" in json_record:
        identifier = json_record['identifier']['identifier']
        #Cound check identifierType for validation
        json_record['doi'] = identifier
        del json_record['identifier']
        #will delete other ideintifiers in file
    else: #We want tind to generate the identifier
        json_record['final_actions'] = [{"type":"create_doi",\
                "parameters":{"type":"records","field":"doi"}}]

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
    #We're only supporting ORCIDS, and losing all URIs
    if "creators" in json_record:
        authors = json_record['creators']
        newa = []
        for a in authors:
            new = {}
            if 'affiliations' in a:
                if isinstance(a['affiliations'], list):
                    new['contributorAffiliation'] = a['affiliations']
                else:
                    new['contributorAffiliation'] = [a['affiliations']]
            new['authorName'] = a['creatorName']
            if 'nameIdentifiers' in a:
                idn = []
                for n in a['nameIdentifiers']:
                    idn.append({"authorIdentifier":n["nameIdentifier"],
                        "authorIdentifierScheme": n["nameIdentifierScheme"]})
                new['authorIdentifiers'] = idn
            newa.append(new)
        json_record['authors']=newa

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
            new['contributorType'] = c['contributorType']
            if 'contributorEmail' in c:
                new['contributorEmail'] = c['contributorEmail']
            newc.append(new)
        json_record['contributors'] = newc

    #format
    if "formats" in json_record:
        json_record['format']=json_record.pop('formats')

    #dates
    if "dates" in json_record:
        dates = json_record['dates']
        for d in dates:
            d['relevantDateValue']=d.pop('date')
            d['relevantDateType']=d.pop('dateType')
        json_record['relevantDates']=json_record.pop('dates')

    if "publicationYear" in json_record:
        json_record["publicationDate"]=json_record["publicationYear"]

    #license
    if 'rightsList' in json_record:
        licenses = json_record['rightsList']
        #Should check acceptable licenses
        if licenses[0]['rights'] == 'TCCON Data Use Policy':
            json_record['license'] = 'other-license'
        else:
            json_record['license']=licenses[0]['rights']
        #Only transfers first license
    
    #Funding
    if 'fundingReferences' in json_record:
        funding = json_record['fundingReferences']
        newf = []
        for f in funding:
            frec = {}
            if 'funderName' in f:
                frec['fundingName'] = f['funderName']
            #f['fundingName']=f.pop('funderName')
            if 'awardNumber' in f:
                frec['fundingAwardNumber']=f['awardNumber']['awardNumber']
            newf.append(frec)
        json_record['fundings']=newf
        #Some fields not preserved

    #Geo
    if 'geoLocations' in json_record:
        for g in json_record['geoLocations']:
            if 'geoLocationPoint' in g:
                g['geoLocationPoint']['pointLatitude'] = str(g['geoLocationPoint']['pointLatitude'])
                g['geoLocationPoint']['pointLongitude'] = str(g['geoLocationPoint']['pointLongitude'])
                g['geoLocationPoint'] = g['geoLocationPoint']
            if 'geoLocationBox' in g:
                g['geoLocationBox']['northBoundLatitude']=str(g['geoLocationBox']['northBoundLatitude'])
                g['geoLocationBox']['southBoundLatitude']=str(g['geoLocationBox']['southBoundLatitude'])
                g['geoLocationBox']['eastBoundLongitude']=str(g['geoLocationBox']['eastBoundLongitude'])
                g['geoLocationBox']['westBoundLongitude']=str(g['geoLocationBox']['westBoundLongitude'])
                g['geoLocationBox'] = [g['geoLocationBox']]
        json_record['geographicCoverage'] = json_record.pop('geoLocations')

    #Publisher
    if "publisher" in json_record:
        publisher = {}
        publisher['publisherName'] = json_record['publisher']
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
