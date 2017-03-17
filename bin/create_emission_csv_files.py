import sys

sys.path.append('..')

import enipedia.euets

YEAR = 2010


def main():
    country_codes = enipedia.euets.get_country_codes()
    for code in country_codes:
        sources = enipedia.euets.get_emission_sources(code, YEAR)
        filepath = '../' + enipedia.euets.get_filename(code, YEAR)
        enipedia.euets.sources_to_csv_file(sources, filepath)


if __name__ == "__main__":
    main()