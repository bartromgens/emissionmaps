import sys

sys.path.append('../vis')

import vis.emissioncontour


def main():
    config = vis.emissioncontour.ContourPlotConfig()
    sources = [
        {
            'lat': 52.47153911872,
            'lon': 4.634706974029,
            'emission_co2_kg': 100
        },
        {
            'lat': 52.1014156,
            'lon': 5.0784016,
            'emission_co2_kg': 300
        }
    ]
    vis.emissioncontour.Contour(emission_sources=sources, config=config)

if __name__ == "__main__":
    # test()
    main()