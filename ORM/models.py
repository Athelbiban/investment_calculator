from sqlalchemy import (
    create_engine,
    String,
    Text,
    Integer,
    DECIMAL,
    BigInteger,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from datetime import date, time

from ORM.database import Base
from ORM.connect_DB import get_db_url


db_url = get_db_url()
engine = create_engine(db_url)


class Transaction(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    conclusion_date: Mapped[date] = mapped_column(nullable=False)
    settlement_date: Mapped[date] = mapped_column(nullable=False)
    conclusion_time: Mapped[time] = mapped_column(nullable=False)
    product_title: Mapped[str] = mapped_column(String(50))
    product_code: Mapped[str] = mapped_column(String(20))
    currency: Mapped[str] = mapped_column(String(10))
    transaction_type: Mapped[str] = mapped_column(String(10))
    product_amount: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(DECIMAL(16, 2))
    summ: Mapped[Decimal] = mapped_column(DECIMAL(16, 2))
    nkd: Mapped[Decimal] = mapped_column(DECIMAL(16, 2))
    broker_commission: Mapped[Decimal] = mapped_column(DECIMAL(16,
                                                               2))
    exchange_commission: Mapped[Decimal] = mapped_column(DECIMAL(16,
                                                                 2))
    transaction_number: Mapped[int] = mapped_column(BigInteger())
    comment: Mapped[str] = mapped_column(String(250), nullable=True)
    status: Mapped[str] = mapped_column(String(10))

    __table_args__ = (
        UniqueConstraint('transaction_number', 'status'),
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__tablename__}(\n"
            f"\tid={self.id},\n"
            f"\tproduct_title='{self.product_title}',\n"
            f"\tcurrency='{self.currency}',\n"
            f"\ttransaction_type='{self.transaction_type}',\n"
            f"\tproduct_amount={self.product_amount},\n"
            f"\tprice={self.price},\n"
            f"\tsumm={self.summ},\n"
            f"\tnkd={self.nkd},\n"
            f"\tbroker_commission={self.broker_commission},\n"
            f"\texchange_commission={self.exchange_commission},\n"
            f"\ttransaction_number={self.transaction_number},\n"
            f"\tcomment='{self.comment}',\n"
            f"\tstatus='{self.status}',\n"
            f"\tconclusion_date={self.conclusion_date},\n"
            f"\tsettlement_date={self.settlement_date},\n"
            f"\tconclusion_time={self.conclusion_time}\n"
            f")>"
        )


class Cashflow(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    trading_date: Mapped[date] = mapped_column(nullable=False)
    trading_platform: Mapped[str] = mapped_column(String(30), nullable=True)
    description_operation: Mapped[str] = mapped_column(Text, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=True)
    transfer_amount: Mapped[Decimal] = mapped_column(DECIMAL(16, 4),
                                                     nullable=True)
    debit_amount: Mapped[Decimal] = mapped_column(DECIMAL(16, 4),
                                                  nullable=True)

    def __repr__(self) -> str:
        return (
            f"<{self.__tablename__}(\n"
            f"\tid={self.id},\n"
            f"\ttrading_date={self.trading_date},\n"
            f"\ttrading_platform='{self.trading_platform}',\n"
            f"\tdescription_operation='{self.description_operation}',\n"
            f"\tcurrency='{self.currency}',\n"
            f"\ttransfer_amount={self.transfer_amount},\n"
            f"\tdebit_amount={self.debit_amount}\n"
            f")>"
        )


def create_all_tables():
    Base.metadata.create_all(engine)
    # print("[INFO] Таблицы успешно созданы или существовали")


if __name__ == '__main__':
    create_all_tables()