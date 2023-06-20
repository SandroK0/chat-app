import sqlite3


conn = sqlite3.connect('Database.sqlite')

c = conn.cursor()


test = c.execute("SELECT * FROM Users").fetchall()

print(test)