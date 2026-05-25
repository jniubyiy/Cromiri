from abc import ABC, abstractmethod
from typing import Any, Dict, List
from logger import browser_logger

class LevelWrapper(ABC):
    def __init__(self, core: 'LevelCore'):
        self._core = core
        self._allowed_external_calls: List[str] = []
        self._internal_interface: Dict[str, Any] = {}

    def register_external_api(self, method_names: List[str]):
        self._allowed_external_calls.extend(method_names)

    def register_internal_api(self, api_dict: Dict[str, Any]):
        self._internal_interface.update(api_dict)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(f"Доступ к защищённому атрибуту {name} запрещён")
        if name in self._allowed_external_calls:
            browser_logger.debug(f"[{self._core.level_name}] Вызов внешнего метода: {name}")
            return getattr(self._core, name)
        raise AttributeError(f"Внешний вызов '{name}' не разрешён на уровне {self._core.level_name}")

    @abstractmethod
    def initialize(self):
        pass

class LevelCore(ABC):
    def __init__(self, level_name: str):
        self.level_name = level_name
        self._boxes: Dict[str, Any] = {}
        self._neighbors: Dict[str, LevelWrapper] = {}

    def register_box(self, name: str, box_instance: Any):
        self._boxes[name] = box_instance
        browser_logger.debug(f"[{self.level_name}] Бокс '{name}' зарегистрирован")

    def get_box(self, name: str) -> Any:
        box = self._boxes.get(name)
        if box:
            browser_logger.debug(f"[{self.level_name}] Запрошен бокс '{name}'")
        else:
            browser_logger.warning(f"[{self.level_name}] Бокс '{name}' не найден!")
        return box

    def connect_neighbor(self, direction: str, neighbor_wrapper: LevelWrapper):
        self._neighbors[direction] = neighbor_wrapper
        browser_logger.debug(f"[{self.level_name}] Подключён соседний уровень: {direction}")

    def send_to_neighbor(self, direction: str, method: str, *args, **kwargs):
        neighbor = self._neighbors.get(direction)
        if not neighbor:
            raise RuntimeError(f"[{self.level_name}] Нет соседа с направлением '{direction}'")
        browser_logger.debug(f"[{self.level_name}] → Запрос к соседу '{direction}'.{method}")
        func = getattr(neighbor, method, None)
        if func is None:
            raise AttributeError(f"Метод '{method}' не найден у соседнего уровня '{direction}'")
        result = func(*args, **kwargs)
        browser_logger.debug(f"[{self.level_name}] ← Ответ от '{direction}'.{method}")
        return result

    @abstractmethod
    def setup_boxes(self):
        pass