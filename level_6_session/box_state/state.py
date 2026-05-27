import json, os
from level_0.level_base import Box
from logger import browser_logger

class StateBox(Box):
    def __init__(self):
        super().__init__("state")
        self._states = []
        self._filepath = None

    def load(self, base_dir):
        path = os.path.join(base_dir, "tab_states", "tab_states.json")
        self._filepath = path
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self._states = json.load(f)
            except Exception as e:
                browser_logger.exception(f"State load error: {e}")

    def save(self):
        if self._filepath:
            os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
            with open(self._filepath, 'w', encoding='utf-8') as f:
                json.dump(self._states, f, indent=2, ensure_ascii=False)

    def get_states(self):
        return self._states

    def set_states(self, states):
        self._states = states