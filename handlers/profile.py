from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

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
# FSM
# =========================
class PromoState(StatesGroup):
    waiting_code = State()


# =========================
# PROFILE
# =========================
@router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):

    balance = await get_balance(call.from_user.id)

    await call.message.edit_text(
        f"👤 Профиль\n\n💰 Баланс: {balance:.2f} Gold",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus"),
                InlineKeyboardButton(text="🎫 Промокод", callback_data="promo")
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="back_menu")
            ]
        ])
    )


# =========================
# BONUS
# =========================
@router.callback_query(F.data == "bonus")
async def bonus(call: CallbackQuery):

    ok, left = await can_take_bonus(call.from_user.id)

    if not ok:
        await call.answer("⏳ Подожди немного", show_alert=True)
        return

    await give_bonus(call.from_user.id)

    await call.answer(f"🎁 +{BONUS_AMOUNT} Gold", show_alert=True)


# =========================
# PROMO START
# =========================
@router.callback_query(F.data == "promo")
async def promo(call: CallbackQuery, state: FSMContext):

    await state.set_state(PromoState.waiting_code)

    await call.message.answer("🎫 Введите промокод:")


# =========================
# PROMO INPUT
# =========================
@router.message(PromoState.waiting_code)
async def promo_input(message: Message, state: FSMContext):

    code = message.text.strip().upper()

    status, reward = await activate_promo(message.from_user.id, code)

    if status == "success":
        await message.answer(f"🎉 +{reward} Gold")
    elif status == "already_used":
        await message.answer("⚠️ Уже использован")
    elif status == "no_uses":
        await message.answer("❌ Лимит исчерпан")
    else:
        await message.answer("❌ Не существует")

    await state.clear()


# =========================
# BACK
# =========================
@router.callback_query(F.data == "back_menu")
async def back(call: CallbackQuery):
    await call.message.edit_text("Главное меню", reply_markup=main_menu())
