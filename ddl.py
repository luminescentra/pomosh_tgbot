import sqlite3
from datetime import datetime

conn = sqlite3.connect('Posts.sql')
cursor = conn.cursor()
cursor.execute("create table shares ( name text , tag text, description text, number text, time text, post_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT)")
cursor.execute("create table needs ( name text , tag text, description text, number text, time text, post_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT )")


conn.commit()
cursor.execute('select * from shares')

from pprint import pprint
print("Делятся помощью")
for row in cursor.fetchall():
    print('{} {} {} {} {} {}'.format(row[0] , row[1] , row[2] , row[3] , row[4 ], row[5]))
cursor.execute('select * from needs')
print('\n\nНуждаются в помощи')
for row in cursor.fetchall():
    print('{} {} {} {} {} {}'.format(row[0] , row[1] , row[2] , row[3] , row[4 ], row[5]))
