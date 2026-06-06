import gspread
import csv
from pathlib import Path
from typing import Any
from google.oauth2.service_account import Credentials
from gspread.utils import ValueInputOption
from app.config import SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, WORKSHEET_NAME, CSV_PORTFOLIO, GSHEETS_SCOPES


def _read_csv(csv_path: str) -> dict[str, tuple[int, float, float]]:
    """Читает CSV и возвращает словарь {ticker: (qty, avg_price, commission)}"""
    data: dict[str, tuple[int, float, float]] = {}
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f'CSV-файл не найден: {csv_path}')

    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            ticker = row.get('Название', '').strip()
            if not ticker:
                continue

            try:
                qty = int(float(row['Количество']))
                avg_price = float(row['Средняя цена'])
                commission = float(row['Комиссия'])
                data[ticker] = (qty, avg_price, commission)
            except (ValueError, KeyError):
                continue
    return data


class GSheetsUpdater:
    """Класс для обновления данных портфеля в Google Sheets"""

    def __init__(self):
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=GSHEETS_SCOPES)
        self.client = gspread.authorize(creds)

    def update(self) -> dict[str, Any]:
        """Обновляет Google таблицу. Возвращает отчет о выполнении"""
        portfolio_data = _read_csv(CSV_PORTFOLIO)
        if not portfolio_data:
            return {'updated': 0, 'not_found': [], 'message': 'CSV-файл пуст или не содержит валидных данных'}

        spreadsheet = self.client.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        all_tickers = worksheet.col_values(2)

        ticker_to_row: dict[str, int] = {}
        for idx, val in enumerate(all_tickers, start=1):
            if isinstance(val, str):
                val = val.strip()
                if val:
                    ticker_to_row[val] = idx

        cell_updates = []
        not_found = []
        updated_count = 0

        for ticker, (qty, avg_price, commission) in portfolio_data.items():
            row = ticker_to_row.get(ticker)
            if row is not None:
                cell_updates.extend([
                    gspread.Cell(row, 5, qty),          # type: ignore[arg-type]
                    gspread.Cell(row, 6, avg_price),    # type: ignore[arg-type]
                    gspread.Cell(row, 7, commission)    # type: ignore[arg-type]
                ])
                updated_count += 1
            else:
                not_found.append(ticker)

        if cell_updates:
            worksheet.update_cells(cell_updates, value_input_option=ValueInputOption.user_entered)

        return {
            'updated': updated_count,
            'not_found': not_found,
            'message': "Успешно"
        }


def update_gsheets() -> dict[str, Any]:
    """Точка входа для CommandManager"""
    updater = GSheetsUpdater()
    return updater.update()


if __name__ == '__main__':
    result = update_gsheets()
    print(f'Обновлено: {result["updated"]} строк')
    if result['not_found']:
        print(f'Не найдены: {", ".join(result["not_found"])}')
