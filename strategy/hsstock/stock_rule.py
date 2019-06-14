import talib


class StockAnalyzer:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def analyze(self, ts_code, stock_data):
        result = True
        for one_rule in self.rules:
            result = one_rule.match(ts_code, stock_data)
            if not result:
                return False

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
