import telebot
import os
from telebot.storage import StateMemoryStorage
from funcs import start, help, place, user_settings, operator, change_distance
from ya_ai_xd import handle_location, create_navigation_keyboard
from settings_requests import get_db_connection, get_user_status, upd_user_status

from secret import tg_api

apishka = os.environ.get("TELEGRAM_API_TOKEN", tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)
tb.remove_webhook()

@tb.message_handler(commands=["start"])
def start_handler(message):
    start(message)

@tb.message_handler(commands=["help"])
def help_handler(message):
    help(message)

@tb.message_handler(commands=["settings"])
def settings_handler(message):
    user_settings(message)


from funcs import set_comment, set_rating
@tb.message_handler()
def message_handler(message):
    status = ""
    user_id = message.from_user.id
    with get_db_connection() as conn:
        status = get_user_status(conn, user_id)
    
    if status == "start":
        place(message)
    elif status == "distance":
        change_distance(message)
    elif status in {"r_1", "r_2", "r_3", "r_4", "r_5"}:
        print("goes wrong not WW")
        set_rating(message)
    elif status in {"c_1", "c_2", "c_3", "c_4", "c_5"}:
        set_comment(message)


@tb.message_handler(content_types=["location"])
def location_handler(message):
    handle_location(message)


from ya_ai_xd import create_place_card_by_db
from places_requests import get_place_by_id
from settings_requests import get_user_places_ids, get_current_index, upd_current_index
@tb.callback_query_handler(func=lambda call: call.data.startswith(('prev_', 'next_', 'rate_', 'comment_')))
def handle_navigation(call):
    """Обрабатывает навигацию между местами"""
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        with get_db_connection() as conn:
            current_index = get_current_index(conn, user_id)
            places_ids = get_user_places_ids(conn, user_id, 5)
    
        total_places = len(places_ids)


        # Определяем новую позицию
        if call.data.startswith('prev_'):
            new_index = max(0, current_index - 1)
        elif call.data.startswith('next_'):
            new_index = min(total_places - 1, current_index + 1)
        elif call.data.startswith('rate_'):
            place_index = int(call.data.split('_')[1])
            
            place_id = places_ids[place_index]
            name = ''
            with get_db_connection() as conn:
                name = get_place_by_id(conn, place_id)["name"]

            tb.answer_callback_query(call.id, f"Вы хотите оценить место: {name}")

            with get_db_connection() as conn:
                upd_user_status(conn, user_id, f'r_{place_index + 1}')
            tb.send_message(user_id, "Напишите оценку, которую хотите оставить")
            return
        elif call.data.startswith('comment_'):
            place_index = int(call.data.split('_')[1])
            
            place_id = places_ids[place_index]
            name = ''
            with get_db_connection() as conn:
                name = get_place_by_id(conn, place_id)['name']

            tb.answer_callback_query(call.id, f"Вы хотите оставить комментарий к месту: {name}")

            with get_db_connection() as conn:
                upd_user_status(conn, user_id, f'c_{place_index + 1}')
            tb.send_message(user_id, "Напишите комментарий, который хотите оставить")
            return
        else:
            return

        # Обновляем текущий индекс
        with get_db_connection() as conn:
            upd_current_index(conn, user_id, new_index)
        
        place_id = places_ids[new_index]

        # Создаем новое сообщение        
        card_text = create_place_card_by_db(place_id, new_index, total_places)
        markup = create_navigation_keyboard(new_index, total_places)

        tb.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=card_text,
            parse_mode="Markdown",
            reply_markup=markup,
            disable_web_page_preview=True
        )

        tb.answer_callback_query(call.id)
    except Exception as e:
        print(f"Error in handle_navigation: {e}")
        tb.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")

tb.infinity_polling()