# Este código es sólo una herramienta para obtener los días de mercado abierto del NYSE desde 2020 hasta hoy.

import pandas_market_calendars as mcal
from datetime import date

start = '2020-01-01'
end = date.today().strftime('%Y-%m-%d')

# Cargar el calendario del NYSE
nyse = mcal.get_calendar('NYSE')

# Fechas entre 2020 y hoy
schedule = nyse.schedule(start_date=start, end_date=end)

# Extraer sólo las fechas (sin hora)
market_open_days = schedule.index.strftime('%Y-%m-%d').tolist()

# Mostrar los primeros 5 días
print(market_open_days[:20])




