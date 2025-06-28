import os
import mysql.connector
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")

try:
    # Conectar a la base de datos
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM prices")
    count = cursor.fetchone()[0]

    print(f"📊 Total filas en 'prices': {count:,}")

except mysql.connector.Error as err:
    print(f"❌ Error de conexión: {err}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
