import asyncpg
import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            # 1. Renderda odatda DATABASE_URL bo'ladi, shuni tekshiramiz
            db_url = os.getenv("DATABASE_URL")
            
            if db_url:
                # URL orqali ulanish (Render uchun)
                self.pool = await asyncpg.create_pool(db_url)
            else:
                # Agar URL bo'lmasa, alohida parametrlar bilan ulanish (Local uchun)
                self.pool = await asyncpg.create_pool(
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASS"),
                    database=os.getenv("DB_NAME"),
                    host=os.getenv("DB_HOST"),
                    port=5432
                )
            print("✅ Baza ulandi")
            return True
        except Exception as e:
            # Xatolikni to'liq chop etamiz
            print(f"❌ Baza xatosi (Ulanishda): {e}")
            logging.error(f"DB Connection Error: {e}")
            return False

    async def create_tables(self):
        # Agar pool bo'lmasa (ulanish o'xshamasligi), to'xtaymiz
        if not self.pool:
            print("⚠️ Baza ulanmagan, jadvallar yaratilmaydi!")
            return

        users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            full_name VARCHAR(255),
            username VARCHAR(255),
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        animes_sql = """
        CREATE TABLE IF NOT EXISTS animes (
            code VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255),
            photo_id VARCHAR(255),
            file_ids TEXT[] 
        );
        """
        try:
            async with self.pool.acquire() as connection:
                await connection.execute(users_sql)
                await connection.execute(animes_sql)
                print("✅ Jadvallar tayyor")
        except Exception as e:
            print(f"❌ Jadval yaratishda xatolik: {e}")

    async def add_user(self, user_id, full_name, username):
        if not self.pool: return
        sql = "INSERT INTO users (id, full_name, username) VALUES ($1, $2, $3) ON CONFLICT (id) DO NOTHING"
        async with self.pool.acquire() as conn:
            await conn.execute(sql, user_id, full_name, username)

    async def add_anime(self, code, name, photo_id, file_ids):
        if not self.pool: return False
        sql = "INSERT INTO animes (code, name, photo_id, file_ids) VALUES ($1, $2, $3, $4)"
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(sql, code, name, photo_id, file_ids)
                return True
            except asyncpg.UniqueViolationError:
                return False

    async def get_anime(self, code):
        if not self.pool: return None
        sql = "SELECT * FROM animes WHERE code = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, code)

    async def delete_anime(self, code):
        if not self.pool: return "Error"
        sql = "DELETE FROM animes WHERE code = $1"
        async with self.pool.acquire() as conn:
            return await conn.execute(sql, code)

    async def get_all_animes(self):
        if not self.pool: return []
        sql = "SELECT code, name FROM animes ORDER BY code"
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql)

    async def close(self):
        if self.pool:
            await self.pool.close()

db = Database()
