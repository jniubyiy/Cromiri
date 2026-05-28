from level_0.level_base import Box

class ProxyBox(Box):
    def __init__(self):
        super().__init__("proxy")
        self._proxy = None

    def set_proxy(self, type, host, port):
        self._proxy = {"type": type, "host": host, "port": port}

    def get_proxy(self):
        return self._proxy

    def clear_proxy(self):
        self._proxy = None