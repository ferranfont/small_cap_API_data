import pandas as pd
import plotly.graph_objs as go

# Leer el archivo resumen
df = pd.read_csv('outputs/bio_summary.csv')

# --- Grupos excluyentes ---
no_drop60 = df['drop60_date'].isna()
drop60_only = df['drop60_date'].notna() & df['drop80_date'].isna()
drop80_only = df['drop80_date'].notna() & df['drop90_date'].isna()
drop90 = df['drop90_date'].notna()

counts = [
    no_drop60.sum(),
    drop60_only.sum(),
    drop80_only.sum(),
    drop90.sum()
]
labels = [
    'No han perdido 60%',
    'Perdido 60-80%',
    'Perdido 80-90%',
    'Perdido >90%'
]
colors = ['gray', 'orange', 'salmon', 'red']

# --- 1. Barras segregadas ---
fig1 = go.Figure([go.Bar(x=labels, y=counts, marker_color=colors)])
fig1.update_layout(
    title='Acciones segregadas por pérdida desde máximo',
    yaxis_title='Número de acciones',
    xaxis_title='Categoría'
)
fig1.show()

# --- 2. Histograma de días hasta perder 90%, BARRAS FINAS ---
dias_drop90 = df.loc[drop90, 'days_from_90'].dropna().astype(int)
if len(dias_drop90) > 0:
    fig2 = go.Figure([
        go.Histogram(
            x=dias_drop90, 
            nbinsx=100,  # Más bins = barras más finas (ajusta a gusto)
            marker_color='yellow',
            opacity=0.8,
            marker_line_color='grey',  # Color del borde
            marker_line_width=1  
        )
    ])
    fig2.update_layout(
        title='Distribución de días hasta caída >90% desde máximo',
        xaxis_title='Días desde máximo hasta perder 90%',
        yaxis_title='Número de acciones'
    )
    fig2.show()
else:
    print("Ninguna acción ha perdido un 90% para mostrar el histograma de días.")
# --- 3. Histograma de días hasta el máximo desde IPO ---
dias_to_max = df['days_to_max'].dropna().astype(int)
if len(dias_to_max) > 0:
    fig3 = go.Figure([
        go.Histogram(
            x=dias_to_max,
            nbinsx=100,              # Barras finas
            marker_color='blue',     # Color de las barras (elige el que prefieras)
            opacity=0.8,
            marker_line_color='grey',
            marker_line_width=1
        )
    ])
    fig3.update_layout(
        title='Distribución de días hasta el máximo desde IPO',
        xaxis_title='Días desde IPO hasta máximo',
        yaxis_title='Número de acciones'
    )
    fig3.show()
else:
    print("No hay datos suficientes para mostrar el histograma de días hasta máximo.")
