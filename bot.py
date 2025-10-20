from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3
import os
from datetime import datetime

# دریافت توکن از Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')

def init_db():
    conn = sqlite3.connect('navaaran_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT,
                  join_date TEXT, user_rank TEXT, total_sales INTEGER)''')
    conn.commit()
    conn.close()

# منوی اصلی
main_keyboard = [
    ['📋 خدمات ما', '💸 پورسانت و پاداش'],
    ['🎯 آموزش فروش', '👥 برنامه رفرال'],
    ['❤️ مشتریان وفادار', '⭐ نمونه کارها'],
    ['📊 پنل شخصی', '📞 ارتباط با مدیریت']
]

reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 **به ربات آژانس تبلیغاتی نوآوران خوش آمدید!**\n\n"
        "لطفاً از منوی زیر انتخاب کنید:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '📋 خدمات ما':
        await update.message.reply_text("🎨 **خدمات ما:**\n• طراحی لوگو\n• طراحی سایت\n• چاپ کارت ویزیت\n• مشاوره برندینگ")
    
    elif text == '💸 پورسانت و پاداش':
        await update.message.reply_text("💰 **پورسانت:**\n۷٪ تا ۱۲٪ + پاداش‌های نقدی")
    
    elif text == '📊 پنل شخصی':
        await update.message.reply_text("📊 **پنل شخصی شما:**\n• فروش ماه: ۰ تومان\n• پورسانت: ۷٪")
    
    else:
        await update.message.reply_text("لطفاً از منوی زیر انتخاب کنید:", reply_markup=reply_markup)

def main():
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 ربات نوآوران اجرا شد...")
    application.run_polling()

if __name__ == '__main__':
    main()
