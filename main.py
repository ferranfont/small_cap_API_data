import pandas as pd
from ib_connector import get_ibkr_data
from chart_volume import plot_close_and_volume

SYMBOL = 'OP'
DAYS = 10
df = get_ibkr_data(symbol=SYMBOL, days=DAYS, bar_size='1 min', what_to_show='TRADES', use_rth=True, client_id=14)
print(df)

plot_close_and_volume(df,symbol=SYMBOL)