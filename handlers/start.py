from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import add_user, is_banned, get_balance, maintenance_enabled
from config import ADMINS

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):

    user_id = message.from_user.id

    await add_user(
        user_id,
        message.from_user.username or "",
        message.from_user.full_name
    )

    if await is_banned(user_id):
        await message.answer("⛔ Вы заблокированы.")
        return

    if await maintenance_enabled() and user_id not in ADMINS:
        await message.answer("🛠 Техработы.")
        return

    balance = await get_balance(user_id)

    await message.answer(
        f"👋 Привет, <b>{message.from_user.full_name}</b>!\n"
        f"💰 Баланс: {balance} Gold"
    )
