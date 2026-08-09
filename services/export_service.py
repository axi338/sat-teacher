import csv
import io
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook

import database as db


def _user_rows(users: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "telegram_id": u["telegram_id"],
            "full_name": u.get("full_name") or "",
            "username": u.get("username") or "",
            "joined_at": u.get("joined_at") or "",
            "invited_by": u.get("invited_by") or "",
            "referral_count": u.get("referral_count", 0),
            "channels_joined": "Yes" if u.get("channels_joined") else "No",
            "file_unlocked": "Yes" if u.get("file_unlocked") else "No",
        }
        for u in users
    ]


FIELDNAMES = [
    "telegram_id",
    "full_name",
    "username",
    "joined_at",
    "invited_by",
    "referral_count",
    "channels_joined",
    "file_unlocked",
]


async def export_users_csv() -> bytes:
    users = await db.get_all_users()
    rows = _user_rows(users)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig")


async def export_users_xlsx() -> bytes:
    users = await db.get_all_users()
    rows = _user_rows(users)
    wb = Workbook()
    ws = wb.active
    ws.title = "Users"
    ws.append(FIELDNAMES)
    for row in rows:
        ws.append([row[f] for f in FIELDNAMES])
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def format_user_info(user: dict[str, Any]) -> str:
    channels = "Yes" if user.get("channels_joined") else "No"
    unlocked = "Yes" if user.get("file_unlocked") else "No"
    username = user.get("username")
    username_display = f"@{username}" if username else "—"
    invited_by = user.get("invited_by") or "—"
    return (
        f"👤 User info\n\n"
        f"Full name: {user.get('full_name') or '—'}\n"
        f"Username: {username_display}\n"
        f"Telegram ID: {user['telegram_id']}\n"
        f"Joined: {user.get('joined_at', '—')}\n"
        f"Invited by: {invited_by}\n"
        f"Referral count: {user.get('referral_count', 0)}\n"
        f"Channels joined: {channels}\n"
        f"File unlocked: {unlocked}"
    )
