@echo off
REM Путь к проекту и виртуальному окружению
set PROJECT_DIR=C:\Users\stas\PycharmProjects\investment_calculator
set VENV_NAME=venv

REM Проверка наличия каталога виртуальной среды
IF NOT EXIST "%PROJECT_DIR%\%VENV_NAME%" (
    echo Ошибка! Каталог виртуальной среды %VENV_NAME% не найден!
    exit /B 1
)

REM Активация виртуальной среды
call "%PROJECT_DIR%\%VENV_NAME%\Scripts\activate.bat"

REM Запуск основного скрипта
python main.py

REM Деактивация виртуальной среды
call deactivate

exit /B 0
