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
def add_user_to_base(connection: sqlite3.Connection, user_id, name, user_name):
    """Adds user to db | Добавляет пользователя в бд"""
    cursor = connection.cursor()

    cursor.execute("""
            INSERT INTO Users (user_id, name, user_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO NOTHING;
        """, (user_id, name, user_name))
    connection.commit()


# меняем имя в БД
def upd_user_name(connection: sqlite3.Connection, user_id, name):
    """Updates users name in db | Обновляет имя пользователя в бд"""
    cursor = connection.cursor()

    cursor.execute("UPDATE Users SET name = ? WHERE user_id = ?", (name, user_id))
    connection.commit()


# меняем роль в БД
def get_user_role(connection: sqlite3.Connection, user_id):
    """Gets users role in db | Получает роль пользователя в бд"""
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
    """Updates users role | Меняет роль пользователя в бд"""
    cursor = connection.cursor()
    cursor.execute("UPDATE Users SET role = ? WHERE user_id = ?", (role, user_id))
    connection.commit()


def get_user_name_by_user_id(connection: sqlite3.Connection, user_id):
    """Получает имя юзера по его id"""
    users = connection.cursor()
    users.execute("""
            SELECT name 
            FROM Users 
            WHERE user_id = ?
    """, (user_id,))
    result = users.fetchone()
    return result[0] if result else None


# меняем роль в БД
def get_user_user_name(connection: sqlite3.Connection, user_id):
    """Gets users user_name in db | Получает user_name пользователя в бд"""
    users = connection.cursor()
    users.execute("""
            SELECT user_name 
            FROM Users 
            WHERE user_id = ?
    """, (user_id,))

    result = users.fetchone()
    return result[0] if result else None


# меняем роль в БД
def get_user_id_by_user_name(connection: sqlite3.Connection, user_name):
    """Gets users user_id in db by username | Получает user_name пользователя в бд по юзернейму"""
    users = connection.cursor()
    users.execute("""
            SELECT user_id 
            FROM Users 
            WHERE user_name = ?
    """, (user_name,))

    result = users.fetchone()
    return result[0] if result else None
