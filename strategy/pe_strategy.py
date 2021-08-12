import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import data.stock as st
from jqdatasdk import *

pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 1000)

# global variable
code = '002032.XSHE'
file = '/Users/yifan.zeng/PycharmProjects/quant/rowdata/price/10d/' + code + '.csv'
cols = ['close', 'pe_ratio', 'pb_ratio', 'ps_ratio', 'market_cap', 'roe', 'roa',
        'net_profit_margin', 'inc_total_revenue_year_on_year', 'date']
fundamental_dir = '/Users/yifan.zeng/PycharmProjects/quant/rowdata/fundamental/'
start_date = '2010-10-01'
end_date = '2021-08-05'
fundamentals = pd.DataFrame()
filtered_stocks = []


def load_fundamental_data_by_year(start=2015, end=2021):
    for i in range(start, end):
        fundamental_data = pd.read_csv(fundamental_dir + str(i) + '.csv', usecols=['roe','code'])
        fundamental_data.index = fundamental_data['code']
        fundamentals[str(i)] = fundamental_data['roe']


def filter_securities_by_roe(threshold=15):
    stock_list = []
    # 沪深300
    stock_list = stock_list + st.get_index_list('000300.XSHG')
    # 创业板50
    stock_list = stock_list + st.get_index_list('399673.XSHE')

    df = fundamentals[fundamentals.index.isin(stock_list)]
    df['min'] = df.min(axis=1)

    df = df[df['min'] > threshold]
    return list(df.index)


def remove_outlier(df, lower_bound=0.05, upper_bound=0.95):
    """
    去除特别极端的例子
    :param df:
    :param lower_bound: pe值不小于loweer_bound的概率
    :param upper_bound: pe值不大于upper_bound的概率
    :return:
    """
    lower, upper = pd.DataFrame(df)['pe_ratio'].quantile([lower_bound, upper_bound])
    print("outlier: ", lower, upper)
    df = df[(df['pe_ratio'] > lower) & (df['pe_ratio'] < upper)]
    return df


def get_lower_bound(df, num_std=1):
    """
    假设该security的pe分布属于正太分布
    则找出pe值低于多少个标准差
    Default： 1个标准差 => 概率约小于16%
    :param df:
    :param num_std:
    :return:
    """
    df1 = remove_outlier(df)
    std = df1['pe_ratio'].std()
    mean = df1['pe_ratio'].mean()
    # 1 std ~> 16 %
    lower_bound = mean - num_std * std
    print("std, mean, lower_bound: ", std, mean, lower_bound)
    return lower_bound


def pe_percent(df):
    max = df['pe_ratio'].max()
    print('max pe is: ', max)

    df['pe_percent'] = df['pe_ratio'] / max
    return df


def compose_signal(df, window=50, lower_num_std=1, upper_num_std=3):
    """
    标记买入卖出的信号
    :param df:
    :param window: 在多少周的窗口内计算该security的pe百分位
    :param upper_num_std: 大于多少个标准差作为卖出信号
    :param lower_num_std: 小于多少个标准差作为买入信号
    :return:
    """
    df['window_mean'] = pd.DataFrame(df['pe_ratio']).rolling(window=window).mean()
    df['window_std'] = pd.DataFrame(df['pe_ratio']).rolling(window=window).std()
    df['buy_signal'] = np.where(df['pe_ratio'] < df['window_mean'] - lower_num_std * df['window_std'], 1, 0)
    df['sell_signal'] = np.where(df['pe_ratio'] > df['window_mean'] + upper_num_std * df['window_std'], -1, 0)
    return df


def display(data):
    """
    展示买入卖出时间点，pe和price
    :param data:
    :return:
    """
    data = compose_signal(data)
    print(data)
    buy_signal_df = data[data['buy_signal'] == 1]
    sell_signal_df = data[data['sell_signal'] == -1]

    # 绘制双Y轴曲线图
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(data.index, data['pe_ratio'], label='pe_ratio')
    ax1.plot(buy_signal_df['pe_ratio'], color='orange', marker='o', linestyle='None')
    ax1.plot(sell_signal_df['pe_ratio'], color='purple', marker='o', linestyle='None')
    ax1.set_ylabel('pe_ratio ')
    ax1.set_title(code)
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(data.index, data['close'], 'r', label='price')
    # ax2.set_xlim([0, np.e])
    ax2.set_ylabel('price')
    ax2.set_xlabel('date')
    ax2.legend(loc="lower right")

    plt.show()


if __name__ == '__main__':
    auth('17621171968', '171968')
    load_fundamental_data_by_year()

    stocks = filter_securities_by_roe()
    print(stocks)
    print(len(stocks))
    for stock in stocks:
        print(st.get_display_name(stock))
