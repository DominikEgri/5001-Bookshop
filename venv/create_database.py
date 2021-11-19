import sqlite3

conn = sqlite3.connect('database.db')
#print "Opened database successfully";

conn.execute('CREATE TABLE Users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, password TEXT NOT NULL)')
#print "Table created successfully";
conn.close()

con = sqlite3.connect('database.db')

con.execute('INSERT INTO Users(name, password ) VALUES(?,?)', ("admin", "p455w0rd"))
con.commit()
con.close()
