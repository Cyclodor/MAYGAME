"""
Простой скрипт для генерации отчета о проблеме с берсерком.
Запустите этот файл после игры для получения анализа.
"""

from berserker_debug import generate_report

if __name__ == '__main__':
    print("Генерация отчета о проблеме с руной берсерка...")
    print("=" * 80)
    generate_report()
    print("\nГотово! Проверьте файл berserker_debug_report.txt")

