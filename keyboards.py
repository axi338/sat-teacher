from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import CHANNEL_1_LINK, CHANNEL_2_LINK, CHANNEL_3_LINK, CHANNEL_4_LINK, EXPLORE_SAT_VALLEY_LINK, SAT_VALLEY_LINK
from services.referral_service import build_referral_link, build_share_url
from translations import T


def language_keyboard() -> InlineKeyboardMarkup:
    """Initial language selection — shown before any localised content."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
                InlineKeyboardButton(text="🇬🇧 English",   callback_data="set_lang_en"),
            ]
        ]
    )


def welcome_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=T[lang]["btn_get_link"],
                    callback_data="get_invite_link",
                )
            ],
        ]
    )


def dashboard_keyboard(user_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    share_url = build_share_url(build_referral_link(user_id))
    buttons = [
        [InlineKeyboardButton(text=T[lang]["btn_invite"],   url=share_url)],
        [InlineKeyboardButton(text=T[lang]["btn_progress"], callback_data="check_progress")],
        [InlineKeyboardButton(text=T[lang]["btn_channels"], callback_data="required_channels")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def status_keyboard(user_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    share_url = build_share_url(build_referral_link(user_id))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=T[lang]["btn_more"],    url=share_url)],
            [InlineKeyboardButton(text=T[lang]["btn_refresh"], callback_data="refresh_status")],
            [InlineKeyboardButton(text=T[lang]["btn_channels"],callback_data="required_channels")],
        ]
    )


def channels_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    buttons = []
    if CHANNEL_1_LINK:
        buttons.append([InlineKeyboardButton(text="📢 Salohiddin SAT",  url=CHANNEL_1_LINK)])
    if CHANNEL_2_LINK:
        buttons.append([InlineKeyboardButton(text="📢 You Can Do It",   url=CHANNEL_2_LINK)])
    if CHANNEL_3_LINK:
        buttons.append([InlineKeyboardButton(text="📢 SAT Valley",      url=CHANNEL_3_LINK)])
    if CHANNEL_4_LINK:
        buttons.append([InlineKeyboardButton(text="📢 SAT Humoyunbek",  url=CHANNEL_4_LINK)])
    buttons.append(
        [InlineKeyboardButton(text=T[lang]["btn_check"], callback_data="check_membership")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def unlock_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=T[lang]["btn_unlock"],  callback_data="get_reward")],
            [InlineKeyboardButton(text=T[lang]["btn_refresh"], callback_data="refresh_status")],
        ]
    )


def post_reward_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=T[lang]["btn_explore"],  url=EXPLORE_SAT_VALLEY_LINK)],
            [InlineKeyboardButton(text=T[lang]["btn_join_sat"], url=SAT_VALLEY_LINK)],
        ]
    )


def referred_welcome_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=T[lang]["btn_join_ch"], callback_data="required_channels")],
            [InlineKeyboardButton(text=T[lang]["btn_check"],   callback_data="check_membership")],
        ]
    )


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Dashboard",          callback_data="admin_campaign_stats")],
            [InlineKeyboardButton(text="🎁 Reward Settings",    callback_data="admin_reward_settings")],
            [InlineKeyboardButton(text="📤 Broadcast Message",  callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="🔍 Search User",        callback_data="admin_search_user")],
            [InlineKeyboardButton(text="📥 Export CSV",         callback_data="admin_export_data")],
        ]
    )


def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Send Broadcast", callback_data="broadcast_confirm"),
                InlineKeyboardButton(text="❌ Cancel",          callback_data="broadcast_cancel"),
            ]
        ]
    )
