"""
based on
https://towardsdatascience.com/backtesting-trading-strategies-using-custom-data-in-zipline-e6fd65eeaca0
tutorial"""

# %%
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import tse_data_reader
from tse_data_reader.ticker import Ticker
from zipline.utils.calendars import get_calendar, register_calendar
from tse_calendar import TehranExchangeCalendar


# %%
def download_csv_data(symbol, start_date, end_date, freq, path):

    ticker = Ticker(symbol)
    cols = ("max_price", "min_price", "close_price",
            "first_price", "trade_volume")
    df = ticker.history(start_date=start_date,
                        end_date=end_date,
                        columns=cols)
    df = format_tsetmc_price_data_for_zipline(df)

    # save data to csv for later ingestion
    path = str(Path.home()) + '/' + '/' + path + '/daily'
    Path(path).mkdir(parents=True, exist_ok=True)
    df.to_csv(path + '/' + symbol + '.csv', header=True, index=True)

    # plot the time series
    df.close.plot(
        title='{} prices --- {}:{}'.format(ticker, start_date, end_date))


# %%
def format_tsetmc_price_data_for_zipline(df):

    df = df.rename(columns={'max_price': 'high', 'min_price': 'low', 'close_price': 'close',
                            'first_price': 'open', 'trade_volume': 'volume'}).loc[:, ['open', 'high', 'low', 'close', 'volume']]
    df['dividend'] = 0
    df['split'] = 1

    # make sure that there is data for every day to avoid calendar errors
    df = df.resample('1d').mean()
    df.fillna(method='ffill', inplace=True)

    # Ensure the df is indexed by UTC timestamps
    df = df.set_index(df.index.to_datetime().tz_localize('UTC'))

    # Get all expected trading sessions in this range and reindex.
    register_calendar('TSE', TehranExchangeCalendar, True)
    trading_calendar = get_calendar('TSE')
    sessions = get_calendar(trading_calendar).sessions_in_range(
        '2017-12-24', '2020-02-26')

    df = df.reindex(sessions)

    return df


# %%
download_csv_data(symbol='چکاپا',
                  start_date='1396-1-1',
                  end_date='1398-9-1',
                  freq='daily',
                  path='.tse_data_zipline')


# %%
"""

import pandas as pd
from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities


start_session = pd.Timestamp('2017-12-26', tz='IRST')
end_session = pd.Timestamp('2020-02-26', tz='IRST')

# register the bundle
register(
    'tse_stocks',  # name we select for the bundle
    csvdir_equities(
        # name of the directory as specified above (named after data frequency)
        ['daily'],
        # path to directory containing the
		'/home/diaco/.tse-data-zipline'
    ),
    calendar_name='TSE',
    start_session=start_session,
    end_session=end_session
)
"""

"""
terminal cmc: zipline ingest --bundle tse_stocks
"""

# %%
