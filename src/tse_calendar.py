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
