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
    filepath = "E:/Code/Python/fy/"

    if pathType == 'data':
        return filepath+ 'data/'
    if pathType == 'img':
        return filepath+'img/'

    return filepath