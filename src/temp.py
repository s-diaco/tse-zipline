import pandas as pd
import numpy as np
from pathlib import Path
from six import iteritems
from logbook import Logger
from zipfile import ZipFile
show_progress = True
log = Logger(__name__)
home = str(Path.home()) + "/"
path = home + "your_data_file.zip"
column_names = ["symbol",
                "date",
                "unadjusted_open",
                "unadjusted_high",
                "unadjusted_low",
                "unadjusted_close",
                "unadjusted_volume",
                "dividends", "splits",
                "adjusted_open",
                "adjusted_high",
                "adjusted_low",
                "adjusted_close",
                "adjusted_volume"]

def load_data_table(file, show_progress=show_progress):
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
            data_table.sort_values(['symbol',
                                    'date'],
                                   ascending=[True, True])
    data_table.rename(columns={
        'unadjusted_open': 'open',
        'unadjusted_high': 'high',
        'unadjusted_low': 'low',
        'unadjusted_close': 'close',
        'unadjusted_volume': 'volume',
        'splits': 'split_ratio'
    }, inplace=True, copy=False)
    if show_progress:
        log.info(data_table.info())
        log.info(data_table.head())
    return data_table

def gen_asset_metadata(data, show_progress):
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

def parse_splits(data, show_progress):
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

def parse_dividends(data, show_progress):
    if show_progress:
        log.info('Parsing dividend data.')
    data['record_date'] = data['declared_date'] = data['pay_date'] = pd.NaT
    data.rename(columns={'date': 'ex_date',
                         'dividends': 'amount'}, inplace=True, copy=False)
    if show_progress:
        log.info(data.info())
        log.info(data.head())
    return data

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
    raw_data = load_data_table(path, show_progress=show_progress)
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