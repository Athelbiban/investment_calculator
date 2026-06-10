import logging
import sys
from functools import partial
from types import TracebackType
from app.animation import AnimationManager
from app.config import APP_LOG
from app.logger import AppLogger
from app.mailer import get_reports
from app.parser import launch_parser
from ORM.create_DB import recreate_database
from app.portfolio_accountant import build_portfolio
from app.command_manager import CommandManager
from app.writer_gsheets import update_gsheets


class InvestmentCalculator:
    """Головной класс приложения"""

    def __init__(self):
        self._name = self.__class__.__name__
        self.__version__ = '0.10.1'
        self.__author__ = 'Stas Vostrov'
        self.logger = AppLogger(self._name)
        self.animation: AnimationManager | None = AnimationManager()
        self.cmanager: CommandManager = CommandManager(self._name, self.animation)
        self._register_commands()
        self.logger.info(f"Приложение {self._name} v{self.__version__} запущено")

    def _register_commands(self):
        """Регистрирует все команды"""

        fetch_reports = partial(get_reports, self.animation)

        @self.cmanager.command('all', 'Полное обновление', steps=[
            ('Загрузка отчетов из e-mail', fetch_reports),
            ('Обработка отчетов', launch_parser),
            ('Создание csv-файлов', build_portfolio),
            ('Создание базы данных', recreate_database),
            ('Внесение изменений в Google-таблицу', update_gsheets)
        ])
        def run_all(): pass

        @self.cmanager.command('reports', 'Обновление отчетов брокера', steps=[
            ('Загрузка отчетов из e-mail', fetch_reports)
        ])
        def run_reports(): pass

        @self.cmanager.command('csv', 'Обновление csv-файлов', steps=[
            ('Обработка отчетов', launch_parser),
            ('Создание csv-файлов', build_portfolio)
        ])
        def run_csv(): pass

        @self.cmanager.command('db', 'Обновление базы данных', steps=[
            ('Создание базы данных', recreate_database)
        ])
        def run_db(): pass

        @self.cmanager.command('sheets', 'Обновление Google-таблицы', steps=[
            ('Внесение изменений в Google-таблицу', update_gsheets)
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
        heading = f'{self._name} v{self.__version__} by {self.__author__}'
        print(heading, end='\n')

    def run(self) -> None:
        """Запускает главный цикл"""
        self.heading()
        while True:
            self.cmanager.execute(input('\nВведите команду\n> ').strip().lower())


def _global_exception_handler(exc_type: type[BaseException],
                              exc_value: BaseException,
                              exc_traceback: TracebackType | None
                              ) -> None:
    """Глобальный перехватчик фатальных ошибок"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger("InvestmentCalculator")
    logger.critical("[КРИТИЧЕСКАЯ ОШИБКА ПРИЛОЖЕНИЯ]", exc_info=(exc_type, exc_value, exc_traceback))

    print("\n" + "="*60)
    print("Произошла критическая ошибка приложения")
    print("="*60)
    print(f"Подробности записаны в файл: {APP_LOG}")
    input("Нажмите Enter для выхода...")

sys.excepthook = _global_exception_handler


if __name__ == '__main__':
    InvestmentCalculator().run()
