from functools import wraps
from collections.abc import Callable
from app.animation import AnimationManager


class CommandManager:
    """Менеджер команд"""

    def __init__(self, name: str='default', animation: AnimationManager | None=None):
        self.name: str = name
        self.animation: AnimationManager | None = animation
        self.commands: dict[str, Callable] = {}
        self.command_metadata: dict[str, dict[str,str | Callable]] = {}
        self.history: list[str] = []
        self._builtin_commands = ['help', 'history', 'exit']

    def command(self, name: str = None, description: str = None) -> Callable:
        """Декоратор для регистрации команд"""
        def decorator(func) -> Callable:
            cmd_name = name or func.__name__

            @wraps(func)
            def wrapper(*args, **kwargs) -> Callable:
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

    def execute(self, name: str) -> None:
        """Выполнить команду"""

        if name not in self.commands:
            print(f"Команда '{name}' не найдена. Список команд: help")
            return
        elif name in self._builtin_commands:
            self.commands[name]()
            return

        try:
            self.animation.start()
            self.commands[name]()
            self.animation.stop()
            print(f"{self.get_command_info(name)['description']}. Выполнено успешно")
        except Exception as e:
            self.animation.stop()
            print(f"\nНепредвиденная ошибка: {e}")
            input('\nНажмите Enter для продолжения...')

    def get_command_info(self, name: str) -> dict or None:
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
