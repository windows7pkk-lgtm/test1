import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

# Database faylidan 'db' obyektini chaqiramiz
from database import db

# .env yuklash
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

# --- HANDLERLAR ---

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    user = message.from_user
    
    # Foydalanuvchini bazaga qo'shish
    await db.add_user(user.id, user.full_name, user.username)
    
    await message.answer(f"Salom, {user.full_name}! 👋\nSiz muvaffaqiyatli ro'yxatdan o'tdingiz.")

# --- STARTUP & SHUTDOWN ---

async def on_startup(bot: Bot):
    """Bot ishga tushganda bajariladigan ishlar"""
    await db.connect()             # Bazaga ulanish
    await db.create_users_table()  # Jadvallarni yaratish

async def on_shutdown(bot: Bot):
    """Bot to'xtaganda bajariladigan ishlar"""
    await db.close()

# --- MAIN ---

async def main():
    bot = Bot(token=TOKEN)
    
    # Startup va Shutdown funksiyalarini ro'yxatdan o'tkazamiz
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("Bot ishga tushirilmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi!")
