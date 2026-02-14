import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ⚠️ Бот токенін осы жерге қой (тырнақшаның ішіне)
API_TOKEN = '8233524201:AAHPPxWyYI8XSzznBJatW2ymfYkJmBreIU4'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Сен берген жаңа ID
EMOJI_ID = "5199785165735367039"

# 1. /start басқанда -> Тек қана Premium Emoji жібереді
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # <tg-emoji> тегі HTML режимінде жұмыс істейді.
    # Ортасындағы "✅" белгісі — егер premium жүктелмесе көрінетін жай смайлик.
    await message.answer(
        f'<tg-emoji emoji-id="{EMOJI_ID}">✅</tg-emoji>', 
        parse_mode="HTML"
    )

# 2. /emoji басқанда -> Мәтін + Premium Emoji жібереді
@dp.message(Command("emoji"))
async def cmd_emoji(message: types.Message):
    await message.answer(
        f'Сәлем, міне emoji <tg-emoji emoji-id="{EMOJI_ID}">✅</tg-emoji>', 
        parse_mode="HTML"
    )

async def main():
    # Ескі "Conflict" қатесін болдырмау үшін сессияны тазалаймыз
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
