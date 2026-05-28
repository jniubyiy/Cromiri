from level_0.level_base import LevelWrapper, LevelCore
from .box_proxy.proxy import ProxyBox
from .box_cache.cache import CacheBox

class NetworkLevelCore(LevelCore):
    def __init__(self):
        super().__init__("NetworkLevel")

    def setup_boxes(self):
        proxy_wrapper = self.register_box(ProxyBox())
        proxy_wrapper.expose_methods("set_proxy", "get_proxy", "clear_proxy")
        cache_wrapper = self.register_box(CacheBox())
        cache_wrapper.expose_methods("clear_cache", "cache_size")

    def set_proxy(self, type, host, port):
        self.send_to_box("proxy", "set_proxy", type, host, port)

    def get_proxy(self):
        return self.send_to_box("proxy", "get_proxy")

    def clear_cache(self):
        self.send_to_box("cache", "clear_cache")

class NetworkLevelWrapper(LevelWrapper):
    def __init__(self):
        core = NetworkLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("set_proxy", "get_proxy", "clear_cache")
        self.allow_request_from("*", ["set_proxy", "get_proxy", "clear_proxy", "clear_cache", "cache_size"])

    def initialize(self):
        pass