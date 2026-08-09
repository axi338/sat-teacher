import asyncio
import csv
import os
import sys

# Auto-configure PythonAnywhere HTTP proxy for free tier
if os.path.exists("/etc/pythonanywhere") or os.getenv("PYTHONANYWHERE_SITE"):
    _pa_proxy = "http://proxy.server:3128"
    os.environ["HTTP_PROXY"] = _pa_proxy
    os.environ["HTTPS_PROXY"] = _pa_proxy
    os.environ["http_proxy"] = _pa_proxy
    os.environ["https_proxy"] = _pa_proxy


from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN

# 1. Configuration
CSV_FILE_PATH = "users.csv"  # Name of your CSV file

MESSAGE_TEXT = (
    "🎁 $1000 qiymatidagi SAT kursini mutlaqo BEPUL qo'lga kiritish imkoniyati! ❤️🔥\n\n"
    "SAT Valley eng katta Giveaway'ni boshladi! 🚀\n"
    "Sizni nimalar kutmoqda?\n\n"
    "📚 $1000+ qiymatidagi SAT Math & English video darslari — mutlaqo bepul.\n"
    "🏆 Asosiy sovg'a:\n"
    "👨‍🏫 Humoyunbek Mirzayev bilan 1 oylik individual mentorlik (qiymati — $1000).\n\n"
    "🎁 TOP 3 ishtirokchiga:\n"
    "📱 Telegram Premium\n"
    "📚 Mutolaa Premium\n\n"
    "📌 Ishtirok etish juda oson:\n"
    "✅ 2 ta kanalga obuna bo'ling.\n"
    "✅ Do'stlaringizni taklif qiling.\n\n"
    "🔥 Eng ko'p do'st taklif qilgan ishtirokchi asosiy sovg'ani qo'lga kiritadi!\n"
    "👇 Hoziroq ishtirok eting:"
)

# 2. Keyboard Definition
# This attaches the exact "Start" button that triggers the bot's registration flow
reply_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Ishtirok etish / Start", callback_data="participate"
            )
        ]
    ]
)

async def main():
    bot_token = BOT_TOKEN
    
    if not bot_token:
        print("❌ Error: BOT_TOKEN topilmadi.")
        return

    session = None
    proxy_url = os.getenv("PROXY_URL") or os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    if not proxy_url and (os.path.exists("/etc/pythonanywhere") or os.getenv("PYTHONANYWHERE_SITE")):
        proxy_url = "http://proxy.server:3128"

    if proxy_url:
        from aiogram.client.session.aiohttp import AiohttpSession
        session = AiohttpSession(proxy=proxy_url)

    # Initialize Bot
    bot = Bot(
        token=bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


    # Read CSV
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ Error: {CSV_FILE_PATH} fayli topilmadi.")
        await bot.session.close()
        return

    with open(CSV_FILE_PATH, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        users = list(reader)

    print(f"📥 Jami o'qilgan foydalanuvchilar: {len(users)}")
    
    success_count = 0
    fail_count = 0

    print("🚀 Broadcast boshlandi...")

    # Broadcast Loop with Rate-Limiting
    for index, row in enumerate(users):
        telegram_id = row.get("telegram_id")
        
        if not telegram_id or not telegram_id.isdigit():
            continue

        try:
            # Send message with the attached keyboard
            await bot.send_message(
                chat_id=int(telegram_id), 
                text=MESSAGE_TEXT,
                reply_markup=reply_keyboard
            )
            success_count += 1
            print(f"[{index + 1}/{len(users)}] ✅ Yuborildi: {telegram_id}")
            
            # Rate limiting delay (~20 msgs per sec safe limit)
            await asyncio.sleep(0.05)
            
        except TelegramRetryAfter as e:
            print(f"[{index + 1}/{len(users)}] ⏳ Rate limit: {e.retry_after} soniya kutilmoqda...")
            await asyncio.sleep(e.retry_after)
            try:
                await bot.send_message(
                    chat_id=int(telegram_id), 
                    text=MESSAGE_TEXT,
                    reply_markup=reply_keyboard
                )
                success_count += 1
                print(f"[{index + 1}/{len(users)}] ✅ Yuborildi (Kutishdan so'ng): {telegram_id}")
            except Exception as inner_e:
                fail_count += 1
                print(f"[{index + 1}/{len(users)}] ❌ Xatolik: {telegram_id} - {inner_e}")
                
        except TelegramAPIError as e:
            fail_count += 1
            print(f"[{index + 1}/{len(users)}] ❌ Telegram xatosi: {telegram_id} - {e.message}")
        except Exception as e:
            fail_count += 1
            print(f"[{index + 1}/{len(users)}] ❌ Noma'lum xato: {telegram_id} - {e}")

    await bot.session.close()
    print("\n--- 🏁 Broadcast Yakunlandi ---")
    print(f"✅ Muvaffaqiyatli: {success_count}")
    print(f"❌ Xatoliklar: {fail_count}")

if __name__ == "__main__":
    asyncio.run(main())
