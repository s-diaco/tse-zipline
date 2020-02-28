"""
Based on
https://analyzingalpha.com/a-simple-trading-strategy-in-zipline-and-jupyter
Tutorial
"""
# %%
from datetime import datetime
import pytz
import zipline
from zipline.api import order_target_percent, record, symbol, set_benchmark, get_open_orders


# %%
def initialize(context):
    context.i = 0
    context.asset = symbol('AAPL')
    set_benchmark(symbol('AAPL'))


# %%
def handle_data(context, data):
    # Skip first 200 days to get full windows
    context.i += 1
    if context.i < 200:
        return
    # Compute averages
    short_mavg = data.history(context.asset, 'price',
                              bar_count=50, frequency="1d").mean()
    long_mavg = data.history(context.asset, 'price',
                             bar_count=200, frequency="1d").mean()

    # Trading logic
    open_orders = get_open_orders()

    if context.asset not in open_orders:
        if short_mavg > long_mavg:
            # order_target orders as many shares as needed to
                        # achieve the desired number of shares.
            order_target_percent(context.asset, 1.0)
        elif short_mavg < long_mavg:
            order_target_percent(context.asset, 0.0)

    # Save values for later inspection
    record(AAPL=data.current(context.asset, 'price'),
           short_mavg=short_mavg, long_mavg=long_mavg)


# %%
start = datetime(2017, 1, 1, 0, 0, 0, 0, pytz.utc)
end = datetime(2019, 12, 31, 0, 0, 0, 0, pytz.utc)

pref = zipline.run_algorithm(
    start=start,
    end=end,
    initialize=initialize,
    capital_base=10000,
    handle_data=handle_data)


# %%
