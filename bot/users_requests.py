import sqlite3
from contextlib import contextmanager

from secret import database

@contextmanager
def get_db_connection():
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()

# добавляем юзера в БД
def add_user_to_base(connection: sqlite3.Connection, user_id, name):
    cursor = connection.cursor()

    cursor.execute('''
            INSERT INTO Users (user_id, name)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO NOTHING;
        ''', (user_id, name))
    connection.commit()

# меняем имя в БД
def upd_user_name(connection: sqlite3.Connection, user_id, name):
    cursor = connection.cursor()

    cursor.execute('UPDATE Users SET name = ? WHERE user_id = ?', (name, user_id))
    connection.commit()


# меняем роль в БД
def get_user_role(connection: sqlite3.Connection, user_id, role):
    users = connection.cursor()
    users.execute("""
            SELECT role 
            FROM Users 
            WHERE user_id = ?
    """, (user_id,))
    
    result = users.fetchone()
    return result[0] if result else None


# меняем роль в БД
def upd_user_role(connection: sqlite3.Connection, user_id, role):
    cursor = connection.cursor()

    cursor.execute('UPDATE Users SET role = ? WHERE user_id = ?', (role, user_id))
    connection.commit()