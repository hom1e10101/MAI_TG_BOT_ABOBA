import telebot
import os
from telebot.storage import StateMemoryStorage
from funcs import start, help, place, user_settings, change_distance
from ya_ai_xd import handle_location, create_navigation_keyboard, create_place_card, user_places_data
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


'''from funcs import set_comment, set_rating
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
    elif status in {"r1", "r2", "r3", "r4", "r5"}:
        set_rating(message)
    elif status in {"c1", "c2", "c3", "c4", "c5"}:
        set_comment(message)'''


@tb.message_handler(content_types=["location"])
def location_handler(message):
    handle_location(message)


@tb.callback_query_handler()
def handle_navigation(call):
    """Обрабатывает навигацию между местами"""
    if call.data in ['prev_', 'next_', 'rate_', 'comment_']:
        try:
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            # Проверяем наличие данных
            if user_id not in user_places_data or 'places' not in user_places_data[user_id]:
                tb.answer_callback_query(call.id, "Данные устарели. Пожалуйста, выполните новый поиск.")
                return

            places = user_places_data[user_id]['places']
            total_places = len(places)
            current_index = user_places_data[user_id].get('current_index', 0)

            # Определяем новую позицию
            if call.data.startswith('prev_'):
                new_index = max(0, current_index - 1)
            elif call.data.startswith('next_'):
                new_index = min(total_places - 1, current_index + 1)
            elif call.data.startswith('rate_'):
                place_index = int(call.data.split('_')[1])
                place = places[place_index]
                tb.answer_callback_query(call.id, f"Вы хотите оценить место: {place['properties']['name']}")
                return
            elif call.data.startswith('comment_'):
                place_index = int(call.data.split('_')[1])
                place = places[place_index]
                tb.answer_callback_query(call.id, f"Вы хотите оставить комментарий к месту: {place['properties']['name']}")
                return
            else:
                return

            # Обновляем текущий индекс
            user_places_data[user_id]['current_index'] = new_index
            place = places[new_index]

            # Создаем новое сообщение
            card_text = create_place_card(place, new_index, total_places)
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
    else:
        user_id = call.from_user.id
        if call.data == "distance":
#            with get_db_connection() as conn:
#                upd_user_status(conn, "distance")
            tb.send_message(user_id, "Напиши желаемое расстояние поиска числом в километрах или название города")
        if call.data == "rating":
#            with get_db_connection() as conn:
#                upd_user_status(conn, "rating")
            tb.send_message(user_id, "Мои оценочкииииии")
        if call.data == "comments":
#            with get_db_connection() as conn:
#                upd_user_status(conn, "comments")
            tb.send_message(user_id, "МАШИНА ПОЛОЖИ БАНКОМАТ!!!!")
        if call.data == "visited":
            tb.send_message(user_id, "Монетка делает дзинь дзинь")

tb.infinity_polling()