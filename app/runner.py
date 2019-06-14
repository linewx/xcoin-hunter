from dynaconf import settings

from client import DBClient, StockClient
from service.stock_service import StockService

db_client = DBClient(settings.DBURL)
stock_client = StockClient(settings.STOCK.TOKEN)

stock_service = StockService(db_client, stock_client)

stock_service._persist_trade_cal()
