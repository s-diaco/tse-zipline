"""
A custom zipline csv bundle for Tehran stock exchange.
"""
# %% Importing some modules
from zipline.data.bundles.csvdir import csvdir_equities
from zipline.data.bundles import register
# for setting our open and close times
from datetime import time
# for setting our start and end sessions
import pandas as pd
# for setting which days of the week we trade on
from pandas.tseries.offsets import CustomBusinessDay
# for setting our timezone
from pytz import timezone
# for creating and registering our calendar
import trading_calendars as tc
from trading_calendars import get_calendar, TradingCalendar, register_calendar
from zipline.utils.memoize import lazyval

from pathlib import Path

# %% define some parameters
start_session = pd.Timestamp('2019-12-26', tz='utc')
end_session = pd.Timestamp('2020-02-26', tz='utc')
tse_csv_dir_name = '.tse_data_zipline'
path = str(Path.home()) + '/' + tse_csv_dir_name


class TehranExchangeCalendar(TradingCalendar):
    """
    An exchange calendar for trading assets in Tehran stock exchange

    Open Time: 8:30AM, IRST
    Close Time: 12:30PM, IRST
    """

    name = 'TSE'

    tz = timezone('UTC')

    weekmask = '1110011'

    open_times = (
        (None, time(9, 31)),
    )

    close_times = (
        (None, time(16)),
    )


# register 'tse' calendar
register_calendar('TSE',  TehranExchangeCalendar(
    start=start_session,
    end=end_session))

# register the bundle
register(
    'tse_stocks',  # name we select for the bundle
    csvdir_equities(
        # name of the directory as specified above (named after data frequency)
        ['daily'],
        # path to directory containing the
        path
    ),
    calendar_name='TSE',
    start_session=start_session,
    end_session=end_session
)


"""
terminal cmc: zipline ingest --bundle tse_stocks
"""
"""
https://github.com/quantopian/zipline/issues/2018
"""
