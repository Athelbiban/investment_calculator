import psycopg2
from passwd.config_DB import connect_attr
from passwd.config_URL_DB import url_cashflow


def create_cashflow_table():

    with psycopg2.connect(connect_attr()) as conn:
        with conn.cursor() as cursor:

            conn.autocommit = True
            cursor.execute(f'''
                CREATE table if not exists cashflow
                (
                    id SERIAL,
                    date DATE,
                    trading_platform VARCHAR(30),
                    description_operation TEXT,
                    currency VARCHAR(10),
                    transfer_amount DECIMAL(16, 4),
                    debit_amount DECIMAL(16, 4),
                    primary key (id)
                );

                copy cashflow
                (
                    date,
                    trading_platform,
                    description_operation,
                    currency,
                    transfer_amount,
                    debit_amount
                )
                FROM '{url_cashflow}'
                DELIMITER ','
                CSV header;

                -- удаляем дубли если их меньше 4, иначе оставляем 2 экз.
                with duplicates as (
                    select id, row_number() over (
                        partition by date, 
                        trading_platform,
                        description_operation,
                        currency,
                        transfer_amount,
                        debit_amount
                        order by id) as rnum 
                    from cashflow
                    )
                delete from cashflow 
                where id in (
                    select id from duplicates where rnum > 1 and rnum < 4
                    );
                '''
                           )

    print("[INFO] Таблица cashflow создана или существовала")


if __name__ == '__main__':
    create_cashflow_table()
