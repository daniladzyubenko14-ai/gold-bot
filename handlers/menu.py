from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import get_balance
from handlers.start import main_menu

router = Router()


# =========================
# 👤 ПРОФИЛЬ
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
# 👥 РЕФЕРАЛ (заглушка)
# =========================
@router.callback_query(F.data == "ref")
async def referral(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "👥 <b>РЕФЕРАЛ</b>\n\n🚧 Скоро будет готово"
    )


# =========================
# 💸 ВЫВОД (заглушка)
# =========================
@router.callback_query(F.data == "withdraw")
async def withdraw(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "💸 <b>ВЫВОД</b>\n\n🚧 Скоро будет готово"
    )


# =========================
# ⭐ ОТЗЫВЫ (заглушка)
# =========================
@router.callback_query(F.data == "reviews")
async def reviews(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "⭐ <b>ОТЗЫВЫ</b>\n\n🚧 Скоро будет готово"
    )


# =========================
# 🛠 ПОДДЕРЖКА (заглушка)
# =========================
@router.callback_query(F.data == "support")
async def support(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "🛠 <b>ТЕХПОДДЕРЖКА</b>\n\n🚧 Скоро будет готово"
    )


# =========================
# ℹ️ ИНФОРМАЦИЯ (заглушка)
# =========================
@router.callback_query(F.data == "info")
async def info(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "ℹ️ <b>ИНФОРМАЦИЯ</b>\n\n🚧 Скоро будет готово"
    )


# =========================
# ⬅️ НАЗАД В МЕНЮ
# =========================
@router.callback_query(F.data == "back_menu")
async def back_menu(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "✨ Добро пожаловать в Gold Bot!\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "💎 Здесь вы можете зарабатывать Gold, выполняя простые действия.\n\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=main_menu()
    )


# =========================
# 🎁 БОНУС (пока заглушка)
# =========================
@router.callback_query(F.data == "bonus")
async def bonus(call: CallbackQuery):
    await call.answer("Бонус скоро будет добавлен 🚀", show_alert=True)


# =========================
# 🎫 ПРОМОКОД (пока заглушка)
# =========================
@router.callback_query(F.data == "promo")
async def promo(call: CallbackQuery):
    await call.answer("Промокоды скоро будут добавлены 🚀", show_alert=True)


# =========================
# 📖
