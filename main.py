from app.mailer import get_reports
from app.parser import launch_parser
from ORM.create_DB import recreate_database
from app.portfolio_accountant import build_general_portfolio
from app.writer_gsheets import main as w_gsheets
from app.command_manager import CommandManager


def greeting():
    application_name = 'Investment Calculator v0.6.1 by Stas Vostrov'
    print(application_name, end='\n')


def main():
    greeting()
    app = CommandManager('InvestmentCalculator')

    @app.command('help')
    def show_help():
        """Показать справку по командам"""
        app.show_help()

    @app.command('all')
    def start_all():
        """Полное обновление"""
        get_reports()
        launch_parser()
        build_general_portfolio()
        recreate_database()
        w_gsheets()

    @app.command('reports')
    def reports():
        """Обновление отчетов брокера"""
        get_reports()

    @app.command('csv')
    def csv():
        """Обновление csv-файлов"""
        launch_parser()
        build_general_portfolio()

    @app.command('db')
    def db():
        """Обновление базы данных"""
        recreate_database()

    @app.command('sheets')
    def sheets():
        """Обновление Google таблицы в облаке"""
        w_gsheets()

    @app.command('exit')
    def main_exit():
        """Завершение по требованию пользователя"""
        pass

    while (response := input('\nВведите команду (список команд help): ').strip().lower()) != 'exit' :
        app.execute(response)

    input("Работа завершена по требованию пользователя. Для выхода нажмите Enter...")


if __name__ == '__main__':
    main()
