#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: drawGIRS.py
@time: 2019/3/28 20:46
@desc:
'''
import os
import h5py
import geopandas as gpd
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from shapely.geometry import Point
import xlwt

datafile = 'FY4A-_GIIRS-_N_DISK_1047E_L1-_IRD-_MULT_NUL_20180701000525_20180701000543_016KM_001V1.HDF'
datapath = os.getcwd()+'\\data\\'

def loadData():
    H5f = h5py.File(datapath+datafile,'r')
    print(H5f.keys())

    vis_rad = H5f['ES_ContVIS'][:]
    VIS_Lat = H5f['VIS_Latitude'][:]
    VIS_Lon = H5f['VIS_Longitude'][:]


    IRLW_rad = H5f['ES_RealLW'][:]
    IRLW_Lat = H5f['IRLW_Latitude'][:]
    IRLW_Lon = H5f['IRLW_Longitude'][:]

    H5f.close()

    return vis_rad,VIS_Lat,VIS_Lon,IRLW_rad,IRLW_Lat,IRLW_Lon


def drawMap(gdf_vis,gdf_ir):
    '''
        plot radiance in specific channel indicated by "cols"
        :param gdf:
        :param cols: specify the shown channel's name
        :param cmap:
        :return:
        '''
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    # print(world.continent)
    cmap_list = ['OrRd', 'Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r']
    # We restrict to Asia and Oceania
    # .tolist() or (world.continent == 'Oceania').tolist()
    ax = world[(world.name == 'China')]. \
        plot(color='white', edgecolor='black', linewidth=2)

    gdf_vis.plot(ax=ax, column='data', cmap=cmap_list[1],markersize=2)
    plt.legend()
    plt.show()

def loadGeoData(data_mat,lat_mat,lon_mat):
    '''
    load data as common dataframe or geographical dataframe
    :return:
    '''
    data_mat = data_mat.reshape(data_mat.shape[0]*data_mat.shape[1], )
    lat_mat = lat_mat.reshape(lat_mat.shape[0] * lat_mat.shape[1], )
    lon_mat = lon_mat.reshape(lon_mat.shape[0] * lon_mat.shape[1], )
    df = pd.DataFrame({'data',data_mat})
    df['Coordinates'] = list(zip(lat_mat, lon_mat))
    df['Coordinates'] = df['Coordinates'].apply(Point)
    gdf = gpd.GeoDataFrame(df, geometry='Coordinates')
    plt.show()
    return gdf

if __name__=='__main__':
    vis_rad, VIS_Lat, VIS_Lon, IRLW_rad, IRLW_Lat, IRLW_Lon = loadData()
    vis_gdf = loadGeoData(vis_rad, VIS_Lat, VIS_Lon)
    ir_gdf = loadGeoData(IRLW_rad, IRLW_Lat, IRLW_Lon)

    drawMap(vis_gdf,ir_gdf)
