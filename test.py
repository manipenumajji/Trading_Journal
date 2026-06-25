# run this once in python shell or as a script
import sqlite3
conn = sqlite3.connect("trades.db")  # adjust path if different
conn.execute("DELETE FROM trades WHERE source = 'coindcx'")
conn.execute("DELETE FROM sync_log")
conn.commit()
conn.close()
print("Cleaned.")