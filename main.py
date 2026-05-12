from app.mailer import get_reports
from app.parser import launch_parser
from ORM.create_DB import recreate_database
from app.animation import start_animation_func, stop_animation_func
from app.portfolio_accountant import build_general_portfolio
from app.writer_gsheets import main as w_gsheets



def main_response():
    return input('\nВведите команду (список команд help): ').strip().lower()


def main_help():
    print('\nhelp - список команд'
          '\nall - выполнить все действия автоматически'
          '\nupdreports - обновить отчеты брокера'
          '\nupdcsv - обновить csv-файлы'
          '\nupddb - обновить базу данных'
          '\nupdgsheets - обновить Google-таблицу в облаке')


def main():

    print('Investment Calculator v0.5.0 by Stas Vostrov\n')

    command_list = ['help', 'all', 'updreports', 'updcsv', 'upddb', 'updgsheets', 'exit',
                    'рудз', 'фдд', 'гзвкузщкеы', 'гзвсым', 'гзвви', 'гзвпырууеы', 'учше'
    ]

    while (response := main_response()) != 'exit':

        if response == 'help' or response == 'рудз':
            main_help()
            continue

        elif response == 'all' or response == 'фдд':
            start_animation_func()
            try:
                get_reports()
                launch_parser()
                build_general_portfolio()
                recreate_database()
                w_gsheets()
            except Exception as e:
                print(f"\nНепредвиденная ошибка: {e}")
                input('\nНажмите Enter для выхода...')
            finally:
                stop_animation_func()
            print('Полное обновление выполнено\n')
            continue

        elif response == 'updreports' or response == 'гзвкузщкеы':
            start_animation_func()
            try:
                get_reports()
            finally:
                stop_animation_func()
            print('Обновление отчетов завершено\n')
            continue

        elif response == 'updcsv' or response == 'гзвсым':
            start_animation_func()
            try:
                launch_parser()
                build_general_portfolio()
            finally:
                stop_animation_func()
            print('Обновление файлов-csv завершено\n')
            continue

        elif response == 'upddb' or response == 'гзвви':
            start_animation_func()
            try:
                recreate_database()
            finally:
                stop_animation_func()
            print('Обновление базы завершено\n')
            continue

        elif response == 'updgsheets' or response == 'гзвпырууеы':
            start_animation_func()
            try:
                w_gsheets()
            finally:
                stop_animation_func()
            print('Обновление Google Таблицы завершено\n')
            continue

        else:
            print('Неверный ответ\n')
            continue


if __name__ == '__main__':
    main()
