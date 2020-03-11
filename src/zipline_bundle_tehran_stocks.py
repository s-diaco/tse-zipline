"""
a bunlde to transform tehran_stocks module to a zipline bundle
"""

# %%
import bs4 as bs
import csv
from logbook import Logger
from datetime import datetime as dt
from datetime import timedelta
import numpy as np
from os import listdir, mkdir, remove
from os.path import exists, isfile, join
from pathlib import Path
import pandas as pd
import pickle
import requests
from trading_calendars import register_calendar
#from trading_calendars.exchange_calendar_binance import BinanceExchangeCalendar
from tse_calendar import TehranExchangeCalendar
import sqlite3

# %%
data_subdir = 'tehran_stocks'
user_home = Path.home()
tse_data_path = user_home / '.zipline' / data_subdir
source_database_file_path = user_home / 'tse' / 'stocks.db'
log = Logger(__name__)

# %%


def load_data_table(file, show_progress=True):
    """
    loads a dataframe from sqlite database provided by 'tehran_stocks' module.
    """

    if show_progress:
        log.info('Parsing raw data.')
    con = sqlite3.connect(str(source_database_file_path))
    # db has two tables: stock_price and stocks
    sql = "select * from stock_price limit 5"
    date_fmt = '%Y%m%d'
    df = pd.read_sql_query(sql=sql,
                           con=con,
                           index_col='dtyyyymmdd',
                           parse_dates={'dtyyyymmdd': date_fmt})
    con.close()

    # df.sort_values(['ticker', 'dtyyyymmdd'],ascending=[True, True])

    df.index.rename('date', inplace=True)
    df = df.rename(columns={
        'first': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'vol': 'volume'
    }).loc[:, ['open', 'high', 'low',
               'close', 'volume']]
    df['dividend'] = 0
    df['split'] = 1
    if show_progress:
        log.info(df.info())
        log.info(df.head())
    return df


# %%
load_data_table(source_database_file_path, True)

# %%
