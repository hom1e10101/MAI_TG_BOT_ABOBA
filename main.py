import telebot
from telebot.storage import StateMemoryStorage
from funcs import start, help, place
from ya_ai_xd import handle_location 
# from shared_state import last_request

with open('huy_vam_a_ne_apishka_sini_blyadey.txt', 'r') as file:
    apishki = file.readlines()
tgap = apishki[0]
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(tgap, state_storage=state_storage)
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
