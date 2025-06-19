import os
import pandas as pd
from ib_connector_single_call import get_ibkr_data
from ib_connector_loop import get_ibkr_data_loop
from chart_volume import plot_close_and_volume
from fill_SQL_from_df import insertar_df_en_mysql


SYMBOL = 'KLTO'
#DAYS = 10

# 1- Fetch data from IBKR
# df = get_ibkr_data(symbol=SYMBOL, days=DAYS, bar_size='1 min', what_to_show='TRADES', use_rth=True, client_id=14) #single call

df = get_ibkr_data_loop(symbol=SYMBOL, bar_size='1 min', what_to_show='TRADES', use_rth=True, client_id=14) #single call
df['ticker'] = SYMBOL
cols = ['ticker'] + [col for col in df.columns if col != 'ticker']
df = df[cols]

print(df)

# 2- Save the DataFrame to CSV
output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, f'{SYMBOL}_data.csv')
df.to_csv(csv_path, index=False)

# 3- Insert the data into a MySQL database
insertar_df_en_mysql(df, ticker=SYMBOL) 

# 4- Plot the close price and volume
plot_close_and_volume(df,symbol=SYMBOL)

