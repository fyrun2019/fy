#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: CoordTrans.py
@time: 2019/4/10 8:52
@desc: Coordinate transformation between image and real geographical coordinates.
'''
import numpy as np
class CoordTrans(object):
    def __init__(self,resolution):
        self._resolution = resolution  # eg. self._resoluttion = '0.5KM'

        self._pi = 3.1415926535897932384626
        self._ea = 6378.137
        self._eb = 6356.7523
        self._h = 42164
        self._lambda_d = 104.7
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

        self._coff = self._COFF[self._resolution]
        self._loff = self._LOFF[self._resolution]
        self._cfac = self._CFAC[self._resolution]
        self._lfac = self._LFAC[self._resolution]

        # [latitude,latitude,longitude,longitude]
        self._GEO_VALID_REGION = [-80.56672132,80.56672132,-174.71662309,24.11662309]

        self._geo_fillvalue = 999.0
        self._img_fillvalue = -1
        self._img_size = self._IMG_SIZE[self._resolution][0]

    def isIMGValid(self,imgCoord):
        return (imgCoord>=0) and (imgCoord<=self._img_size)

    def isGeoValid(self,geoCoord,geoType='lon'):
        if geoType == 'lat':
            return (geoCoord >= self._GEO_VALID_REGION[0]) and (geoCoord <= self._GEO_VALID_REGION[1] )
        elif geoType == 'lon':
            return (geoCoord >= self._GEO_VALID_REGION[2]) and (geoCoord <= self._GEO_VALID_REGION[3])

    def geo2ImgCoord(self,lon,lat):
        l,c = 0,0

        # step 1
        if not (((self.isGeoValid(lon,'lon')) and (self.isGeoValid(lat,'lat')))):
            print(30 * '-' + 'Out of valid region' + 30 * '-')
            return self._img_fillvalue,self._img_fillvalue

        # step 2
        lon = lon * self._pi / 180.0
        lat = lat * self._pi / 180.0

        # step 3
        phi_e = np.arctan((self._eb**2)/(self._ea**2)*np.tan(lat))
        lambda_e = lon

        # step 4
        tmp = (self._ea**2-self._eb**2)/(self._ea**2)*(np.cos(phi_e)**2)
        r_e = self._eb/np.sqrt(1-tmp)

        # step 5
        r1 = self._h-r_e*np.cos(phi_e)*np.cos(lambda_e-self._lambda_d)
        r2 = -r_e*np.cos(phi_e)*np.sin(lambda_e-self._lambda_d)
        r3 = r_e*np.sin(phi_e)

        # step 6
        r_n = np.sqrt(r1**2+r2**2+r3**2)
        x = np.arctan(-r2/r1)*(180.0/self._pi)
        y = np.arcsin(-r3/r_n)*(180.0/self._pi)

        # step 7
        c = self._coff + x/np.power(2,16)*self._cfac
        l = self._loff + y/np.power(2,16)*self._lfac

        if self.isIMGValid(l) and self.isIMGValid(c):
            return np.ceil(l),np.ceil(c)

    def img2GeoCoord(self,l,c):
        lon = 0.0
        lat = 0.0

        # step 1
        x = self._pi * (c-self._coff)*np.power(2,16)/180.0/self._cfac
        y = self._pi * (l-self._loff) * np.power(2,16)/180.0/self._lfac

        # step 2
        s_d_tmp_1 = self._h * np.cos(x)*np.cos(y)
        s_d_tmp_2 \
            = np.cos(y)**2 + (self._ea**2)/(self._eb**2)*(np.sin(y))**2
        s_d = np.sqrt(s_d_tmp_1**2-s_d_tmp_2*(self._h**2-self._ea**2))
        s_n = (s_d_tmp_1-s_d)/s_d_tmp_2
        s1 = self._h-s_n*np.cos(x)*np.cos(y)
        s2 = s_n*np.sin(x)*np.cos(y)
        s3 = -s_n*np.sin(y)
        s_xy = np.sqrt(s1**2+s2**2)

        # step 3
        lat = 180.0/self._pi*np.arctan(s2/s1)+self._lambda_d
        lon = 180.0/self._pi*np.arctan(((self._ea**2) / (self._eb**2))*(s3/s_xy))

        if self.isGeoValid(lon,'lon') and self.isGeoValid(lat,'lat'):
            return lon,lat
        else:
            print(30 * '-' + 'Out of valid region' + 30*'-')
            return self._geo_fillvalue,self._geo_fillvalue

        return lon,lat

if __name__ == '__main__':

    calculator = CoordTrans('4KM')

    res = '4KM'
    l0,c0 = 890,727
    # the corresponding latitude and longitude got from location file are (-1.05792E-26, -1.0744)

    lon,lat = calculator.img2GeoCoord(l0,c0)

    print('lon:  %.2f' % lon)
    print('lat:  %.2f' % lat)

    print(30*'='+'test geo to image'+30*'=')

    lon0,lat0 = 18.32,78.67

    l,c = -1,-1

    l,c = calculator.geo2ImgCoord(lon0,lat0)
    lon_test, lat_test = calculator.img2GeoCoord(l,c)

    if not (calculator.isGeoValid(lon_test,'lon')) or (calculator.isGeoValid(lat_test,'lat')):
        lon0 = lon0 + 0.01
        lat0 = lat0 + 0.01
        l,c = calculator.geo2ImgCoord(lon0,lat0)

    print('l: %d'%l)
    print('c: %d'%c)