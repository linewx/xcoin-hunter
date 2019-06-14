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

    def _persist_trade_cal(self, start_date='', end_date=''):
        trade_cal = self.stock_client.get_trade_cal(start_date=start_date,
                                                    end_date=end_date)
        trade_cal.to_sql(self.trade_cal_table_name, self.db_client.get_engine(), if_exists='replace')


