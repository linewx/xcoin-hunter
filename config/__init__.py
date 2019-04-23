from .db import DBConnection
from dynaconf import settings
# db = DBConnection("mysql+pymysql://root:root@localhost:3306/coin")
db = DBConnection(settings.DBURL)