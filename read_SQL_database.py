import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
from chart_visor_resampled import plot_close_and_volume_resample  # asegúrate de que el archivo esté en el mismo directorio


SYMBOL = "SAGE"  # Ticker específico a consultar

# 🔐 Cargar credenciales desde .env
load_dotenv()
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")

# 📄 Leer tickers desde CSV
csv_path = os.path.join("..", "DATA", "smal_caps_bio.csv")
df_tickers = pd.read_csv(csv_path)
tickers = df_tickers['Ticker'].dropna().str.upper().unique().tolist()

# 🖨️ Imprimir vector de tickers
print("🧬 Lista de tickers:")
print(tickers)

# 🔌 Conectar a MySQL y cargar datos de ABCL
try:
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = connection.cursor(dictionary=True)

    # Cargar datos de ABCL ordenados por fecha
    cursor.execute(f"SELECT date, close, open, high, low, volume FROM prices WHERE ticker = '{SYMBOL}' ORDER BY date")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows)

    if df.empty:
        print("❌ No hay datos para ABCL en la base de datos.")
    else:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # ✅ Llamar a la función del archivo chart_visor_resampled.py
        plot_close_and_volume_resample(df, symbol=SYMBOL, timeframe="1D")

except mysql.connector.Error as err:
    print(f"❌ Error de conexión o consulta: {err}")

finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
