"""
╔══════════════════════════════════════════╗
║        TIVRA PAY BOT - start.py          ║
║   Force Subscribe + Verify + Main Menu   ║
╚══════════════════════════════════════════╝

STRUCTURE:
  /start  →  Welcome Image + FSub Inline Buttons
             + Niche menu: [ ✅ Verify ]

  After Verify  →  Menu: [ 💳 Tivra Pay ] [ 📞 Support ]
                          [ 📢 Channel ] [ 📩 Contact Us ]

  Har button ka content niche clearly marked sections mein hai.
  Tum wahan apna text/image/video/inline button add kar sakte ho.
"""

from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    CallbackQuery,
    Message,
)

# ==============================================================
# ⚙️ CONFIG — Apni values yahan daalein
# ==============================================================

# Bot admins (unhe seedha main menu milega)
ADMINS = [5864182070]  # Apna Telegram user_id yahan daalein

# Required channels jinka member hona zaroori hai
# title  → button par dikhnay wala naam
# link   → invite / public link
REQUIRED_CHANNELS = [
    {"_id": "@@musicgroupxd",  "title": "Main Channel",   "link": "https://t.me/musicgroupxd"},
    {"_id": "@@phblicdarling",  "title": "Update Channel", "link": "https://t.me/phblicdarling"},
    # Aur channels yahan add karo...
]

# Welcome image ka FILE_ID ya local path
WELCOME_IMAGE = "AgACAgUAAxkBAAMCaeJgQzT8-hyPDedVeMWxiC_p02QAAmESaxvg8RBXjYEx96kJgK0BAAMCAAN5AAM7BA"  # Telegram ka file_id yahan paste karo

# ==============================================================
# 🎹 KEYBOARDS
# ==============================================================

def get_verify_keyboard():
    """Sirf Verify button — tab tak jab user ne join nahi kiya."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("✅ Verify")]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def get_main_keyboard():
    """Main menu — verify ke baad dikhta hai."""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("💳 Tivra Pay"),  KeyboardButton("📞 Support")],
            [KeyboardButton("📢 Channel"),    KeyboardButton("📩 Contact Us")],
        ],
        resize_keyboard=True,
    )


# ==============================================================
# 🔍 FSUB CHECK
# ==============================================================

async def check_fsub(client: Client, user_id: int):
    """
    Returns:
        True   — agar user ne sab channels join kar liye hain
        False  — koi channel missing hai
        missing_channels — missing channels ki list
    """
    if user_id in ADMINS:
        return True, []

    missing = []
    for ch in REQUIRED_CHANNELS:
        try:
            member = await client.get_chat_member(ch["_id"], user_id)
            # Banned ya left ho toh missing mein daalo
            if member.status.value in ("left", "banned", "kicked"):
                missing.append(ch)
        except Exception:
            missing.append(ch)

    return (len(missing) == 0), missing


# ==============================================================
# 📨 FSUB INLINE BUTTONS
# ==============================================================

def get_fsub_inline(missing_channels: list):
    """Missing channels ke inline join buttons."""
    buttons = []
    for ch in missing_channels:
        buttons.append([
            InlineKeyboardButton(
                text=f"📢 Join — {ch['title']}",
                url=ch["link"],
            )
        ])
    # Verify inline button (agar user niche menu se verify karna chahe)
    buttons.append([
        InlineKeyboardButton("✅ Verify Karo", callback_data="verify_fsub")
    ])
    return InlineKeyboardMarkup(buttons)


# ==============================================================
# 🏠 START HANDLER
# ==============================================================

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, msg: Message):
    user_id = msg.from_user.id
    user_name = msg.from_user.first_name

    # Admin → seedha main menu
    if user_id in ADMINS:
        await send_main_menu(client, msg.chat.id, user_name)
        return

    # FSub check
    joined, missing = await check_fsub(client, user_id)

    # ──────────────────────────────────────────────
    # WELCOME TEXT — yahan apna text likho
    # ──────────────────────────────────────────────
    welcome_text = f"""
<b>👋 Welcome, <a href='tg://user?id={user_id}'>{user_name}</a>!</b>

