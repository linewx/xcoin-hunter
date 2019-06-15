import talib
import logging

from service.stock_service import StockService


class StockAnalyzer:
    def __init__(self, stock_service: StockService):
        self.rules = []
        self.stock_service = stock_service

    def add_rule(self, rule):
        self.rules.append(rule)

    def analyze_all(self, start_date, end_date=None):
        trade_dates = self.stock_service.get_trade_daterange(start_date, end_date)
        for one_trade_date in trade_dates:
            print("\n\non date %s:" % one_trade_date)
            one_result = self.analyze_on_date(one_trade_date)
            print(one_result)

    def analyze_on_date(self, the_date):
        # prepare data
        start_date = self.stock_service.cal_trade_day(the_date, -10)
        # date_range = self.stock_service.get_trade_daterange(start_date, the_date)
        stock_data = self.stock_service.get_trade_data(start_date, the_date)

        all_stock_codes = self.stock_service.get_all_stock_code()

        results = []
        for one_ts_code in all_stock_codes:
            one_stock_data = stock_data[stock_data['ts_code'] == one_ts_code]
            if self._match_all_rules(one_ts_code, one_stock_data):
                results.append(one_ts_code)

        return results

    def _match_all_rules(self, ts_code, stock_data):
        result = True
        for one_rule in self.rules:
            result = one_rule.match(ts_code, stock_data)
            if not result:
                return False
        # print('matched')
        return result

    def analyze2(self, ts_code, stock_data, ndays):
        result = True
        change = None
        the_stock_data = stock_data
        if ndays > 0:
            the_stock_data = stock_data.iloc[:0 - ndays]

        for one_rule in self.rules:
            result = one_rule.match(ts_code, the_stock_data)
            if not result:
                return False, None
        if ndays != 0:
            change = stock_data['pct_chg'].iloc[0 - ndays]

        return result, change


class StockRule:
    def match(self, ts_code, stock_data):
        pass

    def get_name(self):
        pass


class RsiRule(StockRule):
    def __init__(self, threshold):
        self.threshold = threshold

    def match(self, ts_code, stock_data):
        if stock_data['close'].empty:
            return False

        rsi6 = talib.RSI(stock_data['close'], timeperiod=6)
        latest_rsi = rsi6.iloc[-1]

        if latest_rsi < self.threshold:
            return True
        else:
            return False

    def get_name(self):
        return 'rsi'


class NotSTRule(StockRule):
    def __init__(self, all_comp):
        self.all_st_comp = all_comp.loc[all_comp['name'].str.contains('ST')]
        self.all_st_comp_code = self.all_st_comp['ts_code'].values

    def match(self, ts_code, stock_data):
        if ts_code in self.all_st_comp_code:
            return False
        else:
            return True

    def get_name(self):
        return 'st'


class NotDelistRule(StockRule):
    def __init__(self, all_comp):
        self.all_st_comp = all_comp.loc[all_comp['name'].str.contains('退')]
        self.all_st_comp_code = self.all_st_comp['ts_code'].values

    def match(self, ts_code, stock_data):
        if ts_code in self.all_st_comp_code:
            return False
        else:
            return True

    def get_name(self):
        return 'delist'


class ValidCompRule(StockRule):
    def __init__(self, all_comp):
        self.all_comp_code = all_comp['ts_code'].values

    def match(self, ts_code, stock_data):
        if ts_code in self.all_comp_code:
            return True
        else:
            return False

    def get_name(self):
        return 'valid'


class NotDRRule(StockRule):
    def __init__(self, days=6):
        self.days = days

    # 最近是不是除权
    def match(self, ts_code, stock_data):
        previous = None
        for index, one_data in stock_data.iterrows():
            if previous is not None:
                per_change = one_data['close'] / previous
                the_pct_chg = (per_change - 1) * 100
                pct_chg = one_data['pct_chg']
                if abs(the_pct_chg - pct_chg) > 1:
                    return False
                # if per_change < 0.8 or per_change > 1.2:
                #    return False
            previous = one_data['close']
        return True

    def get_name(self):
        return 'dr'


class RateRule(StockRule):
    # 最近的增长率
    def __init__(self, rate=-6):
        self.rate = rate

    def match(self, ts_code, stock_data):
        if stock_data['pct_chg'].iloc[-1] < self.rate:
            return False

        return True

    def get_name(self):
        return 'rate'
