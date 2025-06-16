from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, ConversationHandler
from utils.menus import BACK_MENU, MAIN_MENU
from database.db import DB_POOL

UPLOAD_CATEGORY_ID, UPLOADING_FILES = range(2)
pending_uploads = {}

async def ask_category_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفاً آیدی دسته‌ای که می‌خواهید فایل به آن اضافه کنید وارد کنید:", reply_markup=BACK_MENU)
    return UPLOAD_CATEGORY_ID

async def store_category_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat_id = update.message.text.strip()
    user_id = update.effective_user.id
    async with DB_POOL.acquire() as conn:
        row = await conn.fetchrow("SELECT id FROM categories WHERE id = $1", cat_id)
        if not row:
            await update.message.reply_text("❌ این آیدی دسته معتبر نیست.")
            return UPLOAD_CATEGORY_ID
    pending_uploads[user_id] = {"category_id": cat_id, "files": []}
    await update.message.reply_text("اکنون فایل‌ها را ارسال کنید. برای پایان «/پایان» را بفرستید.")
    return UPLOADING_FILES

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pending_uploads:
        return

    msg = update.message
    file = None
    file_type = None
    file_name = None

    if msg.document:
        file = msg.document
        file_type = 'document'
        file_name = file.file_name
    elif msg.photo:
        file = msg.photo[-1]
        file_type = 'photo'
        file_name = f"photo_{file.file_id[:8]}.jpg"
    elif msg.video:
        file = msg.video
        file_type = 'video'
        file_name = f"video_{file.file_id[:8]}.mp4"
    elif msg.audio:
        file = msg.audio
        file_type = 'audio'
        file_name = f"audio_{file.file_id[:8]}.mp3"

    if not file:
        await msg.reply_text("❌ فایل پشتیبانی نمی‌شود.")
        return

    pending_uploads[user_id]['files'].append({
        'file_id': file.file_id,
        'file_type': file_type,
        'file_name': file_name,
        'file_size': file.file_size,
        'caption': msg.caption or ''
    })

    await msg.reply_text(f"✅ فایل دریافت شد. مجموع: {len(pending_uploads[user_id]['files'])}")

async def finish_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pending_uploads:
        await update.message.reply_text("هیچ آپلودی در حال انجام نیست.")
        return ConversationHandler.END

    data = pending_uploads.pop(user_id)
    category_id = data["category_id"]
    files = data["files"]

    async with DB_POOL.acquire() as conn:
        for f in files:
            try:
                await conn.execute(
                    "INSERT INTO files(category_id, file_id, file_name, file_size, file_type, caption) VALUES($1,$2,$3,$4,$5,$6)",
                    category_id, f['file_id'], f['file_name'], f['file_size'], f['file_type'], f['caption']
                )
            except Exception:
                continue

    await update.message.reply_text(f"✅ {len(files)} فایل ذخیره شد.", reply_markup=MAIN_MENU)
    return ConversationHandler.END

def setup_upload_handlers(app):
    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📤 آپلود فایل$"), ask_category_id)],
        states={
            UPLOAD_CATEGORY_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_category_id)],
            UPLOADING_FILES: [MessageHandler(
                filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO,
                handle_file
            )],
        },
        fallbacks=[MessageHandler(filters.Regex("^/پایان$"), finish_upload)]
    )
    app.add_handler(conv)
