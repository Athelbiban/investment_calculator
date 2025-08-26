import psycopg2
from connect_DB import connect_attr


def main():

    with psycopg2.connect(connect_attr()) as conn:
        with conn.cursor() as cursor:

            cursor.execute(f'''
                DROP TABLE IF EXISTS transactions;
                DROP TABLE IF EXISTS cashflow;
                DROP TABLE IF EXISTS securities_movement;
                '''
            )

        conn.commit()
        print("[INFO] Таблицы успешно удалены")


if __name__ == '__main__':
    main()
