import datetime
from jqdatasdk import *
import data.stock as st
import pandas as pd

auth('15889545353', '545353')  # 账号是申请时所填写的手机号

# 设置行列不忽略
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 1000)

code = '000001.XSHE'
date = '2021-04-10'

data = get_price(code, start_date='2021-03-10', end_date='2021-04-20', frequency='5d', panel=False)

data = st.append_fundamental_data(code, data)
print(data)