╔══════════════════════════════╗
║   <b>💳 TIVRA PAY BOT</b>          ║
║   Fast · Safe · Reliable     ║
╚══════════════════════════════╝

➻ Yahan apna welcome text likho.
➻ HTML formatting supported hai.
➻ <b>Bold</b>, <i>italic</i>, <code>code</code> sab kuch.

{'⚠️ <b>Pehle niche diye channels join karo, phir ✅ Verify dabao.</b>' if not joined else ''}
"""

    # Welcome image bhejo + fsub buttons (agar missing hai)
    if not joined:
        await client.send_photo(
            chat_id=msg.chat.id,
            photo=WELCOME_IMAGE,
            caption=welcome_text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=get_fsub_inline(missing),
        )
        # Niche sirf Verify button
        await client.send_message(
            chat_id=msg.chat.id,
            text="👇 <b>Sab join karne ke baad niche ka button dabao:</b>",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=get_verify_keyboard(),
        )
    else:
        # Already joined → seedha main menu
        await client.send_photo(
            chat_id=msg.chat.id,
            photo=WELCOME_IMAGE,
            caption=welcome_text,
            parse_mode=enums.ParseMode.HTML,
        )
        await send_main_menu(client, msg.chat.id, user_name)


# ==============================================================
# ✅ VERIFY — Reply Keyboard button se trigger
# ==============================================================

@Client.on_message(filters.text & filters.private & filters.regex("^✅ Verify$"))
async def verify_button_handler(client: Client, msg: Message):
    user_id = msg.from_user.id
    user_name = msg.from_user.first_name

    joined, missing = await check_fsub(client, user_id)

    if joined:
        await msg.reply_text(
            "✅ <b>Verification successful!</b>\n\nAb tum bot use kar sakte ho. 🎉",
            parse_mode=enums.ParseMode.HTML,
        )
        await send_main_menu(client, msg.chat.id, user_name)
    else:
        # Abhi bhi kuch channels missing hain
        await msg.reply_text(
            "❌ <b>Abhi bhi kuch channels join nahi kiye!</b>\n\nNiche diye buttons se join karo phir dobara try karo.",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=get_fsub_inline(missing),
        )


# ✅ VERIFY — Inline callback se bhi (welcome message ke button se)
@Client.on_callback_query(filters.regex("^verify_fsub$"))
async def verify_callback(client: Client, cb: CallbackQuery):
    user_id = cb.from_user.id
    user_name = cb.from_user.first_name

    joined, missing = await check_fsub(client, user_id)

    if joined:
        await cb.answer("✅ Verified!", show_alert=False)
        await send_main_menu(client, cb.message.chat.id, user_name)
    else:
        await cb.answer("❌ Abhi bhi kuch channels join nahi kiye!", show_alert=True)


# ==============================================================
# 🏠 MAIN MENU SENDER
# ==============================================================

async def send_main_menu(client: Client, chat_id: int, user_name: str):
    """Main menu bhejta hai — verify ke baad."""

    # ──────────────────────────────────────────────
    # MAIN MENU TEXT — yahan apna text likho
    # ──────────────────────────────────────────────
    text = f"""
<b>🏠 Main Menu</b>

👋 <b>Hello, {user_name}!</b>

Niche se apni service chunein:

💳 <b>Tivra Pay</b> — Payment gateway
📞 <b>Support</b>   — Help & assistance  
📢 <b>Channel</b>   — Updates channel
📩 <b>Contact Us</b> — Direct contact
"""

    await client.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=get_main_keyboard(),
    )


# ==============================================================
# 💳 TIVRA PAY BUTTON
# ==============================================================

@Client.on_message(filters.text & filters.private & filters.regex("^💳 Tivra Pay$"))
async def tivra_pay_handler(client: Client, msg: Message):
    # ──────────────────────────────────────────────
    # TIVRA PAY CONTENT — yahan apna content likho
    # ──────────────────────────────────────────────

    # TEXT (HTML format mein likho)
    text = f"""
<b>💳 TIVRA PAY</b>
━━━━━━━━━━━━━━━━━━━━

