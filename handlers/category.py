from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, ConversationHandler
from utils.menus import MAIN_MENU, BACK_MENU
from database.db import DB_POOL
import uuid

AWAITING_CATEGORY_NAME = 1

async def ask_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفاً نام دسته جدید را وارد کنید:", reply_markup=BACK_MENU)
    return AWAITING_CATEGORY_NAME

async def save_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    user_id = update.effective_user.id
    category_id = str(uuid.uuid4())[:8]

    async with DB_POOL.acquire() as conn:
        await conn.execute(
            "INSERT INTO categories(id, name, created_by) VALUES($1, $2, $3)",
            category_id, name, user_id
        )
    await update.message.reply_text(f"✅ دسته «{name}» با موفقیت ایجاد شد.", reply_markup=MAIN_MENU)
    return ConversationHandler.END

async def list_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with DB_POOL.acquire() as conn:
        rows = await conn.fetch("SELECT id, name FROM categories")
        if not rows:
            await update.message.reply_text("هیچ دسته‌ای وجود ندارد.", reply_markup=MAIN_MENU)
            return
        msg = "📂 لیست دسته‌ها:\n\n"
        for row in rows:
            msg += f"• {row['name']} (ID: {row['id']})\n"
        await update.message.reply_text(msg, reply_markup=MAIN_MENU)

def setup_category_handlers(app):
    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📁 ساخت دسته جدید$"), ask_category_name)],
        states={
            AWAITING_CATEGORY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_category)]
        },
        fallbacks=[MessageHandler(filters.Regex("↩️ بازگشت.*"), lambda u, c: list_categories(u, c))]
    )
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.Regex("^📂 نمایش دسته‌ها$"), list_categories))