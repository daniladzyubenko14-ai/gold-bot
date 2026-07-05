from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


# ==========================
# 👤 ПРОФИЛЬ
# ==========================
@router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    await call.answer()

    await call.message.edit_text(
        "👤 <b>Профиль</b>\n\n"
        "💰 Баланс: 0.00 Gold\n"
        "👥 Приглашено: 0 человек\n\n"
        "🚧 Раздел находится в разработке."
    )


# ==========================
# 👥 РЕФЕРАЛ
# ==========================
@router.callback_query(F.data == "ref")
async def referral(call: CallbackQuery):
    await call.answer()

    await call.message.edit_text(
        "👥 <b>Реферальная система</b>\n\n"
        "🚧 Скоро здесь появится ваша реферальная ссылка."
    )


# ==========================
# 💸 ВЫВОД
# ==========================
@router.callback_query(F.data == "withdraw")
async def withdraw(call: CallbackQuery):
    await call.answer()

    await call.message.edit_text(
        "💸 <b>Вывод Gold</b>\n\n"
        "🚧 Скоро здесь можно будет оформить заявку."
    )


# ==========================
# ⭐ ОТЗЫВЫ
# ==========================
@router.callback_query(F.data == "reviews")
async def reviews(call: CallbackQuery):
    await call.answer()

    await call.message.edit_text(
        "⭐ <b>Отзывы</b>\n\n"
        "🚧 Скоро здесь будет ссылка на канал с отзывами."
    )


# ==========================
# 🛠 ТЕХПОДДЕРЖКА
# ==========================
@router.callback_query(F.data == "support")
async def support(call: CallbackQuery):
    await call.answer()

    await call.message.edit_text(
        "🛠 <b>Техническая поддержка</b>\n\n"
        "🚧 Скоро здесь будут контакты администратора."
    )


# ==========================
# ℹ️ ИНФОРМАЦИЯ
# ==========================
@router.callback_query(F.data == "info")
async def info(call: CallbackQuery):
    await call.answer()

    await call.message.edit_text(
        "ℹ️ <b>Информация</b>\n\n"
        "🚧 Скоро здесь появится информация о проекте."
    )
