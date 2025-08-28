import csv
import os
import re

from bs4 import BeautifulSoup, element
from pathlib import Path
from app.directing import get_directory


def get_transactions(input_files: list[str], output_file: str,
                     header_flag=True):

    header = [
        'Дата заключения', 'Дата расчетов', 'Время заключения', 'Наименование',
        'Код', 'Валюта', 'Вид', 'Количество', 'Цена', 'Сумма', 'НКД',
        'Комиссия Брокера', 'Комиссия Биржи', 'Номер сделки',
        'Комментарий', 'Статус'
    ]

    reg_table_start = re.compile(r'Сделки купли/продажи')
    reg_table_finish = re.compile(r'Итого, RUB')
    stopwords_list = ['Дата заключения', 'Площадка: Фондовый рынок', '1']

    my_writer(input_files, output_file, header, reg_table_start,
              reg_table_finish, stopwords_list, header_flag)


def get_cashflow(input_files: list[str], output_file: str, header_flag=True):

    header = [
        'Дата', 'Торговая площадка', 'Описание операции',
        'Валюта', 'Сумма зачисления', 'Сумма списания'
    ]

    reg_table_start = re.compile(r'Движение денежных средств за период')
    reg_table_finish = re.compile(r'Итого, RUB')
    stopwords_list = ['Дата', '1']

    my_writer(input_files, output_file, header, reg_table_start,
              reg_table_finish, stopwords_list, header_flag)


def get_securities_movement(input_files: list[str], output_file: str,
                            header_flag=True):

    header = [
        'Дата операции', 'Наименование ЦБ', 'Код ЦБ', 'Вид',
        'Основание операции', 'Количество, шт', 'Дата приобретения', 'Цена',
        'Комиссия Брокера, руб', 'Комиссия Биржи, руб', 'Другие затраты'
    ]

    reg_table_start = re.compile(
        r'Движение ЦБ, не связанное с исполнением сделок'
    )
    reg_table_finish = re.compile(r'Итого по площадке Фондовый рынок')
    stopwords_list = ['', 'Дата операции', '1', 'Площадка: Фондовый рынок']

    my_writer(input_files, output_file, header, reg_table_start,
              reg_table_finish, stopwords_list, header_flag)


def write_file(file: str, output_file: str, header: list[str],
               reg_table_start: re.Pattern, reg_table_finish: re.Pattern,
               reg_numbers: re.Pattern, stopwords_list: list[str],
               header_flag: bool):

    with (open(file, encoding='utf-8') as inf,
          open(output_file, 'a', encoding='utf-8', newline='') as ouf):

        writer = csv.writer(ouf)
        soup: element.ResultSet = BeautifulSoup(
            inf.read(), 'lxml').select('tr, p')
        table_flag = False

        for element_Tag in soup:

            if header_flag:
                writer.writerow(header)
                header_flag = False

            if re.search(reg_table_start, element_Tag.text):
                table_flag = True
            elif re.search(reg_table_finish, element_Tag.text):
                table_flag = False

            if table_flag:
                _resultSet: element.ResultSet = element_Tag.find_all('td')

                if _resultSet and _resultSet[0].text not in stopwords_list:
                    writer.writerow(re.sub(
                        reg_numbers,
                        elem.text.replace(' ', ''),
                        elem.text
                    ) for elem in _resultSet)


def my_writer(input_files, output_file, header, reg_table_start,
              reg_table_finish, stopwords_list, header_flag):

    # Поиск пробелов в числе, например '1 504.24'
    reg_numbers = re.compile(r'^\d+\s+\d+\s*\d*\.?\d*')

    for file in input_files:
        write_file(file, output_file, header, reg_table_start,
                   reg_table_finish, reg_numbers, stopwords_list, header_flag)
        if header_flag:
            header_flag = False


def parse_directory(directory: str):
    return [f'{directory}{node}' for node in sorted(os.listdir(directory))]


def launch_parser():

    directory: str = get_directory()
    paths: list[str] = parse_directory(directory)
    out_file_1 = 'files/transactions.csv'
    out_file_2 = 'files/cashflow.csv'
    out_file_3 = 'files/securities_move.csv'

    for f in out_file_1, out_file_2, out_file_3:
        Path(f).unlink(missing_ok=True)

    os.makedirs('files', exist_ok=True)

    get_transactions(paths, out_file_1)
    get_cashflow(paths, out_file_2)
    get_securities_movement(paths, out_file_3)


if __name__ == '__main__':
    launch_parser()
