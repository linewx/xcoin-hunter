from core.expenseline import ExpenseLine
import logging


class AccountInfo:
    '''
        账号信息
        USDT为默认稳定的交换货币
    '''

    def __init__(self):
        self.account = {}
        self.expenseLines = ExpenseLine()

    def exchange(self, pair1, pair2, price, amount, operation, transaction_time):
        '''

        :param pair1: 交易对中的源货币
        :param pair2: 交易对中的目标货币
        :param price: 交易价格
        :param amount:交易金额
        :param operation:买入还是卖出
        :param transaction_time: 交易时间
        :return:
        '''

        if pair1 not in self.account:
            self.account[pair1] = 0

        if pair2 not in self.account:
            self.account[pair2] = 0

        if operation == 'buy':
            self.account[pair1] = self.account[pair1] + amount
            self.account[pair2] = self.account[pair2] - (amount * price)

        elif operation == 'sell':
            self.account[pair1] = self.account[pair1] - amount
            self.account[pair2] = self.account[pair2] + (amount * price)
        else:
            raise Exception("unsupported operation for %s" % operation)
        try:
            self.validate(pair1)
            self.validate(pair2)
        except Exception as e:
            logging.exception(e)

        self.expenseLines.add(pair1, pair2, price, amount, operation, transaction_time)

    def validate(self, coin):
        if self.account[coin] < 0:
            raise Exception("the account for %s is Overdraft" % coin)
