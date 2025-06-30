# chart_visor_resampled.py
import pandas as pd
from chart_volume import plot_close_and_volume

def plot_close_and_volume_resample(df, symbol, timeframe='1D',v_lines=None, df_tracking=None):

    SYMBOL = symbol
    RESAMPLED_TO = timeframe

    print(f"📊 Resampling data for {SYMBOL} to {RESAMPLED_TO}...")

    # Asegura datetime y zona horaria
    df['date'] = pd.to_datetime(df['date'], utc=True)
    df = df.set_index('date')

    # Resample: último cierre y suma del volumen
    df_resampled = df[['close', 'volume']].resample(RESAMPLED_TO).agg({
        'close': 'last',
        'volume': 'sum'
    }).dropna().reset_index()

    print(df_resampled.head())

    # Llamar al graficador principal (sin highlight_dates)
    plot_close_and_volume(
        timeframe=RESAMPLED_TO,
        df=df_resampled,
        symbol=SYMBOL,
        v_lines=v_lines,
        df_tracking=df_tracking
    )
