"""
Утилита для быстрой проверки генерации процедурных текстур эльфов.

Запуск:
    python tools/elf_texture_debug.py

Скрипт сгенерирует PNG-файлы в каталоге `debug/elf_textures`
и выведет краткую сводку по каждому юниту (тип атаки, наличие дальнего боя).
"""

import os
from pathlib import Path

import sys

import pygame

# Добавляем корень проекта в PYTHONPATH, чтобы корректно импортировать пакет game
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game.config import CELL_SIZE
from game.graphics import load_image


ELF_UNITS = [
    "pixie",
    "elf_scout",
    "elf_archer",
    "dryad",
    "ent",
    "druid",
    "unicorn",
]


def save_surface(surface: pygame.Surface, output_dir: Path, filename: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    pygame.image.save(surface, str(path))
    return path


def analyze_surface(surface: pygame.Surface) -> dict:
    """Возвращает простые метрики для проверки корректности текстур."""
    width, height = surface.get_size()
    pixels = pygame.PixelArray(surface.copy())
    opaque_pixels = 0
    for x in range(width):
        for y in range(height):
            if surface.get_at((x, y)).a > 0:
                opaque_pixels += 1
    del pixels
    return {
        "size": f"{width}x{height}",
        "opaque_pixels": opaque_pixels,
        "opacity_ratio": round(opaque_pixels / max(1, width * height), 3),
    }


def main():
    pygame.init()
    output_dir = Path("debug") / "elf_textures"
    print(f"[ElfTextureDebug] CELL_SIZE={CELL_SIZE}, output => {output_dir}")

    summary = []

    for unit in ELF_UNITS:
        texture_name = f"{unit}_elf"
        surface = load_image(texture_name)
        saved = save_surface(surface, output_dir, f"{texture_name}.png")
        metrics = analyze_surface(surface)
        summary.append((texture_name, saved, metrics))

    print("\n=== Отчет по текстурам ===")
    for texture_name, path, metrics in summary:
        print(
            f"{texture_name}: файл={path}, размер={metrics['size']}, "
            f"непрозрачность={metrics['opacity_ratio']*100:.1f}% "
            f"(px={metrics['opaque_pixels']})"
        )

    print("\nГотово. Изображения можно открыть для визуальной проверки.")
    pygame.quit()


if __name__ == "__main__":
    main()

