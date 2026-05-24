import time
import sys
import threading


class AnimationManager:
    """Управление анимацией в консоли"""

    def __init__(self):
        self._frames = ['. ', '.. ', '...', ' ..', '  .', '   ']
        self._interval = 0.4
        self._message = "Пожалуйста, подождите"
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def _animate(self) -> None:
        """Внутренний метод анимации (выполняется в отдельном потоке)"""
        idx = 0
        while not self._stop_event.is_set():
            frame = self._frames[idx % len(self._frames)]
            sys.stdout.write(f"\r{self._message}{frame}")
            sys.stdout.flush()
            idx += 1
            time.sleep(self._interval)
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    def start(self) -> None:
        """Запуск анимации"""
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        """Остановка анимации"""
        with self._lock:
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=0.5)
            self._thread = None
