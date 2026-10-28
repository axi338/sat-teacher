"""
Handles the language selection callback buttons (set_lang_uz / set_lang_en).
After the user picks a language, this sends the full welcome message.
"""
from aiogram import F, Router
from aiogram.types import CallbackQuery

import database as db
from keyboards import referred_welcome_keyboard, welcome_keyboard
from translations import T

router = Router()


async def _send_welcome(callback: CallbackQuery, lang: str) -> None:
    """Save lang, then deliver the full onboarding welcome."""
    user_id   = callback.from_user.id
    full_name = callback.from_user.full_name
    username  = callback.from_user.username

    # Persist language choice
    await db.update_user(user_id, lang=lang, full_name=full_name, username=username)

    # Edit the language-picker message into the language-set confirmation
    await callback.message.edit_text(T[lang]["language_set"])

    # Send welcome
    await callback.message.answer(T[lang]["welcome"], reply_markup=welcome_keyboard(lang=lang))

    # If this user came via a referral link, show the referred welcome too
    inviter_raw = await db.get_setting(f"pending_inviter_{user_id}")
    if inviter_raw:
        await callback.message.answer(
            T[lang]["referred_welcome"],
            reply_markup=referred_welcome_keyboard(lang=lang),
        )
        # Clean up temp setting
        await db.set_setting(f"pending_inviter_{user_id}", "")


@router.callback_query(F.data == "set_lang_uz")
async def cb_set_lang_uz(callback: CallbackQuery) -> None:
    await callback.answer()
    await _send_welcome(callback, lang="uz")


@router.callback_query(F.data == "set_lang_en")
async def cb_set_lang_en(callback: CallbackQuery) -> None:
    await callback.answer()
    await _send_welcome(callback, lang="en")
