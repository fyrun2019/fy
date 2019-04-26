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
import struct
import numpy as np
import pandas as pd
import config

class ReadRaw(object):

    def __init__(self,resolution,filename,fillValue=999):
        '''
        :param resolution: like '4KM','2KM'
        '''
        self._resolution = resolution
        self._grid_size = config.IMG_SIZE[self._resolution]
        self._fillValue = fillValue

        savefileName = self.saveFilename(filename)
        GEO_LAT, GEO_LON = self.readRaw('%s/%s' % (getBasePath('data'), filename))

        GEO_LAT = self.fillBlank(GEO_LAT, 'lat')
        GEO_LON = self.fillBlank(GEO_LON, 'lon')

        self.saveGeo('%s/%s' % (getBasePath('data'), savefileName), GEO_LAT, GEO_LON)

    def newGeoMat(self):

        GEO_LAT = np.ndarray((self._grid_size[0],self._grid_size[1]),dtype=np.float64)
        GEO_LON = np.ndarray((self._grid_size[0],self._grid_size[1]),dtype=np.float64)

        return GEO_LAT,GEO_LON

    def fillBlank(self,numpy_arr,arr_type):
        '''
        Judge whether the value in array is valid according to the valid region given by NSMC
        :param numpy_arr: latitude array or longitude array
        :param arr_type: 'lat' or 'lon'
        :param fillvalue:
        :return:
        '''
        if arr_type == 'lat':
            numpy_arr[(numpy_arr < config.IMG_VALID_REGION[0]) | (numpy_arr > config.IMG_VALID_REGION[1])] = self._fillValue
        elif arr_type == 'lon':
            numpy_arr[numpy_arr<-180.0] = self._fillValue
            numpy_arr[numpy_arr>180.0] = self._fillValue
            numpy_arr[(numpy_arr > config.IMG_VALID_REGION[2]) & (numpy_arr < config.IMG_VALID_REGION[3])] = self._fillValue
        assert np.sum(numpy_arr==self._fillValue) <= (
                config.IMG_SIZE[self._resolution][0] * config.IMG_SIZE[self._resolution][1])
        # print(np.sum(numpy_arr!=fillvalue)) # the quantity of valid data
        return numpy_arr

    def readRaw(self,fileName):
        ''' read the geographical location table, which are saved as big-endian double.
        :param fileName: the file name of geographical location table
        :return: the latitude table and longitude table.
        '''

        GEO_LAT, GEO_LON = self.newGeoMat() # new 2d arrays to save latitudes and longitudes.
        GEO_LAT_SIZE, GEO_LON_SIZE = GEO_LAT.shape[0], GEO_LON.shape[0] # grid size
        lat_ind, lon_ind = 0, 0  # index of iteration
        with open(fileName,'rb') as f:
            while lat_ind < GEO_LAT_SIZE: # the line indicates latitudes
                while lon_ind < GEO_LON_SIZE: # the column indicates longitudes
                    lat = f.read(8)
                    lon = f.read(8)
                    lat, = struct.unpack('<d', lat)
                    lon, = struct.unpack('<d' ,lon) # Caution, the data is saved as little-endian data, not what is said by the official file

                    GEO_LON[lat_ind][lon_ind] = lon
                    GEO_LAT[lat_ind][lon_ind] = lat
                    lon_ind += 1
                lat_ind += 1
                lon_ind = 0
        return GEO_LAT, GEO_LON

    def saveGeo(self,fileName,GEO_LAT,GEO_LON):
        lat_df = pd.DataFrame(GEO_LAT)
        lat_df.to_csv('%s_lat.csv'%fileName, header= True, index = True)

        lon_df = pd.DataFrame(GEO_LON)
        lon_df.to_csv('%s_lon.csv' % fileName, header=True, index = True)

    def saveFilename(self,filename):
        '''
        Make filename for saving, like
        :param filename:
        :return:
        '''
        return '%s_%d_NULL'%(filename.split('.')[0],self._fillValue)



if __name__=='__main__':

    loader4 = ReadRaw('4KM',filename='FullMask_Grid_4000.raw')

    loader2 = ReadRaw('2KM', filename='FullMask_Grid_2000.raw')

    loader1 = ReadRaw('1KM',filename='FullMask_Grid_1000.raw')