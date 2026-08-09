from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError

from config import CHANNELS


MEMBER_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


async def is_channel_member(bot: Bot, user_id: int, channel_id: str) -> bool:
    if not channel_id:
        return False
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in MEMBER_STATUSES
    except TelegramAPIError:
        return False
    except Exception:
        return False


async def check_all_channels(bot: Bot, user_id: int) -> bool:
    if not CHANNELS:
        return True
    for channel_id in CHANNELS:
        if not await is_channel_member(bot, user_id, channel_id):
            return False
    return True

