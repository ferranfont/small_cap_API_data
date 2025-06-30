#  el codigo busca el primer dia de trading de un ticker en Yahoo Finance
# y genera bloques de 10 días hábiles del NYSE desde esa fecha para evitar problemas de rate limit   
# Luego, guarda estos bloques en un archivo de texto para su uso posterior.

import pandas_market_calendars as mcal
from datetime import datetime
import pandas as pd
import os
import yfinance as yf

def get_first_valid_date(symbol):
    """
    Usa Yahoo Finance para obtener la primera fecha con datos disponibles del ticker.
    """
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="max")
    if not hist.empty:
        first_date = hist.index.min().date()  # Solo la fecha, sin la hora
        return str(first_date)  # Formato 'YYYY-MM-DD'
    else:
        return None

def generate_10_day_blocks(symbol):
    """
    Genera bloques de 10 días hábiles del NYSE desde la fecha de IPO del símbolo.
    """
    first_valid_date = get_first_valid_date(symbol)
    if not first_valid_date:
        print(f"❌ No se encontraron datos históricos para {symbol}.")
        return

    print(f"✅ Primera fecha con datos para {symbol}: {first_valid_date}")

    nyse = mcal.get_calendar('XNYS')
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Crear calendario de mercado
    schedule = nyse.schedule(start_date=first_valid_date, end_date=end_date)
    trading_days = mcal.date_range(schedule, frequency='1D')

    # Bloques de 10 días hábiles
    blocks = [(trading_days[i], trading_days[i+9]) for i in range(0, len(trading_days)-9, 10)]

    # Formatear fechas en 'YYYYMMDD 23:59:59'
    formatted_blocks = [f"{block[1].strftime('%Y%m%d')} 23:59:59" for block in blocks]

    # Guardar en archivo
    os.makedirs("outputs", exist_ok=True)
    with open(f"outputs/endDateTime_blocks.txt", "w") as f:
        for line in formatted_blocks:
            f.write(line + "\n")

    print(f"📁 Archivo guardado: outputs/endDateTime_blocks_{symbol}.txt")


