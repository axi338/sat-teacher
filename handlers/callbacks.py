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
from services.export_service import export_users_csv, format_user_info
from services.referral_service import build_leaderboard_text, build_referral_link


router = Router()

STEP_1_TEXT = (
    "🎁 2 ta kanalga obuna bo'lib, 3 ta do'stingizni taklif qiling va birinchi sovg'ani oching!\n\n"
    "📚 Birinchi sovg'a:\n"
    "$1000+ qiymatidagi premium SAT darsliklari siz uchun ochiladi.\n\n"
    "🏆 Asosiy sovg'a:\n"
    "Humoyunbek Mirzayev bilan $1000 qiymatidagi 1 oylik individual mentorlik.\n\n"
    "🔥 Asosiy sovg'ani qo'lga kiritish uchun imkon qadar ko'proq do'stingizni taklif qiling. "
    "Eng ko'p do'st taklif qilgan ishtirokchi g'olib bo'ladi! ❤️🔥\n\n"
    "👇 Avval quyidagi kanallarga obuna bo'ling:\n"
    "1. [Math with Humoyunbek](https://t.me/sat_humoyunbek)\n"
    "2. [SAT Valley](https://t.me/sat_valley)\n\n"
    "Obuna bo'lgach, **✅ Obunani tekshirish** tugmasini bosing."
)


STEP_2_TEXT = (
    "✅ Obuna muvaffaqiyatli tasdiqlandi! 🎉\n\n"
    "👥 2-qadam: Do'stlaringizni taklif qiling\n"
    "🎁 Shaxsiy referral havolangiz orqali kamida 3 ta do'stingizni taklif qiling.\n\n"
    "Do'stlaringiz havolangiz orqali botga kirib START tugmasini bosgach, siz uchun $1000+ qiymatidagi premium SAT darsliklari ochiladi. 📚\n\n"
    "🏆 Ko'proq do'st taklif qilsangiz, imkoniyatingiz yanada oshadi!\n"
    "Eng ko'p do'st taklif qilgan ishtirokchi:\n\n"
    "👨🏫 Humoyunbek Mirzayev bilan $1000 qiymatidagi 1 oylik individual mentorlikni qo'lga kiritadi.\n\n"
    "🥈 TOP 3 ishtirokchi esa:\n"
    "📱 Telegram Premium\n"
    "📚 Mutolaa Premium bilan taqdirlanadi. ❤️🔥"
)

ABOUT_FILE_TEXT = (
    "🚨 **SAT'dan 1500+ olishni xohlaysizmi?**\n\n"
    "Humoyunbek Mirzayev — SAT bo'yicha O'zbekistondagi eng yaxshi ustoz — \n"
    "siz uchun **$1000+ qiymatidagi** to'liq SAT tayyorgarlik paketini \n"
    "mutlaqo **BEPUL** taqdim etmoqda!\n\n"
    "📚 **Nima olasiz?**\n"
    "✅ SAT Math bo'yicha to'liq video darslar kursi\n"
    "✅ SAT English & Reading tayyorgarlik materiallari\n"
    "✅ Real SAT savollari va yechimlar\n"
    "✅ Shaxsiy o'sish strategiyalari\n\n"
    "🏆 **Sovrinlar:**\n"
    "🥇 1-o'rin — Humoyunbek Mirzayev bilan **1 oylik individual mentorlik** (qiymati $1000)\n"
    "🥈 2-o'rin — **Telegram Premium** + **Mutolaa Premium**\n"
    "🥉 3-o'rin — **Telegram Premium** + **Mutolaa Premium**\n\n"
    "🔥 **G'olib kim bo'ladi?**\n"
    "Eng ko'p do'st taklif qilgan ishtirokchi asosiy sovrinni qo'lga kiritadi!\n\n"
    "📌 **Shartlar:**\n"
    "✅ 2 ta Telegram kanalga obuna bo'ling\n"
    "✅ Do'stlaringizni taklif havolangiz orqali taklif qiling\n\n"
    "Vaqt cheklangan — hoziroq ishtirok eting!"
)

