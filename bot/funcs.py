import telebot
import types
import os
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

from users_requests import get_db_connection, user_in_base, add_user_to_base, upd_last_request

# from shared_state import last_request
from secret import tg_api
apishka = os.environ.get('TELEGRAM_API_TOKEN', tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)

def start(message):
  '''Sends start message | Отправляет стартовое сообщение'''
  user_id = message.from_user.id
  user_name = message.from_user.first_name
  
  with get_db_connection() as conn:
    if user_in_base(conn, user_id) == 0:
      add_user_to_base(conn, user_id, user_name, 'user')
  sent_massege = tb.send_message(user_id, f'Привет, {user_name}! Я бот который поможет тебе открыть новые места в городе! Чтобы узнать что я умею, напиши /help')
  return sent_massege

def help(message, prev_message):
  '''Helps user to understand how it works | Помогает пользользователю понять как оно работает'''
  user_id = message.from_user.id
  user_name = message.from_user.first_name
  tb.delete_message(user_id, message.message_id)
  tb.edit_message_text('Напиши место, которое тебя интересует или напиши "случайно", чтобы получить случайное место', chat_id=message.chat.id, message_id=prev_message.message_id)

def place(message, prev_message):
  '''Gets user's request for place | Получает запрос пользователя на место'''
  user_id = message.from_user.id
  user_name = message.from_user.first_name

  tb.delete_message(user_id, message.message_id)
  
  with get_db_connection() as conn:
    upd_last_request(conn, user_id, message.text)

  if message.text == 'случайно' or message.text == 'Случайно':
    tb.edit_message_text('не, чет не хочу пока', chat_id=message.chat.id, message_id=prev_message.message_id)
  else:
    tb.edit_message_text(f'Ищем места по запросу: {message.text}', chat_id=message.chat.id, message_id=prev_message.message_id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton("Отправить геолокацию", request_location=True)
    markup.add(button)
    tb.send_message(user_id, "Пожалуйста, поделитесь своим местоположением:", reply_markup=markup)
    