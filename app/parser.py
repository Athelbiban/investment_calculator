import csv
import re
from pathlib import Path
from typing import Any
from bs4 import BeautifulSoup
from app.directing import get_directory
from dataclasses import dataclass


_REG_NUMBERS = re.compile(r"(\d+)*\s*(\d+)\s+(\d+(?:\.\d+)?)")

# Маппинг ISIN в Наименовании на "Наименование" и "Код" для случаев, когда брокер в отчетах не возвращает код бумаги
# как с Т-технологиями с 06.2026г.
_KNOWN_SECURITIES_BY_ISIN: dict[str, tuple[str, str]] = {
    'RU000A107UL4': ('Т-технологии', 'T')
}

# Индексы колонок для transaction
_TRANSACTION_NAME_INDEX = 3
_TRANSACTION_CODE_INDEX = 4


def _clean_text(text: str) -> str:
    """Убирает пробелы внутри чисел, например, '12 345 678.91' -> '12345678.91'"""
    return _REG_NUMBERS.sub(r"\1\2\3", text.strip())

def _validate_transaction_row(row: list[str], row_index: int) -> list[str]:
    """
    Валидирует строку транзакции и подставляет известные значения для пустых кодов

    :param row: строка транзакции (список ячеек)
    :param row_index: номер строки для сообщения об ошибке
    :return: валидированная строка (мутирует входной список)
    :raise: ValueError: если Код пустой и Наименование не найдено в маппинге
    """

    code = row[_TRANSACTION_CODE_INDEX].strip()
    name = row[_TRANSACTION_NAME_INDEX].strip()

    if not code:
        if name in _KNOWN_SECURITIES_BY_ISIN:
            new_name, new_code = _KNOWN_SECURITIES_BY_ISIN[name]
            row[_TRANSACTION_NAME_INDEX] = new_name
            row[_TRANSACTION_CODE_INDEX] = new_code
        else:
            raise ValueError(
                f"Обнаружена транзакция с пустым кодом (строка {row_index})\n"
                f"Наименование: '{name}'\n"
                f"Добавьте маппинг в _KNOWN_SECURITIES_BY_ISIN или проверьте отчет брокера\n"
            )

    return row

def _extract_table_data(
        html_content: str,
        start_re: re.Pattern,
        finish_re: re.Pattern,
        stopwords: set[str]
) -> list[list[str]]:
    """Извлекает строки таблицы из HTML-контента"""
    soup = BeautifulSoup(html_content, 'lxml')
    rows = []
    in_table = False

    for tag in soup.select("tr, p"):
        tag_text = tag.get_text(strip=True)

        if start_re.search(tag_text):
            in_table = True
            continue
        if finish_re.search(tag_text):
            in_table = False
            continue

        if in_table:
            cells = tag.find_all("td")
            if not cells:
                continue

            if cells[0].get_text(strip=True) in stopwords:
                continue

            rows.append([_clean_text(cell.get_text()) for cell in cells])

    return rows

def _write_csv(output_path: Path, headers: list[str], data_rows: list[list[str]]) -> int:
    """Записывает данные в CSV и возвращает количество строк"""
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data_rows)
    return len(data_rows)


@dataclass(frozen=True)
class ParserConfig:
    """Конфигурация для парсинга одного типа отчёта"""
    file: Path
    headers: list[str]
    start: re.Pattern
    finish: re.Pattern
    stopwords: set[str]


def parse_reports(directory: Path | None = None) -> dict[str, Any]:
    """Парсит HTML-отчеты брокера, сохраняет в CSV и возвращает статистику"""
    target_dir = directory or get_directory('reports')
    html_files = sorted(target_dir.glob("*.html"))

    if not html_files:
        return {'transactions': 0, 'cashflow': 0, 'securities': 0, 'message': 'HTML-файлы не найдены'}

    output_dir = get_directory('csv')

    configs: dict[str, ParserConfig] = {
        'transactions': ParserConfig(
            file=output_dir / 'transactions.csv',
            headers=['Дата заключения', 'Дата расчетов', 'Время заключения', 'Наименование',
                     'Код', 'Валюта', 'Вид', 'Количество', 'Цена', 'Сумма', 'НКД',
                     'Комиссия Брокера', 'Комиссия Биржи', 'Номер сделки', 'Комментарий', 'Статус'],
            start=re.compile(r'Сделки купли/продажи'),
            finish=re.compile(r'Итого, RUB'),
            stopwords={'Дата заключения', 'Площадка: Фондовый рынок', '1'}
        ),
        'cashflow': ParserConfig(
            file=output_dir / 'cashflow.csv',
            headers=['Дата', 'Торговая площадка', 'Описание операции',
                     'Валюта', 'Сумма зачисления', 'Сумма списания'],
            start=re.compile(r'Движение денежных средств за период'),
            finish=re.compile(r'Итого, RUB'),
            stopwords={'Дата', '1'}
        ),
        'securities': ParserConfig(
            file=output_dir / 'securities_move.csv',
            headers=['Дата операции', 'Наименование ЦБ', 'Код ЦБ', 'Вид',
                     'Основание операции', 'Количество, шт', 'Дата приобретения', 'Цена',
                     'Комиссия Брокера, руб', 'Комиссия Биржи, руб', 'Другие затраты'],
            start=re.compile(r'Движение ЦБ, не связанное с исполнением сделок'),
            finish=re.compile(r'Итого по площадке Фондовый рынок'),
            stopwords= {'', 'Дата операции', '1', 'Площадка: Фондовый рынок'}
        )
    }

    result: dict[str, Any] = {}
    for name, cfg in configs.items():
        all_rows: list[list[str]] = []
        for html_file in html_files:
            content = html_file.read_text(encoding='utf-8')
            rows = _extract_table_data(content, cfg.start, cfg.finish, set(cfg.stopwords))

            if name == 'transactions':
                for i, row in enumerate(rows, start=1):
                    _validate_transaction_row(row, i)

            all_rows.extend(rows)

        result[name] = _write_csv(cfg.file, cfg.headers, all_rows)

    result['message'] = 'Успешно'
    return result

def launch_parser() -> dict[str, Any]:
    """Точка входа для CommandManager"""
    return parse_reports()


if __name__ == '__main__':
    report = launch_parser()
    print(f"Готово. Отчет: {report}")
