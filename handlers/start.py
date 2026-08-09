from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import database as db
from keyboards import welcome_keyboard
from services.referral_service import process_referral_start, build_referral_link

router = Router()

WELCOME_TEXT = (
    "🎁 $1000 qiymatidagi SAT kursini mutlaqo BEPUL qo'lga kiritish imkoniyati! ❤️🔥\n\n"
    "SAT Valley eng katta sovrin o'yinini boshladi! 🚀\n"
    "Sizni nimalar kutmoqda?\n\n"
    "📚 $1000+ qiymatidagi SAT Math & English video darslari — mutlaqo bepul.\n"
    "🏆 Asosiy sovg'a:\n"
    "👨‍🏫 Humoyunbek Mirzayev bilan 1 oylik individual mentorlik (qiymati — $1000).\n\n"
    "🎁 TOP 3 ishtirokchiga:\n"
    "📱 Telegram Premium\n"
    "📚 Mutolaa Premium\n\n"
    "📌 Ishtirok etish juda oson:\n"
    "✅ 2 ta kanalga obuna bo'ling.\n"
    "✅ Ishtirokchilarni taklif qiling.\n\n"
    "🔥 Eng ko'p ishtirokchi taklif qilgan ishtirokchi asosiy sovg'ani qo'lga kiritadi!\n"
    "👇 Hoziroq ishtirok eting:"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = message.from_user
    if not user:
        return

    telegram_id = user.id
    full_name = user.full_name
    username = user.username

    existing = await db.get_user(telegram_id)
    is_new = existing is None

    if is_new:
        invited_by: int | None = None
        payload = None
        if message.text and len(message.text.split()) > 1:
            payload = message.text.split(maxsplit=1)[1].strip()

        await db.create_user(telegram_id, full_name, username, invited_by=None)
        inviter_id = await process_referral_start(telegram_id, payload)
        if inviter_id:
            await db.update_user(telegram_id, invited_by=inviter_id)
    else:
        await db.update_user(
            telegram_id,
            full_name=full_name,
            username=username,
        )

    await message.answer(WELCOME_TEXT, reply_markup=welcome_keyboard())


