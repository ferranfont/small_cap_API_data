# Este código inserta un DataFrame en una base de datos MySQL, asegurándose de que no se dupliquen las filas ya existentes.

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# ✅ Load environment variables
load_dotenv()

def insertar_df_en_mysql(df, ticker):
    # ✅ Get credentials from environment variables
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_NAME")

    # ✅ Create the engine using the secure variables
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

    # 1. Preparar el DataFrame para insertar
    df_sql = df.reset_index()

    # 2. Eliminar columna 'index' si existe
    if 'index' in df_sql.columns:
        df_sql.drop(columns=['index'], inplace=True)

    # 3. Asegurar que 'date' no tenga zona horaria
    df_sql['date'] = pd.to_datetime(df_sql['date']).dt.tz_localize(None)

    # 4. Consultar datos existentes
    query = f"SELECT ticker, date FROM prices WHERE ticker = '{ticker}'"
    existing = pd.read_sql(query, engine)

    # 5. Filtrar filas nuevas
    df_filtered = df_sql.merge(existing, on=['ticker', 'date'], how='left', indicator=True)
    df_new = df_filtered[df_filtered['_merge'] == 'left_only'].drop(columns=['_merge'])

    # 6. Insertar si hay nuevas filas
    if not df_new.empty:
        df_new.to_sql(name='prices', con=engine, if_exists='append', index=False)
        print(f"✅ {len(df_new)} nuevas filas insertadas en la tabla 'prices' para '{ticker}'.")
    else:
        print(f"⚠️ No hay nuevas filas para insertar para '{ticker}'.")

    engine.dispose()
