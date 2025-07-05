import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import webbrowser

# === LECTURA Y LIMPIEZA ===
df = pd.read_csv('outputs/tracking_record_time.csv')
df = pd.read_csv('outputs/tracking_record_time.csv')
df.columns = df.columns.str.strip()  # <-- elimina espacios a ambos lados
df['entry_date'] = pd.to_datetime(df['entry_date'], errors='coerce')
df['exit_date'] = pd.to_datetime(df['exit_date'], errors='coerce')
df = df.sort_values('entry_date').reset_index(drop=True)



# === CÁLCULO DE PROFIT ACUMULADO ===
df['total_profit'] = pd.to_numeric(df['total_profit'], errors='coerce').fillna(0)
df['cum_profit'] = df['total_profit'].cumsum()

# === GRÁFICO ÁREA PROFIT ACUMULADO CON COLORES ===
x = df['entry_date']
y = df['cum_profit']
y_pos = y.clip(lower=0)
y_neg = y.clip(upper=0)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y_pos, mode='lines',
                         line=dict(color='green'), fill='tozeroy',
                         fillcolor='rgba(0,200,0,0.22)', showlegend=False))
fig.add_trace(go.Scatter(x=x, y=y_neg, mode='lines',
                         line=dict(color='red'), fill='tozeroy',
                         fillcolor='rgba(200,0,0,0.22)', showlegend=False))
fig.add_trace(go.Scatter(x=x, y=y, mode='lines',
                         line=dict(color='black', width=1, dash='dot'),
                         opacity=0.7, showlegend=False))

fig.update_layout(
    title='Cumulative Profit Over Time (USD)',
    xaxis_title='Entry Date',
    yaxis_title='Cumulative Profit ($)',
    template='plotly_white',
    width=1700,
    height=800,
    margin=dict(l=40, r=20, t=60, b=40)
)

# === DIRECTORIO SALIDA ===
charts_dir = "charts"
os.makedirs(charts_dir, exist_ok=True)
area_path = os.path.join(charts_dir, 'Cumulative_Profit_Area.html')
fig.write_html(area_path)

# === CÁLCULO MÉTRICAS ===
returns = pd.to_numeric(df['unit_profit'], errors='coerce').fillna(0)
total_trades = len(returns)
num_win = (returns > 0).sum()
num_loss = (returns < 0).sum()
win_rate = 100 * num_win / total_trades if total_trades else 0
loss_rate = 100 * num_loss / total_trades if total_trades else 0
avg_win = returns[returns > 0].mean()
avg_loss = returns[returns < 0].mean()
expectancy = returns.mean()
win_loss_ratio = avg_win / abs(avg_loss) if avg_loss != 0 else np.nan
profit_factor = returns[returns > 0].sum() / abs(returns[returns < 0].sum()) if (returns < 0).any() else np.nan
sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else np.nan
sortino_ratio = returns.mean() / returns[returns < 0].std() * np.sqrt(252) if returns[returns < 0].std() != 0 else np.nan

# Drawdown
cumulative = df['cum_profit']
roll_max = cumulative.cummax()
drawdown = cumulative - roll_max
max_drawdown = drawdown.min()

# === TABLA DE MÉTRICAS ===
metric_names = [
    "Total Trades", "Win Trades", "Loss Trades",
    "Win Rate (%)", "Loss Rate (%)",
    "Average Win ($)", "Average Loss ($)",
    "Expectancy ($)", "Win/Loss Ratio",
    "Profit Factor", "Sharpe Ratio", "Sortino Ratio",
    "Max Drawdown ($)", "Total Profit ($)"
]

metric_values = [
    total_trades, num_win, num_loss,
    round(win_rate, 2), round(loss_rate, 2),
    round(avg_win, 2) if not np.isnan(avg_win) else "--",
    round(avg_loss, 2) if not np.isnan(avg_loss) else "--",
    round(expectancy, 2),
    round(win_loss_ratio, 2) if not np.isnan(win_loss_ratio) else "--",
    round(profit_factor, 2) if not np.isnan(profit_factor) else "--",
    round(sharpe_ratio, 2) if not np.isnan(sharpe_ratio) else "--",
    round(sortino_ratio, 2) if not np.isnan(sortino_ratio) else "--",
    round(max_drawdown, 2),
    round(df['cum_profit'].iloc[-1], 2)
]

fig_table = go.Figure(data=[go.Table(
    header=dict(values=["Metric", "Value"], fill_color='paleturquoise', align='left'),
    cells=dict(values=[metric_names, metric_values], fill_color='lavender', align='left'))
])
fig_table.update_layout(title='Key Trading Metrics', width=900, height=650)
table_path = os.path.join(charts_dir, "Trading_Metrics_Table.html")
fig_table.write_html(table_path)

# === TABLA DE 25 TRADES ===
cols = ['symbol', 'entry_date', 'exit_date', 'entry_price', 'exit_price',
        'unit_profit', 'total_profit', 'pct_to_max', 'time_in_market_days']
df_trades = df[cols].copy().head(25)
df_trades['entry_date'] = df_trades['entry_date'].dt.strftime('%Y-%m-%d %H:%M')
df_trades['exit_date'] = df_trades['exit_date'].dt.strftime('%Y-%m-%d %H:%M')

fig_trades = go.Figure(data=[go.Table(
    header=dict(values=list(df_trades.columns), fill_color='paleturquoise', align='left'),
    cells=dict(values=[df_trades[col] for col in df_trades.columns], fill_color='lavender', align='left'))
])
fig_trades.update_layout(title='Trade Sample (Top 25)', width=1600, height=600)
trades_path = os.path.join(charts_dir, "Trade_Table.html")
fig_trades.write_html(trades_path)

# Crear columna nueva
df['max_us_to_max'] = (df['max_price'] - df['entry_price']).abs()

# === HISTOGRAMA PCT_TO_MAX ===
fig_pct = px.histogram(
    df,
    x='pct_to_max',
    nbins=100,
    title='Histogram: % to Max Price',
    template='plotly_white',
    color_discrete_sequence=['green']
)
fig_pct.update_traces(marker_line_color='darkgreen', marker_line_width=1)
fig_pct.update_layout(width=1200, height=700)
hist_pct_path = os.path.join(charts_dir, "Histogram_pct_to_max.html")
fig_pct.write_html(hist_pct_path)

# === HISTOGRAMA TIME_IN_MARKET ===
fig_time = px.histogram(
    df,
    x='time_in_market_days',
    nbins=100,
    title='Histogram: Days in Market',
    template='plotly_white',
    color_discrete_sequence=['blue']
)
fig_time.update_traces(marker_line_color='darkblue', marker_line_width=1)
fig_time.update_layout(width=1200, height=700)
hist_time_path = os.path.join(charts_dir, "Histogram_time_in_market.html")
fig_time.write_html(hist_time_path)

# === HISTOGRAMA MAX_US_TO_MAX ===
fig_maxus = px.histogram(
    df,
    x='max_us_to_max',
    nbins=200,
    title='Histogram: Absolute Distance to Max Price ($)',
    template='plotly_white',
    color_discrete_sequence=['orange']
)
fig_maxus.update_traces(marker_line_color='darkorange', marker_line_width=1)
fig_maxus.update_layout(width=1200, height=700)
hist_maxus_path = os.path.join(charts_dir, "Histogram_max_us_to_max.html")
fig_maxus.write_html(hist_maxus_path)

# === ABRIR TODO EN NAVEGADOR ===
for path in [area_path, table_path, trades_path, hist_pct_path, hist_time_path, hist_maxus_path]:
    webbrowser.open('file://' + os.path.realpath(path))
