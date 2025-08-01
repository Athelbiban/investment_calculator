import csv
import os
import re

from bs4 import BeautifulSoup
from pathlib import Path
from directing import get_directory


def get_portfolio(input_files, output_file, header_flag=True, date=None):

    header = [
        'Наименование', 'ISIN', 'Валюта', 'Количество_нп', 'Номинал_нп',
        'Цена_нп', 'Стоимость_нп', 'НКД_нп', 'Количество_кп',
        'Номинал_кп', 'Цена_кп', 'Стоимость_кп', 'НКД_кп', 'Количество_изп',
        'Стоимость_изп', 'Зачисления', 'Списания', 'Остаток', 'Дата'
    ]

    reg_table_start = re.compile(r'Портфель Ценных Бумаг')
    reg_table_finish = re.compile(r'Итого по Основному рынку, RUB')
    keywords_list = [
        '', 'Основной рынок', 'Наименование',
        'Площадка: Фондовый рынок', '1', 'Блокировано'
    ]

    for file, date in zip(input_files, date):
        write_file(file, output_file, header, reg_table_start,
                   reg_table_finish, keywords_list, header_flag, date)
        header_flag = False


def get_transactions(input_files, output_file, header_flag=True):

    header = [
        'Дата заключения', 'Дата расчетов', 'Время заключения', 'Наименование',
        'Код', 'Валюта', 'Вид', 'Количество', 'Цена', 'Сумма', 'НКД',
        'Комиссия Брокера', 'Комиссия Биржи', 'Номер сделки', 'Комментарий', 'Статус'
    ]

    reg_table_start = re.compile(r'Сделки купли/продажи')
    reg_table_finish = re.compile(r'Итого, RUB')
    keywords_list = ['Дата заключения', 'Площадка: Фондовый рынок', '1']

    for file in input_files:
        write_file(file, output_file, header, reg_table_start,
                   reg_table_finish, keywords_list, header_flag)
        header_flag = False


def get_cashflow(input_files, output_file, header_flag=True):

    header = [
        'Дата', 'Торговая площадка', 'Описание операции',
        'Валюта', 'Сумма зачисления', 'Сумма списания'
    ]

    reg_table_start = re.compile(r'Движение денежных средств за период')
    reg_table_finish = re.compile(r'Итого, RUB')
    keywords_list = ['Дата', '1']

    for file in input_files:
        write_file(file, output_file, header, reg_table_start,
                   reg_table_finish, keywords_list, header_flag)
        header_flag = False


def write_file(file, output_file, header, reg_table_start, reg_table_finish,
               keywords_list, header_flag, date=None):

    # Поиск пробелов в числе, например '1 504.24'
    reg = re.compile(r'^\d+\s+\d+\s*\d*\.?\d*')

    with (open(file, encoding='utf-8') as inf, \
            open(output_file, 'a', encoding='utf-8', newline='') as ouf):

        writer = csv.writer(ouf)
        soup = BeautifulSoup(inf.read(), 'lxml').select('tr, p')
        table_flag = False
        for string in soup:

            if re.search(reg_table_start, string.text):
                table_flag = True
            elif re.search(reg_table_finish, string.text):
                table_flag = False

            if table_flag:
                string = string.find_all('td')

                if header_flag:
                    writer.writerow(header)
                    header_flag = False

                if string and string[0].text not in keywords_list:
                    if date:
                        writer.writerow([re.sub(reg, elem.text.replace(' ', ''), elem.text)
                                         for elem in string] + [date])
                    else:
                        writer.writerow(re.sub(reg, elem.text.replace(' ', ''), elem.text)
                                        for elem in string)


def parse_directory(directory):
    return [f'{directory}{node}' for node in sorted(os.listdir(directory))]


def main():

    directory = get_directory()
    paths = parse_directory(directory)
    out_file_1, out_file_2 = ['files/cashflow.csv', 'files/transactions.csv']

    for f in out_file_1, out_file_2:
        Path(f).unlink(missing_ok=True)

    os.makedirs('files', exist_ok=True)

    date: list[str] = ['']  # format date '2022-01-31'
    for path in paths:

        path_split = path.split('.')[0].split('_')
        if path_split[-1].isdigit():
            date = [f'20{i[-2:]}-{i[2:4]}-{i[:2]}' for i in [path_split[-1]]]
        elif path_split[-2].isdigit():
            date = [f'20{i[-2:]}-{i[2:4]}-{i[:2]}' for i in [path_split[-2]]]
        else:
            raise Exception('Неверное имя файла: ' + path)

    get_cashflow(paths, out_file_1)
    get_transactions(paths, out_file_2)


if __name__ == '__main__':
    main()
