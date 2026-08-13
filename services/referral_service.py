from aiogram import Bot

import database as db
from config import BOT_USERNAME, REQUIRED_REFERRALS
from services.channel_checker import check_all_channels


def build_referral_link(telegram_id: int) -> str:
    username = BOT_USERNAME or "your_bot"
    return f"https://t.me/{username}?start=ref_{telegram_id}"


def parse_referral_payload(start_payload: str | None) -> int | None:
    if not start_payload:
        return None
    raw = start_payload.strip()
    if raw.startswith("ref_"):
        raw = raw[4:]
    if raw.isdigit():
        return int(raw)
    return None


async def process_referral_start(
    new_user_id: int,
    start_payload: str | None,
) -> int | None:
    """
    Process referral from /start payload.
    Parses payload and returns inviter_id if valid and not a self-referral.
    Does NOT credit inviter immediately — crediting happens after 3-channel verification.
    """
    inviter_id = parse_referral_payload(start_payload)
    if not inviter_id or inviter_id == new_user_id:
        return None

    inviter = await db.get_user(inviter_id)
    if not inviter:
        return None

    return inviter_id


async def check_and_credit_referral(bot: Bot, user_id: int) -> bool:
    """
    Checks if user_id has joined all 3 channels.
    If joined and user has an uncredited inviter, credits the inviter and notifies them.
    Auto-delivers prediction PDF to inviter when they reach REQUIRED_REFERRALS.
    Returns True if a referral was newly credited.
    """
    user = await db.get_user(user_id)
    if not user or not user.get("invited_by") or user.get("referral_credited"):
        return False

    inviter_id = user["invited_by"]
    channels_ok = await check_all_channels(bot, user_id)
    if not channels_ok:
        return False

    credited, new_count = await db.credit_referral(inviter_id, user_id)
    if credited:
        try:
            await bot.send_message(
                inviter_id,
                f"🎉 **New friend added!** You now have **{new_count}/{REQUIRED_REFERRALS}** invites."
            )
        except Exception:
            pass

        if new_count >= REQUIRED_REFERRALS:
            inviter = await db.get_user(inviter_id)
            if inviter and not inviter.get("file_unlocked"):
                await db.update_user(inviter_id, file_unlocked=1)
                file_id = await db.get_setting("predictions_file_id")
                try:
                    await bot.send_message(
                        inviter_id,
                        "🎉 **Congratulations! You've invited 3 friends.**\n\n"
                        "📎 Here is your **SAT Math Prediction** file:"
                    )
                    if file_id:
                        await bot.send_document(inviter_id, file_id)
                    else:
                        await bot.send_message(
                            inviter_id,
                            "ℹ️ Your file is ready! Use the /start command or click **Sovg'ani olish** in the bot menu."
                        )
                except Exception:
                    pass
        return True

    return False


def referrals_complete(referral_count: int) -> bool:
    return referral_count >= REQUIRED_REFERRALS


async def build_leaderboard_text(user_id: int) -> str:
    top_users = await db.get_top_referrers(20)
    user_rank, user_count = await db.get_user_rank(user_id)
    needed = await db.get_next_rank_needed(user_id)

    lines = [
        "🏆 <b>Leaderboard (Top 20 Referrers)</b>\n",
        "📊 <b>Participants with the most successful invites</b>\n",
    ]

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    if not top_users:
        lines.append("<i>No participants yet. Be the first to invite your friends!</i>")
    else:
        for i, u in enumerate(top_users, start=1):
            name = u.get("full_name") or (f"@{u['username']}" if u.get("username") else "Participant")
            count = u.get("referral_count", 0)
            prefix = medals.get(i, f"{i}.")
            lines.append(f"{prefix} {name} — <b>{count}</b> invites")

    lines.append("\n━━━━━━━━━━━━━━\n")
    lines.append(f"👤 Your rank: <b>#{user_rank}</b>")
    lines.append(f"📨 Your invites: <b>{user_count}</b>")

    if user_rank == 1 and user_count > 0:
        lines.append("🎯 You are #1 in the leaderboard! 🎉")
    else:
        lines.append(f"🎯 Invites needed to reach next rank: <b>{needed}</b>")

    lines.append("\n🚀 Invite friends using your referral link to win rewards!")

    return "\n".join(lines)


