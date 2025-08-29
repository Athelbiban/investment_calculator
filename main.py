from app.mailer import get_reports
from app.parser import launch_parser
from ORM.create_DB import recreate_database
from app.animation import start_animation_func, stop_animation_func
from app.portfolio_accountant import build_general_portfolio


def main():

    print('Investment Calculator v0.2.0 by Stas Vostrov\n')
    resp = input('Обновить отчёты брокера?(y/n): ').strip().lower()
    if resp == 'y':
        start_animation_func()
        try:
            get_reports()
        finally:
            stop_animation_func()
        print('Обновление отчетов завершено')
    elif resp == 'n':
        print('Отчёты не обновлены')
    elif resp != 'n':
        print('Неверный ответ. Отчёты не обновлены')

    resp1 = input('Обновить csv-файлы?(y/n): ').strip().lower()
    if resp1 == 'y':
        start_animation_func()
        try:
            launch_parser()
            build_general_portfolio()
        finally:
            stop_animation_func()
        print('Обновление файлов-csv завершено')
    elif resp1 == 'n':
        print('Файлы-csv не обновлены')
    elif resp1 != 'n':
        print('Неверный ответ. файлы-csv не обновлены')

    resp2 = (input('Обновить базу данных?(y/n): ')
             .strip().lower())
    if resp2 == 'y':
        start_animation_func()
        try:
            recreate_database()
        finally:
            stop_animation_func()
        print('База обновлена')
    elif resp2 == 'n':
        print('База не обновлена')
    else:
        print('Неверный ответ. База не обновлена. Обновите в ручную')

    input('\nУспешное выполнение. Нажмите Enter для выхода...')


if __name__ == '__main__':
    main()
