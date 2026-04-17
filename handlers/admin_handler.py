from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import db
from helpers import send_welcome_message, build_welcome_keyboard, build_menu_keyboard
import config


def is_owner(user_id: int) -> bool:
    return user_id in config.OWNER_IDS


# ── Main Admin Panel ────────────────────────────────────────────────────────

def admin_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Welcome Message", callback_data="admin_welcome_menu")],
        [InlineKeyboardButton("📢 Force Join Channels", callback_data="admin_channels_menu")],
        [InlineKeyboardButton("🔘 Welcome Inline Buttons", callback_data="admin_welcome_btns_menu")],
        [InlineKeyboardButton("📋 Post-Verify Menu Buttons", callback_data="admin_menu_btns")],
        [InlineKeyboardButton("👁 Preview Welcome", callback_data="admin_preview_welcome")],
        [InlineKeyboardButton("🚀 Publish / Reset", callback_data="admin_publish")],
    ])


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text(
        "🛠 <b>Admin Control Panel</b>\n\nManage everything about your bot from here.",
        parse_mode="HTML",
        reply_markup=admin_main_keyboard()
    )


# ── Callback Router ─────────────────────────────────────────────────────────

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not is_owner(user_id):
        await query.answer("⛔ Unauthorized", show_alert=True)
        return

    data = query.data

    # ── Welcome Menu ────────────────────────────────────────────────
    if data == "admin_welcome_menu":
        await show_welcome_menu(query)

    elif data == "admin_set_welcome_text":
        db.set_pending(user_id, "await_welcome_text")
        await query.message.reply_text(
            "✏️ <b>Send the welcome text now.</b>\n\nYou can use HTML tags:\n<code>&lt;b&gt;bold&lt;/b&gt;</code>, <code>&lt;i&gt;italic&lt;/i&gt;</code>, <code>&lt;u&gt;underline&lt;/u&gt;</code>, <code>&lt;blockquote expandable&gt;quote&lt;/blockquote&gt;</code>",
            parse_mode="HTML"
        )

    elif data == "admin_set_welcome_photo":
        db.set_pending(user_id, "await_welcome_photo")
        await query.message.reply_text("📷 <b>Send a photo</b> to use as welcome media.", parse_mode="HTML")

    elif data == "admin_set_welcome_video":
        db.set_pending(user_id, "await_welcome_video")
        await query.message.reply_text("🎥 <b>Send a video</b> to use as welcome media.", parse_mode="HTML")

    elif data == "admin_clear_welcome_media":
        db.clear_welcome_media()
        await query.message.reply_text("🗑 Welcome media cleared.", reply_markup=admin_main_keyboard())

    # ── Channels ────────────────────────────────────────────────────
    elif data == "admin_channels_menu":
        await show_channels_menu(query)

    elif data == "admin_add_channel":
        db.set_pending(user_id, "await_channel_id")
        await query.message.reply_text(
            "📢 <b>Step 1/3:</b> Send the <b>Channel ID</b> (e.g. <code>-1001234567890</code>)\n\nMake sure the bot is admin in that channel.",
            parse_mode="HTML"
        )

    elif data.startswith("admin_del_channel_"):
        ch_id = data.replace("admin_del_channel_", "")
        db.remove_channel(ch_id)
        await query.message.reply_text("✅ Channel removed.", reply_markup=admin_main_keyboard())

    # ── Welcome Inline Buttons ──────────────────────────────────────
    elif data == "admin_welcome_btns_menu":
        await show_welcome_btns_menu(query)

    elif data == "admin_add_welcome_btn":
        db.set_pending(user_id, "await_welcome_btn_label")
        await query.message.reply_text("🔘 <b>Step 1/2:</b> Send the <b>button label</b> (text shown on button).", parse_mode="HTML")

    elif data.startswith("admin_del_welcome_btn_"):
        idx = int(data.replace("admin_del_welcome_btn_", ""))
        db.remove_welcome_button(idx)
        await query.message.reply_text("✅ Button removed.", reply_markup=admin_main_keyboard())

    # ── Post-Verify Menu Buttons ────────────────────────────────────
    elif data == "admin_menu_btns":
        await show_menu_btns(query)

    elif data == "admin_add_menu_btn":
        db.set_pending(user_id, "await_menu_btn_label")
        await query.message.reply_text("📋 <b>Send the button label</b> (e.g. Support Group, App Link).", parse_mode="HTML")

    elif data.startswith("admin_edit_menu_btn_"):
        idx = int(data.replace("admin_edit_menu_btn_", ""))
        await show_edit_menu_btn(query, idx)

    elif data.startswith("admin_menu_btn_set_text_"):
        idx = int(data.replace("admin_menu_btn_set_text_", ""))
        db.set_pending(user_id, "await_menu_btn_text", {"btn_index": idx})
        await query.message.reply_text("✏️ <b>Send the text content</b> for this button. HTML tags supported.", parse_mode="HTML")

    elif data.startswith("admin_menu_btn_set_photo_"):
        idx = int(data.replace("admin_menu_btn_set_photo_", ""))
        db.set_pending(user_id, "await_menu_btn_photo", {"btn_index": idx})
        await query.message.reply_text("📷 <b>Send a photo</b> for this button.", parse_mode="HTML")

    elif data.startswith("admin_menu_btn_set_video_"):
        idx = int(data.replace("admin_menu_btn_set_video_", ""))
        db.set_pending(user_id, "await_menu_btn_video", {"btn_index": idx})
        await query.message.reply_text("🎥 <b>Send a video</b> for this button.", parse_mode="HTML")

    elif data.startswith("admin_menu_btn_clear_media_"):
        idx = int(data.replace("admin_menu_btn_clear_media_", ""))
        db.update_menu_button(idx, "photo", None)
        db.update_menu_button(idx, "video", None)
        await query.message.reply_text("🗑 Media cleared for this button.", reply_markup=admin_main_keyboard())

    elif data.startswith("admin_del_menu_btn_"):
        idx = int(data.replace("admin_del_menu_btn_", ""))
        db.remove_menu_button(idx)
        await query.message.reply_text("✅ Menu button removed.", reply_markup=admin_main_keyboard())

    # ── Preview & Publish ───────────────────────────────────────────
    elif data == "admin_preview_welcome":
        await query.message.reply_text("👁 <b>Preview of your welcome message:</b>", parse_mode="HTML")
        await send_welcome_message(query, context, show_verify=True)

    elif data == "admin_publish":
        await query.message.reply_text(
            "🚀 <b>Bot is Live!</b>\n\nAll settings are saved and active. New users will see the updated welcome message.",
            parse_mode="HTML",
            reply_markup=admin_main_keyboard()
        )

    elif data == "admin_back":
        await query.message.reply_text("🛠 Admin Panel:", reply_markup=admin_main_keyboard())


