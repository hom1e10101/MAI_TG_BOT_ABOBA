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
from users_requests import get_user_name_by_user_id, get_user_user_name

def create_navigation_keyboard_for_comments(user_id, current_index, total_comments, place_idx, comment_id):
    """Создает клавиатуру для навигации между комментариями"""
    markup = InlineKeyboardMarkup()
    row = []

    if current_index > 0:
        row.append(InlineKeyboardButton("⬅️", callback_data=f"comm_prev_{current_index}"))
    if current_index < total_comments - 1:
        row.append(InlineKeyboardButton("➡️", callback_data=f"comm_next_{current_index}"))
    markup.row(*row)

    row2 = []
    row2.append(InlineKeyboardButton("Назад", callback_data=f"back_{place_idx}"))
    markup.row(*row2)

    with get_db_connection() as conn:
        role = get_user_role(conn, user_id)
    if role is not None and role in ["admin", "moderator"]:
        row3 = []
        row3.append(InlineKeyboardButton("Удалить", callback_data=f"rem_{comment_id}"))
        markup.row(*row3)
    return markup

def create_comment_card(comment_id):
    """Делает карточку комментария"""
    if comment_id is None:
        return "Нет такого комментария"
    with get_db_connection() as conn:
        comment = get_comment_by_comment_id(conn, comment_id)
        if comment is not None:
            user_name = get_user_name_by_user_id(conn, comment["user_id"])
            user_id = comment["user_id"]
            user_user_name = get_user_user_name(conn, user_id)
            place_name = get_name_by_place_id(conn, comment["place_id"])
            rating = comment["rating"]
            if user_user_name is not None:
                text = f"Отзыв от: @{user_user_name}\n"
            else:
                text = f"Отзыв от: {user_name}"
            text += f"На место: {place_name}\n"
            if (rating is not None and rating > 0):
                text += f"Оценка: {rating}\n\n"
            else:
                text += "\n"
            if comment["text"] != "NULL":
                text += comment["text"]
            return text
        else: return "нет такого комментария"

from settings_requests import get_user_request_comment_ids, upd_user_request_comment_ids
from commet_requests import get_comments_of_place
def get_comments(user_id, chat_id, message_id, place_id, place_idx, call_id):
    """Получаем комментарии на место"""
    with get_db_connection() as conn:
        comments_ids = get_comments_of_place(conn, place_id)

    if (len(comments_ids) == 0):
        tb.answer_callback_query(call_id, f"Нет комментариев")
        return

    with get_db_connection() as conn:
        upd_user_request_comment_ids(conn, user_id, comments_ids)

    comment_id = comments_ids[0]
    card_text = create_comment_card(comment_id)

    markup = create_navigation_keyboard_for_comments(user_id, 0, len(comments_ids), place_idx, comment_id)
    tb.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=card_text,
        parse_mode="Markdown",
        reply_markup=markup,
        disable_web_page_preview=True
    )


def create_navigation_keyboard_for_user_comments(current_index, total_comments, place_id):
    """Создает клавиатуру для навигации между комментариями пользователя"""
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
    row2 = []
    if place_id != -1:
        row2.append(InlineKeyboardButton("📝", callback_data=f"redact_text_{current_index}"))
        row2.append(InlineKeyboardButton("⭐", callback_data=f"redact_rating_{current_index}"))
        markup.row(*row2)
    return markup


from commet_requests import get_user_comment_ids
def get_user_comments(user_id, chat_id, message_id, call_id):
    """Получаем комментарии пользователя"""
    with get_db_connection() as conn:
        comments_ids = get_user_comment_ids(conn, user_id)

    if (len(comments_ids) == 0):
        tb.answer_callback_query(call_id, f"Нет комментариев")
        return

    with get_db_connection() as conn:
        upd_user_request_comment_ids(conn, user_id, comments_ids)

    comment_id = comments_ids[0]
    card_text = create_comment_card(comment_id)

    with get_db_connection() as conn:
        place_id = get_comment_by_comment_id(conn, comment_id)["place_id"]

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
    """Выводит место, на которое оставлял комментарий юзер"""
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