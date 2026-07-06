from aiogram import Router, F
from aiogram.types import Message

from config import ADMINS
from database import create_promo, delete_promo, get_promos

router = Router()


def is_admin(user_id: int):
    return user_id in ADMINS


# =========================
# СОЗДАТЬ ПРОМОКОД
# /createpromo CODE REWARD LIMIT
# =========================
@router.message(F.text.startswith("/createpromo"))
async def create_promo_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    try:
        _, code, reward, limit = message.text.split()

        await create_promo(
            code=code.upper(),
            reward=float(reward),
            max_uses=int(limit)
        )

        await message.answer(
            f"✅ Промокод создан:\n"
            f"🔑 {code.upper()}\n"
            f"💰 {reward}\n"
            f"👥 {limit}"
        )

    except:
        await message.answer("❌ /createpromo CODE REWARD LIMIT")


# =========================
# УДАЛИТЬ
# =========================
@router.message(F.text.startswith("/delpromo"))
async def del_promo(message: Message):

    if not is_admin(message.from_user.id):
        return

    try:
        _, code = message.text.split()

        await delete_promo(code.upper())

        await message.answer(f"🗑 Удалён {code}")

    except:
        await message.answer("❌ /delpromo CODE")


# =========================
# СПИСОК
# =========================
@router.message(F.text == "/promos")
async def list_promos(message: Message):

    if not is_admin(message.from_user.id):
        return

    promos = await get_promos()

    if not promos:
        return await message.answer("Нет промокодов")

    text = "📋 Промокоды:\n\n"

    for p in promos:
        text += f"{p['code']} | {p['uses']}/{p['max_uses']}\n"

    await message.answer(text)
