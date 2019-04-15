#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: readRaw.py
@time: 2019/4/1 21:15
@desc:
'''
from util import getBasePath
filename = 'FullMask_Grid_4000.raw'

import struct
import numpy as np
import pandas as pd

IMG_SIZE_DICT ={
    '16KM':[687,687],
    '8KM':[1374,1374],
    '4KM':[2748,2748],
    '2KM':[5496,5496],
    '1KM':[10992,10992],
    '0.5KM':[21984,21984]
}

# [latitude,latitude,longitude,longitude]
IMG_VALID_REGION = [-80.56672132,80.56672132,-174.71662309,24.11662309]


def newGeoMat(grid_resolution):
    grid_size = IMG_SIZE_DICT[grid_resolution]

    GEO_LAT = np.ndarray((grid_size[0],grid_size[1]),dtype=np.float64)
    GEO_LON = np.ndarray((grid_size[0],grid_size[1]),dtype=np.float64)

    return GEO_LAT,GEO_LON

def isGeoValid(geoCoord,geoType='lon'):
    if geoType == 'lat':
        return (geoCoord >= IMG_VALID_REGION[0]) and (geoCoord <= IMG_VALID_REGION[1])
    elif geoType == 'lon':
        return (geoCoord >= IMG_VALID_REGION[2]) and (geoCoord <= IMG_VALID_REGION[3])


def fillBlank(numpy_arr,arr_type,fillvalue=999.0):
    '''
    Judge whether the value in array is valid according to the valid region given by NSMC
    :param numpy_arr: latitude array or longitude array
    :param arr_type: 'lat' or 'lon'
    :param fillvalue:
    :return:
    '''
    if arr_type == 'lat':
        numpy_arr[(numpy_arr < IMG_VALID_REGION[0]) | (numpy_arr > IMG_VALID_REGION[1])] = fillvalue
    elif arr_type == 'lon':
        numpy_arr[(numpy_arr < IMG_VALID_REGION[2])  | (numpy_arr > IMG_VALID_REGION[3])] = fillvalue
    assert np.sum(numpy_arr==fillvalue) < (IMG_SIZE_DICT['4KM'][0] * IMG_SIZE_DICT['4KM'][1])
    # print(np.sum(numpy_arr!=fillvalue)) # the quantity of valid data
    return numpy_arr

def readRaw(fileName,grid_resolution):
    ''' read the geographical location table, which are saved as big-endian double.
    :param fileName: the file name of geographical location table
    :param grid_resolution: like '4KM','2KM'
    :return: the latitude table and longitude table.
    '''
    lat_ind,lon_ind = 0,0 # index of iteration
    GEO_LAT, GEO_LON = newGeoMat(grid_resolution) # new 2d arrays to save latitudes and longitudes.
    GEO_LAT_SIZE, GEO_LON_SIZE = GEO_LAT.shape[0], GEO_LON.shape[0] # grid size
    with open(fileName,'rb') as f:
        while lat_ind < GEO_LAT_SIZE: # the line indicates latitudes
            while lon_ind < GEO_LON_SIZE: # the column indicates longitudes
                lon = f.read(8)
                lat = f.read(8)
                lon, = struct.unpack('<d' ,lon) # Caution, the data is saved as little-endian data.
                lat, = struct.unpack('<d' ,lat)
                GEO_LON[lat_ind][lon_ind] = lon
                GEO_LAT[lat_ind][lon_ind] = lat
                lon_ind += 1
            lat_ind += 1
            lon_ind = 0
    return GEO_LAT, GEO_LON

def saveGeo(fileName,GEO_LAT,GEO_LON):
    lat_df = pd.DataFrame(GEO_LAT)
    lat_df.to_csv('%s_lat.csv'%fileName, header= True, index = True)

    lon_df = pd.DataFrame(GEO_LON)
    lon_df.to_csv('%s_lon.csv' % fileName, header=True, index = True)

if __name__=='__main__':
    GEO_LAT, GEO_LON = readRaw('%s/%s'%(getBasePath('data'),'FullMask_Grid_4000.raw'),'4KM')

    GEO_LAT = fillBlank(GEO_LAT,'lat')
    GEO_LON = fillBlank(GEO_LON,'lon')

    saveGeo('%s/%s'%(getBasePath('data'),'FullMask_Grid_4KM_999_NULL'),GEO_LAT,GEO_LON)