EVENT_SETTINGS_TEXT = (
    "⚙️ Event Sozlamalari\n\n"
    "🔥 Hozirgi event: $1000 SAT Mukofoti\n\n"
    f"Talablar:\n"
    f"• 2 ta Telegram kanalga obuna bo'lish\n"
    f"• {REQUIRED_REFERRALS} ta do'stni taklif qilish\n\n"
    "Fayl yuklash: Admin paneldagi 📁 Upload Predictions File tugmasi orqali."
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

    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Iltimos, avval /start buyrug'ini yuboring.")
        return

    channels_ok, _, _ = await file_service.user_can_unlock(bot, user)

    if channels_ok:
        await db.update_user(callback.from_user.id, channels_joined=1)
        await callback.message.answer(
            STEP_2_TEXT,
            reply_markup=referral_keyboard(),
        )
    else:
        await db.update_user(callback.from_user.id, channels_joined=0)
        await callback.message.answer(
            "❌ Siz hali barcha kanallarga obuna bo'lmadingiz.\n\n"
            "Iltimos, ko'rsatilgan barcha kanallarga obuna bo'ling va qaytadan **✅ Obunani tekshirish** tugmasini bosing.",
            reply_markup=channels_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )


@router.callback_query(F.data == "referral_link")
async def cb_referral_link(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Iltimos, avval /start buyrug'ini yuboring.")
        return

    link = build_referral_link(callback.from_user.id)
    await callback.message.answer(
        f"🚨 SAT'dan 1500+ olishni xohlaysizmi?\n"
        f"🎁 $1000+ qiymatidagi SAT darsliklari — BEPUL!\n"
        f"🏆 $1000 qiymatidagi Humoyunbek Mirzayev bilan individual mentorlik!\n"
        f"📱 TOP 3 — Telegram Premium + Mutolaa Premium.\n"
        f"🔥 G'olib — eng ko'p do'st taklif qilgan ishtirokchi!\n\n"
        f"👇 Hoziroq qatnashing:\n"
        f"{link}",
        reply_markup=referral_keyboard(),
    )


@router.callback_query(F.data == "my_progress")
async def cb_my_progress(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    db_user = await db.get_user(callback.from_user.id)
    if not db_user:
        await callback.message.answer("Iltimos, avval /start buyrug'ini yuboring.")
        return

    channels_ok, referrals_ok, referral_count = await file_service.user_can_unlock(
        bot, db_user
    )
    db_user = await db.get_user(callback.from_user.id) or db_user
    file_unlocked = bool(db_user.get("file_unlocked"))

    if channels_ok and referrals_ok:
        invite_link = await file_service.get_target_invite_link(bot)
        await callback.message.answer(
            "🎉 **Tabriklaymiz! Barcha shartlarni muvaffaqiyatli bajardingiz!**\n\n"
            f"Sizning kirish havolangiz: {invite_link}",
            reply_markup=main_menu_keyboard(),
        )
        return

    text = file_service.format_progress(
        channels_ok, referral_count, file_unlocked
    )
    await callback.message.answer(
        text, 
        reply_markup=referral_keyboard() if channels_ok else channels_keyboard()
    )


@router.callback_query(F.data == "about_file")
async def cb_about_file(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(ABOUT_FILE_TEXT, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "unlock_file")
async def cb_unlock_file(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()
    if not callback.from_user:
        return

    db_user = await db.get_user(callback.from_user.id)
    if not db_user:
        await callback.message.answer("Iltimos, avval /start buyrug'ini yuboring.")
        return

    channels_ok, referrals_ok, referral_count = await file_service.user_can_unlock(
        bot, db_user
    )

    if channels_ok and referrals_ok:
        await db.update_user(callback.from_user.id, file_unlocked=1)
        invite_link = await file_service.get_target_invite_link(bot)
        
        await callback.message.answer(
            "🎉 **Tabriklaymiz! Barcha shartlarni muvaffaqiyatli bajardingiz!**\n\n"
            "Siz uchun eksklyuziv taklif havolasi ajratildi:\n"
            f"👉 {invite_link}\n\n"
            "Ushbu havola orqali materiallar va sovg'alarga ega bo'ling!",
            reply_markup=main_menu_keyboard(),
        )

        file_id = await file_service.get_predictions_file_id()
        if file_id:
            await callback.message.answer_document(file_id)
        return

    channels_text = "✅ Obuna bo'lingan" if channels_ok else "❌ Obuna bo'linmagan"
    await callback.message.answer(
        "🔒 **Sovg'a hali qulflangan.**\n\n"
        "Uni ochish uchun quyidagi shartlarni bajaring:\n\n"
        "✅ Kanallarga obuna bo'ling\n"
        f"👥 {REQUIRED_REFERRALS} ta do'stingizni taklif qiling\n\n"
        f"Hozirgi holatingiz:\n"
        f"📢 Kanallar: {channels_text}\n"
        f"👥 Taklif qilinganlar: {referral_count}/{REQUIRED_REFERRALS}",
        reply_markup=referral_keyboard() if channels_ok else channels_keyboard(),
    )



# --- Admin callbacks ---


@router.callback_query(F.data == "admin_total_users")
async def cb_admin_total_users(callback: CallbackQuery) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    stats = await db.get_campaign_stats()
    await callback.message.answer(f"Total users: {stats['total_users']}")


@router.callback_query(F.data == "admin_campaign_stats")
async def cb_admin_campaign_stats(callback: CallbackQuery) -> None:
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return
    await callback.answer()
    s = await db.get_campaign_stats()
    await callback.message.answer(
        "📊 Campaign Statistics\n\n"
        f"👥 Total users: {s['total_users']}\n"
        f"📢 Joined channels: {s['joined_channels']}\n"
        f"👥 Users with at least 1 referral: {s['users_with_referrals']}\n"
        f"✅ Users with 3+ referrals: {s['users_with_3_referrals']}\n"
        f"🔓 Users who unlocked the file: {s['file_unlocked']}\n"
        f"🔗 Total successful referrals: {s['total_referrals']}"
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
        "Please upload the new JUNE SAT Predictions File."
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

    text = await build_leaderboard_text(callback.from_user.id)
    await callback.message.answer(text, reply_markup=main_menu_keyboard())



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
