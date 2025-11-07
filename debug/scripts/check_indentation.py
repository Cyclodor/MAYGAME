#!/usr/bin/env python3
"""
Программа для проверки ошибок индентации в Python файлах
Автоматически очищает лог при достижении 3000 строк
"""

import os
import sys
import ast
import datetime

LOG_FILE = "indentation_errors.log"
MAX_LOG_LINES = 3000

def clear_log_if_needed():
    """Очищает лог файл если он превышает MAX_LOG_LINES строк"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) >= MAX_LOG_LINES:
            print(f"Лог файл достиг {len(lines)} строк, очищаем...")
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write(f"=== ЛОГ ОЧИЩЕН {datetime.datetime.now()} ===\n\n")

def log_message(message):
    """Записывает сообщение в лог файл"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")
    print(message)

def check_file_syntax(filepath):
    """Проверяет файл на ошибки синтаксиса и индентации"""
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Пытаемся скомпилировать файл
        compile(source, filepath, 'exec')
        
    except IndentationError as e:
        error_msg = f"ОШИБКА ИНДЕНТАЦИИ в {filepath}:{e.lineno}"
        error_msg += f"\n  Сообщение: {e.msg}"
        error_msg += f"\n  Строка: {e.text.strip() if e.text else 'N/A'}"
        errors.append(error_msg)
        
    except SyntaxError as e:
        error_msg = f"СИНТАКСИЧЕСКАЯ ОШИБКА в {filepath}:{e.lineno}"
        error_msg += f"\n  Сообщение: {e.msg}"
        error_msg += f"\n  Строка: {e.text.strip() if e.text else 'N/A'}"
        errors.append(error_msg)
        
    except Exception as e:
        error_msg = f"НЕИЗВЕСТНАЯ ОШИБКА в {filepath}: {str(e)}"
        errors.append(error_msg)
    
    return errors

def scan_directory(directory, extensions=['.py']):
    """Сканирует директорию на наличие Python файлов и проверяет их"""
    all_errors = []
    checked_files = 0
    
    for root, dirs, files in os.walk(directory):
        # Пропускаем виртуальные окружения и кэш
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'env']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                checked_files += 1
                
                errors = check_file_syntax(filepath)
                if errors:
                    all_errors.extend(errors)
    
    return all_errors, checked_files

def main():
    """Основная функция программы"""
    clear_log_if_needed()
    
    # Определяем директорию для сканирования
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = '.'  # Текущая директория
    
    if not os.path.exists(target_dir):
        log_message(f"ОШИБКА: Директория '{target_dir}' не существует!")
        return 1
    
    # Заголовок лога
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message("=" * 70)
    log_message(f"ПРОВЕРКА ИНДЕНТАЦИИ - {timestamp}")
    log_message(f"Директория: {os.path.abspath(target_dir)}")
    log_message("=" * 70)
    
    # Сканируем директорию
    errors, checked_files = scan_directory(target_dir)
    
    # Выводим результаты
    log_message(f"\nПроверено файлов: {checked_files}")
    
    if errors:
        log_message(f"\nНАЙДЕНО ОШИБОК: {len(errors)}\n")
        for error in errors:
            log_message(error)
            log_message("-" * 70)
    else:
        log_message("\n✅ ОШИБОК НЕ НАЙДЕНО!")
    
    log_message("=" * 70)
    log_message("")
    
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())

