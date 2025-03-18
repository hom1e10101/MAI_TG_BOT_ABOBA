import telebot
import types
import os
import requests
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

last_request = {}

# Get API token from environment variable or use default if not set
apishka = os.environ.get('TELEGRAM_API_TOKEN', '7643562043:AAF8ibjmeHK4CInIueqLO1j7H9n5aRRZC2U')
# Initialize bot with memory storage for user data
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)

@tb.message_handler(commands=['start'])
def start(message):
  user_id = message.from_user.id
  user_name = message.from_user.first_name
  tb.send_message(user_id, f'Привет, {user_name}! Я бот который поможет тебе открыть новые места в городе! Чтобы узнать что я умею, напиши /help')
  
@tb.message_handler(commands=['help'])
def help(message):
  user_id = message.from_user.id
  user_name = message.from_user.first_name
  tb.send_message(user_id, 'Напиши место, которое тебя интересует или напиши "случайно", чтобы получить случайное место')

@tb.message_handler()
def place(message):
  user_id = message.from_user.id
  user_name = message.from_user.first_name
  
  # Store the user's request for later use
  global last_request
  last_request[user_id] = message.text
#   with tb.retrieve_data(user_id, tb.get_me().id) as data:
#     # data['last_request'] = message.text
#     # print(f"запрос был {data['last_request']}")
  
  if message.text == 'случайно' or message.text == 'Случайно':
    tb.send_message(user_id, 'не, чет не хочу пока')
  else:
    tb.send_message(user_id, f'Ищем места по запросу: {message.text}')
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton("Отправить геолокацию", request_location=True)
    markup.add(button)
    tb.send_message(user_id, "Пожалуйста, поделитесь своим местоположением:", reply_markup=markup)



import json
# YandexGPT-based places search
def search_places_nearby(latitude, longitude, place_type=None, keyword=None, radius=1000):
    """Search for places near a specific location using YandexGPT capabilities"""

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
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    latitude = message.location.latitude
    longitude = message.location.longitude
    
    tb.send_message(user_id, f"Спасибо, {user_name}! Получил ваши координаты: {latitude}, {longitude}")
    tb.send_message(user_id, "YandexGPT анализирует данные и ищет интересные места поблизости...")
    
    # Get user's last message if it wasn't "случайно"
    user_request = "случайно"  # Default search term
    
    # Try to get user's last message from the chat history
    
    global last_request
    # last_request[user_id] = message.text
    if (last_request[user_id] not in ['случайно', 'Случайно']):
        user_request = last_request[user_id]
    # with tb.retrieve_data(user_id, tb.get_me().id) as data:
    #     print(f"че {data}")
    #     if data and 'last_request' in data and data['last_request'] not in ['случайно', 'Случайно']:
    #         user_request = data['last_request']
    #         print(user_request, data['last_request'])
    # print(f"обрабатываем {user_request}")
    

    # Status message to show user the request is being processed
    status_message = tb.send_message(user_id, f"🔍 Запрашиваю у YandexGPT информацию о местах по запросу '{user_request}'...")
    
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
                category_name = categories[0].get('name', 'Нет категории') if categories else 'Нет категории'
                
                response_text += f"🏙️ {i}. *{name}*\n"
                response_text += f"   📍 Адрес: {address}\n"
                response_text += f"   🔖 Категория: {category_name}\n"
                response_text += f"   🧐 Описание: {description}\n"
                response_text += f"   🗺️ [Открыть на OpenStreetMap]({maps_url})\n\n"
            
            # Delete the status message
            tb.delete_message(user_id, status_message.message_id)
            
            # Send the results
            tb.send_message(user_id, response_text, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            tb.delete_message(user_id, status_message.message_id)
            tb.send_message(user_id, f"❌ YandexGPT не смог найти места рядом с вами по запросу '{user_request}'. Попробуйте другой запрос.")
    except Exception as e:
        tb.delete_message(user_id, status_message.message_id)
        tb.send_message(user_id, f"❌ Произошла ошибка при поиске мест: {str(e)}. Пожалуйста, попробуйте еще раз.")


tb.infinity_polling()