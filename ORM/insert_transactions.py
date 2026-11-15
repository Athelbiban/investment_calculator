import pandas as pd
from typing import cast
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert as pg_insert
from ORM.connect_DB import get_db_url
from ORM.models import Transaction
from app.config import CSV_TRANSACTIONS
from app.logger import AppLogger

logger = AppLogger('insert_transactions')

_COLUMNS = [
    'conclusion_date', 'settlement_date', 'conclusion_time', 'product_title',
    'product_code', 'currency', 'transaction_type', 'product_amount', 'price',
    'summ', 'nkd', 'broker_commission', 'exchange_commission',
    'transaction_number', 'comment', 'status'
]

COLUMN_RENAME = {
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
}


def _prepare_rows() -> list[dict]:
    """Читает transactions.csv и приводит строки к типам модели Transaction"""

    df = pd.read_csv(CSV_TRANSACTIONS).drop_duplicates(['Статус', 'Номер сделки'])
    df = df.rename(columns=COLUMN_RENAME)
    conclusion_dates = cast(pd.Series, pd.to_datetime(df['conclusion_date'], dayfirst=True))
    settlement_dates = cast(pd.Series, pd.to_datetime(df['settlement_date'], dayfirst=True))
    df['conclusion_date'] = conclusion_dates.dt.date
    df['settlement_date'] = settlement_dates.dt.date
    conclusion_times = cast(pd.Series, pd.to_datetime(df['conclusion_time'], format='%H:%M:%S'))
    df['conclusion_time'] = conclusion_times.dt.time
    df['product_amount'] = df['product_amount'].astype('int64')
    df['transaction_number'] = df['transaction_number'].astype('int64')
    df = df.where(pd.notna(df), None)
    return df[_COLUMNS].to_dict('records')


def insert_transactions() -> int:
    """
    Дозаписывает транзакции в БД, пропуская уже существующие пары
    (номер сделки, статус). Возвращает количество добавленных строк.

    :raise: Любая ошибка пробрасывается наверх после записи в лог
    """

    try:
        rows = _prepare_rows()
        engine = create_engine(get_db_url())
        inserted = 0
        with engine.begin() as conn:
            for start in range(0, len(rows), 500):
                stmt = pg_insert(Transaction).values(rows[start:start + 500])
                stmt = stmt.on_conflict_do_nothing(index_elements=['transaction_number', 'status'])
                inserted += conn.execute(stmt).rowcount
    except Exception as e:
        logger.critical(f'Не удалось загрузить транзакции из {CSV_TRANSACTIONS}: {e}', exc_info=True)
        raise

    logger.info(f'Транзакции: обработано строк {len(rows)}, добавлено новых {inserted}')
    return inserted


if __name__ == '__main__':
    insert_transactions()
