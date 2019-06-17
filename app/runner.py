import datetime

from dynaconf import settings

from client import DBClient, StockClient
from client.index_client import IndexClient
from service.index_service import IndexService
from service.stock_service import StockService
from strategy.hsstock.stock_rule import StockAnalyzer, RsiRule, NotSTRule, NotDelistRule, ValidCompRule, NotDRRule, \
    RateRule, DecreaseRateRule, BreakthroughRule, BreakthroughRule2, BreakthroughRule3

db_client = DBClient(settings.DBURL)
stock_client = StockClient(settings.STOCK.TOKEN)
index_client = IndexClient(settings.STOCK.TOKEN)

stock_service = StockService(db_client, stock_client)
index_service = IndexService(db_client, index_client)
# def init():
#     stock_service._persist_basic_info()
#     # stock_service._persist_trade_cal()
#
#
# #print(stock_service.get_trade_data('20190331'))
# #print(stock_service.get_trade_daterange('20190331'))
# #print(stock_service.cal_trade_day('20190401', 0))
# print(stock_service.get_trade_data('20190403'))

stock_analyzer = StockAnalyzer(stock_service)

stock_info = stock_service.get_all_stock_info()
# stock_analyzer.add_rule(RsiRule(20))
# stock_analyzer.add_rule(BreakthroughRule())
# stock_analyzer.add_rule(NotSTRule(stock_info))
# stock_analyzer.add_rule(NotDelistRule(stock_info))
# stock_analyzer.add_rule(ValidCompRule(stock_info))
# stock_analyzer.add_rule(NotDRRule())
# stock_analyzer.add_rule(RateRule())
# stock_analyzer.add_rule(DecreaseRateRule())

#stock_analyzer.add_rule(BreakthroughRule2(60, 2, 0.6))
#$stock_analyzer.add_rule(BreakthroughRule3())
#stock_analyzer.add_rule(BreakthroughRule3(threashold=30, torlerence=2, break_degree=0.96, field='high', amplitude=20))
stock_analyzer.add_rule(BreakthroughRule3(amplitude=15))
start_time = datetime.datetime.now()
stock_service.preload_data()
stock_analyzer.backtest('20190401', '20190430')
print(datetime.datetime.now() - start_time)




