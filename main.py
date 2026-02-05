import asyncio
import logging
import sys
import os
from aiohttp import web  # Render uchun web server
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
from database import db

load_dotenv()

# --- SOZLAMALAR ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
# Render avtomatik port beradi, agar yo'q bo'lsa 8080 ni oladi
PORT = int(os.getenv("PORT", 8080))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- STATES (Holatlar) ---
class AdminState(StatesGroup):
    waiting_code = State()
    waiting_name = State()
    waiting_photo = State()
    waiting_video = State() # Video qabul qilish holati
    waiting_delete_code = State() # O'chirish uchun kod kuting

class UserState(StatesGroup):
    searching = State()

# --- TUGMALAR (Keyboards) ---
def admin_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🎬 Anime Yuklash"), KeyboardButton(text="🗑 Kod O'chirish")],
        [KeyboardButton(text="📋 Kodlar Ro'yxati")]
    ], resize_keyboard=True)

def user_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔍 Anime Izlash")]
    ], resize_keyboard=True)

def back_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔙 Orqaga")]
    ], resize_keyboard=True)

def done_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="/done")],
        [KeyboardButton(text="🔙 Orqaga")] # Bekor qilish uchun
    ], resize_keyboard=True)

# --- WEB SERVER (Render & UptimeRobot uchun) ---
async def handle_root(request):
    return web.Response(text="Bot ishlmoqda (24/7)!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🌍 Web server {PORT} portda ishga tushdi")

# --- ADMIN HANDLERS ---

