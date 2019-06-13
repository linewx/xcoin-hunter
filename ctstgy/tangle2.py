import sys

import logbook
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from catalyst import run_algorithm
from catalyst.api import (record, symbol, order_target_percent, )
from catalyst.exchange.exchange_bundle import ExchangeBundle
from catalyst.exchange.utils.stats_utils import extract_transactions
from logbook import Logger, StreamHandler
from functools import partial

NAMESPACE = 'tangle2'
log = Logger(NAMESPACE)


def initialize(context, the_sysmbol):
    context.i = 0
    context.short_orders = []
    context.tangles = []
    context.asset = symbol(the_sysmbol)
    context.base_price = None
    context.last_days = 0
    context.last_price = 0


def std_percent(data):
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    return std / mean


def handle_data(context, data):
    # define the windows for the moving averages
    short_window = 5

    long_window = 60

    window1 = 5
    window2 = 10
    window3 = 30
    window4 = 60
    tangle_threshold = 0.04
    tangle_window_size = 15

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

    std_per = std_percent([price, mavg1, mavg2, mavg3])
    # log.info(
    #     '{}: std per: {}, '.format(
    #         data.current_dt, std_per
    #     )
    # )
    if std_per < tangle_threshold:
        # log.info(
        #     '{}: std per: {}, '.format(
        #         data.current_dt, std_per
        #     )
        # )
        context.last_days = context.last_days + 1
    else:

        if context.last_days > 10 and price > context.last_price:
            log.error(
                '{}: time to buy {}, '.format(
                    data.current_dt, context.asset.base_currency
                )
            )
        context.last_days = 0

    context.last_price = price

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
        current_tangle = sum(context.tangles[-tangle_window_size:]) / float(tangle_window_size)
        # if current_tangle > tangle_threshold:
        #     pass
        # log.info('tangle is {} at {}'.format(current_tangle, data.current_dt))

    record(price=price,
           cash=context.portfolio.cash,
           price_change=price_change,
           mavg1=mavg1,
           mavg2=mavg2,
           mavg3=mavg3,
           mavg4=mavg4,
           tangle=current_tangle
           )
    # Trading logic
    # if current_tangle > tangle_threshold and pos_amount == 0:
    #     # we buy 100% of our portfolio for this asset
    #     order_target_percent(context.asset, 1)
    #     # log.info(
    #     #     '{}: buying - price: {}, '.format(
    #     #         data.current_dt, price
    #     #     )
    #     # )
    # elif mavg1 < mavg3 and pos_amount > 0:
    #     # we sell all our positions for this asset
    #     order_target_percent(context.asset, 0)
    #     # log.info(
    #     #     '{}: selling - price: {}, '.format(
    #     #         data.current_dt, price
    #     #     )
    #     # )


def analyze(context, perf):
    # print(perf.loc[:, ['tangle']])
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


