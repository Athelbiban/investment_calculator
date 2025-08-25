from ORM.models import create_all_tables
from ORM.insert_transactions import insert_transactions
from ORM.insert_cashflows import insert_cashflow
from ORM.drop_tables import drop_tables


def recreate_database():
    drop_tables()
    create_all_tables()
    insert_transactions()
    insert_cashflow()


if __name__ == '__main__':
    recreate_database()
