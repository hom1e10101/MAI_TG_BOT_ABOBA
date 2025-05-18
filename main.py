import telebot
import os
from telebot.storage import StateMemoryStorage
from funcs import start, help, place, user_settings, operator, change_distance, pAshAlk0
from ya_ai_xd import handle_location
from settings_requests import get_db_connection, get_user_status, upd_user_status

from secret import tg_api

apishka = os.environ.get('TELEGRAM_API_TOKEN', tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)
tb.remove_webhook()


@tb.message_handler(commands=['start'])
def start_handler(message):
    start(message)


@tb.message_handler(commands=['help'])
def help_handler(message):
    help(message)


@tb.message_handler(commands=['settings'])
def settings_handler(message):
    user_settings(message)

@tb.message_handler(commands=['pashalko'])
def pashalk0(message):
    pAshAlk0(message)

@tb.message_handler()
def message_handler(message):
    status = ''
    user_id = message.from_user.id
    user_id = message.from_user.id
    with get_db_connection() as conn:
        status = get_user_status(conn, user_id)
    if status == "start":
        place(message)
    elif status == "distance":
        change_distance(message)
    elif status == "comments":
        pass


@tb.message_handler(content_types=['location'])
def location_handler(message):
    handle_location(message)


@tb.callback_query_handler(func=lambda call: True)
def perehodnik(call):
    operator(call)






tb.infinity_polling()
