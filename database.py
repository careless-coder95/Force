import json
import os
from typing import Any, Dict, Optional

DB_FILE = "bot_data.json"

DEFAULT_DATA = {
    "welcome": {
        "text": "<b>Welcome to our community bot!</b>\n\nPlease join all required channels to get access.",
        "photo": None,
        "video": None,
        "force_join_channels": [],
        "inline_buttons": [],
    },
    "menu_buttons": [],
    "verified_users": [],
    "pending_input": {}
}


class Database:
    def __init__(self):
        self._load()

    def _load(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                self.data = json.load(f)
            # Migrate missing keys
            for key, val in DEFAULT_DATA.items():
                if key not in self.data:
                    self.data[key] = val
            self._save()
        else:
            self.data = json.loads(json.dumps(DEFAULT_DATA))
            self._save()

    def _save(self):
        with open(DB_FILE, "w") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    # ── Welcome config ──────────────────────────────────────────────

    def get_welcome(self) -> Dict:
        return self.data["welcome"]

    def set_welcome_text(self, text: str):
        self.data["welcome"]["text"] = text
        self._save()

    def set_welcome_photo(self, file_id: Optional[str]):
        self.data["welcome"]["photo"] = file_id
        self.data["welcome"]["video"] = None  # only one media at a time
        self._save()

    def set_welcome_video(self, file_id: Optional[str]):
        self.data["welcome"]["video"] = file_id
        self.data["welcome"]["photo"] = None
        self._save()

    def clear_welcome_media(self):
        self.data["welcome"]["photo"] = None
        self.data["welcome"]["video"] = None
        self._save()

    # ── Force join channels ─────────────────────────────────────────

    def get_channels(self):
        return self.data["welcome"]["force_join_channels"]

    def add_channel(self, channel_id: str, label: str, url: str):
        channels = self.get_channels()
        # avoid duplicates
        for ch in channels:
            if ch["id"] == channel_id:
                return False
        channels.append({"id": channel_id, "label": label, "url": url})
        self._save()
        return True

    def remove_channel(self, channel_id: str):
        channels = self.get_channels()
        self.data["welcome"]["force_join_channels"] = [c for c in channels if c["id"] != channel_id]
        self._save()

    # ── Welcome inline buttons ──────────────────────────────────────

    def get_welcome_buttons(self):
        return self.data["welcome"]["inline_buttons"]

    def add_welcome_button(self, label: str, url: str):
        self.data["welcome"]["inline_buttons"].append({"label": label, "url": url})
        self._save()

    def remove_welcome_button(self, index: int):
        btns = self.data["welcome"]["inline_buttons"]
        if 0 <= index < len(btns):
            btns.pop(index)
            self._save()

    # ── Post-verify menu buttons ────────────────────────────────────

    def get_menu_buttons(self):
        return self.data["menu_buttons"]

    def add_menu_button(self, label: str):
        btn = {
            "label": label,
            "text": None,
            "photo": None,
            "video": None,
        }
        self.data["menu_buttons"].append(btn)
        self._save()
        return len(self.data["menu_buttons"]) - 1  # return index

    def update_menu_button(self, index: int, field: str, value: Any):
        btns = self.data["menu_buttons"]
        if 0 <= index < len(btns):
            btns[index][field] = value
            self._save()

    def remove_menu_button(self, index: int):
        btns = self.data["menu_buttons"]
        if 0 <= index < len(btns):
            btns.pop(index)
            self._save()

    # ── Verified users ──────────────────────────────────────────────

    def is_verified(self, user_id: int) -> bool:
        return user_id in self.data["verified_users"]

    def verify_user(self, user_id: int):
        if user_id not in self.data["verified_users"]:
            self.data["verified_users"].append(user_id)
            self._save()

    # ── Pending admin input ─────────────────────────────────────────

    def set_pending(self, user_id: int, state: str, extra: dict = {}):
        self.data["pending_input"][str(user_id)] = {"state": state, **extra}
        self._save()

    def get_pending(self, user_id: int) -> Optional[Dict]:
        return self.data["pending_input"].get(str(user_id))

    def clear_pending(self, user_id: int):
        self.data["pending_input"].pop(str(user_id), None)
        self._save()


db = Database()
