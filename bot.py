import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db

from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.profile import router as profile_router
from handlers.admin import router as admin_router


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# 💥 ВАЖНО: FSM STORAGE (иначе промо НЕ работает)
dp = Dispatcher(storage=MemoryStorage())


dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(profile_router)
dp.include_router(admin_router)


async def main():
    await init_db()
    print("🚀 Gold Bot запущен")

    # убирает конфликт Railway
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
