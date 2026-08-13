from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import database as db
from keyboards import dashboard_keyboard, referred_welcome_keyboard, welcome_keyboard
from services.referral_service import build_referral_link, process_referral_start

router = Router()

WELCOME_TEXT = (
    "<b>SAT Valley | Math Prediction</b>\n\n"
    "🎯 <b>Want the SAT Math Prediction file?</b>\n\n"
    "Get our <b>SAT Math Prediction</b> and use it as part of your SAT preparation.\n\n"
    "<b>It's free — just invite 3 friends.</b>\n\n"
    "<b>How it works:</b>\n\n"
    "1️⃣ Share your personal invite link\n"
    "2️⃣ Your friend opens the bot and joins all 3 SAT Valley channels\n"
    "3️⃣ After 3 friends complete the process, <b>your file unlocks automatically 🎉</b>\n\n"
    "Ready?"
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

        inviter_id = await process_referral_start(telegram_id, payload)
        await db.create_user(telegram_id, full_name, username, invited_by=inviter_id)

        await message.answer(WELCOME_TEXT, reply_markup=welcome_keyboard())

        if inviter_id:
            await message.answer(
                "👋 You've been invited to help unlock the SAT Math Prediction!\n\n"
                "Join all 3 SAT Valley channels below — once verified, your friend gets credit.",
                reply_markup=referred_welcome_keyboard(),
            )
        return

    await db.update_user(telegram_id, full_name=full_name, username=username)
    await message.answer(WELCOME_TEXT, reply_markup=welcome_keyboard())

    db_user = await db.get_user(telegram_id)
    if db_user:
        link = build_referral_link(telegram_id)
        count = db_user.get("referral_count", 0)
        from services.file_service import format_dashboard

        await message.answer(
            format_dashboard(telegram_id, link, count),
            reply_markup=dashboard_keyboard(telegram_id),
        )
