from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import (
    get_balance,
    can_take_bonus,
    give_bonus,
    BONUS_AMOUNT
)

from handlers.start import main_menu

router = Router()


# =========================
# ПРОФИЛЬ КНОПКИ
# =========================
def profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus"),
            InlineKeyboardButton(text="🎫 Промокод", callback_data="promo")
        ],
        [
            InlineKeyboardButton(text="📖 Инструкция", callback_data="instruction")
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

    text = (
        "👤 <b>ПРОФИЛЬ</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Баланс: <b>{balance:.2f} Gold</b>\n"
        "👥 Приглашено: <b>0</b>\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    await call.message.edit_text(text, reply_markup=profile_keyboard())
    await call.answer()


# =========================
# БОНУС (С АВТООБНОВЛЕНИЕМ ПРОФИЛЯ)
# =========================
@router.callback_query(F.data == "bonus")
async def bonus(call: CallbackQuery):

    can_take, left = await can_take_bonus(call.from_user.id)

    if not can_take:
        hours = left // 3600
        minutes = (left % 3600) // 60

        await call.answer(
            f"⏳ Осталось {hours}ч {minutes}м",
            show_alert=True
        )
        return

    await give_bonus(call.from_user.id)

    await call.answer(f"🎁 +{BONUS_AMOUNT} Gold получено!", show_alert=True)

    # 🔥 ОБНОВЛЕНИЕ ПРОФИЛЯ СРАЗУ
    balance = await get_balance(call.from_user.id)

    text = (
        "👤 <b>ПРОФИЛЬ</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Баланс: <b>{balance:.2f} Gold</b>\n"
        "👥 Приглашено: <b>0</b>\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    await call.message.edit_text(text, reply_markup=profile_keyboard())


# =========================
# ПРОМОКОД (заглушка)
# =========================
@router.callback_query(F.data == "promo")
async def promo(call: CallbackQuery):
    await call.answer("Промокоды скоро будут 🚀", show_alert=True)


# =========================
# ИНСТРУКЦИЯ (заглушка)
# =========================
@router.callback_query(F.data == "instruction")
async def instruction(call: CallbackQuery):
    await call.answer("Инструкция скоро будет 🚀", show_alert=True)


# =========================
# НАЗАД В МЕНЮ
# =========================
@router.callback_query(F.data == "back_menu")
async def back_menu(call: CallbackQuery):

    await call.message.edit_text(
        "✨ Добро пожаловать в Gold Bot!\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "💎 Здесь вы можете зарабатывать Gold\n\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=main_menu()
    )

    await call.answer()
