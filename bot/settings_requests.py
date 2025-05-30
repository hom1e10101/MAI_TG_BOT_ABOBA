import sqlite3
from contextlib import contextmanager
from secret import database


@contextmanager
def get_db_connection():
    """Подключение бд"""
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def add_user_settings(connection: sqlite3.Connection, user_id):
    """Добавляем юзера в таблицу сеттингс"""
    cursor = connection.cursor()
    cursor.execute('''
            INSERT INTO Settings (user_id)
            VALUES (?)
            ON CONFLICT(user_id) DO NOTHING;
        ''', (user_id,))
    connection.commit()


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


def upd_user_message_to_edit(connection: sqlite3.Connection, user_id, message_id):
    """Updates id of message that will be edited | Обновляет id сообщения, которое будет редактировать бот"""
    users = connection.cursor()
    users.execute("""
        UPDATE Settings SET message_to_edit = ? WHERE user_id = ? 
    """, (message_id, user_id))
    connection.commit()


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


def upd_user_city(connection: sqlite3.Connection, user_id, city):
    """Updates city where user is searching | Обновляет город, в котором необходимо искать места"""
    users = connection.cursor()
    users.execute("""
        UPDATE Settings SET city = ? WHERE user_id = ? 
    """, (city, user_id))
    connection.commit()


def get_user_distance(connection: sqlite3.Connection, user_id):
    """Получаем желаемую дистанцию поиска"""
    users = connection.cursor()
    users.execute("""
        SELECT distance 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))

    result = users.fetchone()
    return result[0] if result else None


def upd_user_distance(connection: sqlite3.Connection, user_id, distance):
    """Обновляем желаемую дистанцию поиска"""
    users = connection.cursor()
    users.execute("""
        UPDATE Settings SET distance = ? WHERE user_id = ? 
    """, (distance, user_id))
    connection.commit()


def upd_user_last_request(connection: sqlite3.Connection, user_id, last_request):
    """Обновляем последний запрос пользователя"""
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE Settings SET last_request = ? WHERE user_id = ?",
        (last_request, user_id)
    )
    connection.commit()


def get_user_last_request(connection: sqlite3.Connection, user_id):
    """Получаем последний запрос пользователя"""
    users = connection.cursor()
    users.execute("""
        SELECT last_request 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))

    result = users.fetchone()
    return result[0] if result else None


def upd_user_status(connection: sqlite3.Connection, user_id, status):
    """Обновляем статус пользователя"""
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE Settings SET status = ? WHERE user_id = ?",
        (status, user_id)
    )
    connection.commit()


def get_user_status(connection: sqlite3.Connection, user_id):
    """Получаем статус пользователя"""
    users = connection.cursor()
    users.execute("""
        SELECT status 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))

    result = users.fetchone()
    return result[0] if result else None


def upd_user_request_ids(connection: sqlite3.Connection, user_id, places_ids):
    """Обновляем запрашиваемые ids мест"""
    cursor = connection.cursor()

    s = ' '.join(map(str, places_ids))
    cursor.execute(f"""
        UPDATE Settings
        SET request_ids = ?, current_index = 0
        WHERE user_id = ?
    """, (s, user_id))

    connection.commit()


def get_user_request_ids(connection: sqlite3.Connection, user_id) -> list:
    """Возвращает список ID мест пользователя"""
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT request_ids 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    if not row:
        return []
    ids = list(map(int, row[0].split()))
    return ids


def get_current_index(connection: sqlite3.Connection, user_id):
    """Получаем нынешний индекс"""
    users = connection.cursor()
    users.execute(f"""
        SELECT current_index 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))

    result = users.fetchone()
    return result[0] if result else None


def upd_current_index(connection: sqlite3.Connection, user_id, curr_ind):
    """Обновляем индекс"""
    users = connection.cursor()
    users.execute(f"""
        UPDATE Settings SET current_index = ? WHERE user_id = ? 
    """, (curr_ind, user_id))
    connection.commit()


def upd_user_request_comment_ids(connection: sqlite3.Connection, user_id, comment_ids):
    """Обновляем индекс комментариев"""
    cursor = connection.cursor()

    s = ' '.join(map(str, comment_ids))
    cursor.execute(f"""
        UPDATE Settings
        SET request_comment_ids = ?, current_comment_index = 0
        WHERE user_id = ?
    """, (s, user_id))

    connection.commit()


def get_user_request_comment_ids(connection: sqlite3.Connection, user_id) -> list:
    """Возвращает список ID мест пользователя"""
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT request_comment_ids
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    if not row:
        return []
    ids = list(map(int, row[0].split()))
    return ids


def get_current_comment_index(connection: sqlite3.Connection, user_id):
    """Получаем индекс комментариев"""
    users = connection.cursor()
    users.execute(f"""
        SELECT current_comment_index 
        FROM Settings 
        WHERE user_id = ?
    """, (user_id,))

    result = users.fetchone()
    return result[0] if result else None


def upd_current_comment_index(connection: sqlite3.Connection, user_id, curr_ind):
    """Обновляем индекс комментариев"""
    users = connection.cursor()
    users.execute(f"""
        UPDATE Settings SET current_comment_index = ? WHERE user_id = ? 
    """, (curr_ind, user_id))
    connection.commit()