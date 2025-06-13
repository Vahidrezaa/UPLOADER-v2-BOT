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
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()
    logger.info("🌐 Web server started on port 10000")

async def keep_alive_ping():
    url = os.getenv("RENDER_EXTERNAL_URL") or "https://your-app-name.onrender.com"
    health_url = f"{url}/health"
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url) as resp:
                    logger.info(f"✅ Keep-alive ping sent: {resp.status}")
        except Exception as e:
            logger.warning(f"⚠️ Keep-alive ping failed: {e}")
        await asyncio.sleep(300)