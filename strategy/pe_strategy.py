import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 1000)

# global variable
code = '600585.XSHG'
file = '/Users/yifan.zeng/PycharmProjects/quant/rowdata/price/10d/' + code + '.csv'
cols = ['close', 'pe_ratio', 'pb_ratio', 'ps_ratio', 'market_cap', 'roe', 'roa',
        'net_profit_margin', 'inc_total_revenue_year_on_year', 'date']
start_date = '2010-10-01'
end_date = '2021-08-05'


def remove_outlier(df, lower_bound=0.05, upper_bound=0.95):
    lower, upper = pd.DataFrame(df)['pe_ratio'].quantile([lower_bound, upper_bound])
    print("outlier: ", lower, upper)
    df = df[(df['pe_ratio'] > lower) & (df['pe_ratio'] < upper)]
    return df


def get_lower_bound(df, num_std=1):
    df1 = remove_outlier(df)
    std = df1['pe_ratio'].std()
    mean = df1['pe_ratio'].mean()
    # 1 std => 15.1 %
    lower_bound = mean - num_std * std
    print("std, mean, lower_bound: ", std, mean, lower_bound)
    return lower_bound


def pe_percent(df):
    max = df['pe_ratio'].max()
    print('max pe is: ', max)

    df['pe_percent'] = df['pe_ratio'] / max
    return df


def compose_signal(df, window=100):
    df['window_mean'] = pd.DataFrame(df['pe_ratio']).rolling(window=window).mean()
    df['window_std'] = pd.DataFrame(df['pe_ratio']).rolling(window=window).std()
    df['buy_signal'] = np.where(df['pe_ratio'] < df['window_mean'] - df['window_std'], 1, 0)
    df['sell_signal'] = np.where(df['pe_ratio'] > df['window_mean'] + 3*df['window_std'], -1, 0)
    return df


if __name__ == '__main__':
    data = pd.DataFrame(pd.read_csv(file, index_col='date', usecols=cols).dropna())
    data = data[(data.index >= start_date) & (data.index <= end_date)]
    # data['pe_ratio'].plot.hist(bins=100)

    # df = get_lower_bound(data)
    # df = df[df['signal'] == 1]
    # print(df)
    #
    # plt.plot(data['close'])
    # plt.plot(df['close'], color='red', marker='o', linestyle = 'None')
    # plt.rcParams["figure.figsize"] = (20, 10)
    # plt.xticks(rotation=45)
    # plt.show()

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
