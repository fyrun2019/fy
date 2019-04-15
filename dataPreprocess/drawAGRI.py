#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: drawAGRI.py
@time: 2019/4/4 13:16
@desc:
'''
import config
import h5py
from util import getBasePath
import numpy as np
datafile = 'FY4A-_AGRI--_N_DISK_1047E_L1-_FDI-_MULT_NOM_20180701000000_20180701001459_4000M_V0001.HDF'

import cv2

class DrawAGRI(object):

    def __init__(self,datafilelist,chan_num_list,resolution):
        self._DN_VALID = [0,4095]
        self._chan_num_list = chan_num_list
        self._resolution = resolution
        self._datafilelist = datafilelist
        self._fillValue = self._DN_VALID[1]

        self.load()

    def loadOneDNData(self,filename):
        H5f = h5py.File(getBasePath('data')+filename,'r')
        dn_ch_list = []

        for chan in self._chan_num_list:
            dn_ch_list.append(H5f[config.KEY_VALUE[chan]][:])

        H5f.close()

        return dn_ch_list


    def mergeChan(self,dn_ch_list):
        # Caution: The data have to be configured as a tuple of three integers in every grid.
        return np.dstack(tuple(dn_ch_list))

    def fillBlank(self,dn_ch):
        for idx in range(len(dn_ch)):
            dn_ch[idx][dn_ch[idx] == 65535] = self._fillValue # out of the globe
            dn_ch[idx][dn_ch[idx] == 65534] = self._fillValue # in the globe
            dn_ch[idx][ (dn_ch[idx] < self._DN_VALID[0]) | (dn_ch[idx] > self._DN_VALID[1])] = self._fillValue

        return dn_ch

    def scaleDN2IMG(self,dn_ch_arr):
        return cv2.normalize(dn_ch_arr,None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC3)

    def drawMap(self,filename,dn_ch_arr,ch_name):
        '''
        :param dn_ch: the dn data of one specific channel
        :return:
        '''
        tmp = filename.split('_')[9]
        filename = '%s%s_Channel%s.jpg' % (getBasePath('data'),tmp, ch_name)
        cv2.imwrite(filename, dn_ch_arr, [int(cv2.IMWRITE_JPEG_QUALITY), 50])

    def makeNameForCombinedChan(self):
        chan_num = map(lambda x:'%02d'%(x+1), self._chan_num_list)
        return ''.join(chan_num)

    def load(self):
        ch_name = self.makeNameForCombinedChan()
        for filename in self._datafilelist:
            dn_list = self.loadOneDNData(filename)
            dn_list = self.fillBlank(dn_list)
            dn_ch = self.mergeChan(dn_list)
            dn_ch = self.scaleDN2IMG(dn_ch)

            self.drawMap(filename,dn_ch,ch_name)

if __name__=='__main__':
    cha_num_list = [4,3,5] # channel 4,5,6
    datafile_list = ['FY4A-_AGRI--_N_DISK_1047E_L1-_FDI-_MULT_NOM_20180701000000_20180701001459_4000M_V0001.HDF']
    loader = DrawAGRI(datafile_list,cha_num_list,'4KM')