import telebot
import json
import requests
from telebot.storage import StateMemoryStorage
from users_requests import get_db_connection, get_last_request

with open('huy_vam_a_ne_apishka_sini_blyadey.txt', 'r') as file:
    apishki = file.readlines()
tgap = apishki[0]
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(tgap, state_storage=state_storage)
apiya = apishki[1]

def search_places_nearby(latitude,
                         longitude,
                         place_type=None,
                         keyword=None,
                         radius=1000):
    '''Sends request to YAgpt to search for places nearby | Отправляет запрос Ягпт для поиска мест рядом'''
    prompt = f"""Given the coordinates (latitude: {latitude}, longitude: {longitude}), 
  suggest 5 interesting places nearby (in the area of 5km) that match '{keyword}'.
  For each place, provide:
  1. Name of the place
  2. Brief description
  3. address
  4. Category (museum, restaurant, park, etc.)

  Format the response as a JSON with this structure:
  {{
    "features": [
      {{
        "properties": {{
          "name": "Place Name",
          "address": "Place Address",
          "description": "Place description",
          "CompanyMetaData": {{
            "Categories": [
              {{
                "name": "Category"
              }}
            ]
          }}
        }},
        "geometry": {{
          "coordinates": [longitude, latitude]
        }}
      }}
    ]
  }}
  """
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    API_Key = '<APIkey>'
    # Заголовки запроса
    headers = {
        'Authorization': f'Api-Key {API_Key}',
        'Content-Type': 'application/json'
    }
    # Тело запроса
    data = {
        "modelUri": "gpt://b1gqi7ivu4cnp5fh58js/yandexgpt",
        "generationOptions": {
            "maxTokens": 500,  # Максимальное количество токенов в ответе
            "temperature": 0.7  # Параметр креативности (от 0 до 1)
        },
        "completionOptions": {
            "temperature": 0.6,
            "maxTokens": "2000",
            "reasoningOptions": {
                "mode": "DISABLED"
            }
        },
        "messages": [{
            "role": "system",
            "text": prompt
        }]
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
        "features": [{
            "properties": {
                "name": f"Интересное место по запросу '{keyword}'",
                "description": "Предположительный адрес поблизости",
                "CompanyMetaData": {
                    "Categories": [{
                        "name": "Достопримечательность"
                    }]
                }
            },
            "geometry": {
                "coordinates": [longitude + 0.01, latitude + 0.005]
            }
        }, {
            "properties": {
                "name": f"Еще одно место по запросу '{keyword}'",
                "description": "Адрес недалеко от вас",
                "CompanyMetaData": {
                    "Categories": [{
                        "name": "Развлечения"
                    }]
                }
            },
            "geometry": {
                "coordinates": [longitude - 0.02, latitude + 0.01]
            }
        }]
    }


@tb.message_handler(content_types=['location'])
def handle_location(message):
    '''Gets location of user for use | Получает местоположение пользователя для использования'''
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    latitude = message.location.latitude
    longitude = message.location.longitude

    tb.send_message(
        user_id,
        f"Спасибо, {user_name}! Получил ваши координаты: {latitude}, {longitude}"
    )
    tb.send_message(
        user_id,
        "YandexGPT анализирует данные и ищет интересные места поблизости...")

    # Get user's last message if it wasn't "случайно"
    user_request = "случайно"  # Default search term

    # Try to get user's last message from the chat history
    with get_db_connection() as conn:
        user_request = get_last_request(conn, user_id)
        if (user_request == None):
            print("error with gettin last req")

    # Status message to show user the request is being processed
    status_message = tb.send_message(
        user_id,
        f"🔍 Запрашиваю у YandexGPT информацию о местах по запросу '{user_request}'..."
    )
    try:
        # Search for places based on the user's request using YandexGPT
        places_result = search_places_nearby(latitude,
                                             longitude,
                                             keyword=user_request)
        if places_result and places_result.get('features'):
            places = places_result['features'][:5]  # Get top 5 results
            response_text = f"🌟 Вот интересные места рядом с вами по запросу '{user_request}':\n\n"
            for i, place in enumerate(places, 1):
                properties = place.get('properties', {})
                name = properties.get('name', 'Неизвестное место')
                address = properties.get('address', 'Адрес не указан')
                description = properties.get('description', 'Адрес не указан')
                # Get coordinates from the response
                coordinates = place.get('geometry', {}).get('coordinates', [])
                if coordinates and len(coordinates) >= 2:
                    place_lng, place_lat = coordinates
                    maps_url = f"https://www.openstreetmap.org/?mlat={place_lat}&mlon={place_lng}#map=16/{place_lat}/{place_lng}"
                else:
                    maps_url = "https://www.openstreetmap.org"
                # Get company metadata if available
                company_metadata = properties.get('CompanyMetaData', {})
                categories = company_metadata.get('Categories', [])
                category_name = categories[0].get(
                    'name', 'Нет категории') if categories else 'Нет категории'
                response_text += f"🏙️ {i}. *{name}*\n"
                response_text += f"   📍 Адрес: {address}\n"
                response_text += f"   🔖 Категория: {category_name}\n"
                response_text += f"   🧐 Описание: {description}\n"
                response_text += f"   🗺️ [Открыть на OpenStreetMap]({maps_url})\n\n"
            # Delete the status message
            tb.delete_message(user_id, status_message.message_id)
            # Send the results
            tb.send_message(user_id,
                            response_text,
                            parse_mode="Markdown",
                            disable_web_page_preview=True)
        else:
            tb.delete_message(user_id, status_message.message_id)
            tb.send_message(
                user_id,
                f"❌ YandexGPT не смог найти места рядом с вами по запросу '{user_request}'. Попробуйте другой запрос."
            )
    except Exception as e:
        tb.delete_message(user_id, status_message.message_id)
        tb.send_message(
            user_id,
            f"❌ Произошла ошибка при поиске мест: {str(e)}. Пожалуйста, попробуйте еще раз."
        )
