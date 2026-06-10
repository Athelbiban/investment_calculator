from typing import TypedDict
from pandas import DataFrame


class StockData(TypedDict):
    amount: int
    avg_price: float
    commission: float


ROUND_CONFIG = {
    3: ('LKOH', 'MGNT'),
    4: ('MOEX', 'YDEX'),
    5: ('HYDR', 'AFKS', 'IRAO', 'SBMM'),
    6: ('GAZP', 'MTSS', 'NVTK', 'ROSN', 'SBER', 'CHMF',
        'SNGS', 'SBGD', 'SBMX', 'AFKS', 'AFLT', 'RTKM')
}

SPLIT_CONFIG = {
    'FXGD': ('2022-02-17', 10),
    'SBMX': ('2021-06-09', 100),
    'FXUS': ('2022-01-24', 100),
    'FXRL': ('2021-11-24', 100),
    'FXRU': ('2022-02-17', 10),
    'FXDE': ('2021-12-15', 100),
    'T': ('2026-04-16', 10)
}

TICKER_REPLACEMENT = {
    'VTBE': 'RSHE',
    'RU000A102HB1': 'SU26227RMFS7',
    'RU000A1038V6': 'SU26238RMFS4',
    'RU000A101QE0': 'SU26234RMFS3'
}


def get_rounding_precision(ticker: str) -> int:
    """Возвращает точность округления для тикера"""

    for precision, tickers in ROUND_CONFIG.items():
        if ticker in tickers:
            return precision
    return 2

def calculate_stock_metrics(transactions: list[tuple[str, int, float,float, float]]) -> StockData:
    """
    Вычисляет количество, среднюю цену и комиссию по транзакциям

    :param transactions: список кортежей (тип, количество, сумма, комиссия_брокера, комиссия_биржи)
    :return: StockData с рассчитанными метриками
    """

    amount = 0
    total_cost = 0.0
    total_commission = 0.0
    avg_price = 0.0

    for tx_type, qty, total, broker_comm, exchange_comm in transactions:
        commission = broker_comm + exchange_comm

        if tx_type == 'Покупка':
            amount += qty
            total_cost += total
            total_commission += commission
            avg_price = (total_cost + total_commission) / amount
        elif tx_type == 'Продажа':
            amount -= qty

            if amount > 0:
                total_cost = amount * (avg_price + commission / amount)
                total_commission += commission
                avg_price = (total_cost + total_commission) / amount
            else:
                total_commission = 0
                total_cost = 0

        else:
            raise ValueError(f"Неверный вид транзакции: {tx_type}")

    return StockData(
        amount=amount,
        avg_price=avg_price,
        commission=total_commission
    )

def apply_splits_and_replacements(
        tickers: list[str],
        transactions_df: DataFrame,
        transaction_executed_df: DataFrame
) -> list[str]:
    """
    Применяет сплиты и замены тикеров, возвращает обновленный экземпляр списка тикеров

    :param tickers: список строк тикеров
    :param transactions_df: DataFrame Pandas со всеми транзакциями
    :param transaction_executed_df: DataFrame Pandas с исполненными транзакциями (статус 'И')
    :return: возвращает список с замененными тикерами и учтенными сплитами
    """

    updated_tickers = tickers.copy()

    for old_ticker, new_ticker in TICKER_REPLACEMENT.items():
        if old_ticker in updated_tickers:
            updated_tickers.remove(old_ticker)
            updated_tickers.append(new_ticker)
            transaction_executed_df.loc[transactions_df['Код'] == old_ticker, 'Код'] = new_ticker

    for ticker in updated_tickers:
        if ticker in SPLIT_CONFIG:
            split_date, split_ratio = SPLIT_CONFIG[ticker]
            mask = (
                    (transaction_executed_df['Код'] == ticker) &
                    (transaction_executed_df['Дата заключения'] < split_date)
            )
            transaction_executed_df.loc[mask, 'Количество'] *= split_ratio

    return updated_tickers
