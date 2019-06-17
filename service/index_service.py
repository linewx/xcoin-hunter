import datetime

from client import StockClient, DBClient
import pandas as pd

from client.index_client import IndexClient, Market


def get_today():
    return datetime.datetime.today().strftime("%Y%m%d")


class IndexService:
    def __init__(self, db_client: DBClient, index_client: IndexClient):
        self.db_client = db_client
        self.index_client = index_client

        ##### table name #####
        self.basic_info_table_name = 'index_basic_info'  # 企业基础信息表

        self.index_basic_info = None

    def _persist_basic_info(self):
        result = None
        for one_market in Market.__members__:
            if result is None:
                result = self.index_client.get_basic_info(one_market)
            else:
                result = result.append(self.index_client.get_basic_info(one_market))

        result.to_sql(self.basic_info_table_name, self.db_client.get_engine(), if_exists='replace')

    def get_daily_info(self, ts_code, trade_date=None, start_date=None, end_date=None):
        return self.index_client.get_daily_info(ts_code, trade_date, start_date, end_date)
