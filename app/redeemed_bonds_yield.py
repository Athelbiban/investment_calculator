import psycopg2
import re

from decimal import Decimal
from app.connect_DB import connect_attr


def get_redeemed_bonds():

    with psycopg2.connect(connect_attr()) as conn:
        with conn.cursor() as cursor:

            income_list =[]

            cursor.execute(
                '''
                select trading_date, description_operation, transfer_amount
                from cashflows
                where description_operation ~* '^зачисление д/с'
                    and description_operation ~* 'погашение'
                '''
            )

            redeemed_bonds_tuples_list = cursor.fetchall()
            rb_list = []
            reg = re.compile(r"Зачисление д/с \(погашение ")

            for i in redeemed_bonds_tuples_list:
                bond = re.sub(reg, '', i[1][:-1])
                rb_list.append([bond, i[0], i[2]])

            for i, bond_list in enumerate(rb_list):
                bond_name = bond_list[0]

                cursor.execute(
                    f'''
                    select sum(summ)
                    from transactions
                    where product_title = '{bond_name}'
                        and status = 'И'
                        and transaction_type ~* 'покупка'
                    '''
                )

                purchase_price = cursor.fetchone()[0]
                rb_list[i].append(purchase_price)

                cursor.execute(
                    f'''
                    select sum(transfer_amount)
                    from cashflows
                    where description_operation ~* '^зачисление д/с' 
                        and description_operation ~* 'купон'
                        and description_operation ~* '{bond_name}';
                    '''
                )

                coupons = cursor.fetchone()[0]
                # print(coupons)
                rb_list[i].append(coupons)

                cursor.execute(
                    f'''
                    select conclusion_date, 
                        sum(broker_commission),
                        sum(exchange_commission)
                    from transactions t 
                    where transaction_type ~* 'покупка' 
                        and product_code ~* '^ru' 
                        and status = 'И'
                        and t.product_title = '{bond_name}'
                    group by conclusion_date; 
                    '''
                )

                conclusion_date, broker_comm, exchange_comm = cursor.fetchone()
                # !здесь берем только первую дату, если были докупки, то надо по-другому
                rb_list[i].append(conclusion_date)
                rb_list[i].append(broker_comm)
                rb_list[i].append(exchange_comm)
                rb_list[i].append(
                    (rb_list[i][2] - rb_list[i][3]) *
                    Decimal('0.13')
                )

                if rb_list[i][4]:
                    net_profit_rub = rb_list[i][2] + rb_list[i][4] - rb_list[i][3] \
                                     - rb_list[i][6] - rb_list[i][7] - rb_list[i][8]
                else:
                    net_profit_rub = rb_list[i][2] - rb_list[i][3] \
                                     - rb_list[i][6] - rb_list[i][7] - rb_list[i][8]

                days_delta = (rb_list[i][1] - rb_list[i][5]).days
                net_profit_percent = net_profit_rub * 100 / \
                                     rb_list[i][3] / days_delta * 365
                income_list.append([rb_list[i][0], round(net_profit_percent, 2),
                                    rb_list[i][1], days_delta, rb_list[i][3],
                                    round(net_profit_rub, 2)])

        for i in income_list:
            print('Название: ' + i[0] + ';' + ' % годовых: ' + str(i[1]) + ';' +
                  ' Дата погашения: ' + str(i[2]) + ';' + ' Дни: ' + str(i[3]) +
                  ';' + ' Вложено: ' + str(i[4]) + ' Получено: ' + str(i[5])
                  )


if __name__ == '__main__':
    get_redeemed_bonds()
