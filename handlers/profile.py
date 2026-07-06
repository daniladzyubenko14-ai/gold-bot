from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from database import get_balance, activate_promo

router = Router()

# =========================
# КНОПКИ
# =========================
def profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus"),
            InlineKeyboardButton(text="🎫 Промокод", callback_data="promo")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_menu")
        ]
    ])


# =========================
# ПРОФИЛЬ
# =========================
@router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    balance = await get_balance(call.from_user.id)

    await call.message.edit_text(
        f"👤 <b>Профиль</b>\n\n💰 Баланс: {balance:.2f} Gold",
        reply_markup=profile_keyboard()
    )
    await call.answer()


# =========================
# НАЖАЛ ПРОМОКОД
# =========================
@router.callback_query(F.data == "promo")
async def promo(call: CallbackQuery):
    await call.message.answer("🎫 Введите промокод:")
    await call.answer()


# =========================
# ВВОД ПРОМОКОДА (ВАЖНЫЙ ХЕНДЛЕР)
# =========================
@router.message(F.text)
async def promo_input(message: Message):

    code = message.text.strip().upper()

    # защита от случайного спама
    if len(code) < 2:
        return

    result, reward = await activate_promo(message.from_user.id, code)

    if result == "success":
        await message.answer(f"🎉 Промокод активирован! +{reward} Gold")

    elif result == "already_used":
        await message.answer("⚠️ Ты уже использовал этот промокод")

    elif result == "no_uses":
        await message.answer("❌ Лимит промокода исчерпан")

    elif result == "not_found":
        await message.answer("❌ Промокод не существует")

    else:
        await message.answer("❌ Ошибка")
