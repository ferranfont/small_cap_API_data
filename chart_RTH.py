import os
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import webbrowser

def plot_close_and_volume_segmented(df, titulo="Solo RTH compacto"):
    os.makedirs('charts', exist_ok=True)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.8, 0.2],
        vertical_spacing=0.03,
    )

    # Agrupa por día pero concatena todo para no dejar huecos en X
    # Usamos axis category en X para que no haya huecos de fechas
    # pero mantenemos los tooltips correctos

    # Línea de cierre
    fig.add_trace(go.Scatter(
        x=df['date'].astype(str),  # <= Como string para usar xaxis type category
        y=df['close'],
        mode='lines',
        line=dict(width=1, color='blue'),
        name='Close',
        showlegend=False
    ), row=1, col=1)

    # Volumen
    fig.add_trace(go.Bar(
        x=df['date'].astype(str),
        y=df['volume'],
        marker_color='royalblue',
        marker_line_color='blue',
        marker_line_width=0.4,
        opacity=0.95,
        name='Volumen',
        showlegend=False
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
        xaxis=dict(
            showgrid=False, 
            linecolor='gray', 
            linewidth=1,
            type='category'  # <= Esta línea hace que no haya huecos en fechas
        ),
        yaxis=dict(showgrid=True, linecolor='gray', linewidth=1),
        xaxis2=dict(
            showgrid=False, 
            linecolor='gray', 
            linewidth=1,
            type='category'  # <= También aquí
        ),
        yaxis2=dict(showgrid=True, linecolor='gray', linewidth=1),
    )
    html_path = 'charts/close_vol_chart_rth_segmented.html'
    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Gráfico Plotly guardado como '{html_path}'")
    webbrowser.open('file://' + os.path.realpath(html_path))

# USO:
# plot_close_and_volume_segmented(df_rth)
