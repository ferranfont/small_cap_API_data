import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Tickers que quieres insertar

tickers_to_upload = ['RIGL','RGNX','RGLS','QURE','PRTA']

# Conexión a MySQL
engine = create_engine('mysql+mysqlconnector://root:Plus7070@127.0.0.1/small_caps')

# Ruta a la carpeta
folder = 'outputs'
chunk_size = 50000

# Recorrer tickers deseados
for ticker in tickers_to_upload:
    file = f"{ticker}_data.csv"
    filepath = os.path.join(folder, file)

    if os.path.exists(filepath):
        print(f"\n🔁 Procesando: {file}")
        try:
            # Leer CSV
            df = pd.read_csv(filepath)

            # Formatear fecha correctamente
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_convert(None)

            # Insertar por chunks
            for start in range(0, len(df), chunk_size):
                end = start + chunk_size
                chunk = df.iloc[start:end]
                chunk.to_sql(name='prices', con=engine, if_exists='append', index=False)
                print(f"✅ Insertado chunk {start}–{end} del archivo {file}")

        except SQLAlchemyError as e:
            print(f"❌ Error SQL en {file}:", e)
        except Exception as ex:
            print(f"❌ Error general en {file}:", ex)
    else:
        print(f"⚠️ Archivo no encontrado: {file}")
