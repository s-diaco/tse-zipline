"""
a bunlde to transform tehran_stocks module to a zipline bundle
"""

# %%
import bs4 as bs
import csv
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

# %%
def load_data_table(file, show_progress=1):
    """
    loads a dataframe from sqlite database provided by 'tehran_stocks' module.
    """

    conn = sqlite3.connect(str(source_database_file_path))
    # db has two tables: stock_price and stocks
    query="select * from stock_price limit 5"
    df=pd.read_sql_query(query, conn)
    conn.close()
    print(df.head())


    """
    # Load data table from Quandl.zip file.
    with ZipFile(file) as zip_file:
        file_names = zip_file.namelist()
        assert len(file_names) == 1, "Expected a single file"
        quandl_prices = file_names.pop()
        with zip_file.open(quandl_prices) as table_file:
            if show_progress:
                log.info('Parsing raw data.')
            data_table = pd.read_csv(table_file,
                                     names=column_names,
                                     index_col=False,
                                     usecols=[
                                         0, 1, 2, 3, 4, 5, 6, 7, 8],
                                     parse_dates=[1])
            data_table.sort_values(['symbol', 'date'],
                                   ascending=[True, True])

    data_table.rename(columns={
        'first': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'vol': 'volume',
    }, inplace=True, copy=False)
"""
    if show_progress:
        log.info(df.info())
        log.info(df.head())
    return df

# %%
load_data_table(source_database_file_path, 1)

# %%
