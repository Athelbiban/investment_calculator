import logging
import sys
from pathlib import Path
from types import TracebackType
from app.directing import get_directory
from app.config import APP_LOG


class AppLogger:
    """
    Класс-обертка для логирования приложения.
    Настраивает логгер и предоставляет удобные методы.
    """

    def __init__(self, name: str = "InvestmentCalculator"):
        """
        Инициализирует логгер с настройками для консоли и файла.
        :param name: Имя логгера (по умолчанию имя приложения)
        """

        self.logger = logging.getLogger(name)

        if self.logger.handlers:
            return

        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        try:
            get_directory('logs')
            file_handler = logging.FileHandler(filename=APP_LOG, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Не удалось настроить файловое логирование: {e}", file=sys.stderr)

    def log_command_start(self, command: str) -> None:
        """Логирует начало выполнения команд"""
        self.logger.info(f"Начало выполнения команды: {command}")

    def log_command_success(self, command: str, details: str = '') -> None:
        """Логирует успешное выполнение команды"""
        msg = f"Команда '{command}' выполнена успешно"
        if details:
            msg += f": {details}"
        self.logger.info(msg)

    def log_command_error(self, command: str, error: Exception) -> None:
        """Логирует ошибку выполнения команды"""
        self.logger.error(f"Ошибка во время выполнения команды '{command}': {error}", exc_info=True)

    def log_file_operation(self, operation: str, file_path: Path, success: bool) -> None:
        """Логирует операции с файлами"""
        status = "успешно" if success else "с ошибкой"
        self.logger.info(f"Операция '{operation}' с файлом {file_path} завершена {status}")

    def log_network_error(self, service: str, error: Exception) -> None:
        """Логирует сетевые ошибки (mail, Google API)"""
        self.logger.error(f"При работе с '{service}' возникла сетевая ошибка: {error}", exc_info=True)

    def log_critical(self,
                     message: str,
                     exc_info: bool | tuple[type[BaseException], BaseException, TracebackType | None] | None = None
                     ) -> None:
        """Логирует критическую ошибку (для глобального обработчика)"""
        self.logger.critical(message, exc_info=exc_info)

    def debug(self, message: str, *args, **kwargs) -> None:
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        self.logger.critical(message, *args, **kwargs)
