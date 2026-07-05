from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import add_user

router = Router()


# =========================
# КНОПКИ СПОНСОРОВ
# =========================
def sponsors_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Спонсор 1", url="https://t.me/your_channel")],
        [InlineKeyboardButton(text="📢 Спонсор 2", url="https://t.me/your_channel")],
        [InlineKeyboardButton(text="📢 Спонсор 3", url="https://t.me/your_channel")],
        [InlineKeyboardButton(text="Я подписался ✅", callback_data="check_sub")]
    ])


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="👥 Реферал", callback_data="ref")],
        [InlineKeyboardButton(text="⭐ Отзывы", callback_data="reviews")],
        [InlineKeyboardButton(text="🆘 Техподдержка", callback_data="support")],
        [InlineKeyboardButton(text="💸 Вывод", callback_data="withdraw")]
    ])


# =========================
# /START
# =========================
@router.message(F.text == "/start")
async def start_cmd(message: Message):

    await add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name
    )

    await message.answer(
        "👋 Привет!\n\n"
        "Чтобы зарабатывать голду, подпишись на наших спонсоров 👇",
        reply_markup=sponsors_kb()
    )


# =========================
# ПРОВЕРКА ПОДПИСОК (ЗАГЛУШКА)
# =========================
@router.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery):

    # ⚠️ ВРЕМЕННО: без Telegram API проверки каналов
    # позже добавим real check через bot.get_chat_member

    await call.message.delete()

    await call.message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )

    await call.answer("✅ Доступ открыт")
