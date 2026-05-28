from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_manager.download_manager import DownloadManagerBox

class DownloadLevelCore(LevelCore):
    def __init__(self):
        super().__init__("DownloadLevel")

    def setup_boxes(self):
        download_wrapper = self.register_box(DownloadManagerBox())
        download_wrapper.expose_methods("add", "pause", "resume", "cancel", "get_queue")

    def add_download(self, url, file_path):
        self.send_to_box("download_manager", "add", url, file_path)

    def pause_download(self, download_id):
        self.send_to_box("download_manager", "pause", download_id)

    def resume_download(self, download_id):
        self.send_to_box("download_manager", "resume", download_id)

    def cancel_download(self, download_id):
        self.send_to_box("download_manager", "cancel", download_id)

    def get_download_queue(self):
        return self.send_to_box("download_manager", "get_queue")


class DownloadLevelWrapper(LevelWrapper):
    def __init__(self):
        core = DownloadLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("add_download", "pause_download", "resume_download", "cancel_download", "get_download_queue")
        self.allow_request_from("*", ["add", "pause", "resume", "cancel", "get_queue"])

    def initialize(self):
        pass