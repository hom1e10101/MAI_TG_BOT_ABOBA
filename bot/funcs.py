from time import sleep
import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telebot.storage import StateMemoryStorage
from commet_requests import edit_comment_rating
from commet_requests import commented_by_user
from commet_requests import edit_comment_text
from settings_requests import get_user_request_ids
from ya_ai_xd import is_text_normal_yagpt
from users_requests import get_db_connection, add_user_to_base, upd_user_role
from settings_requests import add_user_settings, get_user_message_to_edit, upd_user_message_to_edit, \
    upd_user_city, upd_user_distance, upd_user_last_request
from settings_requests import upd_user_status, get_user_status
from commet_requests import add_comment
from secret import tg_api
from users_requests import get_user_id_by_user_name

apishka = os.environ.get("TELEGRAM_API_TOKEN", tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)


def start(message):
    """Sends start message | Отправляет стартовое сообщение"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    sent_massage = tb.send_message(user_id,
                                   f"Привет, {user_name}! Я бот который поможет тебе открыть новые места в городе! "
                                   f"Чтобы узнать что я умею, напиши /help")
    tb.delete_message(user_id, message_id=message.id)

    with get_db_connection() as conn:
        add_user_to_base(conn, user_id, user_name, message.from_user.username)
        add_user_settings(conn, user_id)

    with get_db_connection() as conn:
        upd_user_status(conn, user_id, "start")

    with get_db_connection() as conn:
        upd_user_message_to_edit(conn, user_id, sent_massage.id)


def help(message):
    """Helps user to understand how it works | Помогает пользользователю понять как оно работает"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    prev_message = 0
    with get_db_connection() as conn:
        prev_message = get_user_message_to_edit(conn, user_id)

    tb.edit_message_text("Напиши место которое тебя интересует, в случае наличия вопросов, пиши @flovvey36",
                         chat_id=message.chat.id, message_id=prev_message)
    tb.delete_message(user_id, message.message_id)


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

    tb.edit_message_text(f"Ищем места по запросу: {message.text}", chat_id=message.chat.id, message_id=prev_message)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton("Отправить геолокацию", request_location=True)
    markup.add(button)
    tb.send_message(user_id, "Пожалуйста, поделитесь своим местоположением:", reply_markup=markup)


