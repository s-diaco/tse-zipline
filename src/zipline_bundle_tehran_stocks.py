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
from six import iteritems
import pandas as pd
import pickle
import requests
from trading_calendars import register_calendar
# from trading_calendars.exchange_calendar_binance import BinanceExchangeCalendar
# from tse_calendar import TehranExchangeCalendar
import sqlite3

# %%
data_subdir = 'tehran_stocks'
user_home = Path.home()
tse_data_path = user_home / '.zipline' / data_subdir
source_database_file_path = user_home / 'tse' / 'stocks.db'
log = Logger(__name__)
show_progress = True

# %%


def load_data_table(file, show_progress=True):
    """
    loads a dataframe from sqlite database provided by 'tehran_stocks' module.
    """

    if show_progress:
        log.info('Parsing raw data.')
    con = sqlite3.connect(str(file))
    # db has two tables: stock_price and stocks
    sql = "select * from stock_price limit 5"
    date_fmt = '%Y%m%d'
    df = pd.read_sql_query(sql=sql,
                           con=con,
                           index_col=False,
                           parse_dates={'dtyyyymmdd': date_fmt})
    con.close()
    df = df.rename(columns={
        'code': 'symbol',
        'first': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'vol': 'volume'
    })
    df.sort_values(['symbol',
                    'date'],
                    ascending=[True, True])
    # df['dividend'] = 0
    # df['split'] = 1
    if show_progress:
        log.info(df.info())
        log.info(df.head())
        log.info('Got dada from tehran_stocks.')
    return df


# %%
def gen_asset_metadata(data, show_progress=True):
    if show_progress:
        log.info('Generating asset metadata.')
    data = data.groupby(
        by='symbol'
    ).agg(
        {'date': [np.min, np.max]}
    )
    data.reset_index(inplace=True)
    data['start_date'] = data.date.amin
    data['end_date'] = data.date.amax
    del data['date']
    data.columns = data.columns.get_level_values(0)
    data['auto_close_date'] = data['end_date'].values + pd.Timedelta(days=1)
    if show_progress:
        log.info(data.info())
        log.info(data.head())
    return data

# %%


def parse_splits(data, show_progress=True):
    if show_progress:
        log.info('Parsing split data.')
    data['split_ratio'] = 1.0 / data.split_ratio
    data.rename(
        columns={
            'split_ratio': 'ratio',
            'date': 'effective_date',
        },
        inplace=True,
        copy=False,
    )
    if show_progress:
        log.info(data.info())
        log.info(data.head())
    return data


def parse_dividends(data, show_progress=True):
    if show_progress:
        log.info('Parsing dividend data.')
    data['record_date'] = data['declared_date'] = data['pay_date'] = pd.NaT
    data.rename(columns={'date': 'ex_date',
                         'dividends': 'amount'}, inplace=True, copy=False)
    if show_progress:
        log.info(data.info())
        log.info(data.head())
    return data

# %%


def parse_pricing_and_vol(data,
                          sessions,
                          symbol_map):
    for asset_id, symbol in iteritems(symbol_map):
        asset_data = data.xs(
            symbol,
            level=1
        ).reindex(
            sessions.tz_localize(None)
        ).fillna(0.0)
        yield asset_id, asset_data

# %%


def ingest(environ,
           asset_db_writer,
           minute_bar_writer,
           daily_bar_writer,
           adjustment_writer,
           calendar,
           start_session,
           end_session,
           cache,
           show_progress,
           output_dir):
    raw_data = load_data_table(
        source_database_file_path, show_progress=show_progress)
    asset_metadata = gen_asset_metadata(
        raw_data[['symbol', 'date']],
        show_progress
    )
    asset_db_writer.write(asset_metadata)
    symbol_map = asset_metadata.symbol
    sessions = calendar.sessions_in_range(start_session, end_session)
    raw_data.set_index(['date', 'symbol'], inplace=True)
    daily_bar_writer.write(
        parse_pricing_and_vol(
            raw_data,
            sessions,
            symbol_map
        ),
        show_progress=show_progress
    )
    raw_data.reset_index(inplace=True)
    raw_data['symbol'] = raw_data['symbol'].astype('category')
    raw_data['sid'] = raw_data.symbol.cat.codes
    adjustment_writer.write(
        splits=parse_splits(
            raw_data[[
                'sid',
                'date',
                'split_ratio',
            ]].loc[raw_data.split_ratio != 1],
            show_progress=show_progress
        ),
        dividends=parse_dividends(
            raw_data[[
                'sid',
                'date',
                'dividends',
            ]].loc[raw_data.dividends != 0],
            show_progress=show_progress
        )
    )
