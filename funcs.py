import urllib.parse

import requests
import telebot
import types
import os
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

from users_requests import get_db_connection, add_user_to_base, upd_user_name, get_user_role, upd_user_role

from settings_requests import add_user_settings, get_user_message_to_edit, upd_user_message_to_edit, get_user_city, \
    upd_user_city, get_user_distance, upd_user_distance, get_user_last_request, upd_user_last_request
from settings_requests import upd_user_status, get_user_status

from commet_requests import add_comment

from secret import tg_api

apishka = os.environ.get('TELEGRAM_API_TOKEN', tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)


def start(message):
    '''Sends start message | Отправляет стартовое сообщение'''
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    tb.delete_message(user_id, message_id=message.id)

    with get_db_connection() as conn:
        add_user_to_base(conn, user_id, user_name)
        add_user_settings(conn, user_id)

    sent_massage = tb.send_message(user_id,
                                   f'Привет, {user_name}! Я бот который поможет тебе открыть новые места в городе! Чтобы узнать что я умею, напиши /help')
    print(f'sent_massage is {sent_massage.id}')
    with get_db_connection() as conn:
        upd_user_message_to_edit(conn, user_id, sent_massage.id)


def help(message):
    '''Helps user to understand how it works | Помогает пользользователю понять как оно работает'''
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    prev_message = 0
    with get_db_connection() as conn:
        prev_message = get_user_message_to_edit(conn, user_id)

    print(f'\tkek sent_massage is {prev_message}')
    tb.delete_message(user_id, message.message_id)
    tb.edit_message_text('Напиши место, которое тебя интересует или напиши "случайно", чтобы получить случайное место',
                         chat_id=message.chat.id, message_id=prev_message)


def place(message):
    '''Gets user's request for place | Получает запрос пользователя на место'''
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    prev_message = 0
    with get_db_connection() as conn:
        prev_message = get_user_message_to_edit(conn, user_id)

    tb.delete_message(user_id, message.message_id)

    with get_db_connection() as conn:
        upd_user_last_request(conn, user_id, message.text)

    if message.text == 'случайно' or message.text == 'Случайно':
        tb.edit_message_text('не, чет не хочу пока', chat_id=message.chat.id, message_id=prev_message)
    else:
        tb.edit_message_text(f'Ищем места по запросу: {message.text}', chat_id=message.chat.id, message_id=prev_message)
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = KeyboardButton("Отправить геолокацию", request_location=True)
        markup.add(button)
        tb.send_message(user_id, "Пожалуйста, поделитесь своим местоположением:", reply_markup=markup)


def user_settings(message):
    '''получить из бд настройки пользователя, в случае отсуствия, занести дефоль'''
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    print(message.id)
    tb.delete_message(user_id, message.id)
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton("Расстояние поиска", callback_data="distance"),
               InlineKeyboardButton("Мои оценки", callback_data="rating"),
               InlineKeyboardButton("Мои комментарии",
                                    callback_data="comments"))  #поменять все на эмодзи + сделать действия
    tb.send_message(user_id, "Тут ты можешь изменить расстояние поиска мест и посмотреть свои оценки и комментарии",
                    reply_markup=markup)


def operator(call):
    user_id = call.from_user.id
    if call.data == "distance":
        with get_db_connection as conn:
            upd_user_status(conn, 'distance')
        tb.send_message(user_id, "Напиши желаемое расстояние поиска числом в километрах или название города")
        #реализуй try except для того чтобы узнать расстояние / город
    if call.data == "rating":
        with get_db_connection as conn:
            upd_user_status(conn, 'rating')
        tb.send_message(user_id, "Напиши оценку, которую хочешь поставить месту от 1 до 10")
    if call.data == "comments":
        with get_db_connection as conn:
            upd_user_status(conn, 'comments')
        tb.send_message(user_id, "МАШИНА ПОЛОЖИ БАНКОМАТ!!!!")


