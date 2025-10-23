import telebot
import sqlite3
import re
from datetime import datetime

BOT_TOKEN = "7925234053:AAGsQvx5eyVRQXf0SkhYWODOHo0m_bBbgr4"
bot = telebot.TeleBot(BOT_TOKEN)

# حالت‌های کاربر
user_states = {}

# منوی اصلی
main_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row('📋 خدمات ما', '💸 پورسانت و پاداش')
main_keyboard.row('🎯 آموزش فروش', '👥 برنامه رفرال')
main_keyboard.row('❤️ مشتریان وفادار', '⭐ نمونه کارها')
main_keyboard.row('📊 پنل شخصی', '📞 ارتباط با مدیریت')
main_keyboard.row('🚀 شروع همکاری')

# کیبورد شروع ثبت‌نام
start_cooperation_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
start_cooperation_keyboard.row('📝 ثبت‌نام بازاریاب')
start_cooperation_keyboard.row('🔙 منوی اصلی')

# کیبورد تأیید اطلاعات
confirm_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
confirm_keyboard.row('✅ تأیید و ارسال', '✏️ ویرایش اطلاعات')
confirm_keyboard.row('🔙 انصراف')

# اعتبارسنجی نام
def validate_name(name):
    if len(name) < 2:
        return "❌ نام باید حداقل ۲ حرف باشد"
    elif len(name) > 50:
        return "❌ نام نمی‌تواند بیش از ۵۰ حرف باشد"
    elif not re.match(r'^[\u0600-\u06FF\s]+$', name):
        return "❌ لطفاً فقط از حروف فارسی استفاده کنید"
    return None

# اعتبارسنجی شماره موبایل
def validate_phone(phone):
    cleaned_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    pattern = r'^(09\d{9}|9\d{9}|\+989\d{9}|00989\d{9})$'
    
    if not re.match(pattern, cleaned_phone):
        return "❌ شماره موبایل معتبر نیست. مثال: 09123456789"
    return None