➻ Yahan Tivra Pay ka description likho.
➻ <b>Features, rates, process</b> — jo bhi batana ho.

<i>Example: UPI se payment karo, turant wallet mein aayega.</i>
"""

    # INLINE BUTTONS (optional — na chahiye toh None kar do)
    inline_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Pay Now", url="https://example.com/pay")],
        [InlineKeyboardButton("📋 View Rates", callback_data="view_rates")],
    ])

    # IMAGE bhejni hai? → send_photo use karo
    # VIDEO bhejni hai? → send_video use karo
    # Sirf text chahiye? → send_message use karo

    # Example: Text + Inline Buttons (image nahi)
    #await msg.reply_text(
    #    text=text,
    #    parse_mode=enums.ParseMode.HTML,
    #    reply_markup=inline_buttons,
    #)

    # Example: Image + Text + Inline Buttons (uncomment karke use karo)
     await msg.reply_photo(
         photo="FILE_ID_YA_URL",
         caption=text,
         parse_mode=enums.ParseMode.HTML,
         reply_markup=inline_buttons,
     )

    # Example: Video + Text + Inline Buttons (uncomment karke use karo)
    # await msg.reply_video(
    #     video="FILE_ID_YA_URL",
    #     caption=text,
    #     parse_mode=enums.ParseMode.HTML,
    #     reply_markup=inline_buttons,
    # )


# ==============================================================
# 📞 SUPPORT BUTTON
# ==============================================================

@Client.on_message(filters.text & filters.private & filters.regex("^📞 Support$"))
async def support_handler(client: Client, msg: Message):
    # ──────────────────────────────────────────────
    # SUPPORT CONTENT — yahan apna content likho
    # ──────────────────────────────────────────────

    text = f"""
<b>📞 SUPPORT</b>
━━━━━━━━━━━━━━━━━━━━

➻ Yahan support info likho.
➻ <b>Working hours, contact method</b> etc.

<i>Example: Mon–Sat, 10AM–8PM</i>
"""

    inline_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Contact Admin", url="https://t.me/youradmin")],
        [InlineKeyboardButton("💬 Support Group", url="https://t.me/yoursupportgroup")],
    ])

    await msg.reply_text(
        text=text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=inline_buttons,
    )


# ==============================================================
# 📢 CHANNEL BUTTON
# ==============================================================

@Client.on_message(filters.text & filters.private & filters.regex("^📢 Channel$"))
async def channel_handler(client: Client, msg: Message):
    # ──────────────────────────────────────────────
    # CHANNEL CONTENT — yahan apna content likho
    # ──────────────────────────────────────────────

    text = f"""
<b>📢 OUR CHANNELS</b>
━━━━━━━━━━━━━━━━━━━━

➻ Hmare channels join karo latest updates ke liye.
➻ <b>Offers, news, announcements</b> sab wahan milenge.
"""

    inline_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Main Channel", url="https://t.me/yourchannel1")],
        [InlineKeyboardButton("🔔 Update Channel", url="https://t.me/yourchannel2")],
    ])

    await msg.reply_text(
        text=text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=inline_buttons,
    )


# ==============================================================
# 📩 CONTACT US BUTTON
# ==============================================================

@Client.on_message(filters.text & filters.private & filters.regex("^📩 Contact Us$"))
async def contact_us_handler(client: Client, msg: Message):
    # ──────────────────────────────────────────────
    # CONTACT US CONTENT — yahan apna content likho
    # ──────────────────────────────────────────────

    text = f"""
<b>📩 CONTACT US</b>
━━━━━━━━━━━━━━━━━━━━

➻ Yahan contact details likho.
➻ <b>Email, Telegram, WhatsApp</b> — jo bhi relevant ho.

<i>Example: Business inquiries ke liye email karo.</i>
"""

    inline_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Email Us", url="mailto:youremail@example.com")],
        [InlineKeyboardButton("📱 WhatsApp", url="https://wa.me/91XXXXXXXXXX")],
    ])

    await msg.reply_text(
        text=text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=inline_buttons,
    )
