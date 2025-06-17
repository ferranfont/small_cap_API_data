import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_close_and_volume(
    df,
    titulo='Precio de Cierre y Volumen',
    html_path='charts/close_vol_chart.html'
):
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    df = df.rename(columns=str.lower)
    df['date'] = pd.to_datetime(df['date'])

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.80, 0.20],
        vertical_spacing=0.03,
    )

    # --- Línea de cierre ---
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['close'],
        mode='lines',
        name='Close',
        line=dict(color='blue', width=1)
    ), row=1, col=1)

    # --- Volumen barra ---
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['volume'],
        marker_color='royalblue',      # Más claro y visual
        marker_line_color='blue',        # Borde oscuro
        marker_line_width=0.4,
        opacity=0.95,
        name='Volumen'
    ), row=2, col=1)


    fig.update_layout(
        dragmode='pan',
        title=titulo,
        width=1500,
        height=int(1400 * 0.6),
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=12, color="black"),
        plot_bgcolor='rgba(255,255,255,0.05)',
        paper_bgcolor='rgba(240,240,240,0.6)',
        showlegend=False,
        template='plotly_white',
        xaxis=dict(showgrid=False, linecolor='gray', linewidth=1),
        yaxis=dict(showgrid=True, linecolor='gray', linewidth=1),
        xaxis2=dict(showgrid=False, linecolor='gray', linewidth=1),
        yaxis2=dict(showgrid=True, linecolor='gray', linewidth=1),
    )

    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Gráfico Plotly guardado como '{html_path}'")

    import webbrowser
    webbrowser.open('file://' + os.path.realpath(html_path))

    return html_path

# Ejemplo de uso:
# plot_close_and_volume(df, titulo="KLTO Close y Volumen")
