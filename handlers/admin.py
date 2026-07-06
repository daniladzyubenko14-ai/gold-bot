from aiogram import Router, F
from aiogram.types import Message

from config import ADMINS
from database import create_promo, delete_promo, get_promos

router = Router()


# =========================
# CHECK ADMIN
# =========================
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


# =========================
# CREATE PROMO
# /createpromo CODE REWARD LIMIT
# =========================
@router.message(F.text.startswith("/createpromo"))
async def create_promo_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    try:
        parts = message.text.split()

        if len(parts) != 4:
            return await message.answer("❌ Формат: /createpromo CODE REWARD LIMIT")

        _, code, reward, limit = parts

        await create_promo(
            code=code.upper(),
            reward=float(reward),
            max_uses=int(limit)
        )

        await message.answer(
            f"✅ Промокод создан!\n\n"
            f"🔑 Код: <b>{code.upper()}</b>\n"
            f"💰 Награда: <b>{reward} Gold</b>\n"
            f"👥 Лимит: <b>{limit}</b>",
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


# =========================
# DELETE PROMO
# /delpromo CODE
# =========================
@router.message(F.text.startswith("/delpromo"))
async def delete_promo_cmd(message: Message):

    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    try:
        parts = message.text.split()

        if len(parts) != 2:
            return await message.answer("❌ Формат: /delpromo CODE")

        _, code = parts

        await delete_promo(code)

        await message.answer(f"🗑 Удалён промокод: <b>{code.upper()}</b>")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


# =========================
# LIST PROMOS
# =========================
@router.message(F.text == "/promos")
async def list_promos(message: Message):

    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Нет доступа")

    promos = await get_promos()

    if not promos:
        return await message.answer("📭 Промокодов нет")

    text = "📋 <b>Промокоды:</b>\n\n"

    for p in promos:
        text += (
            f"🔑 <b>{p['code']}</b>\n"
            f"💰 {p['reward']} Gold\n"
            f"👥 {p['uses']}/{p['max_uses']}\n\n"
        )

    await message.answer(text)
