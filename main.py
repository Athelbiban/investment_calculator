from app.mailer import get_reports
from app.parser import launch_parser
from ORM.create_DB import recreate_database
from app.animation import start_animation_func, stop_animation_func
from app.portfolio_accountant import build_general_portfolio
from app.writer_gsheets import main as w_gsheets


def main_func(key: str, commands: dict):

    if key in commands:
        start_animation_func()
        try:
            commands[key]()
        except Exception as e:
            print(f"\nНепредвиденная ошибка: {e}")
            input('\nНажмите Enter для выхода...')
        finally:
            stop_animation_func()
        print(f"{commands[key].__doc__} выполнено")


def main_response():
    return input('\nВведите команду (список команд help): ').strip().lower()


def greeting():
    print('Investment Calculator v0.6.0 by Stas Vostrov\n')


def main():

    greeting()
    commands = {}

    def register_commands(name):
        def decorator(function):
            commands[name] = function
            return function
        return decorator

    @register_commands('help')
    def show_help():
        """Справка по командам"""
        print('\n===ДОСТУПНЫЕ КОМАНДЫ===')
        for cmd, func in commands.items():
            desc = func.__doc__ or "Нет описания"
            print(f"  {cmd:<10} - {desc}")
        print('========================')

    @register_commands('all')
    def start_all():
        """Полное обновление"""
        get_reports()
        launch_parser()
        build_general_portfolio()
        recreate_database()
        w_gsheets()

    @register_commands('reports')
    def reports():
        """Обновление отчетов брокера"""
        get_reports()

    @register_commands('csv')
    def csv():
        """Обновление csv-файлов"""
        launch_parser()
        build_general_portfolio()

    @register_commands('db')
    def db():
        """Обновление базы данных"""
        recreate_database()

    @register_commands('sheets')
    def sheets():
        """Обновление Google таблицы в облаке"""
        w_gsheets()

    @register_commands('exit')
    def main_exit():
        """Завершение по требованию пользователя"""
        pass

    while (response := main_response()) != 'exit' :
        main_func(response, commands)

    input("Работа завершена по требованию пользователя. Для выхода нажмите Enter...")


if __name__ == '__main__':
    main()
