from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    await call.message.answer("👤 Профиль временно в разработке")
    await call.answer()
