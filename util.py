#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: util.py
@time: 2019/4/4 14:58
@desc:
'''

def getBasePath(pathType):
    filepath = "D:/Code/fy/"

    if pathType == 'data':
        return filepath+ 'data/'
    elif pathType == 'img':
        return filepath+'img/'
    elif pathType == 'typhoon':
        return filepath+'typhoon/'


    return filepath