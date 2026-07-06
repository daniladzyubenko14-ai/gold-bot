from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import add_user
from subscriptions import is_user_subscribed
from config import SPONSORS

router = Router()


# =========================
# КНОПКИ СПОНСОРОВ
# =========================
def sponsors_kb():

    buttons = []

    for i, sponsor in enumerate(SPONSORS, start=1):

        buttons.append([
            InlineKeyboardButton(
                text=f"📢 Спонсор {i}",
                url=f"https://t.me/{sponsor.replace('@', '')}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="✅ Я подписался",
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

    await add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name
    )

    if not await is_user_subscribed(
        bot,
        message.from_user.id
    ):

        await message.answer(
            "❗ Для использования бота подпишитесь на всех спонсоров.",
            reply_markup=sponsors_kb()
        )
        return

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

        await call.answer(
            "❌ Вы подписались не на все каналы.",
            show_alert=True
        )
        return

    await call.message.edit_text(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )

    await call.answer("✅ Доступ открыт")
