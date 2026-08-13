import database as db
from config import (
    EXPLORE_SAT_VALLEY_LINK,
    PREDICTIONS_FILE_KEY,
    REQUIRED_REFERRALS,
    SAT_VALLEY_LINK,
)
from services.channel_checker import check_all_channels


def progress_bar(count: int, total: int = REQUIRED_REFERRALS) -> str:
    filled = "🟩" * min(count, total)
    empty = "⬜" * max(0, total - count)
    return f"{filled}{empty}  {count} / {total}"


async def get_predictions_file_id() -> str | None:
    active = await db.get_setting("predictions_active")
    if active == "0":
        return None
    return await db.get_setting(PREDICTIONS_FILE_KEY)


async def save_predictions_file_id(file_id: str, file_name: str, file_size: int) -> None:
    await db.save_reward_file(file_id, file_name, file_size)


async def user_can_unlock(bot, user: dict) -> tuple[bool, bool, int]:
    telegram_id = user["telegram_id"]
    channels_ok = await check_all_channels(bot, telegram_id)
    if channels_ok and not user.get("channels_joined"):
        await db.update_user(telegram_id, channels_joined=1)

    referral_count = user.get("referral_count", 0)
    referrals_ok = referral_count >= REQUIRED_REFERRALS
    return channels_ok, referrals_ok, referral_count


def format_dashboard(user_id: int, referral_link: str, referral_count: int) -> str:
    return (
        "🎁 <b>Your SAT Math Prediction is waiting!</b>\n\n"
        f"You need <b>{REQUIRED_REFERRALS} successful referrals</b> to unlock it.\n\n"
        f"<b>Your progress:</b>\n{progress_bar(referral_count)}\n\n"
        "For a referral to count, your friend must:\n"
        "✅ Open this bot through your invite link\n"
        "✅ Join all 3 required channels\n\n"
        f"<b>Your personal invite link:</b>\n{referral_link}"
    )


async def format_referral_status(user_id: int) -> str:
    user = await db.get_user(user_id)
    if not user:
        return "Please send /start first."

    referral_count = user.get("referral_count", 0)
    verified, pending = await db.get_referral_friends(user_id)
    bar = progress_bar(referral_count)

    lines = [
        "🎯 <b>Your SAT Math Prediction</b>",
        "",
        "<b>Referral Progress</b>",
        bar,
        "",
    ]

    slot = 1
    for friend in verified:
        label = friend.get("full_name") or friend.get("username") or f"Friend {slot}"
        lines.append(f"✅ Friend {slot} — Verified ({label})")
        slot += 1

    for friend in pending:
        label = friend.get("full_name") or friend.get("username") or f"Friend {slot}"
        lines.append(f"⏳ Friend {slot} — Waiting ({label})")
        slot += 1

    while slot <= REQUIRED_REFERRALS:
        lines.append(f"⏳ Friend {slot} — Waiting")
        slot += 1

    remaining = max(REQUIRED_REFERRALS - referral_count, 0)
    if remaining:
        lines.extend(
            [
                "",
                f"<b>{remaining} more successful referral{'s' if remaining != 1 else ''} needed!</b>",
                "",
                "Your friend must join all 3 channels for the referral to count.",
            ]
        )
    else:
        lines.extend(["", "🎉 <b>All referrals complete — your PDF is unlocked!</b>"])

    return "\n".join(lines)


def format_channels_step() -> str:
    return (
        "📚 <b>Step 1 — Join the SAT Valley channels</b>\n\n"
        "Join all 3 channels below:\n\n"
        "<b>1. SAT Humoyunbek</b>\n"
        "<b>2. SAT Valley</b>\n"
        "<b>3. Desmos Bootcamp</b>\n\n"
        "After joining all three, return here and tap:\n"
        "<b>✅ Check My Membership</b>"
    )


def format_almost_there(missing_names: list[str]) -> str:
    if len(missing_names) == 1:
        channels_text = f"the <b>{missing_names[0]}</b> channel"
    else:
        channels_text = "these channels: " + ", ".join(f"<b>{n}</b>" for n in missing_names)

    return (
        "⏳ <b>Almost there!</b>\n\n"
        "We haven't counted this referral yet because you still need to join "
        f"{channels_text}.\n\n"
        "Please join the remaining channel(s), then tap "
        "<b>🔄 Check Membership</b>.\n\n"
        "Once all 3 are confirmed, the referral will be added automatically."
    )


def format_unlock_success() -> str:
    return (
        "🎉 <b>YOU UNLOCKED IT!</b>\n\n"
        f"You've successfully invited <b>{REQUIRED_REFERRALS} friends</b>.\n\n"
        "Your <b>SAT Math Prediction PDF</b> is ready. 📎"
    )


def format_post_reward_funnel() -> str:
    return (
        "🚀 <b>Want more SAT preparation resources?</b>\n\n"
        "Explore SAT Valley and continue preparing with our practice materials, "
        "lessons, and resources."
    )


async def deliver_reward(bot, telegram_id: int) -> bool:
    user = await db.get_user(telegram_id)
    if not user or user.get("reward_sent"):
        return False

    referral_count = user.get("referral_count", 0)
    if referral_count < REQUIRED_REFERRALS:
        return False

    file_id = await get_predictions_file_id()
    from aiogram.exceptions import TelegramAPIError

    try:
        await bot.send_message(telegram_id, format_unlock_success())
        if file_id:
            await bot.send_document(telegram_id, file_id)
        else:
            await bot.send_message(
                telegram_id,
                "Your reward is unlocked! The PDF will be delivered shortly — "
                "check back soon or contact SAT Valley support.",
            )
    except TelegramAPIError:
        return False

    await db.update_user(
        telegram_id,
        reward_sent=1,
        file_unlocked=1,
    )

    from keyboards import post_reward_keyboard

    try:
        await bot.send_message(
            telegram_id,
            format_post_reward_funnel(),
            reply_markup=post_reward_keyboard(),
        )
    except TelegramAPIError:
        pass

    return True
