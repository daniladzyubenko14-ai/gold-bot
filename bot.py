import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN

# =========================
# DATABASE
# =========================
from database import init_db

# =========================
# HANDLERS
# =========================
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.admin import router as admin_router
from handlers.profile import router as profile_router  # если есть профиль

# =========================
# BOT INIT
# =========================
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()


# =========================
# ROUTERS (ВАЖНО: ВСЕ ПОДКЛЮЧАЕМ)
# =========================
dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(profile_router)
dp.include_router(admin_router)


# =========================
# START BOT
# =========================
async def main():
    await init_db()
    print("🚀 Gold Bot запущен")
    await dp.start_polling(bot)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    asyncio.run(main())
