import requests

from config import Session
from config.entity import CCHistory


## coin client
class CryptoCompareSource:
    url = "https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=USD&allData=true"

    def get_history_data(self, fsym, tsym, allData='true'):
        params = {
            'fsym': fsym,
            'tsym': tsym,
            'allData': allData
        }
        return requests.get("https://min-api.cryptocompare.com/data/histoday", params).json()

    def sync_history_data(self, fsym, tsym):
        '''
        get history data and save into daetabase
        :return:
        '''
        history_data = self.get_history_data(fsym, tsym).get('Data')
        session = Session()
        for one_record in history_data:
            one_record['transactionTime'] = one_record.pop('time')
            one_record['volumeFrom'] = one_record.pop('volumefrom')
            one_record['volumeTo'] = one_record.pop('volumeto')

            one_record['pair1'] = fsym
            one_record['pair2'] = tsym
            session.add(CCHistory(**one_record))
        session.commit()

    def get_data(self):
        session = Session()
        query = session.query(CCHistory).order_by(CCHistory.transactionTime)
        return query.all()


if __name__ == '__main__':
    cc = CryptoCompareSource()
    cc.sync_history_data("BTC", "USD")
