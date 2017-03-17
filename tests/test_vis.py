import unittest
import numpy
import math


from matplotlib.colors import LogNorm, SymLogNorm, PowerNorm

import enipedia.euets
import vis.emissioncontour
import vis.emissionsouce
import vis.data


class TestCountour(unittest.TestCase):
    YEAR = 2010

    def test_create_contour(self):
        config = vis.emissioncontour.ContourPlotConfig()
        sources = enipedia.euets.get_all_sources_from_file(year=self.YEAR)
        contour = vis.emissioncontour.Contour(emission_sources=sources, config=config)
        # contour.create_contour_data()
        # contour.save()

        contour.load()
        level_upper = contour.Z.max()
        level_lower = contour.Z.min()
        print(level_upper)
        print(level_lower)

        n_contours = 11
        level_lower = 500
        level_upper /= 2
        # norm = SymLogNorm(linthresh=1.0, vmin=level_lower, vmax=level_upper)
        # norm = PowerNorm(gamma=2, vmin=level_lower, vmax=level_upper)
        norm = None
        levels = numpy.logspace(
            start=math.log(level_lower),
            stop=math.log(level_upper + 2),
            num=n_contours,
            base=math.e
        )
        levels = numpy.linspace(
            start=level_lower,
            stop=level_upper,
            num=n_contours
        )
        print(levels)
        # norm=None
        # contour.create_contour_plot(levels=levels, norm=norm)
        contour.create_geojson('emissions.geojson', levels=levels, norm=norm)


class TestReadData(unittest.TestCase):

    def test_load_csv(self):
        sources = vis.data.load_emission_sources_csv()
        print(len(sources))


class TestCreateSourceJson(unittest.TestCase):

    def test_load_csv(self):
        sources = vis.data.load_emission_sources_csv()
        filepath = 'sources.json'
        vis.emissionsouce.create_source_info_json(sources, filepath)
        print(len(sources))