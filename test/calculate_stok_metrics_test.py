def calculate_stock_metrics_test(transactions: list[tuple[str, int, float,float, float]]):
    """
    Вычисляет количество, среднюю цену и комиссию по транзакциям

    :param transactions: список кортежей (тип, количество, сумма, комиссия_брокера, комиссия_биржи)
    :return: StockData с рассчитанными метриками
    """

    amount = 0
    total_cost = 0.0
    total_commission = 0.0
    avg_price_with_commission = 0.0
    avg_price_without_commission = 0.0

    for tx_type, qty, total, broker_comm, exchange_comm in transactions:
        commission = broker_comm + exchange_comm

        if tx_type == 'Покупка':
            amount += qty
            total_cost += total
            total_commission += commission
            avg_price_without_commission = total_cost / amount
            avg_price_with_commission = (total_cost + total_commission) / amount
        elif tx_type == 'Продажа':
            amount -= qty

            if amount > 0:
                total_cost = amount * avg_price_without_commission
                total_commission += commission
                avg_price_with_commission = (total_cost + total_commission) / amount
            elif amount == 0:
                total_commission = 0
                total_cost = 0
            else:
                raise ValueError(f"Количество ценных бумаг не может быть <0: {amount}")

        else:
            raise ValueError(f"Неверный вид транзакции: {tx_type}")

    return {
        "amount":amount,
        "avg_price":avg_price_with_commission,
        "commission":total_commission
    }


if __name__ == '__main__':
    lst_1 = [('Покупка', 10, 1000, 5, 5), ('Продажа', 5, 500, 2, 3)]
    res = calculate_stock_metrics_test(lst_1)
    print(res)
