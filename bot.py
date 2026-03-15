import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio

load_dotenv()
API_TOKEN = os.getenv("8621584119:AAEbdhtmlyxYKdni0zZA7vXawa133rb5K7A")
ADMIN_ID = int(os.getenv("8271113983"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

blocked_users = set()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply(
        "Здравствуйте.\nВы можете оставить сообщение здесь, оно будет доставлено анонимно."
    )

@dp.message()
async def handle_user_message(message: types.Message):
    if message.from_user.id in blocked_users:
        await message.reply("Вы заблокированы, сообщение не будет доставлено.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Ответить", callback_data=f"reply:{message.from_user.id}"),
            InlineKeyboardButton(text="Заблокировать", callback_data=f"block:{message.from_user.id}")
        ]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"@{message.from_user.username or message.from_user.id} - {message.text}",
        reply_markup=keyboard
    )
    await message.reply("Ваше сообщение доставлено анонимно.")

@dp.callback_query()
async def callback_buttons(callback_query: types.CallbackQuery):
    action, user_id_str = callback_query.data.split(":")
    user_id = int(user_id_str)

    if action == "reply":
        await bot.send_message(ADMIN_ID, f"Введите ответ для {user_id}:")
    elif action == "block":
        blocked_users.add(user_id)
        await bot.send_message(ADMIN_ID, f"Пользователь {user_id} заблокирован.")
        await bot.send_message(user_id, "Вы заблокированы.")
    
    await callback_query.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