# ── Sub-menus ───────────────────────────────────────────────────────────────

async def show_welcome_menu(query):
    welcome = db.get_welcome()
    has_photo = "✅ Photo set" if welcome["photo"] else "❌ No photo"
    has_video = "✅ Video set" if welcome["video"] else "❌ No video"
    text_preview = (welcome["text"] or "")[:80] + ("..." if len(welcome.get("text") or "") > 80 else "")

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Set Text", callback_data="admin_set_welcome_text")],
        [InlineKeyboardButton("📷 Set Photo", callback_data="admin_set_welcome_photo"),
         InlineKeyboardButton("🎥 Set Video", callback_data="admin_set_welcome_video")],
        [InlineKeyboardButton("🗑 Clear Media", callback_data="admin_clear_welcome_media")],
        [InlineKeyboardButton("« Back", callback_data="admin_back")],
    ])
    await query.message.reply_text(
        f"📨 <b>Welcome Message Settings</b>\n\n"
        f"<b>Text preview:</b>\n<i>{text_preview or 'Not set'}</i>\n\n"
        f"<b>Media:</b> {has_photo} | {has_video}",
        parse_mode="HTML",
        reply_markup=kb
    )


async def show_channels_menu(query):
    channels = db.get_channels()
    kb_rows = []
    for ch in channels:
        kb_rows.append([InlineKeyboardButton(
            f"🗑 Remove: {ch['label']}", callback_data=f"admin_del_channel_{ch['id']}"
        )])
    kb_rows.append([InlineKeyboardButton("➕ Add Channel", callback_data="admin_add_channel")])
    kb_rows.append([InlineKeyboardButton("« Back", callback_data="admin_back")])

    ch_list = "\n".join([f"• {ch['label']} (<code>{ch['id']}</code>)" for ch in channels]) or "None added yet."
    await query.message.reply_text(
        f"📢 <b>Force Join Channels</b>\n\n{ch_list}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kb_rows)
    )


