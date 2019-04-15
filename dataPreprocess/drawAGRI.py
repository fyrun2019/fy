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

class DrawAGRI(object):
    '''
    Draw data with picked channels.
    '''
    def __init__(self,datafilelist,chan_num_list,resolution,saveIMGQuality=50):
        self._DN_VALID = [0,4095]
        self._chan_num_list = chan_num_list
        self._resolution = resolution
        self._datafilelist = datafilelist
        self._fillValue = self._DN_VALID[1] # for adjusting the image colour

        self._saveIMGQuality = saveIMGQuality

        self.load()

    def loadOneDNData(self,filename):
        '''
        Load the DN data of one specific HDF file.
        :param filename: A file name of HDF file.
        :return:
        '''
        H5f = h5py.File(getBasePath('data')+filename,'r')
        dn_ch_list = []

        for chan in self._chan_num_list:
            dn_ch_list.append(H5f[config.KEY_VALUE[chan]][:])

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
            dn_ch[idx][dn_ch[idx] == 65535] = self._fillValue # out of the globe
            dn_ch[idx][dn_ch[idx] == 65534] = self._fillValue # in the globe
            dn_ch[idx][ (dn_ch[idx] < self._DN_VALID[0]) | (dn_ch[idx] > self._DN_VALID[1])] = self._fillValue

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
        cv2.imwrite(filename, dn_ch_arr, [int(cv2.IMWRITE_JPEG_QUALITY), self._saveIMGQuality])

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
            dn_list = self.loadOneDNData(filename)
            dn_list = self.fillBlank(dn_list)
            dn_ch = self.mergeChan(dn_list)
            dn_ch = self.scaleDN2IMG(dn_ch)

            self.drawMap(filename,dn_ch,ch_name)

if __name__=='__main__':
    cha_num_list = [4,3,5] # channel 4,5,6
    datafile_list = ['FY4A-_AGRI--_N_DISK_1047E_L1-_FDI-_MULT_NOM_20180701000000_20180701001459_4000M_V0001.HDF']
    loader = DrawAGRI(datafile_list,cha_num_list,'4KM')