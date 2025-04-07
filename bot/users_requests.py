import sqlite3
from contextlib import contextmanager


database = r'D:\codes\database\users.db'

@contextmanager
def get_db_connection():
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()

def user_in_base(connection: sqlite3.Connection, id):
    users = connection.cursor()
    users.execute('SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)', (id,))
    exists = users.fetchone()[0] == 1
    return exists

def add_user_to_base(connection: sqlite3.Connection, id, name, role):
    users = connection.cursor()
    users.execute('INSERT INTO Users (user_id, name, role) VALUES (?, ?, ?)', (id, name, role))
    connection.commit()

def upd_last_request(connection: sqlite3.Connection, id, last_request):
    users = connection.cursor()
    users.execute(
        "UPDATE users SET last_request = ? WHERE user_id = ?",
        (last_request, id)
    )
    connection.commit()

def get_last_request(connection: sqlite3.Connection, id):
    users = connection.cursor()
    users.execute("""
        SELECT last_request 
        FROM users 
        WHERE user_id = ?
    """, (id,))
    
    result = users.fetchone()
    
    print(result[0])
    
    return result[0] if result else None