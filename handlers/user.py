from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import database as db
from keyboards import dashboard_keyboard, status_keyboard, unlock_keyboard
from config import REQUIRED_REFERRALS
from services import file_service
from services.referral_service import build_referral_link

router = Router()


@router.message(Command("progress"))
async def cmd_progress(message: Message) -> None:
    user = message.from_user
    if not user:
        return

    db_user = await db.get_user(user.id)
    if not db_user:
        await message.answer("Please send /start first.")
        return

    text = await file_service.format_referral_status(user.id)
    count = db_user.get("referral_count", 0)
    kb = unlock_keyboard() if count >= REQUIRED_REFERRALS else status_keyboard(user.id)
    await message.answer(text, reply_markup=kb)


@router.message(Command("link"))
async def cmd_link(message: Message) -> None:
    user = message.from_user
    if not user:
        return

    db_user = await db.get_user(user.id)
    if not db_user:
        await message.answer("Please send /start first.")
        return

    link = build_referral_link(user.id)
    count = db_user.get("referral_count", 0)
    await message.answer(
        file_service.format_dashboard(user.id, link, count),
        reply_markup=dashboard_keyboard(user.id),
    )
