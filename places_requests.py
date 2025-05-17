import sqlite3
from contextlib import contextmanager

from secret import database


@contextmanager
def get_places_db_connection():
    """Connection with db | Подключение бд"""
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def get_address_by_name(connection: sqlite3.Connection, name):
    """Gets place's address by its name | Получает адресс места по его названию"""
    places = connection.cursor()
    query = "SELECT address FROM places WHERE name = ?"
    places.execute(query, (name,))
    result = places.fetchone()
    return result[0] if result else None


def get_city_by_name(connection: sqlite3.Connection, name):
    """Gets city's name by place name | Получает название города, по названию места"""
    places = connection.cursor()
    query = "SELECT city FROM places WHERE name = ?"
    places.execute(query, (name,))
    result = places.fetchone()
    return result[0] if result else None


def place_in_base(connection: sqlite3.Connection, name, city, address):
    """Checks existence of a place in bd | Проверяет наличие места в бд"""
    places = connection.cursor()
    places.execute('SELECT EXISTS(SELECT 1 FROM places WHERE name = ?)', (name,))
    exists = places.fetchone()[0] == 1
    if exists:
        if get_city_by_name(connection, name) == city and get_address_by_name(connection, name) == address:
            return 1
    return 0


def add_place_to_base(connection: sqlite3.Connection, name, city, address):
    """Adds place to db by its name and address | Добавляет место в бд по его имени и адресу"""
    places = connection.cursor()
    places.execute('INSERT INTO places (name, city, address) VALUES (?, ?, ?)', (name, city, address))
    connection.commit()
