from aiogram import Bot
from config import SPONSORS


async def check_channel(bot: Bot, user_id: int, channel: str):
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False


async def check_all(bot: Bot, user_id: int):
    not_subscribed = []

    for ch in SPONSORS:
        if not await check_channel(bot, user_id, ch):
            not_subscribed.append(ch)

    return not_subscribed
