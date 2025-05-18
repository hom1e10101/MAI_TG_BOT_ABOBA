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



def add_user_settings(connection: sqlite3.Connection, user_id):
    cursor = connection.cursor()

    cursor.execute('''
            INSERT INTO Settings (user_id)
            VALUES (?)
            ON CONFLICT(user_id) DO NOTHING;
        ''', (user_id,))
    connection.commit()

# получаем id сообщения, которое редактирует бот
def get_user_message_to_edit(connection: sqlite3.Connection, user_id):
    """Gets id of message that will be edited | Получает id сообщения, которое будет редактировать бот"""
    users = connection.cursor()
    users.execute("""
        SELECT message_to_edit 
        FROM Settings
        WHERE user_id = ?
    """, (user_id,))
    
    result = users.fetchone()
    return result[0] if result else None

# обновляем id сообщения, которое редактирует бот
def upd_user_message_to_edit(connection: sqlite3.Connection, user_id, message_id):
    """Updates id of message that will be edited | Обновляет id сообщения, которое будет редактировать бот"""
    users = connection.cursor()
    users.execute("""
        UPDATE Settings SET message_to_edit = ? WHERE user_id = ? 
    """, (message_id, user_id))
    connection.commit()



# получаем city юзера
def get_user_city(connection: sqlite3.Connection, user_id):
    """Gets city where user is searching | Получает город, в котором необходимо искать места"""
    users = connection.cursor()
    users.execute("""
        SELECT city 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))
    
    result = users.fetchone()
    return result[0] if result else None

# обновляем city юзера
def upd_user_city(connection: sqlite3.Connection, user_id, city):
    """Updates city where user is searching | Обновляет город, в котором необходимо искать места"""
    users = connection.cursor()
    users.execute("""
        UPDATE Settings SET city = ? WHERE user_id = ? 
    """, (city, user_id))
    connection.commit()


# получаем distance юзера
def get_user_distance(connection: sqlite3.Connection, user_id):
    users = connection.cursor()
    users.execute("""
        SELECT distance 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))
    
    result = users.fetchone()
    return result[0] if result else None

# обновляем city юзера
def upd_user_distance(connection: sqlite3.Connection, user_id, distance):
    users = connection.cursor()
    users.execute("""
        UPDATE Settings SET distance = ? WHERE user_id = ? 
    """, (distance, user_id))
    connection.commit()



# обновляем последний запрос юзера
def upd_user_last_request(connection: sqlite3.Connection, user_id, last_request):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE Settings SET last_request = ? WHERE user_id = ?",
        (last_request, user_id)
    )
    connection.commit()

# получаем последний запрос пользователя
def get_user_last_request(connection: sqlite3.Connection, user_id):
    users = connection.cursor()
    users.execute("""
        SELECT last_request 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))
    
    result = users.fetchone()
    return result[0] if result else None



# обновляем последний запрос юзера
def upd_user_status(connection: sqlite3.Connection, user_id, status):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE Settings SET status = ? WHERE user_id = ?",
        (status, user_id)
    )
    connection.commit()

# получаем последний запрос пользователя
def get_user_status(connection: sqlite3.Connection, user_id):
    users = connection.cursor()
    users.execute("""
        SELECT status 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))
    
    result = users.fetchone()
    return result[0] if result else None