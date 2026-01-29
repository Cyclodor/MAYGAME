# Базовое разрешение для игры (всегда 800x600 для правильного масштабирования)
# ВАЖНО: Используется целочисленное масштабирование (pixel-perfect scaling)
# Каждый пиксель текстуры отображается как NxN пикселей на экране, где N - целое число (1, 2, 3, 4...)
# Это обеспечивает четкие пиксели без размытия при изменении разрешения
BASE_WIDTH = 800
BASE_HEIGHT = 600
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE
SCALE = 1.0  # Масштаб для отображения (устаревший, используется RENDER_SCALE)

# Масштаб для преобразования координат мыши (устанавливается в main.py)
# Параметры масштабирования экрана
# Используем растягивание на весь экран без черных полос
RENDER_SCALE = 1.0  # Основной масштаб (для обратной совместимости)
RENDER_SCALE_X = 1.0  # Масштаб по X
RENDER_SCALE_Y = 1.0  # Масштаб по Y
RENDER_OFFSET_X = 0
RENDER_OFFSET_Y = 0

# Масштаб для преобразования координат мыши (устанавливается в main.py)
MOUSE_SCALE_X = 1.0
MOUSE_SCALE_Y = 1.0

# Функция для получения масштабированных координат мыши
# pygame должен быть импортирован перед использованием
def get_scaled_mouse_pos():
    """Возвращает координаты мыши, преобразованные в координаты внутреннего полотна"""
    try:
        import pygame
        mx, my = pygame.mouse.get_pos()
        # ВАЖНО: Используем целочисленное масштабирование
        # MOUSE_SCALE_X и MOUSE_SCALE_Y всегда целые числа (1, 2, 3, 4...)
        scale_x = int(max(MOUSE_SCALE_X, 1))
        scale_y = int(max(MOUSE_SCALE_Y, 1))
        # Учитываем смещение и масштаб
        mx = (mx - RENDER_OFFSET_X) / scale_x
        my = (my - RENDER_OFFSET_Y) / scale_y
        return int(mx), int(my)
    except:
        return (0, 0)

# Доступные разрешения
AVAILABLE_RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (173, 216, 230)
HIGHLIGHT = (255, 255, 0, 128)
TOOLTIP_BG = (0, 0, 0, 200) 