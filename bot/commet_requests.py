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

'''обращения к таблице'''
def commented(connection: sqlite3.Connection, place_id):
    """Checks if place already commented | Проверяет, были ли уже комментарии на место"""
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE place_id = ?', (place_id,))
    return cursor.fetchone() is not None

def get_place_rating(connection: sqlite3.Connection, place_id):
    """Gets the average rating for place | Получает среднюю оценку места"""
    cursor = connection.cursor()
    cursor.execute('SELECT AVG(rating) FROM Comments WHERE place_id = ? AND rating != 0', (place_id,))
    return cursor.fetchone()[0]

def get_user_comment_ids(connection: sqlite3.Connection, user_id):
    """Gets id's of users comments | Получает идентификаторы комментариев пользователя"""
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE user_id = ?', (user_id,))
    return [row[0] for row in cursor.fetchall()]

def commented_by_user(connection: sqlite3.Connection, user_id, place_id):
    """Checks if user have already commented a place | Проверяет, комментировал ли пользователь данное место"""
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE user_id = ? AND place_id = ?', (user_id, place_id))
    return cursor.fetchone() is not None

def get_comments_of_place(connection: sqlite3.Connection, place_id):
    """Gets comments ids for place | Выводит id комментариев о месте"""
    cursor = connection.cursor()
    cursor.execute('''
        SELECT comment_id 
        FROM Comments
        WHERE place_id = ?
        ORDER BY rating DESC
    ''', (place_id,))
    return [row[0] for row in cursor.fetchall()]


'''изменение в таблице'''
def add_comment(connection: sqlite3.Connection, user_id, place_id, text, rating):
    """Add users comment to db | Добавляет комментарий пользователя в бд"""
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Comments (user_id, place_id, text, rating) VALUES (?, ?, ?, ?)', (user_id, place_id, text, rating))
    connection.commit()

def edit_comment(connection: sqlite3.Connection, user_id, place_id, text):
    """Edits comment | Редактирует комментарий"""
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE user_id = ? AND place_id = ?', (user_id, place_id))
    result = cursor.fetchone()
    if result == None:
        print("нет такого коммента")
        return
    comm_id = result[0]
    cursor.execute('UPDATE Comments SET text = ? WHERE comment_id = ?', (text, comm_id))
    connection.commit()


def edit_comment_rating(connection: sqlite3.Connection, user_id, place_id, rating):
    """Edits comment | Редактирует рейтинг в комментарии"""
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE user_id = ? AND place_id = ?', (user_id, place_id))
    result = cursor.fetchone()
    if result == None:
        print("нет такого коммента")
        return
    comm_id = result[0]
    cursor.execute('UPDATE Comments SET rating = ? WHERE comment_id = ?', (rating, comm_id))
    connection.commit()

    
def edit_comment_text(connection: sqlite3.Connection, user_id, place_id, text):
    """Edits comment | Редактирует текст комментария"""
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE user_id = ? AND place_id = ?', (user_id, place_id))
    result = cursor.fetchone()
    if result == None:
        print("нет такого коммента")
        return
    comm_id = result[0]
    cursor.execute('UPDATE Comments SET text = ? WHERE comment_id = ?', (text, comm_id))
    connection.commit()

def get_comment_by_comment_id(connection: sqlite3.Connection, comment_id):
    """Получаем все данные о комментарии по его id"""
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM Comments WHERE comment_id = ?", 
        (comment_id,)
    )
    if (row := cursor.fetchone()) is not None:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    
    return None

def delete_comment(connection: sqlite3.Connection, comment_id):
    """delets comment | удаляет коммент"""
    cursor = connection.cursor()
    cursor.execute(f"SELECT 1 FROM Comments WHERE comment_id = ?", (comment_id,))
    result = cursor.fetchone()
    if result == None:
        print("нет такого коммента")
        return
    cursor.execute(
        f"DELETE FROM Comments WHERE comment_id = ?", 
        (comment_id,)
    )
    connection.commit()