from datasource.cc import CryptoCompareSource

def main():
    cc = CryptoCompareSource()
    return cc.get_history_data('BTC', 'USD').json()

if __name__ == '__main__':
    result = main()
    print(result)