import time
import urllib

import telebot
import json
import os
import requests
from geopy.geocoders import Nominatim
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from users_requests import get_db_connection
from settings_requests import get_user_message_to_edit, get_user_last_request, upd_user_request_ids, get_user_distance
from secret import yandex_url, yandex_api, tg_api
from places_requests import add_place_to_base, place_in_base, get_places_db_connection, get_id_by_name_address, \
    get_place_by_id
from commet_requests import get_place_rating

apishka = os.environ.get('TELEGRAM_API_TOKEN', tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)



# Инициализация геокодера Nominatim с правильными параметрами
geolocator = Nominatim(
    user_agent="TelegramPlacesBot/1.0 (https://t.me/New_places_fr_bot)",
    timeout=10
)

def get_yandex_maps_link(address):
    # Убираем лишние пробелы и кодируем только нужные символы
    clean_address = (address
                     .replace("ул.", "улица")
                     .replace("д.", "дом")
                     .replace("корп.", "корпус")
                     .strip())

    # Кодируем для URL (но не допускаем дублирование %20)
    encoded_address = urllib.parse.quote_plus(clean_address)
    return f"https://yandex.ru/maps/?text={encoded_address}"
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
и так далее, сделай так чтобы любое предложение можно было классифицировать

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


def is_text_normal_yagpt(text):
    # Четкий промпт с требованием отвечать только "true" или "false"
    prompt = f"""
    Содержит ли следующий текст ненормативную лексику любого рода, в том числе оскорбления, нацизм и тд, 
    (включая замаскированные варианты типа 'п1д0р', 'piдор')? 
    Отвечай строго одним словом: 'true' если текст чистый, 'false' если содержит нарушения.

    Текст:  {text}
    """
    API_Key = yandex_api
    url = yandex_url
    headers = {
        "Authorization": f"Api-Key {API_Key}",
        "Content-Type": "application/json"
    }
    data = {
        "modelUri": f"gpt://b1gaa9e1j7g69a60a8l3/yandexgpt",
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,  # Минимизируем случайные ответы
            "maxTokens": 100  # Ограничиваем длину ответа
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты фильтр ненормативной лексики. Отвечай ТОЛЬКО 'true' или 'false'."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }


    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    answer = ((response.json()["result"]["alternatives"][0]["message"]["text"].strip().lower()).split(' ')[-1]).split('.')[0]
    # Преобразуем строковый ответ в boolean
    if answer == "true":
        return True
    else:
        return False


def search_places_nominatim(latitude, longitude, place_type=None, radius=5):
    """Ищет места поблизости с помощью Nominatim (OpenStreetMap)"""
    try:
        radius_deg = radius / 111
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



def create_place_card_by_db(place_id, index, total):
    """Создает карточку места для отображения"""
    with get_db_connection() as conn:
        properties = get_place_by_id(conn, place_id)
    name = properties.get('name', 'Неизвестное место')
    address = properties.get('address', 'Адрес не указан')
    description = properties.get('description', 'Нет описания')
    coordinate_x = properties.get('coordinate_x')
    coordinate_y = properties.get('coordinate_y')
    coordinates = (coordinate_x, coordinate_y)
    yandex_maps_url = get_yandex_maps_link(address)
    category_name = properties.get('category_name', 'Нет категории')

    avg_rating = 0
    with get_db_connection() as conn:
        if get_place_rating(conn, place_id) is not None:
            avg_rating = round(float(get_place_rating(conn, place_id)), 1)

    card_text = f"🏙️ *{name}*\n" #
    if avg_rating > 0:
        card_text += f"⭐ *Оценка*: {avg_rating}\n" #
    card_text += f"📍 *Адрес*: {address}\n" #
    card_text += f"🔖 *Категория*: {category_name}\n" #
    card_text += f"🧐 *Описание*: {description}\n" #
    card_text += f"🌐 [Посмотреть на Яндекс.Картах]({yandex_maps_url})\n\n"
    if total > 1:
        card_text += f"📍 Место {index + 1} из {total}"

    return card_text


def create_navigation_keyboard(current_index, total_places):
    """Создает клавиатуру для навигации между местами"""
    markup = InlineKeyboardMarkup()
    row = []

    if current_index > 0:
        row.append(InlineKeyboardButton("⬅️", callback_data=f"prev_{current_index}"))

    row.append(InlineKeyboardButton("⭐", callback_data=f"rate_{current_index}"))
    row.append(InlineKeyboardButton("💬", callback_data=f"comment_{current_index}"))

    if current_index < total_places - 1:
        row.append(InlineKeyboardButton("➡️", callback_data=f"next_{current_index}"))
    markup.row(*row)

    row2 = []
    row2.append(InlineKeyboardButton("Отзывы", callback_data=f"get_comm_{current_index}"))
    markup.row(*row2)
    return markup



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
        with get_db_connection() as conn:
            places_result = search_places_nominatim(latitude, longitude, place_type, get_user_distance(conn, user_id))

        if places_result and places_result.get('features'):
            places = places_result['features'][:5]

            # Сохраняем ID мест в базу данных
            places_ids = []
            with get_places_db_connection() as conn:
                for i, place in enumerate(places):
                    properties = place.get('properties', {})
                    name = properties.get('name', 'Неизвестное место')
                    address = properties.get('address', 'Адрес не указан')

                    if place_in_base(conn, name, "", address) == 0:
                        description = properties.get('description', 'Нет описания')
                        coordinates = place.get('geometry', {}).get('coordinates', [])

                        company_metadata = properties.get('CompanyMetaData', {})
                        categories = company_metadata.get('Categories', [])
                        category_name = categories[0].get('name', 'Нет категории') if categories else 'Нет категории'

                        now_ind = add_place_to_base(conn, name, "", address, description, coordinates[0], coordinates[1], category_name, "")
                        places_ids.append(now_ind)
                    else:
                        now_ind = get_id_by_name_address(conn, name, "", address)
                        places_ids.append(now_ind)
            # Сохраняем данные о местах для пользователя
            with get_db_connection() as conn:
                upd_user_request_ids(conn, user_id, places_ids)

            place_id = places_ids[0]
            card_text = create_place_card_by_db(place_id, 0, len(places_ids))

            markup = create_navigation_keyboard(0, len(places))
            tb.edit_message_text(
                chat_id=message.chat.id,
                message_id=prev_message,
                text=card_text,
                parse_mode="Markdown",
                reply_markup=markup,
                disable_web_page_preview=True
            )
        else:
            tb.send_message(user_id,
                            f"❌ Не удалось найти места поблизости по запросу '{user_request}'. Попробуйте другой запрос.")

    except Exception as e:
        tb.send_message(user_id, f"❌ Произошла ошибка: {str(e)}. Пожалуйста, попробуйте еще раз.")