from pathlib import Path
from typing import Literal
from app.config import REPORTS_DIR, CSV_DIR, APP_DATA_DIR, LOGS_DIR


DirectoryType = Literal['reports', 'csv', 'logs']

def get_directory(file_dir: DirectoryType = 'reports') -> Path:
    """
    Возвращает путь к директории для HTML-отчетов брокера или CSV-файлов.
    Автоматически создает директорию, если она не существует.

    Args:
        file_dir: Тип директории ('reports' для HTML-отчетов, 'csv' для CSV-файлов)

    Returns:
        Path: Абсолютный путь к существующей директории

    Raises:
        PermissionError: Если нет прав на создание директории
        OSError: При других ошибках файловой системы
        ValueError: Если передан недопустимый аргумент

    Examples:
        >>> get_directory('reports')
        PosixPath('/home/user/.local/share/InvestmentCalculator/reports')
        WindowsPath('C:\\Users\\<User>\\AppData\\Local\\InvestmentCalculator\\reports')
        >>> get_directory('csv')
        PosixPath('home/user/.local/share/InvestmentCalculator/csv')
        WindowsPath('C:\\Users\\<User>\\AppData\\Local\\InvestmentCalculator\\csv')
        >>> get_directory('logs')
        PosixPath('home/user/.local/share/InvestmentCalculator/logs')
        WindowsPath('C:\\Users\\<User>\\AppData\\Local\\InvestmentCalculator\\logs')
    """

    if file_dir == 'reports':
        raw_dir = REPORTS_DIR
    elif file_dir == 'csv':
        raw_dir = CSV_DIR
    elif file_dir == 'logs':
        raw_dir = LOGS_DIR
    else:
        raise ValueError(f"[НЕДОПУСТИМЫЙ АРГУМЕНТ] Передан аргумент: {file_dir}. "
                         f"Возможные значения: 'reports', 'csv', 'logs'")

    if raw_dir:
        target_dir = Path(raw_dir).expanduser().resolve()
    else:
        target_dir = APP_DATA_DIR / file_dir

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise PermissionError(f"[НЕТ ПРАВ] Нет прав на создание или запись в директорию '{target_dir}'\n"
                              f"Попробуйте запустить приложение с правами администратора "
                              f"или измените права на директорию")
    except OSError as e:
        raise OSError(f"[ОШИБКА СИСТЕМЫ] Ошибка файловой системы при работе с директорией '{target_dir}': {e}")

    return target_dir


if __name__ == '__main__':
    print(f"Директория отчётов: {get_directory('reports')}")
    print(f"Директория CSV: {get_directory('csv')}")
    print(f"Директория логов: {get_directory('logs')}")