async def show_welcome_btns_menu(query):
    btns = db.get_welcome_buttons()
    kb_rows = []
    for i, btn in enumerate(btns):
        kb_rows.append([InlineKeyboardButton(
            f"🗑 Remove: {btn['label']}", callback_data=f"admin_del_welcome_btn_{i}"
        )])
    kb_rows.append([InlineKeyboardButton("➕ Add Button", callback_data="admin_add_welcome_btn")])
    kb_rows.append([InlineKeyboardButton("« Back", callback_data="admin_back")])

    btn_list = "\n".join([f"• {b['label']} → {b['url']}" for b in btns]) or "None added yet."
    await query.message.reply_text(
        f"🔘 <b>Welcome Inline Buttons</b>\n\n{btn_list}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kb_rows)
    )


async def show_menu_btns(query):
    btns = db.get_menu_buttons()
    kb_rows = []
    for i, btn in enumerate(btns):
        kb_rows.append([
            InlineKeyboardButton(f"✏️ Edit: {btn['label']}", callback_data=f"admin_edit_menu_btn_{i}"),
            InlineKeyboardButton("🗑", callback_data=f"admin_del_menu_btn_{i}")
        ])
    kb_rows.append([InlineKeyboardButton("➕ Add Menu Button", callback_data="admin_add_menu_btn")])
    kb_rows.append([InlineKeyboardButton("« Back", callback_data="admin_back")])

    await query.message.reply_text(
        f"📋 <b>Post-Verify Menu Buttons</b>\n\nThese appear after user verifies.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kb_rows)
    )


async def show_edit_menu_btn(query, idx: int):
    btns = db.get_menu_buttons()
    if idx >= len(btns):
        await query.message.reply_text("Button not found.")
        return
    btn = btns[idx]
    has_photo = "✅" if btn.get("photo") else "❌"
    has_video = "✅" if btn.get("video") else "❌"
    has_text = "✅" if btn.get("text") else "❌"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✏️ Set Text {has_text}", callback_data=f"admin_menu_btn_set_text_{idx}")],
        [InlineKeyboardButton(f"📷 Set Photo {has_photo}", callback_data=f"admin_menu_btn_set_photo_{idx}"),
         InlineKeyboardButton(f"🎥 Set Video {has_video}", callback_data=f"admin_menu_btn_set_video_{idx}")],
        [InlineKeyboardButton("🗑 Clear Media", callback_data=f"admin_menu_btn_clear_media_{idx}")],
        [InlineKeyboardButton("« Back", callback_data="admin_menu_btns")],
    ])
    await query.message.reply_text(
        f"✏️ <b>Editing button:</b> <code>{btn['label']}</code>",
        parse_mode="HTML",
        reply_markup=kb
    )


