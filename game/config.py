# Базовое разрешение для игры (всегда 800x600 для правильного масштабирования)
BASE_WIDTH = 800
BASE_HEIGHT = 600
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE
SCALE = 1.0  # Масштаб для отображения

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