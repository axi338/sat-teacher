import asyncio

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, LinkPreviewOptions

import database as db
from config import REQUIRED_REFERRALS
from handlers.admin import AdminStates, is_admin
from keyboards import (
    admin_panel_keyboard,
    broadcast_confirm_keyboard,
    channels_keyboard,
    dashboard_keyboard,
    status_keyboard,
    unlock_keyboard,
)
from services import file_service
from services.channel_checker import get_channel_membership_status
from services.export_service import export_users_csv
from services.referral_service import (
    build_referral_link,
    check_and_credit_referral,
)
from translations import get_lang

router = Router()


def _lang(user: dict | None) -> str:
    return get_lang(user)


@router.callback_query(F.data == "get_invite_link")
async def cb_get_invite_link(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Please send /start first.")
        return

    lang = _lang(user)
    all_joined, joined_count, missing = await get_channel_membership_status(bot, user_id)
    link = build_referral_link(user_id)

    if not all_joined:
        text = (
            file_service.format_almost_there(missing, lang=lang)
            if joined_count > 0
            else file_service.format_channels_step(lang=lang)
        )
        await callback.message.answer(
            text,
            reply_markup=channels_keyboard(lang=lang),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
        return

    await db.update_user(user_id, channels_joined=1)
    count = user.get("referral_count", 0)
    await callback.message.answer(
        file_service.format_dashboard(user_id, link, count, lang=lang),
        reply_markup=dashboard_keyboard(user_id, lang=lang),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data == "check_progress")
async def cb_check_progress(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Please send /start first.")
        return

    lang = _lang(user)
    all_joined, joined_count, missing = await get_channel_membership_status(bot, user_id)
    link = build_referral_link(user_id)

    if not all_joined:
        await db.update_user(user_id, channels_joined=0)
        text = (
            file_service.format_almost_there(missing, lang=lang)
            if joined_count > 0
            else file_service.format_channels_step(lang=lang)
        )
        await callback.message.answer(
            text,
            reply_markup=channels_keyboard(lang=lang),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
        return

    await db.update_user(user_id, channels_joined=1)
    count = user.get("referral_count", 0)
    await callback.message.answer(
        file_service.format_dashboard(user_id, link, count, lang=lang),
        reply_markup=dashboard_keyboard(user_id, lang=lang),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data == "refresh_status")
async def cb_refresh_status(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    lang = _lang(user)
    count = user.get("referral_count", 0) if user else 0

    text = await file_service.format_referral_status(user_id, lang=lang)
    kb = unlock_keyboard(lang=lang) if count >= REQUIRED_REFERRALS else status_keyboard(user_id, lang=lang)
    await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "required_channels")
async def cb_required_channels(callback: CallbackQuery) -> None:
    await callback.answer()
    user = await db.get_user(callback.from_user.id) if callback.from_user else None
    lang = _lang(user)
    await callback.message.answer(
        file_service.format_channels_step(lang=lang),
        reply_markup=channels_keyboard(lang=lang),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data == "check_membership")
async def cb_check_membership(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Please send /start first.")
        return

    lang = _lang(user)
    all_joined, joined_count, missing = await get_channel_membership_status(bot, user_id)

    if not all_joined:
        await db.update_user(user_id, channels_joined=0)
        await callback.message.answer(
            file_service.format_almost_there(missing, lang=lang),
            reply_markup=channels_keyboard(lang=lang),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
        return

    await db.update_user(user_id, channels_joined=1)
    credited = await check_and_credit_referral(bot, user_id)

    if credited:
        return

    user = await db.get_user(user_id) or user
    link  = build_referral_link(user_id)
    count = user.get("referral_count", 0)

    if count >= REQUIRED_REFERRALS and not user.get("reward_sent"):
        await file_service.deliver_reward(bot, user_id)
        return

    from translations import T
    if user.get("reward_sent"):
        await callback.message.answer(
            T[lang]["membership_confirmed_unlocked"],
            reply_markup=dashboard_keyboard(user_id, lang=lang),
        )
        return

    await callback.message.answer(
        T[lang]["membership_confirmed"].format(
            dashboard=file_service.format_dashboard(user_id, link, count, lang=lang)
        ),
        reply_markup=dashboard_keyboard(user_id, lang=lang),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data == "get_reward")
async def cb_get_reward(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Please send /start first.")
        return

    lang  = _lang(user)
    count = user.get("referral_count", 0)
    if count < REQUIRED_REFERRALS:
        from translations import T
        await callback.message.answer(
            f"{'Yana' if lang == 'uz' else 'You need'} "
            f"{REQUIRED_REFERRALS - count} "
            f"{'ta taklif kerak.' if lang == 'uz' else 'more referral(s) to unlock.'}",
            reply_markup=dashboard_keyboard(user_id, lang=lang),
        )
        return

    await file_service.deliver_reward(bot, user_id)


# ── Admin callbacks ──────────────────────────────────────────────────────────


@router.callback_query(F.data == "admin_campaign_stats")
async def cb_admin_campaign_stats(callback: CallbackQuery) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    s = await db.get_campaign_stats()
    total      = s.get("total_users", 0) or 1
    unlocked   = s.get("file_unlocked", 0)
    conversion = round(unlocked / total * 100, 1)
    await callback.message.answer(
        "📊 <b>Dashboard</b>\n\n"
        f"Total Users: <b>{s.get('total_users', 0)}</b>\n"
        f"Joined All 4 Channels: <b>{s.get('joined_channels', 0)}</b>\n"
        f"Total Verified Referrals: <b>{s.get('total_referrals', 0)}</b>\n"
        f"Users Unlocked (3/3): <b>{unlocked}</b>\n"
        f"Conversion Rate: <b>{conversion}%</b>",
        reply_markup=admin_panel_keyboard(),
    )


@router.callback_query(F.data == "admin_reward_settings")
async def cb_admin_reward_settings(callback: CallbackQuery) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()

    from config import REWARD_CHANNEL_ID, REWARD_CHANNEL_LINK

    sent_count       = await db.count_rewards_sent()
    channel_id_label = REWARD_CHANNEL_ID or "Not set — add REWARD_CHANNEL_ID to .env"

    await callback.message.answer(
        "🎁 <b>Reward Settings</b>\n\n"
        "Reward type: <b>One-time private channel link</b>\n\n"
        f"Channel ID: <code>{channel_id_label}</code>\n"
        f"Fallback link: {REWARD_CHANNEL_LINK}\n\n"
        f"Users who received access: <b>{sent_count}</b>\n\n"
        "Each user gets a unique single-use invite link when they reach 3 referrals.\n"
        "The bot must be an <b>admin</b> in the reward channel.",
        reply_markup=admin_panel_keyboard(),
    )


@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.broadcast_message)
    await callback.message.answer("Send the message you want to broadcast to all users.")


@router.callback_query(F.data == "broadcast_confirm")
async def cb_broadcast_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()

    data = await state.get_data()
    text = data.get("broadcast_text", "")
    await state.clear()

    users   = await db.get_all_users()
    success = 0
    failed  = 0
    for u in users:
        try:
            await bot.send_message(u["telegram_id"], text)
            success += 1
            await asyncio.sleep(0.05)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await bot.send_message(u["telegram_id"], text)
                success += 1
            except Exception:
                failed += 1
        except (TelegramAPIError, Exception):
            failed += 1

    await callback.message.answer(
        f"✅ Broadcast complete.\n\nDelivered: {success}\nFailed: {failed}",
        reply_markup=admin_panel_keyboard(),
    )


@router.callback_query(F.data == "broadcast_cancel")
async def cb_broadcast_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    await state.clear()
    await callback.message.answer("Broadcast cancelled.", reply_markup=admin_panel_keyboard())


@router.callback_query(F.data == "admin_search_user")
async def cb_admin_search_user(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.search_user)
    await callback.message.answer("Send a Telegram ID or username to search.")


@router.callback_query(F.data == "admin_export_data")
async def cb_admin_export_data(callback: CallbackQuery) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()

    csv_data = await export_users_csv()
    file     = BufferedInputFile(csv_data, filename="users_export.csv")
    await callback.message.answer_document(
        file,
        caption="📥 Exported user data",
        reply_markup=admin_panel_keyboard(),
    )
