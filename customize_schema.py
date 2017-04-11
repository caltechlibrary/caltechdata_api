# Convert a DataCite 4 standard schema json record to the customized internal
# schema used by TIND in CaltechDATA
import json
import argparse

def customize_schema(json_record):

    #Extract subjects to single string
    subjects = json_record['subjects']
    substr = ''
    for s in subjects:
        if substr != '':
            substr = substr + ', '
        substr = substr+s['subject']
    json_record['subjects']=substr

    #Extract identifier and label as DOI
    identifier = json_record['identifier']['identifier']
    #Cound check identifierType for validation
    json_record['doi'] = identifier
    del json_record['identifier']
    #will delete other ideintifiers in file

    #Extract title
    titles = json_record['titles']
    for t in titles:
        if 'titleType' not in t:
            json_record['title']=t['title']

    #Change related identifier labels
    for listing in json_record['relatedIdentifiers']:
        listing['relatedIdentifierRelation'] = listing.pop('relationType')
        listing['relatedIdentifierScheme'] = listing.pop('relatedIdentifierType')

    #change author formatting
    authors = json_record['creators']
    for a in authors:
        a['authorAffiliation'] = a.pop('affiliations')
        a['authorName'] = a.pop('creatorName')
    json_record['authors']=json_record.pop('creators')

    #format
    json_record['format']=json_record.pop('formats')

    #dates
    dates = json_record['dates']
    for d in dates:
        d['relevantDateValue']=d.pop('date')
        d['relevantDateType']=d.pop('dateType')
    json_record['relevantDates']=json_record.pop('dates')

    #license
    licenses = json_record['rightsList']
    json_record['license']=licenses[0]['rights']
    #Only transfers first license
    
    #Funding
    funding = json_record['fundingReferences']
    for f in funding:
        f['fundingName']=f.pop('funderName')
        if 'awardNumber' in f:
            f['fundingAwardNumber']=f.pop('awardNumber')
    json_record['fundings']=json_record.pop('fundingReferences')
    #Some fields not preserved

    #Geo
    json_record['geographicCoverage'] = json_record.pop('geoLocations')

    #Publisher
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
