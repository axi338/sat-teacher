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

router = Router()


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

    all_joined, joined_count, missing = await get_channel_membership_status(bot, user_id)
    link = build_referral_link(user_id)

    if not all_joined:
        if joined_count > 0:
            await callback.message.answer(
                file_service.format_almost_there(missing),
                reply_markup=channels_keyboard(),
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
        else:
            await callback.message.answer(
                file_service.format_channels_step(),
                reply_markup=channels_keyboard(),
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
        return

    await db.update_user(user_id, channels_joined=1)
    count = user.get("referral_count", 0)
    await callback.message.answer(
        file_service.format_dashboard(user_id, link, count),
        reply_markup=dashboard_keyboard(user_id),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data == "check_progress")
async def cb_check_progress(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Please send /start first.")
        return

    link = build_referral_link(user_id)
    count = user.get("referral_count", 0)
    await callback.message.answer(
        file_service.format_dashboard(user_id, link, count),
        reply_markup=dashboard_keyboard(user_id),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data == "refresh_status")
async def cb_refresh_status(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    text = await file_service.format_referral_status(user_id)
    user = await db.get_user(user_id)
    count = user.get("referral_count", 0) if user else 0

    kb = unlock_keyboard() if count >= REQUIRED_REFERRALS else status_keyboard(user_id)
    await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "required_channels")
async def cb_required_channels(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        file_service.format_channels_step(),
        reply_markup=channels_keyboard(),
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

    all_joined, joined_count, missing = await get_channel_membership_status(bot, user_id)

    if not all_joined:
        await db.update_user(user_id, channels_joined=0)
        await callback.message.answer(
            file_service.format_almost_there(missing),
            reply_markup=channels_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
        return

    await db.update_user(user_id, channels_joined=1)
    credited = await check_and_credit_referral(bot, user_id)

    if credited:
        return

    user = await db.get_user(user_id) or user
    link = build_referral_link(user_id)
    count = user.get("referral_count", 0)

    if count >= REQUIRED_REFERRALS and not user.get("reward_sent"):
        await file_service.deliver_reward(bot, user_id)
        return

    if user.get("reward_sent"):
        await callback.message.answer(
            "✅ <b>Membership confirmed.</b>\n\n"
            "You've already unlocked your SAT Math Prediction PDF!",
            reply_markup=dashboard_keyboard(user_id),
        )
        return

    await callback.message.answer(
        "✅ <b>Membership confirmed.</b>\n\n"
        + file_service.format_dashboard(user_id, link, count),
        reply_markup=dashboard_keyboard(user_id),
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

    count = user.get("referral_count", 0)
    if count < REQUIRED_REFERRALS:
        await callback.message.answer(
            f"You need {REQUIRED_REFERRALS - count} more verified referral(s) to unlock.",
            reply_markup=dashboard_keyboard(user_id),
        )
        return

    if user.get("reward_sent"):
        file_id = await file_service.get_predictions_file_id()
        if file_id:
            await callback.message.answer_document(file_id)
        else:
            await callback.message.answer(
                "Your reward is unlocked! The PDF will be available shortly."
            )
        return

    await file_service.deliver_reward(bot, user_id)


# --- Admin callbacks ---


@router.callback_query(F.data == "admin_campaign_stats")
async def cb_admin_campaign_stats(callback: CallbackQuery) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    s = await db.get_campaign_stats()
    total = s.get("total_users", 0) or 1
    unlocked = s.get("file_unlocked", 0)
    conversion = round(unlocked / total * 100, 1)
    await callback.message.answer(
        "📊 <b>Dashboard</b>\n\n"
        f"Total Users: <b>{s.get('total_users', 0)}</b>\n"
        f"Joined All 3 Channels: <b>{s.get('joined_channels', 0)}</b>\n"
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

    settings = await db.get_reward_settings()
    active = settings.get("predictions_active") != "0"
    size_bytes = settings.get("predictions_file_size")
    size_label = f"{int(size_bytes) / 1024:.1f} KB" if size_bytes and size_bytes.isdigit() else "—"

    await callback.message.answer(
        "🎁 <b>Reward Settings</b>\n\n"
        f"Current PDF: <b>{settings.get('predictions_file_name') or 'Not uploaded'}</b>\n"
        f"File size: <b>{size_label}</b>\n"
        f"Upload date: <b>{settings.get('predictions_uploaded_at') or '—'}</b>\n"
        f"Status: <b>{'Active' if active else 'Inactive'}</b>\n"
        f"Users who received it: <b>{settings.get('rewards_sent_count', '0')}</b>",
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

    users = await db.get_all_users()
    success = 0
    failed = 0
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
        except TelegramAPIError:
            failed += 1
        except Exception:
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


@router.callback_query(F.data == "admin_upload_file")
async def cb_admin_upload_file(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.upload_file)
    await callback.message.answer(
        "Upload the SAT Math Prediction PDF.\n"
        "It will be sent automatically when users reach 3 verified referrals."
    )


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
    file = BufferedInputFile(csv_data, filename="users_export.csv")
    await callback.message.answer_document(
        file,
        caption="📥 Exported user data",
        reply_markup=admin_panel_keyboard(),
    )
