import numpy as np
import talib

from core import *


class AvgStrategy:
    '''
    均值策略：5日均线在短期内突破,单一币种策略
    '''

    def run(self, data, account_info):
        '''
        :param data: 目前为止的交易数据
        :param account: 当前账户情况
        :return: 买入还是卖出还是保持不变
        '''
        if OPS_BUY == self.buy_or_sell(account_info):
            return self.buy_or_not(data, account_info)
        else:
            return self.sell_or_not(data, account_info)

    def buy_or_sell(self, account_info):
        '''
        根据现有账户的币的数量判断现在是买入还是卖出周期
        :return:
        '''
        the_mvc = account_info.mvc()
        if the_mvc == STD_COIN:
            # 如果账户里主要是标准货币，就是买入周期
            return OPS_BUY
        else:
            # 卖出周期
            return OPS_SELL

    def buy_or_not(self, data, context):
        '''
        如果5日均线穿过其他均线的情况
        :param data:
        :return:
        '''
        converted_data = np.array([x.get('price') for x in data])
        if len(converted_data) < 60:
            return OPS_SELL

        ma5 = talib.SMA(converted_data, 5)
        ma10 = talib.SMA(converted_data, 10)
        ma30 = talib.SMA(converted_data, 30)
        ma60 = talib.SMA(converted_data, 60)

        today_order = self.get_order(ma5[-1], [ma5[-1], ma10[-1], ma30[-1], ma60[-1]])
        yesterday_order = self.get_order(ma5[-2], [ma5[-2], ma10[-2], ma30[-2], ma60[-2]])

        if today_order == 1 and yesterday_order != 1:
            return OPS_BUY, 'all'
        else:
            return OPS_KEEP

    def sell_or_not(self, data, account_info):
        # todo: 更好的抛售策略
        return OPS_KEEP

        if (data[-1].transaction_time - account_info.latest_transaction_time) > 3600 * 24 * 2:
            # 超过两天，就抛售
            return OPS_SELL
        else:
            return OPS_KEEP

    def get_order(self, target, all_data):
        result = 1
        for one_data in all_data:
            if one_data > target:
                result = result + 1

        return result


if __name__ == '__main__':
    pass
