import imaplib
import gspread
from functools import wraps
from typing import Any
from collections.abc import Callable, Sequence
from app.animation import AnimationManager
from app.config import WORKSHEET_NAME


class CommandManager:
    """Менеджер команд"""

    def __init__(self, name: str='default', animation: AnimationManager | None=None):
        self.name: str = name
        self.animation: AnimationManager | None = animation
        self.commands: dict[str, Callable] = {}
        self.command_metadata: dict[str, dict[str, Any]] = {}
        self.history: list[str] = []
        self._builtin_commands = ['help', 'history', 'exit']

    def command(self, name: str | None = None,
                description: str | None = None,
                steps: Sequence[tuple[str, Callable]] | None = None
                ) -> Callable:
        """Декоратор для регистрации команд"""

        def decorator(func) -> Callable:
            cmd_name = name or func.__name__
            cmd_desc = description or func.__doc__ or "Нет описания"

            if steps:
                def step_runner(captured_steps=steps):
                    for msg, step_func in captured_steps:
                        if self.animation:
                            with self.animation.status_context(msg):
                                result = step_func()
                        else:
                            result = step_func()
                    return result
                target = step_runner
            else:
                target = func

            @wraps(func)
            def wrapper() -> Any:
                self.history.append(cmd_name)
                return target()

            self.command_metadata[cmd_name] = {
                'name': cmd_name,
                'description': cmd_desc,
                'original_func': func,
                'steps': steps
            }
            self.commands[cmd_name] = wrapper

            return wrapper
        return decorator

    def execute(self, name: str) -> None:
        """Выполнить команду"""

        if name not in self.commands:
            print(f"Команда '{name}' не найдена. Список команд: help")
            return
        elif name in self._builtin_commands:
            self.commands[name]()
            return

        if self.animation:
            try:
                self.animation.start()
                result = self.commands[name]()
                self.animation.stop()

                cmd_info = self.get_command_info(name)
                desc = cmd_info.get('description', 'Команда') if cmd_info else 'Команда пользователя'

                if name == 'sheets' and isinstance(result, dict):
                    print(f"{desc}. Выполнено успешно"
                          f"\nОбновлено записей: {result.get('updated', 0)}")
                    if result.get('not_found'):
                        print(f"Тикеры не найдены в таблице: {', '.join(result['not_found'])}")
                elif name == 'reports' and isinstance(result, dict):
                    print(f"{desc}. Выполнено успешно"
                          f"\nЗагружено новых отчетов: {result.get('updated_count', 0)}"
                          f"\nВсего отчетов: {result.get('total_amount_files', 0)}")
                else:
                    print(f"{desc}. Выполнено успешно")

            except imaplib.IMAP4.error as e:
                self.animation.stop()
                print(f"Ошибка авторизации или подключения: {e}")
                input('\nНажмите Enter для продолжения...')

            except gspread.exceptions.WorksheetNotFound:
                self.animation.stop()
                print(f"\nОшибка: Лист '{WORKSHEET_NAME}' не найден в таблице. Проверьте .env")
                input('\nНажмите Enter для продолжения...')

            except Exception as e:
                self.animation.stop()
                print(f"\nНепредвиденная ошибка: {e}")
                input('\nНажмите Enter для продолжения...')


    def get_command_info(self, name: str) -> dict[str, Any] | None:
        """Получить информацию о команде"""
        return self.command_metadata.get(name)

    def show_help(self) -> None:
        """Показать справку по командам"""
        print('\n===ДОСТУПНЫЕ КОМАНДЫ===')
        for cmd_name, metadata in sorted(self.command_metadata.items()):
            print(f"  {cmd_name:<12} - {metadata['description']}")
        print('========================')

    def show_history(self) -> None:
        """Показать историю вызовов"""
        if not self.history:
            print('История пуста')
            return

        print(f'\n=== ИСТОРИЯ КОМАНД ({len(self.history)}) ===')
        print('Показаны 10 последних')
        for i, cmd in enumerate(self.history[-10:], 1):
            print(f'  {i:2}. {cmd}')
        if len(self.history) > 10:
            print(f'  ... и ещё {len(self.history) - 10}')
        print('========================')
