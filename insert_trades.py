import sqlite3
connection=sqlite3.connect("trades.db")
cursor=connection.cursor()
cursor.execute("""INSERT INTO trades(symbol,side,entry_price,exit_price,quantity,pnl)
VALUES('ETHUSDT',
'SELL',
3000,
2900,
0.1,
100)""")
connection.commit()
print("trade inserted sucessfully")
connection.close()