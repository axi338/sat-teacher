from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import database as db
from config import REQUIRED_REFERRALS
from keyboards import channels_keyboard, main_menu_keyboard, referral_keyboard
from services import file_service
from services.referral_service import build_leaderboard_text, build_referral_link


router = Router()


@router.message(Command("progress"))
async def cmd_progress(message: Message) -> None:
    user = message.from_user
    if not user:
        return

    db_user = await db.get_user(user.id)
    if not db_user:
        await message.answer("Iltimos, avval /start buyrug'ini yuboring.")
        return

    channels_ok, referrals_ok, referral_count = await file_service.user_can_unlock(
        message.bot, db_user
    )
    db_user = await db.get_user(user.id) or db_user
    file_unlocked = bool(db_user.get("file_unlocked"))

    if channels_ok and referrals_ok:
        invite_link = await file_service.get_target_invite_link(message.bot)
        await message.answer(
            "🎉 **Tabriklaymiz! Barcha shartlarni muvaffaqiyatli bajardingiz!**\n\n"
            f"Sizning kirish havolangiz: {invite_link}",
            reply_markup=referral_keyboard(),
        )
        return

    text = file_service.format_progress(
        channels_ok, referral_count, file_unlocked
    )
    await message.answer(
        text, 
        reply_markup=referral_keyboard() if channels_ok else channels_keyboard()
    )


@router.message(Command("link"))
async def cmd_link(message: Message) -> None:
    user = message.from_user
    if not user:
        return

    db_user = await db.get_user(user.id)
    if not db_user:
        await message.answer("Iltimos, avval /start buyrug'ini yuboring.")
        return

    link = build_referral_link(user.id)
    await message.answer(
        f"🚨 SAT'dan 1500+ olishni xohlaysizmi?\n"
        f"🎁 $1000+ qiymatidagi SAT darsliklari — BEPUL!\n"
        f"🏆 $1000 qiymatidagi Humoyunbek Mirzayev bilan individual mentorlik!\n"
        f"📱 TOP 3 — Telegram Premium + Mutolaa Premium.\n"
        f"🔥 G'olib — eng ko'p do'st taklif qilgan ishtirokchi!\n\n"
        f"👇 Hoziroq qatnashing:\n"
        f"{link}",
        reply_markup=referral_keyboard(),
    )

@router.message(Command(commands=["winners", "ranking"]))
async def cmd_winners(message: Message) -> None:
    user = message.from_user
    if not user:
        return
    text = await build_leaderboard_text(user.id)
    await message.answer(text, reply_markup=main_menu_keyboard())

