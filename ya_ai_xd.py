import telebot
import json
import os
import requests
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from funcs import get_yandex_maps_link

from users_requests import get_db_connection, add_user_to_base, upd_user_name, get_user_role, upd_user_role

from settings_requests import get_user_message_to_edit, upd_user_message_to_edit, get_user_city, upd_user_city, \
    get_user_distance, upd_user_distance, get_user_last_request, upd_user_last_request

from secret import yandex_url
from secret import yandex_api

from secret import tg_api

apishka = os.environ.get('TELEGRAM_API_TOKEN', tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)

from places_requests import add_place_to_base
from places_requests import place_in_base
from places_requests import get_places_db_connection


def search_places_nearby(latitude, longitude, place_type=None, keyword=None, radius=1000):
    """Sends request to YAgpt to search for places nearby | Отправляет запрос Ягпт для поиска мест рядом"""
    prompt = f"""Given the coordinates (latitude: {latitude}, longitude: {longitude}), 
suggest 5 REAL, EXISTING places nearby (within 5km) that match '{keyword}'.

**Strict requirements:**  
- Each place MUST exist at the given coordinates.  
- Coordinates MUST be within 5 km (delta: ±0.045° lat, ±0.06° lon).  
- Address format: "улица Название, дом Номер, Город" (обязательно точный адрес).  

!!!MAKE SURE THAT STRICT REQUIREMENTS ARE COMPLETED!!!

The places must actually exist at these locations. For each place, provide:
1. Real, exact name
2. Brief description
3. Full, exact address in the format: "ул. <name>, д. <number>, <city>"
4. Exact coordinates (latitude, longitude)
5. Category (парк, ресторан, музей)



Return as JSON with this exact structure:
{{
  "features": [
    {{
      "properties": {{
        "name": "EXACT REAL NAME",
        "address": "FULL EXACT ADDRESS",
        "city": "Place city"
        "description": "Brief description",
        "CompanyMetaData": {{
          "Categories": [
            {{
              "name": "Category"
            }}
          ]
        }}
      }},
      "geometry": {{
        "coordinates": [EXACT_LONGITUDE, EXACT_LATITUDE]
      }}
    }}
  ]
}}
    """
    url = yandex_url
    API_Key = yandex_api
    # Заголовки запроса
    headers = {
        'Authorization': f'Api-Key {API_Key}',
        'Content-Type': 'application/json'
    }
    # Тело запроса
    data = {
        "modelUri": "gpt://b1gaa9e1j7g69a60a8l3/yandexgpt",
        "generationOptions": {
            "maxTokens": 2000,  # Максимальное количество токенов в ответе
            "temperature": 0.7  # Параметр креативности (от 0 до 1)
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
    # Отправка POST-запроса
    response = requests.post(url, headers=headers, json=data)

    # Проверка статуса ответа
    if response.status_code == 200:
        result = response.json()
        text_response = result["result"]["alternatives"][0]["message"]["text"]
        text_response = text_response[4:-4]
        return json.loads(text_response)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return create_fallback_data(latitude, longitude, keyword)


def create_fallback_data(latitude, longitude, keyword):
    """Create fallback data if YandexGPT API fails"""
    print(f"Creating fallback data for {keyword} at {latitude}, {longitude}")

    # Fallback sample data
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
            },
            {
                "properties": {
                    "name": f"Еще одно место по запросу '{keyword}'",
                    "description": "Адрес недалеко от вас",
                    "CompanyMetaData": {
                        "Categories": [
                            {
                                "name": "Развлечения"
                            }
                        ]
                    }
                },
                "geometry": {
                    "coordinates": [longitude - 0.02, latitude + 0.01]
                }
            }
        ]
    }


@tb.message_handler(content_types=['location'])
def handle_location(message):
    """Gets location of user for use | Получает местоположение пользователя для использования"""

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    latitude = message.location.latitude
    longitude = message.location.longitude

    prev_message = 0
    with get_db_connection() as conn:
        prev_message = get_user_message_to_edit(conn, user_id)

    tb.delete_message(user_id, message.message_id - 1)
    tb.delete_message(user_id, message.message_id)

    # Get user's last message if it wasn't "случайно"
    user_request = "случайно"  # Default search term

    # Try to get user's last message from the chat history
    with get_db_connection() as conn:
        user_request = get_user_last_request(conn, user_id)
        if user_request is None:
            print("error with getting last req")

    # Status message to show user the request is being processed

    tb.edit_message_text(f"🔍 Запрашиваю у YandexGPT информацию о местах по запросу '{user_request}'...",
                         chat_id=message.chat.id, message_id=prev_message)
    try:
        # Search for places based on the user's request using YandexGPT
        places_result = search_places_nearby(latitude, longitude, keyword=user_request)
        if places_result and places_result.get('features'):
            places = places_result['features'][:5]  # Get top 5 results
            response_text = f"🌟 Вот интересные места рядом с вами по запросу '{user_request}':\n\n"
            for i, place in enumerate(places, 1):
                properties = place.get('properties', {})
                name = properties.get('name', 'Неизвестное место')
                address = properties.get('address', 'Адрес не указан')
                city = properties.get('city', 'Адрес не указан')
                description = properties.get('description', 'Адрес не указан')
                # Get coordinates from the response
                coordinates = place.get('geometry', {}).get('coordinates', [])
                address = properties.get('address', '').strip()
                yandex_maps_url = get_yandex_maps_link(address)
                # Get company metadata if available
                company_metadata = properties.get('CompanyMetaData', {})
                categories = company_metadata.get('Categories', [])
                category_name = categories[0].get('name', 'Нет категории') if categories else 'Нет категории'
                response_text += f"🏙️ {i}. *{name}*\n"
                response_text += f"   📍 Адрес: {address}\n"
                response_text += f"   🔖 Категория: {category_name}\n"
                response_text += f"   🧐 Описание: {description}\n"
                response_text += f"   🌐 [Узреть в Яндекс.Карты]({yandex_maps_url})\n\n"

                # add place to base
                with get_places_db_connection() as conn:
                    if place_in_base(conn, name, city, address) == 0:
                        add_place_to_base(conn, name, city, address)

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
                       InlineKeyboardButton("5. 💬", callback_data="c5"),)
            tb.edit_message_text(response_text, chat_id=message.chat.id, message_id=prev_message, parse_mode="Markdown",
                                 disable_web_page_preview=True)
        else:
            # tb.delete_message(user_id, status_message.message_id)
            tb.send_message(user_id,
                            f"❌ YandexGPT не смог найти места рядом с вами по запросу '{user_request}'. Попробуйте "
                            f"другой запрос.")
    except Exception as e:
        # tb.delete_message(user_id, status_message.message_id)
        tb.send_message(user_id, f"❌ Произошла ошибка при поиске мест: {str(e)}. Пожалуйста, попробуйте еще раз.")
