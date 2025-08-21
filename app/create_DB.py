from app.models import create_all_tables
from app.insert_transactions import insert_transactions
from app.insert_cashflows import insert_cashflow
from app.drop_tables import drop_tables


def recreate_database():
    drop_tables()
    create_all_tables()
    insert_transactions()
    insert_cashflow()


if __name__ == '__main__':
    recreate_database()
