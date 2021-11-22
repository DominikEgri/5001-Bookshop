import sqlite3

conn = sqlite3.connect('database.db')
#print "Opened database successfully";

conn.execute('CREATE TABLE Users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, password TEXT NOT NULL)')
conn.execute('CREATE TABLE Books (isbn13 TEXT(13) NOT NULL UNIQUE PRIMARY KEY, title TEXT(128) NOT NULL UNIQUE, author TEXT(128) NOT NULL, releaseDate TEXT NOT NULL, description TEXT(1024) NOT NULL, image TEXT NOT NULL, price INTEGER(100) NOT NULL, quantity INTEGER NOT NULL)')
#print "Table created successfully";
conn.close()

con = sqlite3.connect('database.db')

con.execute('INSERT INTO Users(name, password ) VALUES(?,?)', ("admin", "p455w0rd"))
con.execute('INSERT INTO Books(isbn13, title, author, releaseDate, description, image, price, quantity) VALUES(?, ?, ?, ?, ?, ? , ?, ?)', ("111111", "something", "authorname", "22-01-20020", "description content", "image-name", 10, 20))
con.commit()
con.close()


