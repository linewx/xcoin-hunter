import datetime

from client import StockClient, DBClient
import pandas as pd


class StockService:
    def __init__(self, db_client: DBClient, stock_client: StockClient):
        self.db_client = db_client
        self.stock_client = stock_client

        ##### table name #####
        self.history_table_name = 'stock_history'  # 历史行情表
        self.basic_info_table_name = 'stock_basic_info'  # 企业基础信息表
        self.trade_cal_table_name = 'stock_trade_cal'

        self.trade_cal = None
        self.stock_info = None
        self.all_stock_info = None

    def _persist_trade_cal(self, start_date='', end_date=''):
        trade_cal = self.stock_client.get_trade_cal(start_date=start_date,
                                                    end_date=end_date)
        trade_cal.to_sql(self.trade_cal_table_name,
                         self.db_client.get_engine(),
                         if_exists='replace')

    def _persist_basic_info(self):
        all_basic_info = self.stock_client.get_basic_info()
        all_basic_info.to_sql(self.basic_info_table_name,
                              self.db_client.get_engine(),
                              if_exists='replace')

    def get_all_stock_info(self):
        if self.all_stock_info is None:
            self.all_stock_info = pd.read_sql_table(self.basic_info_table_name, self.db_client.get_engine())
        return self.all_stock_info

    def get_all_trade_cal(self):
        if self.trade_cal is None:
            self.trade_cal = pd.read_sql_table(self.trade_cal_table_name, self.db_client.get_engine())
        return self.trade_cal

    def is_trade_date(self, the_date):
        all_trade_cal = self.get_all_trade_cal()
        return all_trade_cal.loc[all_trade_cal.cal_date == the_date]['is_open'].iloc[0]

    def get_trade_data_by_date(self, trade_date=None):
        if trade_date is None:
            today = datetime.date.today()
            trade_date = today.strftime("%Y%m%d")
        # step1: try from database
        results = pd.read_sql("select * from %s where trade_date = %s" % (self.history_table_name, trade_date),
                              self.db_client.get_engine())
        if results.empty:
            # step2: try from tushare
            results = self.stock_client.get_daily_info(trade_date=trade_date)
            if not results.empty:
                results.to_sql(self.history_table_name, self.db_client.get_engine(), if_exists='append')
        return results
