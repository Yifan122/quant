from jqdatasdk import *
import pandas as pd
from datetime import datetime

auth('17621171968','171968')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

print(get_all_securities(types=['futures'], date=None).size)

# # 拿到沪深300的股票代码
# df_weights = get_index_weights(index_id="000300.XSHG", date=datetime.today().strftime('%Y-%m-%d'))
# stocks = get_index_stocks('000300.XSHG')
#
# df=get_fundamentals(query(
#     valuation, indicator
#     ).filter(
#     valuation.code.in_(stocks),
#     valuation.pe_ratio < 20,
#     valuation.pe_ratio > 0,
#     # indicator.roe > 15,
#     # indicator.inc_net_profit_year_on_year > 10
#     ).order_by(
#         valuation.pe_ratio.desc(),
#         valuation.market_cap.desc()
#     )
#     , date="2021-08-04")
#
# df.index = df['code']
# df['display_name'] = df_weights['display_name']
#
#
# # df.to_csv("/Users/yifan.zeng/PycharmProjects/quant/data/test.csv")
# print(df[['pe_ratio', 'inc_net_profit_year_on_year', 'roe', 'market_cap', 'display_name']])
# df[['pe_ratio', 'inc_net_profit_year_on_year', 'roe', 'market_cap', 'display_name']].to_csv("/Users/yifan.zeng/PycharmProjects/quant/data/test.csv")