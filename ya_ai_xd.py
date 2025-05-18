import time

import telebot
import json
import os
import requests
from geopy.geocoders import Nominatim
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from funcs import get_yandex_maps_link

from users_requests import get_db_connection, add_user_to_base, upd_user_name, get_user_role, upd_user_role

from settings_requests import get_user_message_to_edit, upd_user_message_to_edit, get_user_city, upd_user_city, \
    get_user_distance, upd_user_distance, get_user_last_request, upd_user_last_request

from secret import yandex_url, yandex_api, tg_api

apishka = os.environ.get('TELEGRAM_API_TOKEN', tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)

from places_requests import add_place_to_base
from places_requests import place_in_base
from places_requests import get_places_db_connection

# Инициализация геокодера Nominatim с правильными параметрами
geolocator = Nominatim(
    user_agent="TelegramPlacesBot/1.0 (https://t.me/New_places_fr_bot)",
    timeout=10
)


def classify_place_type(user_query):
    """Определяет тип места с помощью YandexGPT"""
    prompt = f"""Определи тип места для запроса пользователя: "{user_query}".
Выбери один наиболее подходящий тип из списка:
- restaurant (рестораны, кафе, бары, фастфуд)
- park (парки, скверы, места для прогулок)
- museum (музеи, галереи)
- cinema (кинотеатры)
- shop (магазины, торговые центры)
- pharmacy (аптеки)
- hospital (больницы, клиники)
- hotel (отели, гостиницы)
- bank (банки, банкоматы)
- amusement_park (аттракционы, парки развлечений)
- zoo (зоопарки)
- library (библиотеки)
- tourist_attraction (достопримечательности)
- supermarket (супермаркеты)
- cafe (кафе, кофейни)

Верни только одно ключевое слово типа места, без объяснений."""

    url = yandex_url
    API_Key = yandex_api

    headers = {
        'Authorization': f'Api-Key {API_Key}',
        'Content-Type': 'application/json'
    }

    data = {
        "modelUri": "gpt://b1gaa9e1j7g69a60a8l3/yandexgpt",
        "generationOptions": {
            "maxTokens": 2000,
            "temperature": 0.7
        },
        "completionOptions": {
            "temperature": 0.6,
            "maxTokens": "2000",
            "reasoningOptions": {
                "mode": "DISABLED"
            }
        },
        "messages": [
            {
                "role": "system",
                "text": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        text_response = result["result"]["alternatives"][0]["message"]["text"]
        return text_response.strip()
    else:
        print(f"Error classifying place type: {response.status_code}")
        return None


def generate_place_description(place_name, place_type, place_address):
    """Генерирует описание места с помощью YandexGPT"""
    prompt = f"""Напиши краткое, но информативное описание для места "{place_name}" ({place_type}), расположенного по адресу: {place_address}.

Описание должно быть:
1. Лаконичным (2-3 предложения)
2. Информативным
3. Привлекательным для посетителей
4. Содержать ключевые особенности места

Пример хорошего описания:
"Уютное кафе с авторской кухней и домашней атмосферой. Особенно популярны десерты собственного приготовления. Идеально подходит для встреч с друзьями и семейных обедов."

Верни только само описание, без дополнительных комментариев."""

    url = yandex_url
    API_Key = yandex_api

    headers = {
        'Authorization': f'Api-Key {API_Key}',
        'Content-Type': 'application/json'
    }

    data = {
        "modelUri": "gpt://b1gaa9e1j7g69a60a8l3/yandexgpt",
        "generationOptions": {
            "maxTokens": 200,
            "temperature": 0.7
        },
        "completionOptions": {
            "temperature": 0.6,
            "maxTokens": "200",
        },
        "messages": [
            {
                "role": "system",
                "text": prompt
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            text_response = result["result"]["alternatives"][0]["message"]["text"]
            return text_response.strip()
    except Exception as e:
        print(f"Error generating description: {e}")

    return "Интересное место, которое стоит посетить."


def search_places_nominatim(latitude, longitude, place_type=None, radius=5000):
    """Ищет места поблизости с помощью Nominatim (OpenStreetMap)"""
    try:
        radius_deg = radius / 111000
        south = latitude - radius_deg
        north = latitude + radius_deg
        west = longitude - radius_deg
        east = longitude + radius_deg

        query_params = {
            'format': 'json',
            'viewbox': f"{west},{south},{east},{north}",
            'bounded': 1,
            'q': place_type if place_type else 'attraction',
            'limit': 5,
            'addressdetails': 1
        }

        headers = {
            'User-Agent': 'TelegramPlacesBot/1.0',
            'Referer': 'https://t.me/your_bot'
        }

        time.sleep(1)
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=query_params,
            headers=headers
        )

        if response.status_code == 429:
            raise Exception("Слишком много запросов. Пожалуйста, попробуйте позже.")
        response.raise_for_status()

        places = response.json()
        features = []

        for place in places[:5]:
            address = place.get('address', {})
            city = address.get('city', '') or address.get('town', '') or address.get('village', '')
            place_name = place.get('display_name', '').split(',')[0] or 'Неизвестное место'
            place_address = place.get('display_name', 'Адрес не указан')
            place_category = place.get('type', 'attraction')

            # Генерируем описание с помощью YandexGPT
            description = generate_place_description(place_name, place_category, place_address)

            features.append({
                "properties": {
                    "name": place_name,
                    "address": place_address,
                    "city": city,
                    "description": description,  # Используем сгенерированное описание
                    "CompanyMetaData": {
                        "Categories": [
                            {
                                "name": place_category
                            }
                        ]
                    }
                },
                "geometry": {
                    "coordinates": [
                        float(place.get('lon', 0)),
                        float(place.get('lat', 0))
                    ]
                }
            })

        return {"features": features}

    except Exception as e:
        print(f"Error searching places with Nominatim: {e}")
        return create_fallback_data(latitude, longitude, place_type)


def create_fallback_data(latitude, longitude, keyword):
    """Создает резервные данные, если API не работает"""
    print(f"Creating fallback data for {keyword} at {latitude}, {longitude}")
    return {
        "features": [
            {
                "properties": {
                    "name": f"Интересное место по запросу '{keyword}'",
                    "description": "Предположительный адрес поблизости",
                    "CompanyMetaData": {
                        "Categories": [
                            {
                                "name": "Достопримечательность"
                            }
                        ]
                    }
                },
                "geometry": {
                    "coordinates": [longitude + 0.01, latitude + 0.005]
                }
            }
        ]
    }


@tb.message_handler(content_types=['location'])
def handle_location(message):
    """Обрабатывает местоположение пользователя и ищет места поблизости"""
    user_id = message.from_user.id
    latitude = message.location.latitude
    longitude = message.location.longitude

    prev_message = 0
    with get_db_connection() as conn:
        prev_message = get_user_message_to_edit(conn, user_id)

    tb.delete_message(user_id, message.message_id - 1)
    tb.delete_message(user_id, message.message_id)

    user_request = "случайно"
    with get_db_connection() as conn:
        user_request = get_user_last_request(conn, user_id)
        if user_request is None:
            print("error with getting last req")

    tb.edit_message_text(f"🔍 Определяем тип мест для запроса '{user_request}'...",
                         chat_id=message.chat.id, message_id=prev_message)

    try:
        place_type = classify_place_type(user_request)
        if not place_type:
            place_type = "attraction"

        tb.edit_message_text(f"🔍 Ищем {place_type} поблизости и составляем описания...",
                             chat_id=message.chat.id, message_id=prev_message)

        places_result = search_places_nominatim(latitude, longitude, place_type)

        if places_result and places_result.get('features'):
            places = places_result['features'][:5]
            response_text = f"🌟 Вот интересные места рядом с вами по запросу '{user_request}':\n\n"

            for i, place in enumerate(places, 1):
                properties = place.get('properties', {})
                name = properties.get('name', 'Неизвестное место')
                address = properties.get('address', 'Адрес не указан')
                description = properties.get('description', 'Нет описания')

                coordinates = place.get('geometry', {}).get('coordinates', [])
                yandex_maps_url = get_yandex_maps_link(address)

                company_metadata = properties.get('CompanyMetaData', {})
                categories = company_metadata.get('Categories', [])
                category_name = categories[0].get('name', 'Нет категории') if categories else 'Нет категории'

                response_text += f"🏙️ {i}. *{name}*\n"
                response_text += f"   📍 Адрес: {address.split(',')[0]}\n"
                response_text += f"   🔖 Категория: {category_name}\n"
                response_text += f"   🧐 Описание: {description}\n"
                response_text += f"   🌐 [Посмотреть на Яндекс.Картах]({yandex_maps_url})\n\n"

                with get_places_db_connection() as conn:
                    if place_in_base(conn, name, "", address) == 0:
                        add_place_to_base(conn, name, "", address)

            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("1. ⭐", callback_data="r1"),
                       InlineKeyboardButton("1. 💬", callback_data="c1"),
                       InlineKeyboardButton("2. ⭐", callback_data="r2"),
                       InlineKeyboardButton("2. 💬", callback_data="c2"),
                       InlineKeyboardButton("3. ⭐", callback_data="r3"),
                       InlineKeyboardButton("3. 💬", callback_data="c3"),
                       InlineKeyboardButton("4. ⭐", callback_data="r4"),
                       InlineKeyboardButton("4. 💬", callback_data="c4"),
                       InlineKeyboardButton("5. ⭐", callback_data="r5"),
                       InlineKeyboardButton("5. 💬", callback_data="c5"))

            tb.edit_message_text(response_text, chat_id=message.chat.id,
                                 message_id=prev_message, parse_mode="Markdown",
                                 reply_markup=markup, disable_web_page_preview=True)
        else:
            tb.send_message(user_id,
                            f"❌ Не удалось найти места поблизости по запросу '{user_request}'. Попробуйте другой запрос.")

    except Exception as e:
        tb.send_message(user_id, f"❌ Произошла ошибка: {str(e)}. Пожалуйста, попробуйте еще раз.")
