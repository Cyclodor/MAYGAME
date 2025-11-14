import argparse
import importlib
import os
import sys
import unittest
from datetime import datetime
from io import StringIO

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
TEST_MODULE = "debug.test_suite.test_cases"


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def build_log_filename(prefix: str = "test_results") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(LOG_DIR, f"{prefix}_{timestamp}.log")


def format_result_summary(result: unittest.TestResult, elapsed: float) -> str:
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total - failures - errors - skipped
    success_rate = 0.0 if total == 0 else (passed / total) * 100.0

    lines = [
        "# Отчёт о выполнении тестов",
        f"Дата/время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Проект: Фэнтези Стратегия",
        f"Всего тестов: {total}",
        f"Пройдено: {passed}",
        f"Провалено: {failures}",
        f"Ошибок: {errors}",
        f"Пропущено: {skipped}",
        f"Успешность: {success_rate:.2f}%",
        f"Время выполнения: {elapsed:.2f} сек",
        "",
        "## Подробности",
    ]

    def append_details(name: str, entries):
        if not entries:
            return
        lines.append(f"### {name}")
        for test, detail in entries:
            lines.append(f"- {test.id()}: {detail}")
        lines.append("")

    append_details("Неудачные тесты", result.failures)
    append_details("Ошибки", result.errors)
    append_details("Пропущенные", result.skipped)

    if not (result.failures or result.errors):
        lines.append("Все обязательные проверки из TestPlan.md выполнены успешно.")

    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Запуск автоматических тестов для проекта 'Фэнтези Стратегия'.")
    parser.add_argument(
        "--log-prefix",
        default="test_results",
        help="Префикс имени файла лога (по умолчанию test_results)"
    )
    args = parser.parse_args(argv)

    ensure_log_dir()

    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)

    try:
        module = importlib.import_module(TEST_MODULE)
    except Exception as exc:  # pragma: no cover
        print(f"Не удалось импортировать модуль тестов {TEST_MODULE}: {exc}")
        return 1

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(module)

    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)

    start_time = datetime.now()
    result = runner.run(suite)
    elapsed = (datetime.now() - start_time).total_seconds()

    log_content = stream.getvalue()
    summary = format_result_summary(result, elapsed)

    log_path = build_log_filename(args.log_prefix)
    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write(summary)
        fh.write("\n\n")
        fh.write("## Протокол unittest\n")
        fh.write(log_content)

    print(summary)
    print(f"Лог сохранён: {os.path.relpath(log_path, PROJECT_ROOT)}")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
