import sqlite3
while True:
    print("\n Trade journal"
          "1.Add trades",
          "2.view trades",
          "3.exit")
    try:
        choice=int(input("ENTER your choice: "))
    except ValueError:
        print("Enter Number!")  
        continue  
    def add_trade():
        if choice==1:
            symbol=input("ENTER symbol:").strip().upper()
            side=input("ENTER side:")
            entry_price=float(input("ENTER entry_price:"))
            exit_price=float(input("ENTER exit_price:"))
            quantity=float(input("ENTER quantity:"))
            if entry_price<=0 or exit_price<=0 or quantity<=0:
                print("price must be grater than 0")
                continue
            side=side.strip().upper()
            if side=="BUY":
                pnl=(exit_price-entry_price)*quantity
            elif side=="SELL":
                pnl=(entry_price-exit_price)*quantity
        else:
            print("Invalid side!") 
            continue   
        pnl=round(pnl,2)    
        
        print(f"""
Symbol      : {symbol}
Side        : {side}
Entry Price : {entry_price}
Exit Price  : {exit_price}
Quantity    : {quantity}
PnL         : {pnl}
""")     
        

        connection = sqlite3.connect("trades.db")
        cursor = connection.cursor()

        cursor.execute("""
INSERT INTO trades
(symbol, side, entry_price, exit_price, quantity, pnl)
VALUES (?, ?, ?, ?, ?, ?)
""", (symbol, side, entry_price, exit_price, quantity, pnl))

        connection.commit()

        connection.close()

        print("Trade Saved Successfully!")  
    def view_trade():  
        if choice==2:
            connection=sqlite3.connect("trades.db")
            cursor=connection.cursor()
            cursor.execute("""SELECT * FROM trades""")
            trades=cursor.fetchall()
            for trade in trades:
                print(trade)
            connection.close()         
     
    if choice==3:
        print("good luck comeback stronger!")
        break
    else:
        print("Invalid choice")           