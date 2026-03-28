import gspread
import csv
from passwd.config_gsheets import SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, WORKSHEET_NAME, CSV_FILE
from google.oauth2.service_account import Credentials
from gspread.utils import ValueInputOption


SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def read_csv(csv_path):

    data = {}
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            ticker = row['Название'].strip()
            try:
                quantity = int(float(row['Количество']))
                avg_price = float(row['Средняя цена'])
                commission = float(row['Комиссия'])
                data[ticker] = (quantity, avg_price, commission)
            except (ValueError, KeyError) as e:
                print(f"Ошибка в строке {row}: {e}")

    return data

def main():

    # print("Чтение CSV-файла...")
    portfolio_data = read_csv(CSV_FILE)

    if not portfolio_data:
        print("Не удалось загрузить данные из CSV")
        return

    # print(f"Найдено записей: {len(portfolio_data)}")

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    try:
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

        all_tickers = worksheet.col_values(2)
        ticker_to_row = {}

        for idx, val in enumerate(all_tickers, start=1):
            if val:
                ticker_to_row[val] = idx

        cell_updates = []
        not_found = []

        for ticker, (qty, avg_price, commission) in portfolio_data.items():
            row = ticker_to_row.get(ticker)
            if row:
                cell_updates.append((row, 5, qty))
                cell_updates.append((row, 6, avg_price))
                cell_updates.append((row, 7, commission))
                # print(f"Подготовлено обновление для {ticker}: строка {row}")
            else:
                not_found.append(ticker)

        if cell_updates:
            cell_list = []
            for row, col, val in cell_updates:
                cell = gspread.Cell(row, col, val)
                cell_list.append(cell)

            worksheet.update_cells(cell_list, value_input_option=ValueInputOption.user_entered)
            # print(f"\nОбновлено {len(cell_updates)} ячеек для {len(cell_updates)//3} тикеров")
        else:
            print("Нет данных для обновления.")

        if not_found:
            print("\nТикеры не найдены в таблице:", ", ".join(not_found))

    except gspread.exceptions.WorksheetNotFound:
        print(f"Лист с именем '{WORKSHEET_NAME}' не найден. Проверьте имя листа")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    main()
