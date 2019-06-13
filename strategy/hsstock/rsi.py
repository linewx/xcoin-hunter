import tushare as ts
import datetime
from datetime import time
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:root@localhost/coin")


def main():
    token = 'aa4223d759e37de759513fca3a7c2edf86fb60f521f91b183a05f8bd'
    ts.set_token(token)
    tsapi = ts.pro_api()


def get_tran_dates_from_db():
    query_results = engine.execute("select DISTINCT trade_date from coin").fetchall()
    trans_dates = list(map(lambda x: x[0], query_results))
    return trans_dates


def previous_days(days: int):
    results = []
    today = datetime.date.today()
    for delta in range(0, days):
        ndays_ago = today - datetime.timedelta(days=delta)
        one_day = ndays_ago.strftime("%Y%m%d")
        results.append(one_day)
    return results


if __name__ == '__main__':
    print(previous_days(20))
    # print(get_tran_dates_from_db())
