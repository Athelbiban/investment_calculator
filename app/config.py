import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

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
    if not Path(file_path).exists():
        raise EnvironmentError(f"[ERROR VALIDATION config.py] Файл '{file_path}' из переменной '{key}' не найден на диске")
    return file_path

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
CSV_FILE: str = _require_file('CSV_FILE')
SPREADSHEET_ID: str = _require_str('SPREADSHEET_ID')
WORKSHEET_NAME: str = _require_str('WORKSHEET_NAME')
