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

keyDict = ['NOMChannel01','NOMChannel02','NOMChannel03']
DN_VALID = [0,4095]

import cv2
def loadData():
    H5f = h5py.File(getBasePath('data')+datafile,'r')
    print(H5f.keys())

    dn_chan01 = H5f[keyDict[0]][:]
    dn_chan02 = H5f[keyDict[1]][:]
    dn_chan03 = H5f[keyDict[2]][:]

    H5f.close()

    return dn_chan01,dn_chan02,dn_chan03

def mergeChan(dn_ch01,dn_ch02,dn_ch03,resolution):
    # Caution: The data have to be configured as a tuple of three integers in every grid.
    return np.dstack((dn_ch01,dn_ch02,dn_ch03))

def fillBlank(dn_ch,fillValue = 0):
    dn_ch[dn_ch==65535] = fillValue # out of the globe
    dn_ch[dn_ch == 65534] = fillValue # in the globe

    dn_ch[ (dn_ch<DN_VALID[0]) | (dn_ch>DN_VALID[1])] = fillValue

    return dn_ch

def scale(dn_ch):
    return cv2.normalize(dn_ch,None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC3)

def drawMap(dn_ch,ch_name):
    '''

    :param dn_ch: the dn data of one specific channel
    :return:
    '''

    # cv2.imshow("merge channel 01,02,03", dn_ch)
    filename = '%sChannel%s.jpg' % (getBasePath('data'), ch_name)
    print(filename)
    cv2.imwrite(filename, dn_ch, [int(cv2.IMWRITE_JPEG_QUALITY), 50])

if __name__=='__main__':
    dn_chan01, dn_chan02, dn_chan03 = loadData()
    dn_chan01, dn_chan02, dn_chan03 = fillBlank(dn_chan01, 4095),fillBlank(dn_chan02, 4095),fillBlank(dn_chan03, 4095)
    dn_ch = mergeChan(dn_chan03,dn_chan02,dn_chan01,'4KM')
    dn_ch = scale(dn_ch)
    drawMap(dn_ch,'030201')


