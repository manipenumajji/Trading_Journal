import sqlite3
connection=sqlite3.connect("trades.db")
cursor=connection.cursor()
cursor.execute("""CREATE TABLE trades(
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
connection.close()
