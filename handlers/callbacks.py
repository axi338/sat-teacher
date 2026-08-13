import asyncio

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, LinkPreviewOptions

import database as db
from config import REQUIRED_REFERRALS
from handlers.admin import AdminStates, _send_export, is_admin
from keyboards import (
    admin_panel_keyboard,
    broadcast_confirm_keyboard,
    channels_keyboard,
    main_menu_keyboard,
    referral_keyboard,
)
from services import file_service
from services.channel_checker import check_all_channels
from services.export_service import export_users_csv, format_user_info
from services.referral_service import (
    build_leaderboard_text,
    build_referral_link,
    check_and_credit_referral,
)

router = Router()

STEP_1_TEXT = (
    "🎁 **Want the SAT Math Prediction file?**\n\n"
    "This file includes high-value SAT Math practice & prediction problems! 🚀\n\n"
    "📌 **To get started, please join all 3 required channels below:**\n"
    "• https://t.me/sat_humoyunbek\n"
    "• https://t.me/sat_valley\n"
    "• https://t.me/DesmosBootcamp\n\n"
    "Once joined, click **🔄 Check status / Obunani tekshirish** to get your personal referral link."
)

ABOUT_FILE_TEXT = (
    "🎁 **SAT Math Prediction File**\n\n"
    "The SAT Math Prediction file is an exclusive collection of high-yield math problems, "
    "pattern analyses, and prediction formulas designed by SAT Valley experts to help you achieve a top SAT score.\n\n"
    "📌 **How to unlock for free:**\n"
    "1. Join all 3 required channels (§1.1).\n"
    "2. Share your personal referral link with 3 friends.\n"
    "3. Once 3 friends join through your link, the file will be delivered automatically!"
)

EVENT_SETTINGS_TEXT = (
    "⚙️ **Event Settings**\n\n"
    "🔥 Current Event: SAT Math Prediction File Giveaway\n\n"
    "Requirements:\n"
    "• Join 3 required Telegram channels\n"
    f"• Invite {REQUIRED_REFERRALS} friends\n\n"
    "Upload File: Use 📁 Upload Predictions File button in Admin Panel."
)


@router.callback_query(F.data == "participate")
async def cb_participate(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        STEP_1_TEXT,
        reply_markup=channels_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data == "check_subscription")
