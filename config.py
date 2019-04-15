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

KEY_VALUE = [ # the key value of observations for each channel.
    'NOMChannel01',
    'NOMChannel02',
    'NOMChannel03',
    'NOMChannel04',
    'NOMChannel05',
    'NOMChannel06',
    'NOMChannel07',
    'NOMChannel08',
    'NOMChannel09',
    'NOMChannel10',
    'NOMChannel11',
    'NOMChannel12',
    'NOMChannel13',
    'NOMChannel14'
]

# [latitude,latitude,longitude,longitude]
IMG_VALID_REGION = [-80.56672132,80.56672132,-174.71662309,24.11662309]

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


