from dynaconf import settings

from client import DBClient, StockClient
from service.stock_service import StockService

db_client = DBClient(settings.DBURL)
stock_client = StockClient(settings.STOCK.TOKEN)

stock_service = StockService(db_client, stock_client)

def init():
    stock_service._persist_basic_info()
    #stock_service._persist_trade_cal()

print(stock_service.get_all_stock_info())
