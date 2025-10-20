import telebot
import sqlite3
import os
from datetime import datetime

# دریافت توکن از Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# ساخت ربات
bot = telebot.TeleBot(BOT_TOKEN)

def init_db():
    conn = sqlite3.connect('navaaran_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT,
                  join_date TEXT, user_rank TEXT, total_sales INTEGER)''')
    conn.commit()
    conn.close()

# منوی اصلی
main_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row('📋 خدمات ما', '💸 پورسانت و پاداش')
main_keyboard.row('🎯 آموزش فروش', '👥 برنامه رفرال')
main_keyboard.row('❤️ مشتریان وفادار', '⭐ نمونه کارها')
main_keyboard.row('📊 پنل شخصی', '📞 ارتباط با مدیریت')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    init_db()
    bot.send_message(
        message.chat.id,
        "🚀 **به ربات آژانس تبلیغاتی نوآوران خوش آمدید!**\n\n"
        "لطفاً از منوی زیر انتخاب کنید:",
        reply_markup=main_keyboard
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    
    if text == '📋 خدمات ما':
        bot.send_message(message.chat.id, "🎨 **خدمات ما:**\n• طراحی لوگو\n• طراحی سایت\n• چاپ کارت ویزیت\n• مشاوره برندینگ")
    
    elif text == '💸 پورسانت و پاداش':
        bot.send_message(message.chat.id, "💰 **پورسانت:**\n۷٪ تا ۱۲٪ + پاداش‌های نقدی")
    
    elif text == '📊 پنل شخصی':
        bot.send_message(message.chat.id, "📊 **پنل شخصی شما:**\n• فروش ماه: ۰ تومان\n• پورسانت: ۷٪")
    
    elif text == '🎯 آموزش فروش':
        bot.send_message(message.chat.id, "🎓 **آموزش فروش:**\n• شناسایی مشتری\n• ارائه خدمات\n• ثبت سفارش")
    
    elif text == '👥 برنامه رفرال':
        bot.send_message(message.chat.id, "🤝 **برنامه رفرال:**\n• معرفی بازاریاب: ۱۰۰,۰۰۰ تومان\n• معرفی مشتری: تخفیف ۱۰٪")
    
    elif text == '❤️ مشتریان وفادار':
        bot.send_message(message.chat.id, "💎 **مشتریان وفادار:**\n• تخفیف پلکانی\n• خدمات ویژه")
    
    elif text == '⭐ نمونه کارها':
        bot.send_message(message.chat.id, "🏆 **نمونه کارها:**\n• طراحی لوگو رستوران\n• سایت فروشگاهی\n• برندینگ شرکتی")
    
    elif text == '📞 ارتباط با مدیریت':
        bot.send_message(message.chat.id, "📞 **ارتباط با مدیریت:**\n👤 مدیر: [نام مدیر]\n📱 موبایل: [شماره موبایل]")
    
    else:
        bot.send_message(message.chat.id, "لطفاً از منوی زیر انتخاب کنید:", reply_markup=main_keyboard)

if __name__ == '__main__':
    print("🤖 ربات نوآوران با pytelegrambotapi اجرا شد...")
    bot.infinity_polling()
