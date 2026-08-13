from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, Message

import database as db
from config import ADMIN_IDS, REQUIRED_REFERRALS
from keyboards import admin_panel_keyboard, broadcast_confirm_keyboard
from services.export_service import export_users_csv, export_users_xlsx, format_user_info

router = Router()


class AdminStates(StatesGroup):
    broadcast_message = State()
    broadcast_confirm = State()
    upload_file = State()
    search_user = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        await message.answer("⛔ This command is for admins only.")
        return

    await message.answer(
        "🛠 Admin Panel\n\nSelect an option:",
        reply_markup=admin_panel_keyboard(),
    )


@router.message(Command("data"))
async def cmd_data(message: Message, bot: Bot) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        await message.answer("⛔ This command is for admins only.")
        return

    users = await db.get_all_users()
    if not users:
        await message.answer("No users yet.")
        return

    if len(users) <= 30:
        lines = []
        for u in users:
            lines.append(format_user_info(u))
            lines.append("—" * 20)
        text = "\n\n".join(lines)
        if len(text) > 4000:
            await _send_export(message)
        else:
            await message.answer(text)
    else:
        await message.answer(
            f"Total users: {len(users)}. Sending export file..."
        )
        await _send_export(message)


async def _send_export(message: Message) -> None:
    csv_data = await export_users_csv()
    file = BufferedInputFile(csv_data, filename="users_export.csv")
    await message.answer_document(
        file,
        caption="📥 Exported user data (CSV)",
    )


@router.message(AdminStates.broadcast_message)
async def admin_broadcast_receive(message: Message, state: FSMContext) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        await state.clear()
        return

    await state.update_data(broadcast_text=message.text or "")
    await state.set_state(AdminStates.broadcast_confirm)
    await message.answer(
        "Are you sure you want to send this message to all users?",
        reply_markup=broadcast_confirm_keyboard(),
    )


@router.message(AdminStates.upload_file, F.document)
async def admin_upload_file_receive(message: Message, state: FSMContext) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        await state.clear()
        return

    from services.file_service import save_predictions_file_id

    doc = message.document
    if not doc:
        await message.answer("Please send a document file.")
        return

    await save_predictions_file_id(doc.file_id)
    await state.clear()
    await message.answer(
        "✅ SAT Math Prediction File uploaded successfully.\n"
        "Users who invite 3 friends and join all 3 channels will automatically receive this file.",
        reply_markup=admin_panel_keyboard(),
    )


@router.message(AdminStates.upload_file)
async def admin_upload_file_invalid(message: Message) -> None:
    await message.answer("Please upload a document file (PDF, etc.).")


@router.message(AdminStates.search_user)
async def admin_search_receive(message: Message, state: FSMContext) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        await state.clear()
        return

    query = (message.text or "").strip()
    if not query:
        await message.answer("Please send a Telegram ID or username.")
        return

    user = await db.search_user(query)
    await state.clear()
    if not user:
        await message.answer("User not found.", reply_markup=admin_panel_keyboard())
        return

    await message.answer(
        format_user_info(user),
        reply_markup=admin_panel_keyboard(),
    )
