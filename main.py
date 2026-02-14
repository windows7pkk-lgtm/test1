import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# -----------------------------------------------------------
# ⚠️ ОСЫ ЖЕРГЕ ЖАҢА ТОКЕНДІ ҚОЮ КЕРЕК!
# Ескі (8233...) токен енді жұмыс істемейді.
# -----------------------------------------------------------
API_TOKEN = '8535472292:AAEU19Fnw1VAKtaIzu4Cea9s5vsI7jvBqQw'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Эмодзи ID
EMOJI_ID = "5199785165735367039"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f'<tg-emoji emoji-id="{EMOJI_ID}">✅</tg-emoji>', 
        parse_mode="HTML"
    )

@dp.message(Command("emoji"))
async def cmd_emoji(message: types.Message):
    await message.answer(
        f'Сәлем, міне emoji <tg-emoji emoji-id="{EMOJI_ID}">✅</tg-emoji>', 
        parse_mode="HTML"
    )

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
