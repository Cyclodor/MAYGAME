import pygame
import random
import math
from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_WIDTH, GRID_HEIGHT

def load_image(name, scale=1):
    image = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    unit, team = name.rsplit('_', 1)
    # Цветовые схемы
    if team == 'human':
        main_color = (180, 160, 100)
        accent = (60, 60, 200)
        metal = (180, 180, 200)
        gold = (255, 215, 0)
        skin = (255, 224, 189)
        cloth = (100, 120, 200)
    else:
        main_color = (120, 100, 180)
        accent = (80, 40, 120)
        metal = (180, 180, 200)
        gold = (180, 120, 255)
        skin = (200, 200, 220)
        cloth = (80, 60, 120)
    # Герой
    if unit == 'hero':
        if team == 'elf':
            image.fill((60, 180, 80))  # зелёный фон
            # Плащ
            pygame.draw.rect(image, (120, 220, 120), (8, 20, 24, 18))
            # Лицо
            pygame.draw.ellipse(image, (220, 255, 200), (10, 8, 20, 18))
            # Корона/венец
            pygame.draw.polygon(image, (255, 220, 80), [(12, 12), (16, 4), (20, 12), (24, 4), (28, 12)])
            # Глаза
            pygame.draw.circle(image, (0,80,0), (16, 16), 2)
            pygame.draw.circle(image, (0,80,0), (24, 16), 2)
            # Уши
            pygame.draw.polygon(image, (220, 255, 200), [(10, 16), (4, 10), (12, 12)])
            pygame.draw.polygon(image, (220, 255, 200), [(30, 16), (36, 10), (28, 12)])
            # Золотая брошь
            pygame.draw.circle(image, (255, 220, 80), (20, 28), 4)
        elif team == 'demon':
            image.fill((120, 40, 20))  # тёмно-красный фон
            # Плащ
            pygame.draw.rect(image, (180, 60, 40), (8, 20, 24, 18))
            # Лицо
            pygame.draw.ellipse(image, (255, 180, 120), (10, 8, 20, 18))
            # Рога
            pygame.draw.polygon(image, (180, 60, 40), [(12, 12), (8, 2), (16, 8)])
            pygame.draw.polygon(image, (180, 60, 40), [(28, 12), (32, 2), (24, 8)])
            # Глаза
            pygame.draw.circle(image, (200,0,0), (16, 16), 2)
            pygame.draw.circle(image, (200,0,0), (24, 16), 2)
            # Клыки
            pygame.draw.polygon(image, (255,255,255), [(16, 24), (18, 28), (20, 24)])
            pygame.draw.polygon(image, (255,255,255), [(24, 24), (22, 28), (20, 24)])
            # Огненный шар
            pygame.draw.circle(image, (255, 80, 20), (20, 32), 5)
        elif team == 'human':
            image.fill(main_color)
            # Мантия
            pygame.draw.rect(image, cloth, (8, 20, 24, 18))
            # Лицо
            pygame.draw.ellipse(image, skin, (10, 8, 20, 18))
            # Корона
            pygame.draw.polygon(image, gold, [(12, 12), (16, 4), (20, 12), (24, 4), (28, 12)])
            # Глаза
            pygame.draw.circle(image, (0,0,0), (16, 16), 2)
            pygame.draw.circle(image, (0,0,0), (24, 16), 2)
            # Плащ
            pygame.draw.arc(image, accent, (6, 18, 28, 18), 3.14, 0, 3)
        elif team == 'undead':
            image.fill(main_color)
            pygame.draw.ellipse(image, (220,220,220), (10, 8, 20, 18))
            pygame.draw.polygon(image, gold, [(12, 12), (16, 4), (20, 12), (24, 4), (28, 12)])
            pygame.draw.arc(image, accent, (6, 18, 28, 18), 3.14, 0, 3)
            pygame.draw.circle(image, (80,40,120), (16, 16), 2)
            pygame.draw.circle(image, (80,40,120), (24, 16), 2)
        elif team == 'dwarf':
            image.fill((100, 120, 160))
            pygame.draw.rect(image, (180,180,200), (8, 20, 24, 18)) # броня
            pygame.draw.ellipse(image, (220,200,120), (10, 8, 20, 18)) # лицо
            pygame.draw.rect(image, (120,120,160), (8, 28, 24, 10)) # пояс
            pygame.draw.polygon(image, (255,215,0), [(12,12),(16,4),(20,12),(24,4),(28,12)]) # шлем
            pygame.draw.circle(image, (80,80,100), (20, 28), 6) # борода
        elif team == 'shadow':
            image.fill((40,0,60))
            pygame.draw.rect(image, (80,0,120), (8, 20, 24, 18)) # плащ
            pygame.draw.ellipse(image, (220,200,40), (10, 8, 20, 18)) # лицо
            pygame.draw.polygon(image, (255,215,0), [(12,12),(16,4),(20,12),(24,4),(28,12)]) # маска/корона
            pygame.draw.circle(image, (40,40,40), (20, 28), 6) # тень
    # Воин
    elif unit == 'warrior':
        image.fill(main_color)
        # Тело
        pygame.draw.rect(image, metal, (12, 16, 16, 18))
        # Шлем
        pygame.draw.ellipse(image, metal, (12, 6, 16, 14))
        pygame.draw.rect(image, accent, (12, 12, 16, 6))
        # Меч
        pygame.draw.rect(image, (180,180,180), (26, 24, 6, 16))
        pygame.draw.rect(image, (120,120,120), (28, 36, 2, 6))
        # Щит
        pygame.draw.ellipse(image, accent, (2, 22, 10, 16))
    # Лучник
    elif unit == 'archer':
        image.fill(main_color)
        # Капюшон
        pygame.draw.ellipse(image, cloth, (10, 4, 20, 16))
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 10, 12, 10))
        # Тело
        pygame.draw.rect(image, cloth, (14, 20, 12, 16))
        # Лук
        pygame.draw.arc(image, (120, 80, 40), (4, 10, 28, 28), 3.14/2, 3*3.14/2, 3)
        # Стрела
        pygame.draw.line(image, (180,180,180), (18, 24), (28, 8), 2)
    # Рыцарь
    elif unit == 'knight':
        image.fill(main_color)
        # Латы
        pygame.draw.rect(image, metal, (10, 16, 20, 20))
        pygame.draw.ellipse(image, metal, (10, 6, 20, 14))
        # Щит
        pygame.draw.ellipse(image, accent, (2, 22, 12, 18))
        # Меч
        pygame.draw.rect(image, (180,180,180), (28, 24, 6, 16))
        pygame.draw.rect(image, (120,120,120), (30, 36, 2, 6))
        # Перо на шлеме
        pygame.draw.line(image, gold, (20, 8), (20, 2), 2)
    # --- Люди ---
    elif unit == 'peasant':
        # Основа
        image.fill((140, 120, 100))
        # Детализированная одежда крестьянина
        pygame.draw.rect(image, (180,140,80), (14, 20, 12, 18))  # рубаха
        pygame.draw.rect(image, (160,120,60), (16, 22, 8, 14))  # внутренняя рубаха
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 8, 12, 12))
        pygame.draw.circle(image, (0,0,0), (18, 14), 1)  # глаз
        pygame.draw.circle(image, (0,0,0), (22, 14), 1)  # глаз
        pygame.draw.circle(image, (180,160,120), (20, 18), 1)  # нос
        # Волосы
        pygame.draw.ellipse(image, (100,80,40), (14, 6, 12, 8))
        # Мотыга
        pygame.draw.line(image, (120,80,40), (20, 38), (8, 44), 4)  # рукоять
        pygame.draw.line(image, (120,80,40), (20, 38), (32, 44), 4)  # рукоять
        pygame.draw.polygon(image, (160,160,180), [(8,44),(4,48),(12,48)])  # наконечник
        pygame.draw.polygon(image, (160,160,180), [(32,44),(28,48),(36,48)])  # наконечник
        # Пояс
        pygame.draw.rect(image, (100,80,60), (14, 32, 12, 4))
    elif unit == 'spearman':
        # Основа
        image.fill((120, 100, 80))
        # Детализированная броня копейщика
        pygame.draw.rect(image, metal, (14, 18, 12, 18))  # кольчуга
        pygame.draw.rect(image, (140,140,160), (16, 20, 8, 14))  # внутренняя кольчуга
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 8, 12, 12))
        pygame.draw.circle(image, (0,0,0), (18, 14), 1)
        pygame.draw.circle(image, (0,0,0), (22, 14), 1)
        # Шлем
        pygame.draw.ellipse(image, metal, (12, 6, 16, 10))
        pygame.draw.rect(image, accent, (14, 8, 12, 6))
        # Копье
        pygame.draw.line(image, (200,180,160), (20, 20), (20, 44), 3)
        pygame.draw.polygon(image, (160,160,180), [(20,20),(18,16),(22,16)])  # наконечник
        pygame.draw.polygon(image, (120,80,60), [(20,44),(18,48),(22,48)])  # оперение
        # Щит
        pygame.draw.ellipse(image, accent, (2, 22, 10, 16))
        pygame.draw.circle(image, gold, (7, 30), 2)  # украшение щита
    elif unit == 'crossbowman':
        # Основа
        image.fill((100, 120, 140))
        # Детализированная одежда арбалетчика
        pygame.draw.rect(image, cloth, (14, 20, 12, 16))  # туника
        pygame.draw.rect(image, (80,100,140), (16, 22, 8, 12))  # внутренняя туника
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 8, 12, 12))
        pygame.draw.circle(image, (0,0,0), (18, 14), 1)
        pygame.draw.circle(image, (0,0,0), (22, 14), 1)
        # Капюшон
        pygame.draw.ellipse(image, cloth, (12, 4, 16, 10))
        pygame.draw.rect(image, (60,80,120), (14, 6, 12, 6))
        # Арбалет
        pygame.draw.line(image, (120,80,40), (8, 36), (32, 36), 4)  # лук
        pygame.draw.line(image, (200,180,160), (20, 36), (20, 28), 3)  # стрела
        pygame.draw.polygon(image, (160,160,180), [(20,28),(18,24),(22,24)])  # наконечник
        # Колчан
        pygame.draw.rect(image, (180,140,80), (26, 18, 4, 10))
        pygame.draw.rect(image, (160,120,60), (27, 20, 2, 6))
    elif unit == 'swordsman':
        # Основа
        image.fill((100, 100, 120))
        # Детализированная броня мечника
        pygame.draw.rect(image, metal, (12, 16, 16, 18))  # латы
        pygame.draw.rect(image, (160,160,180), (14, 18, 12, 14))  # внутренние латы
        # Детали брони
        pygame.draw.line(image, (120,120,140), (14, 16), (26, 16), 2)
        pygame.draw.line(image, (120,120,140), (14, 20), (26, 20), 2)
        pygame.draw.line(image, (120,120,140), (14, 24), (26, 24), 2)
        pygame.draw.line(image, (120,120,140), (14, 28), (26, 28), 2)
        # Шлем
        pygame.draw.ellipse(image, metal, (12, 6, 16, 14))
        pygame.draw.rect(image, accent, (12, 12, 16, 6))
        # Лицо
        pygame.draw.ellipse(image, skin, (16, 8, 8, 8))
        pygame.draw.circle(image, (0,0,0), (18, 12), 1)
        pygame.draw.circle(image, (0,0,0), (22, 12), 1)
        # Меч
        pygame.draw.rect(image, (180,180,180), (28, 24, 6, 16))
        pygame.draw.rect(image, (120,120,120), (30, 36, 2, 6))
        pygame.draw.polygon(image, (160,160,180), [(28,24),(26,20),(30,20)])  # гарда
        # Щит
        pygame.draw.ellipse(image, accent, (2, 22, 12, 18))
        pygame.draw.circle(image, gold, (8, 31), 2)
    elif unit == 'gryphon':
        # Основа
        image.fill((200,180,120))
        # Детализированное тело грифона
        pygame.draw.ellipse(image, (200,180,120), (8, 20, 24, 16))  # тело
        pygame.draw.ellipse(image, (180,160,100), (10, 22, 20, 12))  # тень тела
        # Голова
        pygame.draw.ellipse(image, (255,224,189), (20, 8, 12, 12))
        pygame.draw.ellipse(image, (240,200,160), (22, 10, 8, 8))  # тень головы
        # Глаза
        pygame.draw.circle(image, (60,40,20), (24, 14), 2)
        pygame.draw.circle(image, (60,40,20), (28, 14), 2)
        pygame.draw.circle(image, (255,255,255), (25, 13), 1)  # блик
        pygame.draw.circle(image, (255,255,255), (29, 13), 1)  # блик
        # Клюв
        pygame.draw.polygon(image, (255,215,0), [(30,14),(36,12),(32,18)])
        pygame.draw.polygon(image, (200,180,0), [(30,14),(34,13),(31,16)])
        # Крылья
        pygame.draw.polygon(image, (180,180,220), [(8,24),(0,8),(16,16)])
        pygame.draw.polygon(image, (180,180,220), [(32,24),(40,8),(24,16)])
        # Перья на крыльях
        for i in range(3):
            pygame.draw.line(image, (160,160,200), (4+i*2, 12), (8+i*2, 20), 2)
            pygame.draw.line(image, (160,160,200), (36-i*2, 12), (32-i*2, 20), 2)
        # Лапы
        pygame.draw.circle(image, (160,140,100), (16, 36), 3)
        pygame.draw.circle(image, (160,140,100), (24, 36), 3)
    # --- Нежить ---
    elif unit == 'skeleton':
        # Основа
        image.fill((80, 60, 100))
        # Детализированный скелет
        pygame.draw.circle(image, (240,240,240), (20, 16), 10)  # череп
        pygame.draw.circle(image, (220,220,220), (20, 16), 8)  # внутренний череп
        # Глазницы
        pygame.draw.circle(image, (40,20,60), (16, 14), 3)
        pygame.draw.circle(image, (40,20,60), (24, 14), 3)
        pygame.draw.circle(image, (80,40,120), (16, 14), 1)  # свечение
        pygame.draw.circle(image, (80,40,120), (24, 14), 1)  # свечение
        # Челюсть
        pygame.draw.arc(image, (200,200,200), (16, 18, 8, 6), 0, 3.14, 2)
        # Позвоночник
        pygame.draw.rect(image, (240,240,240), (18, 26, 4, 12))
        pygame.draw.rect(image, (220,220,220), (19, 27, 2, 10))
        # Ребра
        for i in range(3):
            pygame.draw.line(image, (240,240,240), (14+i*2, 28), (26-i*2, 28), 2)
        # Руки
        pygame.draw.line(image, (240,240,240), (12, 30), (8, 36), 2)
        pygame.draw.line(image, (240,240,240), (28, 30), (32, 36), 2)
        # Ноги
        pygame.draw.line(image, (240,240,240), (18, 38), (16, 44), 2)
        pygame.draw.line(image, (240,240,240), (22, 38), (24, 44), 2)
        # Таз
        pygame.draw.arc(image, (240,240,240), (16, 36, 8, 6), 0, 3.14, 2)
    elif unit == 'zombie':
        # Основа
        image.fill((60, 80, 60))
        # Детализированный зомби
        pygame.draw.rect(image, (120,160,120), (12, 18, 16, 18))  # тело
        pygame.draw.rect(image, (100,140,100), (14, 20, 12, 14))  # внутреннее тело
        # Лицо
        pygame.draw.ellipse(image, (180,220,180), (14, 8, 12, 12))
        pygame.draw.ellipse(image, (160,200,160), (16, 10, 8, 8))  # тень лица
        # Глаза
        pygame.draw.circle(image, (40,80,40), (18, 14), 2)
        pygame.draw.circle(image, (40,80,40), (22, 14), 2)
        pygame.draw.circle(image, (80,120,80), (18, 14), 1)  # свечение
        pygame.draw.circle(image, (80,120,80), (22, 14), 1)  # свечение
        # Рот
        pygame.draw.arc(image, (100,140,100), (18, 18, 4, 3), 0, 3.14, 2)
        # Раны
        pygame.draw.line(image, (100,60,60), (16, 24), (20, 28), 2)
        pygame.draw.line(image, (100,60,60), (24, 26), (28, 30), 2)
        # Руки
        pygame.draw.line(image, (100,140,100), (20, 36), (10, 44), 4)
        pygame.draw.line(image, (100,140,100), (20, 36), (30, 44), 4)
        # Когти
        pygame.draw.polygon(image, (80,120,80), [(10,44),(8,48),(12,48)])
        pygame.draw.polygon(image, (80,120,80), [(30,44),(28,48),(32,48)])
    elif unit == 'ghost':
        # Основа
        image.fill((40, 40, 80))
        # Детализированный призрак
        ghost_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Тело призрака
        pygame.draw.ellipse(ghost_surface, (220,220,255,180), (10, 8, 20, 18))
        pygame.draw.ellipse(ghost_surface, (200,200,235,160), (12, 10, 16, 14))
        # Лицо
        pygame.draw.ellipse(ghost_surface, (240,240,255,200), (14, 10, 12, 8))
        # Глаза
        pygame.draw.circle(ghost_surface, (100,100,200,180), (18, 14), 2)
        pygame.draw.circle(ghost_surface, (100,100,200,180), (22, 14), 2)
        # Рот
        pygame.draw.arc(ghost_surface, (120,120,200,160), (18, 16, 4, 3), 0, 3.14, 2)
        # Плащ
        pygame.draw.arc(ghost_surface, (120,120,180,120), (6, 18, 28, 18), 3.14, 0, 3)
        # Мистические частицы
        for i in range(5):
            pygame.draw.circle(ghost_surface, (200,200,255,100), 
                             (10+i*5, 20+i*2), 1)
        # Применяем к основному изображению
        image.blit(ghost_surface, (0, 0))
    elif unit == 'vampire':
        # Основа
        image.fill((80, 40, 60))
        # Детализированный вампир
        pygame.draw.ellipse(image, (120,40,80), (12, 16, 16, 18))  # тело
        pygame.draw.ellipse(image, (100,20,60), (14, 18, 12, 14))  # внутреннее тело
        # Лицо
        pygame.draw.ellipse(image, (220,220,220), (16, 8, 8, 8))
        pygame.draw.ellipse(image, (200,200,200), (17, 9, 6, 6))  # тень лица
        # Глаза
        pygame.draw.circle(image, (200,0,0), (18, 12), 2)
        pygame.draw.circle(image, (200,0,0), (22, 12), 2)
        pygame.draw.circle(image, (255,100,100), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (255,100,100), (22, 12), 1)  # свечение
        # Плащ
        pygame.draw.polygon(image, (180,0,0), [(20,16),(24,20),(16,20)])
        pygame.draw.polygon(image, (160,0,0), [(20,16),(22,18),(18,18)])
        # Клыки
        pygame.draw.rect(image, (255,255,255), (18, 16, 2, 4))
        pygame.draw.rect(image, (255,255,255), (20, 16, 2, 4))
        # Руки
        pygame.draw.line(image, (100,20,60), (20, 34), (12, 44), 3)
        pygame.draw.line(image, (100,20,60), (20, 34), (28, 44), 3)
        # Когти
        pygame.draw.polygon(image, (80,0,0), [(12,44),(10,48),(14,48)])
        pygame.draw.polygon(image, (80,0,0), [(28,44),(26,48),(30,48)])
    elif unit == 'lich':
        # Основа
        image.fill((60, 40, 80))
        # Детализированный лич
        pygame.draw.ellipse(image, (220,220,220), (10, 8, 20, 18))  # тело
        pygame.draw.ellipse(image, (200,200,200), (12, 10, 16, 14))  # внутреннее тело
        # Лицо
        pygame.draw.ellipse(image, (240,240,240), (14, 10, 12, 8))
        # Глаза
        pygame.draw.circle(image, (80,40,120), (18, 14), 3)
        pygame.draw.circle(image, (80,40,120), (22, 14), 3)
        pygame.draw.circle(image, (120,80,160), (18, 14), 1)  # свечение
        pygame.draw.circle(image, (120,80,160), (22, 14), 1)  # свечение
        # Рот
        pygame.draw.arc(image, (160,160,180), (18, 16, 4, 3), 0, 3.14, 2)
        # Мантия
        pygame.draw.rect(image, (120,80,180), (14, 26, 12, 10))
        pygame.draw.rect(image, (100,60,160), (16, 28, 8, 6))
        # Корона
        pygame.draw.polygon(image, (180,120,255), [(20, 8), (18, 2), (22, 2)])
        pygame.draw.polygon(image, (160,100,235), [(20, 8), (19, 4), (21, 4)])
        # Мистические руны
        pygame.draw.circle(image, (200,160,255), (16, 30), 1)
        pygame.draw.circle(image, (200,160,255), (24, 30), 1)
        pygame.draw.circle(image, (200,160,255), (20, 34), 1)
        # Плащ
        pygame.draw.arc(image, (80,40,120), (6, 18, 28, 18), 3.14, 0, 3)
    # --- Эльфы ---
    elif unit == 'pixie':
        # Основа
        image.fill((80, 180, 80))
        # Детализированная фея
        pygame.draw.ellipse(image, (220,255,220), (12, 8, 16, 16))  # тело
        pygame.draw.ellipse(image, (200,235,200), (14, 10, 12, 12))  # внутреннее тело
        # Лицо
        pygame.draw.circle(image, (255,255,255), (20, 12), 4)  # голова
        pygame.draw.circle(image, (240,240,240), (20, 12), 3)  # внутренняя голова
        # Глаза
        pygame.draw.circle(image, (0,120,0), (18, 12), 1)
        pygame.draw.circle(image, (0,120,0), (22, 12), 1)
        pygame.draw.circle(image, (0,180,0), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (0,180,0), (22, 12), 1)  # свечение
        # Рот
        pygame.draw.arc(image, (0,100,0), (19, 14, 2, 2), 0, 3.14, 1)
        # Крылья
        pygame.draw.ellipse(image, (180,255,180), (8, 16, 24, 12))  # крылья
        pygame.draw.ellipse(image, (160,235,160), (10, 18, 20, 8))  # внутренние крылья
        # Корона
        pygame.draw.polygon(image, (255,255,180), [(20,12),(24,4),(16,4)])
        pygame.draw.polygon(image, (255,255,200), [(20,12),(22,6),(18,6)])
        # Блёстки
        for i in range(3):
            pygame.draw.circle(image, (255,255,180,120), (20+(-1)**i*4, 18), 2)
        # Магические частицы
        for i in range(4):
            angle = i * 1.57  # 90 градусов
            x = 20 + int(8 * math.cos(angle))
            y = 20 + int(8 * math.sin(angle))
            pygame.draw.circle(image, (200,255,200,150), (x, y), 1)
    elif unit == 'elf_scout':
        # Основа
        image.fill((60, 160, 60))
        # Детализированный эльфийский разведчик
        pygame.draw.rect(image, (120,220,120), (14, 18, 12, 18))  # туника
        pygame.draw.rect(image, (100,200,100), (16, 20, 8, 14))  # внутренняя туника
        # Лицо
        pygame.draw.ellipse(image, (220,255,200), (14, 8, 12, 12))
        pygame.draw.ellipse(image, (200,235,180), (16, 10, 8, 8))  # тень лица
        # Глаза
        pygame.draw.circle(image, (0,120,0), (18, 14), 1)
        pygame.draw.circle(image, (0,120,0), (22, 14), 1)
        pygame.draw.circle(image, (0,180,0), (18, 14), 1)  # свечение
        pygame.draw.circle(image, (0,180,0), (22, 14), 1)  # свечение
        # Уши
        pygame.draw.polygon(image, (220,255,200), [(14,12),(10,6),(18,10)])
        pygame.draw.polygon(image, (220,255,200), [(26,12),(30,6),(22,10)])
        # Копье
        pygame.draw.line(image, (60,180,60), (20, 20), (20, 44), 3)
        pygame.draw.polygon(image, (255,255,180), [(18,8),(22,8),(20,2)])
        pygame.draw.polygon(image, (160,160,180), [(20,20),(18,16),(22,16)])  # наконечник
        # Плащ
        pygame.draw.polygon(image, (80,180,120), [(14,36),(26,36),(20,44)])
        pygame.draw.polygon(image, (60,160,100), [(16,36),(24,36),(20,40)])
        # Пояс
        pygame.draw.rect(image, (100,180,80), (14, 30, 12, 4))
    elif unit == 'elf_archer':
        # Основа
        image.fill((80, 180, 80))
        # Детализированный эльфийский лучник
        pygame.draw.rect(image, (120,220,120), (14, 20, 12, 16))  # туника
        pygame.draw.rect(image, (100,200,100), (16, 22, 8, 12))  # внутренняя туника
        # Лицо
        pygame.draw.ellipse(image, (220,255,200), (14, 8, 12, 12))
        pygame.draw.ellipse(image, (200,235,180), (16, 10, 8, 8))  # тень лица
        # Глаза
        pygame.draw.circle(image, (0,120,0), (18, 14), 1)
        pygame.draw.circle(image, (0,120,0), (22, 14), 1)
        pygame.draw.circle(image, (0,180,0), (18, 14), 1)  # свечение
        pygame.draw.circle(image, (0,180,0), (22, 14), 1)  # свечение
        # Уши
        pygame.draw.polygon(image, (220,255,200), [(14,12),(10,6),(18,10)])
        pygame.draw.polygon(image, (220,255,200), [(26,12),(30,6),(22,10)])
        # Лук
        pygame.draw.line(image, (60,180,60), (8, 36), (32, 36), 3)
        pygame.draw.line(image, (255,215,0), (20, 36), (20, 28), 2)
        pygame.draw.polygon(image, (160,160,180), [(20,28),(18,24),(22,24)])  # наконечник
        # Капюшон
        pygame.draw.ellipse(image, (60,120,60), (12, 4, 16, 10))
        pygame.draw.rect(image, (40,100,40), (14, 6, 12, 6))
        # Колчан
        pygame.draw.rect(image, (180,140,80), (26, 18, 4, 10))
        pygame.draw.rect(image, (160,120,60), (27, 20, 2, 6))
        # Стрелы в колчане
        for i in range(3):
            pygame.draw.line(image, (200,180,160), (26, 20+i*2), (30, 20+i*2), 1)
    elif unit == 'dryad':
        # Основа
        image.fill((60, 140, 60))
        # Детализированная дриада
        pygame.draw.ellipse(image, (120,220,120), (10, 8, 20, 18))  # тело
        pygame.draw.ellipse(image, (100,200,100), (12, 10, 16, 14))  # внутреннее тело
        # Лицо
        pygame.draw.ellipse(image, (200,240,180), (14, 10, 12, 8))
        # Глаза
        pygame.draw.circle(image, (0,120,0), (18, 14), 1)
        pygame.draw.circle(image, (0,120,0), (22, 14), 1)
        pygame.draw.circle(image, (0,180,0), (18, 14), 1)  # свечение
        pygame.draw.circle(image, (0,180,0), (22, 14), 1)  # свечение
        # Уши
        pygame.draw.polygon(image, (200,240,180), [(14,12),(10,6),(18,10)])
        pygame.draw.polygon(image, (200,240,180), [(26,12),(30,6),(22,10)])
        # Корона из листьев
        pygame.draw.polygon(image, (255,255,180), [(20,8),(24,2),(16,2)])
        pygame.draw.polygon(image, (200,255,100), [(20,8),(22,4),(18,4)])
        # Ноги (ствол дерева)
        pygame.draw.rect(image, (80,140,60), (16, 26, 8, 12))
        pygame.draw.rect(image, (60,120,40), (17, 27, 6, 10))
        # Корни
        pygame.draw.line(image, (60,120,40), (16, 38), (10, 44), 2)
        pygame.draw.line(image, (60,120,40), (24, 38), (30, 44), 2)
        # Цветы
        for i in range(3):
            pygame.draw.circle(image, (255,200,220), (20+(-1)**i*6, 18), 2)
            pygame.draw.circle(image, (255,180,200), (20+(-1)**i*6, 18), 1)
        # Листья
        for i in range(4):
            angle = i * 1.57
            x = 20 + int(6 * math.cos(angle))
            y = 20 + int(6 * math.sin(angle))
            pygame.draw.circle(image, (100,200,100,150), (x, y), 2)
    elif unit == 'ent':
        # Основа
        image.fill((40, 100, 40))
        # Детализированный энт
        pygame.draw.rect(image, (100,80,40), (14, 20, 12, 18))  # тело
        pygame.draw.rect(image, (80,60,20), (16, 22, 8, 14))  # внутреннее тело
        # Лицо
        pygame.draw.ellipse(image, (120,220,120), (10, 8, 20, 18))
        pygame.draw.ellipse(image, (100,200,100), (12, 10, 16, 14))  # тень лица
        # Глаза
        pygame.draw.ellipse(image, (40,80,40), (16, 16, 4, 2))
        pygame.draw.ellipse(image, (40,80,40), (20, 16, 4, 2))
        pygame.draw.circle(image, (60,120,60), (18, 17), 1)  # свечение
        pygame.draw.circle(image, (60,120,60), (22, 17), 1)  # свечение
        # Рот
        pygame.draw.arc(image, (60,120,60), (18, 20, 4, 3), 0, 3.14, 2)
        # Ветви-руки
        pygame.draw.line(image, (80,140,60), (20, 38), (10, 44), 4)
        pygame.draw.line(image, (80,140,60), (20, 38), (30, 44), 4)
        # Листья на руках
        pygame.draw.circle(image, (100,180,100), (10, 44), 3)
        pygame.draw.circle(image, (100,180,100), (30, 44), 3)
        # Ветви на голове
        pygame.draw.line(image, (100,80,40), (20, 8), (10, 2), 2)
        pygame.draw.line(image, (100,80,40), (20, 8), (30, 2), 2)
        # Листья на голове
        pygame.draw.circle(image, (120,200,120), (10, 2), 2)
        pygame.draw.circle(image, (120,200,120), (30, 2), 2)
        # Корни-ноги
        pygame.draw.line(image, (60,120,40), (16, 38), (12, 44), 3)
        pygame.draw.line(image, (60,120,40), (24, 38), (28, 44), 3)
        # Мох на теле
        pygame.draw.circle(image, (80,160,80), (18, 28), 2)
        pygame.draw.circle(image, (80,160,80), (22, 30), 2)
    # --- Демоны ---
    elif unit == 'imp':
        # Основа
        image.fill((120, 40, 20))
        # Детализированный бес
        pygame.draw.ellipse(image, (255,180,120), (12, 8, 16, 16))  # тело
        pygame.draw.ellipse(image, (235,160,100), (14, 10, 12, 12))  # внутреннее тело
        # Лицо
        pygame.draw.circle(image, (255,220,180), (20, 12), 4)  # голова
        pygame.draw.circle(image, (235,200,160), (20, 12), 3)  # внутренняя голова
        # Глаза
        pygame.draw.circle(image, (200,0,0), (18, 12), 2)
        pygame.draw.circle(image, (200,0,0), (22, 12), 2)
        pygame.draw.circle(image, (255,100,100), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (255,100,100), (22, 12), 1)  # свечение
        # Рога
        pygame.draw.polygon(image, (120,40,20), [(20,8),(24,2),(16,2)])
        pygame.draw.polygon(image, (100,20,0), [(20,8),(22,4),(18,4)])
        # Рот
        pygame.draw.arc(image, (180,0,0), (19, 14, 2, 2), 0, 3.14, 1)
        # Клыки
        pygame.draw.rect(image, (255,255,255), (19, 14, 1, 2))
        pygame.draw.rect(image, (255,255,255), (20, 14, 1, 2))
        # Хвост
        pygame.draw.polygon(image, (255,80,20), [(20,12),(24,20),(16,20)])
        pygame.draw.polygon(image, (235,60,0), [(20,12),(22,16),(18,16)])
        # Крылья
        pygame.draw.polygon(image, (200,80,80), [(12,16),(8,24),(20,20)])
        pygame.draw.polygon(image, (200,80,80), [(28,16),(32,24),(20,20)])
        # Лапы
        pygame.draw.circle(image, (200,120,80), (16, 24), 2)
        pygame.draw.circle(image, (200,120,80), (24, 24), 2)
    elif unit == 'gog':
        # Основа
        image.fill((160, 60, 40))
        # Детализированный гог
        pygame.draw.ellipse(image, (255,180,120), (12, 8, 16, 16))  # тело
        pygame.draw.ellipse(image, (235,160,100), (14, 10, 12, 12))  # внутреннее тело
        # Лицо
        pygame.draw.circle(image, (255,220,180), (20, 12), 4)  # голова
        pygame.draw.circle(image, (235,200,160), (20, 12), 3)  # внутренняя голова
        # Глаза
        pygame.draw.circle(image, (200,0,0), (18, 12), 2)
        pygame.draw.circle(image, (200,0,0), (22, 12), 2)
        pygame.draw.circle(image, (255,100,100), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (255,100,100), (22, 12), 1)  # свечение
        # Рога
        pygame.draw.polygon(image, (255,80,20), [(20,8),(24,2),(16,2)])
        pygame.draw.polygon(image, (235,60,0), [(20,8),(22,4),(18,4)])
        # Рот
        pygame.draw.arc(image, (180,0,0), (19, 14, 2, 2), 0, 3.14, 1)
        # Тело
        pygame.draw.rect(image, (180,60,40), (16, 24, 8, 12))
        pygame.draw.rect(image, (160,40,20), (17, 25, 6, 10))
        # Пламя
        pygame.draw.polygon(image, (255,120,40), [(20,24),(24,32),(16,32)])
        pygame.draw.polygon(image, (255,100,20), [(20,24),(22,28),(18,28)])
        # Лапы
        pygame.draw.circle(image, (200,120,80), (16, 36), 2)
        pygame.draw.circle(image, (200,120,80), (24, 36), 2)
    elif unit == 'demon':
        # Основа
        image.fill((100, 20, 10))
        # Детализированный демон
        pygame.draw.ellipse(image, (255,180,120), (10, 8, 20, 18))  # тело
        pygame.draw.ellipse(image, (235,160,100), (12, 10, 16, 14))  # внутреннее тело
        # Лицо
        pygame.draw.circle(image, (255,220,180), (20, 12), 4)  # голова
        pygame.draw.circle(image, (235,200,160), (20, 12), 3)  # внутренняя голова
        # Глаза
        pygame.draw.circle(image, (200,0,0), (18, 12), 2)
        pygame.draw.circle(image, (200,0,0), (22, 12), 2)
        pygame.draw.circle(image, (255,100,100), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (255,100,100), (22, 12), 1)  # свечение
        # Рога
        pygame.draw.polygon(image, (255,80,20), [(20,8),(24,2),(16,2)])
        pygame.draw.polygon(image, (235,60,0), [(20,8),(22,4),(18,4)])
        # Рот
        pygame.draw.arc(image, (180,0,0), (19, 14, 2, 2), 0, 3.14, 1)
        # Клыки
        pygame.draw.rect(image, (255,255,255), (19, 14, 1, 3))
        pygame.draw.rect(image, (255,255,255), (20, 14, 1, 3))
        # Тело
        pygame.draw.rect(image, (180,60,40), (14, 26, 12, 10))
        pygame.draw.rect(image, (160,40,20), (15, 27, 10, 8))
        # Хвост
        pygame.draw.polygon(image, (255,80,20), [(20,26),(24,36),(16,36)])
        pygame.draw.polygon(image, (235,60,0), [(20,26),(22,31),(18,31)])
        # Крылья
        pygame.draw.polygon(image, (180,60,40), [(10,18),(2,8),(20,20)])
        pygame.draw.polygon(image, (180,60,40), [(30,18),(38,8),(20,20)])
        # Лапы
        pygame.draw.circle(image, (200,120,80), (16, 36), 3)
        pygame.draw.circle(image, (200,120,80), (24, 36), 3)
    elif unit == 'cerberus':
        # Основа
        image.fill((80, 20, 10))
        # Детализированный цербер
        pygame.draw.ellipse(image, (180,60,40), (8, 20, 24, 16))  # тело
        pygame.draw.ellipse(image, (160,40,20), (10, 22, 20, 12))  # тень тела
        # Голова 1
        pygame.draw.ellipse(image, (255,180,120), (10, 8, 10, 10))
        pygame.draw.ellipse(image, (235,160,100), (12, 10, 6, 6))  # тень головы
        # Голова 2
        pygame.draw.ellipse(image, (255,180,120), (20, 8, 10, 10))
        pygame.draw.ellipse(image, (235,160,100), (22, 10, 6, 6))  # тень головы
        # Голова 3
        pygame.draw.ellipse(image, (255,180,120), (16, 4, 8, 8))
        pygame.draw.ellipse(image, (235,160,100), (17, 5, 6, 6))  # тень головы
        # Глаза головы 1
        pygame.draw.circle(image, (255,80,20), (14, 12), 2)
        pygame.draw.circle(image, (255,100,40), (14, 12), 1)  # свечение
        # Глаза головы 2
        pygame.draw.circle(image, (255,80,20), (22, 12), 2)
        pygame.draw.circle(image, (255,100,40), (22, 12), 1)  # свечение
        # Глаза головы 3
        pygame.draw.circle(image, (255,80,20), (18, 8), 2)
        pygame.draw.circle(image, (255,100,40), (18, 8), 1)  # свечение
        # Рты
        pygame.draw.arc(image, (180,0,0), (13, 14, 4, 3), 0, 3.14, 1)
        pygame.draw.arc(image, (180,0,0), (21, 14, 4, 3), 0, 3.14, 1)
        pygame.draw.arc(image, (180,0,0), (17, 10, 2, 2), 0, 3.14, 1)
        # Клыки
        pygame.draw.rect(image, (255,255,255), (14, 16, 1, 2))
        pygame.draw.rect(image, (255,255,255), (22, 16, 1, 2))
        pygame.draw.rect(image, (255,255,255), (18, 12, 1, 2))
        # Хвост
        pygame.draw.polygon(image, (255,80,20), [(20,36),(24,44),(16,44)])
        pygame.draw.polygon(image, (235,60,0), [(20,36),(22,40),(18,40)])
        # Лапы
        pygame.draw.circle(image, (200,120,80), (12, 36), 3)
        pygame.draw.circle(image, (200,120,80), (28, 36), 3)
    elif unit == 'succubus':
        # Основа
        image.fill((140, 40, 60))
        # Детализированная суккуб
        pygame.draw.ellipse(image, (255,180,200), (12, 8, 16, 16))  # тело
        pygame.draw.ellipse(image, (235,160,180), (14, 10, 12, 12))  # внутреннее тело
        # Лицо
        pygame.draw.circle(image, (255,220,220), (20, 12), 4)  # голова
        pygame.draw.circle(image, (235,200,200), (20, 12), 3)  # внутренняя голова
        # Глаза
        pygame.draw.circle(image, (200,0,100), (18, 12), 2)
        pygame.draw.circle(image, (200,0,100), (22, 12), 2)
        pygame.draw.circle(image, (255,100,150), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (255,100,150), (22, 12), 1)  # свечение
        # Рога
        pygame.draw.polygon(image, (180,60,80), [(20,8),(24,2),(16,2)])
        pygame.draw.polygon(image, (160,40,60), [(20,8),(22,4),(18,4)])
        # Рот
        pygame.draw.arc(image, (180,0,100), (19, 14, 2, 2), 0, 3.14, 1)
        # Хвост
        pygame.draw.polygon(image, (255,80,120), [(20,12),(24,20),(16,20)])
        pygame.draw.polygon(image, (235,60,100), [(20,12),(22,16),(18,16)])
        # Крылья
        pygame.draw.polygon(image, (200,80,120), [(12,16),(8,24),(20,20)])
        pygame.draw.polygon(image, (200,80,120), [(28,16),(32,24),(20,20)])
        # Лапы
        pygame.draw.circle(image, (220,140,160), (16, 24), 2)
        pygame.draw.circle(image, (220,140,160), (24, 24), 2)
    # --- Гномы ---
    elif team == 'dwarf':
        if unit == 'hero':
            # Основа - каменный фон
            image.fill((90, 110, 140))
            # Детализированная броня с металлическими пластинами
            pygame.draw.rect(image, (200,200,220), (8, 20, 24, 18))
            pygame.draw.rect(image, (160,160,180), (10, 22, 20, 14))  # внутренняя броня
            pygame.draw.line(image, (120,120,140), (12, 20), (28, 20), 2)  # верхняя пластина
            pygame.draw.line(image, (120,120,140), (12, 24), (28, 24), 2)  # средняя пластина
            pygame.draw.line(image, (120,120,140), (12, 28), (28, 28), 2)  # нижняя пластина
            pygame.draw.line(image, (120,120,140), (12, 32), (28, 32), 2)  # нижняя пластина
            # Лицо с детализацией
            pygame.draw.ellipse(image, (240,220,160), (10, 8, 20, 18))
            pygame.draw.ellipse(image, (200,180,140), (12, 10, 16, 14))  # тень лица
            # Глаза
            pygame.draw.circle(image, (60,40,20), (16, 16), 2)
            pygame.draw.circle(image, (60,40,20), (24, 16), 2)
            pygame.draw.circle(image, (255,255,255), (17, 15), 1)  # блик
            pygame.draw.circle(image, (255,255,255), (25, 15), 1)  # блик
            # Нос
            pygame.draw.circle(image, (180,160,120), (20, 20), 2)
            # Рот
            pygame.draw.arc(image, (160,140,100), (18, 22, 4, 3), 0, 3.14, 2)
            # Детализированный шлем с рогами
            pygame.draw.polygon(image, (180,160,100), [(12,12),(16,4),(20,12),(24,4),(28,12)])
            pygame.draw.polygon(image, (140,120,80), [(14,10),(18,6),(22,10)])  # внутренний шлем
            # Рога
            pygame.draw.polygon(image, (120,100,60), [(14,10),(12,2),(16,6)])
            pygame.draw.polygon(image, (120,100,60), [(26,10),(28,2),(24,6)])
            # Детализированная борода
            pygame.draw.circle(image, (100,80,60), (20, 30), 8)
            pygame.draw.circle(image, (80,60,40), (20, 32), 6)  # тень бороды
            # Украшения на броне
            pygame.draw.circle(image, (255,215,0), (16, 26), 2)  # золотая пуговица
            pygame.draw.circle(image, (255,215,0), (24, 26), 2)  # золотая пуговица
            # Пояс с пряжкой
            pygame.draw.rect(image, (100,80,60), (8, 28, 24, 10))
            pygame.draw.rect(image, (255,215,0), (18, 30, 4, 6))  # золотая пряжка
        elif unit == 'miner':
            # Основа
            image.fill((110,130,160))
            # Детализированная одежда
            pygame.draw.rect(image, (180,160,140), (14, 20, 12, 18))  # рубаха
            pygame.draw.rect(image, (140,120,100), (16, 22, 8, 14))  # внутренняя рубаха
            # Лицо
            pygame.draw.ellipse(image, (240,220,160), (14, 8, 12, 12))
            pygame.draw.circle(image, (60,40,20), (18, 14), 1)  # глаз
            pygame.draw.circle(image, (60,40,20), (22, 14), 1)  # глаз
            # Шахтерская каска
            pygame.draw.ellipse(image, (120,100,80), (12, 6, 16, 10))
            pygame.draw.rect(image, (100,80,60), (14, 8, 12, 6))  # внутренняя каска
            # Фонарь на каске
            pygame.draw.circle(image, (255,200,100), (20, 10), 3)
            pygame.draw.circle(image, (255,255,255), (20, 9), 1)  # свет
            # Кирка
            pygame.draw.line(image, (100,80,60), (20, 38), (8, 44), 4)  # рукоять
            pygame.draw.line(image, (100,80,60), (20, 38), (32, 44), 4)  # рукоять
            pygame.draw.polygon(image, (160,160,180), [(8,44),(4,48),(12,48)])  # наконечник
            pygame.draw.polygon(image, (160,160,180), [(32,44),(28,48),(36,48)])  # наконечник
            # Борода
            pygame.draw.circle(image, (100,80,60), (20, 26), 4)
        elif unit == 'spearthrower':
            # Основа
            image.fill((100,140,180))
            # Детализированная броня
            pygame.draw.rect(image, (180,160,140), (14, 18, 12, 18))
            pygame.draw.rect(image, (140,120,100), (16, 20, 8, 14))
            # Лицо
            pygame.draw.ellipse(image, (240,220,160), (14, 8, 12, 12))
            pygame.draw.circle(image, (60,40,20), (18, 14), 1)
            pygame.draw.circle(image, (60,40,20), (22, 14), 1)
            # Шлем с пером
            pygame.draw.ellipse(image, (120,100,80), (12, 6, 16, 10))
            pygame.draw.polygon(image, (255,100,100), [(18,8),(20,2),(22,8)])  # красное перо
            # Копье
            pygame.draw.line(image, (200,180,160), (20, 20), (20, 44), 3)
            pygame.draw.polygon(image, (160,160,180), [(20,20),(18,16),(22,16)])  # наконечник
            pygame.draw.polygon(image, (100,80,60), [(20,44),(18,48),(22,48)])  # оперение
            # Борода
            pygame.draw.circle(image, (100,80,60), (20, 24), 4)
        elif unit == 'bearrider':
            # Основа
            image.fill((80,100,140))
            # Медведь - тело
            pygame.draw.ellipse(image, (140,100,60), (8, 20, 24, 16))
            pygame.draw.ellipse(image, (120,80,40), (10, 22, 20, 12))  # тень тела
            # Медведь - голова
            pygame.draw.ellipse(image, (160,120,80), (20, 8, 12, 12))
            pygame.draw.ellipse(image, (140,100,60), (22, 10, 8, 8))  # тень головы
            # Уши медведя
            pygame.draw.circle(image, (120,80,40), (22, 10), 3)
            pygame.draw.circle(image, (120,80,40), (30, 10), 3)
            # Глаза медведя
            pygame.draw.circle(image, (60,40,20), (24, 14), 1)
            pygame.draw.circle(image, (60,40,20), (28, 14), 1)
            # Нос медведя
            pygame.draw.circle(image, (80,60,40), (26, 16), 1)
            # Гном-всадник
            pygame.draw.ellipse(image, (240,220,160), (20, 6, 8, 8))  # лицо гнома
            pygame.draw.circle(image, (60,40,20), (22, 8), 1)  # глаз
            pygame.draw.circle(image, (60,40,20), (26, 8), 1)  # глаз
            # Шлем гнома
            pygame.draw.ellipse(image, (120,100,80), (18, 4, 12, 8))
            # Борода гнома
            pygame.draw.circle(image, (100,80,60), (24, 12), 3)
            # Седельные сумки
            pygame.draw.rect(image, (100,80,60), (14, 28, 12, 10))
            pygame.draw.rect(image, (80,60,40), (16, 30, 8, 6))
        elif unit == 'runemage':
            # Основа
            image.fill((60,120,200))
            # Магическая мантия
            pygame.draw.rect(image, (180,160,200), (14, 20, 12, 18))
            pygame.draw.rect(image, (140,120,180), (16, 22, 8, 14))
            # Лицо
            pygame.draw.ellipse(image, (240,220,160), (14, 8, 12, 12))
            pygame.draw.circle(image, (60,40,20), (18, 14), 1)
            pygame.draw.circle(image, (60,40,20), (22, 14), 1)
            # Магический колпак
            pygame.draw.polygon(image, (100,80,160), [(14,8),(20,2),(26,8)])
            pygame.draw.polygon(image, (80,60,140), [(16,8),(20,4),(24,8)])
            # Рунический посох
            pygame.draw.line(image, (160,140,120), (20, 32), (20, 44), 3)
            pygame.draw.circle(image, (200,180,255), (20, 32), 6)  # рунический кристалл
            pygame.draw.circle(image, (255,255,255), (20, 30), 2)  # свет кристалла
            # Руны на мантии
            pygame.draw.circle(image, (255,255,255), (16, 26), 1)
            pygame.draw.circle(image, (255,255,255), (24, 26), 1)
            pygame.draw.circle(image, (255,255,255), (20, 30), 1)
            # Борода
            pygame.draw.circle(image, (100,80,60), (20, 24), 4)
        elif unit == 'jarl':
            # Основа
            image.fill((80,120,180))
            # Королевская броня
            pygame.draw.rect(image, (200,180,160), (12, 16, 16, 18))
            pygame.draw.rect(image, (160,140,120), (14, 18, 12, 14))
            # Детали брони
            pygame.draw.line(image, (120,100,80), (14, 16), (26, 16), 2)
            pygame.draw.line(image, (120,100,80), (14, 20), (26, 20), 2)
            pygame.draw.line(image, (120,100,80), (14, 24), (26, 24), 2)
            pygame.draw.line(image, (120,100,80), (14, 28), (26, 28), 2)
            # Лицо
            pygame.draw.ellipse(image, (240,220,160), (12, 6, 16, 14))
            pygame.draw.ellipse(image, (200,180,140), (14, 8, 12, 10))
            # Глаза
            pygame.draw.circle(image, (60,40,20), (16, 12), 2)
            pygame.draw.circle(image, (60,40,20), (24, 12), 2)
            pygame.draw.circle(image, (255,255,255), (17, 11), 1)
            pygame.draw.circle(image, (255,255,255), (25, 11), 1)
            # Королевский шлем
            pygame.draw.polygon(image, (180,160,100), [(12,12),(16,4),(20,12),(24,4),(28,12)])
            pygame.draw.polygon(image, (140,120,80), [(14,10),(18,6),(22,10)])
            # Корона
            pygame.draw.polygon(image, (255,215,0), [(16,6),(18,2),(20,6),(22,2),(24,6)])
            # Детализированная борода
            pygame.draw.circle(image, (100,80,60), (20, 30), 8)
            pygame.draw.circle(image, (80,60,40), (20, 32), 6)
            # Королевские украшения
            pygame.draw.circle(image, (255,215,0), (16, 24), 2)
            pygame.draw.circle(image, (255,215,0), (24, 24), 2)
            pygame.draw.circle(image, (255,215,0), (20, 28), 2)
    # --- Лига теней ---
    elif team == 'shadow':
        if unit == 'hero':
            # Основа - глубокие тени
            image.fill((20,0,40))
            # Мистический плащ с тенями
            pygame.draw.rect(image, (60,0,100), (8, 20, 24, 18))
            pygame.draw.rect(image, (40,0,80), (10, 22, 20, 14))  # внутренний плащ
            # Теневые складки
            pygame.draw.line(image, (30,0,60), (12, 20), (28, 20), 2)
            pygame.draw.line(image, (30,0,60), (12, 24), (28, 24), 2)
            pygame.draw.line(image, (30,0,60), (12, 28), (28, 28), 2)
            pygame.draw.line(image, (30,0,60), (12, 32), (28, 32), 2)
            # Лицо с мистическим свечением
            pygame.draw.ellipse(image, (180,160,200), (10, 8, 20, 18))
            pygame.draw.ellipse(image, (140,120,180), (12, 10, 16, 14))  # тень лица
            # Мистические глаза
            pygame.draw.circle(image, (200,0,200), (16, 16), 3)
            pygame.draw.circle(image, (200,0,200), (24, 16), 3)
            pygame.draw.circle(image, (255,255,255), (17, 15), 1)  # блик
            pygame.draw.circle(image, (255,255,255), (25, 15), 1)  # блик
            # Теневая маска/корона
            pygame.draw.polygon(image, (100,0,150), [(12,12),(16,4),(20,12),(24,4),(28,12)])
            pygame.draw.polygon(image, (80,0,120), [(14,10),(18,6),(22,10)])
            # Мистические рога
            pygame.draw.polygon(image, (60,0,100), [(14,10),(12,2),(16,6)])
            pygame.draw.polygon(image, (60,0,100), [(26,10),(28,2),(24,6)])
            # Теневая аура
            pygame.draw.circle(image, (40,0,80), (20, 30), 8)
            pygame.draw.circle(image, (20,0,60), (20, 32), 6)
            # Мистические украшения
            pygame.draw.circle(image, (200,0,200), (16, 26), 2)
            pygame.draw.circle(image, (200,0,200), (24, 26), 2)
            # Теневой пояс
            pygame.draw.rect(image, (40,0,80), (8, 28, 24, 10))
            pygame.draw.rect(image, (100,0,150), (18, 30, 4, 6))  # мистическая пряжка
        elif unit == 'scout':
            # Основа
            image.fill((40,0,60))
            # Теневой камуфляж
            pygame.draw.rect(image, (80,0,120), (14, 20, 12, 18))
            pygame.draw.rect(image, (60,0,100), (16, 22, 8, 14))
            # Лицо
            pygame.draw.ellipse(image, (180,160,200), (14, 8, 12, 12))
            pygame.draw.circle(image, (200,0,200), (18, 14), 1)  # мистический глаз
            pygame.draw.circle(image, (200,0,200), (22, 14), 1)  # мистический глаз
            # Теневой капюшон
            pygame.draw.ellipse(image, (60,0,100), (12, 6, 16, 10))
            pygame.draw.rect(image, (40,0,80), (14, 8, 12, 6))
            # Теневые перья
            pygame.draw.polygon(image, (100,0,150), [(18,8),(20,2),(22,8)])
            # Теневой кинжал
            pygame.draw.line(image, (120,0,180), (20, 20), (20, 44), 2)
            pygame.draw.polygon(image, (160,0,200), [(20,20),(18,16),(22,16)])  # лезвие
            pygame.draw.polygon(image, (80,0,120), [(20,44),(18,48),(22,48)])  # рукоять
            # Теневые следы
            pygame.draw.circle(image, (40,0,80), (20, 24), 3)
        elif unit == 'beast':
            # Основа
            image.fill((20,0,40))
            # Теневой зверь - тело
            pygame.draw.ellipse(image, (60,0,100), (8, 20, 24, 16))
            pygame.draw.ellipse(image, (40,0,80), (10, 22, 20, 12))  # тень тела
            # Теневой зверь - голова
            pygame.draw.ellipse(image, (80,0,120), (20, 8, 12, 12))
            pygame.draw.ellipse(image, (60,0,100), (22, 10, 8, 8))  # тень головы
            # Уши теневого зверя
            pygame.draw.circle(image, (40,0,80), (22, 10), 3)
            pygame.draw.circle(image, (40,0,80), (30, 10), 3)
            # Мистические глаза
            pygame.draw.circle(image, (200,0,200), (24, 14), 2)
            pygame.draw.circle(image, (200,0,200), (28, 14), 2)
            pygame.draw.circle(image, (255,255,255), (25, 13), 1)  # блик
            pygame.draw.circle(image, (255,255,255), (29, 13), 1)  # блик
            # Теневой нос
            pygame.draw.circle(image, (100,0,150), (26, 16), 1)
            # Теневые клыки
            pygame.draw.polygon(image, (160,0,200), [(24,18),(22,22),(26,22)])
            pygame.draw.polygon(image, (160,0,200), [(28,18),(26,22),(30,22)])
            # Теневые когти
            pygame.draw.polygon(image, (120,0,180), [(10,36),(8,40),(12,40)])
            pygame.draw.polygon(image, (120,0,180), [(28,36),(26,40),(30,40)])
        elif unit == 'minotaur':
            # Основа
            image.fill((40,0,80))
            # Теневой минотавр - тело
            pygame.draw.rect(image, (80,0,120), (12, 16, 16, 18))
            pygame.draw.rect(image, (60,0,100), (14, 18, 12, 14))
            # Детали теневой брони
            pygame.draw.line(image, (40,0,80), (14, 16), (26, 16), 2)
            pygame.draw.line(image, (40,0,80), (14, 20), (26, 20), 2)
            pygame.draw.line(image, (40,0,80), (14, 24), (26, 24), 2)
            pygame.draw.line(image, (40,0,80), (14, 28), (26, 28), 2)
            # Лицо минотавра
            pygame.draw.ellipse(image, (180,160,200), (12, 6, 16, 14))
            pygame.draw.ellipse(image, (140,120,180), (14, 8, 12, 10))
            # Мистические глаза
            pygame.draw.circle(image, (200,0,200), (16, 12), 2)
            pygame.draw.circle(image, (200,0,200), (24, 12), 2)
            pygame.draw.circle(image, (255,255,255), (17, 11), 1)
            pygame.draw.circle(image, (255,255,255), (25, 11), 1)
            # Теневые рога
            pygame.draw.polygon(image, (100,0,150), [(12,12),(16,4),(20,12),(24,4),(28,12)])
            pygame.draw.polygon(image, (80,0,120), [(14,10),(18,6),(22,10)])
            # Теневые рога минотавра
            pygame.draw.polygon(image, (60,0,100), [(14,10),(12,2),(16,6)])
            pygame.draw.polygon(image, (60,0,100), [(26,10),(28,2),(24,6)])
            # Теневая борода
            pygame.draw.circle(image, (60,0,100), (20, 30), 8)
            pygame.draw.circle(image, (40,0,80), (20, 32), 6)
            # Мистические украшения
            pygame.draw.circle(image, (200,0,200), (16, 24), 2)
            pygame.draw.circle(image, (200,0,200), (24, 24), 2)
        elif unit == 'witch':
            # Основа
            image.fill((60,0,80))
            # Теневая мантия ведьмы
            pygame.draw.rect(image, (100,0,150), (14, 20, 12, 18))
            pygame.draw.rect(image, (80,0,120), (16, 22, 8, 14))
            # Лицо ведьмы
            pygame.draw.ellipse(image, (180,160,200), (14, 8, 12, 12))
            pygame.draw.circle(image, (200,0,200), (18, 14), 1)  # мистический глаз
            pygame.draw.circle(image, (200,0,200), (22, 14), 1)  # мистический глаз
            # Теневой колпак ведьмы
            pygame.draw.polygon(image, (80,0,120), [(14,8),(20,2),(26,8)])
            pygame.draw.polygon(image, (60,0,100), [(16,8),(20,4),(24,8)])
            # Мистический посох
            pygame.draw.line(image, (120,0,180), (20, 32), (20, 44), 3)
            pygame.draw.circle(image, (200,0,200), (20, 32), 6)  # мистический кристалл
            pygame.draw.circle(image, (255,255,255), (20, 30), 2)  # свет кристалла
            # Теневые руны на мантии
            pygame.draw.circle(image, (200,0,200), (16, 26), 1)
            pygame.draw.circle(image, (200,0,200), (24, 26), 1)
            pygame.draw.circle(image, (200,0,200), (20, 30), 1)
            # Теневые волосы
            pygame.draw.circle(image, (60,0,100), (20, 24), 4)
        elif unit == 'lizardrider':
            # Основа
            image.fill((40,0,60))
            # Теневой ящер - тело
            pygame.draw.ellipse(image, (60,0,100), (8, 20, 24, 16))
            pygame.draw.ellipse(image, (40,0,80), (10, 22, 20, 12))  # тень тела
            # Теневой ящер - голова
            pygame.draw.ellipse(image, (80,0,120), (20, 8, 12, 12))
            pygame.draw.ellipse(image, (60,0,100), (22, 10, 8, 8))  # тень головы
            # Глаза ящера
            pygame.draw.circle(image, (200,0,200), (24, 14), 2)
            pygame.draw.circle(image, (200,0,200), (28, 14), 2)
            pygame.draw.circle(image, (255,255,255), (25, 13), 1)  # блик
            pygame.draw.circle(image, (255,255,255), (29, 13), 1)  # блик
            # Теневой всадник
            pygame.draw.ellipse(image, (180,160,200), (20, 6, 8, 8))  # лицо всадника
            pygame.draw.circle(image, (200,0,200), (22, 8), 1)  # мистический глаз
            pygame.draw.circle(image, (200,0,200), (26, 8), 1)  # мистический глаз
            # Теневой шлем всадника
            pygame.draw.ellipse(image, (60,0,100), (18, 4, 12, 8))
            # Теневые волосы всадника
            pygame.draw.circle(image, (60,0,100), (24, 12), 3)
            # Теневые седельные сумки
            pygame.draw.rect(image, (60,0,100), (14, 28, 12, 10))
            pygame.draw.rect(image, (40,0,80), (16, 30, 8, 6))
            # Теневые чешуи ящера
            for i in range(3):
                pygame.draw.circle(image, (80,0,120), (16 + i*4, 26), 1)
                pygame.draw.circle(image, (80,0,120), (16 + i*4, 30), 1)
    return pygame.transform.scale(image, (int(CELL_SIZE * scale), int(CELL_SIZE * scale)))

