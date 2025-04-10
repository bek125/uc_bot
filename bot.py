from flask import Flask, request
import telebot

API_TOKEN = 'YOUR_BOT_TOKEN'  # << bu yerga o'zingni TOKENni yoz
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- Bot komandasi ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom, bot ishlayapti!")

# --- Webhook uchun endpoint ---
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return '', 403

# --- Botni boshlash ---
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://YOUR_RENDER_URL.onrender.com/')  # Bu yerga o'zingni URL yoz
    app.run(host="0.0.0.0", port=5000)
