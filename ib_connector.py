from ib_insync import *
import pandas as pd

def get_ibkr_data(
    symbol='KLTO',
    exchange='SMART',
    currency='USD',
    days=3,
    bar_size='1 min',
    what_to_show='TRADES',
    use_rth=True,
    client_id=14
):
    ib = IB()
    ib.connect('127.0.0.1', 7496, clientId=client_id)

    stock = Stock(symbol, exchange, currency)
    bars = ib.reqHistoricalData(
        stock,
        endDateTime='',
        durationStr=f'{days} D',
        barSizeSetting=bar_size,
        whatToShow=what_to_show,
        useRTH=use_rth,
        formatDate=1
    )

    df = util.df(bars)
    ib.disconnect()
    
    print(df.head(40))
    print('\n ')
    print("Fecha inicial:", df['date'].min())
    print("Fecha final:  ", df['date'].max())
    print("Días de diferencia:", df['date'].max() - df['date'].min())

    return df

