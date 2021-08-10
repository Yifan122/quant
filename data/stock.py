from jqdatasdk import *

import utils.date_utils
from utils import *
import time
import pandas as pd
import datetime
import os

# 设置行列不忽略
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 1000)

# 全局变量
data_root = '/Users/yifan.zeng/PycharmProjects/quant/rowdata/'
update_freq = '10d'


def init_db():
    '''
    初始化股票数据库
    :return:
    '''
    # 1.获取所有沪深300股票代码
    stocks = get_index_list('399673.XSHE')
    print(stocks)

    # 2.存储到csv文件中
    for code in stocks:
        print(code)
        df = get_single_price(code, update_freq)
        export_data(df, code, 'price')
        print(df.head())

    # 3. 初始化每年的财务数据
    annul_report()


def annul_report(start_year=2010, end_year=2021):
    """
    获取历年来的估值数据（valuation），资产负债数据（balance），现金流数据(cash_flow), 利润数据(income)
    并且保存到 data_root/fundamental 目录下面
    :param start_year:
    :param end_year:
    :return:
    """
    fundamental_dir = data_root + '/fundamental/'
    if not os.path.isdir(fundamental_dir):
        os.makedirs(fundamental_dir)

    for year in range(start_year, end_year):
        annul_report_df = get_fundamentals(query(valuation, balance, cash_flow, income), statDate=str(year))
        pd.DataFrame(annul_report_df).to_csv(fundamental_dir + str(year) + '.csv')


def append_fundamental_data(code, df):
    """
    添加每天的财务估值的数据
    :param code:
    :param df:
    :return:
    """
    fundamentals = pd.concat(
        [get_fundamentals(query(
            valuation
            , indicator
            , balance
        ).filter(valuation.code == code), date=date) for date in df.index])

    fundamentals.index = pd.to_datetime(fundamentals['day'])

    df = pd.concat([df, fundamentals], axis=1)
    return df


def get_stock_list():
    """
    获取所有A股股票列表
    上海证券交易所.XSHG
    深圳证券交易所.XSHE
    :return: stock_list
    """
    stock_list = list(get_all_securities(['stock']).index)
    return stock_list


def get_index_list(index_symbol='000300.XSHG'):
    """
    获取指数成分股，指数代码查询：https://www.joinquant.com/indexData
    :param index_symbol: 指数的代码，默认沪深300
    :return: list，成分股代码
    """
    stocks = get_index_stocks(index_symbol)
    return stocks


def get_single_price(code, time_freq, start_date=None, end_date=None):
    """
    获取单个股票行情数据
    :param code:
    :param time_freq:
    :param start_date:
    :param end_date:
    :return:
    """
    # 如果start_date=None，默认为从上市日期开始
    if start_date is None:
        start_date = get_security_info(code).start_date
    if end_date is None:
        end_date = datetime.datetime.today()
    # 获取行情数据
    data = get_price(code, start_date=start_date, end_date=end_date,
                     frequency=time_freq, panel=False)  # 获取获得在2015年
    print(data.head())
    print("Append fundamental data for ", code)
    data = append_fundamental_data(code, data)
    return data


def export_data(data, filename, type, mode=None):
    """
    导出股票相关数据
    :param data:
    :param filename:
    :param type: 股票数据类型，可以是：price、finance
    :param mode: a代表追加，none代表默认w写入
    :return:
    """
    data_dir = data_root + type + '/' + update_freq
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)

    file_root = data_dir + '/' + filename + '.csv'
    data.index.names = ['date']
    if mode == 'a':
        data.to_csv(file_root, mode=mode, header=False)
        # 删除重复值
        # data = pd.read_csv(file_root)  # 读取数据
        # data = data.drop_duplicates(subset=['date'])  # 以日期列为准
        # data.to_csv(file_root, index=False)  # 重新写入
    else:
        data.to_csv(file_root)  # 判断一下file是否存在 > 存在：追加 / 不存在：保持

    print('已成功存储至：', file_root)


def get_csv_price(code, start_date, end_date, columns=None):
    """
    获取本地数据，且顺便完成数据更新工作
    :param code: str,股票代码
    :param start_date: str,起始日期
    :param end_date: str,起始日期
    :param columns: list,选取的字段
    :return: dataframe
    """
    # 使用update直接更新
    update_daily_price(code)
    # 读取数据
    file_root = data_root + 'price/' + update_freq + '/' + code + '.csv'
    if columns is None:
        data = pd.read_csv(file_root, index_col='date')
    else:
        data = pd.read_csv(file_root, usecols=columns, index_col='date')
    # print(data)
    # 根据日期筛选股票数据
    return data[(data.index >= start_date) & (data.index <= end_date)]


def transfer_price_freq(data, time_freq):
    """
    将数据转换为制定周期：开盘价（周期第1天）、收盘价（周期最后1天）、最高价（周期内）、最低价（周期内）
    :param data:
    :param time_freq:
    :return:
    """
    df_trans = pd.DataFrame()
    df_trans['open'] = data['open'].resample(time_freq).first()
    df_trans['close'] = data['close'].resample(time_freq).last()
    df_trans['high'] = data['high'].resample(time_freq).max()
    df_trans['low'] = data['low'].resample(time_freq).min()

    return df_trans


def get_single_finance(code, date, statDate):
    """
    获取单个股票财务指标
    :param code:
    :param date:
    :param statDate:
    :return:
    """
    data = get_fundamentals(query(indicator).filter(indicator.code == code), date=date, statDate=statDate)  # 获取财务指标数据
    return data


def get_single_valuation(code, date, statDate):
    """
    获取单个股票估值指标
    :param code:
    :param date:
    :param statDate:
    :return:
    """
    data = get_fundamentals(query(valuation).filter(valuation.code == code), date=date, statDate=statDate)  # 获取财务指标数据
    return data


def calculate_change_pct(data):
    """
    涨跌幅 = (当期收盘价-前期收盘价) / 前期收盘价
    :param data: dataframe，带有收盘价
    :return: dataframe，带有涨跌幅
    """
    data['close_pct'] = (data['close'] - data['close'].shift(1)) \
                        / data['close'].shift(1)
    return data


def update_daily_price(stock_code, type='price'):
    # 3.1是否存在文件：不存在-重新获取，存在->3.2
    file_root = data_root + type + '/' + update_freq + '/' + stock_code + '.csv'
    if os.path.isfile(file_root):  # 如果存在对应文件
        # 3.2获取增量数据（code，startsdate=对应股票csv中最新日期，enddate=今天）
        start_date = pd.read_csv(file_root, usecols=['date'])['date'].iloc[-1]
        next_date = utils.date_utils.get_next_day(start_date)
        df = get_single_price(stock_code, update_freq, next_date, datetime.datetime.today())
        # 3.3追加到已有文件中
        export_data(df, stock_code, 'price', 'a')
    else:
        # 重新获取该股票行情数据
        df = get_single_price(stock_code, update_freq)
        export_data(df, stock_code, 'price')

    print("股票数据已经更新成功：", stock_code)


if __name__ == '__main__':
    """
    初始化数据库，这里采取最简单的csv格式来存取所有的数据
    """
    auth('15889545353', '545353')  # 账号是申请时所填写的手机号

    init_db()
    annul_report()