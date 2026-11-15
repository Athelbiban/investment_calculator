from ORM.models import create_all_tables
from ORM.insert_transactions import insert_transactions
from ORM.insert_cashflows import insert_cashflow
from ORM.drop_tables import drop_tables
from app.logger import AppLogger

logger = AppLogger('create_DB')


def recreate_database():
    drop_tables()
    create_all_tables()
    insert_transactions()
    insert_cashflow()


def sync_database():
    """Инкрементальная синхронизация: создаёт таблицы при необходимости и дозаписывает только новые строки"""

    create_all_tables()
    new_transactions = insert_transactions()
    new_cashflows = insert_cashflow()
    logger.info(f'База данных синхронизирована: транзакций +{new_transactions}, движений средств +{new_cashflows}')


if __name__ == '__main__':
    sync_database()
