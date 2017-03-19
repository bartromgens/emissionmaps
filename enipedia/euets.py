import csv
from SPARQLWrapper import SPARQLWrapper, JSON

ENIPEDIA_SPARQL_ENDPOINT = "http://enipedia.tudelft.nl/sparql"


def get_filename(country_code, year):
    return 'data/eu-ets/eu-ets-emissions-{}-{}.csv'.format(country_code, year)


def get_country_codes():
    query = """
        PREFIX euets: <http://enipedia.tudelft.nl/data/EU-ETS/>
        SELECT DISTINCT ?countryCode
        WHERE {
          ?installation euets:countryCode ?countryCode
        }
    """
    sparql = SPARQLWrapper(ENIPEDIA_SPARQL_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    country_codes = []
    for result in results["results"]["bindings"]:
        code = result['countryCode']['value']
        if code:
            country_codes.append(code)
    return country_codes


def get_emission_sources(country_code, year):
    print('get_emission_sources: ' + country_code + ' ' + str(year))
    sparql = SPARQLWrapper(ENIPEDIA_SPARQL_ENDPOINT)
    query = """
        PREFIX euets: <http://enipedia.tudelft.nl/data/EU-ETS/>
        SELECT ?installation ?title coalesce(?pt, concat(?lat,", ",?lon)) as ?coordinates ?calculatedEmissions ?napinfo ?enipedia_wiki
        WHERE {{
          GRAPH <http://enipedia.tudelft.nl/data/EU-ETS> {{
            ?installation rdfs:label ?title .
            ?installation euets:euetsID ?id .
            ?installation euets:countryCode ?countryCode .
            FILTER(?countryCode = '{}') .
            ?installation euets:longitude ?lon .
            ?installation euets:latitude ?lat .
            ?installation euets:napInfo ?napinfo .
            ?napinfo euets:periodYear ?year .
            ?napinfo euets:calculatedEmissions ?calculatedEmissions .
            ?napinfo euets:allowanceAllocation ?allowanceAllocation .
            FILTER(?year = {}) .
          }}
          OPTIONAL {{ GRAPH <http://enipedia.tudelft.nl/wiki/> {{
            ?enipedia_wiki prop:EU_ETS_ID ?id .
            ?enipedia_wiki prop:Point ?pt .
          }} }}
        }} order by DESC(?calculatedEmissions)
    """  # double braces are there to allow .format later
    query = query.format(country_code, year)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    sources = []
    for result in results["results"]["bindings"]:
        enipedia_wiki_url = ''
        if 'enipedia_wiki' in result:
            enipedia_wiki_url = result['enipedia_wiki']['value']
        source = {
            'title': result['title']['value'],
            'latitude': float(result['coordinates']['value'].split(',')[0]),
            'longitude': float(result['coordinates']['value'].split(',')[1]),
            'emissions_calculated': float(result['calculatedEmissions']['value']),
            'enipedia_url': result['installation']['value'],
            'enipedia_wiki': enipedia_wiki_url,
            'napinfo': result['napinfo']['value'],
        }
        sources.append(source)
        # print(source)
    return sources


def get_all_sources_from_file(year):
    country_codes = get_country_codes()
    sources = []
    for code in country_codes:
        filepath = get_filename(code, year)
        sources += sources_from_csv_file(filepath)
    print('get_all_sources_from_file: ' + str(len(sources)) + ' found')
    return sources


def sources_to_csv_file(sources, filepath):
    print('sources_to_csv_file: ' + filepath)
    with open(filepath, 'w') as fileout:
        fileout.write('installation title;calculated emission;latitude;longitude;enipedia url;enipedia wiki url\n')
        for source in sources:
            fileout.write(
                source['title'].replace(';', ',') + ';' +
                str(source['emissions_calculated']) + ';' +
                str(source['latitude']) + ';' +
                str(source['longitude']) + ';' +
                source['enipedia_url'] + ';' +
                source['enipedia_wiki'] + '\n'
            )


def sources_from_csv_file(filepath):
    sources = []
    with open(filepath, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=';', quotechar='"')
        next(rows)  # skip header
        for row in rows:
            source = {
                'title': row[0],
                'emissions_calculated': float(row[1]),
                'latitude': float(row[2]),
                'longitude': float(row[3]),
                'enipedia_url': row[4],
                'enipedia_wiki': row[5],
            }
            sources.append(source)
    return sources