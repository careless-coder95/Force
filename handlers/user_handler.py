from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import db
from helpers import send_welcome_message, build_menu_keyboard
import config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if db.is_verified(user_id):
        # Already verified → show menu directly
        menu_kb = build_menu_keyboard()
        await update.message.reply_text(
            "✅ <b>Welcome back!</b>\n\nYou already have access. Use the buttons below:",
            parse_mode="HTML",
            reply_markup=menu_kb
        )
        return

    # Send welcome message with force join + verify button
    await send_welcome_message(update, context, show_verify=True)


async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Check all force join channels
    channels = db.get_channels()
    not_joined = []

    for ch in channels:
        try:
            member = await context.bot.get_chat_member(ch["id"], user_id)
            if member.status in ["left", "kicked", "banned"]:
                not_joined.append(ch)
        except Exception:
            not_joined.append(ch)

    if not_joined:
        labels = "\n".join([f"• {ch['label']}" for ch in not_joined])
        await query.answer(
            f"❌ Please join all required channels first!\n\nNot joined:\n{labels}",
            show_alert=True
        )
        return

    # All joined → verify
    db.verify_user(user_id)

    # Send success message
    menu_kb = build_menu_keyboard()
    await query.message.reply_text(
        "🎉 <b>Access Granted!</b>\n\nYou have successfully joined all required channels and verified your access. You can now use this bot!",
        parse_mode="HTML",
        reply_markup=menu_kb
    )


async def handle_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not db.is_verified(user_id):
        await query.answer("❌ Please verify first by joining all channels!", show_alert=True)
        return

    index = int(query.data.replace("menu_btn_", ""))
    btns = db.get_menu_buttons()

    if index >= len(btns):
        await query.answer("Button not found.", show_alert=True)
        return

    btn = btns[index]
    text = btn.get("text") or ""
    photo = btn.get("photo")
    video = btn.get("video")

    if not text and not photo and not video:
        await query.answer("This button has no content yet.", show_alert=True)
        return

    if video:
        await query.message.reply_video(video=video, caption=text or None, parse_mode="HTML")
    elif photo:
        await query.message.reply_photo(photo=photo, caption=text or None, parse_mode="HTML")
    elif text:
        await query.message.reply_text(text, parse_mode="HTML")
