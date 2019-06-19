from strategy.hsstock.stock_rule import StockAnalyzer, BreakthroughUpRule, BreakthroughRule2, BreakthroughGeneralRule, \
    TurnoverRule, KlineShapeRule1
from app.context import stock_service


stock_analyzer = StockAnalyzer(stock_service, 2)

stock_analyzer.add_rule(KlineShapeRule1())
stock_analyzer.backtest('20190601')



