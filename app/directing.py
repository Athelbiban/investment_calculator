from pathlib import Path
from app.config import BROKER_REPORT_DIR


def get_directory() -> Path:
    """Возвращает путь к директории для отчетов брокера"""

    if BROKER_REPORT_DIR:
        target_dir = Path(BROKER_REPORT_DIR).expanduser().resolve()
    else:
        target_dir = Path.home() / "Downloads" / "broker_report"

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise PermissionError(f"Нет прав на создание или запись в директорию: {target_dir}")
    except OSError as e:
        raise OSError(f"Ошибка файловой системы при работе с {target_dir}: {e}")

    return target_dir


if __name__ == '__main__':
    print(f"Целевая директория: {get_directory()}")
