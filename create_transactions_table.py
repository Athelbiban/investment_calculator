import psycopg2
from passwd.config_DB import dbname, user, password, url


def create_transactions_table():

    conn = psycopg2.connect(
        database=dbname,
        user=user,
        password=password
    )
    conn.autocommit = True

    try:
        with conn.cursor() as cursor:

            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL,
                    conclusion_date DATE,
                    settlement_date DATE,
                    conclusion_time TIME,
                    product_title VARCHAR(50),
                    product_code VARCHAR(20),
                    currency VARCHAR(10),
                    transaction_type VARCHAR(10),
                    product_amount INTEGER,
                    price DECIMAL(16, 2),
                    summ DECIMAL(16, 2),
                    nkd DECIMAL(16, 2),
                    broker_commission DECIMAL(16, 2),
                    exchange_commission DECIMAL(16, 2),
                    transaction_number BIGINT,
                    comment VARCHAR(250),
                    status VARCHAR(10),
                    PRIMARY KEY (transaction_number, status)
                );

                CREATE TEMPORARY TABLE IF NOT EXISTS temp_transactions AS
                SELECT
                    conclusion_date,
                    settlement_date,
                    conclusion_time,
                    product_title,
                    product_code,
                    currency,
                    transaction_type,
                    product_amount,
                    price,
                    summ,
                    nkd,
                    broker_commission,
                    exchange_commission,
                    transaction_number,
                    comment,
                    status
                FROM transactions;

                COPY temp_transactions (
                    conclusion_date,
                    settlement_date,
                    conclusion_time,
                    product_title,
                    product_code,
                    currency,
                    transaction_type,
                    product_amount,
                    price,
                    summ,
                    nkd,
                    broker_commission,
                    exchange_commission,
                    transaction_number,
                    comment,
                    status)
                FROM '{url}'
                DELIMITER ','
                CSV HEADER;

                INSERT INTO transactions (
                    conclusion_date,
                    settlement_date,
                    conclusion_time,
                    product_title,
                    product_code,
                    currency,
                    transaction_type,
                    product_amount,
                    price,
                    summ,
                    nkd,
                    broker_commission,
                    exchange_commission,
                    transaction_number,
                    comment,
                    status)
                SELECT * FROM temp_transactions
                ON CONFLICT DO NOTHING;
                '''
            )

            print("[INFO] Таблица создана или существовала")

    except Exception as _ex:
        print("[INFO] Ошибка в работе в PostgreSQL", _ex)

    finally:
        if conn:
            conn.close()
            print("[INFO] PostgreSQL соединение закрыто")

if __name__ == '__main__':
    create_transactions_table()
