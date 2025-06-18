import pandas as pd
from sqlalchemy import create_engine

# ✅ Step 1: Create the connection
engine = create_engine('mysql+mysqlconnector://root:Plus7070@127.0.0.1/small_caps')

# ✅ Step 2: Run a SQL query and load into pandas
query = "SELECT * FROM prices"
df = pd.read_sql(query, engine)

# ✅ Step 3: Use the data (e.g., show head)
print(df.head())
print('hola')
# ✅ Step 4: Close/dispose connection
engine.dispose()
