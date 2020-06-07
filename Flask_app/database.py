import sqlite3  
  
con = sqlite3.connect("players.db")  
print("Database opened successfully")  
  
con.execute("create table teams (id INTEGER UNIQUE,tname1 TEXT,tname2 TEXT)")  
  
print("Table created successfully")  
  
con.close()  