async def cb_check_subscription(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Please type /start to register.")
        return

    channels_ok = await check_all_channels(bot, user_id)
    if channels_ok:
        await db.update_user(user_id, channels_joined=1)
        await check_and_credit_referral(bot, user_id)

        user = await db.get_user(user_id) or user
        ref_link = build_referral_link(user_id)
        count = user.get("referral_count", 0)

        text = file_service.format_progress(user_id, ref_link, count)
        await callback.message.answer(
            text,
            reply_markup=referral_keyboard(user_id),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    else:
        await db.update_user(user_id, channels_joined=0)
        await callback.message.answer(
            "❌ **You have not joined all 3 required channels yet.**\n\n"
            "Please join each channel below and then click **🔄 Check status / Obunani tekshirish**:",
            reply_markup=channels_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )


@router.callback_query(F.data == "referral_link")
async def cb_referral_link(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Please type /start to register.")
        return

    link = build_referral_link(user_id)
    count = user.get("referral_count", 0)
    text = file_service.format_progress(user_id, link, count)
    await callback.message.answer(
        text,
        reply_markup=referral_keyboard(user_id),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data == "my_progress")
async def cb_my_progress(callback: CallbackQuery, bot: Bot) -> None:
    await cb_check_subscription(callback, bot)


@router.callback_query(F.data == "about_file")
async def cb_about_file(callback: CallbackQuery) -> None:
    await callback.answer()
    user_id = callback.from_user.id if callback.from_user else None
    await callback.message.answer(ABOUT_FILE_TEXT, reply_markup=main_menu_keyboard(user_id))


@router.callback_query(F.data == "unlock_file")
async def cb_unlock_file(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    db_user = await db.get_user(user_id)
    if not db_user:
        await callback.message.answer("Please type /start to register.")
        return

    channels_ok, referrals_ok, referral_count = await file_service.user_can_unlock(
        bot, db_user
    )

    if channels_ok and referrals_ok:
        await db.update_user(user_id, file_unlocked=1)
        file_id = await file_service.get_predictions_file_id()

        await callback.message.answer(
            "🎉 **Congratulations! You've invited 3 friends.**\n\n"
            "📎 Here is your **SAT Math Prediction** file:"
        )

        if file_id:
            await callback.message.answer_document(file_id)
        else:
            await callback.message.answer(
                "ℹ️ Your reward is unlocked! Admin has been notified to attach the prediction file."
            )

        # Step 5 - Route to Funnel
        await callback.message.answer(
            "🚀 **What's Next?**\n\n"
            "Join the main SAT Valley channel for daily SAT practice and updates!\n"
            "👉 https://t.me/sat_valley",
            reply_markup=main_menu_keyboard(user_id),
        )
        return

    await callback.message.answer(
        f"🔒 **SAT Math Prediction file is locked.**\n\n"
        f"Friends invited: **{referral_count}/{REQUIRED_REFERRALS}**\n"
        f"Channels joined: **{'✅ Yes' if channels_ok else '❌ No'}**\n\n"
        f"Invite {REQUIRED_REFERRALS - referral_count if REQUIRED_REFERRALS > referral_count else 0} more friend(s) who join all 3 channels to unlock!",
        reply_markup=referral_keyboard(user_id) if channels_ok else channels_keyboard(),
    )


# --- Admin callbacks ---


@router.callback_query(F.data == "admin_total_users")
async def cb_admin_total_users(callback: CallbackQuery) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    stats = await db.get_campaign_stats()
    await callback.message.answer(f"Total users: {stats.get('total_users', 0)}")


@router.callback_query(F.data == "admin_campaign_stats")
async def cb_admin_campaign_stats(callback: CallbackQuery) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    s = await db.get_campaign_stats()
    await callback.message.answer(
        "📊 **Campaign Conversion Funnel & Statistics**\n\n"
        f"👤 Total Bot Users: **{s.get('total_users', 0)}**\n"
        f"📢 Joined All 3 Channels: **{s.get('joined_channels', 0)}**\n"
        f"1️⃣ Users with 1 Referral: **{s.get('users_with_1_referral', 0)}**\n"
        f"2️⃣ Users with 2 Referrals: **{s.get('users_with_2_referrals', 0)}**\n"
        f"3️⃣ Users with 3+ Referrals: **{s.get('users_with_3_referrals', 0)}**\n"
        f"🔓 File Unlocked: **{s.get('file_unlocked', 0)}**\n"
        f"🔗 Total Confirmed Referrals: **{s.get('total_referrals', 0)}**"
    )


@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.broadcast_message)
    await callback.message.answer(
        "Send the message you want to broadcast to all users."
    )


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
        f"✅ Broadcast complete.\n\n"
        f"Delivered: {success}\n"
        f"Failed: {failed}",
        reply_markup=admin_panel_keyboard(),
    )


@router.callback_query(F.data == "broadcast_cancel")
async def cb_broadcast_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        "Broadcast cancelled.",
        reply_markup=admin_panel_keyboard(),
    )


@router.callback_query(F.data == "admin_upload_file")
async def cb_admin_upload_file(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.upload_file)
    await callback.message.answer(
        "Please upload the SAT Math Prediction File (PDF or Document)."
    )


@router.callback_query(F.data == "admin_search_user")
async def cb_admin_search_user(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.search_user)
    await callback.message.answer(
        "Send a Telegram ID or username to search."
    )


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


@router.callback_query(F.data == "ranking")
async def cb_ranking(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    text = await build_leaderboard_text(user_id)
    await callback.message.answer(text, reply_markup=main_menu_keyboard(user_id))


@router.callback_query(F.data == "admin_event_settings")
async def cb_admin_event_settings(callback: CallbackQuery) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    await callback.message.answer(
        EVENT_SETTINGS_TEXT,
        reply_markup=admin_panel_keyboard(),
    )

