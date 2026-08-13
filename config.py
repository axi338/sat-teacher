import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")


def get_env(key: str, default: str) -> str:
    val = os.getenv(key)
    if val is not None and val.strip():
        return val.strip()
    return default


# Production credentials with optional environment override
BOT_TOKEN = get_env("BOT_TOKEN", "8734653611:AAHBZVSFQ5R_GDSHxu_AYHv86ngKX9GC1GE")
BOT_USERNAME = get_env("BOT_USERNAME", "HumoyunbekMirzayev_bot")

admin_ids_raw = get_env("ADMIN_IDS", "5129658601")
ADMIN_IDS = [int(i.strip()) for i in admin_ids_raw.split(",") if i.strip().isdigit()]
if not ADMIN_IDS:
    ADMIN_IDS = [5129658601]

# Required Channels (3 channels per Technical Specification)
CHANNEL_1_ID = get_env("CHANNEL_1_ID", "-1002892459172")
CHANNEL_2_ID = get_env("CHANNEL_2_ID", "-1002574308633")
CHANNEL_3_ID = get_env("CHANNEL_3_ID", "@DesmosBootcamp")

CHANNEL_1_LINK = get_env("CHANNEL_1_LINK", "https://t.me/sat_humoyunbek")
CHANNEL_2_LINK = get_env("CHANNEL_2_LINK", "https://t.me/sat_valley")
CHANNEL_3_LINK = get_env("CHANNEL_3_LINK", "https://t.me/DesmosBootcamp")

CHANNELS = [c for c in [CHANNEL_1_ID, CHANNEL_2_ID, CHANNEL_3_ID] if c]
CHANNEL_LINKS = [l for l in [CHANNEL_1_LINK, CHANNEL_2_LINK, CHANNEL_3_LINK] if l]

DATABASE_PATH = DATA_DIR / "bot.db"

req_ref_str = get_env("REQUIRED_REFERRALS", "3")
REQUIRED_REFERRALS = int(req_ref_str) if req_ref_str.isdigit() else 3

PREDICTIONS_FILE_KEY = "predictions_file_id"
TARGET_CHANNEL_LINK = get_env("TARGET_CHANNEL_LINK", "https://t.me/sat_valley")
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID", "").strip()

