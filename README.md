# Humoyunbek Mirzayev — SAT Teacher Telegram Bot

Official Telegram bot for **Humoyunbek Mirzayev** SAT students. Students join channels, invite friends, and unlock the exclusive **JUNE SAT Predictions File**.

## Features

- Welcome flow with active event (JUNE SAT Predictions)
- Channel subscription verification (2 channels)
- Referral system (3 valid `/start` invites)
- Progress tracking and file unlock
- Full admin panel (stats, broadcast, file upload, search, export)
- SQLite database

## Project structure

```
sat_teacher_bot/
├── main.py
├── config.py
├── database.py
├── keyboards.py
├── requirements.txt
├── .env.example
├── README.md
├── handlers/
│   ├── start.py
│   ├── user.py
│   ├── admin.py
│   └── callbacks.py
├── services/
│   ├── channel_checker.py
│   ├── referral_service.py
│   ├── file_service.py
│   └── export_service.py
└── data/
    └── bot.db          (created on first run)
```

## Deployment & Quick Start

Credentials are pre-configured in `config.py` so the bot can be deployed immediately without creating environment files.

### Option 1: Direct Python Execution
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
python main.py
```

### Option 2: Docker / Docker Compose (Recommended for Production)
```bash
docker compose up -d
```
The Docker setup automatically persists SQLite data under `./data/bot.db`.

Edit `.env`:

```env
BOT_TOKEN=123456:ABC-DEF...
BOT_USERNAME=humoyunbek_sat_bot
ADMIN_IDS=your_telegram_id,another_admin_id
CHANNEL_1_ID=-1001234567890
CHANNEL_1_LINK=https://t.me/your_channel_1
CHANNEL_2_ID=-1001234567891
CHANNEL_2_LINK=https://t.me/your_channel_2
```

### Admin IDs

- Get your ID from [@userinfobot](https://t.me/userinfobot) or [@getidsbot](https://t.me/getidsbot).
- Separate multiple admins with commas: `111111,222222`.

### Channel IDs and links

1. Create or use two Telegram channels for SAT updates.
2. **Add your bot as an administrator** in both channels (required for subscription checks).
3. Channel ID:
   - Forward a channel post to [@getidsbot](https://t.me/getidsbot), or
   - Use `@RawDataBot` on a forwarded message.
   - Private channels usually look like `-1001234567890`.
4. Set `CHANNEL_1_LINK` / `CHANNEL_2_LINK` to public invite links (`https://t.me/...`).

## 4. Run the bot

```bash
cd sat_teacher_bot
python main.py
```

You should see `Bot started. Polling...` in the console.

## 5. Upload the predictions file (admin)

1. Send `/admin` from an admin account.
2. Tap **📁 Upload Predictions File**.
3. Send the PDF (or document) when prompted.
4. The bot stores Telegram `file_id` in the database; unlocked users receive this file.

## 6. User commands

| Command    | Description              |
|-----------|--------------------------|
| `/start`  | Register and main menu   |
| `/progress` | Check unlock progress |
| `/link`   | Personal referral link |
| `/admin`  | Admin panel (admins only) |
| `/data`   | User list / export (admins only) |

## Referral system

Each user gets a link:

```text
https://t.me/BOT_USERNAME?start=USER_TELEGRAM_ID
```

Rules:

- Friend must open the bot via **your** link and press **START**.
- Each invited user counts **once** (no duplicates).
- **Self-referral** is blocked.
- Only **new** users who press `/start` for the first time count.

## Unlock requirements

1. Join **both** required channels (verify with **✅ Check Subscription**).
2. Invite **3** friends via your referral link.
3. Tap **🔓 Unlock Predictions File**.

## Admin panel

| Button | Action |
|--------|--------|
| 👥 Total Users | User count |
| 📊 Campaign Stats | Funnel statistics |
| 📤 Broadcast Message | Message all users |
| 📁 Upload Predictions File | Set unlock document |
| 🔍 Search User | By ID or @username |
| 📥 Export User Data | CSV download |
| ⚙️ Event Settings | Current event info |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Subscription check always fails | Bot must be **admin** in both channels; check `CHANNEL_*_ID` |
| File unlock says not available | Upload file via admin panel first |
| Referrals not counting | Friend must use your link and press START as a **new** user |
| `BOT_TOKEN is not set` | Create `.env` from `.env.example` |

## Tech stack

- Python 3.10+
- [aiogram](https://docs.aiogram.dev/) 3.x
- SQLite (aiosqlite)
- python-dotenv
- openpyxl (export support)

## License

Private project for Humoyunbek Mirzayev SAT community.
