import pandas as pd
from sqlalchemy import create_engine

# Create connection
engine = create_engine('mysql+mysqlconnector://root:Plus7070@127.0.0.1/small_caps')

# Define tables to read
tables_to_read = ['prices']
dataframes = {}

# Read each table into a pandas DataFrame
for table in tables_to_read:
    query = f'SELECT * FROM {table}'
    dataframes[table] = pd.read_sql(query, engine)

# Dispose engine after use (optional)
engine.dispose()

# Display results
pd.set_option('display.width', 500)
for table_name, df in dataframes.items():
    print(f"Tabla: {table_name}")
    print(df.head())  # Preview data

# Optionally assign directly
prices = dataframes['prices']
