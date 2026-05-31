import time
import sys
import threading
from contextlib import contextmanager


class AnimationManager:
    """Управление анимацией в консоли"""

    def __init__(self):
        self._frames = ['. ', '.. ', '...', ' ..', '  .', '   ']
        self._interval = 0.4
        self.default_message = "Пожалуйста, подождите"
        self._current_message = self.default_message
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def _animate(self) -> None:
        """Внутренний метод анимации (выполняется в отдельном потоке)"""
        idx = 0
        while not self._stop_event.is_set():
            with self._lock:
                msg = self._current_message

            frame = self._frames[idx % len(self._frames)]
            sys.stdout.write(f"\r{msg}{frame}")
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
            new_thread = threading.Thread(target=self._animate, daemon=True)
            self._thread = new_thread
            new_thread.start()

    def stop(self) -> None:
        """Остановка анимации"""
        with self._lock:
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=0.5)
            self._thread = None

    @contextmanager
    def paused(self):
        """Приостановка анимации на время интерактивного ввода"""
        was_running =self._thread is not None and self._thread.is_alive()
        if was_running:
            self.stop()
        try:
            yield
        finally:
            if was_running:
                self.start()

    @contextmanager
    def status_context(self, message):
        with self._lock:
            old_message = self._current_message
            self._current_message = message
        try:
            yield
        finally:
            with self._lock:
                self._current_message = old_message
