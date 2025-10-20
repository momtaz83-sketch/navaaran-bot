from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import sqlite3
import json
from datetime import datetime, timedelta
import asyncio

# توکن ربات - جایگزین کنید
BOT_TOKEN = "7925234053:AAGsQvx5eyVRQXf0SkhYWODOHo0m_bBbgr4"


# ایجاد دیتابیس
def init_db():
    conn = sqlite3.connect('navaaran_bot.db')
    c = conn.cursor()
    
    # جدول کاربران
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT,
                  phone TEXT, join_date TEXT, user_rank TEXT, 
                  total_sales INTEGER, team_sales INTEGER)''')
    
    # جدول فروش‌ها
    c.execute('''CREATE TABLE IF NOT EXISTS sales
                 (id INTEGER PRIMARY KEY, user_id INTEGER, customer_name TEXT,
                  service_type TEXT, amount INTEGER, sale_date TEXT, status TEXT)''')
    
    # جدول تیم‌سازی
    c.execute('''CREATE TABLE IF NOT EXISTS team_structure
                 (id INTEGER PRIMARY KEY, user_id INTEGER, parent_id INTEGER,
                  join_date TEXT)''')
    
    conn.commit()
    conn.close()

# منوی اصلی
main_keyboard = [
    ['📋 خدمات ما', '💸 پورسانت و پاداش'],
    ['🎯 آموزش فروش', '👥 برنامه رفرال'],
    ['❤️ مشتریان وفادار', '⭐ نمونه کارها'],
    ['📊 پنل شخصی', '📞 ارتباط با مدیریت']
]

# سطوح ارتقا
RANKS = {
    'beginner': {'name': '🥉 بازاریاب تازه‌کار', 'team_bonus': 0.0},
    'senior': {'name': '🥈 بازاریاب ارشد', 'team_bonus': 0.5},
    'supervisor': {'name': '🥇 سرپرست تیم', 'team_bonus': 1.0},
    'manager': {'name': '💎 مدیر فروش', 'team_bonus': 1.5},
    'senior_manager': {'name': '🏆 مدیر ارشد', 'team_bonus': 2.0},
    'partner': {'name': '👑 شریک تجاری', 'team_bonus': 2.5}
}

# جدول پورسانت
COMMISSION_TABLE = {
    'beginner': {'min': 0, 'max': 25000000, 'rate': 7, 'bonus': 2000000},
    'junior': {'min': 25000000, 'max': 50000000, 'rate': 8, 'bonus': 5000000},
    'middle': {'min': 50000000, 'max': 100000000, 'rate': 9, 'bonus': 7000000},
    'senior': {'min': 100000000, 'max': 200000000, 'rate': 10, 'bonus': 9000000},
    'expert': {'min': 200000000, 'max': 300000000, 'rate': 11, 'bonus': 12000000},
    'master': {'min': 300000000, 'max': 400000000, 'rate': 12, 'bonus': 14000000}
}

reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    full_name = update.message.from_user.full_name
    
    # ثبت کاربر در دیتابیس
    conn = sqlite3.connect('navaaran_bot.db')
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users 
                 (user_id, username, full_name, join_date, user_rank, total_sales, team_sales)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_id, username, full_name, datetime.now().strftime("%Y-%m-%d"), 'beginner', 0, 0))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(
        "🚀 **به ربات آژانس تبلیغاتی نوآوران خوش آمدید!**\n\n"
        "💎 **سیستم درآمدزایی هوشمند:**\n"
        "• پورسانت پلکانی ۷٪ تا ۱۲٪\n"
        "• پاداش‌های نقدی میلیونی\n"
        "• سیستم ارتقای شغلی پیشرفته\n\n"
        "📊 **برای مشاهده وضعیت خود از منوی زیر استفاده کنید:**",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    
    if text == '📊 پنل شخصی':
        await show_personal_panel(update, user_id)
    
    elif text == '💸 پورسانت و پاداش':
        await show_commission_table(update)
    
    elif text == '📋 خدمات ما':
        await show_services(update)
    
    elif text == '📞 ارتباط با مدیریت':
        await show_contact_info(update)
    
    else:
        await update.message.reply_text(
            "لطفاً از منوی زیر انتخاب کنید:",
            reply_markup=reply_markup
        )

async def show_personal_panel(update: Update, user_id: int):
    """نمایش پنل شخصی کاربر"""
    conn = sqlite3.connect('navaaran_bot.db')
    c = conn.cursor()
    
    # دریافت اطلاعات کاربر
    c.execute('''SELECT user_rank, total_sales, team_sales FROM users WHERE user_id=?''', (user_id,))
    user_data = c.fetchone()
    
    if not user_data:
        await update.message.reply_text("خطا در دریافت اطلاعات کاربر!")
        return
    
    user_rank, total_sales, team_sales = user_data
    
    # محاسبه پورسانت فعلی
    current_level = None
    for level, data in COMMISSION_TABLE.items():
        if total_sales >= data['min'] and total_sales < data['max']:
            current_level = data
            break
    
    if not current_level:
        current_level = COMMISSION_TABLE['master']
    
    # محاسبه درآمد
    personal_commission = (total_sales * current_level['rate']) // 100
    team_commission = (team_sales * RANKS[user_rank]['team_bonus']) // 100
    total_income = personal_commission + team_commission
    
    # ایجاد پیام پنل شخصی
    message = f"""
📊 **پنل شخصی شما**

👤 **رتبه فعلی:** {RANKS[user_rank]['name']}
💰 **فروش شخصی این ماه:** {total_sales:,} تومان
👥 **فروش تیم شما:** {team_sales:,} تومان

💸 **درآمد این ماه:**
• پورسانت شخصی ({current_level['rate']}٪): {personal_commission:,} تومان
• پاداش مدیریت تیم ({RANKS[user_rank]['team_bonus']}٪): {team_commission:,} تومان
• **جمع کل: {total_income:,} تومان**

🎯 **تا سقف بعدی:** {max(0, current_level['max'] - total_sales):,} تومان
🎁 **پاداش پیش‌رو:** {current_level['bonus']:,} تومان

💡 **نکته:** با رسیدن به سقف بعدی، پاداش نقدی فوق‌العاده دریافت می‌کنید!
"""
    
    await update.message.reply_text(message)

async def show_commission_table(update: Update):
    """نمایش جدول پورسانت و پاداش"""
    table_text = """
💰 **جدول پورسانت و پاداش نوآوران**

| سقف فروش | پورسانت | پاداش نقدی |
|----------|---------|------------|
"""
    
    for level, data in COMMISSION_TABLE.items():
        min_sales = f"{data['min']//1000000}M" if data['min'] > 0 else "شروع"
        max_sales = f"{data['max']//1000000}M" if data['max'] < 400000000 else "بالاتر"
        table_text += f"| {min_sales} - {max_sales} | {data['rate']}٪ | {data['bonus']:,} تومان |\n"
    
    table_text += "\n🎁 **پاداش در انتهای ماه و پس از رسیدن به هر سقف پرداخت می‌شود**"
    
    await update.message.reply_text(table_text)

async def show_services(update: Update):
    """نمایش خدمات آژانس"""
    services_text = """
🎨 **خدمات تخصصی آژانس نوآوران:**

📄 **طراحی و چاپ:**
• کارت ویزیت، تراکت، بروشور
• پوستر، کاتالوگ، ست اداری
• بسته‌بندی، لیبل

🏢 **هویت‌سازی برند:**
• طراحی لوگو و آرم
• راهنمای سبک برند
• برندینگ کامل

🌐 **دیجیتال مارکتینگ:**
• طراحی سایت و اپلیکیشن
• سئو و بهینه‌سازی
• کمپین‌های تبلیغاتی

📊 **مشاوره تخصصی:**
• استراتژی برندینگ
• تحلیل بازار
• مشاوره تبلیغات
"""
    await update.message.reply_text(services_text)

async def show_contact_info(update: Update):
    """نمایش اطلاعات تماس"""
    contact_text = """
📞 **ارتباط با مدیریت نوآوران**

👤 **مدیر عامل:** [نام مدیر]
📱 **موبایل:** [شماره موبایل]
📧 **ایمیل:** [آدرس ایمیل]
🏢 **آدرس:** [آدرس دفتر]

🕒 **ساعات پاسخگویی:**
شنبه تا چهارشنبه: ۹ صبح تا ۶ عصر
پنجشنبه: ۹ صبح تا ۱ ظهر

💬 **برای پیگیری فوری:**
پیام خود را در همین ربات ارسال کنید
"""
    await update.message.reply_text(contact_text)

def main():
    """تابع اصلی اجرای ربات"""
    init_db()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ ربات نوآوران در حال اجراست...")
    print("🔗 آدرس ربات: t.me/NavaaranAgencyBot")
    
    application.run_polling()

if __name__ == '__main__':

    main()

