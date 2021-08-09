from jqdatasdk import *
import pandas as pd

auth('17621171968','171968')
pd.set_option('display.max_columns', None)

# get PE ratio, PB ratio
df_valuation=get_fundamentals(query(valuation), statDate=2020)
# df.to_csv("/Users/yifan.zeng/PycharmProjects/quant/data/fundamental.csv")

'''获取财务指标'''
df_fundamental=get_fundamentals(query(indicator),date="2021-08-04")
# df.to_csv("/Users/yifan.zeng/PycharmProjects/quant/data/fundamental.csv")

# 基于盈利指标选股: eps, operating_profit,roe, inc_net_profit_year_on_year
# df = df_fundamental[  (df_fundamental['eps'] > 0)
#                     & (df_fundamental['roe'] > 15)
#                     & (df_fundamental['inc_net_profit_year_on_year'] > 20)
#                     & (df_fundamental['operating_profit'] > 286424400.8) ]

# 把估值数据和财务指标连接到一起
df_valuation.index = df_valuation['code']
df_fundamental.index = df_fundamental['code']

df_fundamental['pe_ratio'] = df_valuation['pe_ratio']
df_fundamental.to_csv("/Users/yifan.zeng/PycharmProjects/quant/data/fundamental.csv")
