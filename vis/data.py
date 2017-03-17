import csv
import requests

from local_settings import GOOGLE_API_KEY


def load_emission_sources_csv():
    filepath = 'data/2013-2015_dutch_ets_emissies_locations.csv'
    emission_sources = []
    with open(filepath, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in rows:
            lat = ''
            lon = ''
            # if not 'Tata' in row[1]:
            #     continue
            if row[5] and row[6]:
                lat = float(row[5])
                lon = float(row[6])
            emission_source = {
                'name': row[1],
                'emission_2013_tons': float(row[2].replace(',', '').replace('-', '0')),
                'emission_2014_tons': float(row[3].replace(',', '').replace('-', '0')),
                'emission_2015_tons': float(row[4].replace(',', '').replace('-', '0')),
                'lat': lat,
                'lon': lon,
            }
            # print(emission_source)
            emission_sources.append(emission_source)
    return emission_sources


def add_location_data_to_sources():
    filepath = 'data/2013-2015_dutch_ets_emissies.csv'
    fileout = 'data/2013-2015_dutch_ets_emissies_locations.csv'
    with open(filepath, 'r') as csvfile:
        with open(fileout, 'w') as fileout:
            counter = 0
            rows = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(rows)
            next(rows)
            for row in rows:
                print(row)
                url = 'https://maps.googleapis.com/maps/api/geocode/json'
                params = {
                    # 'output': 'json',
                    'address': row[1] + ', the Netherlands',
                    'key': GOOGLE_API_KEY
                }
                print(params)
                print('================')
                response = requests.get(url=url, params=params)
                print(response.json())
                locations = response.json()
                lat = ''
                lon = ''
                if locations['results']:
                    lat = str(locations['results'][0]['geometry']['location']['lat'])
                    lon = str(locations['results'][0]['geometry']['location']['lng'])
                print(lat)
                print(lon)
                counter += 1
                fileout.write(
                    row[0] + ';' + row[1] + ';' + row[2] + ';' + row[3] + ';' + row[4] + ';' + lat + ';' + lon + '\n')