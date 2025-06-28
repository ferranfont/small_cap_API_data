import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

# 🔒 Cargar credenciales desde .env
load_dotenv()
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")

# ✅ Cargar tickers de Finviz CSV
df_tickers_list_finviz = pd.read_csv("../DATA/smal_caps_bio.csv")
finviz_tickers = df_tickers_list_finviz['Ticker'].str.upper().dropna().unique().tolist()
print(f"✅ Total tickers in CSV: {len(finviz_tickers)}")

# ✅ Conectar a MySQL con variables de entorno
engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

# ✅ Cargar tickers únicos desde DB
query = "SELECT DISTINCT ticker FROM prices"
df_tickers = pd.read_sql(query, engine)
tickers_in_db = df_tickers['ticker'].str.upper().dropna().unique().tolist()
print(f"✅ Tickers in DB: {len(tickers_in_db)}")

# ✅ Comparar
in_finviz_not_db = sorted(set(finviz_tickers) - set(tickers_in_db))
in_db_not_finviz = sorted(set(tickers_in_db) - set(finviz_tickers))
in_both = sorted(set(finviz_tickers) & set(tickers_in_db))

# ✅ Mostrar resultados
print(f"❌ In Finviz but not in DB ({len(in_finviz_not_db)}): {in_finviz_not_db}")
print(f"❌ In DB but not in Finviz ({len(in_db_not_finviz)}): {in_db_not_finviz}")
print(f"✅ In both ({len(in_both)}): {in_both}")

print(f"✅ Total tickers in Finviz: {len(finviz_tickers)}")
print(f"✅ Tickers in DB: {tickers_in_db}")

# Guardar a CSV
os.makedirs('outputs', exist_ok=True)
pd.DataFrame({'Ticker': tickers_in_db}).to_csv('outputs/tickers_in_db.csv', index=False)
print(f"✅ CSV guardado con {len(tickers_in_db)} filas: outputs/tickers_in_db.csv")