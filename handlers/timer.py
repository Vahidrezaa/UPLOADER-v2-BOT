from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.menus import MAIN_MENU
from database.db import DB_POOL

async def toggle_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    async with DB_POOL.acquire() as conn:
        if "فعال" in text:
            await conn.execute("DELETE FROM auto_delete_settings")
            await conn.execute(
                "INSERT INTO auto_delete_settings(is_active, delete_after_seconds) VALUES(TRUE, 60)"
            )
            await update.message.reply_text("⏱ تایمر فعال شد (۶۰ ثانیه).", reply_markup=MAIN_MENU)
        else:
            await conn.execute("UPDATE auto_delete_settings SET is_active = FALSE")
            await update.message.reply_text("⏱ تایمر غیرفعال شد.", reply_markup=MAIN_MENU)

def setup_timer_handlers(app):
    app.add_handler(MessageHandler(filters.Regex("⏱ تایمر خودکار"), toggle_timer))