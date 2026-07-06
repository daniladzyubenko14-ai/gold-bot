from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database import get_balance, activate_promo

router = Router()


# =========================
# FSM
# =========================
class PromoState(StatesGroup):
    waiting = State()


# =========================
# КНОПКИ
# =========================
def profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus"),
            InlineKeyboardButton(text="🎫 Промокод", callback_data="promo")
        ]
    ])


# =========================
# ПРОФИЛЬ
# =========================
@router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):

    balance = await get_balance(call.from_user.id)

    await call.message.edit_text(
        f"👤 ПРОФИЛЬ\n💰 {balance:.2f} Gold",
        reply_markup=profile_keyboard()
    )

    await call.answer()


# =========================
# НАЖАТ ПРОМО
# =========================
@router.callback_query(F.data == "promo")
async def promo(call: CallbackQuery, state: FSMContext):

    await state.set_state(PromoState.waiting)

    await call.message.answer("🎫 Введите промокод:")
    await call.answer()


# =========================
# ВВОД ПРОМОКОДА (ГЛАВНЫЙ ФИКС)
# =========================
@router.message(PromoState.waiting)
async def promo_input(message: Message, state: FSMContext):

    if message.text.startswith("/"):
        return

    code = message.text.strip().upper()

    result, reward = await activate_promo(message.from_user.id, code)

    if result == "success":
        await message.answer(f"🎉 +{reward} Gold")

    elif result == "already_used":
        await message.answer("⚠️ Уже использован")

    elif result == "no_uses":
        await message.answer("❌ Лимит исчерпан")

    elif result == "not_found":
        await message.answer("❌ Не существует")

    await state.clear()