# ── Input Handler ───────────────────────────────────────────────────────────

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        return

    pending = db.get_pending(user_id)
    if not pending:
        return

    state = pending["state"]
    msg = update.message

    # ── Welcome text ────────────────────────────────────────────────
    if state == "await_welcome_text":
        text = msg.text or msg.caption or ""
        db.set_welcome_text(text)
        db.clear_pending(user_id)
        await msg.reply_text("✅ Welcome text saved!", reply_markup=admin_main_keyboard())

    elif state == "await_welcome_photo":
        if msg.photo:
            db.set_welcome_photo(msg.photo[-1].file_id)
            db.clear_pending(user_id)
            await msg.reply_text("✅ Welcome photo saved!", reply_markup=admin_main_keyboard())
        else:
            await msg.reply_text("❌ Please send a photo.")

    elif state == "await_welcome_video":
        if msg.video:
            db.set_welcome_video(msg.video.file_id)
            db.clear_pending(user_id)
            await msg.reply_text("✅ Welcome video saved!", reply_markup=admin_main_keyboard())
        else:
            await msg.reply_text("❌ Please send a video.")

    # ── Channel add (multi-step) ────────────────────────────────────
    elif state == "await_channel_id":
        channel_id = (msg.text or "").strip()
        if not channel_id:
            await msg.reply_text("❌ Invalid. Send channel ID like -1001234567890")
            return
        db.set_pending(user_id, "await_channel_label", {"channel_id": channel_id})
        await msg.reply_text("📢 <b>Step 2/3:</b> Send the <b>display label</b> for this channel (shown on button).", parse_mode="HTML")

    elif state == "await_channel_label":
        label = (msg.text or "").strip()
        ch_id = pending.get("channel_id")
        db.set_pending(user_id, "await_channel_url", {"channel_id": ch_id, "channel_label": label})
        await msg.reply_text("📢 <b>Step 3/3:</b> Send the <b>invite URL</b> for this channel (e.g. https://t.me/yourchannel).", parse_mode="HTML")

    elif state == "await_channel_url":
        url = (msg.text or "").strip()
        ch_id = pending.get("channel_id")
        label = pending.get("channel_label")
        added = db.add_channel(ch_id, label, url)
        db.clear_pending(user_id)
        if added:
            await msg.reply_text(f"✅ Channel <b>{label}</b> added!", parse_mode="HTML", reply_markup=admin_main_keyboard())
        else:
            await msg.reply_text("⚠️ Channel already exists.", reply_markup=admin_main_keyboard())

    # ── Welcome inline button (multi-step) ─────────────────────────
    elif state == "await_welcome_btn_label":
        label = (msg.text or "").strip()
        db.set_pending(user_id, "await_welcome_btn_url", {"btn_label": label})
        await msg.reply_text("🔘 <b>Step 2/2:</b> Send the <b>URL</b> for this button.", parse_mode="HTML")

    elif state == "await_welcome_btn_url":
        url = (msg.text or "").strip()
        label = pending.get("btn_label")
        db.add_welcome_button(label, url)
        db.clear_pending(user_id)
        await msg.reply_text(f"✅ Button <b>{label}</b> added!", parse_mode="HTML", reply_markup=admin_main_keyboard())

    # ── Menu button label ───────────────────────────────────────────
    elif state == "await_menu_btn_label":
        label = (msg.text or "").strip()
        idx = db.add_menu_button(label)
        db.clear_pending(user_id)
        await msg.reply_text(
            f"✅ Menu button <b>{label}</b> created!\n\nNow set its content via Admin Panel → Post-Verify Menu Buttons → Edit.",
            parse_mode="HTML",
            reply_markup=admin_main_keyboard()
        )

    # ── Menu button content ─────────────────────────────────────────
    elif state == "await_menu_btn_text":
        text = msg.text or msg.caption or ""
        idx = pending.get("btn_index")
        db.update_menu_button(idx, "text", text)
        db.clear_pending(user_id)
        await msg.reply_text("✅ Button text saved!", reply_markup=admin_main_keyboard())

    elif state == "await_menu_btn_photo":
        if msg.photo:
            idx = pending.get("btn_index")
            db.update_menu_button(idx, "photo", msg.photo[-1].file_id)
            db.update_menu_button(idx, "video", None)
            db.clear_pending(user_id)
            await msg.reply_text("✅ Button photo saved!", reply_markup=admin_main_keyboard())
        else:
            await msg.reply_text("❌ Please send a photo.")

    elif state == "await_menu_btn_video":
        if msg.video:
            idx = pending.get("btn_index")
            db.update_menu_button(idx, "video", msg.video.file_id)
            db.update_menu_button(idx, "photo", None)
            db.clear_pending(user_id)
            await msg.reply_text("✅ Button video saved!", reply_markup=admin_main_keyboard())
        else:
            await msg.reply_text("❌ Please send a video.")
