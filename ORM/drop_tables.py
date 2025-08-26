from ORM.database import Base
from ORM.models import engine, Transaction, Cashflow


def drop_tables():
    Base.metadata.drop_all(engine, tables=[Transaction.__table__,
                                           Cashflow.__table__])
    # print('\n[INFO] Все таблицы удалены или не существовали')


if __name__ == '__main__':
    drop_tables()
