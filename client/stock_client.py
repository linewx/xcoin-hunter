import tushare as ts


class StockClient:
    def __init__(self, token=None):
        self.ts_client = ts.pro_api(token)

    def get_basic_info(self, exchange='', status='L', fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs'):
        data = self.ts_client.stock_basic(exchange=exchange, list_status=status, fields=fields)
        return data

    def get_trade_cal(self, start_date='', end_date=''):
        return self.ts_client.trade_cal(start_date=start_date, end_date=end_date)

    def get_daily_info(self, trade_date=''):
        return self.ts_client.daily(trade_date=trade_date)

    def get_daily_index_info(self, trade_date=''):
        return self.ts_client.daily_basic(trade_date=trade_date)




