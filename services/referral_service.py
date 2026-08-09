from aiogram import Bot

import database as db
from config import BOT_USERNAME, REQUIRED_REFERRALS


def build_referral_link(telegram_id: int) -> str:
    username = BOT_USERNAME or "your_bot"
    return f"https://t.me/{username}?start={telegram_id}"


async def process_referral_start(
    new_user_id: int,
    start_payload: str | None,
) -> int | None:
    """
    Process referral from /start payload.
    Returns inviter_id if referral was recorded, else None.
    """
    if not start_payload or not start_payload.isdigit():
        return None

    inviter_id = int(start_payload)
    if inviter_id == new_user_id:
        return None

    inviter = await db.get_user(inviter_id)
    if not inviter:
        return None

    if await db.referral_exists(inviter_id, new_user_id):
        return None

    recorded = await db.add_referral(inviter_id, new_user_id)
    return inviter_id if recorded else None


def referrals_complete(referral_count: int) -> bool:
    return referral_count >= REQUIRED_REFERRALS


async def build_leaderboard_text(user_id: int) -> str:
    top_users = await db.get_top_referrers(20)
    user_rank, user_count = await db.get_user_rank(user_id)
    needed = await db.get_next_rank_needed(user_id)

    lines = [
        "🏆 <b>Marafon Liderlari</b>\n",
        "📊 <b>Eng ko‘p ishtirokchi taklif qilgan TOP 20 ishtirokchi</b>\n",
    ]

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    if not top_users:
        lines.append("<i>Hozircha ishtirokchilar yo'q. Birinchi bo'lib taklif qiling!</i>")
    else:
        for i, u in enumerate(top_users, start=1):
            name = u.get("full_name") or (f"@{u['username']}" if u.get("username") else "Ishtirokchi")
            count = u.get("referral_count", 0)
            prefix = medals.get(i, f"{i}.")
            lines.append(f"{prefix} {name} — <b>{count}</b> ta muvaffaqiyatli taklif")

    lines.append("\n━━━━━━━━━━━━━━\n")
    lines.append(f"👤 Sizning o‘rningiz: <b>#{user_rank}</b>")
    lines.append(f"📨 Takliflar soni: <b>{user_count}</b> ta")

    if user_rank == 1 and user_count > 0:
        lines.append("🎯 Siz marafonda 1-o‘rindasiz! 🎉")
    else:
        lines.append(f"🎯 Keyingi o‘ringa chiqish uchun: <b>{needed}</b> ta taklif kerak")

    lines.append("\n🚀 Do‘stlaringizni marafonga taklif qiling va sovrinlar uchun kurashing!")

    return "\n".join(lines)

