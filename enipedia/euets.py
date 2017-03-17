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
        select distinct ?installation ?installationName ?latitude ?longitude ?calculatedEmissions ?napinfo
        where {{
          ?installation rdf:type euets:Installation .
          ?installation euets:name ?installationName .
          ?installation euets:latitude ?latitude .
          ?installation euets:longitude ?longitude .
          ?installation euets:napInfo ?napinfo .
          ?napinfo euets:periodYear {} .
          ?napinfo euets:calculatedEmissions ?calculatedEmissions .
          ?installation euets:countryCode "{}" .
        }}
    """  # double braces are there to allow .format later
    query = query.format(year, country_code)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    sources = []
    for result in results["results"]["bindings"]:
        source = {
            'name': result['installationName']['value'],
            'enipedia_url': result['installation']['value'],
            'latitude': float(result['latitude']['value']),
            'longitude': float(result['longitude']['value']),
            'emissions_calculated': float(result['calculatedEmissions']['value']),
            'napinfo': result['napinfo']['value'],
        }
        sources.append(source)
        # print(source)
    return sources


def sources_to_csv_file(sources, filepath):
    print('sources_to_csv_file: ' + filepath)
    with open(filepath, 'w') as fileout:
        fileout.write('installation name;calculated emission;latitude;longitude;enipedia url\n')
        for source in sources:
            fileout.write(source['name'].replace(';', ',') + ';' + str(source['emissions_calculated']) + ';' + str(source['latitude']) + ';' + str(source['longitude']) + ';' + source['enipedia_url'] + '\n')


def get_all_sources_from_file(year):
    country_codes = get_country_codes()
    sources = []
    for code in country_codes:
        filepath = get_filename(code, year)
        sources += sources_from_csv_file(filepath)
    print('get_all_sources_from_file: ' + str(len(sources)) + ' found')
    return sources


def sources_from_csv_file(filepath):
    sources = []
    with open(filepath, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=';', quotechar='"')
        next(rows)  # skip header
        for row in rows:
            source = {
                'name': row[0],
                'emissions_calculated': float(row[1]),
                'latitude': float(row[2]),
                'longitude': float(row[3]),
                'enipedia_url': row[4],
            }
            sources.append(source)
    return sources