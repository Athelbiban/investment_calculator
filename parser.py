import csv
import os
import re

from bs4 import BeautifulSoup
from pathlib import Path
from directing import get_directory


def get_portfolio(input_files, output_file, date=None):

    header = [
        'Наименование', 'ISIN', 'Валюта', 'Количество_нп', 'Номинал_нп',
        'Цена_нп', 'Стоимость_нп', 'НКД_нп', 'Количество_кп',
        'Номинал_кп', 'Цена_кп', 'Стоимость_кп', 'НКД_кп', 'Количество_изп',
        'Стоимость_изп', 'Зачисления', 'Списания', 'Остаток', 'Дата'
    ]

    key_words = ['', 'Основной рынок', 'Наименование', 'Площадка: Фондовый рынок', '1', 'Блокировано']
    reg = re.compile('Портфель Ценных Бумаг')

    flag1 = True
    for file, date in zip(input_files, date):
        write_file(file, output_file, header, key_words, reg, flag1, date)
        flag1 = False


def get_transactions(input_files, output_file):

    header = [
        'Дата заключения', 'Дата расчетов', 'Время заключения', 'Наименование',
        'Код', 'Валюта', 'Вид', 'Количество', 'Цена', 'Сумма', 'НКД',
        'Комиссия Брокера', 'Комиссия Биржи', 'Номер сделки', 'Комментарий', 'Статус'
    ]

    key_words = ['Дата заключения', 'Площадка: Фондовый рынок', '1']

    reg = re.compile('Сделки купли/продажи')
    flag1 = True
    for file in input_files:
        write_file(file, output_file, header, key_words, reg, flag1)
        flag1 = False


def write_file(file, output_file, header, key_words, reg_start, flag1,
               date=None):

    # Поиск пробелов в числе, например 1 504.24
    reg1 = re.compile(r'^\d+\s+\d+\s*\d*\.?\d*')
    reg_finish_1 = re.compile(r'Итого по Основному рынку, RUB')
    reg_finish_2 = re.compile(r'Итого, RUB')

    with (open(file, encoding='utf-8') as inf, \
            open(output_file, 'a', encoding='utf-8', newline='') as ouf):

        writer = csv.writer(ouf)
        soup = BeautifulSoup(inf.read(), 'lxml').select('tr, p')
        flag2 = False
        for string in soup:

            if re.search(reg_start, string.text):
                flag2 = True
            elif re.search(reg_finish_1, string.text) \
                or re.search(reg_finish_2, string.text):
                flag2 = False

            if flag2:
                string = string.find_all('td')

                if flag1:
                    writer.writerow(header)
                    flag1 = False

                if string and string[0].text not in key_words:
                    if date:
                        writer.writerow([re.sub(
                            reg1,
                            elem.text.replace(' ', ''),
                            elem.text) for elem in string] + [date])
                    else:
                        writer.writerow(re.sub(
                            reg1,
                            elem.text.replace(' ', ''),
                            elem.text) for elem in string)


def parse_directory(directory): return [f'{directory}{node}' for node in sorted(os.listdir(directory))]


def main():

    directory = get_directory()
    paths = parse_directory(directory)
    out_file_1, out_file_2 = ['files/portfolio.csv', 'files/transactions.csv']

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

    get_portfolio(paths, out_file_1, date)
    get_transactions(paths, out_file_2)


if __name__ == '__main__':
    main()
