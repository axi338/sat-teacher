from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import CHANNEL_1_LINK, CHANNEL_2_LINK


def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Ishtirok etish / Start", callback_data="participate"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Mukofot haqida", callback_data="about_file"
                )
            ],
        ]
    )


def channels_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    if CHANNEL_1_LINK:
        buttons.append(
            [InlineKeyboardButton(text="📢 1-kanalga obuna bo'lish", url=CHANNEL_1_LINK)]
        )
    if CHANNEL_2_LINK:
        buttons.append(
            [InlineKeyboardButton(text="📢 2-kanalga obuna bo'lish", url=CHANNEL_2_LINK)]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text="✅ Obunani tekshirish", callback_data="check_subscription"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def referral_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Mening taklif havolam", callback_data="referral_link"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Mening natijam", callback_data="my_progress"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔓 Sovg'ani olish", callback_data="unlock_file"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏆 Reyting (Top 20)", callback_data="ranking"
                )
            ],
        ]
    )


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Mening taklif havolam", callback_data="referral_link"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Mening natijam", callback_data="my_progress"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔓 Sovg'ani olish", callback_data="unlock_file"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏆 Reyting (Top 20)", callback_data="ranking"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Mukofot haqida", callback_data="about_file"
                )
            ],
        ]
    )



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
