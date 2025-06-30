import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from chart_visor_resampled import plot_close_and_volume_resample

# --- CONFIGURACIÓN ---
CHART_TIMEFRAME = "240min"
INVEST_AMOUNT = 1000  # USD

# --- CREDENCIALES BASE DE DATOS ---
load_dotenv()
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

# --- LEE TODOS LOS TICKERS DEL CSV ---
tickers_df = pd.read_csv('outputs/tickers_in_db.csv')
tickers_in_db = tickers_df.iloc[:,0].tolist()

# --- LEE BIO SUMMARY SOLO UNA VEZ (para todas las búsquedas) ---
bio_summary_path = 'outputs/bio_summary.csv'
bio_summary_df = pd.read_csv(bio_summary_path)

# --- CREAR CARPETA OUTPUTS SI NO EXISTE ---
os.makedirs('outputs', exist_ok=True)
tracking_path = 'outputs/tracking_record_time.csv'

# --- ITERA SOBRE TODOS LOS TICKERS ---
for SYMBOL in tickers_in_db:
    print(f"\n====== Procesando {SYMBOL} ======")
    
    # --- DESCARGA HISTÓRICO ---
    query = f"SELECT * FROM prices WHERE ticker = '{SYMBOL}' ORDER BY date"
    df = pd.read_sql(query, engine, parse_dates=['date'])
    if len(df) < 101:
        print(f"❌ El histórico para {SYMBOL} tiene menos de 101 filas, saltando...")
        continue

    df = df.sort_values('date').reset_index(drop=True)
    df['close'] = df['close'].astype(float)

    # --- ESTRATEGIA SHORT ---
    entry_row = 25000
    if entry_row >= len(df):
        print(f"❌ No hay suficientes filas para la entrada ({entry_row}) en {SYMBOL}, saltando...")
        continue
    entry_date = df.loc[entry_row, 'date']
    entry_price = df.loc[entry_row, 'close']

    n_shares = int(INVEST_AMOUNT // entry_price)
    actual_investment = n_shares * entry_price

    after_entry = df.iloc[entry_row:].copy()
    max_idx = after_entry['close'].idxmax()
    max_price = after_entry.loc[max_idx, 'close']
    max_date = after_entry.loc[max_idx, 'date']

    days_to_max = (max_date - entry_date).days
    pct_to_max = 100 * (max_price - entry_price) / entry_price

    # -90% desde máximo histórico completo
    historic_max = df['close'].max()
    exit_threshold = historic_max * 0.10

    exit_row = after_entry[after_entry['close'] <= exit_threshold].head(1)

    if not exit_row.empty:
        exit_idx = exit_row.index[0]
        exit_date = exit_row.iloc[0]['date']
        exit_price = exit_row.iloc[0]['close']
        closed = True
    else:
        exit_date = df.iloc[-1]['date']
        exit_price = df.iloc[-1]['close']
        closed = False

    unit_profit = entry_price - exit_price
    unit_profit_pct = 100 * unit_profit / entry_price
    total_profit = unit_profit * n_shares
    total_profit_pct = 100 * total_profit / actual_investment if actual_investment > 0 else 0

    mfe = entry_price - after_entry['close'].min()
    mfe_pct = 100 * mfe / entry_price
    mae = entry_price - after_entry['close'].max()
    mae_pct = 100 * mae / entry_price
    period = after_entry[(after_entry['date'] >= entry_date) & (after_entry['date'] <= exit_date)]
    volatility = period['close'].std()
    volatility_pct = 100 * volatility / entry_price

    time_in_market_days = (exit_date - entry_date).days

    # --- EXPORTA Y APPEND A CSV ---
    result = {
        'symbol': SYMBOL,
        'entry_row': entry_row,
        'entry_date': entry_date,
        'entry_price': entry_price,
        'n_shares': n_shares,
        'actual_investment': round(actual_investment, 2),
        'max_date': max_date,
        'max_price': max_price,
        'days_to_max': days_to_max,
        'pct_to_max': round(pct_to_max, 2),
        'exit_date': exit_date,
        'exit_price': exit_price,
        'historic_max': historic_max,
        'closed_at_-90%': closed,
        'unit_profit': round(unit_profit, 4),
        'unit_profit_pct': round(unit_profit_pct, 2),
        'total_profit': round(total_profit, 2),
        'total_profit_pct': round(total_profit_pct, 2),
        'mfe': round(mfe, 4),
        'mfe_pct': round(mfe_pct, 2),
        'mae': round(mae, 4),
        'mae_pct': round(mae_pct, 2),
        'volatility': round(volatility, 4),
        'volatility_pct': round(volatility_pct, 2),
        'time_in_market_days': time_in_market_days
    }

    # APPEND al tracking_record_time.csv (sin sobreescribir)
    df_result = pd.DataFrame([result])
    # Si el archivo ya existe, añade sin cabecera
    if os.path.exists(tracking_path):
        df_result.to_csv(tracking_path, mode='a', index=False, header=False)
    else:
        df_result.to_csv(tracking_path, mode='w', index=False, header=True)
    print(f"✅ Resultado añadido a {tracking_path}")

    # -- OBTENER VLINES DEL SUMMARY (drop60, 80, 90) SI EXISTE --
    resumen_rows = bio_summary_df[bio_summary_df['symbol'] == SYMBOL]
    if resumen_rows.empty:
        print(f"❌ No hay resumen en bio_summary.csv para {SYMBOL}, saltando gráfico...")
        continue

    resumen_row = resumen_rows.iloc[0]
    drop_cols = ['drop60_date', 'drop80_date', 'drop90_date']
    drop_dates = [resumen_row[col] for col in drop_cols]
    v_lines = [d for d in drop_dates if pd.notnull(d) and str(d) != 'nan']

    print("\n📆 Fechas clave de caídas:")
    print(v_lines)

    # --- GRAFICAR ---
    plot_close_and_volume_resample(
        df=df,
        symbol=SYMBOL,
        timeframe=CHART_TIMEFRAME,
        v_lines=v_lines,
        df_tracking=df_result
    )
