from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from logger import browser_logger

# Порядок уровней для определения приоритета (чем меньше номер, тем выше приоритет)
LEVEL_ORDER = {
    "DeviceLevel": 1,
    "ResourceLevel": 2,
    "ManagerLevel": 3,
    "FileLevel": 4,
    "SettingsLevel": 5,
    "SessionLevel": 6,
    "ExtensionsLevel": 7,
    "UILevel": 8,
}

# -------------------------------------------------------------------
# 1. Базовый класс бокса
# -------------------------------------------------------------------
class Box:
    """Базовый класс для всех боксов."""
    def __init__(self, box_name: str):
        self.box_name = box_name
        self.level_number = 99   # будет переопределён при регистрации

# -------------------------------------------------------------------
# 2. Обёртка бокса
# -------------------------------------------------------------------
class BoxWrapper:
    """
    Обёртка бокса.
    - Контролирует доступ к методам бокса.
    - Логирует вызовы.
    """
    def __init__(self, box: Box, level_name: str):
        self._box = box
        self._level_name = level_name
        self._allowed_methods: set[str] = set()

    def expose_methods(self, *methods: str):
        """Регистрирует публичные методы бокса."""
        self._allowed_methods.update(methods)

    def call(self, method: str, *args, **kwargs) -> Any:
        if method not in self._allowed_methods:
            raise AttributeError(
                f"Метод '{method}' не является публичным для бокса '{self._box.box_name}'"
            )
        browser_logger.info(
            f"[{self._level_name}] Бокс '{self._box.box_name}' вызывает метод '{method}'"
            f" (общение бокса с уровнем {self._level_name})"
        )
        func = getattr(self._box, method, None)
        if func is None:
            raise AttributeError(
                f"Бокс '{self._box.box_name}' не имеет метода '{method}'"
            )
        result = func(*args, **kwargs)
        browser_logger.debug(
            f"[{self._level_name}] Бокс '{self._box.box_name}' метод '{method}' выполнен"
        )
        return result

# -------------------------------------------------------------------
# 3. Ядро уровня
# -------------------------------------------------------------------
class LevelCore(ABC):
    """
    Ядро уровня.
    - Хранит обёрнутые боксы.
    - Перенаправляет запросы к боксам.
    """
    def __init__(self, level_name: str):
        self.level_name = level_name
        self._box_wrappers: Dict[str, BoxWrapper] = {}

    def register_box(self, box: Box) -> BoxWrapper:
        # Устанавливаем номер уровня для приоритета
        box.level_number = LEVEL_ORDER.get(self.level_name, 99)
        wrapper = BoxWrapper(box, self.level_name)
        self._box_wrappers[box.box_name] = wrapper
        browser_logger.info(f"[{self.level_name}] Зарегистрирован бокс '{box.box_name}'")
        return wrapper

    def send_to_box(self, box_name: str, method: str, *args, **kwargs) -> Any:
        wrapper = self._box_wrappers.get(box_name)
        if wrapper is None:
            raise KeyError(f"Бокс '{box_name}' не найден на уровне '{self.level_name}'")
        browser_logger.info(
            f"[{self.level_name}] Уровень передаёт запрос боксу '{box_name}' для выполнения метода '{method}'"
        )
        return wrapper.call(method, *args, **kwargs)

    @abstractmethod
    def setup_boxes(self):
        """Создание и регистрация боксов."""
        pass

    def reload_box(self, box_name: str):
        """Перезагружает указанный бокс (по умолчанию не поддерживается)."""
        raise NotImplementedError("Этот уровень не поддерживает перезагрузку боксов")

# -------------------------------------------------------------------
# 4. Запрос между уровнями
# -------------------------------------------------------------------
class LevelRequest:
    """Структура запроса, путешествующего по цепочке уровней."""
    def __init__(self, target_level: str, box_name: str, method: str, args: tuple, kwargs: dict, source_level: str):
        self.target_level = target_level
        self.box_name = box_name
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.source_level = source_level

# -------------------------------------------------------------------
# 5. Обёртка уровня
# -------------------------------------------------------------------
class LevelWrapper(ABC):
    """
    Обёртка уровня.
    - Принимает запросы от соседей.
    - Проверяет права доступа.
    - Либо исполняет запрос (если цель — этот уровень), либо передаёт дальше.
    """
    def __init__(self, core: LevelCore):
        self._core = core
        self._upper: Optional[LevelWrapper] = None   # сосед сверху (больший номер)
        self._lower: Optional[LevelWrapper] = None   # сосед снизу (меньший номер)
        self._allowed_incoming: Dict[str, List[str]] = {}  # {source_level: [methods]}
        self._public_api: set[str] = set()

    def set_neighbors(self, lower: Optional['LevelWrapper'] = None, upper: Optional['LevelWrapper'] = None):
        self._lower = lower
        self._upper = upper

    def register_public_api(self, *methods: str):
        self._public_api.update(methods)

    def allow_request_from(self, source_level: str, methods: List[str]):
        """Разрешает входящие запросы от указанного уровня."""
        self._allowed_incoming[source_level] = methods

    def handle_request(self, request: LevelRequest) -> Any:
        browser_logger.info(
            f"[{self._core.level_name}] Получен запрос от '{request.source_level}' "
            f"к '{request.target_level}' -> box='{request.box_name}' method='{request.method}'"
        )
        allowed = self._allowed_incoming.get(request.source_level, [])
        if request.method not in allowed and "*" not in allowed:
            raise PermissionError(
                f"Уровень '{request.source_level}' не имеет права вызывать "
                f"'{request.method}' на уровне '{self._core.level_name}'"
            )
        if request.target_level == self._core.level_name:
            browser_logger.info(
                f"[{self._core.level_name}] Запрос адресован этому уровню, выполняется"
            )
            return self._core.send_to_box(request.box_name, request.method, *request.args, **request.kwargs)
        direction = self._get_direction(request.target_level)
        if direction == "upper" and self._upper is not None:
            browser_logger.info(
                f"[{self._core.level_name}] Передача запроса вверх к '{self._upper._core.level_name}'"
            )
            return self._upper.handle_request(request)
        elif direction == "lower" and self._lower is not None:
            browser_logger.info(
                f"[{self._core.level_name}] Передача запроса вниз к '{self._lower._core.level_name}'"
            )
            return self._lower.handle_request(request)
        else:
            raise RuntimeError(
                f"Не удалось доставить запрос к уровню '{request.target_level}'"
            )

    def send_request(self, target_level: str, box_name: str, method: str, *args, **kwargs) -> Any:
        browser_logger.info(
            f"[{self._core.level_name}] Отправка запроса к '{target_level}' "
            f"box='{box_name}' method='{method}' (межуровневое взаимодействие)"
        )
        request = LevelRequest(
            target_level=target_level,
            box_name=box_name,
            method=method,
            args=args,
            kwargs=kwargs,
            source_level=self._core.level_name
        )
        return self.handle_request(request)

    def _get_direction(self, target_level: str) -> str:
        current = LEVEL_ORDER.get(self._core.level_name, 0)
        target = LEVEL_ORDER.get(target_level, 0)
        return "upper" if target > current else "lower"

    def __getattr__(self, name: str):
        if name.startswith('_'):
            raise AttributeError(f"Доступ к защищённому атрибуту {name} запрещён")
        if name in self._public_api:
            browser_logger.info(
                f"[{self._core.level_name}] Прямой вызов публичного метода '{name}'"
            )
            func = getattr(self._core, name, None)
            if func is not None:
                return func
        raise AttributeError(
            f"'{name}' не является публичным методом уровня '{self._core.level_name}'"
        )