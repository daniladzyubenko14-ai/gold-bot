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

user_states = {}


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


@router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):

    balance = await get_balance(call.from_user.id)

    await call.message.edit_text(
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"💰 Баланс: <b>{balance:.2f} Gold</b>",
        reply_markup=profile_keyboard()
    )

    await call.answer()


@router.callback_query(F.data == "promo")
async def promo(call: CallbackQuery):

    user_states[call.from_user.id] = "waiting_promo"

    await call.message.answer("🎫 Введите промокод:")
    await call.answer()


@router.message()
async def handle_all_messages(message: Message):

    if not message.text:
        return

    user_id = message.from_user.id

    if user_states.get(user_id) != "waiting_promo":
        return

    code = message.text.strip().upper()

    result, reward = await activate_promo(user_id, code)

    if result == "success":
        await message.answer(f"🎉 +{reward} Gold")
    elif result == "already_used":
        await message.answer("⚠️ Уже использован")
    elif result == "no_uses":
        await message.answer("❌ Лимит исчерпан")
    else:
        await message.answer("❌ Не найден")

    user_states.pop(user_id, None)
