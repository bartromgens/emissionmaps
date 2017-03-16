import unittest
import numpy
import math

from matplotlib.colors import LogNorm, SymLogNorm

import vis.emissioncontour


class TestCountour(unittest.TestCase):

    def test_create_contour(self):
        config = vis.emissioncontour.ContourPlotConfig()
        n_contours = 21
        level_lower = 0
        level_upper = 1000000
        norm = SymLogNorm(linthresh=0.1, vmin=level_lower, vmax=level_upper)
        levels = numpy.logspace(
            start=level_lower,
            stop=math.log(level_upper + 2),
            num=n_contours,
            base=math.e
        )
        # levels = numpy.linspace(
        #     start=level_lower,
        #     stop=level_upper,
        #     num=n_contours
        # )
        sources = [
            {
                'lat': 52.47153911872,
                'lon': 4.634706974029,
                'emission_co2_kg': 1e13
            },
            {
                'lat': 52.1014156,
                'lon': 5.0784016,
                'emission_co2_kg': 3e13
            }
        ]
        contour = vis.emissioncontour.Contour(emission_sources=sources, config=config)
        contour.create_contour_data()
        contour.create_contour_plot(levels=levels, norm=norm)
        contour.create_geojson('emissions.geojson', levels=levels, norm=norm)