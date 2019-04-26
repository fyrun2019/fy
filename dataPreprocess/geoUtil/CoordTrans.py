#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: CoordTrans.py
@time: 2019/4/10 8:52
@desc: Coordinate transformation between image and real geographical coordinates.
'''
from numpy import deg2rad, rad2deg, arctan, arcsin, tan, sqrt, cos, sin,power,rint
import config
import pandas as pd
import util
import numpy as np
class CoordTrans(object):
    def __init__(self,resolution):
        self._resolution = resolution  # eg. self._resoluttion = '0.5KM'

        self._ea = 6378.137
        self._eb = 6356.7523
        self._h = 42164
        self._lambda_d = deg2rad(104.7)
        self._COFF = {
            '0.5KM': 10991.5,
            '1KM': 5495.5,
            '2KM': 2747.5,
            '4KM': 1373.5
        }
        self._CFAC = {
            '0.5KM': 81865099,
            '1KM': 40932549,
            '2KM': 20466274,
            '4KM': 10233137
        }
        self._LOFF = {
            '0.5KM': 10991.5,
            '1KM': 5495.5,
            '2KM': 2747.5,
            '4KM': 1373.5
        }
        self._LFAC = {
            '0.5KM': 81865099,
            '1KM': 40932549,
            '2KM': 20466274,
            '4KM': 10233137
        }
        self._IMG_SIZE = {
            '4KM':[2748,2748],
            '2KM':[5496,5496],
            '1KM':[10992,10992],
            '0.5KM':[21984,21984]
        }

        # offset for calculating image index
        self._OFFSET = {  # lon,lat
            '4KM': [0.005, -0.05],
            '2KM': [0,0],
            '1KM': [0,0]
        }

        self._coff = self._COFF[self._resolution]
        self._loff = self._LOFF[self._resolution]
        self._cfac = self._CFAC[self._resolution]
        self._lfac = self._LFAC[self._resolution]

        # [latitude,latitude,longitude,longitude]
        self._GEO_VALID_REGION = [-80.56672132,80.56672132,-174.71662309,24.11662309]

        self._geo_fillvalue = 999.0
        self._img_fillvalue = -1
        self._img_size = self._IMG_SIZE[self._resolution][0]
        self._offset = self._OFFSET[self._resolution]




    def isIMGValid(self,imgCoord):
        return (imgCoord>=0) and (imgCoord<=self._img_size)

    # def isGeoValid(self,geoCoord,geoType='lon'):
    #     if geoType == 'lat':
    #         return (geoCoord >= self._GEO_VALID_REGION[0]) and (geoCoord <= self._GEO_VALID_REGION[1] )
    #     elif geoType == 'lon':
    #         return ((geoCoord <= self._GEO_VALID_REGION[2]) and geoCoord >= -180.0) or (geoCoord >= self._GEO_VALID_REGION[3] and geoCoord<=180.0)

    def geo2ImgCoord(self,lon,lat):
        l,c = 0,0 # start from 0,0

        # step 1
        # if not (((self.isGeoValid(lon,'lon')) and (self.isGeoValid(lat,'lat')))):
        #     print(30 * '-' + 'Out of valid region' + 30 * '-')
        #     return self._img_fillvalue,self._img_fillvalue

        # step 2
        lon = deg2rad(lon+self._offset[0])
        lat = deg2rad(lat+self._offset[1])

        # step 3
        phi_e = arctan((self._eb**2)/(self._ea**2)*tan(lat))
        lambda_e = lon

        # step 4
        tmp = (self._ea**2-self._eb**2)/(self._ea**2)*(cos(phi_e)**2)
        r_e = self._eb/sqrt(1-tmp)

        # step 5
        r1 = self._h-r_e*cos(phi_e)*cos(lambda_e-self._lambda_d)
        r2 = -r_e*cos(phi_e)*sin(lambda_e-self._lambda_d)
        r3 = r_e*sin(phi_e)

        # step 6
        r_n = sqrt(r1**2+r2**2+r3**2)
        x = rad2deg(arctan(-r2/r1))
        y = rad2deg(arcsin(-r3/r_n))

        # step 7
        c = self._coff + x/power(2,16)*self._cfac
        l = self._loff + y/power(2,16)*self._lfac

        l[ (l<0) | (l>=self._img_size)] = self._img_fillvalue
        c[(c < 0) | (c >= self._img_size)] = self._img_fillvalue

        return rint(l),rint(c)

    def img2GeoCoord(self,l,c):
        lon = 0.0
        lat = 0.0

        # step 1
        x = deg2rad((c-self._coff)*power(2,16)/self._cfac)
        y = deg2rad((l-self._loff) * power(2,16)/self._lfac)

        # step 2
        s_d_tmp_1 = self._h * cos(x)*cos(y)
        s_d_tmp_2 \
            = cos(y)**2 + (self._ea**2)/(self._eb**2)*(sin(y))**2
        s_d = sqrt(s_d_tmp_1**2-s_d_tmp_2*(self._h**2-self._ea**2))
        s_n = (s_d_tmp_1-s_d)/s_d_tmp_2
        s1 = self._h-s_n*cos(x)*cos(y)
        s2 = s_n*sin(x)*cos(y)
        s3 = -s_n*sin(y)
        s_xy = sqrt(s1**2+s2**2)

        # step 3
        lon = rad2deg(arctan(s2/s1)+self._lambda_d)
        lat = rad2deg(arctan(((self._ea**2) / (self._eb**2))*(s3/s_xy)))

        # if self.isGeoValid(lon,'lon') and self.isGeoValid(lat,'lat'):
        return lon,lat
        # else:
            # print(30 * '-' + 'Out of valid region' + 30*'-')
            # return self._geo_fillvalue,self._geo_fillvalue

        # return lon,lat

def getAllGridGeoCoord(calculator,resolution='4KM'):
    GEO_LAT = np.ndarray((config.IMG_SIZE[resolution][0], config.IMG_SIZE[resolution][1]), dtype=np.float64)
    GEO_LON = np.ndarray((config.IMG_SIZE[resolution][0], config.IMG_SIZE[resolution][1]), dtype=np.float64)

    lat_size,lon_size = config.IMG_SIZE[resolution][0],config.IMG_SIZE[resolution][1]

    lat_ind, lon_ind = 0,0  # index of iteration
    while lat_ind < lat_size:  # the line indicates latitudes
        while lon_ind < lon_size:  # the column indicates longitudes
            GEO_LON[lat_ind][lon_ind],GEO_LAT[lat_ind][lon_ind] = calculator.img2GeoCoord(lat_ind,lon_ind)
            lon_ind += 1
        lon_ind = 0
        lat_ind += 1
    return GEO_LAT, GEO_LON

def saveGeo(GEO_LAT,GEO_LON,filename='%stransFormula_IMG_2_GEO'%util.getBasePath('data')):
    lat_df = pd.DataFrame(GEO_LAT)
    lat_df.to_csv('%s_%s_lat.csv' % (filename,res), header=True, index=True)

    lon_df = pd.DataFrame(GEO_LON)
    lon_df.to_csv('%s_%s_lon.csv' % (filename,res), header=True, index=True)

# def getIMGBBoxByGeoBox(calculator,geo_range_str,res):
#     # 若geo_range没有指定，则读取全部数据，不定标
#     geo_range = eval(geo_range_str,res)
#
#     lat_S, lat_N, lon_W, lon_E, step = geo_range
#     lat = np.arange(lat_N, lat_S - 0.005, -step)
#     lon = np.arange(lon_W, lon_E + 0.005, step)
#     lon, lat = np.meshgrid(lon, lat)
#     l, c = calculator.geo2ImgCoord(lon, lat)  # 求标称全圆盘行列号
#     l = np.rint(l).astype(np.uint16)
#     c = np.rint(c).astype(np.uint16)
#     # DISK全圆盘数据和REGC中国区域数据区别在起始行号和终止行号
#     channel = self.h5file[NOMChannelname][()][self.l - self.l_begin, self.c]
#     CALChannel = self.h5file[CALChannelname][()]  # 定标表
#     self.channels[channelname] = CALChannel[channel]  # 缺测值！


if __name__ == '__main__':
    res = '4KM'
    calculator = CoordTrans(resolution=res)

    GEO_LAT,GEO_LON = getAllGridGeoCoord(calculator,res)
    saveGeo(GEO_LAT,GEO_LON)

    res = '2KM'
    calculator = CoordTrans(resolution=res)

    GEO_LAT, GEO_LON = getAllGridGeoCoord(calculator, res)
    saveGeo(GEO_LAT, GEO_LON)

    res = '1KM'
    calculator = CoordTrans(resolution=res)

    GEO_LAT, GEO_LON = getAllGridGeoCoord(calculator, res)
    saveGeo(GEO_LAT, GEO_LON)
