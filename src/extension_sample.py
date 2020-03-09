
import pandas as pd
from zipline.data.bundles.csvdir import csvdir_equities
from zipline.data.bundles import register
from trading_calendars import get_calendar, register_calendar


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


start_session = pd.Timestamp('2017-12-26', tz='utc')
end_session = pd.Timestamp('2020-02-26', tz='utc')

register_calendar('TSE', TehranExchangeCalendar(
    start=start_session, end=end_session))


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
terminal cmc: zipline ingest --bundle tse_stocks
"""
"""
https://github.com/quantopian/zipline/issues/2018
"""