def draw_cell_texture(surface, x, y, size):
    # Градиентный фон с небольшим шумом по клеткам
    for i in range(size):
        rel_x = (x + i) / SCREEN_WIDTH
        color1 = (44, 140, 60)
        color2 = (52, 155, 70)
        r = int(color1[0] * (1-rel_x) + color2[0] * rel_x)
        g = int(color1[1] * (1-rel_x) + color2[1] * rel_x)
        b = int(color1[2] * (1-rel_x) + color2[2] * rel_x)
        # Добавляем небольшой шум для каждой клетки
        noise = random.randint(-8, 8)
        r = max(0, min(255, r + noise))
        g = max(0, min(255, g + noise))
        b = max(0, min(255, b + noise))
        pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + size - 1))
    # Мягкие полутона
    if random.random() < 0.1:
        gx = x + random.randint(0, size-10)
        gy = y + random.randint(0, size-10)
        gr = random.randint(10, 18)
        color = (60, 170, 80)
        alpha = random.randint(30, 50)
        ellipse = pygame.Surface((gr, gr//2), pygame.SRCALPHA)
        ellipse.fill((0,0,0,0))
        pygame.draw.ellipse(ellipse, color + (alpha,), (0, 0, gr, gr//2))
        surface.blit(ellipse, (gx, gy))

def draw_animated_grass(surface, t):
    # 8 травинок на клетку, чуть разный цвет
    random.seed(42)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            cell_x = x * CELL_SIZE
            cell_y = y * CELL_SIZE
            for i in range(8):
                base_x = cell_x + random.randint(4, CELL_SIZE-4)
                base_y = cell_y + random.randint(CELL_SIZE//2, CELL_SIZE-4)
                length = random.randint(10, 18)
                # Цвет травинки чуть отличается
                base_color = (60, 170, 80)
                color = tuple(max(0, min(255, c + random.randint(-10, 10))) for c in base_color)
                phase = (x + y + i) * 0.2
                sway = math.sin(t * 2.0 + phase) * 5
                tip_x = base_x + sway
                tip_y = base_y - length
                pygame.draw.aaline(surface, color, (base_x, base_y), (tip_x, tip_y))
    random.seed()

def _draw_rotated_arrow(screen, x, y, angle, style='normal'):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    # Геометрия стрелы
    shaft_len = 16
    head_len = 8
    half_thick = 2
    # Точка основания древка
    bx = x - shaft_len * cos_a
    by = y - shaft_len * sin_a
    # Оси
    px = -sin_a
    py = cos_a
    # Цвета
    shaft_color = (160, 120, 60) if style == 'normal' else (200, 120, 40)
    head_outer = (200,200,200) if style == 'normal' else (255, 180, 60)
    fletch_color = (80,80,200) if style == 'normal' else (255, 120, 40)
    # Древко (как толстая линия двумя параллелями)
    pygame.draw.line(screen, shaft_color,
                     (bx + half_thick*px, by + half_thick*py),
                     (x + half_thick*px,  y + half_thick*py), 2)
    pygame.draw.line(screen, shaft_color,
                     (bx - half_thick*px, by - half_thick*py),
                     (x - half_thick*px,  y - half_thick*py), 2)
    # Наконечник (треугольник)
    tip = (x, y)
    left = (x - head_len*cos_a + 4*px, y - head_len*sin_a + 4*py)
    right = (x - head_len*cos_a - 4*px, y - head_len*sin_a - 4*py)
    pygame.draw.polygon(screen, head_outer, [tip, left, right])
    # Оперение
    tail = (bx, by)
    f1 = (bx - 6*cos_a + 3*px, by - 6*sin_a + 3*py)
    f2 = (bx - 6*cos_a - 3*px, by - 6*sin_a - 3*py)
    pygame.draw.polygon(screen, fletch_color, [tail, f1, f2])
    # Пламя для огненной стрелы
    if style == 'fire':
        flame1 = (x + 4*cos_a, y + 4*sin_a)
        flame2 = (x + 10*cos_a + 2*px, y + 10*sin_a + 2*py)
        flame3 = (x + 10*cos_a - 2*px, y + 10*sin_a - 2*py)
        pygame.draw.polygon(screen, (255, 80, 20), [flame1, flame2, flame3])
        inner2 = (x + 8*cos_a + 1*px, y + 8*sin_a + 1*py)
        inner3 = (x + 8*cos_a - 1*px, y + 8*sin_a - 1*py)
        pygame.draw.polygon(screen, (255, 200, 80), [flame1, inner2, inner3])

def animate_arrow(screen, start, end, redraw_callback=None, style='normal'):
    frames = 12
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        _draw_rotated_arrow(screen, x, y, angle, style=style)
        pygame.display.flip()
        pygame.time.delay(30)

def animate_arrow_fly(screen, start, end, redraw_callback=None):
    return animate_arrow(screen, start, end, redraw_callback=redraw_callback, style='normal')

def animate_fire_arrow_fly(screen, start, end, redraw_callback=None):
    return animate_arrow(screen, start, end, redraw_callback=redraw_callback, style='fire')

def animate_magic_projectile(screen, start, end, color=(120,40,180)):
    frames = 12
    for i in range(frames):
        pygame.event.pump()
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        # Перерисовываем поле перед каждым кадром
        # Рисуем только магический шар (без следа)
        pygame.draw.circle(screen, color, (x, y), 12)
        pygame.draw.circle(screen, (200,200,255), (x, y), 6)
        pygame.display.flip()
        pygame.time.delay(30)

def animate_magic_fly(screen, start, end, color=(120,40,180), redraw_callback=None):
    frames = 10
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        pygame.draw.circle(screen, color, (x, y), 12)
        pygame.draw.circle(screen, (220,220,255), (x, y), 6)
        pygame.display.flip()
        pygame.time.delay(20)

def animate_stone_skin(screen, target_px, redraw_callback=None):
    # Анимация каменной корки: наложение серых колец и трещин, затем осыпание
    frames = 16
    cx, cy = target_px
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        r = int(CELL_SIZE * (0.6 + 0.4 * i / frames))
        alpha = 180 if i < frames - 4 else max(0, 180 - (i - (frames - 4)) * 45)
        pygame.draw.circle(overlay, (120, 120, 120, alpha), (cx, cy), r, 0)
        # Трещины
        for k in range(6):
            ang = (k * math.pi / 3.0) + (i * 0.1)
            x2 = cx + int(r * math.cos(ang))
            y2 = cy + int(r * math.sin(ang))
            pygame.draw.aaline(overlay, (80, 80, 80, alpha), (cx, cy), (x2, y2))
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(24)

def animate_curse_voodoo(screen, target_px, redraw_callback=None):
    # Проклятие: юнита посыпают вороньими перьями
    frames = 16
    cx, cy = target_px
    # Массив перьев, которые падают на юнит
    feathers = []
    for _ in range(20):  # 20 перьев
        # Позиция начала падения (над юнитом)
        start_x = cx + (random.random() - 0.5) * 60
        start_y = cy - CELL_SIZE - random.random() * 40
        # Скорость падения
        vel_x = (random.random() - 0.5) * 2
        vel_y = random.random() * 1.5 + 0.8
        # Размер и угол поворота
        size = random.random() * 4 + 3
        angle = random.random() * 2 * math.pi
        feathers.append({
            'x': start_x,
            'y': start_y,
            'vel_x': vel_x,
            'vel_y': vel_y,
            'size': size,
            'angle': angle,
            'alpha': 200
        })
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1)
        
        # Обновляем позиции перьев
        for feather in feathers:
            feather['x'] += feather['vel_x']
            feather['y'] += feather['vel_y']
            feather['angle'] += 0.2  # Вращение
            # Замедление по мере падения
            if feather['y'] > cy - CELL_SIZE//2:
                feather['vel_y'] *= 0.95
                feather['alpha'] = max(80, feather['alpha'] - 10)
            else:
                feather['alpha'] = min(220, feather['alpha'] + 5)
        
        # Рисуем перья
        for feather in feathers:
            if feather['y'] < cy + CELL_SIZE//2 and feather['alpha'] > 0:
                # Воронье перо (тёмное, с контуром)
                px, py = int(feather['x']), int(feather['y'])
                alpha = int(feather['alpha'])
                size = feather['size']
                angle = feather['angle']
                
                # Основное тело пера (овальное)
                cos_a = math.cos(angle)
                sin_a = math.sin(angle)
                # Центральная часть
                for offset in range(-int(size), int(size) + 1):
                    ox = offset * cos_a
                    oy = offset * sin_a * 0.3
                    pygame.draw.circle(overlay, (20, 20, 20, alpha), 
                                     (px + int(ox), py + int(oy)), max(1, int(size * 0.5)))
                
                # Ость пера (центральная линия)
                pygame.draw.line(overlay, (40, 40, 40, alpha),
                               (px - int(size * cos_a), py - int(size * sin_a)),
                               (px + int(size * cos_a), py + int(size * sin_a)), 2)
                
                # Барбики (ветвистые части)
                for side in [-1, 1]:
                    for barb in range(3):
                        barb_offset = (barb + 0.5) * size / 2
                        barb_x = px + int(barb_offset * cos_a * side)
                        barb_y = py + int(barb_offset * sin_a * side)
                        barb_length = size * 0.4
                        barb_angle = angle + side * math.pi / 3
                        pygame.draw.line(overlay, (30, 30, 30, alpha),
                                       (barb_x, barb_y),
                                       (barb_x + int(barb_length * math.cos(barb_angle)),
                                        barb_y + int(barb_length * math.sin(barb_angle))), 1)
        
        # Дополнительные перья, которые появляются сверху
        if i < 10 and i % 2 == 0:
            new_x = cx + (random.random() - 0.5) * 40
            new_y = cy - CELL_SIZE - 20 - random.random() * 30
            # Рисуем одно новое перо
            alpha = 180
            size = random.random() * 3 + 2
            angle = random.random() * 2 * math.pi
            px, py = int(new_x), int(new_y)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            for offset in range(-int(size), int(size) + 1):
                ox = offset * cos_a
                oy = offset * sin_a * 0.3
                pygame.draw.circle(overlay, (20, 20, 20, alpha),
                                 (px + int(ox), py + int(oy)), max(1, int(size * 0.5)))
            pygame.draw.line(overlay, (40, 40, 40, alpha),
                           (px - int(size * cos_a), py - int(size * sin_a)),
                           (px + int(size * cos_a), py + int(size * sin_a)), 2)
        
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(20)

def animate_rune_shield_spell(screen, target_px, redraw_callback=None):
    # Руна щита: камень с зелёным руническим знаком (щит) и белыми частицами
    frames = 14
    cx, cy = target_px
    base_y = cy - CELL_SIZE//2 - 15
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Мерцание
        flicker = 0.7 + 0.3 * math.sin(i * 0.9)
        alpha = int(220 * flicker)
        
        # Камень (эллипс) - как в книге
        stone_w, stone_h = 32, 24
        stone_rect = pygame.Rect(cx - stone_w//2, base_y - stone_h//2, stone_w, stone_h)
        pygame.draw.ellipse(overlay, (80, 200, 80, alpha), stone_rect)
        pygame.draw.ellipse(overlay, (40, 100, 40, alpha), stone_rect.inflate(-8, -8), 2)
        
        # Рунический знак (щит) - зелёный полигон, как в книге
        shield_points = [
            (cx - 10, base_y - 8),
            (cx + 10, base_y - 8),
            (cx + 12, base_y + 6),
            (cx, base_y + 14),
            (cx - 12, base_y + 6)
        ]
        pygame.draw.polygon(overlay, (60, 255, 120, alpha), shield_points)
        pygame.draw.polygon(overlay, (40, 200, 100, alpha), shield_points, 2)
        
        # Белые частицы вокруг - как в книге
        for k in range(7):
            angle = math.radians(k * (360 / 7))
            radius = 18 + 3 * math.sin(i * 0.6 + k)
            px = cx + int(radius * math.cos(angle))
            py = base_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.8)
            pygame.draw.circle(overlay, (255, 255, 255, particle_alpha), (px, py), 2)
            # Мерцающие точки
            if k % 2 == 0:
                pygame.draw.circle(overlay, (255, 255, 255, particle_alpha), (px, py), 1)
        
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(24)

def animate_rune_haste_spell(screen, target_px, redraw_callback=None):
    # Руна скорости: камень с белым руническим знаком (молния) и жёлтыми частицами
    frames = 14
    cx, cy = target_px
    base_y = cy - CELL_SIZE//2 - 15
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Мерцание
        flicker = 0.7 + 0.3 * math.sin(i * 0.9)
        alpha = int(220 * flicker)
        
        # Камень (эллипс) - серый, как в книге
        stone_w, stone_h = 32, 24
        stone_rect = pygame.Rect(cx - stone_w//2, base_y - stone_h//2, stone_w, stone_h)
        pygame.draw.ellipse(overlay, (200, 200, 200, alpha), stone_rect)
        pygame.draw.ellipse(overlay, (120, 120, 120, alpha), stone_rect.inflate(-8, -8), 2)
        
        # Рунический знак (молния) - белый, как в книге
        lightning_points = [
            (cx - 8, base_y - 6),
            (cx, base_y + 2),
            (cx - 3, base_y + 2),
            (cx + 8, base_y + 14)
        ]
        pygame.draw.lines(overlay, (255, 255, 255, alpha), False, lightning_points, 3)
        # Дополнительная линия для красоты
        pygame.draw.line(overlay, (255, 255, 255, alpha), (cx - 3, base_y + 2), (cx + 5, base_y + 10), 2)
        
        # Жёлтые частицы вокруг - как в книге
        for k in range(7):
            angle = math.radians(k * (360 / 7))
            radius = 18 + 3 * math.sin(i * 0.6 + k)
            px = cx + int(radius * math.cos(angle))
            py = base_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.8)
            pygame.draw.circle(overlay, (255, 255, 120, particle_alpha), (px, py), 2)
            # Мерцающие точки
            if k % 2 == 0:
                pygame.draw.circle(overlay, (255, 255, 150, particle_alpha), (px, py), 1)
        
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(24)

def animate_fireball(screen, start_px, end_px, redraw_callback=None):
    # Горящий камень летит к цели, затем взрыв после приземления
    flight_frames = 18
    # Этап 1: полет горящего камня
    for i in range(flight_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (flight_frames-1)
        # Позиция камня
        ball_x = int(start_px[0] * (1-t) + end_px[0] * t)
        ball_y = int(start_px[1] * (1-t) + end_px[1] * t)
        # Направление полёта
        dx = end_px[0] - start_px[0]
        dy = end_px[1] - start_px[1]
        angle = math.atan2(dy, dx)
        # Размер горящего камня (неравномерный, как настоящий камень)
        base_r = 12
        # Камень с неровной формой
        stone_r = base_r + int(3 * math.sin(t * 3))
        # Тёмное ядро камня
        pygame.draw.circle(overlay, (60, 50, 45, 255), (ball_x, ball_y), stone_r)
        pygame.draw.circle(overlay, (90, 70, 60, 240), (ball_x, ball_y), int(stone_r*0.9))
        # Раскалённые трещины на камне
        for crack in range(4):
            crack_angle = angle + crack * math.pi / 2
            crack_x = ball_x + int(stone_r * 0.6 * math.cos(crack_angle))
            crack_y = ball_y + int(stone_r * 0.6 * math.sin(crack_angle))
            pygame.draw.line(overlay, (255, 180, 60, 220), (ball_x, ball_y), (crack_x, crack_y), 2)
        # Раскалённые края (огненные точки по краю)
        for edge in range(8):
            edge_angle = edge * (2*math.pi / 8.0) + t
            edge_x = ball_x + int(stone_r * 0.85 * math.cos(edge_angle))
            edge_y = ball_y + int(stone_r * 0.85 * math.sin(edge_angle))
            pygame.draw.circle(overlay, (255, 140, 40, 200), (edge_x, edge_y), 3)
            pygame.draw.circle(overlay, (255, 220, 100, 150), (edge_x, edge_y), 2)
        # Длинный огненный хвост
        tail_length = 35
        for j in range(15):
            trail_t = j / 15.0
            trail_x = ball_x - int(tail_length * trail_t * math.cos(angle))
            trail_y = ball_y - int(tail_length * trail_t * math.sin(angle))
            trail_r = max(2, int(base_r * (1 - trail_t * 0.9)))
            tail_alpha = int(220 * (1 - trail_t * 0.7))
            # Градиент хвоста от яркого к тусклому
            if trail_t < 0.3:
                color = (255, 150, 50, tail_alpha)
            elif trail_t < 0.6:
                color = (255, 120, 40, tail_alpha)
            else:
                color = (200, 80, 30, tail_alpha)
            pygame.draw.circle(overlay, color, (trail_x, trail_y), trail_r)
            # Искры по бокам хвоста
            if j % 2 == 0:
                for side in [-1, 1]:
                    spark_x = trail_x + int(5 * math.cos(angle + math.pi/2 + side * 0.3))
                    spark_y = trail_y + int(5 * math.sin(angle + math.pi/2 + side * 0.3))
                    pygame.draw.circle(overlay, (255, 220, 120, int(tail_alpha*0.6)), (spark_x, spark_y), 2)
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(28)
    
    # Этап 2: взрыв после приземления
    explode_frames = 15
    for i in range(explode_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ex_t = i / (explode_frames - 1)
        # Кольца взрыва (расходящиеся волны)
        for k, radius in enumerate([20, 35, 55, 80, 110]):
            alpha = int(max(0, 240 - int(280 * ex_t * (k+1) / 5)))
            pygame.draw.circle(overlay, (255, 150, 50, alpha), (end_px[0], end_px[1]), radius, 4)
        # Яркое ядро взрыва
        core_size = int(15 + 30 * (1 - ex_t))
        pygame.draw.circle(overlay, (255, 220, 100, int(255 * (1 - ex_t * 0.5))), (end_px[0], end_px[1]), core_size)
        # Искры вокруг взрыва
        for k in range(24):
            spark_angle = (k * (2*math.pi / 24.0)) + ex_t * 3
            spark_dist = 20 + int(100 * ex_t)
            spark_x = end_px[0] + int(spark_dist * math.cos(spark_angle))
            spark_y = end_px[1] + int(spark_dist * math.sin(spark_angle))
            spark_alpha = int(200 * (1 - ex_t))
            pygame.draw.circle(overlay, (255, 140, 40, spark_alpha), (spark_x, spark_y), 4)
            # Дополнительные мелкие искры
            if k % 3 == 0:
                small_spark_x = spark_x + int(8 * math.cos(spark_angle + math.pi/4))
                small_spark_y = spark_y + int(8 * math.sin(spark_angle + math.pi/4))
                pygame.draw.circle(overlay, (255, 200, 100, int(spark_alpha*0.7)), (small_spark_x, small_spark_y), 2)
        # Дым
        for k in range(12):
            smoke_angle = (k * (2*math.pi / 12.0))
            smoke_dist = int(50 * ex_t)
            smoke_x = end_px[0] + int(smoke_dist * math.cos(smoke_angle))
            smoke_y = end_px[1] + int(smoke_dist * math.sin(smoke_angle))
            smoke_size = int(8 + 15 * ex_t)
            pygame.draw.circle(overlay, (70, 55, 55, int(150*(1-ex_t*0.8))), (smoke_x, smoke_y), smoke_size)
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(30)

def animate_raise_dead(screen, center_px, redraw_callback=None):
    # Рука вылазит из земли в центре клетки
    frames = 14
    cx, cy = center_px
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames-1)
        # Земляной круг
        pygame.draw.circle(overlay, (90, 60, 30, 180), (cx, cy+10), int(6 + 10*t))
        # Рука (пальцы появляются снизу вверх)
        height = int(4 + 18 * t)
        pygame.draw.rect(overlay, (200, 200, 200, 240), (cx-3, cy+8-height, 6, height))  # ладонь/предплечье
        for dx in [-6, -2, 2, 6]:
            finger_h = max(4, height - 6)
            pygame.draw.rect(overlay, (200,200,200,240), (cx+dx-1, cy+8-finger_h, 2, finger_h))
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(28)

def animate_fire_explosion(screen, x, y):
    # Небольшой взрыв с искрами — компактный эффект для стрелы
    frames = 8
    for i in range(frames):
        pygame.event.pump()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1)
        # Малое огненное кольцо
        r1 = int(6 + 12 * t)
        alpha = max(0, 200 - int(200 * t))
        pygame.draw.circle(overlay, (255, 140, 50, alpha), (x, y), r1, 3)
        # Небольшое ядро
        core_alpha = max(0, 220 - int(260 * t))
        pygame.draw.circle(overlay, (255, 200, 80, core_alpha), (x, y), max(1, 6 - i))
        # Несколько искр
        for k in range(6):
            ang = (k * (2*math.pi / 6.0)) + t * 1.5
            dist = 4 + int(14 * t)
            sx = x + int(dist * math.cos(ang))
            sy = y + int(dist * math.sin(ang))
            pygame.draw.circle(overlay, (255, 120, 40, int(180*(1-t))), (sx, sy), 2)
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(18)

def animate_forget_spell(screen, start, end, redraw_callback=None):
    """Максимально насыщенная анимация заклинания Забвение с темно-фиолетовыми эффектами"""
    frames = 25
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        
        # Создаем максимально детализированный эффект забвения
        forget_surface = pygame.Surface((CELL_SIZE*4, CELL_SIZE*4), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*2, CELL_SIZE*2
        
        # Основной темно-фиолетовый туман забвения с максимальной насыщенностью
        alpha = int(180 * (1 - abs(t - 0.5) * 2))  # максимальная непрозрачность в середине
        pygame.draw.circle(forget_surface, (40, 10, 60, alpha), (center_x, center_y), 35)
        
        # Множественные слои тумана с разной интенсивностью
        for j in range(6):
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            cloud_alpha = int(alpha * 0.8)
            pygame.draw.circle(forget_surface, (60, 20, 80, cloud_alpha), 
                             (center_x + offset_x, center_y + offset_y), 25)
        
        # Третичные облака забвения
        for j in range(8):
            offset_x = random.randint(-25, 25)
            offset_y = random.randint(-25, 25)
            cloud_alpha = int(alpha * 0.6)
            pygame.draw.circle(forget_surface, (80, 40, 100, cloud_alpha), 
                             (center_x + offset_x, center_y + offset_y), 18)
        
        # Четвертичные облака
        for j in range(10):
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            cloud_alpha = int(alpha * 0.4)
            pygame.draw.circle(forget_surface, (100, 60, 120, cloud_alpha), 
                             (center_x + offset_x, center_y + offset_y), 12)
        
        # Интенсивные мистические частицы забвения
        for j in range(12):
            angle = (j * 0.524 + i * 0.4) % (2 * math.pi)  # вращение
            radius = 20 + random.randint(-8, 8)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 1.0)
            pygame.draw.circle(forget_surface, (160, 80, 180, particle_alpha), 
                             (particle_x, particle_y), 6)
        
        # Дополнительные светящиеся частицы
        for j in range(8):
            particle_x = center_x + random.randint(-25, 25)
            particle_y = center_y + random.randint(-25, 25)
            particle_alpha = int(alpha * 0.9)
            pygame.draw.circle(forget_surface, (200, 120, 220, particle_alpha), 
                             (particle_x, particle_y), 4)
        
        # Мелкие блестящие частицы
        for j in range(15):
            particle_x = center_x + random.randint(-30, 30)
            particle_y = center_y + random.randint(-30, 30)
            particle_alpha = int(alpha * 0.7)
            pygame.draw.circle(forget_surface, (240, 180, 255, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Центральный кристалл забвения с максимальной детализацией
        crystal_alpha = min(255, int(alpha * 1.5))
        # Внешний слой кристалла
        pygame.draw.circle(forget_surface, (80, 30, 100, crystal_alpha), 
                         (center_x, center_y), 18)
        # Средний слой
        pygame.draw.circle(forget_surface, (120, 60, 140, crystal_alpha), 
                         (center_x, center_y), 14)
        # Внутренний слой
        pygame.draw.circle(forget_surface, (160, 100, 180, crystal_alpha), 
                         (center_x, center_y), 10)
        # Ядро кристалла
        pygame.draw.circle(forget_surface, (200, 140, 220, crystal_alpha), 
                         (center_x, center_y), 6)
        # Центральное ядро
        pygame.draw.circle(forget_surface, (255, 200, 255, crystal_alpha), 
                         (center_x, center_y), 3)
        
        # Интенсивный эффект пульсации с множественными слоями
        pulse1 = int(12 * math.sin(i * 0.3))
        pulse2 = int(10 * math.sin(i * 0.5 + 1))
        pulse3 = int(8 * math.sin(i * 0.7 + 2))
        pulse4 = int(6 * math.sin(i * 0.9 + 3))
        
        pygame.draw.circle(forget_surface, (60, 20, 80, alpha//4), 
                         (center_x, center_y), 40 + pulse1)
        pygame.draw.circle(forget_surface, (80, 40, 100, alpha//5), 
                         (center_x, center_y), 45 + pulse2)
        pygame.draw.circle(forget_surface, (100, 60, 120, alpha//6), 
                         (center_x, center_y), 50 + pulse3)
        pygame.draw.circle(forget_surface, (120, 80, 140, alpha//7), 
                         (center_x, center_y), 55 + pulse4)
        
        # Интенсивные мистические руны забвения
        for j in range(8):
            angle = j * math.pi / 4 + i * 0.3
            rune_x = center_x + int(25 * math.cos(angle))
            rune_y = center_y + int(25 * math.sin(angle))
            rune_alpha = int(alpha * 0.8)
            pygame.draw.circle(forget_surface, (180, 120, 200, rune_alpha), 
                             (rune_x, rune_y), 3)
        
        # Дополнительные руны
        for j in range(6):
            angle = j * math.pi / 3 + i * 0.2
            rune_x = center_x + int(15 * math.cos(angle))
            rune_y = center_y + int(15 * math.sin(angle))
            rune_alpha = int(alpha * 0.9)
            pygame.draw.circle(forget_surface, (200, 160, 220, rune_alpha), 
                             (rune_x, rune_y), 2)
        
        # Эффект искажения пространства с множественными слоями
        for j in range(5):
            distortion_x = center_x + random.randint(-35, 35)
            distortion_y = center_y + random.randint(-35, 35)
            distortion_alpha = int(alpha * 0.5)
            pygame.draw.circle(forget_surface, (120, 60, 140, distortion_alpha), 
                             (distortion_x, distortion_y), 12)
        
        # Дополнительные искажения
        for j in range(3):
            distortion_x = center_x + random.randint(-40, 40)
            distortion_y = center_y + random.randint(-40, 40)
            distortion_alpha = int(alpha * 0.3)
            pygame.draw.circle(forget_surface, (140, 80, 160, distortion_alpha), 
                             (distortion_x, distortion_y), 8)
        
        # Эффект вихря забвения
        for j in range(20):
            angle = j * 0.314 + i * 0.6  # вращение
            radius = 15 + j * 0.5
            vortex_x = center_x + int(radius * math.cos(angle))
            vortex_y = center_y + int(radius * math.sin(angle))
            vortex_alpha = int(alpha * 0.4)
            pygame.draw.circle(forget_surface, (100, 50, 120, vortex_alpha), 
                             (vortex_x, vortex_y), 1)
        
        # Применяем эффект забвения к экрану
        screen.blit(forget_surface, (x - CELL_SIZE*2, y - CELL_SIZE*2))
        
        pygame.display.flip()
        pygame.time.delay(35)

def animate_frost_ring(screen, center, radius_cells=1, redraw_callback=None):
    """Кольцо холода: трещины на земле, прозрачный розовый радиус"""
    cx, cy = center
    ring_px = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
    ring_center = (CELL_SIZE*1.5, CELL_SIZE*1.5)
    frames = 16
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        ring_px.fill((0,0,0,0))
        # Трещины льда на земле
        crack_alpha = 120
        for k in range(6):
            ang = k * (2*math.pi/6) + i*0.1
            for seg in range(3):
                r1 = CELL_SIZE//4 + seg*CELL_SIZE//6
                r2 = r1 + CELL_SIZE//8
                x1 = int(ring_center[0] + r1 * math.cos(ang))
                y1 = int(ring_center[1] + r1 * math.sin(ang))
                x2 = int(ring_center[0] + r2 * math.cos(ang+0.1))
                y2 = int(ring_center[1] + r2 * math.sin(ang+0.1))
                pygame.draw.line(ring_px, (200, 220, 255, crack_alpha), (x1, y1), (x2, y2), 1)
        # Прозрачное розовое кольцо радиуса 1 клетки
        pygame.draw.circle(ring_px, (255, 120, 200, 90), ring_center, CELL_SIZE, 4)
        # Применяем поверх
        screen.blit(ring_px, (cx - CELL_SIZE*1.5, cy - CELL_SIZE*1.5))
        pygame.display.flip()
        pygame.time.delay(24)

def animate_frost_impact(screen, center, redraw_callback=None):
    """Анимация морозного удара: ледяные шипы растут из земли и разбиваются"""
    cx, cy = center
    frames = 24
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        t = i / (frames-1)
        splash = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        ox, oy = CELL_SIZE*1.5, CELL_SIZE*1.5
        # Фаза роста шипов (первые 60%)
        if i < int(frames * 0.6):
            grow = i / (frames * 0.6)
            for a in [k * (math.pi/4) for k in range(8)]:
                length = int(20 + 22 * grow)
                ex = int(ox + (CELL_SIZE-6) * math.cos(a))
                ey = int(oy + (CELL_SIZE-6) * math.sin(a))
                bx = int(ex - length * math.cos(a))
                by = int(ey - length * math.sin(a))
                left = (int(bx + 6 * math.cos(a + math.pi/2)), int(by + 6 * math.sin(a + math.pi/2)))
                right = (int(bx + 6 * math.cos(a - math.pi/2)), int(by + 6 * math.sin(a - math.pi/2)))
                tip = (ex, ey)
                color_body = (170, 220, 255, 230)
                color_edge = (210, 245, 255, 240)
                pygame.draw.polygon(splash, color_body, [left, right, tip])
                pygame.draw.polygon(splash, color_edge, [left, right, tip], 2)
        else:
            # Фаза разбивания (осколки разлетаются)
            break_t = (i - frames * 0.6) / (frames * 0.4)
            alpha = int(220 * (1 - break_t))
            for a in [k * (math.pi/4) for k in range(8)]:
                ex = int(ox + (CELL_SIZE-6) * math.cos(a))
                ey = int(oy + (CELL_SIZE-6) * math.sin(a))
                # 3 осколка от каждого шипа
                for k in range(3):
                    da = a + (k-1) * 0.25
                    r = int(6 + 10 * break_t)
                    px = int(ex + r * math.cos(da))
                    py = int(ey + r * math.sin(da))
                    pygame.draw.circle(splash, (200, 240, 255, alpha), (px, py), max(1, 3 - int(2*break_t)))
        screen.blit(splash, (cx - CELL_SIZE*1.5, cy - CELL_SIZE*1.5))
        pygame.display.flip()
        pygame.time.delay(20)

def animate_forget_spell_fly(screen, start, end, redraw_callback=None):
    """Детализированная анимация полета заклинания Забвение"""
    frames = 15
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        
        # Создаем летящий кристалл забвения с детализацией
        crystal_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        center_x, center_y = 15, 15
        
        # Внешний ореол
        pygame.draw.circle(crystal_surface, (80, 40, 100, 120), (center_x, center_y), 14)
        
        # Основной кристалл
        pygame.draw.circle(crystal_surface, (120, 60, 140), (center_x, center_y), 10)
        pygame.draw.circle(crystal_surface, (160, 100, 180), (center_x, center_y), 7)
        pygame.draw.circle(crystal_surface, (200, 140, 220), (center_x, center_y), 4)
        pygame.draw.circle(crystal_surface, (255, 200, 255), (center_x, center_y), 2)
        
        # Светящийся ореол
        pygame.draw.circle(crystal_surface, (140, 80, 160, 100), (center_x, center_y), 12)
        
        # Мистические частицы вокруг кристалла
        for j in range(6):
            angle = (i * 0.4 + j * 1.047) % (2 * math.pi)  # 60 градусов между частицами
            particle_x = center_x + int(10 * math.cos(angle))
            particle_y = center_y + int(10 * math.sin(angle))
            pygame.draw.circle(crystal_surface, (200, 160, 220, 150), 
                             (particle_x, particle_y), 2)
        
        # Дополнительные вращающиеся частицы
        for j in range(4):
            angle = (i * 0.6 + j * 1.57) % (2 * math.pi)  # 90 градусов между частицами
            particle_x = center_x + int(8 * math.cos(angle))
            particle_y = center_y + int(8 * math.sin(angle))
            pygame.draw.circle(crystal_surface, (220, 180, 255, 180), 
                             (particle_x, particle_y), 1)
        
        # Эффект пульсации
        pulse = int(3 * math.sin(i * 0.8))
        pygame.draw.circle(crystal_surface, (100, 60, 120, 80), 
                         (center_x, center_y), 16 + pulse)
        
        # Мистические руны
        for j in range(3):
            angle = j * 2.094 + i * 0.3  # 120 градусов между рунами
            rune_x = center_x + int(6 * math.cos(angle))
            rune_y = center_y + int(6 * math.sin(angle))
            pygame.draw.circle(crystal_surface, (180, 120, 200, 200), 
                             (rune_x, rune_y), 1)
        
        # Применяем кристалл к экрану
        screen.blit(crystal_surface, (x - 15, y - 15))
        
        pygame.display.flip()
        pygame.time.delay(25)

def animate_slow_spell(screen, start, end, redraw_callback=None):
    """Замедление: густые шипастые лозы с тенями оплетают цель"""
    frames = 24
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        
        # Эффект замедления с корнями
        slow_surface = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*1.5, CELL_SIZE*1.5
        
        # Основной эффект замедления
        alpha = int(150 * (1 - abs(t - 0.5) * 2))
        
        # Земляной фон и падающая тень от лоз
        pygame.draw.circle(slow_surface, (70, 50, 30, alpha//2), (center_x+2, center_y+2), 32)
        pygame.draw.circle(slow_surface, (80, 60, 40, alpha//2), (center_x, center_y), 30)
        
        # Оплетающие шипастые корни
        for j in range(10):
            angle = j * math.pi / 4 + i * 0.2
            # Основной корень
            root_length = 22 + int(12 * math.sin(i * 0.3 + j))
            root_x = center_x + int(root_length * math.cos(angle))
            root_y = center_y + int(root_length * math.sin(angle))
            # Тень
            pygame.draw.line(slow_surface, (50, 35, 20, alpha//2), (center_x+2, center_y+2), (root_x+2, root_y+2), 5)
            # Рисуем корень с ветвлением
            pygame.draw.line(slow_surface, (60, 40, 20, alpha), (center_x, center_y), (root_x, root_y), 5)
            # Шипы на корне
            for s in range(2):
                spike_angle = angle + (s*2-1)*0.3
                spike_len = 6
                sx = root_x - int(8 * math.cos(angle))
                sy = root_y - int(8 * math.sin(angle))
                ex = sx + int(spike_len * math.cos(spike_angle))
                ey = sy + int(spike_len * math.sin(spike_angle))
                pygame.draw.line(slow_surface, (60, 40, 20, alpha), (sx, sy), (ex, ey), 3)
            # Ветви корня
            for k in range(2):
                branch_angle = angle + (k * 2 - 1) * 0.5
                branch_length = 8 + int(5 * math.sin(i * 0.4 + j + k))
                branch_x = root_x + int(branch_length * math.cos(branch_angle))
                branch_y = root_y + int(branch_length * math.sin(branch_angle))
                pygame.draw.line(slow_surface, (50, 30, 10, alpha), (root_x, root_y), (branch_x, branch_y), 3)
                
                # Мелкие отростки
                for l in range(2):
                    twig_angle = branch_angle + (l * 2 - 1) * 0.3
                    twig_length = 4 + int(3 * math.sin(i * 0.5 + j + k + l))
                    twig_x = branch_x + int(twig_length * math.cos(twig_angle))
                    twig_y = branch_y + int(twig_length * math.sin(twig_angle))
                    pygame.draw.line(slow_surface, (40, 20, 0, alpha), (branch_x, branch_y), (twig_x, twig_y), 2)
        
        # Дополнительные корни, появляющиеся постепенно
        for j in range(5):
            if i > j * 3:  # Появляются постепенно
                angle = j * math.pi / 2 + i * 0.15
                root_length = 15 + int(8 * math.sin(i * 0.25 + j))
                root_x = center_x + int(root_length * math.cos(angle))
                root_y = center_y + int(root_length * math.sin(angle))
                
                pygame.draw.line(slow_surface, (70, 50, 30, alpha), (center_x, center_y), (root_x, root_y), 4)
        
        # Эффект оцепенения (густой круг)
        pygame.draw.circle(slow_surface, (90, 70, 50, alpha//3), (center_x, center_y), 26)
        
        # Частицы земли
        for j in range(16):
            particle_x = center_x + random.randint(-20, 20)
            particle_y = center_y + random.randint(-20, 20)
            particle_alpha = int(alpha * 0.6)
            pygame.draw.circle(slow_surface, (90, 70, 50, particle_alpha), (particle_x, particle_y), 2)
        
        # Эффект пульсации корней
        pulse = int(5 * math.sin(i * 0.4))
        pygame.draw.circle(slow_surface, (60, 40, 20, alpha//4), (center_x, center_y), 30 + pulse)
        
        # Применяем эффект к экрану
        screen.blit(slow_surface, (x - CELL_SIZE*1.5, y - CELL_SIZE*1.5))
        
        pygame.display.flip()
        pygame.time.delay(30)

def animate_slow_spell_fly(screen, start, end, redraw_callback=None):
    """Анимация полета заклинания Замедление"""
    frames = 12
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        
        # Создаем летящий корень
        root_surface = pygame.Surface((25, 25), pygame.SRCALPHA)
        center_x, center_y = 12, 12
        
        # Основной корень
        pygame.draw.line(root_surface, (80, 60, 40), (center_x-8, center_y), (center_x+8, center_y), 4)
        
        # Ветви корня
        pygame.draw.line(root_surface, (70, 50, 30), (center_x-6, center_y-3), (center_x-2, center_y-6), 2)
        pygame.draw.line(root_surface, (70, 50, 30), (center_x+6, center_y-3), (center_x+2, center_y-6), 2)
        pygame.draw.line(root_surface, (70, 50, 30), (center_x-6, center_y+3), (center_x-2, center_y+6), 2)
        pygame.draw.line(root_surface, (70, 50, 30), (center_x+6, center_y+3), (center_x+2, center_y+6), 2)
        
        # Частицы земли
        for j in range(3):
            particle_x = center_x + random.randint(-8, 8)
            particle_y = center_y + random.randint(-8, 8)
            pygame.draw.circle(root_surface, (90, 70, 50, 150), 
                             (particle_x, particle_y), 1)
        
        # Применяем к экрану
        screen.blit(root_surface, (x - 12, y - 12))
        
        pygame.display.flip()
        pygame.time.delay(25)

def animate_bless_spell(screen, start, end, redraw_callback=None):
    """Новая анимация Благословения: святой символ, золотой столп света,
    материализация кубка на краткий миг, поток святой воды и финальная вспышка."""
    frames = 34
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Фиксируем позицию на цели
        x = int(end[0])
        y = int(end[1])

        surf = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        cx, cy = CELL_SIZE*1.5, CELL_SIZE*1.5

        # 1) Святой символ на земле (круг, крест, орнамент), появляется и ярчеет
        sym_t = min(1.0, i / 8.0)
        sym_alpha = int(220 * sym_t)
        pygame.draw.circle(surf, (255, 230, 160, sym_alpha//3), (cx, cy), 32, 2)
        pygame.draw.circle(surf, (255, 240, 180, sym_alpha//2), (cx, cy), 22, 2)
        # крест
        pygame.draw.line(surf, (255, 255, 200, sym_alpha), (cx-10, cy), (cx+10, cy), 3)
        pygame.draw.line(surf, (255, 255, 200, sym_alpha), (cx, cy-10), (cx, cy+10), 3)
        # мелкие рунки по кругу
        for k in range(6):
            a = k * (2*math.pi/6) + i*0.1
            rx = int(cx + 16 * math.cos(a))
            ry = int(cy + 16 * math.sin(a))
            pygame.draw.circle(surf, (255, 240, 190, sym_alpha), (rx, ry), 2)

        # 2) Золотой столп света сверху, слегка пульсирует
        beam_t = min(1.0, max(0.0, (i-4)/6.0))
        beam_alpha = int(180 * beam_t)
        pygame.draw.rect(surf, (255, 240, 180, beam_alpha), (cx-10, cy-40, 20, 80))
        # мягкие края столпа
        pygame.draw.rect(surf, (255, 240, 180, max(0, beam_alpha//2)), (cx-14, cy-40, 4, 80))
        pygame.draw.rect(surf, (255, 240, 180, max(0, beam_alpha//2)), (cx+10, cy-40, 4, 80))

        # 3) Усиление столпа и символа в средней фазе (без кубка и воды)
        if 8 <= i <= 16:
            boost_t = (i-8) / 8.0
            boost_alpha = int(140 * (1.0 - abs(0.5 - boost_t) * 2))
            # дополнительное свечение столпа
            pygame.draw.rect(surf, (255, 245, 200, boost_alpha), (cx-12, cy-42, 24, 84), 0)
            # расширяющееся кольцо на символе
            ring_r = 16 + int(10 * boost_t)
            pygame.draw.circle(surf, (255, 245, 200, boost_alpha), (cx, cy), ring_r, 2)

        # 4) Золотые лучи и искры вокруг цели
        ray_alpha = int(180 * min(1.0, max(0.0, (i-6)/10.0)))
        for r in range(10):
            ang = r * (2*math.pi/10) + i*0.12
            rlen = 22 + int(6*math.sin(i*0.2 + r))
            rx = cx + int(rlen * math.cos(ang))
            ry = cy + int(rlen * math.sin(ang))
            pygame.draw.line(surf, (255, 235, 180, ray_alpha), (cx, cy), (rx, ry), 2)
        for s in range(14):
            ang = s * 0.45 + i*0.18
            rr = 16 + random.randint(-3, 5)
            sx = cx + int(rr * math.cos(ang))
            sy = cy + int(rr * math.sin(ang))
            pygame.draw.circle(surf, (255, 245, 200, ray_alpha), (sx, sy), 2)

        # 5) Финальная мягкая вспышка благодати (последние кадры)
        if i > frames-8:
            ft = (i-(frames-8))/8.0
            burst_alpha = int(220 * (1.0 - ft))
            pygame.draw.circle(surf, (255, 250, 210, burst_alpha), (cx, cy), 26 + int(10*ft))

        # Рендер на экран
        screen.blit(surf, (x - CELL_SIZE*1.5, y - CELL_SIZE*1.5))
        pygame.display.flip()
        pygame.time.delay(26)

def animate_bless_spell_fly(screen, start, end, redraw_callback=None):
    """Анимация полета заклинания Благословение"""
    frames = 12
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        
        # Создаем летящий кубок
        cup_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        center_x, center_y = 10, 10
        
        # Кубок
        pygame.draw.ellipse(cup_surface, (200, 200, 255), (center_x-6, center_y+2, 12, 8))
        pygame.draw.rect(cup_surface, (220, 220, 255), (center_x-4, center_y-6, 8, 8))
        pygame.draw.rect(cup_surface, (180, 180, 255), (center_x-4, center_y-6, 8, 2))
        
        # Светящиеся частицы вокруг кубка
        for j in range(4):
            angle = j * 1.57 + i * 0.5
            particle_x = center_x + int(8 * math.cos(angle))
            particle_y = center_y + int(8 * math.sin(angle))
            pygame.draw.circle(cup_surface, (255, 255, 200, 180), 
                             (particle_x, particle_y), 2)
        
        # Применяем к экрану
        screen.blit(cup_surface, (x - 10, y - 10))
        
        pygame.display.flip()
        pygame.time.delay(25)

def animate_dispel_spell(screen, start, end, redraw_callback=None):
    """Детальная анимация заклинания Снятие чар с расходящимися волнами"""
    frames = 22
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        
        # Создаем эффект снятия чар
        dispel_surface = pygame.Surface((CELL_SIZE*4, CELL_SIZE*4), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*2, CELL_SIZE*2
        
        # Основной эффект снятия чар
        alpha = int(170 * (1 - abs(t - 0.5) * 2))
        
        # Расходящиеся волны
        for wave in range(5):
            wave_radius = 10 + wave * 8 + int(5 * math.sin(i * 0.3 + wave))
            wave_alpha = int(alpha * (1 - wave * 0.2))
            pygame.draw.circle(dispel_surface, (100, 150, 255, wave_alpha), 
                             (center_x, center_y), wave_radius, 3)
        
        # Дополнительные волны
        for wave in range(3):
            wave_radius = 15 + wave * 12 + int(8 * math.sin(i * 0.4 + wave))
            wave_alpha = int(alpha * 0.6 * (1 - wave * 0.3))
            pygame.draw.circle(dispel_surface, (120, 170, 255, wave_alpha), 
                             (center_x, center_y), wave_radius, 2)
        
        # Центральная вспышка
        flash_alpha = int(alpha * 1.2)
        pygame.draw.circle(dispel_surface, (200, 220, 255, flash_alpha), 
                         (center_x, center_y), 8)
        pygame.draw.circle(dispel_surface, (255, 255, 255, flash_alpha), 
                         (center_x, center_y), 4)
        
        # Частицы очищения
        for j in range(15):
            angle = j * 0.419 + i * 0.4  # вращение
            radius = 20 + random.randint(-8, 8)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.8)
            pygame.draw.circle(dispel_surface, (150, 200, 255, particle_alpha), 
                             (particle_x, particle_y), 3)
        
        # Дополнительные светящиеся частицы
        for j in range(10):
            particle_x = center_x + random.randint(-25, 25)
            particle_y = center_y + random.randint(-25, 25)
            particle_alpha = int(alpha * 0.6)
            pygame.draw.circle(dispel_surface, (180, 220, 255, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Эффект пульсации волн
        pulse1 = int(6 * math.sin(i * 0.5))
        pulse2 = int(4 * math.sin(i * 0.7 + 1))
        pulse3 = int(3 * math.sin(i * 0.9 + 2))
        
        pygame.draw.circle(dispel_surface, (80, 130, 255, alpha//4), 
                         (center_x, center_y), 30 + pulse1)
        pygame.draw.circle(dispel_surface, (100, 150, 255, alpha//5), 
                         (center_x, center_y), 40 + pulse2)
        pygame.draw.circle(dispel_surface, (120, 170, 255, alpha//6), 
                         (center_x, center_y), 50 + pulse3)
        
        # Световые лучи очищения
        for j in range(8):
            angle = j * math.pi / 4 + i * 0.3
            ray_length = 30 + int(8 * math.sin(i * 0.4 + j))
            ray_x = center_x + int(ray_length * math.cos(angle))
            ray_y = center_y + int(ray_length * math.sin(angle))
            pygame.draw.line(dispel_surface, (150, 200, 255, alpha//2), 
                           (center_x, center_y), (ray_x, ray_y), 3)
        
        # Эффект искр очищения
        for j in range(12):
            spark_x = center_x + random.randint(-30, 30)
            spark_y = center_y + random.randint(-30, 30)
            spark_alpha = int(alpha * 0.7)
            pygame.draw.circle(dispel_surface, (255, 255, 255, spark_alpha), 
                             (spark_x, spark_y), 1)
        
        # Применяем эффект к экрану
        screen.blit(dispel_surface, (x - CELL_SIZE*2, y - CELL_SIZE*2))
        
        pygame.display.flip()
        pygame.time.delay(30)

def animate_stone_skin(screen, target_pos, redraw_callback=None):
    """Плитки-кирпичики поднимаются снизу, собираются вокруг юнита и потом рассыпаются."""
    x, y = target_pos
    cx, cy = x, y
    frames = 34
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        t = i / (frames - 1)
        layer = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        ox, oy = CELL_SIZE//2, CELL_SIZE//2
        # Фаза 1 (0..0.35): кирпичики поднимаются снизу
        if t <= 0.35:
            rise = t / 0.35
            tile_w, tile_h = 12, 8
            base_y = CELL_SIZE + int(20 * (1 - rise))
            for tx in range(0, CELL_SIZE+tile_w, tile_w):
                for ty in range(0, CELL_SIZE+tile_h, tile_h):
                    px = tx
                    py = ty + (CELL_SIZE - ty) * (1 - rise)
                    color = (122+random.randint(-4,4), 114+random.randint(-4,4), 106+random.randint(-4,4), int(160 + 80*rise))
                    pygame.draw.rect(layer, color, (px, py, tile_w-2, tile_h-2))
                    # шов
                    pygame.draw.rect(layer, (90,80,70, int(140*rise)), (px, py, tile_w-2, 1))
        # Фаза 2 (0.35..0.7): кирпичики стягиваются и обволакивают
        elif t <= 0.7:
            wrap = (t - 0.35) / 0.35
            tile_w, tile_h = 12, 8
            for tx in range(0, CELL_SIZE+tile_w, tile_w):
                for ty in range(0, CELL_SIZE+tile_h, tile_h):
                    # Смещение к центру
                    dirx = (ox - tx)
                    diry = (oy - ty)
                    px = int(tx + dirx * 0.4 * wrap)
                    py = int(ty + diry * 0.4 * wrap)
                    shade = 120 + int(20*wrap)
                    pygame.draw.rect(layer, (shade, shade-10, shade-20, 220), (px, py, tile_w-2, tile_h-2))
                    # Лёгкие трещины по мере стягивания
                    if random.random() < 0.2:
                        pygame.draw.line(layer, (80,70,60,200), (px, py), (px+tile_w-2, py+tile_h//2), 2)
        # Фаза 3 (0.7..1.0): растрескивание и осыпание
        else:
            crack_t = (t - 0.7) / 0.3
            alpha = int(220 * (1 - crack_t))
            # Кирпичные осколки разлетаются
            for k in range(40):
                ang = random.uniform(0, 2*math.pi)
                r = int(8 + 26 * crack_t)
                px = ox + int(r * math.cos(ang))
                py = oy + int(r * math.sin(ang))
                w = max(1, 3 - int(2*crack_t))
                pygame.draw.rect(layer, (140, 130, 120, alpha), (px, py, w, w))
        screen.blit(layer, (cx - CELL_SIZE//2, cy - CELL_SIZE//2))
        pygame.display.flip()
        pygame.time.delay(22)

def animate_dispel_spell_fly(screen, start, end, redraw_callback=None):
    """Анимация полета заклинания Снятие чар"""
    frames = 12
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        
        # Создаем летящую волну очищения
        wave_surface = pygame.Surface((25, 25), pygame.SRCALPHA)
        center_x, center_y = 12, 12
        
        # Центральная вспышка
        pygame.draw.circle(wave_surface, (200, 220, 255), (center_x, center_y), 6)
        pygame.draw.circle(wave_surface, (255, 255, 255), (center_x, center_y), 3)
        
        # Волны вокруг центра
        for j in range(3):
            wave_radius = 4 + j * 2
            pygame.draw.circle(wave_surface, (150, 200, 255, 150), 
                             (center_x, center_y), wave_radius, 2)
        
        # Частицы очищения
        for j in range(6):
            angle = j * 1.047 + i * 0.5
            particle_x = center_x + int(8 * math.cos(angle))
            particle_y = center_y + int(8 * math.sin(angle))
            pygame.draw.circle(wave_surface, (180, 220, 255, 180), 
                             (particle_x, particle_y), 2)
        
        # Применяем к экрану
        screen.blit(wave_surface, (x - 12, y - 12))
        
        pygame.display.flip()
        pygame.time.delay(25)

def animate_rune_shield_spell(screen, start, end, redraw_callback=None):
    """Анимация руны защиты: насыщенный глиф над целью с мерцанием и исчезновением"""
    frames = 28
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Позиция над целью (чуть выше центра клетки цели), с ограничениями по экрану
        x = int(end[0])
        y = int(end[1] - CELL_SIZE * 0.7)
        top_margin = int(CELL_SIZE * 0.5)
        bottom_margin = int(CELL_SIZE * 0.5)
        ui_panel = 80  # высота нижней панели интерфейса
        y = max(top_margin, min(SCREEN_HEIGHT - ui_panel - bottom_margin, y))
        
        # Создаем эффект руны защиты
        rune_surface = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*1.5, CELL_SIZE*1.5
        
        # Основной эффект руны (фазы появления/мерцания/исчезновения)
        t = i / (frames-1)
        base_alpha = int(220 * (1 - abs(t - 0.5) * 2))
        base_alpha = max(0, min(255, base_alpha))
        flicker = 0.75 + 0.25 * (math.sin(i * 0.8) + 1) / 2  # мягкое мерцание 0.75..1.0
        alpha = int(base_alpha * flicker)
        
        # Фаза появления (первые 8 кадров)
        if i < 8:
            appear_alpha = int(alpha * (i / 8))
            
            # Многоуровневая аура (насыщенный сине-голубой щит)
            pygame.draw.circle(rune_surface, (60, 140, 255, appear_alpha//3), (center_x, center_y), 36)
            pygame.draw.circle(rune_surface, (80, 180, 255, appear_alpha//2), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (120, 210, 255, appear_alpha//1), (center_x, center_y), 24)

            # Внешнее свечение
            pygame.draw.circle(rune_surface, (140, 240, 255, appear_alpha//2), (center_x, center_y), 18)

            # Центральный камень (как в книге заклинаний для rune_shield)
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (80, 200, 80, appear_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (40, 100, 40, appear_alpha), stone_rect.inflate(-6, -6), 2)

            # Глиф: круг и крестообразные полосы с диагоналями
            pygame.draw.circle(rune_surface, (200, 255, 255, appear_alpha), (center_x, center_y), 16, 3)
            pygame.draw.line(rune_surface, (255, 255, 255, appear_alpha), (center_x-10, center_y), (center_x+10, center_y), 3)
            pygame.draw.line(rune_surface, (255, 255, 255, appear_alpha), (center_x, center_y-10), (center_x, center_y+10), 3)
            pygame.draw.line(rune_surface, (180, 255, 255, appear_alpha), (center_x-8, center_y-8), (center_x+8, center_y+8), 2)
            pygame.draw.line(rune_surface, (180, 255, 255, appear_alpha), (center_x-8, center_y+8), (center_x+8, center_y-8), 2)

            # Рунический знак щита как в книге (поверх камня)
            shield_points = [
                (center_x-6, center_y-6), (center_x+6, center_y-6), (center_x+8, center_y+4),
                (center_x, center_y+10), (center_x-8, center_y+4)
            ]
            pygame.draw.polygon(rune_surface, (60, 255, 120, appear_alpha), shield_points)
        
        # Фаза мерцания (кадры 8-17)
        elif i < 17:
            flicker_alpha = alpha

            # Многоуровневая аура (усиленная насыщенность)
            pygame.draw.circle(rune_surface, (60, 140, 255, flicker_alpha//4), (center_x, center_y), 38)
            pygame.draw.circle(rune_surface, (80, 180, 255, flicker_alpha//3), (center_x, center_y), 32)
            pygame.draw.circle(rune_surface, (120, 210, 255, flicker_alpha//2), (center_x, center_y), 26)

            # Пульсирующее свечение
            pulse = int(3 * math.sin(i * 0.9))
            pygame.draw.circle(rune_surface, (160, 255, 255, flicker_alpha//2), (center_x, center_y), 18 + pulse)

            # Центральный камень
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (80, 200, 80, flicker_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (40, 100, 40, flicker_alpha), stone_rect.inflate(-6, -6), 2)

            # Глиф: круг и крест с диагоналями (ярче)
            pygame.draw.circle(rune_surface, (220, 255, 255, flicker_alpha), (center_x, center_y), 16, 3)
            pygame.draw.line(rune_surface, (255, 255, 255, flicker_alpha), (center_x-10, center_y), (center_x+10, center_y), 3)
            pygame.draw.line(rune_surface, (255, 255, 255, flicker_alpha), (center_x, center_y-10), (center_x, center_y+10), 3)
            pygame.draw.line(rune_surface, (190, 255, 255, flicker_alpha), (center_x-8, center_y-8), (center_x+8, center_y+8), 2)
            pygame.draw.line(rune_surface, (190, 255, 255, flicker_alpha), (center_x-8, center_y+8), (center_x+8, center_y-8), 2)

            # Рунический знак щита
            shield_points = [
                (center_x-6, center_y-6), (center_x+6, center_y-6), (center_x+8, center_y+4),
                (center_x, center_y+10), (center_x-8, center_y+4)
            ]
            pygame.draw.polygon(rune_surface, (60, 255, 120, flicker_alpha), shield_points)

            # Вращающееся кольцо рун (малые точки-глифы)
            for j in range(6):
                a = j * (math.pi/3) + i * 0.15
                rx = center_x + int(12 * math.cos(a))
                ry = center_y + int(12 * math.sin(a))
                pygame.draw.circle(rune_surface, (200, 255, 255, flicker_alpha), (rx, ry), 2)
        
        # Фаза исчезновения (последние 8 кадров)
        else:
            # Безопасная затухающая прозрачность на последних кадрах
            tail = 8
            disappear_ratio = max(0.0, min(1.0, (frames - 1 - i) / tail))
            disappear_alpha = int(alpha * disappear_ratio)

            # Исчезающая аура и глиф
            pygame.draw.circle(rune_surface, (80, 180, 255, disappear_alpha//3), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (140, 240, 255, disappear_alpha//2), (center_x, center_y), 22)
            pygame.draw.circle(rune_surface, (220, 255, 255, disappear_alpha), (center_x, center_y), 16, 2)
            pygame.draw.line(rune_surface, (255, 255, 255, disappear_alpha), (center_x-10, center_y), (center_x+10, center_y), 2)
            pygame.draw.line(rune_surface, (255, 255, 255, disappear_alpha), (center_x, center_y-10), (center_x, center_y+10), 2)

            # Камень и знак при исчезновении
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (80, 200, 80, disappear_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (40, 100, 40, disappear_alpha), stone_rect.inflate(-6, -6), 2)
            shield_points = [
                (center_x-6, center_y-6), (center_x+6, center_y-6), (center_x+8, center_y+4),
                (center_x, center_y+10), (center_x-8, center_y+4)
            ]
            pygame.draw.polygon(rune_surface, (60, 255, 120, disappear_alpha), shield_points)
        
        # Эффект пульсации
        pulse = int(5 * math.sin(i * 0.5))
        pygame.draw.circle(rune_surface, (60, 150, 255, alpha//4), 
                         (center_x, center_y), 25 + pulse)
        
        # Частицы магии
        for j in range(8):
            angle = j * 0.785 + i * 0.3
            radius = 15 + random.randint(-5, 5)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.6)
            pygame.draw.circle(rune_surface, (160, 220, 255, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Применяем эффект к экрану
        screen.blit(rune_surface, (x - CELL_SIZE*1.5, y - CELL_SIZE*1.5))
        
        pygame.display.flip()
        pygame.time.delay(30)

def animate_rune_haste_spell(screen, start, end, redraw_callback=None):
    """Анимация руны скорости: насыщенный глиф над целью с мерцанием и исчезновением"""
    frames = 28
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Позиция над целью (чуть выше центра клетки цели), с ограничениями по экрану
        x = int(end[0])
        y = int(end[1] - CELL_SIZE * 0.7)
        top_margin = int(CELL_SIZE * 0.5)
        bottom_margin = int(CELL_SIZE * 0.5)
        ui_panel = 80  # высота нижней панели интерфейса
        y = max(top_margin, min(SCREEN_HEIGHT - ui_panel - bottom_margin, y))
        
        # Создаем эффект руны скорости
        rune_surface = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*1.5, CELL_SIZE*1.5
        
        # Основной эффект руны (фазы появления/мерцания/исчезновения)
        t = i / (frames-1)
        base_alpha = int(220 * (1 - abs(t - 0.5) * 2))
        base_alpha = max(0, min(255, base_alpha))
        flicker = 0.75 + 0.25 * (math.sin(i * 0.9) + 1) / 2
        alpha = int(base_alpha * flicker)
        
        # Фаза появления (первые 8 кадров)
        if i < 8:
            appear_alpha = int(alpha * (i / 8))
            
            # Многоуровневая аура (насыщённый янтарно-золотой)
            pygame.draw.circle(rune_surface, (255, 150, 60, appear_alpha//3), (center_x, center_y), 36)
            pygame.draw.circle(rune_surface, (255, 180, 80, appear_alpha//2), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (255, 210, 110, appear_alpha//1), (center_x, center_y), 24)

            # Внешнее свечение
            pygame.draw.circle(rune_surface, (255, 240, 160, appear_alpha//2), (center_x, center_y), 18)

            # Центральный камень (как в книге заклинаний для rune_haste)
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (200, 200, 200, appear_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (120, 120, 120, appear_alpha), stone_rect.inflate(-6, -6), 2)

            # Глиф скорости: круг + стрелы/усики ускорения
            pygame.draw.circle(rune_surface, (255, 255, 220, appear_alpha), (center_x, center_y), 16, 3)
            pygame.draw.line(rune_surface, (255, 255, 255, appear_alpha), (center_x-10, center_y-5), (center_x+10, center_y-5), 3)
            pygame.draw.line(rune_surface, (255, 255, 255, appear_alpha), (center_x-8, center_y), (center_x+8, center_y), 2)
            pygame.draw.line(rune_surface, (255, 255, 255, appear_alpha), (center_x-6, center_y+5), (center_x+6, center_y+5), 2)
            # косые штрихи-ускорители
            pygame.draw.line(rune_surface, (255, 255, 220, appear_alpha), (center_x-7, center_y-9), (center_x-1, center_y-13), 2)
            pygame.draw.line(rune_surface, (255, 255, 220, appear_alpha), (center_x+7, center_y+9), (center_x+1, center_y+13), 2)

            # Молния как в книге (поверх камня)
            bolt_points = [
                (center_x-5, center_y-4), (center_x, center_y+2), (center_x-2, center_y+2), (center_x+5, center_y+10)
            ]
            pygame.draw.lines(rune_surface, (255, 255, 255, appear_alpha), False, bolt_points, 3)
        
        # Фаза мерцания (кадры 8-17)
        elif i < 17:
            flicker_alpha = alpha

            # Многоуровневая аура (усиленная насыщенность)
            pygame.draw.circle(rune_surface, (255, 150, 60, flicker_alpha//4), (center_x, center_y), 38)
            pygame.draw.circle(rune_surface, (255, 180, 80, flicker_alpha//3), (center_x, center_y), 32)
            pygame.draw.circle(rune_surface, (255, 210, 110, flicker_alpha//2), (center_x, center_y), 26)

            # Пульсирующее свечение
            pulse = int(3 * math.sin(i * 1.0))
            pygame.draw.circle(rune_surface, (255, 240, 160, flicker_alpha//2), (center_x, center_y), 18 + pulse)

            # Центральный камень
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (200, 200, 200, flicker_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (120, 120, 120, flicker_alpha), stone_rect.inflate(-6, -6), 2)

            # Глиф скорости (ярче) + ускорители
            pygame.draw.circle(rune_surface, (255, 255, 220, flicker_alpha), (center_x, center_y), 16, 3)
            pygame.draw.line(rune_surface, (255, 255, 255, flicker_alpha), (center_x-10, center_y-5), (center_x+10, center_y-5), 3)
            pygame.draw.line(rune_surface, (255, 255, 255, flicker_alpha), (center_x-8, center_y), (center_x+8, center_y), 2)
            pygame.draw.line(rune_surface, (255, 255, 255, flicker_alpha), (center_x-6, center_y+5), (center_x+6, center_y+5), 2)
            pygame.draw.line(rune_surface, (255, 255, 220, flicker_alpha), (center_x-7, center_y-9), (center_x-1, center_y-13), 2)
            pygame.draw.line(rune_surface, (255, 255, 220, flicker_alpha), (center_x+7, center_y+9), (center_x+1, center_y+13), 2)

            # Вращающееся кольцо точечных глифов
            for j in range(6):
                a = j * (math.pi/3) + i * 0.18
                rx = center_x + int(12 * math.cos(a))
                ry = center_y + int(12 * math.sin(a))
                pygame.draw.circle(rune_surface, (255, 230, 160, flicker_alpha), (rx, ry), 2)

            # Молния как в книге
            bolt_points = [
                (center_x-5, center_y-4), (center_x, center_y+2), (center_x-2, center_y+2), (center_x+5, center_y+10)
            ]
            pygame.draw.lines(rune_surface, (255, 255, 255, flicker_alpha), False, bolt_points, 3)
        
        # Фаза исчезновения (последние 8 кадров)
        else:
            # Безопасная затухающая прозрачность на последних кадрах
            tail = 8
            disappear_ratio = max(0.0, min(1.0, (frames - 1 - i) / tail))
            disappear_alpha = int(alpha * disappear_ratio)

            # Исчезающая аура и глиф
            pygame.draw.circle(rune_surface, (255, 180, 80, disappear_alpha//3), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (255, 210, 110, disappear_alpha//2), (center_x, center_y), 22)
            pygame.draw.circle(rune_surface, (255, 255, 220, disappear_alpha), (center_x, center_y), 16, 2)
            pygame.draw.line(rune_surface, (255, 255, 255, disappear_alpha), (center_x-10, center_y-5), (center_x+10, center_y-5), 2)
            pygame.draw.line(rune_surface, (255, 255, 255, disappear_alpha), (center_x-8, center_y), (center_x+8, center_y), 2)

            # Камень и молния при исчезновении
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (200, 200, 200, disappear_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (120, 120, 120, disappear_alpha), stone_rect.inflate(-6, -6), 2)
            bolt_points = [
                (center_x-5, center_y-4), (center_x, center_y+2), (center_x-2, center_y+2), (center_x+5, center_y+10)
            ]
            pygame.draw.lines(rune_surface, (255, 255, 255, disappear_alpha), False, bolt_points, 3)
        
        # Эффект пульсации
        pulse = int(5 * math.sin(i * 0.5))
        pygame.draw.circle(rune_surface, (255, 170, 70, alpha//4), 
                         (center_x, center_y), 25 + pulse)
        
        # Частицы скорости
        for j in range(8):
            angle = j * 0.785 + i * 0.4
            radius = 15 + random.randint(-5, 5)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.6)
            pygame.draw.circle(rune_surface, (255, 230, 160, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Применяем эффект к экрану
        screen.blit(rune_surface, (x - CELL_SIZE*1.5, y - CELL_SIZE*1.5))
        
        pygame.display.flip()
        pygame.time.delay(30) 