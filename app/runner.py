from dynaconf import settings

from client import DBClient, StockClient
from service.stock_service import StockService
from strategy.hsstock.stock_rule import StockAnalyzer, RsiRule, NotSTRule, NotDelistRule, ValidCompRule, NotDRRule, \
    RateRule

db_client = DBClient(settings.DBURL)
stock_client = StockClient(settings.STOCK.TOKEN)

stock_service = StockService(db_client, stock_client)

print(stock_service.get_all_stock_code())
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
stock_analyzer.add_rule(RsiRule(20))
stock_analyzer.add_rule(NotSTRule(stock_info))
stock_analyzer.add_rule(NotDelistRule(stock_info))
stock_analyzer.add_rule(ValidCompRule(stock_info))
stock_analyzer.add_rule(NotDRRule())
stock_analyzer.add_rule(RateRule())

stock_analyzer.analyze_all('20190601')

