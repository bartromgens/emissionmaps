import sys
import os
import math
import logging

import numpy
from scipy.spatial import KDTree

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import geojson
import geojsoncontour

import vis.utilgeo

logger = logging.getLogger(__name__)


class ContourPlotConfig(object):
    def __init__(self):
        self.bound_box_filepath = 'bounding_box.geojson'
        self.stepsize_deg = 0.05
        self.n_processes = 4
        self.n_nearest = 20
        self.lon_start = 3.0
        self.lat_start = 50.5
        self.delta_deg = 6.5
        self.lon_end = self.lon_start + self.delta_deg
        self.lat_end = self.lat_start + self.delta_deg / 2.0
        self.min_angle_between_segments = 7


class Contour(object):
    def __init__(self, emission_sources, config, data_dir=None):
        self.emission_sources = emission_sources
        self.config = config
        self.data_dir = data_dir

    def create_contour_data(self, filepath=None):
        numpy.set_printoptions(3, threshold=100, suppress=True)  # .3f

        altitude = 0.0
        self.lonrange = numpy.arange(self.config.lon_start, self.config.lon_end, self.config.stepsize_deg)
        self.latrange = numpy.arange(self.config.lat_start, self.config.lat_end, self.config.stepsize_deg / 2.0)
        self.Z = numpy.zeros((int(self.lonrange.shape[0]), int(self.latrange.shape[0])))
        gps = vis.utilgeo.GPS()

        positions = []
        for source in self.emission_sources:
            x, y, z = gps.lla2ecef([source['lat'], source['lon'], altitude])
            positions.append([x, y, z])

        tree = KDTree(positions)

        logger.info('starting spatial interpolation')
        self.Z = self.get_emission_per_square_meter(
            kdtree = tree,
            sources=self.emission_sources,
            gps=gps,
            lonrange=self.lonrange,
            latrange=self.latrange,
            altitude=altitude,
            n_nearest=min([10, len(self.emission_sources)])
        )


    @staticmethod
    def get_emission_per_square_meter(kdtree, sources, gps, latrange, lonrange, altitude, n_nearest):
        logger.info('get_emission_per_square_meter')
        Z = numpy.zeros((int(latrange.shape[0]), int(lonrange.shape[0])))
        for i, lat in enumerate(latrange):
            if i % (len(latrange) / 10) == 0:
                logger.debug(str(int(i / len(latrange) * 100)) + '%')
            for j, lon in enumerate(lonrange):
                x, y, z = gps.lla2ecef([lat, lon, altitude])
                local_emission_per_square_m = 0.0
                distances, indexes = kdtree.query([x, y, z], n_nearest)
                for distance, index in zip(distances, indexes):
                    print(index)
                    print('length: ' + str(len(distances)))
                    local_emission_per_square_m += sources[index]['emission_co2_kg'] / (math.pi*distance*distance)
                print('local emission: ' + str(local_emission_per_square_m))
                Z[i][j] = local_emission_per_square_m
        return Z


    def create_contour_plot(self, levels, norm=None):
        figure = Figure(frameon=False)
        FigureCanvas(figure)
        ax = figure.add_subplot(111)
        # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
        contours = ax.contour(
            self.lonrange, self.latrange, self.Z,
            levels=levels,
            # norm=norm,
            cmap=plt.cm.jet,
            linewidths=3
        )
        figure.savefig('test.png', dpi=90)


            # self.create_geojson(filepath, max_zoom, min_zoom, stroke_width)

    def create_geojson(self, filepath, min_zoom=0, max_zoom=12, stroke_width=1, levels=[], norm=None):
        figure = Figure(frameon=False)
        FigureCanvas(figure)
        ax = figure.add_subplot(111)
        # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
        contours = ax.contour(
            self.lonrange, self.latrange, self.Z,
            levels=levels,
            norm=norm,
            cmap=plt.cm.jet,
            linewidths=3
        )

        ndigits = len(str(int(1.0 / self.config.stepsize_deg))) + 1
        logger.info('converting contour to geojson file: ' + filepath)
        geojsoncontour.contour_to_geojson(
            contour=contours,
            geojson_filepath=filepath,
            contour_levels=levels,
            min_angle_deg=self.config.min_angle_between_segments,
            ndigits=ndigits,
            unit='min',
            stroke_width=stroke_width
        )
        with open(filepath, 'r') as jsonfile:
            feature_collection = geojson.load(jsonfile)
            for feature in feature_collection['features']:
                feature["tippecanoe"] = {"maxzoom": str(int(max_zoom)), "minzoom": str(int(min_zoom))}
        dump = geojson.dumps(feature_collection, sort_keys=True)
        with open(filepath, 'w') as fileout:
            fileout.write(dump)

        # cbar = figure.colorbar(contours, format='%d', orientation='horizontal')
        # cbar.set_label('Travel time [minutes]')
        # # cbar.set_ticks(self.config.colorbar_ticks)
        # ax.set_visible(False)
        # figure.savefig(
        #     filepath.replace('.geojson', '') + "_colorbar.png",
        #     dpi=90,
        #     bbox_inches='tight',
        #     pad_inches=0,
        #     transparent=True,
        # )

    # def create_geojson_tiles(self, filepaths, tile_dir, min_zoom=0, max_zoom=12):
    #     bound_box_filepath = os.path.join(self.data_dir, self.config.bound_box_filepath)
    #     assert os.path.exists(bound_box_filepath)
    #     filepaths.append(bound_box_filepath)
    #     togeojsontiles.geojson_to_mbtiles(
    #         filepaths=filepaths,
    #         tippecanoe_dir=TIPPECANOE_DIR,
    #         mbtiles_file='out.mbtiles',
    #         minzoom=min_zoom,
    #         maxzoom=max_zoom,
    #         full_detail=10,
    #         lower_detail=8,
    #         min_detail=7
    #     )
    #     logger.info('converting mbtiles to geojson-tiles')
    #     togeojsontiles.mbtiles_to_geojsontiles(
    #         tippecanoe_dir=TIPPECANOE_DIR,
    #         tile_dir=tile_dir,
    #         mbtiles_file='out.mbtiles',
    #     )
    #     logger.info('DONE: create contour json tiles')
