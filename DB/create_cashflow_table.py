import psycopg2
from passwd.config_DB import dbname, user, password, url_cashflow


def create_cashflow_table():

    conn = psycopg2.connect(
        database=dbname,
        user=user,
        password=password
    )
    conn.autocommit = True

    try:
        with conn.cursor() as cursor:

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
                    primary key (date, description_operation, trading_platform)
                );

                create temp table if not exists temp_cashflow as
                SELECT
                    date,
                    trading_platform,
                    description_operation,
                    currency,
                    transfer_amount,
                    debit_amount
                FROM cashflow;

                COPY temp_cashflow
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

                insert into cashflow
                (
                    date,
                    trading_platform,
                    description_operation,
                    currency,
                    transfer_amount,
                    debit_amount
                )
                select * from temp_cashflow
                on conflict do nothing;
                '''
                           )

            print("[INFO] Таблица cashflow создана или существовала")

    except Exception as _ex:
        print("[INFO] Ошибка в работе PostgreSQL", _ex)

    finally:
        if conn:
            conn.close()
            print("[INFO] PostgreSQL соединение закрыто")

if __name__ == '__main__':
    create_cashflow_table()
