import json, os
from datetime import datetime
from level_0.level_base import Box
from logger import browser_logger

class BufferBox(Box):
    def __init__(self):
        super().__init__("buffer")
        self.buffers = {"actions":[], "navigation":[], "settings_changes":[], "page_events":[]}
        self.files = {}

    def load_all(self, base_dir):
        dirs = {
            "actions": os.path.join(base_dir, "actions"),
            "navigation": os.path.join(base_dir, "navigation"),
            "settings_changes": os.path.join(base_dir, "settings_changes"),
            "page_events": os.path.join(base_dir, "page_events"),
        }
        for d in dirs.values():
            os.makedirs(d, exist_ok=True)
        for key, path in dirs.items():
            filepath = os.path.join(path, f"{key}.json")
            self.files[key] = filepath
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        self.buffers[key] = data
                except Exception as e:
                    browser_logger.exception(f"Buffer load error {key}: {e}")

    def save_all(self):
        for key, path in self.files.items():
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.buffers[key], f, indent=2, ensure_ascii=False)
            except Exception as e:
                browser_logger.exception(f"Buffer save error {key}: {e}")

    def log_action(self, action_type, details=None):
        self.buffers["actions"].append({
            "timestamp": datetime.now().isoformat(),
            "type": action_type,
            "details": details or {}
        })