from enum import Enum

import tushare as ts


#
# 市场代码	说明
# MSCI	MSCI指数
# CSI	中证指数
# SSE	上交所指数
# SZSE	深交所指数
# CICC	中金所指数
# SW	申万指数
# OTH	其他指数
class Market(Enum):
    MSCI = 'MSCI'
    CSI = 'CSI'
    SSE = 'SSE'
    SZSE = 'SZSE'
    CICC = 'CICC'
    SW = 'SW'
    OTH = 'OTH'


class IndexClient:
    def __init__(self, token=None):
        self.ts_client = ts.pro_api(token)

    def get_basic_info(self, market):
        data = self.ts_client.index_basic(market = market)
        return data

    def get_daily_info(self, ts_code, trade_date=None, start_date=None, end_date=None):
        return self.ts_client.index_daily(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)

