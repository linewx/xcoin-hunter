from dynaconf import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .db import DBConnection

# db = DBConnection("mysql+pymysql://root:root@localhost:3306/coin")
db = DBConnection(settings.DBURL)

engine = create_engine(settings.DBURL)
Session = sessionmaker()
Session.configure(bind=engine)
