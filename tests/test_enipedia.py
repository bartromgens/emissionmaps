import unittest
import math

from enipedia import euets


class TestEnipediaSparql(unittest.TestCase):

    def test_get_country_data(self):
        print('test_get_country_data')
        country_code = 'NL'
        year = 2010
        sources = euets.get_emission_sources(country_code, year)
        filepath = euets.get_filename(country_code, year)
        euets.sources_to_csv_file(sources, filepath)

    def test_get_country_codes(self):
        codes = euets.get_country_codes()
        print(codes)
        self.assertEqual(len(codes), 29)


class TestCone(unittest.TestCase):

    def test_calc(self):
        V = 1000
        alpha = 10*math.pi/180
        w = math.pow( (3*V) / (math.pi*math.tan(alpha)), 1/3)
        print('w: ' + str(w))
        h = math.tan(alpha)*w
        print('h: ' + str(h))
        V = math.pi * w*w * h/3
        print('V: ' + str(V))
