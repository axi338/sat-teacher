from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import database as db
from keyboards import language_keyboard, welcome_keyboard
from services.referral_service import process_referral_start
from translations import T, get_lang

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = message.from_user
    if not user:
        return

    telegram_id = user.id
    full_name   = user.full_name
    username    = user.username

    existing = await db.get_user(telegram_id)

    # ── Returning user — skip language picker, show welcome directly ──────
    if existing and existing.get("lang"):
        await db.update_user(telegram_id, full_name=full_name, username=username)
        lang = get_lang(existing)
        await message.answer(T[lang]["welcome"], reply_markup=welcome_keyboard(lang=lang))
        return

    # ── Brand-new user (or user with no lang set yet) — store referral
    #    payload in FSM-free way: we create the user record now but with
    #    no lang, then the language callback will set it and send welcome.
    #    We persist the referral payload via a temp DB setting keyed by user id.
    payload = None
    if message.text and len(message.text.split()) > 1:
        payload = message.text.split(maxsplit=1)[1].strip()

    # Store referral payload temporarily so the language callback can use it
    if payload:
        await db.set_setting(f"pending_ref_{telegram_id}", payload)

    # Create user record (lang=None until they choose)
    if not existing:
        inviter_id = await process_referral_start(telegram_id, payload)
        await db.create_user(telegram_id, full_name, username, invited_by=inviter_id)
        # Store inviter_id so language callback knows if this was a referral
        if inviter_id:
            await db.set_setting(f"pending_inviter_{telegram_id}", str(inviter_id))

    # Show language selection
    await message.answer(
        "🌐 <b>Tilni tanlang / Choose your language</b>",
        reply_markup=language_keyboard(),
    )
