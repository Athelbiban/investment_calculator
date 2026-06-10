import pandas as pd
from app.config import CSV_PORTFOLIO, CSV_TRANSACTIONS
from app.moex_client import MoexClient
from app.portfolio_calculator import calculate_stock_metrics, apply_splits_and_replacements, get_rounding_precision


def build_portfolio() -> None:
    """Рассчитывает портфель по транзакциям из файла transactions.csv и сохраняет его в файл portfolio.csv"""

    # 1. Чтение и подготовка транзакций
    transactions = pd.read_csv(CSV_TRANSACTIONS)
    transactions = transactions.drop_duplicates(['Дата заключения', 'Время заключения', 'Статус', 'Номер сделки'])

    transactions['Дата заключения'] = pd.to_datetime(
        transactions['Дата заключения'] + ' ' + transactions['Время заключения'],
        dayfirst=True
    )
    transactions['Дата расчетов'] = pd.to_datetime(transactions['Дата расчетов'], dayfirst=True)
    transactions = (transactions
                    .drop('Время заключения', axis=1)
                    .dropna(axis=1)
                    .sort_values('Дата заключения')
                    .reset_index(drop=True))

    transactions_executed = transactions[transactions['Статус'] == 'И']
    ticker_list = list(transactions_executed['Код'].unique())

    # 2. Применение сплитов и замен
    ticker_list = apply_splits_and_replacements(ticker_list, transactions, transactions_executed)

    # 3. Получение данных с MOEX
    moex = MoexClient()
    bond_tickers = [t for t in ticker_list if t.startswith('SU') or t.startswith('RU')]

    last_prices = moex.get_last_prices(ticker_list, bond_tickers)
    coupon_data = moex.get_coupon_data(bond_tickers)

    # 4. Вычисление метрик по каждой бумаге
    portfolio_data = {}

    for ticker in ticker_list:
        share_frame = transactions_executed[transactions_executed['Код'] == ticker]

        if share_frame.empty:
            continue

        tx_list = list(zip(
            share_frame['Вид'],
            share_frame['Количество'],
            share_frame['Сумма'],
            share_frame['Комиссия Брокера'],
            share_frame['Комиссия Биржи']
        ))

        metrics = calculate_stock_metrics(tx_list)
        precision = get_rounding_precision(ticker)

        portfolio_data[ticker] = {
            'Котировки': last_prices.get(ticker),
            'НКД': coupon_data.get(ticker, 0),
            'Количество': metrics['amount'],
            'Средняя цена': round(metrics['avg_price'], precision),
            'Комиссия': round(metrics['commission'], 2)
        }

    # 5. Сборка DataFrame
    df = pd.DataFrame.from_dict(portfolio_data, orient='index')
    df.index.name = 'Название'

    df.dropna(subset=['Котировки'], inplace=True)
    df = df[df['Количество'] != 0]
    df['НКД'] = df['НКД'].fillna(0)
    df[['Котировки', 'НКД']] = df[['Котировки', 'НКД']].astype('float64')
    df['Количество'] = df['Количество'].astype('int64')

    df['Текущая цена'] = round((df['Котировки'] + df['НКД']) * df['Количество'], 2)
    df['P/L, руб.'] = round(df['Текущая цена'] - df['Средняя цена'] * df['Количество'], 2)
    df['P/L, %'] = ((df['Котировки'] + df['НКД']) * 100 / df['Средняя цена'] - 100).round(2)

    desired_columns = [
        'Количество',       # 1. Объем
        'Средняя цена',     # 2. Цена входа
        'Котировки',        # 3. Текущая рыночная цена
        'НКД',              # 4. Накопленный купонный доход (облигации)
        'Текущая цена',     # 5. Текущая стоимость актива
        'P/L, руб.',        # 6. Результат в рублях
        'P/L, %',           # 7. Результат в процентах
        'Комиссия'          # 8. Затраты на комиссию
    ]
    df = df[desired_columns]

    # 6. Сохранение DataFrame в файл CSV
    df.to_csv(path_or_buf=CSV_PORTFOLIO)


if __name__ == '__main__':
    build_portfolio()
