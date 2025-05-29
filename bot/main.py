import sys

import telebot
import os
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from funcs import start, help, place, user_settings, change_distance, v1
from ya_ai_xd import handle_location, create_navigation_keyboard
from settings_requests import get_db_connection, get_user_status, upd_user_status
from secret import tg_api
from commet_requests import get_comment_by_comment_id
from ya_ai_xd import create_place_card_by_db
from places_requests import get_place_by_id
from settings_requests import get_user_request_ids, get_current_index, upd_current_index, get_user_request_comment_ids, \
    upd_current_comment_index, get_current_comment_index
from comments import create_comment_card, create_navigation_keyboard_for_comments, get_comments, \
    get_user_comments, create_navigation_keyboard_for_user_comments, print_place
from funcs import set_comment, set_rating

apishka = os.environ.get("TELEGRAM_API_TOKEN", tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)
tb.remove_webhook()
# tb.send_message(419737412, "Бот запущен админом @flovvey36 (это сообщение видят лишь избранные)")
tb.send_message(1765684196, "Бот запущен админом @flovvey36 (это сообщение видят лишь избранные)")
tb.send_message(1458457789, "Бот запущен админом @flovvey36 (это сообщение видят лишь избранные)")


@tb.message_handler(commands=['shutdown'])
def stop(message):
    user_id = message.from_user.id
    if user_id in [419737412, 1765684196, 1458457789]:
        tb.send_message(419737412, f"{message.from_user.first_name} (@{message.from_user.username}) прервал работу бота с "
                                   f"помощью /shutdown")
        tb.send_message(1765684196, f"{message.from_user.first_name} (@{message.from_user.username}) прервал работу бота с "
                                    f"помощью /shutdown")
        tb.send_message(1458457789, f"{message.from_user.first_name} (@{message.from_user.username}) прервал работу бота с "
                                    f"помощью /shutdown")
        tb.stop_polling()
    else:
        tb.send_message(user_id, "Недостаточно прав для выполнения задачи")


@tb.message_handler(commands=["start"])
def start_handler(message):
    start(message)


@tb.message_handler(commands=["help"])
def help_handler(message):
    help(message)


@tb.message_handler(commands=["settings"])
def settings_handler(message):
    user_settings(message)


@tb.message_handler(commands=["promote"])
def promotion(message):
    tb.send_message(message.from_user.id, "Получил вашу заявку, в ближайшее время администраторы ее рассмотрят")
    tb.send_message(419737412,
                    f"Пользователь @{message.from_user.username} с id: `{message.from_user.id}` запросил "
                    f"повышение", parse_mode="MarkdownV2")
    tb.send_message(1765684196,
                    f"Пользователь @{message.from_user.username} с id: `{message.from_user.id}` запросил повышение",
                    parse_mode="MarkdownV2")
    tb.send_message(1458457789,
                    f"Пользователь @{message.from_user.username} с id: `{message.from_user.id}` запросил повышение",
                    parse_mode="MarkdownV2")


@tb.message_handler(commands=["add_moder"])
def promotion(message):
    user_id = message.from_user.id
    tb.delete_message(user_id, message.id)
    with get_db_connection() as conn:
        upd_user_status(conn, user_id, "add_moder")
    tb.send_message(message.from_user.id, """Напиши username пользователя, которого хочешь повысить до модератора
                                            в формате @username""")


from funcs import add_moder
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
    elif status == "rating":
        change_distance(message)
    elif status == "comments":
        change_distance(message)
    elif status in {"r_1", "r_2", "r_3", "r_4", "r_5"}:
        set_rating(message)
    elif status in {"c_1", "c_2", "c_3", "c_4", "c_5"}:
        set_comment(message)
    elif status == "add_moder":
        add_moder(message)


@tb.message_handler(content_types=["location"])
def location_handler(message):
    handle_location(message)


@tb.message_handler(commands=['v1'])
def gab(message):
    v1(message)


from commet_requests import delete_comment
@tb.callback_query_handler()
def handle_navigation(call):
    if call.data.startswith(('prev_', 'next_', 'rate_', 'comment_', "back_", "get_comm_")):
        """Обрабатывает навигацию между местами"""

        try:
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            with get_db_connection() as conn:
                current_index = get_current_index(conn, user_id)
                places_ids = get_user_request_ids(conn, user_id)

            total_places = len(places_ids)
            print(places_ids)

            # Определяем новую позицию
            if call.data.startswith('prev_'):
                new_index = max(0, current_index - 1)
            elif call.data.startswith('next_'):
                new_index = min(total_places - 1, current_index + 1)
            elif call.data.startswith('back_'):
                new_index = current_index
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
            elif call.data.startswith("get_comm_"):
                # print("error piska")
                place_index = int(call.data.split('_')[2])
                get_comments(user_id, chat_id, message_id, places_ids[place_index], place_index, call.id)
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

    elif call.data.startswith(("comm_prev_", "comm_next_", "comm_back_")):
        """Навигация в комментариях"""
        try:
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            if call.data.startswith(('comm_next_u_', 'comm_prev_u_')):
                current_index = int(call.data.split('_')[3])
            else :
                current_index = int(call.data.split('_')[2])
            with get_db_connection() as conn:
                comment_ids = get_user_request_comment_ids(conn, user_id)

            total_comments = len(comment_ids)

            # Определяем новую позицию
            # call.data.startswith('rate_')
            if call.data.startswith('comm_prev_'):
                new_index = max(0, current_index - 1)
            elif call.data.startswith('comm_next_'):
                # current_index = int(current_index)
                new_index = min(total_comments - 1, current_index + 1)
            elif call.data.startswith('comm_back_'):
                new_index = current_index
            else:
                return

            # Обновляем текущий индекс
            with get_db_connection() as conn:
                upd_current_comment_index(conn, user_id, new_index)

            comment_id = comment_ids[new_index]
            print(comment_ids)

            # Создаем новое сообщение
            card_text = create_comment_card(comment_id)
            if call.data.startswith(('comm_next_u_', 'comm_prev_u_', 'comm_back_')):
                with get_db_connection() as conn:
                    comm = get_comment_by_comment_id(conn, comment_id)
                markup = create_navigation_keyboard_for_user_comments(new_index, total_comments, comm["place_id"])
            else:
                with get_db_connection() as conn:
                    comm_idx = get_current_index(conn, user_id)
                markup = create_navigation_keyboard_for_comments(user_id, new_index, total_comments, comm_idx, comment_id)

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
    elif call.data.startswith(("rem_")):

        try:
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            
            comm_id = int(call.data.split('_')[1])
            with get_db_connection() as conn:
                delete_comment(conn, comm_id)
            tb.answer_callback_query(call.id, "Коммент удален")

        except Exception as e:
            print(f"Error in handle_navigation: {e}")
            tb.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")
    else:
        """Обрабатывает настройки"""
        try:
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            # Определяем новую позицию
            if call.data.startswith('distance'):
                with get_db_connection() as conn:
                    upd_user_status(conn, user_id, "distance")
                    tb.send_message(call.from_user.id, "Вы собираетесь изменить расстояние, напишите желаемое в км")
            elif call.data.startswith('comments'):
                get_user_comments(user_id, chat_id, message_id, call.id)
            elif call.data.startswith('place_'):
                with get_db_connection() as conn:
                    curr_inx = int(get_current_comment_index(conn, user_id))
                place_id = int(call.data.split('_')[1])
                print_place(user_id, curr_inx, chat_id, message_id, call.id, place_id)
            else:
                return
        except Exception as e:
            print(f"Error in handle_navigation: {e}")
            tb.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")


tb.infinity_polling()