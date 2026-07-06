from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from database import (
    get_balance,
    can_take_bonus,
    give_bonus,
    activate_promo,
    BONUS_AMOUNT
)

from handlers.start import main_menu

router = Router()

# =========================
# СОСТОЯНИЕ ПРОМОКОДА
# =========================
user_states = {}


# =========================
# КЛАВИАТУРА ПРОФИЛЯ
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

    await call.message.edit_text(
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"💰 Баланс: <b>{balance:.2f} Gold</b>",
        reply_markup=profile_keyboard()
    )

    await call.answer()


# =========================
# БОНУС
# =========================
@router.callback_query(F.data == "bonus")
async def bonus(call: CallbackQuery):

    can_take, left = await can_take_bonus(call.from_user.id)

    if not can_take:
        await call.answer("⏳ Кулдаун ещё не прошёл", show_alert=True)
        return

    await give_bonus(call.from_user.id)

    balance = await get_balance(call.from_user.id)

    await call.message.edit_text(
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"💰 Баланс: <b>{balance:.2f} Gold</b>",
        reply_markup=profile_keyboard()
    )

    await call.answer("🎁 Бонус получен!")


# =========================
# НАЖАТИЕ ПРОМОКОДА
# =========================
@router.callback_query(F.data == "promo")
async def promo(call: CallbackQuery):

    user_states[call.from_user.id] = "promo"

    await call.message.answer(
        "🎫 Введите промокод:\n\n"
        "⬅️ Напишите код или нажмите назад"
    )

    await call.answer()


# =========================
# ВВОД ПРОМОКОДА (ГЛАВНЫЙ ФИКС)
# =========================
@router.message()
async def promo_input(message: Message):

    user_id = message.from_user.id

    if user_states.get(user_id) != "promo":
        return

    if not message.text:
        return

    code = message.text.strip().upper()

    result, reward = await activate_promo(user_id, code)

    if result == "success":
        await message.answer(f"🎉 Промокод активирован! +{reward} Gold")
    elif result == "already_used":
        await message.answer("⚠️ Уже использован")
    elif result == "no_uses":
        await message.answer("❌ Лимит исчерпан")
    else:
        await message.answer("❌ Промокод не найден")

    user_states.pop(user_id, None)


# =========================
# ИНСТРУКЦИЯ
# =========================
@router.callback_query(F.data == "instruction")
async def instruction(call: CallbackQuery):
    await call.answer("Скоро будет 🚀", show_alert=True)


# =========================
# НАЗАД
# =========================
@router.callback_query(F.data == "back_menu")
async def back_menu(call: CallbackQuery):

    await call.message.edit_text(
        "✨ Главное меню",
        reply_markup=main_menu()
    )

    await call.answer()
