import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
import os

API_TOKEN = os.getenv("7944549921:AAHjpkt410iydVMyaELn3XTob0DJj3PtQUQ")  # Безпечніше
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Посилання від Render

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

user_photo_index = {}

@dp.message(F.text.startswith("/start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Start", callback_data="start_signals")]
    ])
    await message.answer(
        "Hello 👋 This Aviator Signals BOT will give you guaranteed predicted Aviator signals with 100% chance✅ Ready to start?",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "start_signals")
async def start_signals(callback: types.CallbackQuery):
    await callback.message.answer(
        "To receive signals, you need to register an account with a promo code and top up your balance❗️\n\n"
        "1️⃣Promo: MONEYSIGNAL22\n2️⃣Balance: 3500PKR\n\n"
        "After completing two steps, signals will be available to you ✅\n\n"
        "👇Send me your account user ID to activate signals🖇"
    )
    await callback.answer()

@dp.message(F.text)
async def on_any_text(message: types.Message):
    user_photo_index[message.from_user.id] = 1
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Get Signal", callback_data="get_signal")]
    ])
    await message.answer("Your account has been successfully connected✔️ You can start using signals right now🚀", reply_markup=keyboard)

@dp.callback_query(F.data == "get_signal")
async def send_first_photo(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_photo_index[user_id] = 1
    await send_signal_photo(callback.message, user_id)

@dp.callback_query(F.data == "next_signal")
async def send_next_photo(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_photo_index[user_id] += 1
    await send_signal_photo(callback.message, user_id)

async def send_signal_photo(message: types.Message, user_id: int):
    index = user_photo_index.get(user_id, 1)
    if index > 14:
        await message.answer("✅ You've received all 14 signals!")
        return

    try:
        photo_path = f"signals/{index}.jpg"
        photo = FSInputFile(photo_path)
        buttons = []

        if index < 14:
            buttons.append([InlineKeyboardButton(text="Next", callback_data="next_signal")])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer_photo(photo=photo, reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"❌ Error loading photo {index}: {e}")

# --- Webhook server ---
async def handle(request):
    body = await request.read()
    await dp.feed_webhook_update(bot, request)
    return web.Response()

async def main():
    await bot.set_webhook(WEBHOOK_URL)
    app = web.Application()
    app.router.add_post("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()
    print("Bot is running via webhook...")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
