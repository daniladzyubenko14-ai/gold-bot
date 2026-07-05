from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import add_user
from subscriptions import check_all
from config import ADMINS

router = Router()


# =========================
# СПОНСОРЫ КНОПКИ
# =========================
def sub_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url="https://t.me/daksiSO2")],
        [InlineKeyboardButton(text="📢 Подписаться", url="https://t.me/KIgolda")],
        [InlineKeyboardButton(text="Я подписался ✅", callback_data="check_sub")]
    ])


# =========================
# МЕНЮ
# =========================
def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="👥 Реферал", callback_data="ref")],
        [InlineKeyboardButton(text="💸 Вывод", callback_data="withdraw")]
    ])


# =========================
# /START
# =========================
@router.message(F.text == "/start")
async def start(message: Message):

    await add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name
    )

    await message.answer(
        "👋 Привет!\n\nПодпишись на спонсоров чтобы продолжить:",
        reply_markup=sub_kb()
    )


# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================
@router.callback_query(F.data == "check_sub")
async def check(call: CallbackQuery, bot: Bot):

    not_sub = await check_all(bot, call.from_user.id)

    if not_sub:
        await call.answer("❌ Вы не подписаны на всех спонсоров", show_alert=True)
        return

    await call.message.delete()

    await call.message.answer(
        "🏠 Главное меню",
        reply_markup=menu()
    )

    await call.answer("✅ Доступ открыт")


# =========================
# АВТО-БЛОК (ОТПИСКА)
# =========================
async def check_access(bot: Bot, user_id: int):
    not_sub = await check_all(bot, user_id)
    return len(not_sub) == 0
