import sys

from app.animation import AnimationManager
from app.mailer import get_reports
from app.parser import launch_parser
from ORM.create_DB import recreate_database
from app.portfolio_accountant import build_general_portfolio
from app.writer_gsheets import main as w_gsheets
from app.command_manager import CommandManager


class InvestmentCalculator:
    """Головной класс приложения"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.version = '0.6.2'
        self.author = 'Stas Vostrov'
        self.animation: AnimationManager | None = AnimationManager()
        self.cmanager: CommandManager = CommandManager(self.name, self.animation)
        self._register_commands()

    def _register_commands(self):
        """Регистрирует все команды"""

        @self.cmanager.command('all')
        def run_all():
            """Полное обновление"""
            get_reports(self.animation)
            launch_parser()
            build_general_portfolio()
            recreate_database()
            w_gsheets()

        @self.cmanager.command('reports')
        def reports():
            """Обновление отчетов брокера"""
            get_reports(self.animation)

        @self.cmanager.command('csv')
        def csv():
            """Обновление csv-файлов"""
            launch_parser()
            build_general_portfolio()

        @self.cmanager.command('db')
        def db():
            """Обновление базы данных"""
            recreate_database()

        @self.cmanager.command('sheets')
        def sheets():
            """Обновление Google таблицы в облаке"""
            w_gsheets()

        @self.cmanager.command('exit')
        def exit_program():
            """Завершение по требованию пользователя"""
            input("Работа завершена по требованию пользователя. Для выхода нажмите Enter...")
            sys.exit(0)

        @self.cmanager.command('help')
        def show_help():
            """Показать справку по командам"""
            self.cmanager.show_help()

        @self.cmanager.command('history')
        def show_history():
            """Показать историю выполнения команд"""
            self.cmanager.show_history()

    def heading(self) -> None:
        """Заголовок приложения"""
        heading = f'{self.name} v{self.version} by {self.author}'
        print(heading, end='\n')

    def run(self) -> None:
        """Запускает главный цикл"""
        self.heading()
        while True:
            self.cmanager.execute(input('\nВведите команду\n> ').strip().lower())


if __name__ == '__main__':
    app = InvestmentCalculator()
    app.run()
