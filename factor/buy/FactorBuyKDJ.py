# -*- encoding:utf-8 -*-
"""
    买入择时示例因子：突破买入择时因子
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
import talib as ta
from abupy.FactorBuyBu import AbuFactorBuyBase, AbuFactorBuyXD, BuyCallMixin, BuyPutMixin
from stockstats import StockDataFrame

__author__ = '阿布'
__weixin__ = 'abu_quant'


# noinspection PyAttributeOutsideInit
class FactorBuyKDJ(AbuFactorBuyXD, BuyCallMixin):
    """示例正向突破买入择时类，混入BuyCallMixin，即向上突破触发买入event"""

    def _init_self(self, **kwargs):
        """kwargs中必须包含: 突破参数xd 比如20，30，40天...突破"""
        # 突破参数 xd， 比如20，30，40天...突破, 不要使用kwargs.pop('xd', 20), 明确需要参数xq
        self.xd = kwargs['xd']
        # 在输出生成的orders_pd中显示的名字
        self.factor_name = '{}:{}'.format(self.__class__.__name__, self.xd)

    def fit_day(self, today):
        """
        针对每一个交易日拟合买入交易策略，寻找向上突破买入机会
        :param today: 当前驱动的交易日金融时间序列数据
        :return:
        """
        # 忽略不符合买入的天（统计周期内前xd天）
        if self.today_ind < self.xd - 1:
            return None


        xd_kl = self.kl_pd[self.today_ind - self.xd + 1:self.today_ind + 1]
        stock = StockDataFrame.retype(xd_kl)
        k = stock['kdjk'][today.date]
        d = stock['kdjd'][today.date]
        j = stock['kdjj'][today.date]

        rsi_12 = stock['rsi_6'][today.date]

        #if k < 10 and d < 10 and j < 10:
        # if rsi_12 < 20:
        #     print('###############')
        #     print(today.date)
        #     return self.buy_tomorrow()

        if today.date == 20181203.0:
            rsi_6 = stock['rsi_6'][today.date]
            rsi_12 = stock['rsi_12'][today.date]
            print("the date: %f, rsi6: %f, rsi_12: %f" % (today.date, rsi_6, rsi_12))

        return None
