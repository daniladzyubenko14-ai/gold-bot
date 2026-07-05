from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    await callback.answer("Раздел Профиль скоро будет готов 🚀")


@router.callback_query(F.data == "referral")
async def referral(callback: CallbackQuery):
    await callback.answer("Раздел Реферал скоро будет готов 🚀")


@router.callback_query(F.data == "reviews")
async def reviews(callback: CallbackQuery):
    await callback.answer("Раздел Отзывы скоро будет готов 🚀")


@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    await callback.answer("Раздел Техподдержка скоро будет готов 🚀")


@router.callback_query(F.data == "info")
async def info(callback: CallbackQuery):
    await callback.answer("Раздел Информация скоро будет готов 🚀")


@router.callback_query(F.data == "withdraw")
async def withdraw(callback: CallbackQuery):
    await callback.answer("Раздел Вывод скоро будет готов 🚀")
