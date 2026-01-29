@echo off
chcp 65001 >nul
echo ========================================
echo Пересборка BattleGame.exe
echo ========================================
echo.

REM Проверка наличия PyInstaller
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller не установлен. Устанавливаю...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo Ошибка установки PyInstaller!
        pause
        exit /b 1
    )
)

echo.
echo Очистка предыдущих сборок...
if exist build\BattleGame rmdir /s /q build\BattleGame
if exist dist\BattleGame.exe del /q dist\BattleGame.exe

echo.
echo Запуск PyInstaller...
REM Убеждаемся, что мы в правильной директории и game доступен
set PYTHONPATH=%CD%;%PYTHONPATH%
python -m PyInstaller BattleGame.spec

if errorlevel 1 (
    echo.
    echo ОШИБКА при сборке!
    pause
    exit /b 1
)

echo.
echo Проверка результата...
if exist dist\BattleGame.exe (
    echo.
    echo ========================================
    echo Сборка успешно завершена!
    echo ========================================
    echo.
    echo Файл: dist\BattleGame.exe
    echo.
    
    REM Копируем exe в корень проекта
    copy /Y dist\BattleGame.exe BattleGame.exe >nul
    if exist BattleGame.exe (
        echo BattleGame.exe также скопирован в корень проекта.
    )
    
    echo.
    echo Готово! Можно запускать BattleGame.exe
) else (
    echo.
    echo ОШИБКА: dist\BattleGame.exe не найден!
    echo Проверьте сообщения об ошибках выше.
)

echo.
pause

