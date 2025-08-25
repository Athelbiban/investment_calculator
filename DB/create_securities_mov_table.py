import psycopg2
from passwd.config_DB import connect_attr
from passwd.config_URL_DB import url_securities_move


def create_securities_movement():

    with psycopg2.connect(connect_attr()) as conn:
        with conn.cursor() as cursor:

            conn.autocommit = True
            cursor.execute(f'''
                CREATE table if not exists securities_movement
                (
                    id SERIAL,
                    operation_date DATE,
                    security_name VARCHAR(30),
                    security_code VARCHAR(20),
                    type_operation VARCHAR(20),
                    basis_operation TEXT,
                    amount DECIMAL(17, 5),
                    purchase_date DATE,
                    price DECIMAL(16, 4),
                    broker_commission DECIMAL(16, 4),
                    exchange_commission DECIMAL(16, 4),
                    other_costs DECIMAL(16, 4),
                    primary key (id),
                    unique nulls not distinct (
                        operation_date, security_name, type_operation,
                        basis_operation, amount, price
                        )
                );

                create temp table if not exists temp_securities_movement as
                SELECT
                    operation_date,
                    security_name,
                    security_code,
                    type_operation,
                    basis_operation,
                    amount,
                    purchase_date,
                    price,
                    broker_commission,
                    exchange_commission,
                    other_costs
                FROM securities_movement;

                COPY temp_securities_movement
                (
                    operation_date,
                    security_name,
                    security_code,
                    type_operation,
                    basis_operation,
                    amount,
                    purchase_date,
                    price,
                    broker_commission,
                    exchange_commission,
                    other_costs
                )
                FROM '{url_securities_move}'
                DELIMITER ','
                CSV header;

                insert into securities_movement
                (
                    operation_date,
                    security_name,
                    security_code,
                    type_operation,
                    basis_operation,
                    amount,
                    purchase_date,
                    price,
                    broker_commission,
                    exchange_commission,
                    other_costs
                )
                select * from temp_securities_movement
                on conflict do nothing;
                '''
                           )

    print("[INFO] Таблица securities_movement создана или существовала")


if __name__ == '__main__':
    create_securities_movement()
