from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.menus import MAIN_MENU
from database.db import DB_POOL

async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"سلام {user.first_name}!\nبه پنل مدیریت خوش آمدید.", reply_markup=MAIN_MENU)

    async with DB_POOL.acquire() as conn:
        await conn.execute('''
            INSERT INTO admins(user_id, is_super)
            VALUES($1, TRUE)
            ON CONFLICT (user_id) DO NOTHING;
        ''', user.id)

def setup_start_handlers(app):
    app.add_handler(MessageHandler(filters.Regex("^(/start|↩️ بازگشت به منوی اصلی)$"), start_message))