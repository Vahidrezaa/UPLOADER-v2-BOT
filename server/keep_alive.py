import asyncio
import logging
import aiohttp
from aiohttp import web
import os

logger = logging.getLogger(__name__)

async def health_check(request):
    return web.Response(text="🤖 Bot is alive!")

async def run_web_server():
    app = web.Application()
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()

    # استفاده از PORT که Render تنظیم می‌کند
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Web server started on port {port}")

async def keep_alive_ping():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        logger.warning("RENDER_EXTERNAL_URL not set. Skipping keep-alive ping.")
        return

    health_url = f"{url}/health"
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url) as resp:
                    logger.info(f"✅ Keep-alive ping sent: {resp.status}")
        except Exception as e:
            logger.warning(f"⚠️ Keep-alive ping failed: {e}")
        await asyncio.sleep(450)
