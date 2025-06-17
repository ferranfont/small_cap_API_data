from ib_insync import *
import pandas as pd

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=14)  # hay que tener el TWS o IB Gateway corriendo y configurado para aceptar conexiones API

# Definir el contrato para Apple en el mercado SMART en dólares
stock = Stock('KLTO', 'SMART', 'USD')

# Descargar datos históricos en velas de 1 minuto (máximo: 7 días hacia atrás)
bars = ib.reqHistoricalData(
    stock,
    endDateTime='',            # ahora
    durationStr='3 D',         # máximo permitido por IB para 1 minuto
    barSizeSetting='1 min',    # velas de 1 minuto
    whatToShow='TRADES',       # tipo de precio (puedes poner 'TRADES' para precios de operaciones)
    useRTH=True,               # solo horario regular (si quieres todo el día: False)
    formatDate=1               # formato de fecha (1 para timestamp, 2 para Timestamp con milisegundos)
)

df = util.df(bars)
print(df.head(40))
print('\n ')
ib.disconnect()

print(df['date'].min())
print(df['date'].max())
print(df['date'].max() - df['date'].min())

