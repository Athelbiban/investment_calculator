import sys
from functools import partial

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
        self.version = '0.7.1'
        self.author = 'Stas Vostrov'
        self.animation: AnimationManager | None = AnimationManager()
        self.cmanager: CommandManager = CommandManager(self.name, self.animation)
        self._register_commands()

    def _register_commands(self):
        """Регистрирует все команды"""

        fetch_reports = partial(get_reports, self.animation)

        @self.cmanager.command('all', 'Полное обновление', steps=[
            ('Загрузка отчетов из e-mail', fetch_reports),
            ('Обработка отчетов', launch_parser),
            ('Создание csv-файлов', build_general_portfolio),
            ('Создание базы данных', recreate_database),
            ('Внесение изменений в Google-таблицу', w_gsheets)
        ])
        def run_all(): pass

        @self.cmanager.command('reports', 'Обновление отчетов брокера', steps=[
            ('Загрузка отчетов из e-mail', fetch_reports)
        ])
        def run_reports(): pass

        @self.cmanager.command('csv', 'Обновление csv-файлов', steps=[
            ('Обработка отчетов', launch_parser),
            ('Создание csv-файлов', build_general_portfolio)
        ])
        def run_csv(): pass

        @self.cmanager.command('db', 'Обновление базы данных', steps=[
            ('Создание базы данных', recreate_database)
        ])
        def run_db(): pass

        @self.cmanager.command('sheets', 'Обновление Google-таблицы', steps=[
            ('Внесение изменений в Google-таблицу', w_gsheets)
        ])
        def run_sheets(): pass

        @self.cmanager.command('exit', 'Завершение работы')
        def exit_program():
            input("Для завершения работы нажмите Enter...")
            sys.exit(0)

        @self.cmanager.command('help', 'Справка')
        def show_help(): self.cmanager.show_help()

        @self.cmanager.command('history', 'История')
        def show_history(): self.cmanager.show_history()

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
    InvestmentCalculator().run()
