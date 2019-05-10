import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from catalyst import run_algorithm
from catalyst.api import (record, symbol, order_target_percent, )
from catalyst.exchange.utils.stats_utils import extract_transactions
from logbook import Logger

NAMESPACE = 'dual_moving_average'
log = Logger(NAMESPACE)


def initialize(context):
    context.i = 0
    context.short_orders = []
    context.tangles = []
    context.asset = symbol('btc_usd')
    context.base_price = None


def handle_data(context, data):
    # define the windows for the moving averages
    short_window = 5

    long_window = 60

    window1 = 5
    window2 = 10
    window3 = 30
    window4 = 60
    tangle_threshold = 0.3
    tangle_window_size = 30
    # Skip as many bars as long_window to properly compute the average
    context.i += 1
    if context.i < long_window:
        return

    # Compute moving averages calling data.history() for each
    # moving average with the appropriate parameters. We choose to use
    # minute bars for this simulation -> freq="1m"
    # Returns a pandas dataframe.
    window_data1 = data.history(context.asset,
                                'price',
                                bar_count=window1,
                                frequency="1D",
                                )
    mavg1 = window_data1.mean()
    window_data2 = data.history(context.asset,
                                'price',
                                bar_count=window2,
                                frequency="1D",
                                )
    mavg2 = window_data2.mean()

    window_data3 = data.history(context.asset,
                                'price',
                                bar_count=window3,
                                frequency="1D",
                                )
    mavg3 = window_data3.mean()

    window_data4 = data.history(context.asset,
                                'price',
                                bar_count=window4,
                                frequency="1D",
                                )
    mavg4 = window_data4.mean()

    current_order = 0
    if mavg1 < mavg2:
        current_order = current_order + 1
    if mavg1 < mavg3:
        current_order = current_order + 1
    if mavg1 < mavg4:
        current_order = current_order + 1

    if context.short_orders:
        the_tangle = abs(context.short_orders[-1] - current_order)
        context.tangles.append(the_tangle)
    else:
        context.tangles.append(0)

    context.short_orders.append(current_order)

    # Let's keep the price of our asset in a more handy variable
    price = data.current(context.asset, 'price')

    # If base_price is not set, we use the current value. This is the
    # price at the first bar which we reference to calculate price_change.
    if context.base_price is None:
        context.base_price = price
    price_change = (price - context.base_price) / context.base_price

    # Save values for later inspection


    # Since we are using limit orders, some orders may not execute immediately
    # we wait until all orders are executed before considering more trades.
    orders = context.blotter.open_orders
    if len(orders) > 0:
        return

    # Exit if we cannot trade
    if not data.can_trade(context.asset):
        return

    # We check what's our position on our portfolio and trade accordingly
    pos_amount = context.portfolio.positions[context.asset].amount

    current_tangle = 0
    if len(context.tangles) > 60:
        current_tangle = sum(context.tangles[-tangle_window_size:])/float(tangle_window_size)
        if current_tangle > tangle_threshold:
            pass
            #log.info('tangle is {} at {}'.format(current_tangle, data.current_dt))

    record(price=price,
           cash=context.portfolio.cash,
           price_change=price_change,
           mavg1=mavg1,
           mavg2=mavg2,
           mavg3=mavg3,
           mavg4=mavg4,
           tangle=current_tangle
           )
    #Trading logic
    if current_tangle > tangle_threshold and pos_amount == 0:
        # we buy 100% of our portfolio for this asset
        order_target_percent(context.asset, 1)
        log.info(
            '{}: buying - price: {}, '.format(
                data.current_dt, price
            )
        )
    elif mavg1 < mavg3 and pos_amount > 0:
        # we sell all our positions for this asset
        order_target_percent(context.asset, 0)
        log.info(
            '{}: selling - price: {}, '.format(
                data.current_dt, price
            )
        )


def analyze(context, perf):
    #print(perf.loc[:, ['tangle']])
    # Get the quote_currency that was passed as a parameter to the simulation
    exchange = list(context.exchanges.values())[0]
    quote_currency = exchange.quote_currency.upper()

    # First chart: Plot portfolio value using quote_currency
    ax1 = plt.subplot(511)
    perf.loc[:, ['portfolio_value']].plot(ax=ax1)
    ax1.legend_.remove()
    ax1.set_ylabel('Portfolio Value\n({})'.format(quote_currency))
    start, end = ax1.get_ylim()
    ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    # Second chart: Plot asset price, moving averages and buys/sells
    ax2 = plt.subplot(512, sharex=ax1)
    perf.loc[:, ['price', 'short_mavg', 'long_mavg']].plot(
        ax=ax2,
        label='Price')
    ax2.legend_.remove()
    ax2.set_ylabel('{asset}\n({quote})'.format(
        asset=context.asset.symbol,
        quote=quote_currency
    ))
    start, end = ax2.get_ylim()
    ax2.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    transaction_df = extract_transactions(perf)
    if not transaction_df.empty:
        buy_df = transaction_df[transaction_df['amount'] > 0]
        sell_df = transaction_df[transaction_df['amount'] < 0]
        ax2.scatter(
            buy_df.index.to_pydatetime(),
            perf.loc[buy_df.index, 'price'],
            marker='^',
            s=100,
            c='green',
            label=''
        )
        ax2.scatter(
            sell_df.index.to_pydatetime(),
            perf.loc[sell_df.index, 'price'],
            marker='v',
            s=100,
            c='red',
            label=''
        )

    # Third chart: Compare percentage change between our portfolio
    # and the price of the asset
    ax3 = plt.subplot(513, sharex=ax1)
    perf.loc[:, ['algorithm_period_return', 'price_change']].plot(ax=ax3)
    ax3.legend_.remove()
    ax3.set_ylabel('Percent Change')
    start, end = ax3.get_ylim()
    ax3.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    # Fourth chart: Plot our cash
    ax4 = plt.subplot(514, sharex=ax1)
    perf.cash.plot(ax=ax4)
    ax4.set_ylabel('Cash\n({})'.format(quote_currency))
    start, end = ax4.get_ylim()
    ax4.yaxis.set_ticks(np.arange(0, end, end / 5))

    # Fifth chart: Plat max drawdown
    ax5 = plt.subplot(515, sharex=ax1)
    perf.loc[:, ['max_drawdown']].plot(ax=ax5)
    ax5.legend_.remove()
    ax5.set_ylabel('Max draw down\n({})'.format(quote_currency))
    start, end = ax5.get_ylim()
    ax5.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    plt.show()


if __name__ == '__main__':
    run_algorithm(
        capital_base=1000,
        data_frequency='daily',
        initialize=initialize,
        handle_data=handle_data,
        analyze=analyze,
        exchange_name='bitfinex',
        algo_namespace=NAMESPACE,
        quote_currency='usd',
        start=pd.to_datetime('2017-1-1', utc=True),
        end=pd.to_datetime('2019-5-1', utc=True),
    )
