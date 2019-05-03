import talib
import time
import numpy as np
class AvgIndicator:
    def calculate(self, the_data):
        close_data = [one_record.open for one_record in the_data]
        sma_5 = talib.SMA(np.array(close_data), 5)
        sma_10 = talib.SMA(np.array(close_data), 10)
        sma_30 = talib.SMA(np.array(close_data), 30)
        sma_60 = talib.SMA(np.array(close_data), 60)


        results = []
        for index in range(0, len(sma_5)):
            rank = 0
            if sma_5[index] > sma_10[index]:
                rank = rank + 1
            if sma_5[index] > sma_30[index]:
                rank = rank + 1
            if sma_5[index] > sma_60[index]:
                    rank = rank + 1
            results.append(rank)

        rank_results = [0]

        for index in range(1, len(results)):
            rank_results.append(results[index] - results[index-1])
        print(results)
        print(rank_results)
        print(rank_results.index(max(rank_results)))

        print(rank_results[83])
        print(the_data[83].transactionTime)
        print(np.where(np.array(rank_results) == max(rank_results)))
        for one_index in np.where(np.array(rank_results)== max(rank_results))[0]:
            the_time = the_data[one_index].transactionTime
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(the_time)))






    '''
    import pyecharts
import talib
import numpy as np
import tushare as ts
from pyecharts import Grid, Bar, Line, Kline, Overlap
data = ts.get_k_data('399300', index=True, start='2017-01-01', end='2017-06-31')
ochl = data[['open', 'close', 'high', 'low']]
ochl_tolist = [ochl.ix[i].tolist() for i in range(len(ochl))]
sma_10 = talib.SMA(np.array(data['close']), 10)
sma_30 = talib.SMA(np.array(data['close']), 30)
kline = Kline()
kline.add("日K", data['date'], ochl_tolist, is_datazoom_show=True)
line = Line()
line.add('10 日均线', data['date'], sma_10, is_fill=False, line_opacity=0.8, is_smooth=True)
line.add('30 日均线', data['date'], sma_30, is_fill=False, line_opacity=0.8, is_smooth=True)
overlap = Overlap()
overlap.add(kline)
overlap.add(line)
overlap.render()


# from pyecharts import Bar,Line,Overlap
# #overlap将多张图表整合到一个画板上
# #绘制柱状图
# hero = ['鲁班','妲己','程咬金','后裔']
# death_times = [1200,600,90,1000]
#
# myBar = Bar("王者荣耀英雄死亡次数")
# myBar.add("",hero,death_times)
# myBar.render()
    '''

if __name__ == '__main__':
    from datasource.cc import CryptoCompareSource

    cc = CryptoCompareSource()
    query_result = cc.get_data()
    AvgIndicator().calculate(query_result)
