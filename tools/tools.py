#!/anaconda3/envs/catalyst/bin/python

# -*- coding: utf-8 -*-
import re
import sys

from catalyst.__main__ import main
from catalyst.exchange.exchange_bundle import ExchangeBundle

binance_symbols = ['ada_bnb', 'ada_btc', 'ada_eth', 'ada_pax', 'ada_tusd', 'ada_usdc', 'ada_usdt', 'adx_bnb', 'adx_btc', 'adx_eth', 'ae_bnb', 'ae_btc', 'ae_eth', 'agi_bnb', 'agi_btc', 'agi_eth', 'aion_bnb', 'aion_btc', 'aion_eth', 'amb_bnb', 'amb_btc', 'amb_eth', 'appc_bnb', 'appc_btc', 'appc_eth', 'ardr_bnb', 'ardr_btc', 'ardr_eth', 'ark_btc', 'ark_eth', 'arn_btc', 'arn_eth', 'ast_btc', 'ast_eth', 'atom_bnb', 'atom_btc', 'atom_pax', 'atom_tusd', 'atom_usdc', 'atom_usdt', 'bat_bnb', 'bat_btc', 'bat_eth', 'bat_pax', 'bat_tusd', 'bat_usdc', 'bat_usdt', 'bcd_btc', 'bcd_eth', 'bch_bnb', 'bch_btc', 'bch_eth', 'bch_usdt', 'bchabc_btc', 'bchabc_pax', 'bchabc_tusd', 'bchabc_usdc', 'bchabc_usdt', 'bchsv_btc', 'bchsv_pax', 'bchsv_tusd', 'bchsv_usdc', 'bchsv_usdt', 'bcn_bnb', 'bcn_btc', 'bcn_eth', 'bcpt_bnb', 'bcpt_btc', 'bcpt_eth', 'blz_bnb', 'blz_btc', 'blz_eth', 'bnb_btc', 'bnb_eth', 'bnb_pax', 'bnb_tusd', 'bnb_usdc', 'bnb_usds', 'bnb_usdt', 'bnt_btc', 'bnt_eth', 'bqx_btc', 'bqx_eth', 'brd_bnb', 'brd_btc', 'brd_eth', 'btc_pax', 'btc_tusd', 'btc_usdc', 'btc_usds', 'btc_usdt', 'btg_btc', 'btg_eth', 'bts_bnb', 'bts_btc', 'bts_eth', 'btt_bnb', 'btt_btc', 'btt_pax', 'btt_tusd', 'btt_usdc', 'btt_usdt', 'cdt_btc', 'cdt_eth', 'celr_bnb', 'celr_btc', 'celr_usdt', 'chat_btc', 'chat_eth', 'cloak_btc', 'cloak_eth', 'cmt_bnb', 'cmt_btc', 'cmt_eth', 'cnd_bnb', 'cnd_btc', 'cnd_eth', 'cvc_bnb', 'cvc_btc', 'cvc_eth', 'dash_bnb', 'dash_btc', 'dash_eth', 'dash_usdt', 'data_btc', 'data_eth', 'dcr_bnb', 'dcr_btc', 'dent_btc', 'dent_eth', 'dgd_btc', 'dgd_eth', 'dlt_bnb', 'dlt_btc', 'dlt_eth', 'dnt_btc', 'dnt_eth', 'dock_btc', 'dock_eth', 'edo_btc', 'edo_eth', 'elf_btc', 'elf_eth', 'eng_btc', 'eng_eth', 'enj_bnb', 'enj_btc', 'enj_eth', 'enj_usdt', 'eos_bnb', 'eos_btc', 'eos_eth', 'eos_pax', 'eos_tusd', 'eos_usdc', 'eos_usdt', 'etc_bnb', 'etc_btc', 'etc_eth', 'etc_pax', 'etc_tusd', 'etc_usdc', 'etc_usdt', 'eth_btc', 'eth_pax', 'eth_tusd', 'eth_usdc', 'eth_usdt', 'evx_btc', 'evx_eth', 'fet_bnb', 'fet_btc', 'fet_usdt', 'fuel_btc', 'fuel_eth', 'fun_btc', 'fun_eth', 'gas_btc', 'gnt_bnb', 'gnt_btc', 'gnt_eth', 'go_bnb', 'go_btc', 'grs_btc', 'grs_eth', 'gto_bnb', 'gto_btc', 'gto_eth', 'gvt_btc', 'gvt_eth', 'gxs_btc', 'gxs_eth', 'hc_btc', 'hc_eth', 'hot_bnb', 'hot_btc', 'hot_eth', 'hot_usdt', 'hsr_btc', 'hsr_eth', 'icn_btc', 'icn_eth', 'icx_bnb', 'icx_btc', 'icx_eth', 'icx_usdt', 'ins_btc', 'ins_eth', 'iost_bnb', 'iost_btc', 'iost_eth', 'iost_usdt', 'iota_bnb', 'iota_btc', 'iota_eth', 'iota_usdt', 'iotx_btc', 'iotx_eth', 'key_btc', 'key_eth', 'kmd_btc', 'kmd_eth', 'knc_btc', 'knc_eth', 'lend_btc', 'lend_eth', 'link_btc', 'link_eth', 'link_pax', 'link_tusd', 'link_usdc', 'link_usdt', 'loom_bnb', 'loom_btc', 'loom_eth', 'lrc_btc', 'lrc_eth', 'lsk_bnb', 'lsk_btc', 'lsk_eth', 'ltc_bnb', 'ltc_btc', 'ltc_eth', 'ltc_pax', 'ltc_tusd', 'ltc_usdc', 'ltc_usdt', 'lun_btc', 'lun_eth', 'mana_btc', 'mana_eth', 'matic_bnb', 'matic_btc', 'matic_usdt', 'mco_bnb', 'mco_btc', 'mco_eth', 'mda_btc', 'mda_eth', 'mft_bnb', 'mft_btc', 'mft_eth', 'mith_bnb', 'mith_btc', 'mith_usdt', 'mod_btc', 'mod_eth', 'mth_btc', 'mth_eth', 'mtl_btc', 'mtl_eth', 'nano_bnb', 'nano_btc', 'nano_eth', 'nano_usdt', 'nas_bnb', 'nas_btc', 'nas_eth', 'nav_bnb', 'nav_btc', 'nav_eth', 'ncash_bnb', 'ncash_btc', 'ncash_eth', 'nebl_bnb', 'nebl_btc', 'nebl_eth', 'neo_bnb', 'neo_btc', 'neo_eth', 'neo_pax', 'neo_tusd', 'neo_usdc', 'neo_usdt', 'npxs_btc', 'npxs_eth', 'nuls_bnb', 'nuls_btc', 'nuls_eth', 'nuls_usdt', 'nxs_bnb', 'nxs_btc', 'nxs_eth', 'oax_btc', 'oax_eth', 'omg_bnb', 'omg_btc', 'omg_eth', 'omg_usdt', 'ong_bnb', 'ong_btc', 'ong_usdt', 'ont_bnb', 'ont_btc', 'ont_eth', 'ont_usdt', 'ost_bnb', 'ost_btc', 'ost_eth', 'pax_bnb', 'pax_btc', 'pax_eth', 'pax_tusd', 'pax_usdt', 'phx_bnb', 'phx_btc', 'phx_eth', 'pivx_bnb', 'pivx_btc', 'pivx_eth', 'poa_bnb', 'poa_btc', 'poa_eth', 'poe_btc', 'poe_eth', 'poly_bnb', 'poly_btc', 'powr_bnb', 'powr_btc', 'powr_eth', 'ppt_btc', 'ppt_eth', 'qkc_btc', 'qkc_eth', 'qlc_bnb', 'qlc_btc', 'qlc_eth', 'qsp_bnb', 'qsp_btc', 'qsp_eth', 'qtum_bnb', 'qtum_btc', 'qtum_eth', 'qtum_usdt', 'rcn_bnb', 'rcn_btc', 'rcn_eth', 'rdn_bnb', 'rdn_btc', 'rdn_eth', 'ren_bnb', 'ren_btc', 'rep_bnb', 'rep_btc', 'rep_eth', 'req_btc', 'req_eth', 'rlc_bnb', 'rlc_btc', 'rlc_eth', 'rpx_bnb', 'rpx_btc', 'rpx_eth', 'rvn_bnb', 'rvn_btc', 'salt_btc', 'salt_eth', 'sc_bnb', 'sc_btc', 'sc_eth', 'sky_bnb', 'sky_btc', 'sky_eth', 'sngls_btc', 'sngls_eth', 'snm_btc', 'snm_eth', 'snt_btc', 'snt_eth', 'steem_bnb', 'steem_btc', 'steem_eth', 'storj_btc', 'storj_eth', 'storm_bnb', 'storm_btc', 'storm_eth', 'strat_btc', 'strat_eth', 'sub_btc', 'sub_eth', 'sys_bnb', 'sys_btc', 'sys_eth', 'theta_bnb', 'theta_btc', 'theta_eth', 'theta_usdt', 'tnb_btc', 'tnb_eth', 'tnt_btc', 'tnt_eth', 'trig_bnb', 'trig_btc', 'trig_eth', 'trx_bnb', 'trx_btc', 'trx_eth', 'trx_pax', 'trx_tusd', 'trx_usdc', 'trx_usdt', 'trx_xrp', 'tusd_bnb', 'tusd_btc', 'tusd_eth', 'tusd_usdt', 'usdc_bnb', 'usdc_btc', 'usdc_pax', 'usdc_tusd', 'usdc_usdt', 'usds_pax', 'usds_tusd', 'usds_usdc', 'usds_usdt', 'ven_bnb', 'ven_btc', 'ven_eth', 'ven_usdt', 'vet_bnb', 'vet_btc', 'vet_eth', 'vet_usdt', 'via_bnb', 'via_btc', 'via_eth', 'vib_btc', 'vib_eth', 'vibe_btc', 'vibe_eth', 'wabi_bnb', 'wabi_btc', 'wabi_eth', 'wan_bnb', 'wan_btc', 'wan_eth', 'waves_bnb', 'waves_btc', 'waves_eth', 'waves_pax', 'waves_tusd', 'waves_usdc', 'waves_usdt', 'wings_btc', 'wings_eth', 'wpr_btc', 'wpr_eth', 'wtc_bnb', 'wtc_btc', 'wtc_eth', 'xem_bnb', 'xem_btc', 'xem_eth', 'xlm_bnb', 'xlm_btc', 'xlm_eth', 'xlm_pax', 'xlm_tusd', 'xlm_usdc', 'xlm_usdt', 'xmr_bnb', 'xmr_btc', 'xmr_eth', 'xmr_usdt', 'xrp_bnb', 'xrp_btc', 'xrp_eth', 'xrp_pax', 'xrp_tusd', 'xrp_usdc', 'xrp_usdt', 'xvg_btc', 'xvg_eth', 'xzc_bnb', 'xzc_btc', 'xzc_eth', 'xzc_xrp', 'yoyow_bnb', 'yoyow_btc', 'yoyow_eth', 'zec_bnb', 'zec_btc', 'zec_eth', 'zec_pax', 'zec_tusd', 'zec_usdc', 'zec_usdt', 'zen_bnb', 'zen_btc', 'zen_eth', 'zil_bnb', 'zil_btc', 'zil_eth', 'zil_usdt', 'zrx_bnb', 'zrx_btc', 'zrx_eth', 'zrx_usdt']

def get_all_pairs_by_quote(quote_symbol):
    targets = []
    for one_symbol in binance_symbols:
        if one_symbol.endswith(quote_symbol):
            print(one_symbol)
            targets.append(one_symbol)
    return targets



if __name__ == '__main__':
    # sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    # sys.exit(main())


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

    all_pairs = get_all_pairs_by_quote("usdt")

    for one_pair in all_pairs:
        try:
            exchange_bundle.ingest(
                data_frequency=data_frequency,
                include_symbols=one_pair,
                exclude_symbols=exclude_symbols,
                start=start,
                end=end,
                show_progress=show_progress,
                show_breakdown=verbose,
                show_report=validate,
                csv=csv
            )
        except Exception as e:
            log


