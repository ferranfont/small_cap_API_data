import os
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_close_and_volume(timeframe, df, symbol='AAPL', v_lines=None):
    html_path = 'charts/close_vol_chart_rth.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    df = df.rename(columns=str.lower)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.80, 0.20],
        vertical_spacing=0.03,
    )

    # Línea de cierre
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['close'],
        mode='lines',
        name='Close',
        line=dict(color='blue', width=1)
    ), row=1, col=1)

    # Barras de volumen
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['volume'],
        marker_color='royalblue',
        marker_line_color='blue',
        marker_line_width=0.4,
        opacity=0.95,
        name='Volumen'
    ), row=2, col=1)


    # ------- BLOQUE CORRECTO PARA VLINES -------
    shapes = []
    if v_lines is not None:
        for v in v_lines:
            if pd.isna(v):      # <-- SALTA si es NaT o NaN
                continue
            v_dt = pd.to_datetime(v).normalize()
            v_str = v_dt.strftime('%Y-%m-%dT00:00:00')
            shapes.append(
                dict(
                    type="line",
                    xref="x",
                    yref="paper",
                    x0=v_str,
                    x1=v_str,
                    y0=0,
                    y1=1,
                    line=dict(
                        color="rgba(128,128,128,0.4)",
                        width=1,
                    ),
                )
            )


    # --------------------------------------------

    fig.update_layout(
        dragmode='pan',
        title=f'{symbol}_RTH_{timeframe}',
        width=1500,
        height=700,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=12, color="black"),
        plot_bgcolor='rgba(255,255,255,0.05)',
        paper_bgcolor='rgba(240,240,240,0.1)',
        showlegend=False,
        template='plotly_white',
        xaxis=dict(
            type='date',
            tickformat="%b %d<br>%Y",
            tickangle=0,
            showgrid=False,
            linecolor='gray',
            linewidth=1
        ),
        yaxis=dict(showgrid=True, linecolor='gray', linewidth=1),
        xaxis2=dict(
            type='date',
            tickformat="%b %d<br>%Y",
            tickangle=45,
            showgrid=False,
            linecolor='gray',
            linewidth=1
        ),
        yaxis2=dict(showgrid=True, linecolor='grey', linewidth=1),
        shapes=shapes
    )

    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Gráfico Plotly guardado como '{html_path}'")

    import webbrowser
    webbrowser.open('file://' + os.path.realpath(html_path))
