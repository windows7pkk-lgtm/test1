
import asyncpg
import os
from dotenv import load_dotenv

# .env faylidagi o'zgaruvchilarni yuklaymiz
load_dotenv()

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Bazaga ulanishni hosil qiladi"""
        try:
            self.pool = await asyncpg.create_pool(
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                database=os.getenv("DB_NAME"),
                host=os.getenv("DB_HOST")
            )
            print("✅ PostgreSQL bazasiga ulanildi")
        except Exception as e:
            print(f"❌ Bazaga ulanishda xatolik: {e}")

    async def create_users_table(self):
        """Foydalanuvchilar jadvalini yaratadi"""
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            full_name VARCHAR(255),
            username VARCHAR(255),
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        async with self.pool.acquire() as connection:
            await connection.execute(sql)
            print("✅ 'users' jadvali tekshirildi/yaratildi")

    async def add_user(self, user_id: int, full_name: str, username: str):
        """Foydalanuvchini bazaga qo'shadi (agar mavjud bo'lsa, o'tkazib yuboradi)"""
        sql = """
        INSERT INTO users (id, full_name, username)
        VALUES ($1, $2, $3)
        ON CONFLICT (id) DO NOTHING;
        """
        async with self.pool.acquire() as connection:
            await connection.execute(sql, user_id, full_name, username)

    async def close(self):
        """Ulanishni yopadi"""
        if self.pool:
            await self.pool.close()
            print("🔒 Baza ulanishi yopildi")

# Boshqa fayllarda ishlatish uchun obyekt yaratib qo'yamiz
db = Database()
