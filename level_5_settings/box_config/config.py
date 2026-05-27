from level_0.level_base import Box

class SettingsConfigBox(Box):
    def __init__(self):
        super().__init__("config")
        self._data = {}
    def set_data(self, data):
        self._data = data
    def get(self, key, default=None):
        keys = key.split('.')
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    def set(self, key, value):
        keys = key.split('.')
        d = self._data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value