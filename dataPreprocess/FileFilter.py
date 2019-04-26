#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: FileFilter.py
@time: 2019/4/23 21:09
@desc: Filtering the files need to be processed.
'''
import pandas as pd
from util import getBasePath
import os
class FileFilter(object):
    def __init__(self):
        return

    def trackTime(self,fileName='bst_2018-2019.csv',start_time='2018-07-01'):
        '''
        Extrct the time of tracks data.
        :param fileName:
        :return:
        '''
        tracks_df = pd.read_csv('%s%s'%(getBasePath('typhoon'),fileName))

        time_list = list(tracks_df['time'].unique())
        time_list = ['%s00'%x for x in time_list]

        time_df = pd.DataFrame(data=time_list,columns=['time'])

        time_df['date'] = pd.to_datetime(time_df['time'],format='%Y%m%d%H%M%S')  # 将数据类型转换为日期类型
        time_df = time_df.set_index('date')  # 将date设置为index
        time_df = time_df['2018-07-01':]

        time_df = time_df.sort(ascending=True)

        time_df.to_csv('%stime_tracks.csv'%getBasePath('typhoon'),header=None,index=False,encoding='UTF-8')

        # time_df.groupby()

        f = open('%stime_tracks.txt'%getBasePath('typhoon'),'w',encoding='UTF-8')
        for itm in time_list:
            f.writelines(itm+'\n')
        f.close()

        return time_list

    def filterTimeofData(self,fileName):
        idx = fileName.rfind('\\')
        fileName = fileName[idx+1+44:idx+59]
        return fileName

    def getAllFilesList(self,basepath='F:\风云数据\\1KM\\1Km全圆盘数据',res='1KM'):
        # miss_list = []
        f = open("%sdir_%s.txt"%(getBasePath('typhoon'),res), "w",encoding='UTF-8')
        for root, dirs, files in os.walk(basepath):
            for file in files:
                tmp = os.path.join(root, file)
                # if tmp.endswith('.null') or tmp.endswith('hdf.td') or tmp.endswith('hdf.td.cfg'):
                #     miss_list.append(tmp)
                f.writelines(tmp + "\n")

        f.close()

        # miss_f = open('%sdir_miss%s.txt'%(getBasePath('typhoon'),res), "w",encoding='UTF-8')
        # for tmp in miss_list:
        #     tmp = tmp[tmp.rfind('\\')+1:]
        #     miss_f.writelines(tmp[48:58]+'\n')
        # miss_f.close()

    def dataTime(self,pickList,dataFilename='dir_1KM.txt',res='1KM'):
        '''
        Extract data which are observed when typhoons occur.
        :param pickList: the time interval when typhoons occur, which are concluded from tracks data.
        :param dataFilename: raw file which storing all the data file names.
        :param res: resolution
        :return:
        '''
        data_time_df = pd.read_csv('%s%s'%(getBasePath('typhoon'),dataFilename),header=None)
        data_time_df.columns=['path']

        data_time_df['names'] = data_time_df.applymap(lambda x: x[x.rfind('\\')+1:])
        data_time_df.drop(axis=1,labels=['path'],inplace=True)

        data_time_df['time'] = data_time_df.applymap(lambda x: x[44:58])
        data_time_df['date'] = pd.to_datetime(data_time_df['time'],format='%Y%m%d%H%M%S')  # 将数据类型转换为日期类型
        data_time_df = data_time_df.set_index('date')  # 将date设置为index

        data_time_df_pick = pd.DataFrame()
        for x in pickList:
            data_time_df_pick = pd.concat([data_time_df_pick,data_time_df[x[0]:x[1]]])

        print(data_time_df_pick.shape[0])

        data_time_df_pick[['names','time']].to_csv('%sdata_pick_%s.csv'%(getBasePath('typhoon'),res),index=False,header=True,encoding='utf-8')

    def pickDataByTrackTime(self,trackFilename='time_tracks.csv',dataFilename='data_pick_1KM.csv',res='1KM'):
        track_time_df = pd.read_csv('%s%s'%(getBasePath('typhoon'),trackFilename))
        track_time_df.columns = ['time']
        track_time_df.set_index('time', inplace=True)  # 将date设置为index
        track_time_df.index = pd.to_datetime(track_time_df.index, format='%Y%m%d%H%M%S')  # 将数据类型转换为日期类型

        track_time_list = list(track_time_df.index.values)

        data_time_df = pd.read_csv('%s%s'%(getBasePath('typhoon'),dataFilename))
        data_time_df.set_index('time', inplace=True)  # 将date设置为index
        data_time_df.index = pd.to_datetime(data_time_df.index,format='%Y%m%d%H%M%S')  # 将数据类型转换为日期类型


        data_match_df = pd.DataFrame()

        for idx in track_time_list:

            if idx in data_time_df.index:

                idx_int = data_time_df.index.get_loc(idx)

                data_match_df = pd.concat([data_match_df,data_time_df.iloc[idx_int]])

        print(data_match_df.shape[0])

        data_match_df.to_csv('%sdata_match_%s.csv'%(getBasePath('typhoon'),res),index=False,header=False,encoding='utf-8')



if __name__=='__main__':
    basepath_1KM = 'F:\风云数据\\1KM\\1Km全圆盘数据'
    basepath_4KM = 'F:\风云数据\\4KM'

    fileFilter = FileFilter()
    # fileFilter.getAllFilesList(basepath_1KM,'1KM')
    # fileFilter.trackTime()

    date_group_list = [
        ['2018-07-01','2018-07-12'],
        ['2018-07-16','2018-09-17'],
        ['2018-09-20', '2018-10-07'],
        ['2018-10-20', '2018-11-03'],
        ['2018-11-13', '2018-11-30'],
        ['2018-11-13', '2018-11-30'],
        ['2018-12-31', '2019-01-04'],
        ['2019-02-18', '2019-02-28'],
        ['2019-02-18', '2019-03-02']
    ]
    # fileFilter.dataTime(date_group_list,dataFilename='dir_4KM.txt',res='4KM')
    fileFilter.pickDataByTrackTime(dataFilename='data_pick_4KM.csv',res='4KM')
