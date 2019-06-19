from strategy.hsstock.stock_rule import StockAnalyzer, BreakthroughUpRule, BreakthroughRule2, BreakthroughGeneralRule, \
    TurnoverRule
from app.context import stock_service

print(stock_service.get_trade_data('20190606', '20190606')['close'])

# stock_analyzer = StockAnalyzer(stock_service)
#
# stock_info = stock_service.get_all_stock_info()
# stock_analyzer.add_rule(TurnoverRule(threashold=30, torlerence=0, break_degree=0.93, field='turnover_rate_f', field_range=(0, 1.0), amplitude=None))
# stock_analyzer.backtest('20190614')



