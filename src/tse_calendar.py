"""
A custom zipline trading calendar for Tehran stock exchange.
"""
# %% Importing some modules
# for setting our open and close times
from datetime import time
# for setting our start and end sessions
import pandas as pd
# for setting which days of the week we trade on
from pandas.tseries.offsets import CustomBusinessDay
# for setting our timezone
from pytz import timezone
# for creating and registering our calendar
from trading_calendars import TradingCalendar, register_calendar
from zipline.utils.memoize import lazyval


# %%
class TehranExchangeCalendar(TradingCalendar):
    """
    An exchange calendar for trading assets in Tehran stock exchange

    Open Time: 8:30AM, IRST
    Close Time: 12:30PM, IRST
    """

    @property
    def name(self):
        """
        The name of the exchange, which Zipline will look for
        when we run our algorithm and pass TFS to
        the --trading-calendar CLI flag.
        """
        return "TSE"

    @property
    def tz(self):
        """
        The timezone in which we'll be running our algorithm.
        """
        return timezone("IRST")

    @property
    def open_time(self):
        """
        The time in which our exchange will open each day.
        """
        return time(8, 30)

    @property
    def close_time(self):
        """
        The time in which our exchange will close each day.
        """
        return time(12, 30)

    @lazyval
    def day(self):
        """
        The days on which our exchange will be open.
        """
        weekmask = "Sat Sun Mon Tue Wed"
        return CustomBusinessDay(
            weekmask=weekmask
        )
