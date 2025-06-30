# el código procesa datos de acciones desde una base de datos MySQL, calcula fechas clave de caídas y genera gráficos.
# crea un CSV llamado bio_summary.csv con las días necesarios para alcanzar las caídas.

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from chart_visor_resampled import plot_close_and_volume_resample
from Utils.us_market_open_days_fraction_10_days import get_first_valid_date

from datetime import datetime

# Lee tickers
tickers_in_db_df = pd.read_csv('outputs/tickers_in_db.csv')
tickers_in_db = tickers_in_db_df.iloc[:, 0].tolist()

CHART_TIMEFRAME = "240min"

# Load .env credentials
load_dotenv()
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

# Path resumen
os.makedirs("outputs", exist_ok=True)
summary_path = "outputs/bio_summary.csv"
csv_exists = os.path.isfile(summary_path)

for idx, SYMBOL in enumerate(tickers_in_db):
    print(f"\n====== Procesando {SYMBOL} ======")
    first_oficial = get_first_valid_date(SYMBOL)
    print(f"📅 IPO_oficial para {SYMBOL}: {first_oficial}")

    query = f"SELECT * FROM prices WHERE ticker = '{SYMBOL}' ORDER BY date"
    df = pd.read_sql(query, engine, parse_dates=['date'])
    print(f"✅ Data loaded: {len(df)} rows for {SYMBOL}")

    if df.empty:
        print(f"⚠️  No hay datos para {SYMBOL}, se omite.")
        continue

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    ipo_date = df.loc[0, 'date']
    ipo_price = df.loc[0, 'close']

    max_idx = df['close'].idxmax()
    max_price = df.loc[max_idx, 'close']
    max_date = df.loc[max_idx, 'date']
    days_to_max = (max_date - ipo_date).days

    def find_drop(df, max_date, threshold_pct):
        threshold_price = max_price * (1 - threshold_pct)
        df_after = df[df['date'] > max_date]
        drop = df_after[df_after['close'] <= threshold_price].head(1)
        if not drop.empty:
            date = pd.to_datetime(drop.iloc[0]['date'])
            price = drop.iloc[0]['close']
            days = (date - max_date).days
            return date, round(price, 2), days
        return None, None, None

    drop60_date, drop60_price, days_drop60 = find_drop(df, max_date, 0.60)
    drop80_date, drop80_price, days_drop80 = find_drop(df, max_date, 0.80)
    drop90_date, drop90_price, days_drop90 = find_drop(df, max_date, 0.90)

    summary_data = {
        'symbol': SYMBOL,
        'ipo_date': ipo_date.date(),
        'ipo_oficial': first_oficial,
        'ipo_price': round(ipo_price, 2),
        'max_date': max_date.date(),
        'max_price': round(max_price, 2),
        'pct_from_ipo': round(((max_price - ipo_price) / ipo_price) * 100, 2),
        'days_to_max': days_to_max,
        'drop60_date': drop60_date.date() if drop60_date else None,
        'drop60_price': drop60_price,
        'days_from_60': days_drop60,
        'drop80_date': drop80_date.date() if drop80_date else None,
        'drop80_price': drop80_price,
        'days_from_80': days_drop80,
        'drop90_date': drop90_date.date() if drop90_date else None,
        'drop90_price': drop90_price,
        'days_from_90': days_drop90
    }

    # Append al CSV
    df_summary = pd.DataFrame([summary_data])
    if idx == 0 and not csv_exists:
        # Primera vez: crea con cabecera
        df_summary.to_csv(summary_path, index=False, mode='w')
        print(f"\n✅ CSV creado y guardado en: {summary_path}")
    else:
        # Luego: solo agrega fila sin cabecera
        df_summary.to_csv(summary_path, index=False, mode='a', header=False)
        print(f"\n✅ Fila añadida a: {summary_path}")

    # ------------------ DROP DATES + GRAFICACIÓN ------------------
    drop_dates_df = pd.DataFrame({
        'drop_label': ['Drop 60%', 'Drop 80%', 'Drop 90%'],
        'date': [drop60_date, drop80_date, drop90_date]
    })
    v_lines = [d for d in drop_dates_df['date'].tolist() if pd.notnull(d)]

    print("\n📆 Fechas clave de caídas:")
    print(v_lines)

    # Graficar
    plot_close_and_volume_resample(
        df=df,
        symbol=SYMBOL,
        timeframe=CHART_TIMEFRAME,
        v_lines=v_lines
    )

print(f"\n✅ Proceso terminado. Revisa el CSV en: {summary_path}")


