import asyncpg
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DB_POOL = None

async def init_db():
    global DB_POOL
    if DB_POOL:
        return DB_POOL

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise Exception("DATABASE_URL is not set in environment")

    DB_POOL = await asyncpg.create_pool(dsn=db_url)
    logger.info("✅ Database connected")

    async with DB_POOL.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                created_by BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS files (
                category_id TEXT REFERENCES categories(id) ON DELETE CASCADE,
                file_id TEXT,
                file_name TEXT,
                file_size BIGINT,
                file_type TEXT,
                caption TEXT,
                UNIQUE(category_id, file_id)
            );
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                user_id BIGINT PRIMARY KEY,
                is_super BOOLEAN NOT NULL DEFAULT FALSE,
                added_by BIGINT,
                added_at TIMESTAMP DEFAULT NOW()
            );
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT PRIMARY KEY,
                channel_name TEXT,
                invite_link TEXT
            );
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS auto_delete_settings (
                id SERIAL PRIMARY KEY,
                is_active BOOLEAN DEFAULT FALSE,
                delete_after_seconds INTEGER,
                post_delete_message TEXT DEFAULT '⏰ زمان مشاهده فایل به پایان رسید!'
            );
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS static_messages (
                category_id TEXT PRIMARY KEY REFERENCES categories(id) ON DELETE CASCADE,
                file_id TEXT,
                caption TEXT
            );
        ''')

        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_files_category ON files(category_id);
        ''')

    logger.info("✅ Database schema initialized")
    return DB_POOL