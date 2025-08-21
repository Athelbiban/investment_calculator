import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from app.drop_dudplicates_cashflow import drop_duplicates_cashflow
from app.config import get_db_url


def insert_cashflow():
    db_url = get_db_url()
    engine = create_engine(db_url)
    csv_file_path = "files/cashflow.csv"
    df = pd.read_csv(csv_file_path)
    df = drop_duplicates_cashflow(df)

    df.rename(columns={
        'Дата': 'trading_date',
        'Торговая площадка': 'trading_platform',
        'Описание операции': 'description_operation',
        'Валюта': 'currency',
        'Вид': 'transaction_type',
        'Сумма зачисления': 'transfer_amount',
        'Сумма списания': 'debit_amount',
    }, inplace=True)

    try:
        df.to_sql('cashflows', engine, if_exists='append', index=False)
        print("[INFO] Данные успешно загружены в таблицу cashflows!")
    except IntegrityError as e:
        print(f"[INFO] Произошла ошибка целостности данных: {e}")
    except Exception as ex:
        print(f"[INFO] Произошла ошибка: {ex}")


if __name__ == '__main__':
    insert_cashflow()