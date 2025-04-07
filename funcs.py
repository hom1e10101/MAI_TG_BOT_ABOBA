import telebot
import types
import os
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

from shared_state import last_request
apishka = os.environ.get('TELEGRAM_API_TOKEN', '7732717132:AAHPdgXQJGvWUzP2MaYpZQ7vxwyaQGEHv1s')
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)


def start(message):
  '''Sends start message | Отправляет стартовое сообщение'''
  user_id = message.from_user.id
  user_name = message.from_user.first_name
  tb.send_message(user_id, f'Привет, {user_name}! Я бот который поможет тебе открыть новые места в городе! Чтобы узнать что я умею, напиши /help')

def help(message):
  '''Helps user to understand how it works | Помогает пользользователю понять как оно работает'''
  user_id = message.from_user.id
  user_name = message.from_user.first_name
  tb.send_message(user_id, 'Напиши место, которое тебя интересует или напиши "случайно", чтобы получить случайное место')

def place(message):
  '''Gets user's request for place | Получает запрос пользователя на место'''
  user_id = message.from_user.id
  user_name = message.from_user.first_name

  global last_request
  last_request[user_id] = message.text
  if message.text == 'случайно' or message.text == 'Случайно':
    tb.send_message(user_id, 'не, чет не хочу пока')
  else:
    tb.send_message(user_id, f'Ищем места по запросу: {message.text}')
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton("Отправить геолокацию", request_location=True)
    markup.add(button)
    tb.send_message(user_id, "Пожалуйста, поделитесь своим местоположением:", reply_markup=markup)

