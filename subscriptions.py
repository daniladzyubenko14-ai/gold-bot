from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from config import SPONSORS


async def is_user_subscribed(
    bot: Bot,
    user_id: int
) -> bool:

    for channel in SPONSORS:

        try:

            member = await bot.get_chat_member(
                channel,
                user_id
            )

            if member.status in (
                ChatMemberStatus.LEFT,
                ChatMemberStatus.KICKED
            ):
                return False

        except Exception:
            return False

    return True
