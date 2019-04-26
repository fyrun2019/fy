
import config
import pandas as pd
from util import getBasePath
import numpy as np
from draw_util import draw_geo_line

def compGeoReadAndCalcu(geo_read,geo_calcu,res='4KM'):
    lat_ind, lon_ind = 0,0
    lat_size, lon_size = config.IMG_SIZE[res][0],config.IMG_SIZE[res][1]
    geo_read = geo_read[geo_read!=999]
    geo_calcu = geo_calcu[geo_calcu!=999]
    geo_diff_list = []
    lat_list = []
    print('comparation\n max_diff\tmin_diff\tavg_diff')
    while lat_ind < lat_size:

        arr_read_tmp = (geo_read.iloc[lat_ind][:]).dropna()
        arr_calcu_tmp = (geo_calcu.iloc[lat_ind][:]).dropna()

        if arr_read_tmp.size>1 and arr_calcu_tmp.size>1:
            print('%.2f\t%.2f\t%.2f' % (np.abs(np.max(arr_read_tmp) - np.max(arr_calcu_tmp)),
                                            np.abs(np.min(arr_read_tmp) - np.min(arr_calcu_tmp)),
                                            np.abs(np.average(arr_read_tmp) - np.average(arr_calcu_tmp))
                                            ))

            geo_diff_list.append(list(arr_read_tmp-arr_calcu_tmp))
            lat_list.append(list(arr_read_tmp))
        lat_ind += 1

    return lat_list,geo_diff_list

if __name__=='__main__':

    from dataPreprocess.geoUtil.CoordTrans import CoordTrans
    calculator = CoordTrans('4KM')

    l,c = calculator.geo2ImgCoord(127.6,23.7)
    print(l)
    print(c)

    calculator = CoordTrans('2KM')

    l, c = calculator.geo2ImgCoord(127.6, 23.7)
    print(l)
    print(c)

    calculator = CoordTrans('2KM')

    l, c = calculator.geo2ImgCoord(127.6, 23.7)
    print(l)
    print(c)

    # geo_read_lat = pd.read_csv('%sFullMask_Grid_%d_999_NULL_%s.csv'%(getBasePath('data'),4000,'lon'),header=0,index_col=0)
    # geo_calcu_lat = pd.read_csv('%stransFormula_IMG_2_GEO_%s_%s.csv'%(getBasePath('data'),'4KM','lon'),header=0,index_col=0)
    #
    # lat_list, geo_diff_list = compGeoReadAndCalcu(geo_read_lat,geo_calcu_lat,'4KM')
    # draw_geo_line(lat_list,geo_diff_list)