@dp.message(CommandStart())
async def start_command(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    
    if message.from_user.id == ADMIN_ID:
        await message.answer(f"Salom Admin! Xush kelibsiz.", reply_markup=admin_menu())
    else:
        await message.answer("Salom! Anime botga xush kelibsiz.", reply_markup=user_menu())

# 1. Anime yuklash bosilganda
@dp.message(F.text == "🎬 Anime Yuklash", F.from_user.id == ADMIN_ID)
async def admin_add_anime(message: types.Message, state: FSMContext):
    await message.answer("Yangi anime uchun **KOD** kiriting (masalan: 101):", reply_markup=back_menu())
    await state.set_state(AdminState.waiting_code)

@dp.message(AdminState.waiting_code)
async def process_code(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_menu())
        return

    # Kod band emasligini tekshirish kerak (ixtiyoriy, lekin foydali)
    exist = await db.get_anime(message.text)
    if exist:
        await message.answer("Bu kod allaqachon mavjud! Boshqa kod yozing:")
        return

    await state.update_data(code=message.text)
    await message.answer("Anime **NOMINI** yozing:", reply_markup=back_menu())
    await state.set_state(AdminState.waiting_name)

@dp.message(AdminState.waiting_name)
async def process_name(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_menu())
        return
        
    await state.update_data(name=message.text)
    await message.answer("Anime uchun **RASM** (Poster) yuboring:", reply_markup=back_menu())
    await state.set_state(AdminState.waiting_photo)

@dp.message(AdminState.waiting_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id # Eng sifatli rasmni olamiz
    await state.update_data(photo_id=photo_id, videos=[]) # Videolar uchun bo'sh ro'yxat ochamiz
    
    await message.answer(
        "Rasm qabul qilindi. Endi **VIDEOLARNI** (qismlarni) ketma-ket tashlang.\n"
        "Tugatgach **/done** tugmasini bosing.",
        reply_markup=done_menu()
    )
    await state.set_state(AdminState.waiting_video)

@dp.message(AdminState.waiting_video, F.video)
async def process_video_upload(message: types.Message, state: FSMContext):
    data = await state.get_data()
    videos = data.get('videos', [])
    
    # Videoning file_id sini olib ro'yxatga qo'shamiz
    videos.append(message.video.file_id)
    await state.update_data(videos=videos)
    
    await message.answer(f"✅ {len(videos)}-qism qabul qilindi. Yana tashlashingiz yoki tugatish uchun /done bosishingiz mumkin.")

@dp.message(AdminState.waiting_video, Command("done"))
@dp.message(AdminState.waiting_video, F.text == "/done")
async def finish_upload(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    code = data['code']
    name = data['name']
    photo = data['photo_id']
    videos = data['videos']
    
    if not videos:
        await message.answer("Hech qanday video yuklamadingiz! Iltimos, video tashlang.")
        return

    # Bazaga yozish
    success = await db.add_anime(code, name, photo, videos)
    
    if success:
        await message.answer(f"🎉 <b>{name}</b> muvaffaqiyatli saqlandi! Kod: {code}", parse_mode="HTML", reply_markup=admin_menu())
    else:
        await message.answer("Xatolik yuz berdi. Kod takrorlanmaganini tekshiring.", reply_markup=admin_menu())
    
    await state.clear()

# 2. Kod o'chirish
@dp.message(F.text == "🗑 Kod O'chirish", F.from_user.id == ADMIN_ID)
async def admin_delete_start(message: types.Message, state: FSMContext):
    await message.answer("O'chirmoqchi bo'lgan anime **KODINI** yozing:", reply_markup=back_menu())
    await state.set_state(AdminState.waiting_delete_code)

@dp.message(AdminState.waiting_delete_code)
async def process_delete(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_menu())
        return

    code = message.text
    result = await db.delete_anime(code)
    
    # result odatda "DELETE 1" yoki "DELETE 0" qaytaradi
    if "0" in result:
        await message.answer("❌ Bunday kod topilmadi.", reply_markup=admin_menu())
    else:
        await message.answer(f"✅ {code} kodli anime o'chirib tashlandi.", reply_markup=admin_menu())
    
    await state.clear()

# 3. Kodlar ro'yxati
@dp.message(F.text == "📋 Kodlar Ro'yxati", F.from_user.id == ADMIN_ID)
async def admin_list_animes(message: types.Message):
    animes = await db.get_all_animes()
    if not animes:
        await message.answer("Hozircha animelar yo'q.")
        return
    
    text = "📂 **Bazadagi Animelar:**\n\n"
    for anime in animes:
        text += f"🔹 Kod: `{anime['code']}` | Nom: {anime['name']}\n"
    
    await message.answer(text, parse_mode="Markdown")


# --- USER HANDLERS ---

@dp.message(F.text == "🔍 Anime Izlash")
async def user_search_start(message: types.Message, state: FSMContext):
    await message.answer("Iltimos, Anime **KODINI** yozing:", reply_markup=back_menu())
    await state.set_state(UserState.searching)

@dp.message(UserState.searching)
async def process_search(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=user_menu())
        return

    code = message.text
    anime = await db.get_anime(code)
    
    if not anime:
        await message.answer("❌ Bunday kodli anime topilmadi. Qayta urinib ko'ring yoki 'Orqaga' bosing.")
        return
    
    # Anime topildi
    caption = f"🎬 **Nomi:** {anime['name']}\n🔢 **Kod:** {anime['code']}\n\nVideolar yuborilmoqda..."
    await message.answer_photo(photo=anime['photo_id'], caption=caption, parse_mode="Markdown")
    
    # Videolarni yuborish
    video_ids = anime['file_ids'] # Bu array
    for i, vid_id in enumerate(video_ids, 1):
        await message.answer_video(video=vid_id, caption=f"{i}-qism")
        await asyncio.sleep(0.5) # Telegram bloklamasligi uchun ozgina pauza
    
    await state.clear()
    await message.answer("Tomosha qiling! 😊", reply_markup=user_menu())


# --- SYSTEM ---

async def on_startup(bot: Bot):
    await db.connect()
    await db.create_tables()
    # Web serverni alohida task qilib ishga tushiramiz
    asyncio.create_task(start_web_server())

async def on_shutdown(bot: Bot):
    await db.close()

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
