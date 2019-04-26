#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: config.py
@time: 2019/4/13 9:55
@desc:
'''

IMG_SIZE = {
    '4KM':[2748,2748],
    '2KM':[5496,5496],
    '1KM':[10992,10992],
    '0.5KM':[21984,21984]
}

NOM_KEY_VALUE =  {# the key value of observations for each channel.
    "0.5KM": ("NOMChannel02",),
            "1KM": ("NOMChannel01", "NOMChannel02", "NOMChannel03"),
            "2KM": tuple(["NOMChannel%02d" % x for x in range(1, 8)]),
            "4KM": tuple(["NOMChannel%02d" % x for x in range(1, 15)])
}

CALIB_KEY_VALUE = {
    "0.5KM": ("CALChannel02",),
    "1KM": ("CALChannel01", "CALChannel02", "CALChannel03"),
    "2KM": tuple(["CALChannel%02d"%x for x in range(1, 8)]),
    "4KM": tuple(["CALChannel%02d" %x for x in range(1, 15)])
}

# [latitude,latitude,longitude,longitude]
IMG_VALID_REGION = [-80.56672132,80.56672132,-174.71662309,24.11662309]


# geographical locations
GEO_RAW_FILES = {
    '4KM': 'FullMask_Grid_4000.raw',
    '2KM': 'FullMask_Grid_2000.raw',
    '1KM': 'FullMask_Grid_1000.raw'
}

# global functions
def isGeoValid(geoCoord,geoType='lon'):
    '''
    Judge whether the coordinates are in the valid region.
    :param geoCoord: latitude or longitude
    :param geoType: indicate whether it is latitude or longitude.
    :return:
    '''
    if geoType == 'lat':
        return (geoCoord >= IMG_VALID_REGION[0]) and (geoCoord <= IMG_VALID_REGION[1])
    elif geoType == 'lon':
        return (geoCoord >= IMG_VALID_REGION[2]) and (geoCoord <= IMG_VALID_REGION[3])


