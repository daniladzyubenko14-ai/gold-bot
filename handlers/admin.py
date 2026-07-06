from aiogram import Router, F
from aiogram.types import Message

from config import ADMINS
from database import (
    create_promo,
    delete_promo,
    get_promos
)

router = Router()


# =========================
# ПРОВЕРКА АДМИНА
# =========================
def is_admin(user_id: int):
    return user_id in ADMINS


# =========================
# СОЗДАТЬ ПРОМО
# /createpromo CODE REWARD LIMIT
# =========================
@router.message(F.text.startswith("/createpromo"))
async def createpromo(message: Message):

    if not is_admin(message.from_user.id):
        return

    try:

        parts = message.text.split()

        if len(parts) != 4:
            await message.answer(
                "❌ Использование:\n"
                "/createpromo CODE REWARD LIMIT"
            )
            return

        _, code, reward, limit = parts

        await create_promo(
            code,
            float(reward),
            int(limit)
        )

        await message.answer(
            f"✅ Промокод создан!\n\n"
            f"🔑 Код: {code.upper()}\n"
            f"💰 Награда: {reward} Gold\n"
            f"👥 Лимит: {limit}"
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка:\n{e}")


# =========================
# УДАЛИТЬ ПРОМО
# /delpromo CODE
# =========================
@router.message(F.text.startswith("/delpromo"))
async def delpromo(message: Message):

    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) != 2:
        await message.answer(
            "❌ Использование:\n"
            "/delpromo CODE"
        )
        return

    _, code = parts

    await delete_promo(code)

    await message.answer(
        f"🗑 Промокод {code.upper()} удалён."
    )


# =========================
# СПИСОК ПРОМО
# /promos
# =========================
@router.message(F.text == "/promos")
async def promos(message: Message):

    if not is_admin(message.from_user.id):
        return

    promos = await get_promos()

    if not promos:
        await message.answer("📭 Промокодов нет.")
        return

    text = "📋 <b>Промокоды:</b>\n\n"

    for promo in promos:

        text += (
            f"🔑 <b>{promo['code']}</b>\n"
            f"💰 {promo['reward']} Gold\n"
            f"👥 Использовано: {promo['uses']}/{promo['max_uses']}\n\n"
        )

    await message.answer(text)
