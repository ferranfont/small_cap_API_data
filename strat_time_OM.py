import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# --- CONFIG ---
SYMBOL = 'VERA'
OUTPUT_PATH = 'outputs/short_test_VERA.csv'

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

os.makedirs('outputs', exist_ok=True)
pd.DataFrame([result]).to_csv(OUTPUT_PATH, index=False)
print(f"✅ Resultado guardado en {OUTPUT_PATH}")
print(pd.DataFrame([result]).T)

