from __future__ import print_function
from __future__ import division
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#%matplotlib inline
import os
import sys
# 使用insert 0即只使用github，避免交叉使用了pip安装的abupy，导致的版本不一致问题
sys.path.insert(0, os.path.abspath('../'))
import abupy
# 使用沙盒数据，目的是和书中一样的数据环境
#abupy.env.enable_example_env_ipython()
abupy.env.disable_example_env_ipython()
from abupy import AbuFactorBuyBreak, AbuFactorSellBreak
from factor.buy import FactorBuyKDJ

# buy_factors 60日向上突破，42日向上突破两个因子
buy_factors = [{'xd': 14, 'class': FactorBuyKDJ}]
# 使用120天向下突破为卖出信号
sell_factor1 = {'xd': 120, 'class': AbuFactorSellBreak}
from abupy import AbuFactorAtrNStop
from abupy import ABuPickTimeExecute, AbuBenchmark, AbuCapital

# 趋势跟踪策略止盈要大于止损设置值，这里0.5，3.0
# sell_factor2 = {'stop_loss_n': 0.5, 'stop_win_n': 3.0,
#                 'class': AbuFactorAtrNStop}

# 两个卖出因子策略并行同时生效
sell_factors = [sell_factor1]
benchmark = AbuBenchmark()
capital = AbuCapital(1000000, benchmark)
orders_pd, action_pd, _ = ABuPickTimeExecute.do_symbols_with_same_factors(['002230'],
                                                                          benchmark,
                                                                          buy_factors,
                                                                          sell_factors,
                                                                          capital, show=True)
