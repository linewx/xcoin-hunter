import uuid


class ExpenseLine:
    def __init__(self):
        self.expense_lines = []

    def add(self, pair1, pair2, price, amount, operation, transaction_time):
        trans_id = uuid.uuid1()
        ops1 = '买入'
        ops2 = '支持'

        if operation == 'sell':
            ops1 = '支持'
            ops2 = '买入'

        expense_line1 = {
            'coin': pair1,
            'amount': amount,
            'operation': ops1,
            'transaction_time': transaction_time,
            "transaction_id": trans_id
        }

        expense_line2 = {
            'coin': pair2,
            'amount': amount * price,
            'operation': ops2,
            'transaction_time': transaction_time,
            "transaction_id": trans_id
        }

        self.expense_lines.append(expense_line1)
        self.expense_lines.append(expense_line2)
