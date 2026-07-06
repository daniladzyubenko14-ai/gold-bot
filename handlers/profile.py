from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

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
# FSM
# =========================
class PromoState(StatesGroup):
    waiting_code = State()


# =========================
# КНОПКИ ПРОФИЛЯ
# =========================
def profile_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🎁 Бонус",
                    callback_data="bonus"
                ),

                InlineKeyboardButton(
                    text="🎫 Промокод",
                    callback_data="promo"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📖 Инструкция",
                    callback_data="instruction"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_menu"
                )
            ]
        ]
    )


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

    await call.message.edit_text(
        text,
        reply_markup=profile_keyboard()
    )

    await call.answer()


# =========================
# БОНУС
# =========================
@router.callback_query(F.data == "bonus")
async def bonus(call: CallbackQuery):

    can_take, left = await can_take_bonus(
        call.from_user.id
    )

    if not can_take:

        hours = left // 3600
        minutes = (left % 3600) // 60

        await call.answer(
            f"⏳ Осталось {hours}ч {minutes}м",
            show_alert=True
        )
        return

    await give_bonus(call.from_user.id)

    balance = await get_balance(
        call.from_user.id
    )

    text = (
        "👤 <b>ПРОФИЛЬ</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Баланс: <b>{balance:.2f} Gold</b>\n"
        "👥 Приглашено: <b>0</b>\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    await call.message.edit_text(
        text,
        reply_markup=profile_keyboard()
    )

    await call.answer(
        f"🎁 Получено +{BONUS_AMOUNT} Gold",
        show_alert=True
    )
    # =========================
# ПРОМОКОД
# =========================
@router.callback_query(F.data == "promo")
async def promo(call: CallbackQuery, state: FSMContext):

    await state.set_state(
        PromoState.waiting_code
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="promo_back"
                )
            ]
        ]
    )

    await call.message.edit_text(
        "🎫 <b>Введите промокод:</b>",
        reply_markup=keyboard
    )

    await call.answer()


# =========================
# ВВОД ПРОМОКОДА
# =========================
@router.message(PromoState.waiting_code)
async def promo_enter(
    message: Message,
    state: FSMContext
):

    # Если пользователь ввёл команду —
    # просто выходим из режима ввода.
    if message.text.startswith("/"):
        await state.clear()
        return

    code = message.text.strip().upper()

    status, reward = await activate_promo(
        message.from_user.id,
        code
    )

    if status == "success":

        await message.answer(
            f"✅ Промокод активирован!\n\n"
            f"💰 +{reward:.2f} Gold"
        )

    elif status == "already_used":

        await message.answer(
            "⚠️ Вы уже использовали этот промокод."
        )

    elif status == "no_uses":

        await message.answer(
            "❌ Лимит промокода исчерпан."
        )

    elif status == "not_found":

        await message.answer(
            "❌ Промокод не существует."
        )

    else:

        await message.answer(
            "❌ Ошибка активации."
        )

    await state.clear()


# =========================
# НАЗАД ИЗ ПРОМО
# =========================
@router.callback_query(F.data == "promo_back")
async def promo_back(
    call: CallbackQuery,
    state: FSMContext
):

    await state.clear()

    balance = await get_balance(
        call.from_user.id
    )

    text = (
        "👤 <b>ПРОФИЛЬ</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Баланс: <b>{balance:.2f} Gold</b>\n"
        "👥 Приглашено: <b>0</b>\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    await call.message.edit_text(
        text,
        reply_markup=profile_keyboard()
    )

    await call.answer()


# =========================
# ИНСТРУКЦИЯ
# =========================
@router.callback_query(F.data == "instruction")
async def instruction(call: CallbackQuery):

    await call.answer(
        "📖 Инструкция скоро появится.",
        show_alert=True
    )


# =========================
# НАЗАД
# =========================
@router.callback_query(F.data == "back_menu")
async def back_menu(call: CallbackQuery):

    await call.message.edit_text(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )

    await call.answer()
