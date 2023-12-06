import sqlite3

def create_db():
    with sqlite3.connect('email_db') as db:
        cursor = db.cursor()
        
        query = '''CREATE TABLE IF NOT EXISTS email (
                   No int,
                   UIDL varchar(17) PRIMARY KEY,
                   SenderMail varchar(30),
                   Subject varchar(100),
                   Folder varchar(20),
                   IsRead int
                );'''
        cursor.execute(query)
        
        cursor.close()