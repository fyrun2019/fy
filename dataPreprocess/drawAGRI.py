#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: drawAGRI.py
@time: 2019/4/4 13:16
@desc: Draw data with picked channels.
'''
import config
import h5py
from util import getBasePath
import numpy as np
import cv2
from dataPreprocess.geoUtil.CoordTrans import CoordTrans
import pandas as pd

class DrawAGRI(object):
    '''
    Draw data with picked channels.
    '''
    def __init__(self,datafilelist,chan_num_list,resolution,geo_range,saveIMGQuality=50):
        self._DN_VALID = [0,4095]
        self._chan_num_list = chan_num_list
        self._resolution = resolution
        self._datafilelist = datafilelist
        self._FILLVALUE_LOW = [0] * 6+ [100]*8
        self._FILLVALUE_HIGH = [1.5] * 6 + [500] * 8
        self._fillValue_high = [self._FILLVALUE_HIGH[idx] for idx in cha_num_list] # for adjusting the image colour
        self._fillValue_low = [self._FILLVALUE_LOW[idx] for idx in cha_num_list]  # for adjusting the image colour
        self._geo_range = geo_range

        self._saveIMGQuality = saveIMGQuality
        self._transformer = CoordTrans(self._resolution)

        self.load()

    def loadOneRadTempData(self,filename):
        '''
        Load the radiation temperature data of one specific HDF file.
        :param filename: A file name of HDF file.
        :return:
        '''
        H5f = h5py.File(getBasePath('data')+filename,'r')
        self._IMG_VALID_REG = H5f['NOMObsColumn'][:]

        dn_ch_list = []
        rad_temp_list = []
        lat_size,lon_size = config.IMG_SIZE[self._resolution][0],config.IMG_SIZE[self._resolution][1]

        for chan in self._chan_num_list:
            dn_ch_list.append(H5f[config.NOM_KEY_VALUE[self._resolution][chan]][:])
            rad_temp_list.append(H5f[config.CALIB_KEY_VALUE[self._resolution][chan]][:])

        for idx,(dn,rad) in enumerate(zip(dn_ch_list,rad_temp_list)):
            for lat_ind in range(lat_size):
                valid_reg_interval = self._IMG_VALID_REG[lat_ind][:]
                if valid_reg_interval[0]>-1 and valid_reg_interval[1]>-1:
                    for lon_ind in range(valid_reg_interval[0],valid_reg_interval[1]+1):
                        tmp = int(dn[lat_ind][lon_ind])
                        if tmp>=65535:
                            # dn[lat_ind][lon_ind] = self._fillValue[idx]
                            dn[lat_ind][lon_ind] = 65535
                        else:
                            dn[lat_ind][lon_ind] = rad[tmp]
                else:
                    dn[lat_ind][:] = 65535

            dn_ch_list[idx] = dn

        H5f.close()

        return dn_ch_list


    def mergeChan(self,dn_ch_list):
        # To construct RGB data, they have to be configured as a tuple of three integers in every grid.
        return np.dstack(tuple(dn_ch_list))

    def fillBlank(self,dn_ch):
        '''
        Filling the invalid data by default value, which it the maximum of dn here.
        :param dn_ch: Data need to be processed
        :return:
        '''
        for idx in range(len(dn_ch)):
            dn_ch[idx][dn_ch[idx] > self._fillValue_high[idx]] = self._fillValue_low[idx] # out of the globe
            dn_ch[idx][dn_ch[idx] < self._fillValue_low[idx]] = self._fillValue_low[idx]  # out of the globe


        return dn_ch

    def scaleDN2IMG(self,dn_ch_arr):
        '''
        Scale data from the range of DN to range of image
        :param dn_ch_arr: the reshaped dn data constructed as RGB array.
        :return: Normalized RGB data
        '''
        return cv2.normalize(dn_ch_arr,None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC3)

    def drawMap(self,filename,dn_ch_arr,ch_name):
        ''' Save extracted image file.
        :param dn_ch: the dn data of one specific channel
        '''
        tmp = filename.split('_')[9] # extract filename from raw filename
        filename = '%s%s/%s_Channel%s.jpg' % (getBasePath('img'),self._resolution,tmp, ch_name)
        img = cv2.cvtColor(dn_ch_arr, cv2.COLOR_BGR2RGB)
        cv2.imwrite(filename, img, [int(cv2.IMWRITE_JPEG_QUALITY), self._saveIMGQuality])

    def makeNameForCombinedChan(self):
        '''
        The raw dn channel of image, which is indicated as a string.
        :return: string
        '''
        chan_num = map(lambda x:'%02d'%(x+1), self._chan_num_list) # format the string of channel number.
        return ''.join(chan_num)

    def load(self):
        ch_name = self.makeNameForCombinedChan()
        for filename in self._datafilelist:
            dn_list = self.loadOneRadTempData(filename)
            dn_list = self.fillBlank(dn_list)
            dn_ch = self.mergeChan(dn_list)
            dn_ch = self.scaleDN2IMG(dn_ch)

            dn_ch = self.extractRegion(dn_ch,self._geo_range)

            self.drawMap(filename,dn_ch,ch_name)


    def extractRegion(self, rad_temp,geo_range):

        geo_range = eval(geo_range)
        if self._geo_range != geo_range:
            self._geo_range = geo_range
        lat_S, lat_N, lon_W, lon_E, step = geo_range
        lat = np.arange(lat_N, lat_S - 0.005, -step)
        lon = np.arange(lon_W, lon_E + 0.005, step)
        lon, lat = np.meshgrid(lon, lat)
        l, c = self._transformer.geo2ImgCoord(lon, lat)  # 求标称全圆盘行列号
        l = np.rint(l).astype(np.uint16)
        c = np.rint(c).astype(np.uint16)


        # DISK全圆盘数据和REGC中国区域数据区别在起始行号和终止行号
        rad_temp_extract = rad_temp[l, c]

        print(np.sum(rad_temp_extract))

        return rad_temp_extract

if __name__=='__main__':
    cha_num_list = [12,9,4] # channel 4,5,6
    datafile_list = ['FY4A-_AGRI--_N_DISK_1047E_L1-_FDI-_MULT_NOM_20180701000000_20180701001459_4000M_V0001.HDF']
    geo_range = "10, 54, 70, 140, 0.05" #lat_S, lat_N, lon_W, lon_E, step
    loader = DrawAGRI(datafile_list,cha_num_list,'4KM',geo_range)
