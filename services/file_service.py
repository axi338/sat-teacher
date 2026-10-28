import database as db
from config import (
    REQUIRED_REFERRALS,
    REWARD_CHANNEL_ID,
    REWARD_CHANNEL_LINK,
)
from services.channel_checker import check_all_channels
from translations import T, get_lang


def progress_bar(count: int, total: int = REQUIRED_REFERRALS) -> str:
    filled = "🟩" * min(count, total)
    empty  = "⬜" * max(0, total - count)
    return f"{filled}{empty}  {count} / {total}"


async def user_can_unlock(bot, user: dict) -> tuple[bool, bool, int]:
    telegram_id = user["telegram_id"]
    channels_ok = await check_all_channels(bot, telegram_id)
    if channels_ok and not user.get("channels_joined"):
        await db.update_user(telegram_id, channels_joined=1)

    referral_count = user.get("referral_count", 0)
    referrals_ok   = referral_count >= REQUIRED_REFERRALS
    return channels_ok, referrals_ok, referral_count


async def create_unique_reward_link(bot, telegram_id: int) -> str | None:
    """Generate a one-time invite link (member_limit=1) to the reward channel."""
    if REWARD_CHANNEL_ID:
        try:
            link_obj = await bot.create_chat_invite_link(
                chat_id=REWARD_CHANNEL_ID,
                member_limit=1,
                name=f"SAT To\u02bbliq Kurs {telegram_id}",
            )
            return link_obj.invite_link
        except Exception:
            pass
    return REWARD_CHANNEL_LINK or None


def format_dashboard(user_id: int, referral_link: str, referral_count: int,
                     lang: str = "uz") -> str:
    bar = progress_bar(referral_count)
    return T[lang]["dashboard"].format(n=REQUIRED_REFERRALS, bar=bar, link=referral_link)


async def format_referral_status(user_id: int, lang: str = "uz") -> str:
    user = await db.get_user(user_id)
    if not user:
        return T[lang]["not_started"]

    referral_count = user.get("referral_count", 0)
    verified, pending = await db.get_referral_friends(user_id)
    bar = progress_bar(referral_count)
    t = T[lang]

    lines = [t["status_header"], "", t["status_progress_title"], bar, ""]

    slot = 1
    for friend in verified:
        label = friend.get("full_name") or friend.get("username") or f"#{slot}"
        lines.append(t["status_verified"].format(n=slot, label=label))
        slot += 1

    for friend in pending:
        label = friend.get("full_name") or friend.get("username") or f"#{slot}"
        lines.append(t["status_pending"].format(n=slot, label=label))
        slot += 1

    while slot <= REQUIRED_REFERRALS:
        lines.append(t["status_waiting"].format(n=slot))
        slot += 1

    remaining = max(REQUIRED_REFERRALS - referral_count, 0)
    if remaining:
        s = "" if lang == "uz" else ("s" if remaining != 1 else "")
        lines.extend([
            "",
            t["status_need_more"].format(n=remaining, s=s),
            "",
            t["status_channel_note"],
        ])
    else:
        lines.extend(["", t["status_complete"]])

    return "\n".join(lines)


def format_channels_step(lang: str = "uz") -> str:
    return T[lang]["channels_step"]


def format_almost_there(missing_names: list[str], lang: str = "uz") -> str:
    t = T[lang]
    if len(missing_names) == 1:
        ch = missing_names[0]
        return t["almost_there_single"].format(ch=ch)
    else:
        ch = ", ".join(f"<b>{n}</b>" for n in missing_names)
        return t["almost_there_multi"].format(ch=ch)


def format_unlock_success(access_link: str, lang: str = "uz") -> str:
    return T[lang]["unlock_success"].format(n=REQUIRED_REFERRALS, link=access_link)


def format_access_link_resend(access_link: str, lang: str = "uz") -> str:
    return T[lang]["access_link_resend"].format(link=access_link)


def format_post_reward_funnel(lang: str = "uz") -> str:
    return T[lang]["post_reward"]


async def deliver_reward(bot, telegram_id: int) -> bool:
    user = await db.get_user(telegram_id)
    if not user:
        return False

    lang = get_lang(user)
    referral_count = user.get("referral_count", 0)
    if referral_count < REQUIRED_REFERRALS:
        return False

    if user.get("reward_sent") and user.get("reward_access_link"):
        from aiogram.exceptions import TelegramAPIError
        try:
            await bot.send_message(
                telegram_id,
                format_access_link_resend(user["reward_access_link"], lang=lang),
            )
        except TelegramAPIError:
            return False
        return True

    if user.get("reward_sent"):
        return False

    access_link = await create_unique_reward_link(bot, telegram_id)
    if not access_link:
        return False

    from aiogram.exceptions import TelegramAPIError

    try:
        await bot.send_message(telegram_id, format_unlock_success(access_link, lang=lang))
    except TelegramAPIError:
        return False

    await db.update_user(
        telegram_id,
        reward_sent=1,
        file_unlocked=1,
        reward_access_link=access_link,
    )

    from keyboards import post_reward_keyboard

    try:
        await bot.send_message(
            telegram_id,
            format_post_reward_funnel(lang=lang),
            reply_markup=post_reward_keyboard(lang=lang),
        )
    except TelegramAPIError:
        pass

    return True
