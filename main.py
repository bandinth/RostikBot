import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = '7944549921:AAHjpkt410iydVMyaELn3XTob0DJj3PtQUQ'  # 🔐 Заміни на свій токен

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Трекаємо на якому фото зараз кожен користувач
user_photo_index = {}

# /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Start", callback_data="start_signals")]
    ])
    await message.answer(
        "Hello 👋 This Aviator Signals BOT will give you guaranteed predicted Aviator signals with 100% chance✅ Ready to start?",
        reply_markup=keyboard
    )

# Кнопка Start (поправлений фільтр)
@dp.callback_query(lambda c: c.data == "start_signals")
async def start_signals(callback: types.CallbackQuery):
    await callback.message.answer(
        "To receive signals, you need to register an account with a promo code and top up your balance❗️ If you do not complete one of the tasks, there will be no signals for you 📌\n\n"
        "1️⃣Promo: MONEYSIGNAL22\n"
        "2️⃣Balance: 3500PKR\n\n"
        "After completing two steps, signals will be available to you ✅\n\n"
        "👇Send me your account user ID to activate signals🖇"
    )
    await callback.answer()

# Коли користувач надсилає щось → даємо "Get Signal"
@dp.message()
async def on_any_text(message: types.Message):
    user_photo_index[message.from_user.id] = 1  # починаємо з першої фотки

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Get Signal", callback_data="get_signal")]
    ])

    await message.answer(
        "Your account has been successfully connected✔️ You can start using signals right now🚀",
        reply_markup=keyboard
    )

# Кнопка Get Signal (поправлений фільтр)
@dp.callback_query(lambda c: c.data == "get_signal")
async def send_first_photo(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_photo_index[user_id] = 1  # починаємо з першого сигналу
    await send_signal_photo(callback.message, user_id)
    await callback.answer()

# Кнопка Next (поправлений фільтр)
@dp.callback_query(lambda c: c.data == "next_signal")
async def send_next_photo(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_photo_index[user_id] += 1
    await send_signal_photo(callback.message, user_id)
    await callback.answer()

# Надсилання фото + кнопка Next (якщо не останнє фото)
async def send_signal_photo(message: types.Message, user_id: int):
    index = user_photo_index.get(user_id, 1)

    if index > 13:
        await message.answer("✅ For today your signals finished!")
        return

    try:
        photo_path = f"signals/{index}.jpg"
        photo = FSInputFile(photo_path)

        # Якщо це останнє фото, не додаємо кнопку "Next"
        if index == 14:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Next", callback_data="next_signal")]
            ])

        await message.answer_photo(photo=photo, reply_markup=keyboard)

    except Exception as e:
        await message.answer(f"❌ Error loading photo {index}: {e}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
