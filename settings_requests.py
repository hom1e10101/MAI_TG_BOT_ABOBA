import sqlite3
from contextlib import contextmanager

from secret import database


@contextmanager
def get_db_connection():
    """db connection | Подключение бд"""
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def add_user_settings(connection: sqlite3.Connection, user_id):
    """Adds user settings | Добавляет настройки пользователя"""
    cursor = connection.cursor()

    cursor.execute('''
            INSERT INTO Settings (user_id)
            VALUES (?)
            ON CONFLICT(user_id) DO NOTHING;
        ''', (user_id,))
    connection.commit()


def get_user_message_to_edit(connection: sqlite3.Connection, user_id):
    """Gets id of message that bot wants to edit | Получение идентификатора сообщенияЮ для редактирования ботом"""
    users = connection.cursor()
    users.execute("""
        SELECT message_to_edit 
        FROM Settings
        WHERE user_id = ?
    """, (user_id,))

    result = users.fetchone()
    return result[0] if result else None


def upd_user_message_to_edit(connection: sqlite3.Connection, user_id, message_id):
    """Updates id of message that was redacted by bot | Обновление идентификатора сообщения, которое редактировал бот"""
    users = connection.cursor()
    users.execute("""
        UPDATE Settings SET message_to_edit = ? WHERE user_id = ? 
    """, (message_id, user_id))
    connection.commit()


def get_user_city(connection: sqlite3.Connection, user_id):
    """Gets users city | Получает город пользователя"""
    users = connection.cursor()
    users.execute("""
        SELECT city 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))

    result = users.fetchone()
    return result[0] if result else None


def upd_user_city(connection: sqlite3.Connection, user_id, city):
    """Updates users city | Обновляет город пользователя"""
    users = connection.cursor()
    users.execute("""
        UPDATE Settings SET city = ? WHERE user_id = ? 
    """, (city, user_id))
    connection.commit()


def get_user_distance(connection: sqlite3.Connection, user_id):
    """Gets user search distance | Получает расстояние поиска места пользователя"""
    users = connection.cursor()
    users.execute("""
        SELECT distance 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))

    result = users.fetchone()
    return result[0] if result else None


def upd_user_distance(connection: sqlite3.Connection, user_id, distance):
    """Updates users search distance | Обновляет расстояние поиска места пользователя"""
    users = connection.cursor()
    users.execute("""
        UPDATE Settings SET distance = ? WHERE user_id = ? 
    """, (distance, user_id))
    connection.commit()


def upd_user_last_request(connection: sqlite3.Connection, user_id, last_request):
    """Updates last users request | Обновляет последний запрос пользователя"""
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE Settings SET last_request = ? WHERE user_id = ?",
        (last_request, user_id)
    )
    connection.commit()


def get_user_last_request(connection: sqlite3.Connection, user_id):
    """Gets last users request | Получает последний запрос пользователя"""
    users = connection.cursor()
    users.execute("""
        SELECT last_request 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))

    result = users.fetchone()
    return result[0] if result else None
