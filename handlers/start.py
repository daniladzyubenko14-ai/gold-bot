from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import add_user
from subscriptions import is_user_subscribed
from config import SPONSORS

router = Router()


# =========================
# КНОПКИ СПОНСОРОВ
# =========================
def subscribe_kb():
    buttons = []

    for ch in SPONSORS:
        url = f"https://t.me/{ch.replace('@', '')}"
        buttons.append([InlineKeyboardButton(text=f"📢 Подписаться {ch}", url=url)])

    buttons.append([
        InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# МЕНЮ
# =========================
def menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="💸 Вывод", callback_data="withdraw")],
        [InlineKeyboardButton(text="👥 Реферал", callback_data="ref")]
    ])


# =========================
# /START
# =========================
@router.message(CommandStart())
async def start(message: Message, bot: Bot):

    await add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name
    )

    if not await is_user_subscribed(bot, message.from_user.id):
        await message.answer(
            "👋 Чтобы пользоваться ботом, подпишитесь на спонсоров:",
            reply_markup=subscribe_kb()
        )
        return

    await message.answer("🏠 Главное меню", reply_markup=menu_kb())


# =========================
# ПРОВЕРКА ПОДПИСОК
# =========================
@router.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery, bot: Bot):

    if not await is_user_subscribed(bot, call.from_user.id):
        await call.answer("❌ Вы не подписались на всех", show_alert=True)
        await call.message.answer(
            "❌ Вы не подписаны на всех спонсоров!",
            reply_markup=subscribe_kb()
        )
        return

    await call.message.delete()

    await call.message.answer("🏠 Главное меню", reply_markup=menu_kb())
    await call.answer("✅ Доступ открыт")


# =========================
# ЗАЩИТА (ВЫЗЫВАЙ В ДРУГИХ ФАЙЛАХ)
# =========================
async def check_access(bot: Bot, message: Message):
    if not await is_user_subscribed(bot, message.from_user.id):
        await message.answer(
            "❌ Сначала подпишитесь на спонсоров:",
            reply_markup=subscribe_kb()
        )
        return False
    return True
