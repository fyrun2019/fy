#!/usr/bin/env python
# encoding: utf-8
'''
@author: MiaFeng
@contact: skaudrey@163.com
@file: readRaw.py
@time: 2019/4/23 11:00
@desc: Construct the typhoon data
'''
import pandas as pd
from util import getBasePath
import re
from dataPreprocess.geoUtil.CoordTrans import CoordTrans

class TyphoonTracks(object):
    def __init__(self):
        self._columns = ['time','lat','lon','tc_id','tc_name',
                         'center_press','max_sustained_wind_spd',
                         'direct_longest_rad_50kt',
                         'longest_rad_50kt','shortest_rad_50kt',
                         'direct_longest_rad_30kt',
                         'longest_rad_30kt', 'shortest_rad_30kt',
                         ]

    def splitMultiBlank(self,aStr):
        return re.compile('\s+').split(aStr.replace(" \\r\\n",'').replace("\\r\\n",''))

    def readBST_Track_file(self,fileName='bst_2018-2019.txt',saveFileName='bst_2018-2019.csv'):
        # track_df = pd.DataFrame(columns=self._columns)
        itm_list = []

        with open('%s%s'%(getBasePath('typhoon'),fileName),'rb') as f:
            while True:
                tmp = f.readline()
                if len(tmp)==0:
                    break
                aTyphoon = self.splitMultiBlank(str(tmp))
                linesNum = int(aTyphoon[2])
                aTyphoonID = aTyphoon[5]
                aTyphoonName = aTyphoon[7]
                for idx in range(linesNum):
                    aLine = self.splitMultiBlank(str(f.readline()))
                    # itm_time = f[0]
                    # lat = int(f[3]) * 0.1
                    # lon = int(f[4]) * 0.1
                    # center_press = int(f[5])
                    # max_sustained_wind_spd = int(f[6])
                    # direct_longest_rad_50kt = f[7]
                    # longest_rad_50kt = int(f[8])
                    # shortest_rad_50kt = int(f[9])
                    # direct_longest_rad_30kt = f[10]
                    # longest_rad_30kt = int(f[11])
                    # shortest_rad_30kt = int(f[12])
                    aItm = ['20%s'%aLine[0],int(aLine[3]) * 0.1,int(aLine[4]) * 0.1,aTyphoonID,aTyphoonName,
                            int(re.sub("\D", "", aLine[5])),int(re.sub("\D", "", aLine[6]))]
                    if int(re.sub("\D", "", aLine[6])) == 0:
                        aItm +=['8',0,0,'8',0,0]
                    else:
                        aItm += [aLine[7][0],
                            int(aLine[7][1:]),int(aLine[8]),
                            aLine[9][0],
                            int(aLine[9][1:]),int(aLine[10])
                            ]
                    itm_list.append(aItm)
                    if(len(aItm)!=13):
                        print(aItm)
                    # track_df.loc[df_idx] = aItm
                    # df_idx += 1
        track_df = pd.DataFrame(itm_list,columns=self._columns)
        track_df.to_csv('%s%s'%(getBasePath('typhoon'),saveFileName),index=False,header=True)

    def mergeBst_ch(self,fileName='bst_2018-2019.csv',file_ch = 'bst_ch_2018.txt'):
        data_df = pd.read_csv('%s%s'%(getBasePath('typhoon'),fileName))

        change_idx = 0
        with open('%s%s'%(getBasePath('typhoon'),file_ch),'r') as f:
            while True:
                tmp = f.readline()
                if len(tmp)==0:
                    break
                aTyphoon = self.splitMultiBlank(str(tmp))
                linesNum = int(aTyphoon[2])
                data_time_list = data_df.time.tolist()
                for idx in range(linesNum):
                    aLine = self.splitMultiBlank(str(f.readline()))
                    time = int(aLine[0])
                    lat = int(aLine[2]) * 0.1
                    lon = int(aLine[3]) * 0.1

                    if time in data_time_list:
                        idx_data_match = data_df.index[data_df['time'] == time].tolist()[0]
                        lat_data = data_df.iloc[idx_data_match]['lat']
                        lon_data = data_df.iloc[idx_data_match]['lon']

                        if lat_data != lat or lon_data!=lon:
                            data_df.ix[idx_data_match,'lat'] = lat
                            data_df.ix[idx_data_match,'lon'] = lon
                            change_idx += 1

        print(change_idx)
        data_df.to_csv('%s%s'%(getBasePath('typhoon'),fileName),index=False,header=True)

    def getIMGCoord(self,filename='bst_2018-2019.csv'):
        df = pd.read_csv('%s%s'%(getBasePath('typhoon'),filename))

        for res in ['4KM','2KM','1KM']:

            transformer = CoordTrans(res)

            def valuation_formula(x, y,type='l'):
                if type=='l':
                    return int(transformer.geo2ImgCoord(x,y)[0])
                elif type=='c':
                    return int(transformer.geo2ImgCoord(x,y)[1])


            key_l,key_c = 'l_img_%s'%res,  'c_img_%s'%res,

            df[key_l] = df.apply(lambda row: valuation_formula(row['lon'], row['lat'],'l'), axis=1)
            df[key_c] = df.apply(lambda row: valuation_formula(row['lon'], row['lat'],'c'), axis=1)


        print(df.head())

        df.to_csv('%s%s' % (getBasePath('typhoon'), filename), index=False, header=True)


if __name__=='__main__':
    loader = TyphoonTracks()
    # loader.readBST_Track_file()
    # loader.mergeBst_ch()
    loader.getIMGCoord()