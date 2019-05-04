from config import db
from core.account import AccountInfo
from runtime.runner import DailyRunner
from strategy.avg_stratey import AvgStrategy


def get_btc_data():
    the_data = db.query(
        "select 'BTC', 'USDT', us_price,transaction_time from fxh_history where code='bitcoin' order by transaction_time")
    return [{'pair1': x[0], 'pair2': x[1], 'price': x[2], 'transaction_time': x[3]} for x in the_data]


def main():
    runner = DailyRunner()
    account_info = AccountInfo()
    account_info.charge("USDT", 10000)

    runner.run(account_info, get_btc_data(), AvgStrategy())


if __name__ == '__main__':
    main()
