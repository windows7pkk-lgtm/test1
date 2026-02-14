import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Бот токенін осы жерге қой
API_TOKEN = '8233524201:AAF6DaNXGQBFRa3SlhqcC1iH0nc1qrCbAUI'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Сенің ID-ің (шам эмодзиі)
EMOJI_ID = "5422439311196834318"

# 1. /start басқанда тек ЭМОДЗИ жібереді
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # <tg-emoji> тегін қолданамыз. parse_mode="HTML" болуы МІНДЕТТІ.
    # Ортасындағы "💡" белгісі - егер premium көрінбесе шығатын қарапайым смайлик.
    await message.answer(
        f'<tg-emoji emoji-id="{EMOJI_ID}">💡</tg-emoji>', 
        parse_mode="HTML"
    )

# 2. /emoji басқанда МӘТІН + ЭМОДЗИ жібереді
@dp.message(Command("emoji"))
async def cmd_emoji(message: types.Message):
    await message.answer(
        f'Сәлем, міне emoji <tg-emoji emoji-id="{EMOJI_ID}">💡</tg-emoji>', 
        parse_mode="HTML"
    )

async def main():
    # Ескі қателерді жою үшін (Conflict болмау үшін)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
