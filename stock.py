from jqdatasdk import *
import pandas as pd

auth('17621171968','171968')
# auth('15889545353','545353')

# 获取平安银行按1分钟为周期以“2015-01-30 14:00:00”为基础前4个时间单位的数据
# XSHG 代表 Shan(g)hai，XSHE 代表 Sh(e)nzhen
df = get_price('000001.XSHE', end_date='2021-08-05',count=20, frequency='1d', fields=['open','close','high','low','volume','money'])

df['weekday'] = df.index.weekday
print(df)

# 获取周K的开盘价, 收盘价， 一周最高价，最低价
df_week = pd.DataFrame()
df_week['open'] = df['open'].resample('W').first()
df_week['close'] = df['close'].resample('W').last()
df_week['high'] = df['high'].resample('W').max()
df_week['low'] = df['low'].resample('W').min()

df_week['volume(sum)'] = df['volume'].resample('W').sum()
df_week['money(sum)'] = df['money'].resample('W').sum()
print(df_week)



