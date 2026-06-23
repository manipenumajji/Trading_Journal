import sqlite3
import pandas as pd
connection=sqlite3.connect("trades.db")
cursor=connection.cursor()
cursor.execute(""" CREATE TABLE IF NOT EXISTS trades(
               id INTEGER PRIMARY KEY,
               symbol TEXT,
               side TEXT,
               entry_price REAL,
               exit_price REAL,
               quantity REAL,
               pnl REAL
               )
               """)
connection.commit()
print("Trades table created sucessfully")
df = pd.read_sql_query(
    "SELECT * FROM trades",
    connection
)
print(df)
print("\nTotal PnL:")
print(df["pnl"].sum())
connection.close()
