from functools import wraps
from typing import Callable, Dict, Any
from app.animation import start_animation_func, stop_animation_func


class CommandManager:
    """Менеджер команд"""

    def __init__(self, name='default'):
        self.name: str = name
        self.commands: Dict[str, Callable] = {}
        self.command_metadata: Dict[str, dict] = {}
        self.history: list = []

    def command(self, name: str = None, description: str = None):
        """Декоратор для регистрации команд"""
        def decorator(func):
            cmd_name = name or func.__name__

            @wraps(func)
            def wrapper(*args, **kwargs):
                self.history.append(cmd_name)
                return func(*args, **kwargs)

            self.command_metadata[cmd_name] = {
                'name': cmd_name,
                'description': description or func.__doc__ or "Нет описания",
                'original_func': func
            }
            self.commands[cmd_name] = wrapper
            return wrapper

        return decorator

    def execute(self, name: str) -> Any:
        """Выполнить команду"""

        if name not in self.commands:
            available = ", ".join(self.commands.keys())
            raise ValueError(f"Команда '{name}' не найдена. Доступные команды: {available}")

        start_animation_func()
        try:
            self.commands[name]()
        except Exception as e:
            print(f"\nНепредвиденная ошибка: {e}")
            input('\nНажмите Enter для выхода...')
        finally:
            stop_animation_func()
        print(f"{self.get_command_info(name)['description']}. Выполнено успешно")

    def get_command_info(self, name: str) -> dict or None:
        """Получить информацию о команде"""
        return self.command_metadata.get(name)

    def show_help(self):
        """Показать справку по командам"""
        print(f'\n=== МЕНЕДЖЕР КОМАНД: {self.name} ===')
        print(f'Всего команд: {len(self.commands)}')
        print(f'История вызовов: {self.history}')
        print('\n===ДОСТУПНЫЕ КОМАНДЫ===')
        for cmd_name, metadata in self.command_metadata.items():
            print(f"  {cmd_name:<12} - {metadata['description']}")
        print('========================')
