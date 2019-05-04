class Runner:
    def __init__(self):
        pass

    def run(self, account_info, datasource, strategy):
        strategy.run(datasource, account_info)


