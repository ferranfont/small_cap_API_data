
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from chart_visor_resampled import plot_close_and_volume_resample



# --- CONFIG ---
SYMBOL = 'VERA'
OUTPUT_PATH = 'outputs/short_test_VERA.csv'
CHART_TIMEFRAME = "240min"

# --- DB CREDENCIALES ---
load_dotenv()
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")

engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

# --- DESCARGA HISTÓRICO ---
query = f"SELECT * FROM prices WHERE ticker = '{SYMBOL}' ORDER BY date"
df = pd.read_sql(query, engine, parse_dates=['date'])
if len(df) < 101:
    raise ValueError(f"El histórico para {SYMBOL} tiene menos de 101 filas.")

df = df.sort_values('date').reset_index(drop=True)
df['close'] = df['close'].astype(float)

# --- ESTRATEGIA SHORT ---
entry_row = 100
entry_date = df.loc[entry_row, 'date']
entry_price = df.loc[entry_row, 'close']

# Encuentra el máximo posterior a la entrada
after_entry = df.iloc[entry_row:].copy()
max_idx = after_entry['close'].idxmax()
max_price = after_entry.loc[max_idx, 'close']
max_date = after_entry.loc[max_idx, 'date']

# Días hasta máximo desde la entrada
days_to_max = (max_date - entry_date).days
pct_to_max = 100 * (max_price - entry_price) / entry_price

# Objetivo de caída -90% desde el máximo del histórico completo
historic_max = df['close'].max()
exit_threshold = historic_max * 0.10

# Buscamos el primer cierre igual o inferior al 10% del máximo histórico, DESPUÉS de la entrada
exit_row = after_entry[after_entry['close'] <= exit_threshold].head(1)

if not exit_row.empty:
    exit_idx = exit_row.index[0]
    exit_date = exit_row.iloc[0]['date']
    exit_price = exit_row.iloc[0]['close']
    # En corto: beneficio = venta - recompra
    profit_abs = entry_price - exit_price
    profit_pct = 100 * profit_abs / entry_price
    closed = True
else:
    # Si nunca alcanza ese precio, consideramos cierre al último precio
    exit_date = df.iloc[-1]['date']
    exit_price = df.iloc[-1]['close']
    profit_abs = entry_price - exit_price
    profit_pct = 100 * profit_abs / entry_price
    closed = False

# --- EXPORTAR RESULTADO ---
result = {
    'symbol': SYMBOL,
    'entry_row': entry_row,
    'entry_date': entry_date,
    'entry_price': entry_price,
    'max_date': max_date,
    'max_price': max_price,
    'days_to_max': days_to_max,
    'pct_to_max': round(pct_to_max, 2),
    'exit_date': exit_date,
    'exit_price': exit_price,
    'historic_max': historic_max,
    'closed_at_-90%': closed,
    'profit_abs': round(profit_abs, 4),
    'profit_pct': round(profit_pct, 2)
}


# --- GUARDA RESULTADO EN CSV ---
os.makedirs('outputs', exist_ok=True)
tracking_record_time = pd.DataFrame([result])
OUTPUT_PATH = 'outputs/tracking_record_time.csv'
tracking_record_time.to_csv(OUTPUT_PATH, index=False)
print(f"✅ Resultado guardado en {OUTPUT_PATH}")
print(tracking_record_time.T)



# Leer la fila del resumen CSV para el SYMBOL actual y mostrarla
bio_summary_path = 'outputs/bio_summary.csv'
resumen_df = pd.read_csv(bio_summary_path)
resumen_row = resumen_df[resumen_df['symbol'] == SYMBOL]

print(resumen_row)

# Extraer las fechas de caída directamente de las columnas
drop_cols = ['drop60_date', 'drop80_date', 'drop90_date']
drop_dates = resumen_row[drop_cols].values.flatten().tolist()
# Extraer las fechas de caída directamente de las columnas
drop_cols = ['drop60_date', 'drop80_date', 'drop90_date']
drop_dates = resumen_row[drop_cols].values.flatten().tolist()

# Limpiar la lista: convertir a string y filtrar nulos/vacíos
v_lines = [d for d in drop_dates if pd.notnull(d) and str(d) != 'nan']

print("\n📆 Fechas clave de caídas:")
print(v_lines)

# Graficar las líneas verticales en el gráfico
plot_close_and_volume_resample(
    df=df,
    symbol=SYMBOL,
    timeframe=CHART_TIMEFRAME,
    v_lines=v_lines
    )