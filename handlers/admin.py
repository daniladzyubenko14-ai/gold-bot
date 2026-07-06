from aiogram import Router, F
from aiogram.types import Message

from config import ADMINS
from database import create_promo, delete_promo, get_promos

router = Router()


# =========================
# ПРОВЕРКА АДМИНА
# =========================
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

        await create_promo(code, float(reward), int(limit))

        await message.answer(
            f"✅ Промокод создан:\n\n"
            f"🔑 {code}\n"
            f"💰 {reward} Gold\n"
            f"👥 Лимит: {limit}"
        )

    except:
        await message.answer("❌ Формат: /createpromo CODE REWARD LIMIT")


# =========================
# УДАЛИТЬ ПРОМОКОД
# =========================
@router.message(F.text.startswith("/delpromo"))
async def delete_promo_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    try:
        _, code = message.text.split()
        await delete_promo(code)

        await message.answer(f"🗑 Удалён: {code}")

    except:
        await message.answer("❌ Формат: /delpromo CODE")


# =========================
# СПИСОК ПРОМОКОДОВ
# =========================
@router.message(F.text == "/promos")
async def list_promos(message: Message):

    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    promos = await get_promos()

    if not promos:
        return await message.answer("Промокодов нет")

    text = "📋 <b>Промокоды:</b>\n\n"

    for p in promos:
        text += (
            f"🔑 {p['code']}\n"
            f"💰 {p['reward']}\n"
            f"👥 {p['uses']}/{p['max_uses']}\n\n"
        )

    await message.answer(text)
