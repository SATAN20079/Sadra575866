import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive
import json

keep_alive()

BOT_TOKEN = "7961627371:AAE8CQAefLS0C5NZjw03eFNAB1FXvaK5B_k"
bot = telebot.TeleBot(BOT_TOKEN)

def search_user(user_id):
    results = []
    folder = "funstat"
    for file_name in os.listdir(folder):
        if file_name.endswith(".json"):
            with open(os.path.join(folder, file_name), "r") as file:
                try:
                    data = json.load(file)
                    for user in data.get("users", []):
                        if user["user_id"] == user_id:
                            results.append(user)
                except json.JSONDecodeError:
                    continue
    return results

def format_user_data(user_data, page, total_pages):
    return (
        f"Запись {page + 1} из {total_pages}:\n"
        f"- Имя: {user_data.get('first_name', 'Неизвестно')} {user_data.get('last_name', 'Неизвестно')}\n"
        f"- Юзернейм: @{user_data.get('username', 'Неизвестно')}\n"
        f"- Телефон: {user_data.get('phone', 'Неизвестно')}\n"
        f"- Дата сообщения: {user_data.get('message_date', 'Неизвестно')}\n"
        f"- Содержание сообщения: {user_data.get('message_content', 'Нет текста')}\n"
        f"- Ссылка на сообщение: {user_data.get('message_link', 'Нет ссылки')}\n"
        f"- Чат: {user_data.get('chat_name', 'Неизвестно')} (ID: {user_data.get('chat_id', 'Неизвестно')})"
    )

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "سلام! آیدی عددی کاربر مورد نظر رو بفرست تا اطلاعاتش رو بگردم.")

@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_user_id(message):
    user_id = int(message.text)
    matches = search_user(user_id)
    if not matches:
        bot.send_message(message.chat.id, "هیچ اطلاعاتی برای این کاربر پیدا نشد.")
        return

    page = 0
    markup = create_pagination_markup(page, len(matches))
    bot.send_message(message.chat.id, format_user_data(matches[page], page, len(matches)), reply_markup=markup)

def create_pagination_markup(current, total):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    if current > 0:
        buttons.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"page_{current - 1}"))
    if current < total - 1:
        buttons.append(InlineKeyboardButton("بعدی ➡️", callback_data=f"page_{current + 1}"))
    markup.add(*buttons)
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def handle_pagination(call):
    user_id = int(call.message.text.split("ID:")[0].split()[-1])
    matches = search_user(user_id)
    page = int(call.data.split("_")[1])
    markup = create_pagination_markup(page, len(matches))
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=format_user_data(matches[page], page, len(matches)),
        reply_markup=markup
    )

bot.infinity_polling()
