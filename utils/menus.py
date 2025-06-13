from telegram import ReplyKeyboardMarkup

MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["📁 ساخت دسته جدید", "📂 نمایش دسته‌ها"],
        ["📤 آپلود فایل", "⏱ تایمر خودکار"],
        ["🔗 تنظیم کانال اجباری", "👤 مدیریت ادمین‌ها"]
    ],
    resize_keyboard=True,
    input_field_placeholder="لطفا یک گزینه را انتخاب کنید"
)

BACK_MENU = ReplyKeyboardMarkup(
    [["↩️ بازگشت به منوی اصلی"]],
    resize_keyboard=True
)