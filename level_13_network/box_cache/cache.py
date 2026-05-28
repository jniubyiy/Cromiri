from level_0.level_base import Box

class CacheBox(Box):
    def __init__(self):
        super().__init__("cache")

    def clear_cache(self):
        # Здесь будет вызов очистки кеша браузера
        pass

    def cache_size(self):
        return 0