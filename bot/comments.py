import telebot
import json
import os
import requests
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from users_requests import get_db_connection, add_user_to_base, upd_user_name, get_user_role, upd_user_role

from settings_requests import get_user_message_to_edit, upd_user_message_to_edit, get_user_city, upd_user_city, \
    get_user_distance, upd_user_distance, get_user_last_request, upd_user_last_request

from secret import yandex_url, yandex_api, tg_api

apishka = os.environ.get('TELEGRAM_API_TOKEN', tg_api)
state_storage = StateMemoryStorage()
tb = telebot.TeleBot(apishka, state_storage=state_storage)

from places_requests import add_place_to_base, get_place_by_id, \
    place_in_base, get_places_db_connection, get_id_by_name_address, get_name_by_place_id
from settings_requests import upd_user_request_ids
from commet_requests import get_place_rating, get_comment_by_comment_id
from users_requests import get_user_name_by_user_id

def create_navigation_keyboard_for_comments(current_index, total_comments, place_idx):
    """Создает клавиатуру для навигации между местами"""
    markup = InlineKeyboardMarkup()
    row = []
    if current_index > 0:
        row.append(InlineKeyboardButton("⬅️", callback_data=f"comm_prev_{current_index}"))
    if current_index < total_comments - 1:
        row.append(InlineKeyboardButton("➡️", callback_data=f"comm_next_{current_index}"))
    row.append(InlineKeyboardButton("Назад", callback_data=f"back_{place_idx}"))
    markup.row(*row)
    return markup

def create_comment_card(comment_id):
    with get_db_connection() as conn:
        comment = get_comment_by_comment_id(conn, comment_id)
        user_name = get_user_name_by_user_id(conn, comment["user_id"])
        place_name = get_name_by_place_id(conn, comment["place_id"])
    rating = comment["rating"]
    if comment is not None:
        text = f"Отзыв от: {user_name}\n"
        text += f"На место: {place_name}\n"
        if (rating > 0):
            text += f"Оценка: {rating}\n\n"
        else:
            text += "\n"
        if comment["text"] != "NULL":
            text += comment["text"]
        print(text)
        return text
    else: return "нет такого комментария"

from settings_requests import get_user_request_comment_ids, upd_user_request_comment_ids
from commet_requests import get_comments_of_place
def get_comments(user_id, chat_id, message_id, place_id, place_idx, call_id):
    with get_db_connection() as conn:
        comments_ids = get_comments_of_place(conn, place_id)

    if (len(comments_ids) == 0):
        tb.answer_callback_query(call_id, f"Нет комментариев")
        return

    with get_db_connection() as conn:
        upd_user_request_comment_ids(conn, user_id, comments_ids)

    comment_id = comments_ids[0]
    card_text = create_comment_card(comment_id)

    markup = create_navigation_keyboard_for_comments(0, len(comments_ids), place_idx)
    tb.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=card_text,
        parse_mode="Markdown",
        reply_markup=markup,
        disable_web_page_preview=True
    )


def create_navigation_keyboard_for_user_comments(current_index, total_comments, place_id):
    """Создает клавиатуру для навигации между местами"""
    print("lelelelelel")
    markup = InlineKeyboardMarkup()
    row = []

    if current_index > 0:
        row.append(InlineKeyboardButton("⬅️", callback_data=f"comm_prev_u_{current_index}"))
    
    if place_id != -1:
        row.append(InlineKeyboardButton("ℹ️", callback_data=f"place_{place_id}"))
    else:
        row.append(InlineKeyboardButton("💬", callback_data=f"comm_back_{current_index}"))
    
    if current_index < total_comments - 1:
        row.append(InlineKeyboardButton("➡️", callback_data=f"comm_next_u_{current_index}"))
    markup.row(*row)
    return markup


from commet_requests import get_user_comment_ids
def get_user_comments(user_id, chat_id, message_id, call_id):
    with get_db_connection() as conn:
        comments_ids = get_user_comment_ids(conn, user_id)

    if (len(comments_ids) == 0):
        tb.answer_callback_query(call_id, f"Нет комментариев")
        return

    with get_db_connection() as conn:
        upd_user_request_comment_ids(conn, user_id, comments_ids)

    comment_id = comments_ids[0]
    print(comments_ids)
    card_text = create_comment_card(comment_id)

    with get_db_connection() as conn:
        place_id = get_comment_by_comment_id(conn, comment_id)["place_id"]

    print(card_text)
    markup = create_navigation_keyboard_for_user_comments(0, len(comments_ids), place_id)
    tb.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=card_text,
        parse_mode="Markdown",
        reply_markup=markup,
        disable_web_page_preview=True
    )


from ya_ai_xd import create_place_card_by_db
def print_place(user_id, current_index, chat_id, message_id, call_id, place_id):
    text = create_place_card_by_db(place_id, 1, 1)
    with get_db_connection() as conn:
        comment_ids = get_user_request_comment_ids(conn, user_id)
    markup = create_navigation_keyboard_for_user_comments(current_index, len(comment_ids), -1)
    tb.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=markup,
        disable_web_page_preview=True
    )