def change_distance(message):
    if message.isdigit():
        print(int(message))
        with get_db_connection as conn:
            upd_user_distance(int(conn, message))
    else:
        with get_db_connection as conn:
            upd_user_city(conn, message)
    with get_db_connection as conn:
        upd_user_status(conn, 'start')


def set_rating(message, place_id):
    user_id = message.from_user.id
    if message.isdigit():
        print(int(message))
        with get_db_connection as conn:
            add_comment(conn, user_id, place_id, "NULL", int(conn, message))
    else:
        print('needed to do try exept')


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


def pAshAlk0(message):
    user_id = message.from_user.id
    for i in range(10):
        tb.send_message(user_id, "Т̷̢̛̝̹͓̘̼̣̯̘̮͗̏̅̈́̈́̀͡ͅы̶̛̪͖̻͈͙̪͇̘̰̼͇͇̯͇͈̽̈́͆̑̉͒̒̍̄̃̉͐͗̄̀̍̄͟͝͝ͅ "
                                 "̷̡̛̻͎̀̎̽̐͛̿̿̃̌͛͂̎̃͗̀̓̔͒͆̄̍̈̚͘̚͟͝п̸̲͑̇̃́р̵̧̢̱̙̭̺͎͖͕̥̖̰̝̲͔͉̠̳̠̘̗̘̓̊̓͒̄͛̇̂̓́̈́̑̅̾̈́̍̍̄̐̕͝͡͝ͅͅо̴̛͉̼̫̱͉̫͓͛̈́̿̒͑̓̈́̌̍͘͟к̴̨̨̡̮͉̼̘̘̤̼͎͙͊͐̆͛̒̏̾͑̌̚̕"
        "л̷̡̡̣͍͕̰̼̼͕͎̼̝̩͙̟̰͈̖̠͔̙̬̌̈́͒̓͌̂͑̾́̈́͊̈́̇̈́́́̊̿̎̎̅̾̔̕͜͝͝я̸̧̢̧͖̜̯̗͇̰̤̖̖̱͔̹͖̗͙̦̜̹͖͚͇̩̣̙̲̅̈́̿̋̎̇̋̐̋̓͑͂́̕̚͜͝т̶̛̟̟͓͗́̈́̉̀̓̽̓̽̈̽̍̏͊͌̂̓͗̆̂̚̕͟")
    for i in range(10):
        tb.send_message(user_id, "Н̴͗̋͜е̵̠͔̳̿̓к̵̩̦̔̏͝у̷͉͖̝̾д̶͚̍̈́а̵͔̠̔̾ ̸̰͒б̴͙̈́͠е̴̦̙̌͡ж̶̮̟͖̎͆͌ӓ̸̣́̈́т̵̻̥̽̂̈́ь̶̝͚̝̽̑")
    for i in range(10):
        tb.send_message(user_id, "Я̵̗̮͉̋͊ ̶̫̼͋̆з̷̧̛̱̲̎д̸̖̼̮̟̏̐̀͝е̸̱̖̰̔̓͑͡с̶̖̰̱̈́̀̄͋̚ь̶̨̱̭̯́͟")
    for i in range(10):
        tb.send_message(user_id, "У̷̙͆͒ ̴͈̹̲̥̦̍̔т̷̫̪̫̼̩̈̋̽е̸͕̻̠̃͛̈̉б̵̹̌̂͊̉͘я̷̛̫̝̖͕͗͛̆͑ "
                                 "̴̢̛̋̓̄н̸̜̱̌ͅе̷̨͙̩̩͊͐т̵̟̣̦̲̲̀̉̿̉͡ "
                                 "̵̮͘͜в̷̩̐́͝ы̴̢͕͉͎̙͡х̶̹̹̤͑̔̀͝о̶͓͍̘͚̄̈́д̵̢̑̆ͅа̵̛̝̳̘́̽͌̚͟")