import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from ORM.config import get_db_url


def insert_transactions():
    db_url = get_db_url()
    engine = create_engine(db_url)
    csv_file_path = "files/transactions.csv"
    df = pd.read_csv(csv_file_path).drop_duplicates(['Статус', 'Номер сделки'])

    df.rename(columns={
        'Дата заключения': 'conclusion_date',
        'Дата расчетов': 'settlement_date',
        'Время заключения': 'conclusion_time',
        'Наименование': 'product_title',
        'Код': 'product_code',
        'Валюта': 'currency',
        'Вид': 'transaction_type',
        'Количество': 'product_amount',
        'Цена': 'price',
        'Сумма': 'summ',
        'НКД': 'nkd',
        'Комиссия Брокера': 'broker_commission',
        'Комиссия Биржи': 'exchange_commission',
        'Номер сделки': 'transaction_number',
        'Комментарий': 'comment',
        'Статус': 'status'
    }, inplace=True)

    try:
        df.to_sql('transactions', engine, if_exists='append', index=False)
        print("[INFO] Данные успешно загружены в таблицу transactions!")
    except IntegrityError as e:
        print(f"[INFO] Произошла ошибка целостности данных: {e}")
    except Exception as ex:
        print(f"[INFO] Произошла ошибка: {ex}")


if __name__ == '__main__':
    insert_transactions()
