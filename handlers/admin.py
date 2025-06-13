from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, ConversationHandler
from utils.menus import MAIN_MENU
from database.db import DB_POOL

ADMIN_ID_STEP, REMOVE_ID_STEP = range(2)

async def ask_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("آیدی عددی کاربر را وارد کنید:")
    return ADMIN_ID_STEP

async def save_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(update.message.text.strip())
    except:
        await update.message.reply_text("فرمت آیدی نادرست است.")
        return ADMIN_ID_STEP

    async with DB_POOL.acquire() as conn:
        await conn.execute(
            "INSERT INTO admins(user_id, is_super, added_by) VALUES($1, FALSE, $2) ON CONFLICT DO NOTHING",
            user_id, update.effective_user.id
        )
    await update.message.reply_text("✅ ادمین با موفقیت افزوده شد.", reply_markup=MAIN_MENU)
    return ConversationHandler.END

async def ask_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("آیدی عددی ادمینی که می‌خواهید حذف کنید را وارد کنید:")
    return REMOVE_ID_STEP

async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(update.message.text.strip())
    except:
        await update.message.reply_text("فرمت آیدی نادرست است.")
        return REMOVE_ID_STEP

    async with DB_POOL.acquire() as conn:
        await conn.execute(
            "DELETE FROM admins WHERE user_id = $1 AND is_super = FALSE",
            user_id
        )
    await update.message.reply_text("✅ ادمین حذف شد.", reply_markup=MAIN_MENU)
    return ConversationHandler.END

def setup_admin_handlers(app):
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^👤 مدیریت ادمین‌ها$"), ask_add_admin)],
        states={
            ADMIN_ID_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_admin)]
        },
        fallbacks=[]
    ))
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔗 تنظیم کانال اجباری$"), ask_remove_admin)],
        states={
            REMOVE_ID_STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_admin)]
        },
        fallbacks=[]
    ))