import database as db
from config import (
    PREDICTIONS_FILE_KEY,
    REQUIRED_REFERRALS,
    TARGET_CHANNEL_ID,
    TARGET_CHANNEL_LINK,
)
from services.channel_checker import check_all_channels


async def get_predictions_file_id() -> str | None:
    return await db.get_setting(PREDICTIONS_FILE_KEY)


async def save_predictions_file_id(file_id: str) -> None:
    await db.set_setting(PREDICTIONS_FILE_KEY, file_id)


async def get_target_invite_link(bot) -> str:
    """Generate a single-use Telegram invite link if TARGET_CHANNEL_ID is set, else return TARGET_CHANNEL_LINK."""
    if TARGET_CHANNEL_ID:
        try:
            link_obj = await bot.create_chat_invite_link(
                chat_id=TARGET_CHANNEL_ID,
                member_limit=1,
                name="SAT Mukofoti",
            )
            return link_obj.invite_link
        except Exception:
            pass
    return TARGET_CHANNEL_LINK or "https://t.me/+ZAWZoc8Cim9kYjAy"


async def user_can_unlock(bot, user: dict) -> tuple[bool, bool, int]:
    """
    Returns (channels_ok, referrals_ok, referral_count).
    Updates channels_joined in DB if verified.
    """
    telegram_id = user["telegram_id"]
    channels_ok = await check_all_channels(bot, telegram_id)
    if channels_ok and not user.get("channels_joined"):
        await db.update_user(telegram_id, channels_joined=1)
    elif not channels_ok and user.get("channels_joined"):
        await db.update_user(telegram_id, channels_joined=0)

    referral_count = user.get("referral_count", 0)
    referrals_ok = referral_count >= REQUIRED_REFERRALS
    return channels_ok, referrals_ok, referral_count


async def requirements_met(bot, user: dict) -> bool:
    channels_ok, referrals_ok, _ = await user_can_unlock(bot, user)
    return channels_ok and referrals_ok


def format_progress(user_id: int, referral_link: str, referral_count: int) -> str:
    return (
        f"📊 **Your Referral Progress**\n\n"
        f"🔗 **Your personal referral link:**\n"
        f"{referral_link}\n\n"
        f"👥 **Friends invited:** {referral_count}/{REQUIRED_REFERRALS}\n\n"
        f"📌 **Your friend needs to open the bot through this link and join all 3 channels below:**\n"
        f"• https://t.me/sat_humoyunbek\n"
        f"• https://t.me/sat_valley\n"
        f"• https://t.me/DesmosBootcamp"
    )


