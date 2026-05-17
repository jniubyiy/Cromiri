# system/resource_manager.py
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QRunnable, QThreadPool
from logger import browser_logger

class BackgroundWorker(QThread):
    """Поток 2: фоновые задачи (расширения, скрипты, сетевые операции)."""
    task_completed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._running = False

    def add_task(self, task, *args, **kwargs):
        self._tasks.append((task, args, kwargs))
        if not self._running:
            self.start()

    def run(self):
        self._running = True
        while self._tasks:
            task, args, kwargs = self._tasks.pop(0)
            try:
                result = task(*args, **kwargs)
                self.task_completed.emit(result)
            except Exception as e:
                browser_logger.error(f"Ошибка в фоновой задаче: {e}")

    def stop(self):
        self._running = False
        self.wait()


class RenderWorker(QThread):
    """Поток 3: подготовка данных для рендеринга (предзагрузка, скриншоты)."""
    task_completed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []

    def add_task(self, task, *args, **kwargs):
        self._tasks.append((task, args, kwargs))
        if not self.isRunning():
            self.start()

    def run(self):
        while self._tasks:
            task, args, kwargs = self._tasks.pop(0)
            try:
                result = task(*args, **kwargs)
                self.task_completed.emit(result)
            except Exception as e:
                browser_logger.error(f"Ошибка в задаче рендеринга: {e}")

    def stop(self):
        self.wait()


class TabTask(QRunnable):
    """Задача для вкладки (выполняется в пуле потоков)."""
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            browser_logger.error(f"Ошибка в задаче вкладки: {e}")


class ResourceManager:
    """
    Управляет распределением потоков согласно загрузке CPU/GPU.
    Поток 1 – GUI (main)
    Поток 2 – BackgroundWorker (расширения, скрипты)
    Поток 3 – RenderWorker (подготовка рендеринга)
    Поток 4+ – QThreadPool для вкладок (динамический)
    """
    def __init__(self, load_balancer):
        self.load_balancer = load_balancer
        self.background_worker = BackgroundWorker()
        self.render_worker = RenderWorker()
        self.tab_pool = QThreadPool()
        self.tab_pool.setMaxThreadCount(self.load_balancer.cpu.max_workers)

    def submit_background_task(self, func, *args, **kwargs):
        if self.load_balancer.cpu.is_overloaded(90):
            browser_logger.warning("CPU перегружен, задача отложена")
            return
        self.background_worker.add_task(func, *args, **kwargs)

    def submit_render_task(self, func, *args, **kwargs):
        if self.load_balancer.gpu.is_heavy_load(80):
            browser_logger.warning("GPU перегружен, задача рендеринга отложена")
            return
        self.render_worker.add_task(func, *args, **kwargs)

    def submit_tab_task(self, func, *args, **kwargs):
        task = TabTask(func, *args, **kwargs)
        self.tab_pool.start(task)

    def shutdown(self):
        self.background_worker.stop()
        self.render_worker.stop()
        self.tab_pool.clear()