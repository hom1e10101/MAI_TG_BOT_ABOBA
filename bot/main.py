
import telebot
import os
from telebot.storage import StateMemoryStorage
from funcs import start, help, place
from ya_ai_xd import handle_location 
# from shared_state import last_request

apishka = os.environ.get('TELEGRAM_API_TOKEN', '7732717132:AAHPdgXQJGvWUzP2MaYpZQ7vxwyaQGEHv1s')
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)
tb.remove_webhook()

@tb.message_handler(commands=['start'])
def start_handler(message):
    start(message)

@tb.message_handler(commands=['help'])
def help_handler(message):
    help(message)

@tb.message_handler()
def message_handler(message):
    place(message)

@tb.message_handler(content_types=['location'])
def location_handler(message):
    handle_location(message)

tb.infinity_polling()
