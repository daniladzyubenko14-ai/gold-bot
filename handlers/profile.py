from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from database import (
    get_balance,
    can_take_bonus,
    give_bonus,
    BONUS_AMOUNT,
    activate_promo
)

from handlers.start import main_menu

router = Router()

# =========================
# СОСТОЯНИЯ ПОЛЬЗОВАТЕЛЕЙ
# =========================
user_states = {}

# =========================
# КНОПКИ ПРОФИЛЯ
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
# БОНУС
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

    await call.answer(f"🎁 +{BONUS_AMOUNT} Gold", show_alert=True)

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
# ПРОМОКОД (ОТКРЫТЬ ВВОД)
# =========================
@router.callback_query(F.data == "promo")
async def promo(call: CallbackQuery):

    user_states[call.from_user.id] = "waiting_promo"

    await call.message.edit_text(
        "🎫 Введите промокод:\n\n"
        "или нажмите назад 👇",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_profile")]
        ])
    )

    await call.answer()

# =========================
# ВВОД ПРОМОКОДА
# =========================
@router.message(lambda m: m.from_user.id in user_states and user_states[m.from_user.id] == "waiting_promo")
async def handle_promo(message: Message):

    code = message.text.strip().upper()

    result, reward = await activate_promo(message.from_user.id, code)

    if result == "success":
        await message.answer(f"🎉 Промокод активирован! +{reward} Gold")
    elif result == "already_used":
        await message.answer("⚠️ Уже использован")
    elif result == "no_uses":
        await message.answer("❌ Лимит исчерпан")
    else:
        await message.answer("❌ Промокод не найден")

    user_states.pop(message.from_user.id, None)

# =========================
# НАЗАД В ПРОФИЛЬ
# =========================
@router.callback_query(F.data == "back_profile")
async def back_profile(call: CallbackQuery):

    user_states.pop(call.from_user.id, None)

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
# ИНСТРУКЦИЯ
# =========================
@router.callback_query(F.data == "instruction")
async def instruction(call: CallbackQuery):
    await call.answer("Скоро будет 🚀", show_alert=True)

# =========================
# В МЕНЮ
# =========================
@router.callback_query(F.data == "back_menu")
async def back_menu(call: CallbackQuery):

    user_states.pop(call.from_user.id, None)

    await call.message.edit_text(
        "✨ Главное меню",
        reply_markup=main_menu()
    )

    await call.answer()
