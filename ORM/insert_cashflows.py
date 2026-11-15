import pandas as pd
from decimal import Decimal
from typing import cast
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from ORM.drop_duplicates_cashflow import drop_duplicates_cashflow
from ORM.connect_DB import get_db_url
from ORM.models import Cashflow
from app.config import CSV_CASHFLOW
from app.logger import AppLogger

logger = AppLogger('insert_cashflows')

_COLUMNS = [
    'trading_date', 'trading_platform', 'description_operation',
    'currency', 'transfer_amount', 'debit_amount'
]

COLUMN_RENAME = {
    'Дата': 'trading_date',
    'Торговая площадка': 'trading_platform',
    'Описание операции': 'description_operation',
    'Валюта': 'currency',
    'Сумма зачисления': 'transfer_amount',
    'Сумма списания': 'debit_amount',
}


def _norm(value: object) -> object:
    """Приводит значение к сопоставимому виду: None вместо NaN, Decimal.normalize для чисел"""

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, float):
        return Decimal(str(value)).normalize()
    return value


def _load_rows() -> list[dict]:
    df = pd.read_csv(CSV_CASHFLOW)
    df = drop_duplicates_cashflow(df)
    df = df.rename(columns=COLUMN_RENAME)
    df = df[_COLUMNS]
    trading_dates = cast(pd.Series, pd.to_datetime(df['trading_date'], dayfirst=True))
    df['trading_date'] = trading_dates.dt.date
    df = df.where(pd.notna(df), None)
    return df.to_dict('records')


def _existing_keys(engine) -> set[tuple]:
    """Ключи строк, уже лежащих в cashflows, по всем колонкам таблицы"""

    with engine.connect() as conn:
        rows = conn.execute(text(f"SELECT {', '.join(_COLUMNS)} FROM cashflows")).all()
    return {tuple(_norm(v) for v in row) for row in rows}


def insert_cashflow() -> int:
    """
    Дозаписывает в БД только те строки cashflow.csv, которых ещё нет в таблице.
    Возвращает количество добавленных строк.

    :raise: Любая ошибка пробрасывается наверх после записи в лог
    """

    try:
        rows = _load_rows()
        engine = create_engine(get_db_url())
        fresh = [r for r in rows
                 if tuple(_norm(r[c]) for c in _COLUMNS) not in _existing_keys(engine)]
        with engine.begin() as conn:
            for start in range(0, len(fresh), 500):
                conn.execute(pg_insert(Cashflow).values(fresh[start:start + 500]))
    except Exception as e:
        logger.critical(f'Не удалось загрузить движения средств из {CSV_CASHFLOW}: {e}', exc_info=True)
        raise

    logger.info(f'Движение средств: обработано строк {len(rows)}, добавлено новых {len(fresh)}')
    return len(fresh)


if __name__ == '__main__':
    insert_cashflow()
