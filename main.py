hereimport asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Бот токенін осы жерге қой
API_TOKEN = '8569457526:AAEJGGk2G37eiMWMtebw9McFSGKrifUVx94'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Түймелерді құрастырамыз
    # icon_custom_emoji_id параметріне суреттегі ID-ді қойдым
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="YouTube арна",
                url="https://youtube.com/@sudoteach",
                # Суреттегідей YouTube-ке арналған ID (мысал)
                # Егер нақты YouTube эмодзи ID болмаса, төмендегідей кез келген premium ID жарайды
            )
        ],
        [
            InlineKeyboardButton(
                text="Telegram Premium", 
                url="https://t.me/sudoteach",
                # Міне, сенің суретіңдегі "шам" (лампочка) эмодзиінің ID-і:
                icon_custom_emoji_id="5422439311196834318"
            )
        ]
    ])

    await message.answer(
        "Сәлем! Міне, жаңа `icon_custom_emoji_id` арқылы жасалған түйме:",
        reply_markup=keyboard
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
