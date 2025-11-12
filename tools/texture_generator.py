"""
Генератор статических (непроцедурных) текстур для игры
Создаёт PNG файлы высокого качества с тенями, градиентами и деталями
"""
import pygame
import os
import sys
import math
import random
from pathlib import Path
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ Pillow не установлен, некоторые функции будут ограничены")

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from game.config import CELL_SIZE

# Инициализируем pygame для работы с графикой
# Используем headless режим (без дисплея) для генерации текстур
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Для работы без дисплея
pygame.init()

# Настройки
TEXTURE_SIZE = CELL_SIZE  # 40x40 по умолчанию
OUTPUT_DIR = project_root / "assets" / "sprites"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Увеличенный размер для генерации (для лучшего качества)
GENERATION_SIZE = TEXTURE_SIZE * 8  # 320x320 для максимального качества


def darken_color(color, factor=0.7):
    """Затемняет цвет"""
    return tuple(max(0, int(c * factor)) for c in color)


def lighten_color(color, factor=1.3):
    """Осветляет цвет"""
    return tuple(min(255, int(c * factor)) for c in color)


def blend_colors(color1, color2, ratio=0.5):
    """Смешивает два цвета"""
    return tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(color1, color2))


def draw_gradient_circle(surface, center, radius, color, light_direction=(0, -1)):
    """Рисует круг с градиентом для объёма (оптимизированная версия)"""
    x, y = center
    light_x, light_y = light_direction
    
    # Используем несколько слоёв для имитации градиента
    # Основной круг (тёмный)
    dark_color = darken_color(color, 0.7)
    pygame.draw.circle(surface, dark_color, center, radius)
    
    # Освещённая часть (светлая)
    light_pos = (int(x + light_x * radius * 0.5), int(y + light_y * radius * 0.5))
    light_radius = int(radius * 0.6)
    light_color = lighten_color(color, 1.3)
    
    # Создаём маску для светлой части
    mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 180), (radius, radius), light_radius)
    mask_pos = (light_pos[0] - radius, light_pos[1] - radius)
    
    # Применяем светлую часть
    temp_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    temp_surf.fill(light_color)
    temp_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(temp_surf, mask_pos, special_flags=pygame.BLEND_RGBA_ADD)
    
    # Обводка
    pygame.draw.circle(surface, darken_color(color, 0.5), center, radius, max(1, radius // 15))


def draw_gradient_rect(surface, rect, color, light_direction=(0, -1), shadow=False):
    """Рисует прямоугольник с градиентом (оптимизированная версия)"""
    x, y, w, h = rect
    light_x, light_y = light_direction
    
    # Основной прямоугольник
    pygame.draw.rect(surface, color, rect)
    
    # Градиент через несколько прямоугольников
    steps = 8
    for i in range(steps):
        ratio = i / steps
        # Вычисляем яркость
        brightness = 0.7 + 0.3 * (1 - ratio) if light_y < 0 else 0.7 + 0.3 * ratio
        
        # Создаём градиент сверху вниз
        gradient_y = y + int(h * ratio)
        gradient_h = h // steps + 1
        
        # Цвет с учётом освещения
        grad_color = tuple(int(c * brightness) for c in color)
        
        # Рисуем горизонтальные полоски градиента
        if ratio < 0.5:  # Верхняя часть (светлее)
            pygame.draw.rect(surface, grad_color, (x, gradient_y, w, gradient_h))
        else:  # Нижняя часть (темнее)
            pygame.draw.rect(surface, grad_color, (x, gradient_y, w, gradient_h))
    
    # Тень снизу
    if shadow:
        shadow_rect = (x, y + h - h//4, w, h//4)
        shadow_color = darken_color(color, 0.6)
        pygame.draw.rect(surface, shadow_color, shadow_rect)
    
    # Подсветка сверху
    highlight_rect = (x + 1, y + 1, w - 2, h // 4)
    highlight_color = lighten_color(color, 1.2)
    pygame.draw.rect(surface, highlight_color, highlight_rect)
    
    # Обводка
    pygame.draw.rect(surface, darken_color(color, 0.6), rect, max(1, min(w, h) // 20))


def draw_rounded_rect(surface, rect, color, radius=5, shadow=True):
    """Рисует скруглённый прямоугольник с тенью"""
    x, y, w, h = rect
    
    if shadow:
        # Тень
        shadow_surface = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 60), (2, 2, w, h), border_radius=radius)
        surface.blit(shadow_surface, (x - 1, y + 1))
    
    # Основной прямоугольник
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=radius)
    
    # Подсветка сверху
    highlight_color = lighten_color(color, 1.2)
    pygame.draw.rect(surface, highlight_color, (x + 1, y + 1, w - 2, h // 3), border_radius=max(1, radius - 1))


def create_texture_surface(width, height):
    """Создаёт поверхность с альфа-каналом для текстуры"""
    return pygame.Surface((width, height), pygame.SRCALPHA)


def add_texture_noise(surface, intensity=3):
    """Добавляет шум для текстуры"""
    width, height = surface.get_size()
    for y in range(0, height, 2):
        for x in range(0, width, 2):
            if random.random() < 0.3:
                noise = random.randint(-intensity, intensity)
                try:
                    color = surface.get_at((x, y))
                    if len(color) == 4 and color[3] > 0:  # Проверяем альфа-канал
                        new_color = tuple(max(0, min(255, c + noise)) for c in color[:3]) + (color[3],)
                        surface.set_at((x, y), new_color)
                except:
                    pass


def generate_hero_texture(race, hero_class, team_colors):
    """Генерирует детализированную текстуру героя"""
    surface = create_texture_surface(GENERATION_SIZE, GENERATION_SIZE)
    
    scale = GENERATION_SIZE / TEXTURE_SIZE  # 8x увеличение
    
    skin = team_colors.get('skin', (255, 224, 189))
    metal = team_colors.get('metal', (180, 180, 200))
    gold = team_colors.get('gold', (255, 215, 0))
    cloth = team_colors.get('cloth', (100, 120, 200))
    main_color = team_colors.get('main', (180, 160, 100))
    accent = team_colors.get('accent', (60, 60, 200))
    
    # Прозрачный фон
    surface.fill((0, 0, 0, 0))
    
    # Адаптируем цвета в зависимости от расы
    if race == 'elf':
        # Эльфы - более зелёные и светлые
        skin = lighten_color(skin, 1.1)
        cloth = blend_colors(cloth, (60, 180, 80), 0.5)
    elif race == 'dwarf':
        # Гномы - более коренастые, каменные цвета
        skin = darken_color(skin, 0.9)
        metal = blend_colors(metal, (150, 150, 170), 0.3)
    elif race == 'undead':
        # Нежить - бледная, сероватая
        skin = blend_colors(skin, (200, 200, 200), 0.7)
        metal = darken_color(metal, 0.8)
    elif race == 'demon':
        # Демоны - красноватые оттенки
        skin = blend_colors(skin, (200, 100, 80), 0.4)
        metal = blend_colors(metal, (200, 60, 40), 0.5)
    elif race == 'shadow':
        # Тени - тёмные, фиолетовые
        skin = blend_colors(skin, (150, 120, 180), 0.5)
        metal = darken_color(metal, 0.7)
    
    # Генерируем текстуру в зависимости от класса
    if hero_class == 'warrior':
        # === РЫЦАРЬ В ДОСПЕХАХ ===
        
        # Тело (торс в доспехах)
        body_rect = (int(40*scale), int(80*scale), int(80*scale), int(100*scale))
        draw_gradient_rect(surface, body_rect, metal, light_direction=(0.3, -0.7), shadow=True)
        
        # Плечи/наплечники
        shoulder_left = (int(30*scale), int(70*scale), int(30*scale), int(30*scale))
        shoulder_right = (int(110*scale), int(70*scale), int(30*scale), int(30*scale))
        draw_gradient_rect(surface, shoulder_left, metal, light_direction=(0.5, -0.5))
        draw_gradient_rect(surface, shoulder_right, metal, light_direction=(-0.5, -0.5))
        
        # Шлем
        helmet_rect = (int(50*scale), int(40*scale), int(70*scale), int(50*scale))
        draw_gradient_rect(surface, helmet_rect, metal, light_direction=(0, -1))
        
        # Лицо (видно через забрало)
        draw_gradient_circle(surface, (int(85*scale), int(67*scale)), int(27*scale), skin, light_direction=(0.3, -0.7))
        
        # Глаза
        pygame.draw.circle(surface, (20, 20, 30), (int(75*scale), int(60*scale)), int(3*scale))
        pygame.draw.circle(surface, (20, 20, 30), (int(95*scale), int(60*scale)), int(3*scale))
        pygame.draw.circle(surface, (200, 200, 255), (int(75*scale), int(60*scale)), int(1*scale))
        pygame.draw.circle(surface, (200, 200, 255), (int(95*scale), int(60*scale)), int(1*scale))
        
        # Корона на шлеме
        crown_rect = (int(60*scale), int(35*scale), int(50*scale), int(12*scale))
        draw_gradient_rect(surface, crown_rect, gold, light_direction=(0, -1))
        # Зубцы короны
        for i in range(5):
            x = int(62*scale + i * 10*scale)
            pygame.draw.polygon(surface, gold, [
                (x, int(35*scale)), (x + int(4*scale), int(28*scale)), 
                (x + int(8*scale), int(35*scale))
            ])
            # Подсветка на зубцах
            pygame.draw.polygon(surface, lighten_color(gold, 1.4), [
                (x + int(1*scale), int(35*scale)), (x + int(4*scale), int(30*scale)), 
                (x + int(7*scale), int(35*scale))
            ])
        
        # Детали доспеха (вертикальные линии)
        for x_pos in [int(60*scale), int(100*scale)]:
            pygame.draw.line(surface, darken_color(metal, 0.7), 
                           (x_pos, int(80*scale)), (x_pos, int(180*scale)), int(2*scale))
            pygame.draw.line(surface, lighten_color(metal, 1.3), 
                           (x_pos + int(1*scale), int(80*scale)), 
                           (x_pos + int(1*scale), int(180*scale)), int(1*scale))
        
        # Меч
        sword_x = int(120*scale)
        pygame.draw.rect(surface, (240, 240, 255), (sword_x, int(100*scale), int(8*scale), int(80*scale)))
        # Остриё меча
        pygame.draw.polygon(surface, (255, 255, 255), [
            (sword_x + int(4*scale), int(180*scale)),
            (sword_x, int(190*scale)),
            (sword_x + int(8*scale), int(190*scale))
        ])
        # Гарда меча
        guard_rect = (int(112*scale), int(95*scale), int(16*scale), int(8*scale))
        draw_gradient_rect(surface, guard_rect, gold, light_direction=(0, -1))
        # Рукоять
        pygame.draw.rect(surface, darken_color(gold, 0.6), 
                       (int(115*scale), int(103*scale), int(10*scale), int(15*scale)))
        
        # Щит
        shield_center = (int(25*scale), int(130*scale))
        shield_radius = int(35*scale)
        # Основа щита
        draw_gradient_circle(surface, shield_center, shield_radius, accent, light_direction=(0.5, -0.5))
        # Обод щита
        pygame.draw.circle(surface, darken_color(accent, 0.6), shield_center, shield_radius, int(3*scale))
        pygame.draw.circle(surface, lighten_color(accent, 1.3), shield_center, shield_radius - int(2*scale), int(1*scale))
        # Эмблема на щите
        pygame.draw.circle(surface, gold, shield_center, int(15*scale))
        pygame.draw.circle(surface, lighten_color(gold, 1.4), shield_center, int(12*scale))
        # Крест на щите
        pygame.draw.line(surface, darken_color(gold, 0.7), 
                       (shield_center[0] - int(10*scale), shield_center[1]),
                       (shield_center[0] + int(10*scale), shield_center[1]), int(2*scale))
        pygame.draw.line(surface, darken_color(gold, 0.7), 
                       (shield_center[0], shield_center[1] - int(10*scale)),
                       (shield_center[0], shield_center[1] + int(10*scale)), int(2*scale))
        
    elif hero_class == 'archer':
        # === ЛУЧНИК ===
        
        # Туника
        tunic_rect = (int(50*scale), int(90*scale), int(60*scale), int(90*scale))
        draw_gradient_rect(surface, tunic_rect, cloth, light_direction=(0.3, -0.7), shadow=True)
        
        # Пояс
        belt_rect = (int(52*scale), int(120*scale), int(56*scale), int(8*scale))
        draw_gradient_rect(surface, belt_rect, (80, 60, 40), light_direction=(0, -1))
        
        # Лицо
        face_center = (int(80*scale), int(55*scale))
        draw_gradient_circle(surface, face_center, int(28*scale), skin, light_direction=(0.3, -0.7))
        
        # Глаза
        pygame.draw.ellipse(surface, (20, 20, 30), (int(72*scale), int(50*scale), int(5*scale), int(8*scale)))
        pygame.draw.ellipse(surface, (20, 20, 30), (int(83*scale), int(50*scale), int(5*scale), int(8*scale)))
        pygame.draw.circle(surface, (150, 100, 50), (int(74*scale), int(54*scale)), int(2*scale))
        pygame.draw.circle(surface, (150, 100, 50), (int(85*scale), int(54*scale)), int(2*scale))
        
        # Нос
        pygame.draw.ellipse(surface, darken_color(skin, 0.9), (int(78*scale), int(58*scale), int(4*scale), int(3*scale)))
        
        # Рот
        pygame.draw.arc(surface, (100, 50, 50), (int(75*scale), int(62*scale), int(10*scale), int(6*scale)), 0, 3.14, int(1*scale))
        
        # Капюшон
        hood_points = [
            (int(45*scale), int(45*scale)),
            (int(50*scale), int(25*scale)),
            (int(80*scale), int(20*scale)),
            (int(110*scale), int(25*scale)),
            (int(115*scale), int(45*scale)),
            (int(110*scale), int(70*scale)),
            (int(50*scale), int(70*scale))
        ]
        pygame.draw.polygon(surface, darken_color(cloth, 0.8), hood_points)
        # Тень на капюшоне
        pygame.draw.polygon(surface, darken_color(cloth, 0.6), 
                          [(int(50*scale), int(70*scale)), (int(110*scale), int(70*scale)), 
                           (int(115*scale), int(45*scale))])
        
        # Лук (дуга)
        bow_center = (int(30*scale), int(80*scale))
        for angle in range(30, 150, 3):
            rad = math.radians(angle)
            dist = int(50*scale)
            x = int(bow_center[0] + dist * math.cos(rad))
            y = int(bow_center[1] + dist * math.sin(rad))
            pygame.draw.circle(surface, (140, 100, 60), (x, y), int(2*scale))
        
        # Тетива
        pygame.draw.line(surface, (200, 200, 200), 
                       (int(50*scale), int(60*scale)), (int(50*scale), int(100*scale)), int(1*scale))
        
        # Стрела
        arrow_start = (int(70*scale), int(95*scale))
        arrow_end = (int(105*scale), int(65*scale))
        pygame.draw.line(surface, (180, 160, 140), arrow_start, arrow_end, int(3*scale))
        # Оперение стрелы
        pygame.draw.polygon(surface, (100, 150, 200), [
            (int(72*scale), int(93*scale)), (int(68*scale), int(88*scale)),
            (int(70*scale), int(95*scale)), (int(72*scale), int(97*scale))
        ])
        # Наконечник
        pygame.draw.polygon(surface, (200, 200, 220), [
            arrow_end, (int(102*scale), int(62*scale)), (int(108*scale), int(62*scale))
        ])
        
        # Колчан
        quiver_rect = (int(105*scale), int(75*scale), int(12*scale), int(50*scale))
        draw_gradient_rect(surface, quiver_rect, (100, 80, 40), light_direction=(0.5, -0.5))
        # Стрелы в колчане
        for i in range(3):
            y_pos = int(80*scale + i * 12*scale)
            pygame.draw.line(surface, (120, 100, 60), 
                           (int(108*scale), y_pos), (int(115*scale), y_pos + int(8*scale)), int(2*scale))
    
    else:  # mage
        # === МАГ ===
        
        # Мантия
        robe_rect = (int(45*scale), int(100*scale), int(70*scale), int(100*scale))
        draw_gradient_rect(surface, robe_rect, cloth, light_direction=(0.3, -0.7), shadow=True)
        
        # Складки на мантии
        for x_pos in [int(55*scale), int(75*scale), int(95*scale)]:
            pygame.draw.line(surface, darken_color(cloth, 0.8), 
                           (x_pos, int(100*scale)), (x_pos, int(200*scale)), int(2*scale))
        
        # Лицо
        face_center = (int(80*scale), int(55*scale))
        draw_gradient_circle(surface, face_center, int(30*scale), skin, light_direction=(0.3, -0.7))
        
        # Борода
        beard_points = [
            (int(70*scale), int(70*scale)), (int(65*scale), int(85*scale)),
            (int(75*scale), int(88*scale)), (int(85*scale), int(88*scale)),
            (int(95*scale), int(85*scale)), (int(90*scale), int(70*scale))
        ]
        pygame.draw.polygon(surface, darken_color(skin, 0.7), beard_points)
        
        # Глаза
        pygame.draw.circle(surface, (50, 30, 100), (int(75*scale), int(55*scale)), int(4*scale))
        pygame.draw.circle(surface, (50, 30, 100), (int(85*scale), int(55*scale)), int(4*scale))
        pygame.draw.circle(surface, (150, 100, 255), (int(75*scale), int(55*scale)), int(2*scale))
        pygame.draw.circle(surface, (150, 100, 255), (int(85*scale), int(55*scale)), int(2*scale))
        # Свечение глаз
        glow_surf = pygame.Surface((int(12*scale), int(12*scale)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (150, 100, 255), (int(6*scale), int(6*scale)), int(6*scale))
        glow_surf.set_alpha(100)
        surface.blit(glow_surf, (int(75*scale - 6*scale), int(55*scale - 6*scale)))
        surface.blit(glow_surf, (int(85*scale - 6*scale), int(55*scale - 6*scale)))
        
        # Шляпа
        hat_points = [
            (int(60*scale), int(45*scale)), (int(80*scale), int(15*scale)),
            (int(100*scale), int(45*scale))
        ]
        pygame.draw.polygon(surface, darken_color(cloth, 0.7), hat_points)
        # Звезда на шляпе
        star_center = (int(80*scale), int(25*scale))
        star_points = []
        for i in range(5):
            angle = math.radians(i * 72)
            x = int(star_center[0] + int(8*scale) * math.cos(angle))
            y = int(star_center[1] + int(8*scale) * math.sin(angle))
            star_points.append((x, y))
        pygame.draw.polygon(surface, gold, star_points)
        
        # Посох
        staff_x = int(115*scale)
        pygame.draw.rect(surface, (140, 120, 80), (staff_x, int(50*scale), int(6*scale), int(100*scale)))
        
        # Кристалл на посохе
        crystal_center = (int(118*scale), int(50*scale))
        # Внешнее свечение
        for radius in [int(18*scale), int(12*scale), int(8*scale)]:
            glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            alpha = int(80 * (1 - radius / 20))
            # Рисуем круг без альфа, затем применяем прозрачность
            pygame.draw.circle(glow_surf, (100, 180, 255), (radius, radius), radius)
            # Применяем альфа-канал через set_alpha
            glow_surf.set_alpha(alpha)
            surface.blit(glow_surf, (crystal_center[0] - radius, crystal_center[1] - radius))
        
        # Основной кристалл
        draw_gradient_circle(surface, crystal_center, int(12*scale), (100, 180, 255), light_direction=(0.5, -0.5))
        # Блик на кристалле
        pygame.draw.circle(surface, (200, 230, 255), 
                         (int(crystal_center[0] - 3*scale), int(crystal_center[1] - 3*scale)), int(4*scale))
    
    # Добавляем текстуру (шум) - только немного для реалистичности
    # add_texture_noise(surface, intensity=1)  # Отключено для скорости
    
    # Масштабируем до нужного размера с антиалиасингом
    scaled = pygame.transform.smoothscale(surface, (TEXTURE_SIZE, TEXTURE_SIZE))
    return scaled


def generate_unit_texture(unit_type, team, team_colors):
    """Генерирует текстуру юнита"""
    # Пока используем базовую реализацию, можно расширить
    return generate_hero_texture(team, 'warrior', team_colors)


def save_texture(surface, filename):
    """Сохраняет текстуру в PNG файл"""
    filepath = OUTPUT_DIR / filename
    pygame.image.save(surface, str(filepath))
    print(f"✓ Сохранено: {filepath}")


def generate_all_hero_textures():
    """Генерирует все текстуры героев"""
    
    # Цветовые схемы для разных рас
    color_schemes = {
        'human': {
            'main': (180, 160, 100),
            'accent': (60, 60, 200),
            'metal': (180, 180, 200),
            'gold': (255, 215, 0),
            'skin': (255, 224, 189),
            'cloth': (100, 120, 200)
        },
        'elf': {
            'main': (60, 180, 80),
            'accent': (40, 140, 60),
            'metal': (120, 200, 120),
            'gold': (200, 180, 60),
            'skin': (220, 255, 200),
            'cloth': (100, 200, 100)
        },
        'dwarf': {
            'main': (100, 120, 160),
            'accent': (80, 100, 140),
            'metal': (200, 200, 220),
            'gold': (255, 215, 0),
            'skin': (220, 180, 120),
            'cloth': (140, 160, 180)
        },
        'undead': {
            'main': (120, 100, 180),
            'accent': (80, 60, 120),
            'metal': (180, 180, 200),
            'gold': (180, 120, 255),
            'skin': (220, 220, 220),
            'cloth': (80, 60, 120)
        },
        'demon': {
            'main': (140, 40, 20),
            'accent': (100, 20, 10),
            'metal': (200, 60, 40),
            'gold': (255, 100, 60),
            'skin': (240, 120, 80),
            'cloth': (160, 40, 80)
        },
        'shadow': {
            'main': (40, 0, 60),
            'accent': (80, 0, 120),
            'metal': (100, 80, 120),
            'gold': (180, 120, 255),
            'skin': (200, 180, 120),
            'cloth': (60, 0, 90)
        }
    }
    
    hero_classes = ['warrior', 'archer', 'mage']
    races = list(color_schemes.keys())
    
    print("🎨 Генерация детализированных текстур героев...")
    print(f"📁 Папка вывода: {OUTPUT_DIR}")
    print(f"📐 Размер генерации: {GENERATION_SIZE}x{GENERATION_SIZE} → {TEXTURE_SIZE}x{TEXTURE_SIZE}")
    print()
    
    count = 0
    for race in races:
        colors = color_schemes[race]
        for hero_class in hero_classes:
            print(f"  Генерация: {race} {hero_class}...", end=" ", flush=True)
            texture = generate_hero_texture(race, hero_class, colors)
            filename = f"hero_{race}_{hero_class}.png"
            save_texture(texture, filename)
            count += 1
    
    print()
    print(f"✅ Сгенерировано {count} детализированных текстур!")


def generate_custom_texture(name, width=TEXTURE_SIZE, height=TEXTURE_SIZE, 
                           callback=None):
    """
    Генерирует кастомную текстуру с помощью функции обратного вызова
    """
    if callback is None:
        print(f"❌ Ошибка: не указана функция для генерации текстуры '{name}'")
        return
    
    gen_width = width * 8
    gen_height = height * 8
    surface = create_texture_surface(gen_width, gen_height)
    
    callback(surface, gen_width, gen_height)
    
    scaled = pygame.transform.smoothscale(surface, (width, height))
    
    filename = f"{name}.png"
    save_texture(scaled, filename)


if __name__ == "__main__":
    print("=" * 60)
    print("🎨 Генератор статических текстур (улучшенная версия)")
    print("=" * 60)
    print()
    
    generate_all_hero_textures()
    
    print()
    print("=" * 60)
    print("✨ Готово! Текстуры сохранены в assets/sprites/")
    print("=" * 60)
