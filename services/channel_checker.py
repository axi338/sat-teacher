from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError

from config import CHANNELS, CHANNEL_NAMES


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


async def get_channel_membership_status(
    bot: Bot, user_id: int
) -> tuple[bool, int, list[str]]:
    """Return (all_joined, joined_count, missing_channel_names)."""
    if not CHANNELS:
        return True, 0, []

    joined = 0
    missing: list[str] = []
    for i, channel_id in enumerate(CHANNELS):
        name = CHANNEL_NAMES[i] if i < len(CHANNEL_NAMES) else f"Channel {i + 1}"
        if await is_channel_member(bot, user_id, channel_id):
            joined += 1
        else:
            missing.append(name)

    return joined == len(CHANNELS), joined, missing


async def check_all_channels(bot: Bot, user_id: int) -> bool:
    all_joined, _, _ = await get_channel_membership_status(bot, user_id)
    return all_joined
