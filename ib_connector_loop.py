# Este código itera sobre el vector con rangos de fecha y hace una call a la API de Interactve Brokers

from ib_insync import *
import pandas as pd
import time
    

def get_ibkr_data_loop(
    symbol='AAPL',
    exchange='SMART',
    currency='USD',
    bar_size='1 min',
    what_to_show='TRADES',
    use_rth=True,
    client_id=14,
    path_to_end_dates="outputs/endDateTime_blocks.txt",
    delay_seconds=10  # Pause between requests
):
    # Load endDateTime values
    with open(path_to_end_dates, "r") as f:
        end_dates = [line.strip() for line in f if line.strip()]

    ib = IB()
    ib.connect('127.0.0.1', 7496, clientId=client_id)

    stock = Stock(symbol, exchange, currency)
    all_data = pd.DataFrame()

    for i, end_dt in enumerate(end_dates):
        print(f"\n🔁 Requesting block {i+1}/{len(end_dates)}: {end_dt}")
        try:
            bars = ib.reqHistoricalData(
                stock,
                endDateTime=end_dt,
                durationStr='10 D',
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=use_rth,
                formatDate=1
            )

            df = util.df(bars)
            if not df.empty:
                all_data = pd.concat([all_data, df])
                print(f"✅ {len(df)} rows from {df['date'].min()} to {df['date'].max()}")
            else:
                print(f"⚠️ No data returned for {end_dt}")
        except Exception as e:
            print(f"❌ Error fetching data for {end_dt}: {e}")

        time.sleep(delay_seconds)  # ⏸ Pause to avoid rate limit

    ib.disconnect()

    # Save to file
    output_path = "outputs/ib_data_full.csv"
    all_data.to_csv(output_path, index=False)
    print(f"\n💾 Final dataset saved to '{output_path}' ({len(all_data)} rows)")

    return all_data
