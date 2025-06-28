import os
import pandas as pd
from ib_connector_single_call import get_ibkr_data
from ib_connector_loop import get_ibkr_data_loop
from chart_volume import plot_close_and_volume
from fill_SQL_from_df import insertar_df_en_mysql
from chart_visor_resampled import plot_close_and_volume_resample

# 0- Leer tickers desde el CSV
df_tickers = pd.read_csv("../DATA/smal_caps_bio.csv")
tickers = df_tickers['Ticker'].dropna().unique().tolist()

tickers = [
    'RGLS', 'NVAX', 'MENS'
]
# Lista de tickers ya insertados en SQL

'''
existing = [
    "AARD", "ABCL", "ABEO", "ABSI", "ABUS", "ABVX", "ADCT", "ADPT", "ALMS", "ALT",
    "AMLX", "ANAB", "ARCT", "ARDX", "ARQT", "ARVN", "ATAI", "ATXS", "ATYR", "AURA",
    "AUPH", "AUTL", "AVBP", "AVXL", "BCAX", "BCYC", "BEAM", "BHVN", "BLTE", "BNTC",
    "CAPR", "CELC", "CGEM", "CLDX", "CMPX", "CNTA", "COGT", "CRMD", "CRVS", "CTMX",
    "CVAC", "DAWN", "DNA", "DNTH", "DYN", "ELVN", "ERAS", "ETNB", "EWTX", "EYPT",
    "FOLD", "FTRE", "FULC", "GERN", "GHRS", "GLPG", "GPCR", "GYRE", "HRMY", "HRTX",
    "HUMA", "IDYA", "IMCR", "IMNM", "IMTX", "INVA", "IOVA", "IRON", "ITOS", "IVA",
    "JANX", "KALV", "KLTO", "KROS", "KURA", "LENZ", "LIMN", "LQDA", "MAZE", "MBX",
    "MDXG", "MENS", "MESO", "MGTX", "MLYS", "MNKD", "MNMD", "MREO", "MRVI", "NTLA",
    "NRIX", "NUVB", "OP","NAGE","NVAX"
]


# Filtrar los que no están en la lista de ya presentes
tickers = [ticker for ticker in tickers if ticker not in existing]

'''
print("Tickers to process:", tickers)



# 1- Crear carpeta de salida
output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)

# 2- Iterar sobre cada ticker
for SYMBOL in tickers:
    print(f"\n🔁 Processing: {SYMBOL}")

    try:
        # Obtener datos de IBKR
        df = get_ibkr_data_loop(
            symbol=SYMBOL,
            bar_size='1 min',
            what_to_show='TRADES',
            use_rth=True,
            client_id=14
        )

        # Añadir columna de ticker
        df['ticker'] = SYMBOL
        cols = ['ticker'] + [col for col in df.columns if col != 'ticker']
        df = df[cols]

        # Guardar CSV individual
        csv_path = os.path.join(output_dir, f'{SYMBOL}_data.csv')
        df.to_csv(csv_path, index=False)
        print(f"✅ CSV saved for {SYMBOL}")

        # Insertar en base de datos
        insertar_df_en_mysql(df, ticker=SYMBOL)
        print(f"✅ Inserted into MySQL for {SYMBOL}")

        # Graficar resampleado
        plot_close_and_volume_resample(df, symbol, timeframe)

        print(f"✅ Chart generated for {SYMBOL}")

    except Exception as e:
        print(f"❌ Error processing {SYMBOL}: {e}")
