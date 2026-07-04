from aiogram import Router
from aiogram.types import Message

from database import add_user, is_banned, maintenance_enabled, get_balance
from config import ADMINS

router = Router()


@router.message()
async def start_handler(message: Message):

    user_id = message.from_user.id

    # регистрация пользователя
    await add_user(
        user_id,
        message.from_user.username or "",
        message.from_user.full_name
    )

    # бан
    if await is_banned(user_id):
        await message.answer("⛔ Вы заблокированы.")
        return

    # техработы
    if await maintenance_enabled() and user_id not in ADMINS:
        await message.answer("🛠 Бот на техобслуживании.")
        return

    # баланс
    balance = await get_balance(user_id)

    await message.answer(
        f"👋 Привет, <b>{message.from_user.full_name}</b>!\n"
        f"💰 Баланс: {balance} Gold"
    )