binance_symbols = ['ada_bnb', 'ada_btc', 'ada_eth', 'ada_pax', 'ada_tusd', 'ada_usdc', 'ada_usdt', 'adx_bnb', 'adx_btc',
                   'adx_eth', 'ae_bnb', 'ae_btc', 'ae_eth', 'agi_bnb', 'agi_btc', 'agi_eth', 'aion_bnb', 'aion_btc',
                   'aion_eth', 'amb_bnb', 'amb_btc', 'amb_eth', 'appc_bnb', 'appc_btc', 'appc_eth', 'ardr_bnb',
                   'ardr_btc', 'ardr_eth', 'ark_btc', 'ark_eth', 'arn_btc', 'arn_eth', 'ast_btc', 'ast_eth', 'atom_bnb',
                   'atom_btc', 'atom_pax', 'atom_tusd', 'atom_usdc', 'atom_usdt', 'bat_bnb', 'bat_btc', 'bat_eth',
                   'bat_pax', 'bat_tusd', 'bat_usdc', 'bat_usdt', 'bcd_btc', 'bcd_eth', 'bch_bnb', 'bch_btc', 'bch_eth',
                   'bch_usdt', 'bchabc_btc', 'bchabc_pax', 'bchabc_tusd', 'bchabc_usdc', 'bchabc_usdt', 'bchsv_btc',
                   'bchsv_pax', 'bchsv_tusd', 'bchsv_usdc', 'bchsv_usdt', 'bcn_bnb', 'bcn_btc', 'bcn_eth', 'bcpt_bnb',
                   'bcpt_btc', 'bcpt_eth', 'blz_bnb', 'blz_btc', 'blz_eth', 'bnb_btc', 'bnb_eth', 'bnb_pax', 'bnb_tusd',
                   'bnb_usdc', 'bnb_usds', 'bnb_usdt', 'bnt_btc', 'bnt_eth', 'bqx_btc', 'bqx_eth', 'brd_bnb', 'brd_btc',
                   'brd_eth', 'btc_pax', 'btc_tusd', 'btc_usdc', 'btc_usds', 'btc_usdt', 'btg_btc', 'btg_eth',
                   'bts_bnb', 'bts_btc', 'bts_eth', 'btt_bnb', 'btt_btc', 'btt_pax', 'btt_tusd', 'btt_usdc', 'btt_usdt',
                   'cdt_btc', 'cdt_eth', 'celr_bnb', 'celr_btc', 'celr_usdt', 'chat_btc', 'chat_eth', 'cloak_btc',
                   'cloak_eth', 'cmt_bnb', 'cmt_btc', 'cmt_eth', 'cnd_bnb', 'cnd_btc', 'cnd_eth', 'cvc_bnb', 'cvc_btc',
                   'cvc_eth', 'dash_bnb', 'dash_btc', 'dash_eth', 'dash_usdt', 'data_btc', 'data_eth', 'dcr_bnb',
                   'dcr_btc', 'dent_btc', 'dent_eth', 'dgd_btc', 'dgd_eth', 'dlt_bnb', 'dlt_btc', 'dlt_eth', 'dnt_btc',
                   'dnt_eth', 'dock_btc', 'dock_eth', 'edo_btc', 'edo_eth', 'elf_btc', 'elf_eth', 'eng_btc', 'eng_eth',
                   'enj_bnb', 'enj_btc', 'enj_eth', 'enj_usdt', 'eos_bnb', 'eos_btc', 'eos_eth', 'eos_pax', 'eos_tusd',
                   'eos_usdc', 'eos_usdt', 'etc_bnb', 'etc_btc', 'etc_eth', 'etc_pax', 'etc_tusd', 'etc_usdc',
                   'etc_usdt', 'eth_btc', 'eth_pax', 'eth_tusd', 'eth_usdc', 'eth_usdt', 'evx_btc', 'evx_eth',
                   'fet_bnb', 'fet_btc', 'fet_usdt', 'fuel_btc', 'fuel_eth', 'fun_btc', 'fun_eth', 'gas_btc', 'gnt_bnb',
                   'gnt_btc', 'gnt_eth', 'go_bnb', 'go_btc', 'grs_btc', 'grs_eth', 'gto_bnb', 'gto_btc', 'gto_eth',
                   'gvt_btc', 'gvt_eth', 'gxs_btc', 'gxs_eth', 'hc_btc', 'hc_eth', 'hot_bnb', 'hot_btc', 'hot_eth',
                   'hot_usdt', 'hsr_btc', 'hsr_eth', 'icn_btc', 'icn_eth', 'icx_bnb', 'icx_btc', 'icx_eth', 'icx_usdt',
                   'ins_btc', 'ins_eth', 'iost_bnb', 'iost_btc', 'iost_eth', 'iost_usdt', 'iota_bnb', 'iota_btc',
                   'iota_eth', 'iota_usdt', 'iotx_btc', 'iotx_eth', 'key_btc', 'key_eth', 'kmd_btc', 'kmd_eth',
                   'knc_btc', 'knc_eth', 'lend_btc', 'lend_eth', 'link_btc', 'link_eth', 'link_pax', 'link_tusd',
                   'link_usdc', 'link_usdt', 'loom_bnb', 'loom_btc', 'loom_eth', 'lrc_btc', 'lrc_eth', 'lsk_bnb',
                   'lsk_btc', 'lsk_eth', 'ltc_bnb', 'ltc_btc', 'ltc_eth', 'ltc_pax', 'ltc_tusd', 'ltc_usdc', 'ltc_usdt',
                   'lun_btc', 'lun_eth', 'mana_btc', 'mana_eth', 'matic_bnb', 'matic_btc', 'matic_usdt', 'mco_bnb',
                   'mco_btc', 'mco_eth', 'mda_btc', 'mda_eth', 'mft_bnb', 'mft_btc', 'mft_eth', 'mith_bnb', 'mith_btc',
                   'mith_usdt', 'mod_btc', 'mod_eth', 'mth_btc', 'mth_eth', 'mtl_btc', 'mtl_eth', 'nano_bnb',
                   'nano_btc', 'nano_eth', 'nano_usdt', 'nas_bnb', 'nas_btc', 'nas_eth', 'nav_bnb', 'nav_btc',
                   'nav_eth', 'ncash_bnb', 'ncash_btc', 'ncash_eth', 'nebl_bnb', 'nebl_btc', 'nebl_eth', 'neo_bnb',
                   'neo_btc', 'neo_eth', 'neo_pax', 'neo_tusd', 'neo_usdc', 'neo_usdt', 'npxs_btc', 'npxs_eth',
                   'nuls_bnb', 'nuls_btc', 'nuls_eth', 'nuls_usdt', 'nxs_bnb', 'nxs_btc', 'nxs_eth', 'oax_btc',
                   'oax_eth', 'omg_bnb', 'omg_btc', 'omg_eth', 'omg_usdt', 'ong_bnb', 'ong_btc', 'ong_usdt', 'ont_bnb',
                   'ont_btc', 'ont_eth', 'ont_usdt', 'ost_bnb', 'ost_btc', 'ost_eth', 'pax_bnb', 'pax_btc', 'pax_eth',
                   'pax_tusd', 'pax_usdt', 'phx_bnb', 'phx_btc', 'phx_eth', 'pivx_bnb', 'pivx_btc', 'pivx_eth',
                   'poa_bnb', 'poa_btc', 'poa_eth', 'poe_btc', 'poe_eth', 'poly_bnb', 'poly_btc', 'powr_bnb',
                   'powr_btc', 'powr_eth', 'ppt_btc', 'ppt_eth', 'qkc_btc', 'qkc_eth', 'qlc_bnb', 'qlc_btc', 'qlc_eth',
                   'qsp_bnb', 'qsp_btc', 'qsp_eth', 'qtum_bnb', 'qtum_btc', 'qtum_eth', 'qtum_usdt', 'rcn_bnb',
                   'rcn_btc', 'rcn_eth', 'rdn_bnb', 'rdn_btc', 'rdn_eth', 'ren_bnb', 'ren_btc', 'rep_bnb', 'rep_btc',
                   'rep_eth', 'req_btc', 'req_eth', 'rlc_bnb', 'rlc_btc', 'rlc_eth', 'rpx_bnb', 'rpx_btc', 'rpx_eth',
                   'rvn_bnb', 'rvn_btc', 'salt_btc', 'salt_eth', 'sc_bnb', 'sc_btc', 'sc_eth', 'sky_bnb', 'sky_btc',
                   'sky_eth', 'sngls_btc', 'sngls_eth', 'snm_btc', 'snm_eth', 'snt_btc', 'snt_eth', 'steem_bnb',
                   'steem_btc', 'steem_eth', 'storj_btc', 'storj_eth', 'storm_bnb', 'storm_btc', 'storm_eth',
                   'strat_btc', 'strat_eth', 'sub_btc', 'sub_eth', 'sys_bnb', 'sys_btc', 'sys_eth', 'theta_bnb',
                   'theta_btc', 'theta_eth', 'theta_usdt', 'tnb_btc', 'tnb_eth', 'tnt_btc', 'tnt_eth', 'trig_bnb',
                   'trig_btc', 'trig_eth', 'trx_bnb', 'trx_btc', 'trx_eth', 'trx_pax', 'trx_tusd', 'trx_usdc',
                   'trx_usdt', 'trx_xrp', 'tusd_bnb', 'tusd_btc', 'tusd_eth', 'tusd_usdt', 'usdc_bnb', 'usdc_btc',
                   'usdc_pax', 'usdc_tusd', 'usdc_usdt', 'usds_pax', 'usds_tusd', 'usds_usdc', 'usds_usdt', 'ven_bnb',
                   'ven_btc', 'ven_eth', 'ven_usdt', 'vet_bnb', 'vet_btc', 'vet_eth', 'vet_usdt', 'via_bnb', 'via_btc',
                   'via_eth', 'vib_btc', 'vib_eth', 'vibe_btc', 'vibe_eth', 'wabi_bnb', 'wabi_btc', 'wabi_eth',
                   'wan_bnb', 'wan_btc', 'wan_eth', 'waves_bnb', 'waves_btc', 'waves_eth', 'waves_pax', 'waves_tusd',
                   'waves_usdc', 'waves_usdt', 'wings_btc', 'wings_eth', 'wpr_btc', 'wpr_eth', 'wtc_bnb', 'wtc_btc',
                   'wtc_eth', 'xem_bnb', 'xem_btc', 'xem_eth', 'xlm_bnb', 'xlm_btc', 'xlm_eth', 'xlm_pax', 'xlm_tusd',
                   'xlm_usdc', 'xlm_usdt', 'xmr_bnb', 'xmr_btc', 'xmr_eth', 'xmr_usdt', 'xrp_bnb', 'xrp_btc', 'xrp_eth',
                   'xrp_pax', 'xrp_tusd', 'xrp_usdc', 'xrp_usdt', 'xvg_btc', 'xvg_eth', 'xzc_bnb', 'xzc_btc', 'xzc_eth',
                   'xzc_xrp', 'yoyow_bnb', 'yoyow_btc', 'yoyow_eth', 'zec_bnb', 'zec_btc', 'zec_eth', 'zec_pax',
                   'zec_tusd', 'zec_usdc', 'zec_usdt', 'zen_bnb', 'zen_btc', 'zen_eth', 'zil_bnb', 'zil_btc', 'zil_eth',
                   'zil_usdt', 'zrx_bnb', 'zrx_btc', 'zrx_eth', 'zrx_usdt']


def get_all_usdt_pairs():
    targets = []

    for one_symbol in binance_symbols:
        if one_symbol.endswith('usdt'):
            targets.append(one_symbol)
    return targets


if __name__ == '__main__':
    StreamHandler(sys.stdout, level=logbook.ERROR).push_application()
    exchange_name = 'binance'
    exchange_bundle = ExchangeBundle(exchange_name)
    data_frequency = 'daily'
    include_symbols = 'ada_btc'
    exclude_symbols = None
    start = None
    end = None
    show_progress = True
    verbose = False
    validate = False
    csv = None

    all_pairs = get_all_usdt_pairs()

    for one_pair in all_pairs:

        try:
            run_algorithm(
                capital_base=10000,
                data_frequency='daily',
                initialize=partial(initialize, the_sysmbol=one_pair),
                handle_data=handle_data,
                analyze=None,
                exchange_name='binance',
                algo_namespace=NAMESPACE,
                quote_currency='usd',
                start=pd.to_datetime('2019-1-1', utc=True),
                end=pd.to_datetime('2019-05-01', utc=True),
            )
        except Exception as e:
            # log.exception(e)
            log.warn("something wrong with the pair %s" % one_pair)
