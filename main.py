import os
import pandas as pd           # <<--- AÑADE ESTA LÍNEA
import plotly.graph_objs as go
from plotly.subplots import make_subplots



from ib_connector import get_ibkr_data
from chart_volume import plot_close_and_volume

symbol = 'KLTO'
df = get_ibkr_data(symbol=symbol, days=3)
plot_close_and_volume(df, titulo="KLTO Close y Volumen")
