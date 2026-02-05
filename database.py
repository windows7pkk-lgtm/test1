import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                database=os.getenv("DB_NAME"),
                host=os.getenv("DB_HOST"),
                port=5432 
            )
            print("✅ Baza ulandi")
        except Exception as e:
            print(f"❌ Baza xatosi: {e}")

    async def create_tables(self):
        # Users jadvali
        users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            full_name VARCHAR(255),
            username VARCHAR(255),
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        # Animes jadvali (Code, Name, Photo, Videos[])
        animes_sql = """
        CREATE TABLE IF NOT EXISTS animes (
            code VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255),
            photo_id VARCHAR(255),
            file_ids TEXT[] 
        );
        """
        async with self.pool.acquire() as connection:
            await connection.execute(users_sql)
            await connection.execute(animes_sql)
            print("✅ Jadvallar tayyor")

    async def add_user(self, user_id, full_name, username):
        sql = "INSERT INTO users (id, full_name, username) VALUES ($1, $2, $3) ON CONFLICT (id) DO NOTHING"
        async with self.pool.acquire() as conn:
            await conn.execute(sql, user_id, full_name, username)

    # --- ANIME FUNKSIYALARI ---

    async def add_anime(self, code, name, photo_id, file_ids):
        """Animeni bazaga saqlash"""
        sql = "INSERT INTO animes (code, name, photo_id, file_ids) VALUES ($1, $2, $3, $4)"
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(sql, code, name, photo_id, file_ids)
                return True
            except asyncpg.UniqueViolationError:
                return False

    async def get_anime(self, code):
        """Kod bo'yicha anime olish"""
        sql = "SELECT * FROM animes WHERE code = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, code)

    async def delete_anime(self, code):
        """Animeni o'chirish"""
        sql = "DELETE FROM animes WHERE code = $1"
        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, code)
            return result # "DELETE 1" kabi javob qaytadi

    async def get_all_animes(self):
        """Barcha kodlarni olish (Admin uchun)"""
        sql = "SELECT code, name FROM animes ORDER BY code"
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql)

    async def close(self):
        if self.pool:
            await self.pool.close()

db = Database()
