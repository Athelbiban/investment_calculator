from app.mailer import get_reports
from app.parser import launch_parser
from ORM.create_DB import recreate_database
from app.animation import start_animation_func, stop_animation_func
from app.portfolio_accountant import build_general_portfolio
from app.writer_gsheets import main as w_gsheets


def main():

    print('Investment Calculator v0.3.1 by Stas Vostrov\n')
    resp = input('Обновить отчёты брокера?(y/n): ').strip().lower()
    if resp == 'y' or 'н':
        start_animation_func()
        try:
            get_reports()
        finally:
            stop_animation_func()
        print('Обновление отчетов завершено')
    elif resp == 'n' or 'т':
        print('Отчёты не обновлены')
    elif resp != 'n' or 'т':
        print('Неверный ответ. Отчёты не обновлены')

    resp1 = input('Обновить csv-файлы?(y/n): ').strip().lower()
    if resp == 'y' or 'н':
        start_animation_func()
        try:
            launch_parser()
            build_general_portfolio()
        finally:
            stop_animation_func()
        print('Обновление файлов-csv завершено')
    elif resp1 == 'n' or 'т':
        print('Файлы-csv не обновлены: отменено пользователем')
    elif resp1 != 'n' or 'т':
        print('Неверный ответ. файлы-csv не обновлены')

    resp2 = (input('Обновить базу данных?(y/n): ')
             .strip().lower())
    if resp == 'y' or 'н':
        start_animation_func()
        try:
            recreate_database()
        finally:
            stop_animation_func()
        print('Обновление базы завершено')
    elif resp2 == 'n' or 'т':
        print('База не обновлена: отменено пользователем')
    else:
        print('Неверный ответ. База не обновлена')

    resp3 = input('Обновить Google Таблицу в облаке?(y/n): ').strip().lower()
    if resp3 == 'y' or 'н':
        start_animation_func()
        try:
            w_gsheets()
        finally:
            stop_animation_func()
        print('Обновление Google Таблицы завершено')
    elif resp3 == 'n' or 'т':
        print('Google Таблица не обновлена: отменено пользователем')
    else:
        print('Неверный ответ. Google Таблица не обновлена')

    input('\nУспешное выполнение. Нажмите Enter для выхода...')


if __name__ == '__main__':
    main()
