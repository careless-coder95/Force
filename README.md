# 🤖 Telegram Force Join Bot — Full Guide

## 📁 File Structure
```
bot/
├── bot.py              ← Main entry point
├── config.py           ← Bot token + Owner IDs
├── database.py         ← JSON-based storage
├── helpers.py          ← Shared utilities
├── requirements.txt
├── bot_data.json       ← Auto-created on first run
└── handlers/
    ├── __init__.py
    ├── user_handler.py ← /start, verify, menu buttons
    └── admin_handler.py← /admin panel, all settings
```

---

## ⚙️ Setup Steps

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Edit `config.py`
```python
BOT_TOKEN = "paste_your_bot_token_here"

OWNER_IDS = [
    123456789,   # Your Telegram user ID
    987654321,   # Second owner (optional)
    111222333,   # Third owner (optional)
]
```
> Get your user ID from: @userinfobot  
> Get bot token from: @BotFather

### 3. Run the bot
```bash
python bot.py
```

---

## 🛠️ Admin Panel — `/admin`

Only owners (from OWNER_IDS) can access this.

### What you can configure:

| Section | What you can do |
|--------|----------------|
| 📨 Welcome Message | Set text (HTML), photo or video |
| 📢 Force Join Channels | Add/remove channels with labels & URLs |
| 🔘 Welcome Inline Buttons | Add/remove URL buttons shown on welcome |
| 📋 Post-Verify Menu Buttons | Add/remove/edit buttons after verification |
| 👁 Preview | Preview welcome message before publishing |
| 🚀 Publish | Confirm everything is live |

---

## 📝 HTML Tags in Text

When setting any text, you can use these HTML tags:

```
<b>bold text</b>
<i>italic text</i>
<u>underlined</u>
<blockquote expandable>collapsible quote</blockquote>
<code>monospace</code>
<a href="https://example.com">link text</a>
```

---

## 📢 Adding Force Join Channels

1. Open `/admin` → Force Join Channels → Add Channel
2. Send Channel ID (e.g. `-1001234567890`)
   - To get channel ID: forward a message from the channel to @userinfobot
3. Send display label (e.g. `My Main Channel`)
4. Send invite URL (e.g. `https://t.me/mychannel`)

> ⚠️ Make sure your bot is **admin** in all force-join channels!

---

## 🔘 Post-Verify Menu Buttons

These appear after a user joins all channels and clicks Verify.

Examples: `Support Group`, `Contact Owner`, `App Link`

Each button can have:
- Text (with HTML formatting)
- Photo
- Video
- Or any combination (text + photo/video)

---

## 🔄 User Flow

```
User sends /start
    ↓
Bot sends Welcome message (photo/video + text + inline buttons + Verify button)
    ↓
User clicks channel join buttons → joins all channels
    ↓
User clicks ✅ Verify Access
    ↓
Bot checks membership in all channels
    ↓
If not joined → Shows alert with missing channels
If all joined → Access granted! Shows post-verify menu buttons
```

---

## 👑 Multiple Owners

Just add multiple IDs to `OWNER_IDS` in `config.py`:

```python
OWNER_IDS = [
    111111111,
    222222222,
    333333333,
    444444444,
]
```

All owners have equal access to `/admin`.

---

## 💾 Data Storage

All settings are saved in `bot_data.json` automatically.  
No database setup needed. The file is created on first run.
