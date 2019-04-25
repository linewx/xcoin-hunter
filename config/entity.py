from dynaconf import settings
from sqlalchemy import Column
from sqlalchemy import Integer, String, Float, Date
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CCHistory(Base):
    __tablename__ = 'cc_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    transactionTime = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    open = Column(Float)
    volumeFrom = Column(Float)
    volumeTo = Column(Float)
    pair1 = Column(String(5))
    pair2 = Column(String(5))
    updateTime = Column(Date)
    insertTime = Column(Date)


if __name__ == '__main__':
    engine = create_engine(settings.DBURL)
    Base.metadata.create_all(bind=engine)