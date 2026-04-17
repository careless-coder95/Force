from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from database import db
from typing import Optional


def build_welcome_keyboard(include_verify: bool = False):
    """Build keyboard for welcome message."""
    welcome = db.get_welcome()
    channels = welcome["force_join_channels"]
    inline_btns = welcome["inline_buttons"]

    rows = []

    # Force join channel buttons (each on its own row)
    for ch in channels:
        rows.append([InlineKeyboardButton(f"➕ {ch['label']}", url=ch["url"])])

    # Custom inline buttons (2 per row)
    custom_row = []
    for btn in inline_btns:
        custom_row.append(InlineKeyboardButton(btn["label"], url=btn["url"]))
        if len(custom_row) == 2:
            rows.append(custom_row)
            custom_row = []
    if custom_row:
        rows.append(custom_row)

    if include_verify:
        rows.append([InlineKeyboardButton("✅ Verify Access", callback_data="verify")])

    return InlineKeyboardMarkup(rows) if rows else None


def build_menu_keyboard():
    """Build post-verify menu buttons."""
    btns = db.get_menu_buttons()
    if not btns:
        return None
    rows = []
    row = []
    for i, btn in enumerate(btns):
        row.append(InlineKeyboardButton(btn["label"], callback_data=f"menu_btn_{i}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


async def send_welcome_message(update_or_message, context, show_verify=True):
    """Send the welcome message with media and buttons."""
    welcome = db.get_welcome()
    text = welcome["text"] or "Welcome!"
    photo = welcome["photo"]
    video = welcome["video"]
    keyboard = build_welcome_keyboard(include_verify=show_verify)

    msg = update_or_message if hasattr(update_or_message, "chat_id") else update_or_message.message

    if video:
        await msg.reply_video(
            video=video,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif photo:
        await msg.reply_photo(
            photo=photo,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await msg.reply_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
