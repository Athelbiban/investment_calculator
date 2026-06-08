"""
Тестовый скрипт для проверки логгера и обработки ошибок.
Запускай через: python test_logger.py
"""
import time
from app.logger import AppLogger
from app.config import APP_LOG
from pathlib import Path


print("=" * 60)
print("ТЕСТИРОВАНИЕ ЛОГГЕРА")
print("=" * 60)
print(f"Лог-файл будет создан: {APP_LOG}")
print()

# Создаём логгер
logger = AppLogger("TestLogger")

print("1. Тестируем запись в лог...")
logger.info("Это тестовое INFO-сообщение")
logger.warning("Это тестовое WARNING-сообщение")
logger.error("Это тестовое ERROR-сообщение")

print("2. Тестируем специальные методы...")
logger.log_command_start("test_command")
logger.log_command_success("test_command", "Все поля заполнены")
logger.log_file_operation("чтение", Path("test.txt"), success=True)

print("3. Проверяем существование лог-файла...")
time.sleep(0.5)  # Даём время на запись
log_path = Path(APP_LOG)

if log_path.exists():
    print(f"✅ Лог-файл создан: {log_path}")
    print(f"   Размер: {log_path.stat().st_size} байт")

    # Показываем последние 10 строк
    print("\n📄 Последние записи в логе:")
    print("-" * 60)
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[-10:]:
            print(line.strip())
    print("-" * 60)
else:
    print(f"❌ Лог-файл НЕ создан: {log_path}")

print("\n4. Тестирование завершено!")
print("   Теперь проверь файл app.log вручную.")
print()

# Спрашиваем, хотим ли мы протестировать падение
response = input("Хочешь протестировать обработку падения? (y/n): ").strip().lower()
if response == 'y':
    print("\n⚠️  СЕЙЧАС ПРОИЗОЙДЁТ НАМЕРЕННОЕ ПАДЕНИЕ...")
    print("   После этого проверь, что:")
    print("   1. Окно не закрылось мгновенно")
    print("   2. В консоли показано сообщение об ошибке")
    print("   3. В app.log записан полный traceback")
    print()
    input("Нажми Enter для продолжения...")

    # Намеренное падение
    try:
        logger.info("Попытка выполнить опасную операцию...")
        raise ValueError("Это намеренная ошибка для тестирования!")
    except ValueError:
        logger.critical("Тестируем критическую ошибку", exc_info=True)
else:
    print("\n✅ Все тесты пройдены!")
    print(f"   Открой файл {APP_LOG} в текстовом редакторе, чтобы увидеть полный лог.")
