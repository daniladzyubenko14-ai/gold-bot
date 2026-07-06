from aiogram import Router, F
from aiogram.types import Message

from config import ADMINS
from database import create_promo, delete_promo

router = Router()


def is_admin(user_id: int):
    return user_id in ADMINS


@router.message(F.text.startswith("/createpromo"))
async def createpromo(message: Message):

    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    parts = message.text.split()

    if len(parts) != 4:
        return await message.answer("❌ /createpromo CODE REWARD LIMIT")

    _, code, reward, limit = parts

    await create_promo(code, float(reward), int(limit))

    await message.answer(f"✅ Промокод создан: {code}")


@router.message(F.text.startswith("/delpromo"))
async def delpromo(message: Message):

    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    parts = message.text.split()

    if len(parts) != 2:
        return await message.answer("❌ /delpromo CODE")

    _, code = parts

    await delete_promo(code)

    await message.answer(f"🗑 Удалён: {code}")
