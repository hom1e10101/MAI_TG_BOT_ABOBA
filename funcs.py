import urllib.parse
from time import sleep

import telebot
import types
import os
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

from users_requests import get_db_connection, add_user_to_base, upd_user_name, get_user_role, upd_user_role

from settings_requests import add_user_settings, get_user_message_to_edit, upd_user_message_to_edit, get_user_city, upd_user_city, get_user_distance, upd_user_distance, get_user_last_request, upd_user_last_request
from settings_requests import upd_user_status, get_user_status

from commet_requests import add_comment

from secret import tg_api
apishka = os.environ.get("TELEGRAM_API_TOKEN", tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)

def start(message):
    """Sends start message | Отправляет стартовое сообщение"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    tb.delete_message(user_id, message_id=message.id)

    with get_db_connection() as conn:
        add_user_to_base(conn, user_id, user_name)
        add_user_settings(conn, user_id)
    
    with get_db_connection() as conn:
        upd_user_status(conn, user_id, "start")
    
    sent_massage = tb.send_message(user_id,
            f"Привет, {user_name}! Я бот который поможет тебе открыть новые места в городе! Чтобы узнать что я умею, напиши /help")
    print(f"sent_massage is {sent_massage.id}")
    with get_db_connection() as conn:
        upd_user_message_to_edit(conn, user_id, sent_massage.id)

def help(message):
    """Helps user to understand how it works | Помогает пользользователю понять как оно работает"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    prev_message = 0
    with get_db_connection() as conn:
        prev_message = get_user_message_to_edit(conn, user_id)

    print(f"\tkek sent_massage is {prev_message}")
    tb.delete_message(user_id, message.message_id)
    tb.edit_message_text("Напиши место, которое тебя интересует или напиши 'случайно', чтобы получить случайное место", chat_id=message.chat.id, message_id=prev_message)

def place(message):
    """Gets user"s request for place | Получает запрос пользователя на место"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    prev_message = 0
    with get_db_connection() as conn:
        prev_message = get_user_message_to_edit(conn, user_id)

    tb.delete_message(user_id, message.message_id)
    
    with get_db_connection() as conn:
        upd_user_last_request(conn, user_id, message.text)

    if message.text == "случайно" or message.text == "Случайно":
        tb.edit_message_text("не, чет не хочу пока", chat_id=message.chat.id, message_id=prev_message)
    else:
        tb.edit_message_text(f"Ищем места по запросу: {message.text}", chat_id=message.chat.id, message_id=prev_message)
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = KeyboardButton("Отправить геолокацию", request_location=True)
        markup.add(button)
        tb.send_message(user_id, "Пожалуйста, поделитесь своим местоположением:", reply_markup=markup)

def user_settings(message):
    """получить из бд настройки пользователя, в случае отсуствия, занести дефоль"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    print(message.id)
    tb.delete_message(user_id, message.id)
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton("🗺️WIP", callback_data="distance"),
               InlineKeyboardButton("⭐", callback_data="rating"),
               InlineKeyboardButton("💬", callback_data="comments"))
    tb.send_message(user_id, "Тут ты можешь изменить расстояние поиска мест и посмотреть свои оценки и комментарии", reply_markup=markup)

def operator(call):
    """реакция на кнопки"""
    user_id = call.from_user.id
    if call.data == "distance":
        with get_db_connection() as conn:
            upd_user_status(conn, "distance")
        tb.send_message(user_id, "Напиши желаемое расстояние поиска числом в километрах или название города")
        #реализуй try except для того чтобы узнать расстояние / город
    if call.data == "rating":
        with get_db_connection() as conn:
            upd_user_status(conn, "rating")
        tb.send_message(user_id, "Напиши оценку, которую хочешь поставить месту от 1 до 10")
    if call.data == "comments":
        with get_db_connection() as conn:
            upd_user_status(conn, "comments")
        tb.send_message(user_id, "МАШИНА ПОЛОЖИ БАНКОМАТ!!!!")
    if call.data in {"r1", "r2", "r3", "r4", "r5"}:
        with get_db_connection() as conn:
            upd_user_status(conn, user_id, call.data)
        tb.send_message(user_id, "Напиши оценку, которую хочешь поставить месту от 1 до 10")
    if call.data in {"c1", "c2", "c3", "c4", "c5"}:
        with get_db_connection() as conn:
            upd_user_status(conn, user_id, call.data)
        tb.send_message(user_id, "Напиши комментарий, который хотите оставить")


def change_distance(message):
    """меняем дистанцию поиска мест"""
    if message.isdigit():
        print(int(message))
        with get_db_connection() as conn:
            upd_user_distance(conn, int(message))
    else:
        with get_db_connection() as conn:
            upd_user_city(conn, message)
    with get_db_connection() as conn:
        upd_user_status(conn, "start")

from costil import ids

from commet_requests import edit_comment_rating
from commet_requests import commented_by_user, edit_comment
from commet_requests import edit_comment_text
def set_rating(message):
    user_id = message.from_user.id
    tb.delete_message(user_id, message.id - 1)
    tb.delete_message(user_id, message.id)

    with get_db_connection() as conn:
        status = get_user_status(conn, user_id)
    
    needed_place = int(status[-1])
    place_id = ids[needed_place]
    if message.text.isdigit():
        print(int(message.text))
        with get_db_connection() as conn:
            if (commented_by_user(conn, user_id, place_id)):
                edit_comment_rating(conn, user_id, place_id, int(message.text))
            else:
                add_comment(conn, user_id, place_id, "NULL", int(message.text))
    else:
        print("needed to do try exept")

    
    sent_massage = tb.send_message(user_id,
            f"твоя оценка учтена)")
    sleep(1)
    tb.delete_message(user_id, sent_massage.id)
    
    with get_db_connection() as conn:
        upd_user_status(conn, user_id, "start")

def set_comment(message):
    user_id = message.from_user.id
    tb.delete_message(user_id, message.id - 1)
    tb.delete_message(user_id, message.id)

    with get_db_connection() as conn:
        status = get_user_status(conn, user_id)
    
    needed_place = int(status[-1])
    place_id = ids[needed_place]
    with get_db_connection() as conn:
        if (commented_by_user(conn, user_id, place_id)):
            edit_comment_text(conn, user_id, place_id, message.text)
        else:
            add_comment(conn, user_id, place_id, message.text, 5)
    
    
    sent_massage = tb.send_message(user_id,
            f"твой комментарий учтен)")
    sleep(1)
    tb.delete_message(user_id, sent_massage.id)
    
    with get_db_connection() as conn:
        upd_user_status(conn, user_id, "start")

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