import datetime

import pandas as pd
import talib
import tushare as ts

from config import DBConnection
from strategy.hsstock.stock_rule import StockAnalyzer, RsiRule, NotSTRule, NotDelistRule, ValidCompRule, NotDRRule, \
    RateRule


class HSStock:
    def __init__(self):
        self.db = DBConnection("mysql+pymysql://root:root@localhost/coin")
        token = 'aa4223d759e37de759513fca3a7c2edf86fb60f521f91b183a05f8bd'
        ts.set_token(token)
        self.tsapi = ts.pro_api()
        self.history_table_name = 'hs_stock_history'
        self.basic_info_table_name = 'hs_company_basic_info'

    def get_tran_dates_from_db(self):
        query_results = self.db.query("select DISTINCT trade_date from coin")
        trans_dates = list(map(lambda x: x[0], query_results))
        return trans_dates

    def previous_days(self, days: int):
        results = []
        today = datetime.date.today()
        for delta in range(0, days):
            ndays_ago = today - datetime.timedelta(days=delta)
            one_day = ndays_ago.strftime("%Y%m%d")
            results.append(one_day)
        return results

    def get_trade_data_by_date(self, trade_date):
        # step1: try from database
        results = pd.read_sql("select * from %s where trade_date = %s" % (self.history_table_name, trade_date),
                              self.db.get_engine())
        if results.empty:
            # step2: try from tushare
            results = self.tsapi.daily(trade_date=trade_date)
            if not results.empty:
                results.to_sql(self.history_table_name, self.db.get_engine(), if_exists='append')
        return results

    def save_comp_basic_info(self):
        results = self.tsapi.stock_basic(exchange='', fields='ts_code,symbol,name,area,industry,list_date')
        results = self.tsapi.stock_basic(exchange='', list_status='L',
                                         fields='ts_code,symbol,name,area,industry,list_date')
        results.to_sql(self.basic_info_table_name, self.db.get_engine(), if_exists='replace')

    def get_all_comp_basic_info(self):
        results = pd.read_sql("select * from %s" % self.basic_info_table_name, self.db.get_engine())
        return results


def main():
    stock = HSStock()
    all_comp = stock.get_all_comp_basic_info()

    stock_analyzer = StockAnalyzer()

    stock_analyzer.add_rule(RsiRule(20))
    stock_analyzer.add_rule(NotSTRule(all_comp))
    stock_analyzer.add_rule(NotDelistRule(all_comp))
    stock_analyzer.add_rule(ValidCompRule(all_comp))
    stock_analyzer.add_rule(NotDRRule())
    stock_analyzer.add_rule(RateRule())

    stock = HSStock()
    all_days = (stock.previous_days(30))
    result = None
    for one_day in all_days:
        one_day_result = stock.get_trade_data_by_date(one_day)
        if result is None:
            result = one_day_result
        else:
            result = result.append(one_day_result)

    all_codes = result['ts_code'].unique()
    for one_code in all_codes:
        one_stock = result.loc[lambda df: df['ts_code'] == one_code].sort_values('trade_date')
        if stock_analyzer.analyze(one_code, one_stock):
            print(one_code)


def store_comp_basic_info():
    stock = HSStock()
    stock.save_comp_basic_info()


if __name__ == '__main__':
    main()
