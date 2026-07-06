# profile.py
# NOTE: Placeholder generated file.
# The full project-specific version depends on the final database/admin API.
# This version preserves the structure discussed and should be completed
# together with the remaining modules.

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database import get_balance, can_take_bonus, give_bonus, BONUS_AMOUNT, activate_promo
from handlers.start import main_menu

router = Router()

class PromoState(StatesGroup):
    waiting_code = State()

def profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus"),
         InlineKeyboardButton(text="🎫 Промокод", callback_data="promo")],
        [InlineKeyboardButton(text="📖 Инструкция", callback_data="instruction")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_menu")]
    ])

@router.callback_query(F.data=="profile")
async def profile(call: CallbackQuery):
    bal=await get_balance(call.from_user.id)
    await call.message.edit_text(
        f"👤 <b>ПРОФИЛЬ</b>\n\n💰 Баланс: <b>{bal:.2f} Gold</b>",
        reply_markup=profile_keyboard()
    )
    await call.answer()

@router.callback_query(F.data == "bonus")
async def bonus(call: CallbackQuery):

    ok, left = await can_take_bonus(call.from_user.id)

    if not ok:

        hours = left // 3600
        minutes = (left % 3600) // 60

        await call.answer(
            f"⏳ Осталось {hours}ч {minutes}м",
            show_alert=True
        )
        return

    await give_bonus(call.from_user.id)

    balance = await get_balance(call.from_user.id)

    await call.message.edit_text(
        f"👤 <b>ПРОФИЛЬ</b>\n\n💰 Баланс: <b>{balance:.2f} Gold</b>",
        reply_markup=profile_keyboard()
    )

    await call.answer(
        f"🎁 Получено +{BONUS_AMOUNT} Gold",
        show_alert=True
    )

@router.callback_query(F.data=="promo")
async def promo(call: CallbackQuery,state:FSMContext):
    await state.set_state(PromoState.waiting_code)
    await call.message.edit_text(
        "🎫 <b>Введите промокод:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад",callback_data="back_menu")]])
    )
    await call.answer()

@router.message(PromoState.waiting_code)
async def promo_enter(message:Message,state:FSMContext):
    if not message.text:
        return
    if message.text.startswith("/"):
        await state.clear()
        return
    status,reward=await activate_promo(message.from_user.id,message.text.strip().upper())
    texts={
        "success":f"✅ Промокод активирован!\n💰 +{reward:.2f} Gold",
        "already_used":"⚠️ Вы уже использовали этот промокод.",
        "no_uses":"❌ Лимит промокода исчерпан.",
        "not_found":"❌ Промокод не существует."
    }
    await message.answer(texts.get(status,"❌ Ошибка."))
    await state.clear()

@router.callback_query(F.data=="instruction")
async def instruction(call:CallbackQuery):
    await call.answer("📖 Скоро.",show_alert=True)

@router.callback_query(F.data=="back_menu")
async def back(call:CallbackQuery,state:FSMContext):
    await state.clear()
    await call.message.edit_text("🏠 Главное меню",reply_markup=main_menu())
    await call.answer()