def user_settings(message):
    """получить из бд настройки пользователя, в случае отсуствия, занести дефоль"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    with get_db_connection() as conn:
        tb.delete_message(user_id, get_user_message_to_edit(conn, user_id))
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton("🗺️WIP", callback_data="distance"),
               InlineKeyboardButton("💬", callback_data="comments"))
    sent_message = tb.send_message(user_id, "Тут ты можешь изменить расстояние поиска мест и посмотреть свои оценки и "
                                            "комментарии", reply_markup=markup)
    tb.delete_message(user_id, message.id)
    with get_db_connection() as conn:
        upd_user_message_to_edit(conn, user_id, sent_message.id)





def add_moder(message):
    """Добавляем модератора"""
    user_id = message.from_user.id
    username = message.text[1:]

    tb.delete_message(user_id, message.id - 1)
    tb.delete_message(user_id, message.id)
    with get_db_connection() as conn:
        new_user_id = get_user_id_by_user_name(conn, username)
    if new_user_id is not None:
        sent_message = tb.send_message(user_id, "Юзер повышен")
        with get_db_connection() as conn:
            upd_user_role(conn, new_user_id, "moderator")
    else:
        sent_message = tb.send_message(user_id, "Ошибка: юзер с таким юзернеймом не найден")
    with get_db_connection() as conn:
        upd_user_status(conn, message.from_user.id, "start")
    sleep(1)
    tb.delete_message(user_id, sent_message.id)


def change_distance(message):
    """Меняем дистанцию поиска мест"""
    tb.delete_message(message.from_user.id, message.id - 1)
    tb.delete_message(message.from_user.id, message.id)
    if message.text.isdigit():
        with get_db_connection() as conn:
            upd_user_distance(conn, message.from_user.id, message.text)
        sent_message = tb.send_message(message.from_user.id, f"Твое новое расстояние поиска {message.text} км!")
        sleep(1)
        tb.delete_message(message.from_user.id, sent_message.id)
    else:
        with get_db_connection() as conn:
            upd_user_city(conn, message.text)
    with get_db_connection() as conn:
        upd_user_status(conn, message.from_user.id, "start")


def set_rating(message):
    """Добавляем оценку места"""
    user_id = message.from_user.id
    tb.delete_message(user_id, message.id - 1)
    tb.delete_message(user_id, message.id)

    with get_db_connection() as conn:
        status = get_user_status(conn, user_id)

    needed_place = int(status[-1]) - 1

    with get_db_connection() as conn:
        ids = get_user_request_ids(conn, user_id)
    place_id = ids[needed_place]

    response = ""
    if message.text.isdigit() and 0 < int(message.text) <= 10:
        with get_db_connection() as conn:
            if commented_by_user(conn, user_id, place_id):
                edit_comment_rating(conn, user_id, place_id, int(message.text))
            else:
                add_comment(conn, user_id, place_id, "NULL", int(message.text))
    else:
        sent_massage = tb.send_message(user_id,
                                       f"поставьте оценку от 1 до 10, заново использовав кнопку")
        sleep(1.5)
        tb.delete_message(user_id, sent_massage.id)
        return

    sent_massage = tb.send_message(user_id,
                                   f"твоя оценка учтена)")
    sleep(1)
    tb.delete_message(user_id, sent_massage.id)

    with get_db_connection() as conn:
        upd_user_status(conn, user_id, "start")


def set_comment(message):
    """Добавляем комментарий"""
    user_id = message.from_user.id
    tb.delete_message(user_id, message.id - 1)
    tb.delete_message(user_id, message.id)

    with get_db_connection() as conn:
        status = get_user_status(conn, user_id)

    needed_place = int(status[-1]) - 1

    with get_db_connection() as conn:
        ids = get_user_request_ids(conn, user_id)
        place_id = ids[needed_place]
        proverka = is_text_normal_yagpt(message.text)
        if proverka:
            if commented_by_user(conn, user_id, place_id):
                edit_comment_text(conn, user_id, place_id, message.text)
                sent_message = (tb.send_message(message.from_user.id, 'Комментарий обновлен'))
                sleep(1)
                tb.delete_message(message.from_user.id, sent_message.id)
            else:
                add_comment(conn, user_id, place_id, message.text, 0)
                sent_message = (tb.send_message(message.from_user.id, 'Комментарий добавлен'))
                sleep(1)
                tb.delete_message(message.from_user.id, sent_message.id)
        else:
            sent_message = (tb.send_message(message.from_user.id,
                                            "Грешник, твой комментарий содержит ненормативную лексику. Бог тобой не "
                                            "доволен, переписывай, заново нажав кнопку"))
            sleep(2)
            tb.delete_message(message.from_user.id, sent_message.id)
        upd_user_status(conn, user_id, "start")


def v1(message):
    """Шутка"""
    user_id = message.from_user.id
    tb.send_message(user_id, "Machine, turn back now. The layers of this palace are not for your kind. Turn back, "
                             "or you will be crossing the Will of GOD... Your choice is made. As the righteous hand "
                             "of the Father, I shall REND YOU APART, and you will become inanimate once more.")
    sleep(15)
    tb.send_message(user_id, "BEHOLD! THE POWER OF AN ANGEL!")
    sleep(4)
    tb.send_message(user_id, "What? How can this be? Bested by this... this thing? You insignificant FUCK! THIS IS "
                             "NOT OVER! May your woes be many, and your days few!")
    sleep(12)
    tb.send_message(user_id, "Machine, I know you're here. I can smell the insolent stench of your bloodstained "
                             "hands. I await you down below. Come to me.")
    sleep(10)
    tb.send_message(user_id, "Limbo, Lust, all gone... With Gluttony soon to follow. Your kind know nothing but "
                             "hunger; purged all life on the upper layers, and yet they remain unsatiated... As do "
                             "you. You've taken everything from me, machine. And now all that remains is PERFECT "
                             "HATRED")