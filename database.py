import aiosqlite
from datetime import datetime, timezone
from typing import Any

from config import DATABASE_PATH


async def init_db() -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT,
                username TEXT,
                joined_at TEXT NOT NULL,
                invited_by INTEGER,
                referral_count INTEGER DEFAULT 0,
                channels_joined INTEGER DEFAULT 0,
                file_unlocked INTEGER DEFAULT 0,
                referral_credited INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inviter_id INTEGER NOT NULL,
                invited_user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(inviter_id, invited_user_id)
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            """
        )
        # Auto-migrate table if referral_credited column missing
        async with db.execute("PRAGMA table_info(users)") as cursor:
            rows = await cursor.fetchall()
            columns = [row[1] for row in rows]
            if "referral_credited" not in columns:
                await db.execute("ALTER TABLE users ADD COLUMN referral_credited INTEGER DEFAULT 0;")
        await db.commit()


async def get_user(telegram_id: int) -> dict[str, Any] | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def create_user(
    telegram_id: int,
    full_name: str | None,
    username: str | None,
    invited_by: int | None = None,
) -> dict[str, Any]:
    joined_at = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users
            (telegram_id, full_name, username, joined_at, invited_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (telegram_id, full_name, username, joined_at, invited_by),
        )
        await db.commit()
    user = await get_user(telegram_id)
    if user is None:
        user = {
            "telegram_id": telegram_id,
            "full_name": full_name,
            "username": username,
            "joined_at": joined_at,
            "invited_by": invited_by,
            "referral_count": 0,
            "channels_joined": 0,
            "file_unlocked": 0,
        }
    return user



async def update_user(telegram_id: int, **fields: Any) -> None:
    if not fields:
        return
    columns = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [telegram_id]
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            f"UPDATE users SET {columns} WHERE telegram_id = ?", values
        )
        await db.commit()


async def add_referral(inviter_id: int, invited_user_id: int) -> bool:
    """Returns True if referral was newly recorded."""
    if inviter_id == invited_user_id:
        return False

    created_at = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            await db.execute(
                """
                INSERT INTO referrals (inviter_id, invited_user_id, created_at)
                VALUES (?, ?, ?)
                """,
                (inviter_id, invited_user_id, created_at),
            )
            await db.execute(
                """
                UPDATE users SET referral_count = referral_count + 1
                WHERE telegram_id = ?
                """,
                (inviter_id,),
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def credit_referral(inviter_id: int, invited_user_id: int) -> tuple[bool, int]:
    """
    Credits a referral to inviter_id for invited_user_id if not already credited.
    Returns (credited: bool, new_referral_count: int).
    """
    if inviter_id == invited_user_id:
        inviter = await get_user(inviter_id)
        return False, inviter.get("referral_count", 0) if inviter else 0

    invited_user = await get_user(invited_user_id)
    if not invited_user or invited_user.get("referral_credited"):
        inviter = await get_user(inviter_id)
        return False, inviter.get("referral_count", 0) if inviter else 0

    created_at = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET referral_credited = 1 WHERE telegram_id = ?",
            (invited_user_id,),
        )
        try:
            await db.execute(
                """
                INSERT INTO referrals (inviter_id, invited_user_id, created_at)
                VALUES (?, ?, ?)
                """,
                (inviter_id, invited_user_id, created_at),
            )
        except aiosqlite.IntegrityError:
            pass

        await db.execute(
            "UPDATE users SET referral_count = referral_count + 1 WHERE telegram_id = ?",
            (inviter_id,),
        )
        await db.commit()

        async with db.execute(
            "SELECT referral_count FROM users WHERE telegram_id = ?", (inviter_id,)
        ) as cursor:
            row = await cursor.fetchone()
            count = row[0] if row else 0

    return True, count


async def referral_exists(inviter_id: int, invited_user_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            """
            SELECT 1 FROM referrals
            WHERE inviter_id = ? AND invited_user_id = ?
            """,
            (inviter_id, invited_user_id),
        ) as cursor:
            return await cursor.fetchone() is not None


async def get_setting(key: str) -> str | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def set_setting(key: str, value: str) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        await db.commit()


async def get_all_users() -> list[dict[str, Any]]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY joined_at") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def search_user(query: str) -> dict[str, Any] | None:
    query = query.strip().lstrip("@")
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        if query.isdigit():
            async with db.execute(
                "SELECT * FROM users WHERE telegram_id = ?", (int(query),)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        async with db.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)" , (query,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_campaign_stats() -> dict[str, int]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        stats: dict[str, int] = {}

        async with db.execute("SELECT COUNT(*) FROM users") as c:
            stats["total_users"] = (await c.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE channels_joined = 1"
        ) as c:
            stats["joined_channels"] = (await c.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE referral_count = 1"
        ) as c:
            stats["users_with_1_referral"] = (await c.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE referral_count = 2"
        ) as c:
            stats["users_with_2_referrals"] = (await c.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE referral_count >= 1"
        ) as c:
            stats["users_with_referrals"] = (await c.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE referral_count >= 3"
        ) as c:
            stats["users_with_3_referrals"] = (await c.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE file_unlocked = 1"
        ) as c:
            stats["file_unlocked"] = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM referrals") as c:
            stats["total_referrals"] = (await c.fetchone())[0]
        return stats


async def get_top_referrers(limit: int = 20) -> list[dict[str, Any]]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT full_name, username, referral_count FROM users ORDER BY referral_count DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_user_rank(telegram_id: int) -> tuple[int, int]:
    """Returns (rank, referral_count) for the given user. Rank is 1-based."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            """
            SELECT COUNT(*) + 1 FROM users
            WHERE referral_count > (SELECT referral_count FROM users WHERE telegram_id = ?)
            """,
            (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            rank = row[0] if row else 1
        async with db.execute(
            "SELECT referral_count FROM users WHERE telegram_id = ?",
            (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            count = row[0] if row else 0
    return rank, count


async def get_next_rank_needed(telegram_id: int) -> int:
    rank, count = await get_user_rank(telegram_id)
    if rank <= 1:
        return 0
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            """
            SELECT MIN(referral_count) FROM users
            WHERE referral_count > ?
            """,
            (count,)
        ) as cursor:
            row = await cursor.fetchone()
            next_count = row[0] if row and row[0] is not None else None
            if next_count is None:
                return 1
            return max(1, (next_count - count) + 1)


