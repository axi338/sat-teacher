from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import database as db
from keyboards import welcome_keyboard
from services.referral_service import process_referral_start

router = Router()

WELCOME_TEXT = (
    "🎁 **Want the SAT Math Prediction file?**\n\n"
    "This file includes high-value SAT Math predictions & practice materials to boost your score! 🚀\n\n"
    "Invite 3 friends to get it for free! 👇"
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



