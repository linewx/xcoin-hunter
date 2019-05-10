import time

import pandas as pd

from config import db
from core.account import AccountInfo
from runtime.runner import DailyRunner
from strategy.avg_strategy import AvgStrategy


def get_btc_data():
    the_data = db.query(
        "select 'BTC', 'USDT', us_price,transaction_time from fxh_history where code='bitcoin' order by transaction_time")
    return [{'pair1': x[0], 'pair2': x[1], 'price': x[2], 'transaction_time': x[3]} for x in the_data]


def get_btc_data2():
    origin_data = db.query(
        "select 'BTC', 'USDT', us_price, us_price, us_price, us_price, transaction_time from fxh_history where code='bitcoin' order by transaction_time"
    )

    data = pd.DataFrame(data=origin_data, columns=('pair1', 'pair2', 'open', 'close', 'high', 'low', 'trans_time'),
                        index=range(0, len(origin_data)))

    trans_time = data['trans_time']
    data['date'] = (trans_time.transform(lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x/1000))))
    #print(trans_time)
    return data


def main():
    runner = DailyRunner()
    account_info = AccountInfo()
    account_info.charge("USDT", 10000)

    runner.run(account_info, get_btc_data(), AvgStrategy())
    runner.draw(get_btc_data2())


if __name__ == '__main__':
    main()
