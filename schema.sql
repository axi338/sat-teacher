PRAGMA foreign_keys = ON;

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
    referral_credited INTEGER DEFAULT 0,
    reward_sent INTEGER DEFAULT 0,
    reward_access_link TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_invited_by ON users(invited_by);

CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inviter_id INTEGER NOT NULL,
    invited_user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(inviter_id, invited_user_id),
    FOREIGN KEY(inviter_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
    FOREIGN KEY(invited_user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
