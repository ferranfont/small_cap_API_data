import pandas as pd
from chart_volume import plot_close_and_volume

SYMBOL = 'symbol'
RESAMPLED_TO = '1h'  # Resample to 1 hour

# Leer CSV y preparar índice
df = pd.read_csv("outputs/ib_data_full.csv")
df['date'] = pd.to_datetime(df['date'], utc=True)  # Asegura timezone consistente
df = df.set_index('date')

# Resamplear por hora: último close, suma de volumen
df_resampled = df[['close', 'volume']].resample(RESAMPLED_TO).agg({
    'close': 'last',
    'volume': 'sum'
}).dropna().reset_index()

print(df_resampled.head())

# Graficar
plot_close_and_volume(df=df_resampled, symbol=SYMBOL)
