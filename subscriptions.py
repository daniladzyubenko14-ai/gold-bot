from aiogram import Bot
from config import SPONSORS


async def check_channel(bot: Bot, user_id: int, channel: str):
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def is_user_subscribed(bot: Bot, user_id: int) -> bool:
    for ch in SPONSORS:
        ok = await check_channel(bot, user_id, ch)
        if not ok:
            return False
    return True
