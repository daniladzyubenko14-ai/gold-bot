from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import get_ref_info
from handlers.start import main_menu

router = Router()


# =========================
# РЕФЕРАЛЫ
# =========================
@router.callback_query(F.data == "ref")
async def referral(call: CallbackQuery):

    count = await get_ref_info(call.from_user.id)

    link = f"https://t.me/Kigold_bot?start={call.from_user.id}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_menu"
                )
            ]
        ]
    )

    await call.message.edit_text(
        f"👥 <b>РЕФЕРАЛКА</b>\n\n"
        f"👤 Приглашено: {count}\n\n"
        f"🔗 Ссылка:\n{link}",
        reply_markup=keyboard
    )

    await call.answer()


# =========================
# НАЗАД В МЕНЮ
# =========================
@router.callback_query(F.data == "back_menu")
async def back_menu(call: CallbackQuery):

    await call.message.edit_text(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )

    await call.answer()


# =========================
# ВЫВОД
# =========================
@router.callback_query(F.data == "withdraw")
async def withdraw(call: CallbackQuery):

    await call.answer(
        "🚧 Вывод скоро будет доступен.",
        show_alert=True
    )


# =========================
# ОТЗЫВЫ
# =========================
@router.callback_query(F.data == "reviews")
async def reviews(call: CallbackQuery):

    await call.answer(
        "⭐ Скоро появятся отзывы.",
        show_alert=True
    )


# =========================
# ПОДДЕРЖКА
# =========================
@router.callback_query(F.data == "support")
async def support(call: CallbackQuery):

    await call.answer(
        "🛠 Напишите: @YOUR_SUPPORT",
        show_alert=True
    )


# =========================
# ИНФОРМАЦИЯ
# =========================
@router.callback_query(F.data == "info")
async def info(call: CallbackQuery):

    await call.answer(
        "ℹ️ Gold Bot\nВерсия 1.0",
        show_alert=True
    )
