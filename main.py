import asyncio
import logging
import os
from telegram.ext import Application
from handlers.start import setup_start_handlers
from handlers.category import setup_category_handlers
from handlers.upload import setup_upload_handlers
from handlers.admin import setup_admin_handlers
from handlers.timer import setup_timer_handlers
from database.db import init_db
from dotenv import load_dotenv
from server.keep_alive import run_web_server, keep_alive_ping

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    await init_db()

    setup_start_handlers(application)
    setup_category_handlers(application)
    setup_upload_handlers(application)
    setup_admin_handlers(application)
    setup_timer_handlers(application)

    await asyncio.gather(
        application.initialize(),
        application.start(),
        application.updater.start_polling(),
        run_web_server(),
        keep_alive_ping()
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("ربات متوقف شد.")