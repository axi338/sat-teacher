from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import CHANNEL_1_LINK, CHANNEL_2_LINK, CHANNEL_3_LINK, EXPLORE_SAT_VALLEY_LINK, SAT_VALLEY_LINK
from services.referral_service import build_referral_link, build_share_url


def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Get My Invite Link",
                    callback_data="get_invite_link",
                )
            ],
        ]
    )


def dashboard_keyboard(user_id: int) -> InlineKeyboardMarkup:
    share_url = build_share_url(build_referral_link(user_id))
    buttons = [
        [InlineKeyboardButton(text="📤 Invite Friends", url=share_url)],
        [InlineKeyboardButton(text="🔄 Check My Progress", callback_data="check_progress")],
        [InlineKeyboardButton(text="📚 Required Channels", callback_data="required_channels")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def status_keyboard(user_id: int) -> InlineKeyboardMarkup:
    share_url = build_share_url(build_referral_link(user_id))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Invite More Friends", url=share_url)],
            [InlineKeyboardButton(text="🔄 Refresh Status", callback_data="refresh_status")],
            [InlineKeyboardButton(text="📚 Required Channels", callback_data="required_channels")],
        ]
    )


def channels_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    if CHANNEL_1_LINK:
        buttons.append([InlineKeyboardButton(text="📢 SAT Humoyunbek", url=CHANNEL_1_LINK)])
    if CHANNEL_2_LINK:
        buttons.append([InlineKeyboardButton(text="📢 SAT Valley", url=CHANNEL_2_LINK)])
    if CHANNEL_3_LINK:
        buttons.append([InlineKeyboardButton(text="📢 Desmos Bootcamp", url=CHANNEL_3_LINK)])
    buttons.append(
        [InlineKeyboardButton(text="✅ Check My Membership", callback_data="check_membership")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def unlock_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Get SAT Math August Prediction", callback_data="get_reward")],
            [InlineKeyboardButton(text="🔄 Refresh Status", callback_data="refresh_status")],
        ]
    )


def post_reward_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎓 Explore SAT Valley", url=EXPLORE_SAT_VALLEY_LINK)],
            [InlineKeyboardButton(text="📢 Join SAT Valley", url=SAT_VALLEY_LINK)],
        ]
    )


def referred_welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Join Required Channels", callback_data="required_channels")],
            [InlineKeyboardButton(text="✅ Check My Membership", callback_data="check_membership")],
        ]
    )


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Dashboard", callback_data="admin_campaign_stats")],
            [InlineKeyboardButton(text="🎁 Reward Settings", callback_data="admin_reward_settings")],
            [InlineKeyboardButton(text="📤 Broadcast Message", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="🔍 Search User", callback_data="admin_search_user")],
            [InlineKeyboardButton(text="📥 Export CSV", callback_data="admin_export_data")],
        ]
    )


def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Send Broadcast", callback_data="broadcast_confirm"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="broadcast_cancel"),
            ]
        ]
    )
