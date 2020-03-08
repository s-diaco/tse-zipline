"""
based on
https://towardsdatascience.com/backtesting-trading-strategies-using-custom-data-in-zipline-e6fd65eeaca0
tutorial"""

# %%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tse_data_reader
from tse_data_reader.ticker import Ticker


# %%
def download_csv_data(ticker, start_date, end_date, freq, path):

    ticker = Ticker(ticker)
    df = ticker.history(start_date='1396-1-1', end_date='1397-3-3')
    df = df.rename(columns={'max_price': 'high', 'min_price': 'low', 'close_price': 'close',
                              'first_price': 'open', 'trade_volume': 'volume'}).loc[:, ['open', 'high', 'low', 'close', 'volume']]
    df['dividend'] = 0
    df['split'] = 1

    # save data to csv for later ingestion
    df.to_csv(path, header=True, index=True)

    # plot the time series
    df.close.plot(
        title='{} prices --- {}:{}'.format(ticker, start_date, end_date))


# %%
download_csv_data(ticker='فخوز',
                  start_date='2017-01-01',
                  end_date='2017-12-31',
                  freq='daily',
                  path='tse.csv')


# %%
"""
start_session = pd.Timestamp('2017-01-02', tz='utc')
end_session = pd.Timestamp('2017-12-29', tz='utc')

# register the bundle
register(
    'eu_stocks',  # name we select for the bundle
    csvdir_equities(
        # name of the directory as specified above (named after data frequency)
        ['daily'],
        # path to directory containing the
        '/.../medium_articles/Quantitative Finance/european',
    ),
    calendar_name='XAMS',  # Euronext Amsterdam
    start_session=start_session,
    end_session=end_session
)
"""

# %%
