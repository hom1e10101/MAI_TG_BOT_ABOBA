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

'''обращения к таблице'''
# комментировали ли это место раньше True/False
def commented(connection: sqlite3.Connection, place_id):
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE place_id = ?', (place_id,))
    return cursor.fetchone() is not None

# возвращаем среднее арифм рейтинга места
def get_place_rating(connection: sqlite3.Connection, place_id):
    cursor = connection.cursor()
    cursor.execute('SELECT AVG(rating) FROM Comments WHERE place_id = ?', (place_id,))
    return cursor.fetchone()[0]

# возвращаем список id комментов юзера
def get_user_comment_ids(connection: sqlite3.Connection, user_id):
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE user_id = ?', (user_id,))
    return [row[0] for row in cursor.fetchall()]

# возвращаем список id комментов на место
def get_place_comment_ids(connection: sqlite3.Connection, place_id):
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE place_id = ?', (place_id,))
    return [row[0] for row in cursor.fetchall()]

# возвращаем true если юзер комментил данное место
def commented_by_user(connection: sqlite3.Connection, user_id, place_id):
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE user_id = ? AND place_id = ?', (user_id, place_id))
    return cursor.fetchone() is not None

# возвращаем 5 комментов с самым высоким рейтингом на это место
def get_comments_of_place(connection: sqlite3.Connection, place_id):
    cursor = connection.cursor()
    cursor.execute('''
        SELECT Comments.comment_id, Comments.text, Users.name 
        FROM Comments
        JOIN Users ON Comments.user_id = Users.user_id 
        WHERE place_id = ?
        ORDER BY rating DESC
        LIMIT 5
    ''', (place_id,))
    results = cursor.fetchall()
    return results


'''изменение в таблице'''
# добавляем коммент
def add_comment(connection: sqlite3.Connection, user_id, place_id, text, rating):
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Comments (user_id, place_id, text, rating) VALUES (?, ?, ?, ?)', (user_id, place_id, text, rating))
    connection.commit()

# замена коммента
def edit_comment(connection: sqlite3.Connection, user_id, place_id, text, rating):
    cursor = connection.cursor()
    cursor.execute('SELECT comment_id FROM Comments WHERE user_id = ? AND place_id = ?', (user_id, place_id))
    result = cursor.fetchone()
    if result == None:
        print("нет такого коммента")
    comm_id = result[0]
    cursor.execute('UPDATE Comments SET text = ?, rating = ? WHERE comment_id = ?', (text, rating, comm_id))
    connection.commit()