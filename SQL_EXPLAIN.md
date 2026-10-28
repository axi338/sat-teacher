**Schema Overview**

- **`users`**: stores each Telegram user tracked by the bot.
  - Columns: `id`, `telegram_id` (unique), `full_name`, `username`, `joined_at`, `invited_by`, `referral_count`, `channels_joined`, `file_unlocked`, `referral_credited`, `reward_sent`, `reward_access_link`.
  - Indexes: `idx_users_telegram_id`, `idx_users_invited_by` for common lookups.

- **`referrals`**: records referral relationships. `inviter_id` and `invited_user_id` map to `users.telegram_id`.
  - Unique constraint prevents duplicate referrals between same pair.

- **`settings`**: key/value store for files and runtime settings (e.g., predictions file metadata).

**How `database.py` uses the schema**

- `init_db()` now prefers loading `schema.sql` (next to `database.py`) and runs it with `db.executescript()`.
- If `schema.sql` is missing, `init_db()` falls back to the previously embedded SQL so startup remains backwards compatible.
- Auto-migration: `init_db()` still checks `PRAGMA table_info(users)` and will add missing columns like `referral_credited`, `reward_sent`, or `reward_access_link` to avoid breaking existing deployments.

**Maintenance notes**

- To change the DB layout, edit `schema.sql` then restart the bot. `init_db()` will create missing tables.
- For destructive changes (dropping columns), perform a migration outside the automated path (dump/restore or ALTER with temp tables).
- To inspect the DB manually (SQLite file at `DATABASE_PATH` per `config.py`):

```bash
sqlite3 path/to/database.db
sqlite> .tables
sqlite> PRAGMA table_info(users);
```
