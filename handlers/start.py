from aiogram import Router, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import add_user, is_banned
from subscriptions import is_user_subscribed
from config import SPONSORS

router = Router()


# =========================
# КНОПКИ СПОНСОРОВ
# =========================
def sponsors_keyboard():

    buttons = []

    for sponsor in SPONSORS:
        buttons.append([
            InlineKeyboardButton(
                text=f"📢 {sponsor}",
                url=f"https://t.me/{sponsor.replace('@','')}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="✅ Проверить подписку",
            callback_data="check_sub"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================
def main_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="👤 Профиль",
                    callback_data="profile"
                ),

                InlineKeyboardButton(
                    text="👥 Рефералы",
                    callback_data="ref"
                )
            ],

            [
                InlineKeyboardButton(
                    text="💸 Вывод",
                    callback_data="withdraw"
                ),

                InlineKeyboardButton(
                    text="⭐ Отзывы",
                    callback_data="reviews"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🛠 Поддержка",
                    callback_data="support"
                ),

                InlineKeyboardButton(
                    text="ℹ️ Информация",
                    callback_data="info"
                )
            ]
        ]
    )


# =========================
# START
# =========================
@router.message(CommandStart())
async def start(message: Message, bot: Bot):

    if await is_banned(message.from_user.id):
        return await message.answer(
            "⛔ Вы заблокированы."
        )

    await add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name
    )

    if not await is_user_subscribed(
        bot,
        message.from_user.id
    ):

        return await message.answer(
            "❗ Для использования бота подпишитесь на всех спонсоров.",
            reply_markup=sponsors_keyboard()
        )

    await message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )


# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================
@router.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery, bot: Bot):

    if not await is_user_subscribed(
        bot,
        call.from_user.id
    ):

        return await call.answer(
            "❌ Вы подписались не на все каналы.",
            show_alert=True
        )

    await call.message.edit_text(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )

    await call.answer(
        "✅ Проверка успешно пройдена!"
    )
