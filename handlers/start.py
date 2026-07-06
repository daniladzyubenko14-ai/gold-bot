from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import add_user, set_referrer, reward_referrer
from subscriptions import is_user_subscribed
from config import SPONSORS

router = Router()


# =========================
# СПОНСОРЫ
# =========================

def sponsors_kb():

    buttons = []

    for i, sponsor in enumerate(SPONSORS, start=1):

        buttons.append([
            InlineKeyboardButton(
                text=f"📢 Спонсор {i}",
                url=f"https://t.me/{sponsor.replace('@','')}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="✅ Я подписался",
            callback_data="check_sub"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

def main_menu():

    return InlineKeyboardMarkup(inline_keyboard=[

        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
            InlineKeyboardButton(text="👥 Рефералы", callback_data="ref")
        ],
        [
            InlineKeyboardButton(text="💸 Вывод", callback_data="withdraw"),
            InlineKeyboardButton(text="⭐ Отзывы", callback_data="reviews")
        ],
        [
            InlineKeyboardButton(text="🛠 Поддержка", callback_data="support"),
            InlineKeyboardButton(text="ℹ️ Информация", callback_data="info")
        ]
    ])


# =========================
# START (РЕФЕРАЛ + ПОДПИСКА)
# =========================

@router.message(CommandStart())
async def start(message: Message, bot: Bot):

    user_id = message.from_user.id

    # =========================
    # РЕФЕРАЛ КОД
    # =========================
    args = message.text.split()

    if len(args) > 1:

        try:
            ref_id = int(args[1])

            # сохраняем реферала (ТОЛЬКО 1 РАЗ)
            await set_referrer(user_id, ref_id)

        except:
            pass

    # =========================
    # СОЗДАНИЕ ЮЗЕРА
    # =========================
    await add_user(
        user_id,
        message.from_user.username or "",
        message.from_user.full_name
    )

    # =========================
    # ПРОВЕРКА ПОДПИСОК
    # =========================
    if not await is_user_subscribed(bot, user_id):

        await message.answer(
            "❗ Подпишитесь на всех спонсоров, чтобы продолжить.",
            reply_markup=sponsors_kb()
        )
        return

    # =========================
    # ВЫДАЧА РЕФЕРАЛ НАГРАДЫ
    # =========================
    await reward_referrer(user_id)

    # =========================
    # МЕНЮ
    # =========================
    await message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )


# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================

@router.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery, bot: Bot):

    user_id = call.from_user.id

    if not await is_user_subscribed(bot, user_id):

        await call.answer(
            "❌ Вы не подписались на всех спонсоров.",
            show_alert=True
        )
        return

    await reward_referrer(user_id)

    await call.message.edit_text(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )

    await call.answer("✅ Доступ открыт")
