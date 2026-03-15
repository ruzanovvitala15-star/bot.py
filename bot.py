from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import asyncio

# ⚠️ замените на свой токен
API_TOKEN = "8621584119:AAEbdhtmlyxYKdni0zZA7vXawa133rb5K7A"
ADMIN_ID = 8271113983  # твой Telegram ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Список заблокированных юзеров
blocked_users = set()

# /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply(
        "Здравствуйте.\nВы можете оставить сообщение здесь, оно будет доставлено анонимно."
    )

# Получаем сообщения от пользователей
@dp.message_handler()
async def handle_user_message(message: types.Message):
    if message.from_user.id in blocked_users:
        await message.reply("Вы заблокированы, сообщение не будет доставлено.")
        return

    # Отправляем админу сообщение с кнопками
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Ответить", callback_data=f"reply:{message.from_user.id}"),
        InlineKeyboardButton("Заблокировать", callback_data=f"block:{message.from_user.id}")
    )

    await bot.send_message(
        ADMIN_ID,
        f"@{message.from_user.username or message.from_user.id} - {message.text}",
        reply_markup=keyboard
    )
    await message.reply("Ваше сообщение доставлено анонимно.")

# Обработка кнопок инлайн
@dp.callback_query_handler(lambda c: c.data.startswith(("reply:", "block:")))
async def callback_buttons(callback_query: types.CallbackQuery):
    action, user_id_str = callback_query.data.split(":")
    user_id = int(user_id_str)

    if action == "reply":
        await bot.send_message(ADMIN_ID, f"Введите ответ для {user_id}:")
        
        # Ждём следующий текст от админа
        @dp.message_handler(lambda m: m.from_user.id == ADMIN_ID)
        async def send_reply(message: types.Message):
            await bot.send_message(user_id, message.text)
            await message.reply("Ответ отправлен.")
            dp.message_handlers.unregister(send_reply)  # удаляем обработчик, чтобы не ловил все сообщения

    elif action == "block":
        blocked_users.add(user_id)
        await bot.send_message(ADMIN_ID, f"Пользователь {user_id} заблокирован.")
        await bot.send_message(user_id, "Вы заблокированы, сообщение не будет доставлено.")
    
    await callback_query.answer()  # убираем "часики" на кнопке

# Запуск
if name == "main":
    executor.start_polling(dp, skip_updates=True)
