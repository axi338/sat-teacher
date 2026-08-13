from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import BOT_USERNAME, CHANNEL_1_LINK, CHANNEL_2_LINK, CHANNEL_3_LINK


def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Start / Unlock SAT Math Prediction", callback_data="participate"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ About SAT Math Prediction", callback_data="about_file"
                )
            ],
        ]
    )


def channels_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    if CHANNEL_1_LINK:
        buttons.append(
            [InlineKeyboardButton(text="📢 1. SAT Humoyunbek", url=CHANNEL_1_LINK)]
        )
    if CHANNEL_2_LINK:
        buttons.append(
            [InlineKeyboardButton(text="📢 2. SAT Valley", url=CHANNEL_2_LINK)]
        )
    if CHANNEL_3_LINK:
        buttons.append(
            [InlineKeyboardButton(text="📢 3. Desmos Bootcamp", url=CHANNEL_3_LINK)]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text="🔄 Check status / Obunani tekshirish", callback_data="check_subscription"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def referral_keyboard(user_id: int | None = None) -> InlineKeyboardMarkup:
    buttons = []
    if user_id:
        share_url = f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}?start=ref_{user_id}&text=🎁%20Unlock%20the%20SAT%20Math%20Prediction%20file%20for%20free!"
        buttons.append([
            InlineKeyboardButton(
                text="📤 Send to friends", url=share_url
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="👥 Get referral link", callback_data="referral_link"
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text="🔄 Check status", callback_data="check_subscription"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text="🏆 Leaderboard", callback_data="ranking"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text="🔓 Get SAT Math Prediction", callback_data="unlock_file"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def main_menu_keyboard(user_id: int | None = None) -> InlineKeyboardMarkup:
    return referral_keyboard(user_id)




def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Total Users", callback_data="admin_total_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Campaign Stats", callback_data="admin_campaign_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📤 Broadcast Message", callback_data="admin_broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📁 Upload Predictions File",
                    callback_data="admin_upload_file",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Search User", callback_data="admin_search_user"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📥 Export User Data", callback_data="admin_export_data"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Event Settings", callback_data="admin_event_settings"
                )
            ],
        ]
    )


def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Send Broadcast", callback_data="broadcast_confirm"
                ),
                InlineKeyboardButton(
                    text="❌ Cancel", callback_data="broadcast_cancel"
                ),
            ]
        ]
    )
