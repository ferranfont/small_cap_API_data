import pandas as pd
from ib_connector import get_ibkr_data
from chart_volume import plot_close_and_volume
import os

SYMBOL = 'OP'
DAYS = 10

df = get_ibkr_data(symbol=SYMBOL, days=DAYS, bar_size='1 min', what_to_show='TRADES', use_rth=True, client_id=14)
df['ticker'] = SYMBOL
cols = ['ticker'] + [col for col in df.columns if col != 'ticker']
df = df[cols]

print(df)

# Save the DataFrame to CSV
output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, f'{SYMBOL}_data.csv')
df.to_csv(csv_path, index=False)

plot_close_and_volume(df,symbol=SYMBOL)