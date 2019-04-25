import pyecharts
import talib
import numpy as np
import tushare as ts
from pyecharts import Grid, Bar, Line, Kline, Overlap
from pypika import Query, Table, Field
from config import db
from dynaconf import settings
import time

def paint(the_data):
    prices = [oneRecord[1] for oneRecord in the_data]
    ochl_tolist = [[oneRecord[1], oneRecord[1],  oneRecord[1], oneRecord[1]] for oneRecord in the_data]
    all_dates = [time.strftime('%Y-%m-%d', time.localtime(oneRecord[0]/1000)) for oneRecord in the_data]
    #data = ts.get_k_data('399300', index=True, start='2017-01-01', end='2017-06-31')
    #ochl = data[['open', 'close', 'high', 'low']]
    #ochl_tolist = [ochl.ix[i].tolist() for i in range(len(ochl))]
    #sma_10 = talib.SMA(np.array(data['close']), 10)
    #sma_30 = talib.SMA(np.array(data['close']), 30)
    sma_5 = talib.SMA(np.array(prices), 5)
    sma_10 = talib.SMA(np.array(prices), 10)
    sma_30 = talib.SMA(np.array(prices), 30)
    sma_60 = talib.SMA(np.array(prices), 60)
    kline = Kline()
    kline.add("日K", all_dates, ochl_tolist, is_datazoom_show=True)
    line = Line()
    line.add('5 日均线', all_dates, sma_5, is_fill=False, line_opacity=0.8, is_smooth=True)
    line.add('10 日均线', all_dates, sma_10, is_fill=False, line_opacity=0.8, is_smooth=True)
    line.add('30 日均线', all_dates, sma_30, is_fill=False, line_opacity=0.8, is_smooth=True)
    line.add('60 日均线', all_dates, sma_60, is_fill=False, line_opacity=0.8, is_smooth=True)
    overlap = Overlap()
    overlap.add(kline)
    overlap.add(line)
    overlap.render()


def main():
    test_sql = "select transaction_time,us_price,code  from bdl_history order by transaction_time"
    print(db.query(test_sql))
    paint(db.query(test_sql))

if __name__ == '__main__':
    main()

