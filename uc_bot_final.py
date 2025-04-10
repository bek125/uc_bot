
import telebot
from telebot import types
import json
from datetime import datetime
import requests
import pandas as pd
import socket
import os

TOKEN = '7618485150:AAFdtCQkpwd572NYHt7CiHlRDzdbCa3pmlg'
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 1382850686

# UC variantlari
uc_options = {
    '60 UC': '14,000 so‘m',
    '180 UC': '39,000 so‘m',
    '325 UC': '60,000 so‘m',
    '660 UC': '115,000 so‘m'
}

user_data = {}
all_orders = []
blacklist = set()

ORDER_FILE = 'orders.json'

API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJhY2I1YTc1MC1mNjY1LTAxM2QtZTdkYy0wNjFhOWQ1YjYxYWYiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNzQ0MDg5MDEyLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6Ii05NWE5NTRlNS03YmQ1LTQ2YjktOTNmYy1jNGQ0ODYxYzg2MzcifQ.2tmUT7NRbzzzm8rs0DJmUfZmOCPp9mYSGxB_5TKaY_M'

def save_orders():
    with open(ORDER_FILE, 'w') as f:
        json.dump(all_orders, f, indent=2)

def load_orders():
    global all_orders
    try:
        with open(ORDER_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                all_orders = []
            else:
                all_orders = json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        all_orders = []

load_orders()

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id in blacklist:
        return bot.send_message(message.chat.id, "🚫 Siz botdan foydalanishingiz bloklangan.")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for uc in uc_options:
        markup.add(uc)
    bot.send_message(
        message.chat.id,
        "👋 Xush kelibsiz *UC Market* botiga!\n\n"
        "👇 Kerakli UC paketini tanlang:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text in uc_options)
def ask_pubg_id(message):
    if message.from_user.id in blacklist:
        return bot.send_message(message.chat.id, "🚫 Siz botdan foydalanishingiz bloklangan.")
    user_data[message.chat.id] = {'uc': message.text}
    bot.send_message(message.chat.id, "📌 PUBG ID'ingizni yuboring:")

@bot.message_handler(func=lambda message: message.chat.id in user_data and 'pubg_id' not in user_data[message.chat.id])
def get_pubg_id(message):
    pubg_id = message.text

    url = f"https://api.gamelockerapp.com/shards/asia/players?filter[playerIds]={pubg_id}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/vnd.api+json"
    }

    try:
        socket.gethostbyname("api.gamelockerapp.com")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return bot.send_message(message.chat.id, "❌ PUBG ID topilmadi yoki noto‘g‘ri.")
    except socket.gaierror:
        return bot.send_message(message.chat.id, "⚠️ DNS blokirovkasi aniqlangandi. VPN orqali urinib ko‘ring.")
    except requests.exceptions.RequestException:
        return bot.send_message(message.chat.id, "⚠️ Tarmoq xatosi yuz berdi.")

    user_data[message.chat.id]['pubg_id'] = pubg_id
    uc = user_data[message.chat.id]['uc']
    narx = uc_options[uc]

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ To‘ladim", callback_data="paid"))

    bot.send_message(
        message.chat.id,
        f"💳 To‘lovni quyidagi kartaga yuboring:\n\n"
        f"*HUMO/UZCARD:* 5614 6816 0723 9906\n"
        f"*VISA/MASTERCARD:* 4916 9902 0011 5456\n"
        f"*Summa:* {narx}\n\n"
        f"To‘lov qilgach, \"To‘ladim\" tugmasini bosing 👇",
        reply_markup=markup,
        parse_mode='Markdown'
    )

bot.polling(none_stop=True, interval=0, timeout=30)
