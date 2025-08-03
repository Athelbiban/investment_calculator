import psycopg2
from passwd.config_DB import dbname, user, password


def main():

    conn = psycopg2.connect(
        database=dbname,
        user=user,
        password=password
    )

    try:
        with conn.cursor() as cursor:

            cursor.execute(f'''
                DROP TABLE IF EXISTS transactions;
                DROP TABLE IF EXISTS cashflow;
                DROP TABLE IF EXISTS securities_movement;
                '''
            )

        conn.commit()

        print("[INFO] Таблицы успешно удалены")

    except Exception as _ex:
        print("[INFO] Ошибка в работе PostgreSQL", _ex)

    finally:
        if conn:
            conn.close()
            print("[INFO] PostgreSQL соединение закрыто")


if __name__ == '__main__':
    main()
