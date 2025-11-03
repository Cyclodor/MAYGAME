@echo off
chcp 65001 >nul
echo ================================================
echo   Пересборка веб-версии игры
echo ================================================
echo.

REM Проверка наличия pygbag
python -c "import pygbag" 2>nul
if errorlevel 1 (
    echo Устанавливаю pygbag...
    pip install pygbag
    if errorlevel 1 (
        echo Не удалось установить pygbag!
        pause
        exit /b 1
    )
)

echo.
echo Удаляю старый APK если существует...
if exist "build\web\may_game.apk" (
    del /f /q "build\web\may_game.apk"
)

echo.
echo ================================================
echo Запускаю сборку веб-версии...
echo ================================================
echo.
echo ВАЖНО: Pygbag запустит веб-сервер после сборки.
echo После завершения сборки нажмите Ctrl+C для остановки.
echo.
echo Начинаю сборку из main_web.py...
echo.

REM Сборка веб-версии
py -m pygbag main_web.py

REM После завершения сборки (если не была прервана ошибкой)
if not errorlevel 1 (
    echo.
    echo ================================================
    echo Сборка завершена! Исправляю index.html...
    echo ================================================
    
    REM Исправляем путь к main_web.py в index.html
    powershell -NoProfile -Command "$content = Get-Content 'build\web\index.html' -Raw; $content = $content -replace 'main = appdir / \"assets\" / \"main\.py\"', 'main = appdir / \"assets\" / \"main_web.py\"'; Set-Content 'build\web\index.html' -Value $content -NoNewline"
    
    if exist "build\web\may_game.apk" (
        echo.
        echo ✓ APK файл создан успешно!
        echo ✓ index.html исправлен
        echo.
        echo Веб-версия готова в папке build/web/
        echo.
        echo Для запуска:
        echo 1. Откройте папку build/web/
        echo 2. Запустите RUN_WEB_SERVER.bat
    ) else (
        echo.
        echo ⚠ ВНИМАНИЕ: APK файл не найден!
        echo Проверьте ошибки выше.
    )
)

echo.
pause
