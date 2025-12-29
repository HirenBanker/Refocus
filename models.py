import json
import os

DATA_FILE = os.path.join("data", "user_data.json")

DEFAULT_DATA = {
    "user": {
        "username": "User",
        "email": "user@example.com",
        "phone": "",
        "profile_pic": "default.png"
    },
    "blocked_sites": [],
    "settings": {
        "blocking_active": False,
        "block_until": None,
        "strict_mode": True  # Default to True as per requirements ("strict blocking")
    }
}

class DataManager:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(self.data_file):
            self.save_data(DEFAULT_DATA)
            return DEFAULT_DATA.copy()
        
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Ensure structure is up to date (simple migration)
                if "strict_mode" not in data.get("settings", {}):
                    if "settings" not in data:
                        data["settings"] = DEFAULT_DATA["settings"].copy()
                    else:
                        data["settings"]["strict_mode"] = True
                return data
        except (json.JSONDecodeError, IOError):
            return DEFAULT_DATA.copy()

    def save_data(self, data=None):
        if data is not None:
            self.data = data
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_user(self):
        return self.data.get("user", DEFAULT_DATA["user"])

    def update_user(self, username=None, email=None, phone=None):
        if username:
            self.data["user"]["username"] = username
        if email:
            self.data["user"]["email"] = email
        if phone is not None:
            self.data["user"]["phone"] = phone
        self.save_data()

    def get_blocked_sites(self):
        return self.data.get("blocked_sites", [])

    def add_site(self, url):
        if url and url not in self.data["blocked_sites"]:
            self.data["blocked_sites"].append(url)
            self.save_data()

    def remove_site(self, url):
        if url in self.data["blocked_sites"]:
            self.data["blocked_sites"].remove(url)
            self.save_data()

    def update_blocking_state(self, active, until=None, strict=True):
        self.data["settings"]["blocking_active"] = active
        self.data["settings"]["block_until"] = until
        self.data["settings"]["strict_mode"] = strict
        self.save_data()

    def get_blocking_state(self):
        return self.data.get("settings", DEFAULT_DATA["settings"])
