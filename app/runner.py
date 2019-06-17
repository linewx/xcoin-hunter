from strategy.hsstock.stock_rule import StockAnalyzer, BreakthroughUpRule
from app.context import stock_service

stock_analyzer = StockAnalyzer(stock_service)

stock_info = stock_service.get_all_stock_info()
stock_analyzer.add_rule(BreakthroughUpRule(amplitude=15))
stock_service.preload_data()
stock_analyzer.backtest('20190601', '20190631')



