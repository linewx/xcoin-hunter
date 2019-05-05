from core import OPS_BUY
import logging
import time
import pyecharts
import talib
import numpy as np
import tushare as ts
from pyecharts import Grid, Bar, Line, Kline, Overlap


class DailyRunner:
    def __init__(self):
        pass

    def run(self, account_info, datasource, strategy):
        current_history_data = []
        for one_day_data in datasource:
            trans_time = one_day_data.get('transaction_time')
            current_history_data.append(one_day_data)
            if OPS_BUY == self.run_one_day(account_info, current_history_data, strategy, trans_time)[0]:
                logging.error("buy BTC at %s %d" % (
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(trans_time / 1000)), trans_time))

    def run_one_day(self, account_info, datasource, strategy, transaction_time):
        return strategy.run(datasource, account_info)

    def draw(self, data):
        #data = ts.get_k_data('399300', index=True, start='2017-01-01', end='2017-06-31')
        ochl = data[['open', 'close', 'high', 'low']]
        ochl_tolist = [ochl.ix[i].tolist() for i in range(len(ochl))]
        sma_5 = talib.SMA(np.array(data['close']), 5)
        sma_10 = talib.SMA(np.array(data['close']), 10)
        sma_30 = talib.SMA(np.array(data['close']), 30)
        sma_60 = talib.SMA(np.array(data['close']), 60)
        kline = Kline()
        kline.add("日K", data['date'], ochl_tolist, is_datazoom_show=True)
        line = Line()
        line.add('5 日均线', data['date'], sma_5, is_fill=False, line_opacity=0.8, is_smooth=True)
        line.add('10 日均线', data['date'], sma_10, is_fill=False, line_opacity=0.8, is_smooth=True)
        line.add('30 日均线', data['date'], sma_30, is_fill=False, line_opacity=0.8, is_smooth=True)
        line.add('60 日均线', data['date'], sma_60, is_fill=False, line_opacity=0.8, is_smooth=True)
        overlap = Overlap()
        overlap.add(kline)
        overlap.add(line)
        overlap.render()
