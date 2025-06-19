# este código genera bloques de 10 días hábiles del mercado de valores de EE.UU. (NYSE)
# y los guarda en un archivo de texto con el formato 'YYYYMMDD 23:59:59'.       
# Este script utiliza la biblioteca pandas_market_calendars para obtener los días de mercado abierto

import pandas_market_calendars as mcal
from datetime import datetime
import pandas as pd
import os

# Calendario NYSE
nyse = mcal.get_calendar('XNYS')
start_date = '2022-05-17'
end_date = datetime.today().strftime('%Y-%m-%d')

# Días de mercado abierto
schedule = nyse.schedule(start_date=start_date, end_date=end_date)
trading_days = mcal.date_range(schedule, frequency='1D')

# Segmentos de 10 días hábiles
blocks = [(trading_days[i], trading_days[i+9]) for i in range(0, len(trading_days)-9, 10)]

# Convertir a formato 'YYYYMMDD 23:59:59'
formatted_blocks = [
    f"{block[1].strftime('%Y%m%d')} 23:59:59"
    for block in blocks
]

# Guardar en CSV
os.makedirs("outputs", exist_ok=True)
with open("outputs/endDateTime_blocks.txt", "w") as f:
    for line in formatted_blocks:
        f.write(line + "\n")
