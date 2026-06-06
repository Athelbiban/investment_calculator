import os
from pathlib import Path
from dotenv import load_dotenv
from platformdirs import user_data_dir


load_dotenv()

# =========================================
# ROOT PROJECT DIRECTORY
# =========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# =========================================
# ХЕЛПЕРЫ ДЛЯ FAIL-FAST ВАЛИДАЦИИ
# =========================================
def _require_str(key: str) -> str:
    """Возвращает значение переменной окружения или вызывает исключение"""
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"[ERROR VALIDATION config.py] Переменная '{key}' не указана в .env")
    return value

def _require_file(key: str) -> str:
    """Проверяет наличие пути к файлу и возвращает его, иначе вызывает исключение"""
    file_path = _require_str(key)
    path_obj = Path(file_path)
    if not path_obj.is_absolute():
        path_obj = PROJECT_ROOT / path_obj
    if not path_obj.exists():
        raise EnvironmentError(f"[ERROR VALIDATION config.py] Файл '{file_path}' из переменной '{key}' не найден на диске")
    return str(path_obj)

def _require_path(key: Path) -> Path:
    """Проверяет наличие пути и возвращает его, иначе вызывает исключение"""
    if not key or key == Path('.'):
        raise EnvironmentError(f"[ERROR VALIDATION config.py] Не удалось определить наличие пути '{key}'")
    return key

# =========================================
# APPDATA DIRECTORIES
# =========================================
APP_DATA_DIR: Path = _require_path(Path(user_data_dir('InvestmentCalculator', 'StasVostrov')))
REPORTS_DIR: str | None = os.getenv('REPORTS_DIR')
CSV_DIR: str | None = os.getenv('CSV_DIR')

# =========================================
# MAIL CONFIG
# =========================================
MAIL_USERNAME: str | None = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD: str | None = os.getenv('MAIL_PASSWORD')
BROKERAGE_ACCOUNT_NUMBER: str = _require_str('BROKERAGE_ACCOUNT_NUMBER')
IMAP_SERVER: str = _require_str('IMAP_SERVER')
IMAP_FOLDER: str = _require_str('IMAP_FOLDER')

# =========================================
# DATABASE CONFIG
# =========================================
DB_NAME: str = _require_str('DB_NAME')
DB_USER: str = _require_str('DB_USER')
DB_PASSWORD: str = _require_str('DB_PASSWORD')
DB_HOST: str = _require_str('DB_HOST')
DB_PORT: str = _require_str('DB_PORT')

# =========================================
# GOOGLE-SHEETS CONFIG
# =========================================
GSHEETS_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
SERVICE_ACCOUNT_FILE: str = _require_file('SERVICE_ACCOUNT_FILE')
SPREADSHEET_ID: str = _require_str('SPREADSHEET_ID')
WORKSHEET_NAME: str = _require_str('WORKSHEET_NAME')

# =========================================
# CSV-FILES CONFIG
# =========================================
CSV_PORTFOLIO: str = os.getenv('CSV_PORTFOLIO') or str(APP_DATA_DIR / 'csv' / 'portfolio.csv')
CSV_TRANSACTIONS: str = os.getenv('CSV_TRANSACTIONS') or str(APP_DATA_DIR / 'csv' / 'transactions.csv')
CSV_CASHFLOW: str = os.getenv('CSV_CASHFLOW') or str(APP_DATA_DIR / 'csv' / 'cashflow.csv')
CSV_SECURITIES_MOVE: str = os.getenv('CSV_SECURITIES_MOVE') or str(APP_DATA_DIR / 'csv' / 'securities_move.csv')
