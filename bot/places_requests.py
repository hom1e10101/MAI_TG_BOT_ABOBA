import sqlite3
from contextlib import contextmanager

from secret import database

@contextmanager
def get_places_db_connection():
    """Connection to db | Подключаемся к бд"""
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()

# получаем адресс по названию места
def get_address_by_name(connection: sqlite3.Connection, name):
    """Gets place's address by its name | Получает адресс места по его названию"""
    places = connection.cursor()
    query = "SELECT address FROM Places WHERE name = ?"
    places.execute(query, (name,))
    result = places.fetchone()
    return result[0] if result else None

# получаем город места по названию
def get_city_by_name(connection: sqlite3.Connection, name):
    """Gets city's name by place name | Получает название города, по названию места"""
    places = connection.cursor()
    query = "SELECT city FROM Places WHERE name = ?"
    places.execute(query, (name,))
    result = places.fetchone()
    return result[0] if result else None

# получаем True/False если место уже есть в БД
def place_in_base(connection: sqlite3.Connection, name, city, address):
    """Checks existence of a place in bd | Проверяет наличие места в бд"""
    places = connection.cursor()
    places.execute('SELECT EXISTS(SELECT 1 FROM Places WHERE name = ?)', (name,))
    exists = places.fetchone()[0] == 1
    if (exists) :
        if get_city_by_name(connection, name) == city and get_address_by_name(connection, name) == address:
            return 1
    return 0

# добавляем место в БД по имени и адрессу
def add_place_to_base(connection: sqlite3.Connection, name, city, address, description, coordinate_x, coordinate_y, category_name, yandex_maps_url):
    """Adds place to db by its name and address | Добавляет место в бд по его имени и адресу"""
    places = connection.cursor()
    places.execute('INSERT INTO Places (name, city, address, description, coordinate_x, coordinate_y, category_name, yandex_maps_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                   (name, city, address, description, coordinate_x, coordinate_y, category_name, yandex_maps_url))
    new_id = places.lastrowid
    connection.commit()
    return new_id

def get_id_by_name_address(connection: sqlite3.Connection, name, city, address):
    """Gets id of place by name and address | получает id места по имени и адресу"""
    places = connection.cursor()
    places.execute('SELECT place_id FROM Places WHERE name = ? AND address = ?', (name, address))
    result = places.fetchone()
    return result[0] if result else None

def get_place_by_id(conn, place_id):
    """Получает полную информацию о месте по его ID"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM places WHERE place_id = ?", (place_id,))
    place_data = cursor.fetchone()
    
    if place_data:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, place_data))
    return None