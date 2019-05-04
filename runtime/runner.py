from core import OPS_BUY
import logging
import time


class DailyRunner:
    def __init__(self):
        pass

    def run(self, account_info, datasource, strategy):
        current_history_data = []
        for one_day_data in datasource:
            trans_time = one_day_data.get('transaction_time')
            current_history_data.append(one_day_data)
            if OPS_BUY == self.run_one_day(account_info, current_history_data, strategy, trans_time)[0]:
                logging.error("buy BTC at %s %d" % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(trans_time/1000)), trans_time)   )

    def run_one_day(self, account_info, datasource, strategy, transaction_time):
        return strategy.run(datasource, account_info)
