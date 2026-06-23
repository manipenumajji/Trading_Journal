import sqlite3
def initialize_database():

    connection = sqlite3.connect("trades.db")

    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades(
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

    connection.close()
def add_trade():
    symbol=input("enter symbol: ").strip().upper()
    if not symbol:
        print("symbol cannot be empty!")
        return
    side=input("enter Side: ").strip().upper()
    try:
        entry_price=float(input("Enter entry_price: "))
        exit_price=float(input("Enter exit_price: "))
        quantity=float(input("Enter quantity: "))
    except ValueError:
        print("enter valid price!")
        return    
    if entry_price<=0 or exit_price<=0 or quantity<=0:
        print("The value must be grater than 0!")
        return
    if side=="BUY":
        pnl=(exit_price-entry_price)*quantity
    elif side=="SELL":
        pnl=(entry_price-exit_price)*quantity
    else:
        print("Invalid side!") 
        return   
    pnl=round(pnl,2)
    print(f"""
symbol     :{symbol}
side       :{side}
entry_price:{entry_price}
exit_price :{exit_price}
quantity   :{quantity}
pnl        :{pnl}
""")    
    connection=sqlite3.connect("trades.db")
    cursor=connection.cursor()
    cursor.execute("""INSERT INTO trades(symbol,side,entry_price,exit_price,quantity,pnl)
                   VALUES(?,?,?,?,?,?)""",
                   (symbol,side,entry_price,exit_price,quantity,pnl))
    connection.commit()
    print("Trade Saved Sucessfully!")
    connection.close()    
def view_trades():
    connection=sqlite3.connect("trades.db")
    cursor=connection.cursor()
    cursor.execute("""SELECT * FROM trades""")
    trades=cursor.fetchall()
    if not trades:
        print("No trades found!")
        connection.close()  
        return
    else:
        for trade in trades:
            print(f"""
ID         : {trade[0]}
Symbol     : {trade[1]}
Side       : {trade[2]}
Entry      : {trade[3]}
Exit       : {trade[4]}
Quantity   : {trade[5]}
PnL        : {trade[6]}
--------------------
""")
    connection.close()       
initialize_database()      
while True:
    print("\n Trading journal\n"
    "1.add trade\n"
    "2.view trades\n"
    "3.exit")
    try:
        choice=int(input("enter your choice: "))
    except ValueError:
        print("enter number!")
        continue    
    if choice == 1:
        add_trade()

    elif choice == 2:
        view_trades()

    elif choice == 3:
        print("Good Luck Comeback Stronger!")
        break

    else:
        print("Invalid Choice") 
   