#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: draw_util.py
@time: 2019/4/22 14:59
@desc:
'''
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()
def draw_geo_line(lat_list,lon_list):
    plt.figure()
    for idx,(x,y) in enumerate(zip(lat_list,lon_list)):
        plt.plot(x,y)

    plt.xlabel('lat')
    plt.ylabel('lon_diff')
    plt.show()