# اعتبارسنجی تاریخ تولد
def validate_birth_date(date_text):
    try:
        # تبدیل تاریخ به شیء datetime
        birth_date = datetime.strptime(date_text, '%Y/%m/%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 18:
            return "❌ حداقل سن ۱۸ سال است"
        elif age > 70:
            return "❌ حداکثر سن ۷۰ سال است"
        elif birth_date > today:
            return "❌ تاریخ تولد نمی‌تواند از تاریخ امروز بیشتر باشد"
        return None
    except ValueError:
        return "❌ فرمت تاریخ اشتباه است. مثال: 1375/05/15"

# ایجاد دیتابیس
def init_db():
    conn = sqlite3.connect('navaaran_bot.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT,
                  phone TEXT, join_date TEXT, user_rank TEXT, 
                  total_sales INTEGER, team_sales INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS marketers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER, full_name TEXT, phone TEXT, 
                  city TEXT, birth_date TEXT, experience TEXT,
                  daily_time TEXT, registration_date TEXT,
                  status TEXT DEFAULT 'pending')''')
    
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    init_db()
    
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.first_name
    
    conn = sqlite3.connect('navaaran_bot.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users 
                 (user_id, username, full_name, join_date, user_rank, total_sales, team_sales)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_id, username, full_name, datetime.now().strftime("%Y-%m-%d"), "beginner", 0, 0))
    conn.commit()
    conn.close()
    
    bot.send_message(
        message.chat.id,
        "🚀 **به ربات آژانس تبلیغاتی نوآوران خوش آمدید!**\n\n"
        "💎 **فرصت درآمدزایی فوق‌العاده:**\n"
        "• پورسانت پلکانی ۷٪ تا ۱۲٪\n"
        "• پاداش‌های نقدی میلیونی\n" 
        "• آموزش رایگان فروش\n"
        "• پشتیبانی ۲۴ ساعته\n\n"
        "🎯 **برای شروع همکاری روی دکمه زیر کلیک کنید:**",
        reply_markup=main_keyboard
    )

# منوی شروع همکاری
@bot.message_handler(func=lambda message: message.text == '🚀 شروع همکاری')
def start_cooperation(message):
    bot.send_message(
        message.chat.id,
        "🎉 **فرم درخواست همکاری در بازاریابی**\n\n"
        "برای ثبت‌نام در تیم بازاریابی نوآوران، روی دکمه زیر کلیک کنید:",
        reply_markup=start_cooperation_keyboard
    )

# برگشت به منوی اصلی
@bot.message_handler(func=lambda message: message.text == '🔙 منوی اصلی')
def back_to_main(message):
    bot.send_message(message.chat.id, "منوی اصلی:", reply_markup=main_keyboard)

# شروع ثبت‌نام
@bot.message_handler(func=lambda message: message.text == '📝 ثبت‌نام بازاریاب')
def start_registration(message):
    user_id = message.from_user.id
    user_states[user_id] = {'step': 'full_name'}
    
    bot.send_message(
        message.chat.id,
        "📝 **فرم ثبت‌نام بازاریاب - مرحله ۱/۷**\n\n"
        "👤 **اطلاعات فردی**\n"
        "لطفاً نام و نام خانوادگی خود را وارد کنید:\n\n"
        "📌 **مثال:** محمد محمدی",
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )

# مدیریت مراحل ثبت‌نام با اعتبارسنجی
@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_registration(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    
    if state['step'] == 'full_name':
        error = validate_name(message.text)
        if error:
            bot.send_message(message.chat.id, error)
            return
        
        state['full_name'] = message.text
        state['step'] = 'phone'
        bot.send_message(
            message.chat.id,
            "📞 **مرحله ۲/۷**\n"
            "لطفاً شماره موبایل خود را وارد کنید:\n\n"
            "📱 **فرمت قابل قبول:**\n"
            "• 09123456789\n"
            "• 9123456789\n"
            "• +989123456789"
        )
    
    elif state['step'] == 'phone':
        error = validate_phone(message.text)
        if error:
            bot.send_message(message.chat.id, error)
            return
        
        state['phone'] = message.text
        state['step'] = 'city'
        bot.send_message(
            message.chat.id,
            "🏙️ **مرحله ۳/۷**\n"
            "لطفاً شهر و استان خود را وارد کنید:\n\n"
            "📍 **مثال:** تهران - تهران"
        )
    
    elif state['step'] == 'city':
        if len(message.text) < 2:
            bot.send_message(message.chat.id, "❌ نام شهر باید حداقل ۲ حرف باشد")
            return
        
        state['city'] = message.text
        state['step'] = 'birth_date'
        bot.send_message(
            message.chat.id,
            "🎂 **مرحله ۴/۷**\n"
            "لطفاً تاریخ تولد خود را وارد کنید:\n\n"
            "📅 **فرمت:** سال/ماه/روز\n"
            "🎁 **مثال:** 1375/05/15\n\n"
            "💡 **کاربرد:** برای ارسال هدیه تولد و برنامه‌های ویژه"
        )
    
    elif state['step'] == 'birth_date':
        error = validate_birth_date(message.text)
        if error:
            bot.send_message(message.chat.id, error)
            return
        
        state['birth_date'] = message.text
        state['step'] = 'experience'
        
        experience_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        experience_keyboard.row('بدون سابقه', 'کمتر از ۱ سال')
        experience_keyboard.row('۱-۳ سال', '۳-۵ سال')
        experience_keyboard.row('بالای ۵ سال')
        
        bot.send_message(
            message.chat.id,
            "💼 **مرحله ۵/۷**\n"
            "سابقه فعالیت در زمینه بازاریابی یا فروش:",
            reply_markup=experience_keyboard
        )
    
    elif state['step'] == 'experience':
        valid_experience = ['بدون سابقه', 'کمتر از ۱ سال', '۱-۳ سال', '۳-۵ سال', 'بالای ۵ سال']
        if message.text not in valid_experience:
            bot.send_message(message.chat.id, "❌ لطفاً یکی از گزینه‌های بالا را انتخاب کنید")
            return
        
        state['experience'] = message.text
        state['step'] = 'daily_time'
        
        time_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        time_keyboard.row('کمتر از ۲ ساعت', '۲-۴ ساعت')
        time_keyboard.row('۴-۶ ساعت', 'بیش از ۶ ساعت')
        
        bot.send_message(
            message.chat.id,
            "⏰ **مرحله ６/７**\n"
            "میانگین زمانی که می‌توانید روزانه اختصاص دهید:",
            reply_markup=time_keyboard
        )
    
    elif state['step'] == 'daily_time':
        valid_times = ['کمتر از ۲ ساعت', '۲-۴ ساعت', '۴-۶ ساعت', 'بیش از ۶ ساعت']
        if message.text not in valid_times:
            bot.send_message(message.chat.id, "❌ لطفاً یکی از گزینه‌های بالا را انتخاب کنید")
            return
        
        state['daily_time'] = message.text
        state['step'] = 'confirm'
        
        # محاسبه سن از روی تاریخ تولد
        birth_date = datetime.strptime(state['birth_date'], '%Y/%m/%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        summary = f"""
📋 **خلاصه اطلاعات ثبت‌نامی:**

👤 **اطلاعات فردی:**
• نام و نام خانوادگی: {state['full_name']}
• شماره تماس: {state['phone']}
• شهر و استان: {state['city']}
• تاریخ تولد: {state['birth_date']}
• سن: {age} سال

💼 **سوابق کاری:**
• سابقه فعالیت: {state['experience']}
• زمان روزانه: {state['daily_time']}

✅ لطفاً اطلاعات فوق را بررسی و تأیید کنید:
        """
        
        bot.send_message(
            message.chat.id,
            summary,
            reply_markup=confirm_keyboard
        )
    
    elif state['step'] == 'confirm':
        if message.text == '✅ تأیید و ارسال':
            conn = sqlite3.connect('navaaran_bot.db', check_same_thread=False)
            c = conn.cursor()
            c.execute('''INSERT INTO marketers 
                         (user_id, full_name, phone, city, birth_date, experience, daily_time, registration_date)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, state['full_name'], state['phone'], state['city'], 
                       state['birth_date'], state['experience'], state['daily_time'],
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            
            bot.send_message(
                message.chat.id,
                "🎉 **ثبت‌نام شما با موفقیت انجام شد!**\n\n"
                "✅ اطلاعات شما برای تیم مدیریت ارسال شد.\n"
                "📞 به زودی با شما تماس گرفته خواهد شد.\n"
                "🎁 **ویژه:** در تاریخ تولدتان هدیه ویژه دریافت خواهید کرد!\n\n"
                "با تشکر از اعتماد شما به نوآوران!",
                reply_markup=main_keyboard
            )
            
            del user_states[user_id]
            
        elif message.text == '✏️ ویرایش اطلاعات':
            user_states[user_id] = {'step': 'full_name'}
            bot.send_message(
                message.chat.id,
                "✏️ **ویرایش اطلاعات**\n\n"
                "لطفاً نام و نام خانوادگی خود را مجدداً وارد کنید:\n\n"
                "📌 **مثال:** محمد محمدی",
                reply_markup=telebot.types.ReplyKeyboardRemove()
            )
        
        elif message.text == '🔙 انصراف':
            del user_states[user_id]
            bot.send_message(
                message.chat.id,
                "❌ **ثبت‌نام لغو شد.**\n\n"
                "هر زمان که آماده بودید می‌توانید مجدداً ثبت‌نام کنید.",
                reply_markup=main_keyboard
            )

# 📋 خدمات ما
@bot.message_handler(func=lambda message: message.text == '📋 خدمات ما')
def services_menu(message):
    response = """🎨 **خدمات تخصصی آژانس تبلیغاتی نوآوران:**

🤖 **طراحی ربات تلگرام:**
• ربات‌های بازاریابی و فروش (مشابه همین ربات)
• ربات‌های پشتیبانی خودکار
• ربات‌های آموزشی و اطلاع‌رسانی
• ربات‌های سفارش‌گیری و خدمات

📄 **طراحی و چاپ حرفه‌ای:**
• کارت ویزیت • تراکت • بروشور
• پوستر • کاتالوگ • ست اداری
• بسته‌بندی • لیبل و استیکر

🏢 **هویت‌سازی برند (برندینگ):**
• طراحی لوگو و آرم تجاری
• راهنمای سبک برند
• طراحی ست اداری یکپارچه
• برندینگ کامل کسب‌وکار

🌐 **حلول دیجیتال:**
• طراحی سایت شرکتی و فروشگاهی
• سئو و بهینه‌سازی موتورهای جستجو
• طراحی اپلیکیشن موبایل
• کمپین‌های تبلیغاتی دیجیتال

📊 **مشاوره استراتژیک:**
• مشاوره برندینگ و positioning
• استراتژی مارکتینگ
• تحلیل بازار و رقبا
• مشاوره کمپین‌های تبلیغاتی

💎 **نمونه کار زنده:**
این ربات که هم اکنون در حال استفاده از آن هستید،
یکی از محصولات تیم فنی نوآوران است!"""
    bot.send_message(message.chat.id, response)

# 💸 پورسانت و پاداش
@bot.message_handler(func=lambda message: message.text == '💸 پورسانت و پاداش')
def commission_menu(message):
    response = """💰 **سیستم درآمدزایی هوشمند نوآوران**

🏆 **جدول پورسانت پلکانی پیشرفته:**

| رتبه | سقف فروش ماهیانه | پورسانت | پاداش نقدی |
|------|------------------|---------|------------|
| 🥉 تازه‌کار | تا ۲۵ میلیون | ۷٪ | ۲ میلیون تومان |
| 🥈 فعال | ۲۵ تا ۵۰ میلیون | ۸٪ | ۵ میلیون تومان |
| 🥇 پیشرفته | ۵۰ تا ۱۰۰ میلیون | ۹٪ | ۷ میلیون تومان |
| 💎 حرفه‌ای | ۱۰۰ تا ۲۰۰ میلیون | ۱۰٪ | ۹ میلیون تومان |
| 🏆 ستاره | ۲۰۰ تا ۴۰۰ میلیون | ۱۱٪ | ۱۲ میلیون تومان |
| 👑 الماسی | بالای ۴۰۰ میلیون | ۱۲٪ | ۲۰ میلیون تومان |

💡 **مثال محاسبه درآمد:**
فروش ۸۰ میلیون در ماه:
• پورسانت: ۸۰M × ۹٪ = ۷,۲۰۰,۰۰۰ تومان
• پاداش سطح: ۷,۰۰۰,۰۰۰ تومان
• **💰 درآمد کل: ۱۴,۲۰۰,۰۰۰ تومان**"""
    bot.send_message(message.chat.id, response)

# 📊 پنل شخصی
@bot.message_handler(func=lambda message: message.text == '📊 پنل شخصی')
def personal_panel(message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect('navaaran_bot.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''SELECT user_rank, total_sales FROM users WHERE user_id=?''', (user_id,))
    user_data = c.fetchone()
    conn.close()
    
    if user_data:
        user_rank, total_sales = user_data
        rank_name = "تازه‌کار" if user_rank == "beginner" else user_rank
    else:
        rank_name, total_sales = "تازه‌کار", 0
    
    response = f"""📊 **پنل شخصی شما**

👤 **اطلاعات فردی:**
• نام: {message.from_user.first_name}
• رتبه: {rank_name}
• تاریخ عضویت: {datetime.now().strftime("%Y-%m-%d")}

💰 **عملکرد مالی:**
• فروش این ماه: {total_sales:,} تومان
• پورسانت فعلی: ۷٪ - ۱۲٪ (پلکانی)
• درآمد فعلی: {int(total_sales * 0.07):,} تومان

🎯 **اهداف پیش رو:**
• برای شروع، اولین فروش خود را ثبت کنید!
• با اولین فروش، به سیستم پاداش دسترسی پیدا می‌کنید"""
    bot.send_message(message.chat.id, response)

# 🎯 آموزش فروش
@bot.message_handler(func=lambda message: message.text == '🎯 آموزش فروش')
def training_menu(message):
    response = """🎓 **آکادمی فروش نوآوران**

📚 **دوره‌های آموزشی رایگان:**

۱. **اصول بازاریابی حرفه‌ای:**
   • شناسایی مشتریان بالقوه
   • تکنیک‌های برقراری ارتباط
   • اصول مذاکره و متقاعدسازی

۲. **تکنیک‌های فروش خدمات:**
   • ارائه مؤثر خدمات نوآوران
   • پاسخ به اعتراضات مشتریان
   • تکنیک‌های بستن فروش

۳. **مدیریت مشتری:**
   • پیگیری مؤثر مشتریان
   • ساخت رابطه بلندمدت
   • دریافت معرفی از مشتریان راضی

💡 **نکته طلایی:** بهترین آموزش، عمل کردن است!"""
    bot.send_message(message.chat.id, response)

# 👥 برنامه رفرال
@bot.message_handler(func=lambda message: message.text == '👥 برنامه رفرال')
def referral_menu(message):
    response = """🤝 **برنامه معرفی نوآوران**

💰 **درآمد از طریق معرفی:**

👥 **معرفی بازاریاب:**
• پاداش سطح اول: ۱۰۰,۰۰۰ تومان به ازای هر بازاریاب جدید
• پاداش سطح دوم: ۵۰,۰۰۰ تومان از فروش بازاریاب‌های معرفی‌شده

👨‍💼 **معرفی مشتری:**
• به ازای هر معرفی موفق: ۱۰٪ تخفیف در سفارش بعدی
• مشتری معرفی شده: ۵٪ تخفیف در اولین سفارش

📋 **نحوه ثبت معرفی:**
۱. نام و شماره فرد را برای مدیریت ارسال کنید
۲. ما پیگیری و هماهنگی را انجام می‌دهیم
۳. پس از اولین فروش، پاداش شما پرداخت می‌شود"""
    bot.send_message(message.chat.id, response)

# ❤️ مشتریان وفادار
@bot.message_handler(func=lambda message: message.text == '❤️ مشتریان وفادار')
def loyalty_menu(message):
    response = """💎 **باشگاه مشتریان وفادار نوآوران**

🏅 **سطح‌های باشگاه مشتریان:**

🟢 **مشتری نقره‌ای (۳ سفارش موفق):**
• ۵٪ تخفیف دائمی روی تمام خدمات
• اولویت در اجرای پروژه‌ها
• پشتیبانی ویژه

🟡 **مشتری طلایی (۵ سفارش موفق):**
• ۱۰٪ تخفیف دائمی روی تمام خدمات
• طراحی ۱ کارت ویزیت رایگان در سال
• مشاوره رایگان برندینگ (۱ جلسه)

🔴 **مشتری الماسی (۱۰+ سفارش):**
• ۱۵٪ تخفیف دائمی
• طراحی لوگو رایگان برای کسب‌وکار جدید
• پشتیبانی اختصاصی VIP"""
    bot.send_message(message.chat.id, response)

# ⭐ نمونه کارها
@bot.message_handler(func=lambda message: message.text == '⭐ نمونه کارها')
def portfolio_menu(message):
    response = """🏆 **گالری پروژه‌های موفق نوآوران**

🤖 **ربات‌های تلگرام طراحی شده:**
• ✅ **ربات بازاریابی نوآوران** (همین ربات)
• ✅ **ربات فروشگاهی** - ثبت سفارش و پیگیری
• ✅ **ربات پشتیبانی** - پاسخگویی خودکار

🎨 **طراحی لوگو و هویت بصری:**
• ✅ **لوگو رستوران "طعم بهشت"**
• ✅ **لوگو کافی‌شاپ "دلنواز"**  
• ✅ **لوگو کلینیک "دکتر زیبا"**

📄 **طراحی و چاپ کارت ویزیت:**
• ✅ **کارت ویزیت دندانپزشکی**
• ✅ **کارت ویزیت رستوران**
• ✅ **کارت ویزیت شرکتی**

🌐 **طراحی سایت (به زودی):**
• 🚧 **سایت فروشگاهی "عطرستان"**
• 🚧 **سایت شرکتی "گروه کارن"**"""
    bot.send_message(message.chat.id, response)

# 📞 ارتباط با مدیریت
@bot.message_handler(func=lambda message: message.text == '📞 ارتباط با مدیریت')
def contact_menu(message):
    response = """📞 **اطلاعات تماس با مدیریت نوآوران**

👤 **مدیر عامل:** [نام مدیر]
📱 **موبایل:** [شماره موبایل] 
📧 **ایمیل:** [آدرس ایمیل]

🕒 **ساعات پاسخگویی:**
• شنبه تا چهارشنبه: ۹ صبح تا ۶ عصر
• پنجشنبه: ۹ صبح تا ۱ ظهر

💬 **روش‌های ارتباطی:**
۱. پیام مستقیم در این ربات
۲. تماس تلفنی
۳. واتساپ

🤝 **آماده همکاری با شما هستیم!**"""
    bot.send_message(message.chat.id, response)

print("=" * 60)
print("✅ ربات نوآوران با سیستم تاریخ تولد اجرا شد!")
print("🎁 قابلیت هدیه تولد اضافه شد")
print("🛡️ اعتبارسنجی کامل تاریخ تولد")
print("🤖 ربات در حال دریافت پیام...")
print("=" * 60)

bot.infinity_polling()
