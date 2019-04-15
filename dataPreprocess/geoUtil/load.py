#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: CalibrationShow.py
@time: 2019/4/14 15:08
@desc: show image data on a map according to the calibration location
'''

import geopandas as gpd
import pandas as pd
from util import getBasePath
from shapely.geometry import Point

class Loader(object):
    def loadGeoData(self,resolution, category='raw'):
        df = pd.read_csv(
            "%s/FullMask_Grid_%s_999_NULL_%s.csv" % (getBasePath(''), resolution,'lat'),
                         sep=',')
        df['Coordinates'] = list(zip(df.lon, df.lat))
        df['Coordinates'] = df['Coordinates'].apply(Point)
        gdf = gpd.GeoDataFrame(df, geometry='Coordinates')
        return gdf