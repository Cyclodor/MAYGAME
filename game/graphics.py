import pygame
import random
import math
from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_WIDTH, GRID_HEIGHT

def load_image(name, scale=1):
    image = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    # Разделяем имя на части
    parts = name.split('_')
    if len(parts) >= 3 and parts[0] == 'hero':
        # Формат: hero_team_class
        unit = 'hero'
        team = parts[1]
        hero_class = parts[2]
    elif len(parts) >= 2:
        # Обычный формат: unit_team
        unit = '_'.join(parts[:-1])
        team = parts[-1]
        hero_class = None
    else:
        unit = name
        team = 'human'
        hero_class = None
    # Цветовые схемы
    if team == 'human':
        main_color = (180, 160, 100)
        accent = (60, 60, 200)
        metal = (180, 180, 200)
        gold = (255, 215, 0)
        skin = (255, 224, 189)
        cloth = (100, 120, 200)
    elif team == 'dwarf':
        main_color = (100, 120, 160)
        accent = (80, 100, 140)
        metal = (200, 200, 220)
        gold = (255, 215, 0)
        skin = (220, 180, 120)
        cloth = (140, 160, 180)
    elif team == 'shadow':
        main_color = (40, 0, 60)
        accent = (80, 0, 120)
        metal = (100, 80, 120)
        gold = (180, 120, 255)
        skin = (200, 180, 120)
        cloth = (60, 0, 90)
    else:
        main_color = (120, 100, 180)
        accent = (80, 40, 120)
        metal = (180, 180, 200)
        gold = (180, 120, 255)
        skin = (200, 200, 220)
        cloth = (80, 60, 120)
    # Герой
    if unit == 'hero':
        # Рисуем героя в зависимости от расы и класса
        if team == 'human':
            if hero_class == 'warrior':
                # Воин-человек: рыцарь в доспехах
                image.fill((180, 160, 100))
                pygame.draw.rect(image, (200,200,220), (10, 16, 20, 20))  # Латы
                pygame.draw.ellipse(image, (200,200,220), (10, 6, 20, 14))  # Шлем
                pygame.draw.ellipse(image, skin, (14, 10, 12, 8))  # Лицо
                pygame.draw.circle(image, (0,0,0), (18, 14), 1)
                pygame.draw.circle(image, (0,0,0), (22, 14), 1)
                pygame.draw.rect(image, gold, (14, 8, 12, 4))  # Корона на шлеме
                pygame.draw.rect(image, (220,220,240), (28, 24, 6, 14))  # Меч
                pygame.draw.rect(image, gold, (26, 22, 10, 4))  # Гарда
                pygame.draw.ellipse(image, accent, (2, 22, 12, 18))  # Щит
            elif hero_class == 'archer':
                # Лучник-человек
                image.fill((140, 160, 120))
                pygame.draw.rect(image, (120,140,80), (14, 20, 12, 16))  # Туника
                pygame.draw.ellipse(image, skin, (14, 8, 12, 12))  # Лицо
                pygame.draw.ellipse(image, (100,120,60), (12, 4, 16, 10))  # Капюшон
                pygame.draw.circle(image, (0,0,0), (18, 14), 1)
                pygame.draw.circle(image, (0,0,0), (22, 14), 1)
                pygame.draw.arc(image, (140,100,60), (4, 10, 24, 24), 0.7, 2.4, 3)  # Лук
                pygame.draw.line(image, (200,200,200), (16, 22), (26, 14), 2)  # Стрела
                pygame.draw.rect(image, (100,80,40), (26, 18, 4, 12))  # Колчан
            else:  # mage
                # Маг-человек
                image.fill((160, 140, 180))
                pygame.draw.rect(image, (100,120,200), (10, 20, 20, 16))  # Мантия
                pygame.draw.ellipse(image, skin, (12, 8, 16, 14))  # Лицо
                pygame.draw.polygon(image, (80,100,180), [(14,10),(20,4),(26,10)])  # Остроконечная шляпа
                pygame.draw.circle(image, (0,0,0), (17, 15), 1)
                pygame.draw.circle(image, (0,0,0), (23, 15), 1)
                pygame.draw.line(image, (140,120,80), (28, 12), (28, 30), 3)  # Посох
                pygame.draw.circle(image, (100,180,255), (28, 12), 4)  # Кристалл
                pygame.draw.circle(image, (120,200,255), (28, 12), 2)
        
        elif team == 'elf':
            if hero_class == 'archer':  # Лучник по умолчанию
                image.fill((60, 180, 80))
                pygame.draw.rect(image, (100, 200, 100), (12, 20, 16, 16))  # Одежда
                pygame.draw.ellipse(image, (220, 255, 200), (12, 8, 16, 16))  # Лицо
                pygame.draw.polygon(image, (220, 255, 200), [(10, 14), (4, 8), (12, 10)])  # Ухо
                pygame.draw.polygon(image, (220, 255, 200), [(30, 14), (36, 8), (28, 10)])  # Ухо
                pygame.draw.circle(image, (0,100,0), (17, 14), 2)
                pygame.draw.circle(image, (0,100,0), (23, 14), 2)
                pygame.draw.polygon(image, (200,180,60), [(14,12),(20,6),(26,12)])  # Венец
                pygame.draw.arc(image, (80,140,40), (2, 8, 28, 28), 0.5, 2.6, 3)  # Длинный лук
                pygame.draw.line(image, (220,220,220), (14, 20), (30, 12), 2)  # Стрела
            elif hero_class == 'warrior':
                image.fill((60, 180, 80))
                pygame.draw.rect(image, (120,200,120), (10, 18, 20, 18))  # Лёгкие доспехи
                pygame.draw.ellipse(image, (220, 255, 200), (12, 8, 16, 14))  # Лицо
                pygame.draw.polygon(image, (220, 255, 200), [(10, 14), (4, 8), (12, 10)])
                pygame.draw.polygon(image, (220, 255, 200), [(30, 14), (36, 8), (28, 10)])
                pygame.draw.circle(image, (0,100,0), (17, 14), 2)
                pygame.draw.circle(image, (0,100,0), (23, 14), 2)
                pygame.draw.polygon(image, (200,180,60), [(14,10),(20,4),(26,10)])
                pygame.draw.rect(image, (220,240,220), (28, 22, 5, 14))  # Эльфийский клинок
                pygame.draw.rect(image, (180,160,60), (26, 20, 9, 4))
            else:  # mage
                image.fill((60, 180, 80))
                pygame.draw.rect(image, (80,160,140), (10, 20, 20, 16))  # Мантия природы
                pygame.draw.ellipse(image, (220, 255, 200), (12, 8, 16, 14))
                pygame.draw.polygon(image, (220, 255, 200), [(10, 14), (4, 8), (12, 10)])
                pygame.draw.polygon(image, (220, 255, 200), [(30, 14), (36, 8), (28, 10)])
                pygame.draw.circle(image, (0,100,0), (17, 14), 2)
                pygame.draw.circle(image, (0,100,0), (23, 14), 2)
                pygame.draw.line(image, (100,140,60), (30, 10), (30, 32), 3)  # Посох друида
                pygame.draw.circle(image, (120,255,120), (30, 10), 4)  # Зелёный кристалл
        
        elif team == 'undead':
            if hero_class == 'mage':  # Маг по умолчанию (лич)
                image.fill((120, 100, 180))
                pygame.draw.rect(image, (80,60,120), (10, 20, 20, 16))  # Тёмная мантия
                pygame.draw.ellipse(image, (220,220,220), (12, 8, 16, 16))  # Череп
                pygame.draw.polygon(image, (180,120,255), [(14,10),(20,2),(26,10)])  # Корона мёртвых
                pygame.draw.circle(image, (180,40,220), (17, 15), 3)  # Светящиеся глаза
                pygame.draw.circle(image, (180,40,220), (23, 15), 3)
                pygame.draw.line(image, (100,80,60), (28, 10), (28, 34), 3)  # Посох некроманта
                pygame.draw.circle(image, (140,40,180), (28, 10), 5)  # Тёмный кристалл
            elif hero_class == 'warrior':
                image.fill((120, 100, 180))
                pygame.draw.rect(image, (100,100,120), (10, 16, 20, 20))  # Древняя броня
                pygame.draw.ellipse(image, (220,220,220), (12, 8, 16, 14))  # Череп в шлеме
                pygame.draw.rect(image, (80,80,100), (10, 6, 20, 8))  # Шлем
                pygame.draw.circle(image, (180,40,220), (17, 14), 2)
                pygame.draw.circle(image, (180,40,220), (23, 14), 2)
                pygame.draw.rect(image, (180,180,200), (28, 22, 6, 14))  # Проклятый меч
                pygame.draw.rect(image, (140,40,180), (26, 20, 10, 4))
            else:  # archer
                image.fill((120, 100, 180))
                pygame.draw.rect(image, (100,80,140), (12, 20, 16, 16))  # Плащ
                pygame.draw.ellipse(image, (220,220,220), (12, 8, 16, 14))  # Череп
                pygame.draw.circle(image, (180,40,220), (17, 14), 2)
                pygame.draw.circle(image, (180,40,220), (23, 14), 2)
                pygame.draw.arc(image, (60,40,80), (4, 10, 24, 24), 0.6, 2.5, 3)  # Костяной лук
                pygame.draw.line(image, (200,200,200), (16, 22), (28, 14), 2)
        
        elif team == 'demon':
            if hero_class == 'warrior':  # Воин по умолчанию
                image.fill((140, 40, 20))
                pygame.draw.rect(image, (200,60,40), (10, 18, 20, 18))  # Адская броня
                pygame.draw.ellipse(image, (240,120,80), (12, 8, 16, 14))  # Лицо
                pygame.draw.polygon(image, (180,40,20), [(12, 12), (8, 2), (16, 8)])  # Рог
                pygame.draw.polygon(image, (180,40,20), [(28, 12), (32, 2), (24, 8)])  # Рог
                pygame.draw.circle(image, (255,40,0), (17, 14), 2)  # Огненные глаза
                pygame.draw.circle(image, (255,40,0), (23, 14), 2)
                pygame.draw.rect(image, (255,100,60), (28, 22, 6, 14))  # Огненный меч
                pygame.draw.rect(image, (200,40,20), (26, 20, 10, 4))
            elif hero_class == 'mage':
                image.fill((140, 40, 20))
                pygame.draw.rect(image, (160,40,80), (10, 20, 20, 16))  # Мантия
                pygame.draw.ellipse(image, (240,120,80), (12, 8, 16, 14))
                pygame.draw.polygon(image, (180,40,20), [(12, 12), (8, 2), (16, 8)])
                pygame.draw.polygon(image, (180,40,20), [(28, 12), (32, 2), (24, 8)])
                pygame.draw.circle(image, (255,40,0), (17, 14), 2)
                pygame.draw.circle(image, (255,40,0), (23, 14), 2)
                pygame.draw.line(image, (120,60,40), (30, 10), (30, 32), 3)  # Посох демона
                pygame.draw.circle(image, (255,80,20), (30, 10), 5)  # Огненный шар
                pygame.draw.circle(image, (255,140,60), (30, 10), 3)
            else:  # archer
                image.fill((140, 40, 20))
                pygame.draw.rect(image, (180,60,40), (12, 20, 16, 16))
                pygame.draw.ellipse(image, (240,120,80), (12, 8, 16, 14))
                pygame.draw.polygon(image, (180,40,20), [(12, 12), (8, 2), (16, 8)])
                pygame.draw.polygon(image, (180,40,20), [(28, 12), (32, 2), (24, 8)])
                pygame.draw.circle(image, (255,40,0), (17, 14), 2)
                pygame.draw.circle(image, (255,40,0), (23, 14), 2)
                pygame.draw.arc(image, (140,40,20), (4, 10, 24, 24), 0.6, 2.5, 3)
                pygame.draw.line(image, (255,120,60), (16, 22), (28, 14), 2)  # Огненная стрела
        
        elif team == 'dwarf':
            if hero_class == 'warrior':  # Воин по умолчанию
                image.fill((100, 120, 160))
                pygame.draw.rect(image, (200,200,220), (10, 18, 20, 18))  # Тяжёлая броня
                pygame.draw.ellipse(image, (220,180,120), (12, 10, 16, 12))  # Лицо
                pygame.draw.ellipse(image, (200,200,220), (10, 6, 20, 10))  # Шлем
                pygame.draw.rect(image, gold, (14, 8, 12, 4))  # Рунический узор
                pygame.draw.circle(image, (60,40,20), (18, 16), 1)
                pygame.draw.circle(image, (60,40,20), (22, 16), 1)
                pygame.draw.rect(image, (140,100,60), (10, 24, 20, 8))  # Борода
                pygame.draw.rect(image, (220,220,240), (28, 20, 7, 16))  # Топор (рукоять)
                pygame.draw.polygon(image, (200,200,220), [(28,20),(28,16),(36,18)])  # Лезвие топора
            elif hero_class == 'archer':
                image.fill((100, 120, 160))
                pygame.draw.rect(image, (160,160,180), (12, 20, 16, 16))
                pygame.draw.ellipse(image, (220,180,120), (12, 10, 16, 12))
                pygame.draw.circle(image, (60,40,20), (18, 16), 1)
                pygame.draw.circle(image, (60,40,20), (22, 16), 1)
                pygame.draw.rect(image, (140,100,60), (12, 22, 16, 8))  # Борода
                pygame.draw.arc(image, (120,80,40), (2, 8, 28, 28), 0.5, 2.6, 3)  # Арбалет
                pygame.draw.line(image, (200,200,200), (14, 20), (30, 12), 2)
            else:  # mage
                image.fill((100, 120, 160))
                pygame.draw.rect(image, (120,140,180), (10, 20, 20, 16))  # Рунная мантия
                pygame.draw.ellipse(image, (220,180,120), (12, 10, 16, 12))
                pygame.draw.circle(image, (60,40,20), (18, 16), 1)
                pygame.draw.circle(image, (60,40,20), (22, 16), 1)
                pygame.draw.rect(image, (140,100,60), (12, 22, 16, 6))  # Борода
                pygame.draw.line(image, (180,140,80), (30, 10), (30, 32), 4)  # Рунный посох
                pygame.draw.circle(image, (200,180,80), (30, 10), 5)  # Руна
                for i in range(3):
                    pygame.draw.circle(image, gold, (30, 16+i*6), 2)  # Руны на посохе
        
        elif team == 'shadow':
            if hero_class == 'mage':  # Маг по умолчанию (чернокнижник)
                image.fill((40,0,60))
                pygame.draw.rect(image, (80,0,120), (10, 20, 20, 16))  # Тёмный плащ
                pygame.draw.ellipse(image, (200,180,120), (12, 8, 16, 14))  # Лицо
                pygame.draw.polygon(image, (120,0,180), [(12,8),(20,0),(28,8)])  # Капюшон
                pygame.draw.circle(image, (120,0,180), (17, 14), 2)  # Тёмные глаза
                pygame.draw.circle(image, (120,0,180), (23, 14), 2)
                pygame.draw.line(image, (60,40,80), (30, 10), (30, 34), 3)  # Посох теней
                pygame.draw.circle(image, (140,0,200), (30, 10), 5)  # Фиолетовый кристалл
            elif hero_class == 'warrior':
                image.fill((40,0,60))
                pygame.draw.rect(image, (60,0,90), (10, 18, 20, 18))  # Теневая броня
                pygame.draw.ellipse(image, (200,180,120), (12, 10, 16, 12))
                pygame.draw.rect(image, (40,0,60), (10, 8, 20, 8))  # Шлем
                pygame.draw.circle(image, (140,0,200), (17, 15), 2)
                pygame.draw.circle(image, (140,0,200), (23, 15), 2)
                pygame.draw.rect(image, (100,0,140), (28, 22, 6, 14))  # Теневой клинок
                pygame.draw.rect(image, (80,0,120), (26, 20, 10, 4))
            else:  # archer
                image.fill((40,0,60))
                pygame.draw.rect(image, (60,0,90), (12, 20, 16, 16))
                pygame.draw.ellipse(image, (200,180,120), (12, 10, 16, 12))
                pygame.draw.circle(image, (140,0,200), (17, 15), 2)
                pygame.draw.circle(image, (140,0,200), (23, 15), 2)
                pygame.draw.arc(image, (80,0,120), (4, 10, 24, 24), 0.6, 2.5, 3)
                pygame.draw.line(image, (140,0,200), (16, 22), (28, 14), 2)  # Теневая стрела
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
        # --- Новые юниты гномов ---
        elif unit == 'forgedragon':
            image.fill((140, 80, 40))
            # Каменно-металлическое тело (дракон без крыльев)
            pygame.draw.ellipse(image, (160, 100, 60), (8, 20, 24, 14))
            # Металлические пластины
            for i in range(3):
                pygame.draw.rect(image, metal, (10+i*6, 22, 5, 10))
            # Голова
            pygame.draw.ellipse(image, (160, 100, 60), (22, 8, 14, 12))
            pygame.draw.circle(image, (255, 100, 0), (26, 12), 2)  # Огненный глаз
            pygame.draw.circle(image, (255, 100, 0), (32, 12), 2)
            # Рога из металла
            pygame.draw.polygon(image, metal, [(24, 8), (22, 2), (26, 8)])
            pygame.draw.polygon(image, metal, [(34, 8), (36, 2), (32, 8)])
            # Хвост с молотом
            pygame.draw.line(image, (140, 80, 40), (10, 28), (4, 34), 3)
            pygame.draw.rect(image, metal, (2, 32, 4, 6))
        elif unit == 'mountainruler':
            image.fill((120, 100, 80))
            # Мощное тело
            pygame.draw.rect(image, metal, (10, 18, 20, 20))
            # Борода и лицо
            pygame.draw.ellipse(image, skin, (14, 12, 12, 10))
            pygame.draw.circle(image, (0,0,0), (18, 16), 1)
            pygame.draw.circle(image, (0,0,0), (22, 16), 1)
            # Длинная борода
            pygame.draw.ellipse(image, (140, 100, 60), (12, 20, 16, 14))
            # Корона
            pygame.draw.rect(image, gold, (14, 10, 12, 4))
            for i in range(3):
                pygame.draw.polygon(image, gold, [(16+i*3, 10), (17+i*3, 6), (18+i*3, 10)])
            # Королевский молот
            pygame.draw.line(image, (100, 80, 60), (28, 20), (28, 36), 4)
            pygame.draw.rect(image, metal, (24, 16, 8, 8))
            pygame.draw.circle(image, gold, (28, 20), 2)
        elif unit == 'volkhv':
            image.fill((100, 120, 140))
            # Роба с рунами
            pygame.draw.rect(image, (140, 160, 180), (10, 18, 20, 22))
            pygame.draw.ellipse(image, (140, 160, 180), (10, 10, 20, 12))  # Капюшон
            # Лицо с бородой
            pygame.draw.ellipse(image, skin, (14, 14, 12, 10))
            pygame.draw.circle(image, (0,0,0), (18, 18), 1)
            pygame.draw.circle(image, (0,0,0), (22, 18), 1)
            # Борода
            pygame.draw.ellipse(image, (180, 160, 140), (14, 22, 12, 10))
            # Руны на робе
            for i in range(3):
                pygame.draw.line(image, (100, 200, 255), (14, 26+i*4), (18, 26+i*4), 2)
                pygame.draw.line(image, (100, 200, 255), (22, 26+i*4), (26, 26+i*4), 2)
            # Рунический посох
            pygame.draw.line(image, (100, 80, 60), (28, 12), (28, 38), 3)
            for i in range(4):
                pygame.draw.circle(image, (100, 200, 255), (28, 14+i*6), 2)
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
        # --- Новые юниты теней ---
        elif unit == 'manticore':
            image.fill((60, 40, 80))
            # Тело льва
            pygame.draw.ellipse(image, (100, 80, 60), (8, 20, 24, 14))
            # Лапы
            for i in range(4):
                pygame.draw.rect(image, (100, 80, 60), (10+i*6, 32, 4, 8))
            # Голова со злым лицом
            pygame.draw.ellipse(image, (100, 80, 60), (24, 10, 12, 10))
            pygame.draw.circle(image, (200, 0, 0), (28, 14), 2)
            pygame.draw.circle(image, (200, 0, 0), (32, 14), 2)
            # Крылья летучей мыши
            pygame.draw.polygon(image, (60, 40, 80), [(16, 18), (4, 12), (10, 22)])
            pygame.draw.polygon(image, (60, 40, 80), [(24, 18), (36, 12), (30, 22)])
            # Хвост скорпиона
            for i in range(3):
                pygame.draw.circle(image, (80, 60, 100), (6-i, 28+i*2), 2)
            pygame.draw.polygon(image, (120, 0, 120), [(4, 34), (2, 36), (6, 36)])  # Жало
        elif unit == 'reddragon':
            image.fill((120, 0, 0))
            # Красное тело дракона
            pygame.draw.ellipse(image, (180, 0, 0), (8, 20, 24, 14))
            # Чешуя
            for i in range(3):
                for j in range(2):
                    pygame.draw.circle(image, (140, 0, 0), (12+i*6, 24+j*4), 2)
            # Голова
            pygame.draw.ellipse(image, (180, 0, 0), (22, 8, 14, 12))
            pygame.draw.circle(image, (255, 150, 0), (26, 12), 2)  # Огненный глаз
            pygame.draw.circle(image, (255, 150, 0), (32, 12), 2)
            # Рога
            pygame.draw.polygon(image, (80, 0, 0), [(24, 8), (22, 2), (26, 8)])
            pygame.draw.polygon(image, (80, 0, 0), [(34, 8), (36, 2), (32, 8)])
            # Большие крылья
            for i in range(3):
                pygame.draw.ellipse(image, (140, 0, 0), (2+i, 10+i*4, 12, 16))
                pygame.draw.ellipse(image, (140, 0, 0), (26+i, 10+i*4, 12, 16))
            # Огонь изо рта
            for i in range(2):
                pygame.draw.circle(image, (255, 200, 0), (36+i*2, 14+i), 2)
        elif unit == 'beholder':
            image.fill((60, 20, 80))
            # Центральный большой глаз
            pygame.draw.circle(image, (100, 60, 120), (20, 20), 12)
            pygame.draw.circle(image, (255, 255, 255), (20, 20), 10)
            pygame.draw.circle(image, (200, 0, 200), (20, 20), 6)
            pygame.draw.circle(image, (0, 0, 0), (20, 20), 3)
            pygame.draw.circle(image, (255, 255, 255), (18, 18), 1)  # Блик
            # Маленькие глаза на щупальцах вокруг
            positions = [(20, 8), (30, 12), (32, 22), (28, 32), (20, 34), (12, 32), (8, 22), (10, 12)]
            for i, (x, y) in enumerate(positions):
                # Щупальце
                pygame.draw.line(image, (80, 40, 100), (20, 20), (x, y), 2)
                # Глаз
                pygame.draw.circle(image, (150, 100, 180), (x, y), 3)
                pygame.draw.circle(image, (0, 0, 0), (x, y), 1)
    
    # ==================== НОВЫЕ ЮНИТЫ ====================
    # --- Новые юниты людей ---
    elif unit == 'monk':
        image.fill((200, 180, 140))
        # Роба
        pygame.draw.rect(image, (150, 120, 80), (10, 18, 20, 22))
        pygame.draw.ellipse(image, (150, 120, 80), (10, 10, 20, 12))  # Капюшон
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 14, 12, 10))
        pygame.draw.circle(image, (0,0,0), (18, 18), 1)
        pygame.draw.circle(image, (0,0,0), (22, 18), 1)
        # Крест
        pygame.draw.rect(image, gold, (19, 24, 2, 8))
        pygame.draw.rect(image, gold, (16, 26, 8, 2))
        # Руки сложены в молитве
        pygame.draw.ellipse(image, skin, (16, 28, 8, 6))
    
    elif unit == 'angel':
        image.fill((240, 240, 255))
        # Тело в доспехах
        pygame.draw.rect(image, (220, 220, 240), (12, 18, 16, 18))
        # Голова
        pygame.draw.ellipse(image, skin, (14, 10, 12, 10))
        pygame.draw.circle(image, (0,0,0), (18, 14), 1)
        pygame.draw.circle(image, (0,0,0), (22, 14), 1)
        # Волосы
        pygame.draw.ellipse(image, (255, 220, 150), (12, 8, 16, 8))
        # Крылья
        for i in range(3):
            pygame.draw.ellipse(image, (255, 255, 255), (2+i*2, 16+i*4, 8, 12))
            pygame.draw.ellipse(image, (255, 255, 255), (30-i*2, 16+i*4, 8, 12))
        # Меч света
        pygame.draw.rect(image, (255, 255, 200), (28, 20, 4, 14))
        pygame.draw.rect(image, gold, (26, 18, 8, 4))
    
    elif unit == 'cavalryman':
        image.fill((180, 140, 100))
        # Конь - тело
        pygame.draw.ellipse(image, (140, 100, 60), (6, 22, 28, 14))
        # Конь - голова
        pygame.draw.ellipse(image, (140, 100, 60), (26, 12, 10, 10))
        pygame.draw.circle(image, (0,0,0), (30, 16), 2)
        # Всадник - торс
        pygame.draw.rect(image, metal, (14, 12, 12, 12))
        # Всадник - голова
        pygame.draw.ellipse(image, skin, (16, 6, 8, 8))
        pygame.draw.circle(image, (0,0,0), (18, 9), 1)
        pygame.draw.circle(image, (0,0,0), (22, 9), 1)
        # Шлем
        pygame.draw.ellipse(image, metal, (16, 4, 8, 6))
        # Копьё
        pygame.draw.line(image, (160, 140, 120), (26, 10), (36, 4), 3)
        pygame.draw.polygon(image, metal, [(36,2), (38,4), (36,6)])
    
    # --- Новые юниты нежити ---
    elif unit == 'deathknight':
        image.fill((40, 40, 60))
        # Чёрные доспехи
        pygame.draw.rect(image, (60, 60, 80), (10, 16, 20, 22))
        # Шлем
        pygame.draw.ellipse(image, (60, 60, 80), (10, 8, 20, 14))
        # Глаза - светящиеся красные
        pygame.draw.circle(image, (255, 0, 0), (16, 14), 2)
        pygame.draw.circle(image, (255, 0, 0), (24, 14), 2)
        # Тёмный меч
        pygame.draw.rect(image, (40, 40, 60), (28, 22, 6, 16))
        pygame.draw.rect(image, (80, 0, 0), (26, 20, 10, 4))
        # Щит с черепом
        pygame.draw.ellipse(image, (60, 60, 80), (2, 22, 12, 18))
        pygame.draw.circle(image, (200, 200, 200), (8, 28), 3)
    
    elif unit == 'bonedragon':
        image.fill((60, 60, 80))
        # Костяное тело дракона
        pygame.draw.ellipse(image, (200, 200, 200), (8, 20, 24, 14))
        # Рёбра
        for i in range(4):
            pygame.draw.arc(image, (180, 180, 180), (10+i*4, 22, 8, 8), 0, 3.14, 2)
        # Костяная голова
        pygame.draw.ellipse(image, (200, 200, 200), (22, 8, 14, 12))
        pygame.draw.circle(image, (255, 0, 0), (26, 12), 2)  # Красный глаз
        pygame.draw.circle(image, (255, 0, 0), (32, 12), 2)
        # Зубы
        for i in range(3):
            pygame.draw.polygon(image, (240, 240, 240), [(24+i*3, 18), (25+i*3, 20), (26+i*3, 18)])
        # Костяные крылья
        for i in range(2):
            pygame.draw.line(image, (180, 180, 180), (16, 16), (4+i*4, 8+i*6), 2)
            pygame.draw.line(image, (180, 180, 180), (24, 16), (32+i*4, 8+i*6), 2)
    
    elif unit == 'reaper':
        image.fill((20, 20, 40))
        # Чёрная роба
        pygame.draw.ellipse(image, (40, 40, 60), (8, 12, 24, 26))
        # Капюшон
        pygame.draw.ellipse(image, (40, 40, 60), (12, 6, 16, 14))
        # Темнота под капюшоном
        pygame.draw.ellipse(image, (0, 0, 0), (14, 10, 12, 8))
        # Красные глаза
        pygame.draw.circle(image, (255, 0, 0), (18, 14), 2)
        pygame.draw.circle(image, (255, 0, 0), (22, 14), 2)
        # Коса
        pygame.draw.line(image, (160, 160, 160), (28, 14), (28, 36), 3)
        pygame.draw.arc(image, (160, 160, 160), (20, 8, 16, 12), 0, 3.14, 3)
    
    # --- Новые юниты эльфов ---
    elif unit == 'greendragon':
        image.fill((60, 140, 60))
        # Тело дракона
        pygame.draw.ellipse(image, (80, 180, 80), (8, 20, 24, 14))
        # Чешуя
        for i in range(3):
            for j in range(2):
                pygame.draw.circle(image, (60, 160, 60), (12+i*6, 24+j*4), 2)
        # Голова
        pygame.draw.ellipse(image, (80, 180, 80), (22, 8, 14, 12))
        pygame.draw.circle(image, (255, 255, 0), (26, 12), 2)  # Золотой глаз
        pygame.draw.circle(image, (255, 255, 0), (32, 12), 2)
        # Рога
        pygame.draw.polygon(image, (100, 200, 100), [(24, 8), (22, 4), (26, 8)])
        pygame.draw.polygon(image, (100, 200, 100), [(34, 8), (36, 4), (32, 8)])
        # Крылья
        for i in range(3):
            pygame.draw.ellipse(image, (100, 200, 100), (2+i, 12+i*4, 10, 14))
            pygame.draw.ellipse(image, (100, 200, 100), (28+i, 12+i*4, 10, 14))
    
    elif unit == 'druid':
        image.fill((80, 120, 60))
        # Зелёная роба
        pygame.draw.rect(image, (100, 160, 80), (10, 18, 20, 22))
        pygame.draw.ellipse(image, (100, 160, 80), (10, 10, 20, 12))  # Капюшон
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 14, 12, 10))
        pygame.draw.circle(image, (0,0,0), (18, 18), 1)
        pygame.draw.circle(image, (0,0,0), (22, 18), 1)
        # Длинные уши эльфа
        pygame.draw.polygon(image, skin, [(13, 16), (10, 14), (14, 14)])
        pygame.draw.polygon(image, skin, [(27, 16), (30, 14), (26, 14)])
        # Посох с листьями
        pygame.draw.line(image, (120, 80, 40), (28, 12), (28, 38), 3)
        pygame.draw.circle(image, (100, 200, 100), (28, 10), 3)
        for i in range(3):
            pygame.draw.ellipse(image, (120, 220, 120), (26+i*2, 8+i, 4, 6))
    
    elif unit == 'unicorn':
        image.fill((200, 200, 240))
        # Белое тело
        pygame.draw.ellipse(image, (240, 240, 255), (8, 20, 24, 16))
        # Ноги
        pygame.draw.rect(image, (240, 240, 255), (10, 34, 4, 8))
        pygame.draw.rect(image, (240, 240, 255), (18, 34, 4, 8))
        pygame.draw.rect(image, (240, 240, 255), (26, 34, 4, 8))
        # Голова
        pygame.draw.ellipse(image, (240, 240, 255), (24, 10, 12, 12))
        pygame.draw.circle(image, (0, 100, 200), (28, 14), 2)  # Голубой глаз
        # Рог
        pygame.draw.polygon(image, gold, [(28, 8), (30, 2), (32, 8)])
        # Грива
        for i in range(3):
            pygame.draw.ellipse(image, (255, 200, 255), (20-i*2, 10+i*2, 8, 10))
    
    # --- Новые юниты демонов ---
    elif unit == 'bloodpriestess':
        image.fill((80, 0, 40))
        # Красная роба
        pygame.draw.rect(image, (140, 0, 60), (10, 18, 20, 22))
        # Плечи
        pygame.draw.ellipse(image, (140, 0, 60), (8, 16, 10, 8))
        pygame.draw.ellipse(image, (140, 0, 60), (22, 16, 10, 8))
        # Голова
        pygame.draw.ellipse(image, (200, 150, 150), (14, 10, 12, 10))
        pygame.draw.circle(image, (255, 0, 0), (18, 14), 1)  # Красные глаза
        pygame.draw.circle(image, (255, 0, 0), (22, 14), 1)
        # Рога
        pygame.draw.arc(image, (80, 0, 0), (12, 8, 6, 8), 0, 3.14, 2)
        pygame.draw.arc(image, (80, 0, 0), (22, 8, 6, 8), 0, 3.14, 2)
        # Посох с кровавым кристаллом
        pygame.draw.line(image, (80, 40, 40), (28, 14), (28, 38), 3)
        pygame.draw.circle(image, (200, 0, 0), (28, 12), 3)
    
    elif unit == 'devil':
        image.fill((100, 0, 0))
        # Мощное тело
        pygame.draw.rect(image, (160, 0, 0), (10, 16, 20, 24))
        # Мускулы
        pygame.draw.ellipse(image, (180, 20, 20), (8, 18, 10, 12))
        pygame.draw.ellipse(image, (180, 20, 20), (22, 18, 10, 12))
        # Голова
        pygame.draw.ellipse(image, (160, 0, 0), (12, 8, 16, 12))
        pygame.draw.circle(image, (255, 100, 0), (17, 12), 2)  # Огненные глаза
        pygame.draw.circle(image, (255, 100, 0), (23, 12), 2)
        # Большие рога
        pygame.draw.arc(image, (80, 0, 0), (10, 6, 8, 10), 0, 3.14, 3)
        pygame.draw.arc(image, (80, 0, 0), (22, 6, 8, 10), 0, 3.14, 3)
        # Крылья кожистые
        for i in range(2):
            pygame.draw.polygon(image, (80, 0, 0), [(16, 20), (4+i*4, 16+i*8), (10+i*2, 24+i*4)])
            pygame.draw.polygon(image, (80, 0, 0), [(24, 20), (32+i*4, 16+i*8), (28+i*2, 24+i*4)])
        # Трезубец
        pygame.draw.line(image, (120, 120, 120), (30, 12), (30, 36), 3)
        pygame.draw.line(image, (120, 120, 120), (26, 10), (30, 14), 2)
        pygame.draw.line(image, (120, 120, 120), (30, 10), (30, 14), 2)
        pygame.draw.line(image, (120, 120, 120), (34, 10), (30, 14), 2)
    
    elif unit == 'hellhorse':
        image.fill((80, 20, 0))
        # Огненное тело коня
        pygame.draw.ellipse(image, (160, 40, 0), (6, 22, 28, 14))
        # Ноги в огне
        for i in range(4):
            pygame.draw.rect(image, (200, 60, 0), (8+i*6, 34, 4, 8))
            # Пламя от копыт
            pygame.draw.circle(image, (255, 100, 0), (10+i*6, 40), 2)
        # Голова в огне
        pygame.draw.ellipse(image, (160, 40, 0), (26, 12, 10, 10))
        pygame.draw.circle(image, (255, 0, 0), (30, 16), 2)  # Красный глаз
        # Огненная грива
        for i in range(4):
            pygame.draw.circle(image, (255, 100, 0), (20+i*2, 14+i), 3)
        # Огненный хвост
        for i in range(3):
            pygame.draw.circle(image, (255, 80, 0), (8-i, 28+i*2), 2)
    
    
    # ==================== КОНЕЦ НОВЫХ ЮНИТОВ ====================
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

# Кэш для анимированной травы
_grass_cache = {}
_grass_cache_time = 0
_grass_update_interval = 0.0125  # Обновляем каждые 0.0125 секунды для максимальной плавности (80 FPS анимация)
_grass_base_cache = {}  # Базовый кэш без анимации (создается один раз)
_grass_initialized = False

def _init_grass_base_cache():
    """Инициализирует базовый кэш травы (выполняется один раз)"""
    global _grass_base_cache, _grass_initialized
    if _grass_initialized:
        return
    
    # Используем numpy для быстрой генерации базовых травинок если доступен
    try:
        import numpy as np
        use_numpy = True
    except ImportError:
        use_numpy = False
    
    random.seed(42)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            cell_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            # Качественная анимация: 16 травинок на клетку для максимального качества
            grass_data = []
            for i in range(16):  # Увеличено до 16 травинок для максимальной детализации
                base_x = random.randint(4, CELL_SIZE-4)
                base_y = random.randint(CELL_SIZE//2, CELL_SIZE-4)
                length = random.randint(10, 18)
                base_color = (60, 170, 80)
                color = tuple(max(0, min(255, c + random.randint(-10, 10))) for c in base_color)
                phase = (x + y + i) * 0.2
                grass_data.append({
                    'base_x': base_x,
                    'base_y': base_y,
                    'length': length,
                    'color': color,
                    'phase': phase
                })
            _grass_base_cache[(x, y)] = grass_data
            # Рисуем начальное состояние
            for grass in grass_data:
                pygame.draw.line(cell_surface, grass['color'], 
                               (grass['base_x'], grass['base_y']), 
                               (grass['base_x'], grass['base_y'] - grass['length']), 1)
    random.seed()
    _grass_initialized = True

def draw_animated_grass(surface, t):
    global _grass_cache, _grass_cache_time
    
    # Инициализируем базовый кэш один раз
    _init_grass_base_cache()
    
    # Оптимизация: используем более частое обновление кэша для плавной анимации
    current_time = int(t / _grass_update_interval)
    
    # Обновляем кэш анимации только если нужно
    if current_time != _grass_cache_time or not _grass_cache:
        _grass_cache_time = current_time
        _grass_cache.clear()
        
        # Создаем анимированные поверхности из базового кэша
        for (x, y), grass_data in _grass_base_cache.items():
            cell_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            # Рисуем каждую травинку с анимацией
            for grass in grass_data:
                phase = grass['phase']
                sway = math.sin(t * 2.0 + phase) * 5
                tip_x = grass['base_x'] + int(sway)
                tip_y = grass['base_y'] - grass['length']
                pygame.draw.line(cell_surface, grass['color'], 
                               (grass['base_x'], grass['base_y']), 
                               (tip_x, tip_y), 1)
            _grass_cache[(x, y)] = cell_surface
    
    # Быстрое blit всех кэшированных поверхностей
    for (x, y), cached_surface in _grass_cache.items():
        surface.blit(cached_surface, (x * CELL_SIZE, y * CELL_SIZE))

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
    frames = 60  # Увеличено до 60 кадров для максимальной плавности
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
        pygame.time.delay(12)  # Уменьшена задержка для плавности

def animate_arrow_fly(screen, start, end, redraw_callback=None):
    return animate_arrow(screen, start, end, redraw_callback=redraw_callback, style='normal')

def animate_fire_arrow_fly(screen, start, end, redraw_callback=None):
    """Улучшенная анимация полета огненной стрелы с детальными эффектами"""
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
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
        
        # Создаем слой эффектов
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Длинный огненный шлейф за стрелой
        trail_length = 50
        for j in range(40):  # Увеличено с 20 до 40 для более плавного шлейфа
            trail_t = j / 40.0  # Исправлено деление для правильного расчета
            trail_x = x - int(trail_length * trail_t * math.cos(angle))
            trail_y = y - int(trail_length * trail_t * math.sin(angle))
            trail_r = max(2, int(8 * (1 - trail_t * 0.85)))
            
            # Градиент от яркого оранжевого к темному красному
            if trail_t < 0.3:
                color = (255, 200, 80, int(220 * (1 - trail_t)))
            elif trail_t < 0.6:
                color = (255, 140, 40, int(200 * (1 - trail_t)))
            else:
                color = (220, 80, 30, int(160 * (1 - trail_t)))
            
            pygame.draw.circle(overlay, color, (trail_x, trail_y), trail_r)
            
            # Огненные искры по бокам шлейфа
            if j % 3 == 0:
                for side in [-1, 1]:
                    spark_x = trail_x + int(8 * math.cos(angle + math.pi/2 * side))
                    spark_y = trail_y + int(8 * math.sin(angle + math.pi/2 * side))
                    pygame.draw.circle(overlay, (255, 220, 100, int(180 * (1 - trail_t))), 
                                     (spark_x, spark_y), max(1, 3 - int(trail_t * 2)))
        
        # Сама стрела (древко и наконечник)
        arrow_len = 20
        tail_x = x - int(arrow_len * math.cos(angle))
        tail_y = y - int(arrow_len * math.sin(angle))
        
        # Древко (деревянное с огнём)
        pygame.draw.line(overlay, (140, 100, 60), (tail_x, tail_y), (x, y), 4)
        pygame.draw.line(overlay, (200, 150, 80), (tail_x, tail_y), (x, y), 2)
        
        # Огненный наконечник
        tip_len = 8
        tip_x = x + int(tip_len * math.cos(angle))
        tip_y = y + int(tip_len * math.sin(angle))
        
        # Металлический наконечник с огненным свечением
        pygame.draw.line(overlay, (255, 180, 60), (x, y), (tip_x, tip_y), 5)
        pygame.draw.line(overlay, (255, 220, 120), (x, y), (tip_x, tip_y), 3)
        
        # Пульсирующее огненное свечение вокруг стрелы
        glow_r = int(12 + 4 * math.sin(i * 0.8))
        pygame.draw.circle(overlay, (255, 120, 40, 80), (x, y), glow_r)
        pygame.draw.circle(overlay, (255, 200, 100, 60), (x, y), int(glow_r * 1.3))
        
        # Летящие искры впереди стрелы
        for k in range(12):  # Увеличено с 5 до 12 искр
            spark_angle = angle + (random.random() - 0.5) * 0.5
            spark_dist = 10 + random.randint(0, 15)
            spark_x = x + int(spark_dist * math.cos(spark_angle))
            spark_y = y + int(spark_dist * math.sin(spark_angle))
            pygame.draw.circle(overlay, (255, 200, 80, 200), (spark_x, spark_y), 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_ice_arrow(screen, start, end, redraw_callback=None):
    """Анимация полета ледяной стрелы с ледяными эффектами"""
    frames = 100  # Увеличено до 100 кадров для максимальной плавности
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames - 1) if frames > 1 else 1.0
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        
        # Создаем слой эффектов
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Ледяной шлейф за стрелой
        trail_length = 40
        for j in range(30):  # Увеличено с 15 до 30 для более плавного шлейфа
            trail_t = j / 30.0  # Исправлено деление для правильного расчета
            trail_x = x - int(trail_length * trail_t * math.cos(angle))
            trail_y = y - int(trail_length * trail_t * math.sin(angle))
            trail_r = max(2, int(6 * (1 - trail_t * 0.8)))
            
            # Градиент от яркого голубого к белому
            if trail_t < 0.4:
                color = (200, 240, 255, int(200 * (1 - trail_t)))
            elif trail_t < 0.7:
                color = (180, 220, 255, int(180 * (1 - trail_t)))
            else:
                color = (150, 200, 255, int(140 * (1 - trail_t)))
            
            pygame.draw.circle(overlay, color, (trail_x, trail_y), trail_r)
        
        # Ледяные кристаллы вокруг стрелы
        for k in range(12):  # Увеличено с 6 до 12 кристаллов
            crystal_angle = angle + (k * math.pi / 3) + (i * 0.1)
            crystal_dist = 8 + random.randint(-2, 2)
            crystal_x = x + int(crystal_dist * math.cos(crystal_angle))
            crystal_y = y + int(crystal_dist * math.sin(crystal_angle))
            crystal_size = 2 + random.randint(0, 1)
            pygame.draw.circle(overlay, (220, 240, 255, 180), (crystal_x, crystal_y), crystal_size)
        
        # Сама стрела
        arrow_len = 18
        tail_x = x - int(arrow_len * math.cos(angle))
        tail_y = y - int(arrow_len * math.sin(angle))
        
        # Древко (деревянное)
        pygame.draw.line(overlay, (120, 80, 50), (tail_x, tail_y), (x, y), 3)
        pygame.draw.line(overlay, (160, 120, 70), (tail_x, tail_y), (x, y), 2)
        
        # Ледяной наконечник
        tip_len = 7
        tip_x = x + int(tip_len * math.cos(angle))
        tip_y = y + int(tip_len * math.sin(angle))
        
        # Ледяной наконечник с градиентом
        pygame.draw.line(overlay, (180, 220, 255), (x, y), (tip_x, tip_y), 4)
        pygame.draw.line(overlay, (220, 240, 255), (x, y), (tip_x, tip_y), 2)
        
        # Ледяное свечение вокруг наконечника
        glow_r = int(8 + 2 * math.sin(i * 0.7))
        pygame.draw.circle(overlay, (180, 220, 255, 100), (x, y), glow_r)
        pygame.draw.circle(overlay, (220, 240, 255, 60), (x, y), int(glow_r * 1.2))
        
        # Ледяные частицы перед стрелой
        for m in range(3):
            particle_angle = angle + (random.random() - 0.5) * 0.4
            particle_dist = 12 + random.randint(0, 10)
            particle_x = x + int(particle_dist * math.cos(particle_angle))
            particle_y = y + int(particle_dist * math.sin(particle_angle))
            pygame.draw.circle(overlay, (240, 250, 255, 180), (particle_x, particle_y), 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_magic_projectile(screen, start, end, color=(120,40,180)):
    frames = 60  # Увеличено до 60 кадров для максимальной плавности
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
        pygame.time.delay(12)  # Уменьшена задержка для плавности

def animate_magic_fly(screen, start, end, color=(120,40,180), redraw_callback=None):
    frames = 30  # Увеличено с 10 до 30 кадров
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
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
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
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_curse_voodoo(screen, target_px, redraw_callback=None):
    """Улучшенная анимация проклятия с темной магией и вороньими перьями"""
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = target_px
    
    # Массив перьев, которые падают на юнит
    feathers = []
    for _ in range(60):  # Увеличено до 60 перьев для максимальной насыщенности
        # Позиция начала падения (над юнитом)
        start_x = cx + (random.random() - 0.5) * 80
        start_y = cy - CELL_SIZE - random.random() * 60
        # Скорость падения
        vel_x = (random.random() - 0.5) * 2.5
        vel_y = random.random() * 2.0 + 1.0
        # Размер и угол поворота
        size = random.random() * 5 + 3
        angle = random.random() * 2 * math.pi
        rotation_speed = (random.random() - 0.5) * 0.3
        feathers.append({
            'x': start_x,
            'y': start_y,
            'vel_x': vel_x,
            'vel_y': vel_y,
            'size': size,
            'angle': angle,
            'rotation_speed': rotation_speed,
            'alpha': 230
        })
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1)
        
        # Темная магическая аура вокруг цели
        aura_alpha = int(140 * math.sin(t * math.pi))
        for aura_ring in range(3):
            aura_r = int(25 + aura_ring * 12 + 10 * math.sin(i * 0.3 + aura_ring))
            pygame.draw.circle(overlay, (80, 0, 80, aura_alpha // (aura_ring + 1)), 
                             (cx, cy), aura_r, 3)
        
        # Темные энергетические спирали
        for spiral in range(8):
            spiral_angle = (spiral * 2 * math.pi / 8) + t * 3
            spiral_r = int(30 + 15 * t)
            spiral_x = cx + int(spiral_r * math.cos(spiral_angle))
            spiral_y = cy + int(spiral_r * math.sin(spiral_angle))
            spiral_alpha = int(180 * (1 - t * 0.7))
            
            # Темная частица
            pygame.draw.circle(overlay, (120, 0, 120, spiral_alpha), (spiral_x, spiral_y), 3)
            pygame.draw.circle(overlay, (180, 0, 180, spiral_alpha), (spiral_x, spiral_y), 2)
            
            # След за спиралью
            trail_r = spiral_r - 8
            trail_x = cx + int(trail_r * math.cos(spiral_angle))
            trail_y = cy + int(trail_r * math.sin(spiral_angle))
            pygame.draw.line(overlay, (100, 0, 100, spiral_alpha // 2), 
                           (trail_x, trail_y), (spiral_x, spiral_y), 2)
        
        # Обновляем позиции перьев
        for feather in feathers:
            feather['x'] += feather['vel_x']
            feather['y'] += feather['vel_y']
            feather['angle'] += feather['rotation_speed']  # Вращение
            # Замедление по мере падения
            if feather['y'] > cy - CELL_SIZE//2:
                feather['vel_y'] *= 0.93
                feather['alpha'] = max(60, feather['alpha'] - 8)
            else:
                feather['alpha'] = min(230, feather['alpha'] + 8)
        
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
        
        # Темное свечение от центра проклятия
        glow_alpha = int(100 * math.sin(t * math.pi))
        for glow_layer in range(4):
            glow_r = int(20 + glow_layer * 8)
            pygame.draw.circle(overlay, (60, 0, 60, glow_alpha // (glow_layer + 1)), 
                             (cx, cy), glow_r)
        
        # Искры проклятия разлетаются
        if t > 0.3:
            spark_t = (t - 0.3) / 0.7
            for k in range(12):
                spark_angle = k * (2 * math.pi / 12) + spark_t * 0.5
                spark_dist = int(10 + 30 * spark_t)
                spark_x = cx + int(spark_dist * math.cos(spark_angle))
                spark_y = cy + int(spark_dist * math.sin(spark_angle))
                spark_alpha = int(200 * (1 - spark_t))
                
                pygame.draw.circle(overlay, (150, 0, 150, spark_alpha), (spark_x, spark_y), 3)
                pygame.draw.circle(overlay, (200, 50, 200, spark_alpha), (spark_x, spark_y), 2)
        
        # Дополнительные перья, которые появляются сверху
        if i < 15 and i % 2 == 0:
            new_x = cx + (random.random() - 0.5) * 60
            new_y = cy - CELL_SIZE - 25 - random.random() * 40
            # Рисуем одно новое перо
            alpha = 200
            size = random.random() * 4 + 3
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
        
        # Темные дымные частицы поднимаются вверх
        for k in range(10):
            smoke_x = cx + random.randint(-20, 20)
            smoke_y = cy - int(10 * t) + random.randint(-10, 10)
            smoke_alpha = int(120 * (1 - t) * random.random())
            smoke_r = random.randint(2, 4)
            pygame.draw.circle(overlay, (40, 0, 40, smoke_alpha), (smoke_x, smoke_y), smoke_r)
        
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(20)

def animate_rune_shield_spell(screen, target_px, redraw_callback=None):
    # Руна щита: камень с зелёным руническим знаком (щит) и белыми частицами
    frames = 70  # Увеличено до 70 кадров для максимальной плавности
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
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_meteor_rain(screen, meteors, redraw_callback=None, explosion_sound_callback=None, flight_sound_callback=None):
    """Анимация метеоритного дождя - все метеориты падают одновременно с маленьким промежутком"""
    import pygame
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    # Подготовка данных для всех метеоритов
    meteor_data = []
    for idx, (start_px, end_px, delay_frames) in enumerate(meteors):
        meteor_data.append({
            'start': start_px,
            'end': end_px,
            'delay': delay_frames,
            'current_frame': -delay_frames,  # Отрицательное значение означает задержку
            'exploded': False
        })
    
    max_flight_frames = 60  # Увеличено до 60 кадров для максимальной плавности
    explode_frames = 80  # Увеличено до 80 кадров для максимальной плавности
    if not meteor_data:
        return  # Нет метеоритов для анимации
    max_delay = max(meteor['delay'] for meteor in meteor_data)
    max_total_frames = max_flight_frames + explode_frames + max_delay
    
    # Флаги для звуков (чтобы каждый звук проигрался один раз)
    flight_sounds_played = [False] * len(meteor_data)
    explosion_sounds_played = [False] * len(meteor_data)
    
    # Проигрываем все кадры анимации
    for global_frame in range(max_total_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Обрабатываем каждый метеорит
        for meteor_idx, meteor in enumerate(meteor_data):
            # Если метеорит еще в задержке
            if meteor['current_frame'] < 0:
                meteor['current_frame'] += 1
                continue
            
            frame = meteor['current_frame']
            
            # Этап полета
            if frame < max_flight_frames and not meteor['exploded']:
                # Проигрываем звук полета один раз
                if not flight_sounds_played[meteor_idx] and flight_sound_callback:
                    try:
                        flight_sound_callback()
                    except:
                        pass
                    flight_sounds_played[meteor_idx] = True
                
                t = frame / (max_flight_frames - 1) if max_flight_frames > 1 else 1.0
                ball_x = int(meteor['start'][0] * (1-t) + meteor['end'][0] * t)
                ball_y = int(meteor['start'][1] * (1-t) + meteor['end'][1] * t)
                
                dx = meteor['end'][0] - meteor['start'][0]
                dy = meteor['end'][1] - meteor['start'][1]
                angle = math.atan2(dy, dx)
                
                base_r = 12
                stone_r = base_r + int(3 * math.sin(t * 3))
                
                # Камень
                pygame.draw.circle(overlay, (60, 50, 45, 255), (ball_x, ball_y), stone_r)
                pygame.draw.circle(overlay, (90, 70, 60, 240), (ball_x, ball_y), int(stone_r*0.9))
                
                # Трещины
                for crack in range(4):
                    crack_angle = angle + crack * math.pi / 2
                    crack_x = ball_x + int(stone_r * 0.6 * math.cos(crack_angle))
                    crack_y = ball_y + int(stone_r * 0.6 * math.sin(crack_angle))
                    pygame.draw.line(overlay, (255, 180, 60, 220), (ball_x, ball_y), (crack_x, crack_y), 2)
                
                # Раскалённые края
                for edge in range(8):
                    edge_angle = edge * (2*math.pi / 8.0) + t
                    edge_x = ball_x + int(stone_r * 0.85 * math.cos(edge_angle))
                    edge_y = ball_y + int(stone_r * 0.85 * math.sin(edge_angle))
                    pygame.draw.circle(overlay, (255, 140, 40, 200), (edge_x, edge_y), 3)
                    pygame.draw.circle(overlay, (255, 220, 100, 150), (edge_x, edge_y), 2)
                
                # Огненный хвост
                tail_length = 35
                for j in range(15):
                    trail_t = j / 15.0
                    trail_x = ball_x - int(tail_length * trail_t * math.cos(angle))
                    trail_y = ball_y - int(tail_length * trail_t * math.sin(angle))
                    trail_r = max(2, int(base_r * (1 - trail_t * 0.9)))
                    tail_alpha = int(220 * (1 - trail_t * 0.7))
                    
                    if trail_t < 0.3:
                        color = (255, 150, 50, tail_alpha)
                    elif trail_t < 0.6:
                        color = (255, 120, 40, tail_alpha)
                    else:
                        color = (200, 80, 30, tail_alpha)
                    pygame.draw.circle(overlay, color, (trail_x, trail_y), trail_r)
                    
                    if j % 2 == 0:
                        for side in [-1, 1]:
                            spark_x = trail_x + int(5 * math.cos(angle + math.pi/2 + side * 0.3))
                            spark_y = trail_y + int(5 * math.sin(angle + math.pi/2 + side * 0.3))
                            pygame.draw.circle(overlay, (255, 220, 120, int(tail_alpha*0.6)), (spark_x, spark_y), 2)
                
                meteor['current_frame'] += 1
                
                # Переход к взрыву
                if frame >= max_flight_frames - 1:
                    meteor['exploded'] = True
                    meteor['explode_start_frame'] = global_frame
            
            # Этап взрыва
            elif meteor['exploded']:
                if not explosion_sounds_played[meteor_idx] and explosion_sound_callback:
                    try:
                        explosion_sound_callback()
                    except:
                        pass
                    explosion_sounds_played[meteor_idx] = True
                
                # Проверяем что explode_start_frame был установлен
                if 'explode_start_frame' not in meteor:
                    meteor['explode_start_frame'] = global_frame
                
                explode_frame = global_frame - meteor['explode_start_frame']
                if explode_frame < explode_frames:
                    ex_t = explode_frame / (explode_frames - 1) if explode_frames > 1 else 1.0
                    ex_x, ex_y = meteor['end']
                    
                    # Кольца взрыва
                    for k, radius in enumerate([20, 35, 55, 80, 110]):
                        alpha = int(max(0, 240 - int(280 * ex_t * (k+1) / 5)))
                        pygame.draw.circle(overlay, (255, 150, 50, alpha), (ex_x, ex_y), radius, 4)
                    
                    # Ядро взрыва
                    core_size = int(15 + 30 * (1 - ex_t))
                    pygame.draw.circle(overlay, (255, 220, 100, int(255 * (1 - ex_t * 0.5))), (ex_x, ex_y), core_size)
                    
                    # Искры
                    for k in range(24):
                        spark_angle = (k * (2*math.pi / 24.0)) + ex_t * 3
                        spark_dist = 20 + int(100 * ex_t)
                        spark_x = ex_x + int(spark_dist * math.cos(spark_angle))
                        spark_y = ex_y + int(spark_dist * math.sin(spark_angle))
                        spark_alpha = int(200 * (1 - ex_t))
                        pygame.draw.circle(overlay, (255, 140, 40, spark_alpha), (spark_x, spark_y), 4)
                        
                        if k % 3 == 0:
                            small_spark_x = spark_x + int(8 * math.cos(spark_angle + math.pi/4))
                            small_spark_y = spark_y + int(8 * math.sin(spark_angle + math.pi/4))
                            pygame.draw.circle(overlay, (255, 200, 100, int(spark_alpha*0.7)), (small_spark_x, small_spark_y), 2)
                    
                    # Дым
                    for k in range(12):
                        smoke_angle = (k * (2*math.pi / 12.0))
                        smoke_dist = int(50 * ex_t)
                        smoke_x = ex_x + int(smoke_dist * math.cos(smoke_angle))
                        smoke_y = ex_y + int(smoke_dist * math.sin(smoke_angle))
                        smoke_size = int(8 + 15 * ex_t)
                        pygame.draw.circle(overlay, (70, 55, 55, int(150*(1-ex_t*0.8))), (smoke_x, smoke_y), smoke_size)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(18)

def animate_chain_lightning(screen, caster, targets, redraw_callback=None):
    """Анимация цепной молнии - молния бьёт первую цель, затем отскакивает к остальным"""
    import random
    import math
    from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
    
    # Анимация для каждой цели по очереди
    for target_idx, target in enumerate(targets):
        if target.health <= 0:
            continue
        
        target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
        
        # Определяем начальную позицию молнии
        if target_idx == 0:
            # Первая молния сверху экрана к цели
            start_px = (target_px[0], 0)
        else:
            # Последующие молнии начинаются от предыдущей цели (отскок)
            prev_target = targets[target_idx - 1]
            start_px = (prev_target.x * CELL_SIZE + CELL_SIZE // 2, 
                       prev_target.y * CELL_SIZE + CELL_SIZE // 2)
        
        # Рисуем молнию от начальной позиции к цели
        for strike in range(2):  # 2 удара молнии на каждую цель
            pygame.event.pump()
            if redraw_callback:
                redraw_callback()
            
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            cx, cy = target_px
            start_x, start_y = start_px
            
            # Рисуем зигзагообразную молнию
            points = [(start_x, start_y)]
            current_y = start_y
            current_x = start_x
            
            # Для отскоков - рисуем молнию горизонтально или по направлению к цели
            if target_idx > 0:
                # Отскок - молния идёт от предыдущей цели к следующей
                steps = 10
                for step in range(steps + 1):
                    t = step / steps
                    x = int(start_x * (1 - t) + cx * t)
                    y = int(start_y * (1 - t) + cy * t)
                    # Добавляем случайные отклонения для зигзага
                    if step > 0 and step < steps:
                        x += random.randint(-8, 8)
                        y += random.randint(-5, 5)
                    points.append((x, y))
            else:
                # Первая молния - вертикально сверху вниз
                while current_y < cy:
                    offset = random.randint(-15, 15)
                    current_x += offset
                    current_y += random.randint(15, 30)
                    points.append((current_x, min(current_y, cy)))
            
            # Яркая молния
            if len(points) > 1:
                pygame.draw.lines(s, (255, 255, 255, 255), False, points, 4)
                pygame.draw.lines(s, (200, 200, 255, 200), False, points, 8)
                pygame.draw.lines(s, (150, 150, 255, 100), False, points, 12)
            
            # Вспышка в точке удара
            if target_idx == 0:
                # Первый удар - светящийся шар
                for i in range(3):
                    radius = 30 - i * 8
                    alpha = 255 - i * 60
                    pygame.draw.circle(s, (255, 255, 255, alpha), (cx, cy), radius)
            else:
                # Последующие удары - красивые искры вместо шара
                # Основные искры - больше и ярче
                for spark_idx in range(16):
                    spark_angle = (spark_idx * (2*math.pi / 16.0)) + random.uniform(-0.4, 0.4)
                    spark_dist = random.randint(12, 35)
                    spark_x = cx + int(spark_dist * math.cos(spark_angle))
                    spark_y = cy + int(spark_dist * math.sin(spark_angle))
                    spark_alpha = random.randint(200, 255)
                    
                    # Яркая центральная часть искры
                    spark_size = random.randint(3, 6)
                    pygame.draw.circle(s, (255, 255, 255, spark_alpha), (spark_x, spark_y), spark_size)
                    # Голубая оболочка
                    pygame.draw.circle(s, (180, 220, 255, int(spark_alpha*0.8)), (spark_x, spark_y), spark_size + 2)
                    # Внешнее свечение
                    pygame.draw.circle(s, (150, 200, 255, int(spark_alpha*0.5)), (spark_x, spark_y), spark_size + 4)
                    
                    # Дополнительные маленькие искры-хвосты
                    if spark_idx % 2 == 0:
                        tail_x = spark_x + int(8 * math.cos(spark_angle + math.pi))
                        tail_y = spark_y + int(8 * math.sin(spark_angle + math.pi))
                        pygame.draw.circle(s, (255, 255, 255, int(spark_alpha*0.9)), (tail_x, tail_y), 2)
                    # Боковые искры
                    if spark_idx % 4 == 0:
                        for side in [-1, 1]:
                            side_angle = spark_angle + side * 0.5
                            side_x = spark_x + int(6 * math.cos(side_angle))
                            side_y = spark_y + int(6 * math.sin(side_angle))
                            pygame.draw.circle(s, (220, 240, 255, int(spark_alpha*0.7)), (side_x, side_y), 2)
            
            screen.blit(s, (0, 0))
            pygame.display.flip()
            pygame.time.delay(12)  # Уменьшена задержка для плавности  # Ускорено с 50 до 30
            
            if strike < 1:
                pygame.event.pump()
                if redraw_callback:
                    redraw_callback()
                pygame.display.flip()
                pygame.time.delay(15)  # Ускорено с 30 до 15
        
        # Небольшая задержка перед следующим отскоком
        if target_idx < len(targets) - 1:
            pygame.event.pump()
            if redraw_callback:
                redraw_callback()
            pygame.display.flip()
            pygame.time.delay(20)  # Ускорено с 40 до 20

def animate_accuracy(screen, target_px, redraw_callback=None):
    """Анимация точности - появляется линза и монетка крутится два раза по вертикальной оси"""
    import random
    import math
    from .config import CELL_SIZE
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = target_px
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1)
        
        # Линза появляется (эллипс с градиентом)
        lens_alpha = int(200 * min(1.0, t * 2))  # Быстро появляется
        lens_w = int(40 + 20 * min(1.0, t * 2))
        lens_h = int(50 + 30 * min(1.0, t * 2))
        
        # Рисуем линзу (эллипс с эффектом стекла)
        lens_rect = pygame.Rect(cx - lens_w // 2, cy - lens_h // 2, lens_w, lens_h)
        
        # Внешний ободок
        pygame.draw.ellipse(overlay, (180, 220, 255, lens_alpha), lens_rect, 2)
        # Внутреннее стекло с градиентом
        for j in range(3):
            inner_rect = lens_rect.inflate(-j*4, -j*4)
            inner_alpha = int(lens_alpha * (1 - j * 0.3))
            pygame.draw.ellipse(overlay, (220, 240, 255, inner_alpha), inner_rect)
        
        # Монетка крутится два раза по вертикальной оси
        coin_rotations = 2  # Два оборота
        rotation_angle = (t * coin_rotations * 2 * math.pi) % (2 * math.pi)
        
        # Размер монетки меняется при вращении (эффект перспективы)
        coin_base_size = 8
        coin_size = int(coin_base_size * abs(math.cos(rotation_angle)))
        
        # Позиция монетки в центре линзы
        coin_y = cy
        
        # Рисуем монетку (круг, который становится линией при повороте на 90/270 градусов)
        if coin_size > 1:
            pygame.draw.circle(overlay, (255, 215, 0, 200), (cx, coin_y), coin_size)  # Золотая монетка
            pygame.draw.circle(overlay, (200, 150, 0, 200), (cx, coin_y), coin_size - 2)
        
        # Дополнительные блики на линзе
        if t > 0.3:
            for k in range(3):
                spark_x = cx + random.randint(-15, 15)
                spark_y = cy + random.randint(-15, 15)
                spark_alpha = int(150 * (1 - t) * random.random())
                pygame.draw.circle(overlay, (255, 255, 255, spark_alpha), (spark_x, spark_y), 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_rune_haste_spell(screen, target_px, redraw_callback=None):
    # Руна скорости: камень с белым руническим знаком (молния) и жёлтыми частицами
    frames = 70  # Увеличено до 70 кадров для максимальной плавности
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
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_fireball(screen, start_px, end_px, redraw_callback=None, explosion_sound_callback=None, flight_sound_callback=None):
    # Горящий камень летит к цели, затем взрыв после приземления
    flight_frames = 80  # Увеличено до 80 кадров для максимальной плавности
    # Воспроизводим звук полёта в начале анимации
    if flight_sound_callback:
        flight_sound_callback()
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
        pygame.time.delay(10)  # Уменьшена задержка для плавности
    
    # Этап 2: взрыв после приземления
    explode_frames = 80  # Увеличено до 80 кадров для максимальной плавности
    # Воспроизводим звук взрыва в начале этапа взрыва
    if explosion_sound_callback and callable(explosion_sound_callback):
        explosion_sound_callback()
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
        pygame.time.delay(12)  # Уменьшена задержка для плавности

def animate_raise_dead(screen, center_px, redraw_callback=None):
    # Рука вылазит из земли в центре клетки
    frames = 70  # Увеличено до 70 кадров для максимальной плавности
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
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_fire_explosion(screen, x, y):
    """Улучшенный взрыв с детальными огненными эффектами"""
    frames = 80  # Увеличено до 80 кадров для максимальной плавности  # Увеличено с 14 до 40 кадров
    for i in range(frames):
        pygame.event.pump()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1)
        
        # Множественные расходящиеся огненные кольца
        for ring in range(4):
            r = int(8 + (18 + ring * 8) * t)
            alpha = max(0, int((200 - ring * 30) * (1 - t)))
            # Внешнее кольцо - оранжевое
            pygame.draw.circle(overlay, (255, 140, 50, alpha), (x, y), r, 4)
            # Внутреннее кольцо - желтое
            if ring < 2:
                pygame.draw.circle(overlay, (255, 200, 80, min(255, alpha + 40)), (x, y), max(1, r - 3), 2)
        
        # Яркое белое ядро взрыва
        core_r = max(2, int(12 * (1 - t)))
        pygame.draw.circle(overlay, (255, 255, 255, int(255 * (1 - t * 0.7))), (x, y), core_r)
        pygame.draw.circle(overlay, (255, 240, 180, int(220 * (1 - t))), (x, y), core_r + 3)
        pygame.draw.circle(overlay, (255, 180, 100, int(180 * (1 - t))), (x, y), core_r + 6)
        
        # Множество разлетающихся искр
        for k in range(16):
            ang = (k * (2*math.pi / 16.0)) + t * 0.8 + k * 0.3
            # Искры разлетаются с разной скоростью
            base_dist = 8 + (k % 3) * 5
            dist = base_dist + int(30 * t)
            sx = x + int(dist * math.cos(ang))
            sy = y + int(dist * math.sin(ang))
            
            spark_alpha = int(220 * (1 - t * 0.9))
            spark_size = max(1, 4 - int(3 * t))
            
            # Градиент цвета искр
            if k % 3 == 0:
                color = (255, 220, 100, spark_alpha)  # Желтые
            elif k % 3 == 1:
                color = (255, 160, 60, spark_alpha)   # Оранжевые
            else:
                color = (255, 100, 40, spark_alpha)   # Красные
            
            pygame.draw.circle(overlay, color, (sx, sy), spark_size)
            
            # След за искрой
            if t < 0.6:
                trail_x = x + int((dist - 8) * math.cos(ang))
                trail_y = y + int((dist - 8) * math.sin(ang))
                pygame.draw.line(overlay, (*color[:3], spark_alpha // 2), 
                               (trail_x, trail_y), (sx, sy), 2)
        
        # Дополнительные мелкие искры между основными
        for k in range(24):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.randint(5, int(15 + 35 * t))
            sx = x + int(dist * math.cos(ang))
            sy = y + int(dist * math.sin(ang))
            alpha = int(random.randint(150, 220) * (1 - t))
            pygame.draw.circle(overlay, (255, 200, 120, alpha), (sx, sy), 1)
        
        # Огненное свечение вокруг взрыва
        glow_r = int(20 + 35 * t)
        pygame.draw.circle(overlay, (255, 140, 40, int(60 * (1 - t))), (x, y), glow_r)
        
        # Дым начинает появляться в конце
        if t > 0.5:
            smoke_t = (t - 0.5) / 0.5
            for k in range(8):
                smoke_ang = k * (2*math.pi / 8.0) + smoke_t * 0.5
                smoke_dist = int(15 + 25 * smoke_t)
                smoke_x = x + int(smoke_dist * math.cos(smoke_ang))
                smoke_y = y + int(smoke_dist * math.sin(smoke_ang)) - int(10 * smoke_t)
                smoke_r = int(5 + 8 * smoke_t)
                smoke_alpha = int(120 * (1 - smoke_t * 0.7))
                pygame.draw.circle(overlay, (60, 50, 45, smoke_alpha), (smoke_x, smoke_y), smoke_r)
        
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(22)

def animate_forget_spell(screen, start, end, redraw_callback=None):
    """Максимально насыщенная анимация заклинания Забвение с темно-фиолетовыми эффектами"""
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
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
    """Улучшенное Кольцо холода: детальная заморозка с ледяными кристаллами и туманом"""
    cx, cy = center
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames - 1)
        ring_px = pygame.Surface((CELL_SIZE*4, CELL_SIZE*4), pygame.SRCALPHA)
        ring_center = (CELL_SIZE*2, CELL_SIZE*2)
        
        # Морозное расширяющееся кольцо
        expand_r = int(CELL_SIZE * 1.5 * t)
        
        # Ледяной туман расползается от центра
        for fog_ring in range(5):
            fog_r = int((10 + fog_ring * 15) * t)
            fog_alpha = int(80 * (1 - fog_ring * 0.15) * (1 - t * 0.5))
            pygame.draw.circle(ring_px, (200, 230, 255, fog_alpha), ring_center, fog_r)
        
        # Множественные ледяные кольца
        for ring in range(4):
            ring_r = int(expand_r - ring * 8)
            if ring_r > 5:
                ring_alpha = int(180 - ring * 30)
                # Основное голубое кольцо
                pygame.draw.circle(ring_px, (180, 220, 255, ring_alpha), ring_center, ring_r, 3)
                # Белое свечение по краю
                pygame.draw.circle(ring_px, (230, 245, 255, min(255, ring_alpha + 40)), ring_center, ring_r, 1)
        
        # Ледяные трещины растут от центра
        num_cracks = 12
        for k in range(num_cracks):
            ang = k * (2*math.pi/num_cracks) + i*0.05
            crack_len = int(expand_r * 0.9)
            
            # Рисуем разветвляющуюся трещину
            for seg in range(4):
                seg_t = seg / 4.0
                if seg_t > t:
                    break
                    
                r1 = int(crack_len * seg_t)
                r2 = int(crack_len * min(1.0, seg_t + 0.25))
                
                x1 = int(ring_center[0] + r1 * math.cos(ang))
                y1 = int(ring_center[1] + r1 * math.sin(ang))
                x2 = int(ring_center[0] + r2 * math.cos(ang + random.uniform(-0.2, 0.2)))
                y2 = int(ring_center[1] + r2 * math.sin(ang + random.uniform(-0.2, 0.2)))
                
                crack_alpha = int(220 * (1 - seg_t * 0.5))
                pygame.draw.line(ring_px, (200, 230, 255, crack_alpha), (x1, y1), (x2, y2), 2)
                pygame.draw.line(ring_px, (240, 250, 255, crack_alpha), (x1, y1), (x2, y2), 1)
                
                # Боковые ответвления трещин
                if seg % 2 == 0:
                    for side in [-1, 1]:
                        branch_ang = ang + side * 0.5
                        branch_len = int((r2 - r1) * 0.6)
                        bx = int(x2 + branch_len * math.cos(branch_ang))
                        by = int(y2 + branch_len * math.sin(branch_ang))
                        pygame.draw.line(ring_px, (210, 235, 255, crack_alpha // 2), (x2, y2), (bx, by), 1)
        
        # Ледяные кристаллы появляются вдоль трещин
        if t > 0.3:
            crystal_t = (t - 0.3) / 0.7
            for k in range(num_cracks * 2):
                ang = k * (math.pi/num_cracks) + crystal_t * 0.3
                r = int(expand_r * random.uniform(0.4, 0.9))
                x = int(ring_center[0] + r * math.cos(ang))
                y = int(ring_center[1] + r * math.sin(ang))
                
                # Рисуем кристалл (ромб)
                size = random.randint(3, 6)
                crystal_alpha = int(230 * (1 - crystal_t * 0.5))
                
                crystal_points = [
                    (x, y - size),
                    (x + size//2, y),
                    (x, y + size),
                    (x - size//2, y)
                ]
                pygame.draw.polygon(ring_px, (220, 240, 255, crystal_alpha), crystal_points)
                pygame.draw.polygon(ring_px, (240, 250, 255, crystal_alpha), crystal_points, 1)
        
        # Ледяные искры разлетаются от центра
        for k in range(20):
            spark_ang = k * (2*math.pi/20) + t * 2
            spark_r = int(15 + 40 * t + random.randint(-5, 5))
            spark_x = int(ring_center[0] + spark_r * math.cos(spark_ang))
            spark_y = int(ring_center[1] + spark_r * math.sin(spark_ang))
            spark_alpha = int(200 * (1 - t * 0.8))
            
            pygame.draw.circle(ring_px, (220, 240, 255, spark_alpha), (spark_x, spark_y), 2)
            pygame.draw.circle(ring_px, (240, 250, 255, spark_alpha), (spark_x, spark_y), 1)
        
        # Центральная ледяная вспышка
        core_alpha = int(220 * (1 - t))
        pygame.draw.circle(ring_px, (240, 250, 255, core_alpha), ring_center, int(12 * (1 - t * 0.7)))
        pygame.draw.circle(ring_px, (200, 230, 255, core_alpha), ring_center, int(18 * (1 - t * 0.5)))
        
        # Применяем поверх
        screen.blit(ring_px, (cx - CELL_SIZE*2, cy - CELL_SIZE*2))
        pygame.display.flip()
        pygame.time.delay(26)

def animate_frost_impact(screen, center, redraw_callback=None):
    """Анимация морозного удара: ледяные шипы растут из земли и разбиваются"""
    cx, cy = center
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
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
    frames = 80  # Увеличено до 80 кадров для максимальной плавности  # Увеличено для плавности
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
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_slow_spell(screen, start, end, redraw_callback=None):
    """Замедление: густые шипастые лозы с тенями оплетают цель"""
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
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
        pygame.time.delay(12)  # Уменьшена задержка для плавности

def animate_slow_spell_fly(screen, start, end, redraw_callback=None):
    """Анимация полета заклинания Замедление"""
    frames = 30  # Увеличено для плавности
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
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_bless_spell(screen, start, end, redraw_callback=None):
    """Новая анимация Благословения: святой символ, золотой столп света,
    материализация кубка на краткий миг, поток святой воды и финальная вспышка."""
    frames = 60  # Увеличено для плавности
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
    frames = 30  # Увеличено для плавности
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
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_dispel_spell(screen, start, end, redraw_callback=None):
    """Детальная анимация заклинания Снятие чар с расходящимися волнами"""
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
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
        alpha = int(220 * (1 - abs(t - 0.5) * 2))
        
        # Расходящиеся волны
        for wave in range(5):
            wave_radius = 10 + wave * 8 + int(5 * math.sin(i * 0.3 + wave))
            wave_alpha = int(alpha * (1 - wave * 0.2))
            pygame.draw.circle(dispel_surface, (80, 140, 255, min(255, wave_alpha+40)), 
                             (center_x, center_y), wave_radius, 3)
        
        # Дополнительные волны
        for wave in range(3):
            wave_radius = 15 + wave * 12 + int(8 * math.sin(i * 0.4 + wave))
            wave_alpha = int(alpha * 0.6 * (1 - wave * 0.3))
            pygame.draw.circle(dispel_surface, (140, 200, 255, min(255, int(wave_alpha*0.9)+30)), 
                             (center_x, center_y), wave_radius, 2)
        
        # Центральная вспышка
        flash_alpha = min(255, int(alpha * 1.5))
        pygame.draw.circle(dispel_surface, (230, 240, 255, flash_alpha), 
                         (center_x, center_y), 8)
        pygame.draw.circle(dispel_surface, (255, 255, 255, flash_alpha), 
                         (center_x, center_y), 4)
        
        # Частицы очищения
        for j in range(15):
            angle = j * 0.419 + i * 0.4  # вращение
            radius = 20 + random.randint(-8, 8)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = min(255, int(alpha * 0.95))
            pygame.draw.circle(dispel_surface, (180, 220, 255, particle_alpha), 
                             (particle_x, particle_y), 3)
        
        # Дополнительные светящиеся частицы
        for j in range(10):
            particle_x = center_x + random.randint(-25, 25)
            particle_y = center_y + random.randint(-25, 25)
            particle_alpha = min(255, int(alpha * 0.8))
            pygame.draw.circle(dispel_surface, (220, 240, 255, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Эффект пульсации волн
        pulse1 = int(6 * math.sin(i * 0.5))
        pulse2 = int(4 * math.sin(i * 0.7 + 1))
        pulse3 = int(3 * math.sin(i * 0.9 + 2))
        
        pygame.draw.circle(dispel_surface, (90, 150, 255, min(255, alpha//3 + 30)), 
                         (center_x, center_y), 30 + pulse1)
        pygame.draw.circle(dispel_surface, (120, 180, 255, min(255, alpha//4 + 20)), 
                         (center_x, center_y), 40 + pulse2)
        pygame.draw.circle(dispel_surface, (150, 200, 255, min(255, alpha//5 + 10)), 
                         (center_x, center_y), 50 + pulse3)
        
        # Световые лучи очищения
        for j in range(8):
            angle = j * math.pi / 4 + i * 0.3
            ray_length = 30 + int(8 * math.sin(i * 0.4 + j))
            ray_x = center_x + int(ray_length * math.cos(angle))
            ray_y = center_y + int(ray_length * math.sin(angle))
            pygame.draw.line(dispel_surface, (200, 230, 255, min(255, alpha//2 + 40)), 
                           (center_x, center_y), (ray_x, ray_y), 3)
        
        # Эффект искр очищения
        for j in range(12):
            spark_x = center_x + random.randint(-30, 30)
            spark_y = center_y + random.randint(-30, 30)
            spark_alpha = min(255, int(alpha * 0.9))
            pygame.draw.circle(dispel_surface, (255, 255, 255, spark_alpha), 
                             (spark_x, spark_y), 1)
        
        # Применяем эффект к экрану
        screen.blit(dispel_surface, (x - CELL_SIZE*2, y - CELL_SIZE*2))
        
        pygame.display.flip()
        pygame.time.delay(12)  # Уменьшена задержка для плавности

def animate_stone_skin(screen, target_pos, redraw_callback=None):
    """Плитки-кирпичики поднимаются снизу, собираются вокруг юнита и потом рассыпаются."""
    x, y = target_pos
    cx, cy = x, y
    frames = 60  # Увеличено для плавности
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
    frames = 30  # Увеличено для плавности
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
        pygame.draw.circle(wave_surface, (230, 240, 255), (center_x, center_y), 6)
        pygame.draw.circle(wave_surface, (255, 255, 255), (center_x, center_y), 3)
        
        # Волны вокруг центра
        for j in range(3):
            wave_radius = 4 + j * 2
            pygame.draw.circle(wave_surface, (180, 220, 255, 200), 
                             (center_x, center_y), wave_radius, 2)
        
        # Частицы очищения
        for j in range(6):
            angle = j * 1.047 + i * 0.5
            particle_x = center_x + int(8 * math.cos(angle))
            particle_y = center_y + int(8 * math.sin(angle))
            pygame.draw.circle(wave_surface, (220, 240, 255, 220), 
                             (particle_x, particle_y), 2)
        
        # Применяем к экрану
        screen.blit(wave_surface, (x - 12, y - 12))
        
        pygame.display.flip()
        pygame.time.delay(10)  # Уменьшена задержка для плавности

# Улучшенная анимация: ускорение воздуха с детальными эффектами ветра
def animate_air_haste_spell(screen, start, end, redraw_callback=None):
    """Улучшенное ускорение с мощными потоками ветра и воздушными эффектами"""
    frames = 110  # Увеличено до 110 кадров для максимальной плавности
    tx, ty = end
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames - 1)
        layer = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        cx, cy = CELL_SIZE*1.5, CELL_SIZE*1.5
        
        # Мощные вихри ветра, закручивающиеся вокруг цели
        for vortex in range(3):
            vortex_phase = t * 4 + vortex * (2 * math.pi / 3)
            vortex_r = int(30 + vortex * 8 + 8 * math.sin(vortex_phase))
            vortex_alpha = int(180 - vortex * 40)
            
            # Основной вихрь
            for arc_seg in range(6):
                arc_start = vortex_phase + arc_seg * (math.pi / 3)
                arc_end = arc_start + (math.pi / 4)
                pygame.draw.arc(layer, (180, 230, 255, vortex_alpha), 
                              (cx - vortex_r, cy - vortex_r, vortex_r * 2, vortex_r * 2),
                              arc_start, arc_end, 4)
                pygame.draw.arc(layer, (220, 245, 255, vortex_alpha), 
                              (cx - vortex_r + 2, cy - vortex_r + 2, vortex_r * 2 - 4, vortex_r * 2 - 4),
                              arc_start, arc_end, 2)
        
        # Быстрые линии потока ветра (более детализированные)
        for k in range(20):
            ang = 2 * math.pi * (k / 20.0) + t * 3.5
            r1 = int(CELL_SIZE * 0.7)
            r2 = r1 + 15 + int(10 * math.sin(t * 4 + k * 0.3))
            x1 = cx + int(r1 * math.cos(ang))
            y1 = cy + int(r1 * math.sin(ang))
            x2 = cx + int(r2 * math.cos(ang + 0.35))
            y2 = cy + int(r2 * math.sin(ang + 0.35))
            
            # Градиент линий
            stream_alpha = int(160 - abs(k % 10 - 5) * 15)
            pygame.draw.line(layer, (160, 215, 255, stream_alpha), (x1, y1), (x2, y2), 3)
            pygame.draw.line(layer, (200, 235, 255, stream_alpha), (x1, y1), (x2, y2), 1)
            
            # Искры ветра на концах линий
            pygame.draw.circle(layer, (220, 240, 255, stream_alpha), (x2, y2), 2)
        
        # Воздушные частицы, кружащиеся вокруг
        for particle in range(30):
            particle_ang = (particle * 2 * math.pi / 30) + t * 5
            particle_r = int(20 + 25 * math.sin(t * 2 + particle * 0.2))
            particle_x = cx + int(particle_r * math.cos(particle_ang))
            particle_y = cy + int(particle_r * math.sin(particle_ang))
            particle_alpha = int(200 * (0.7 + 0.3 * math.sin(t * 3 + particle)))
            
            pygame.draw.circle(layer, (200, 230, 255, particle_alpha), (particle_x, particle_y), 3)
            pygame.draw.circle(layer, (240, 250, 255, particle_alpha), (particle_x, particle_y), 2)
        
        # Пульсирующие кольца ускорения
        for ring in range(4):
            pulse_r = int(12 + ring * 6 + 8 * math.sin(t * 6 + ring * 0.5))
            ring_alpha = int(120 - ring * 25)
            pygame.draw.circle(layer, (180, 220, 255, ring_alpha), (cx, cy), pulse_r, 2)
        
        # Центральное яркое свечение
        core_alpha = int(180 * (0.6 + 0.4 * math.sin(t * 8)))
        pygame.draw.circle(layer, (220, 240, 255, core_alpha), (cx, cy), 8)
        pygame.draw.circle(layer, (240, 250, 255, core_alpha), (cx, cy), 5)
        
        # Спиральные потоки воздуха
        for spiral in range(2):
            spiral_dir = 1 if spiral == 0 else -1
            for j in range(15):
                spiral_t = j / 15.0
                spiral_ang = (spiral_t * 4 * math.pi + t * 6) * spiral_dir
                spiral_r = int(10 + spiral_t * 40)
                spiral_x = cx + int(spiral_r * math.cos(spiral_ang))
                spiral_y = cy + int(spiral_r * math.sin(spiral_ang))
                spiral_alpha = int(150 * (1 - spiral_t * 0.7))
                
                pygame.draw.circle(layer, (190, 225, 255, spiral_alpha), (spiral_x, spiral_y), 2)
        
        screen.blit(layer, (tx - CELL_SIZE*1.5, ty - CELL_SIZE*1.5))
        pygame.display.flip()
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_rune_shield_spell(screen, start, end, redraw_callback=None):
    """Анимация руны защиты: насыщенный глиф над целью с мерцанием и исчезновением"""
    frames = 110  # Увеличено до 110 кадров для максимальной плавности
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
        pygame.time.delay(12)  # Уменьшена задержка для плавности

def animate_rune_haste_spell(screen, start, end, redraw_callback=None):
    """Анимация руны скорости: насыщенный глиф над целью с мерцанием и исчезновением"""
    frames = 110  # Увеличено до 110 кадров для максимальной плавности
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
        pygame.time.delay(12)  # Уменьшена задержка для плавности 

def animate_rune_magic_spell(screen, start, end, redraw_callback=None):
    """Анимация руны магии: фиолетовый магический глиф над целью"""
    import random
    import math
    from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 110  # Увеличено до 110 кадров для максимальной плавности
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Позиция над целью
        x = int(end[0])
        y = int(end[1] - CELL_SIZE * 0.7)
        top_margin = int(CELL_SIZE * 0.5)
        bottom_margin = int(CELL_SIZE * 0.5)
        ui_panel = 80
        y = max(top_margin, min(SCREEN_HEIGHT - ui_panel - bottom_margin, y))
        
        # Создаем эффект руны магии
        rune_surface = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*1.5, CELL_SIZE*1.5
        
        # Основной эффект руны
        t = i / (frames-1)
        base_alpha = int(220 * (1 - abs(t - 0.5) * 2))
        base_alpha = max(0, min(255, base_alpha))
        flicker = 0.75 + 0.25 * (math.sin(i * 0.8) + 1) / 2
        alpha = int(base_alpha * flicker)
        
        # Фаза появления (первые 8 кадров)
        if i < 8:
            appear_alpha = int(alpha * (i / 8))
            
            # Многоуровневая аура (фиолетово-магическая)
            pygame.draw.circle(rune_surface, (180, 100, 255, appear_alpha//3), (center_x, center_y), 36)
            pygame.draw.circle(rune_surface, (200, 120, 255, appear_alpha//2), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (220, 140, 255, appear_alpha//1), (center_x, center_y), 24)
            
            # Внешнее свечение
            pygame.draw.circle(rune_surface, (240, 160, 255, appear_alpha//2), (center_x, center_y), 18)
            
            # Центральный камень
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (160, 100, 200, appear_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (120, 60, 150, appear_alpha), stone_rect.inflate(-6, -6), 2)
            
            # Глиф магии: круг с магическими символами
            pygame.draw.circle(rune_surface, (255, 200, 255, appear_alpha), (center_x, center_y), 16, 3)
            # Звездочка магии
            for j in range(8):
                angle = j * (math.pi / 4)
                px = center_x + int(10 * math.cos(angle))
                py = center_y + int(10 * math.sin(angle))
                pygame.draw.circle(rune_surface, (255, 255, 255, appear_alpha), (px, py), 2)
        
        # Фаза мерцания (кадры 8-17)
        elif i < 17:
            flicker_alpha = alpha
            
            # Многоуровневая аура
            pygame.draw.circle(rune_surface, (180, 100, 255, flicker_alpha//4), (center_x, center_y), 38)
            pygame.draw.circle(rune_surface, (200, 120, 255, flicker_alpha//3), (center_x, center_y), 32)
            pygame.draw.circle(rune_surface, (220, 140, 255, flicker_alpha//2), (center_x, center_y), 26)
            
            # Пульсирующее свечение
            pulse = int(3 * math.sin(i * 0.9))
            pygame.draw.circle(rune_surface, (240, 160, 255, flicker_alpha//2), (center_x, center_y), 18 + pulse)
            
            # Центральный камень
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (160, 100, 200, flicker_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (120, 60, 150, flicker_alpha), stone_rect.inflate(-6, -6), 2)
            
            # Глиф магии (ярче)
            pygame.draw.circle(rune_surface, (255, 220, 255, flicker_alpha), (center_x, center_y), 16, 3)
            # Вращающаяся звездочка магии
            for j in range(8):
                angle = j * (math.pi / 4) + i * 0.15
                px = center_x + int(10 * math.cos(angle))
                py = center_y + int(10 * math.sin(angle))
                pygame.draw.circle(rune_surface, (255, 255, 255, flicker_alpha), (px, py), 2)
            
            # Вращающееся кольцо рун
            for j in range(6):
                a = j * (math.pi/3) + i * 0.15
                rx = center_x + int(12 * math.cos(a))
                ry = center_y + int(12 * math.sin(a))
                pygame.draw.circle(rune_surface, (255, 200, 255, flicker_alpha), (rx, ry), 2)
        
        # Фаза исчезновения (последние 8 кадров)
        else:
            tail = 8
            disappear_ratio = max(0.0, min(1.0, (frames - 1 - i) / tail))
            disappear_alpha = int(alpha * disappear_ratio)
            
            # Исчезающая аура и глиф
            pygame.draw.circle(rune_surface, (200, 120, 255, disappear_alpha//3), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (220, 140, 255, disappear_alpha//2), (center_x, center_y), 22)
            pygame.draw.circle(rune_surface, (255, 200, 255, disappear_alpha), (center_x, center_y), 16, 2)
            
            # Камень и звездочка при исчезновении
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (160, 100, 200, disappear_alpha), stone_rect)
            for j in range(8):
                angle = j * (math.pi / 4)
                px = center_x + int(10 * math.cos(angle))
                py = center_y + int(10 * math.sin(angle))
                pygame.draw.circle(rune_surface, (255, 255, 255, disappear_alpha), (px, py), 2)
        
        # Эффект пульсации
        pulse = int(5 * math.sin(i * 0.5))
        pygame.draw.circle(rune_surface, (200, 120, 255, alpha//4), 
                         (center_x, center_y), 25 + pulse)
        
        # Частицы магии
        for j in range(8):
            angle = j * 0.785 + i * 0.3
            radius = 15 + random.randint(-5, 5)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.6)
            pygame.draw.circle(rune_surface, (240, 160, 255, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Применяем эффект к экрану
        screen.blit(rune_surface, (x - CELL_SIZE*1.5, y - CELL_SIZE*1.5))
        
        pygame.display.flip()
        pygame.time.delay(12)  # Уменьшена задержка для плавности

def animate_rune_berserker_spell(screen, start, end, redraw_callback=None):
    """Простая анимация руны берсерка: красное свечение прямо на юните (без полета снаряда)"""
    import random
    import math
    from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
    
    # Игнорируем start - анимация проигрывается сразу на цели (end)
    frames = 90  # Увеличено до 90 кадров для максимальной плавности
    cx, cy = int(end[0]), int(end[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Создаем поверхность для эффекта
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Плавное появление и исчезновение
        t = i / (frames - 1)
        if t < 0.3:
            alpha = int(255 * (t / 0.3))
        elif t > 0.7:
            alpha = int(255 * ((1 - t) / 0.3))
        else:
            alpha = 255
        
        # Пульсирующее красное свечение вокруг юнита
        pulse = int(5 * math.sin(i * 0.8))
        radius = 20 + pulse
        
        # Внешнее свечение
        pygame.draw.circle(overlay, (255, 60, 60, alpha // 3), (cx, cy), radius + 8)
        # Среднее свечение
        pygame.draw.circle(overlay, (255, 80, 40, alpha // 2), (cx, cy), radius + 4)
        # Внутреннее яркое свечение
        pygame.draw.circle(overlay, (255, 100, 20, alpha), (cx, cy), radius)
        
        # Вращающиеся частицы ярости
        for j in range(6):
            angle = j * (math.pi / 3) + i * 0.5
            px = cx + int(radius * 0.6 * math.cos(angle))
            py = cy + int(radius * 0.6 * math.sin(angle))
            pygame.draw.circle(overlay, (255, 150, 50, alpha), (px, py), 3)
        
        # Применяем эффект к экрану
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_luck_horseshoe(screen, unit_pos, redraw_callback=None):
    """Анимация подковы при срабатывании удачи - подкова крутится по вертикальной оси над юнитом"""
    import math
    from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 30
    cx, cy = int(unit_pos[0]), int(unit_pos[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Создаем поверхность для эффекта
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Плавное появление и исчезновение
        t = i / (frames - 1)
        if t < 0.2:
            alpha = int(255 * (t / 0.2))
        elif t > 0.7:
            alpha = int(255 * ((1 - t) / 0.3))
        else:
            alpha = 255
        
        # Позиция подковы над юнитом (выше на 30-50 пикселей)
        horseshoe_y = cy - 40 - int(10 * math.sin(i * 0.3))  # Небольшое покачивание вверх-вниз
        horseshoe_x = cx
        
        # Вращение подковы по вертикальной оси (от 0 до 360 градусов)
        rotation_angle = (i * 360 / frames) * (math.pi / 180)  # В радианах
        
        # Размер подковы
        horseshoe_size = 40
        horseshoe_thickness = 4
        
        # Рисуем подкову (форма подковы с вращением)
        # Подкова состоит из дуги и двух "ножек"
        # При вращении по вертикальной оси она выглядит как эллипс, который меняет ширину
        
        # Вычисляем ширину эллипса в зависимости от угла вращения
        # Когда подкова повернута на 90 градусов - она видна сбоку (узкая)
        # Когда на 0/180 градусов - видна спереди (широкая)
        ellipse_width = int(horseshoe_size * abs(math.cos(rotation_angle)))
        ellipse_height = horseshoe_size
        
        # Цвет подковы (золотой/бронзовый)
        horseshoe_color = (255, 215, 0, alpha)  # Золотой
        glow_color = (255, 255, 200, alpha // 2)  # Свечение
        
        # Внешнее свечение
        pygame.draw.ellipse(overlay, glow_color, 
                          (horseshoe_x - ellipse_width//2 - 5, horseshoe_y - ellipse_height//2 - 5,
                           ellipse_width + 10, ellipse_height + 10), 2)
        
        # Основная подкова (дуга сверху)
        if ellipse_width > 5:  # Рисуем только если подкова видна
            # Верхняя дуга подковы
            pygame.draw.arc(overlay, horseshoe_color,
                          (horseshoe_x - ellipse_width//2, horseshoe_y - ellipse_height//2,
                           ellipse_width, ellipse_height),
                          math.pi * 0.2, math.pi * 0.8, horseshoe_thickness)
            
            # Левая "ножка" подковы
            left_leg_x = horseshoe_x - ellipse_width//2
            left_leg_y1 = horseshoe_y + int(ellipse_height * 0.3)
            left_leg_y2 = horseshoe_y + int(ellipse_height * 0.6)
            pygame.draw.line(overlay, horseshoe_color,
                           (left_leg_x, left_leg_y1), (left_leg_x, left_leg_y2), horseshoe_thickness)
            
            # Правая "ножка" подковы
            right_leg_x = horseshoe_x + ellipse_width//2
            right_leg_y1 = horseshoe_y + int(ellipse_height * 0.3)
            right_leg_y2 = horseshoe_y + int(ellipse_height * 0.6)
            pygame.draw.line(overlay, horseshoe_color,
                           (right_leg_x, right_leg_y1), (right_leg_x, right_leg_y2), horseshoe_thickness)
        
        # Звездочки удачи вокруг подковы
        for star_idx in range(6):
            star_angle = (star_idx * 2 * math.pi / 6) + i * 0.3
            star_radius = 25
            star_x = cx + int(star_radius * math.cos(star_angle))
            star_y = cy - 40 + int(star_radius * 0.5 * math.sin(star_angle))
            star_alpha = int(alpha * (0.6 + 0.4 * math.sin(i * 0.5 + star_idx)))
            pygame.draw.circle(overlay, (255, 255, 200, star_alpha), (star_x, star_y), 3)
        
        # Применяем эффект к экрану
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)

def animate_combat_spirit_bird(screen, unit_pos, redraw_callback=None):
    """Анимация золотой птицы при срабатывании боевого духа - птица поднимает крылья"""
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = int(unit_pos[0]), int(unit_pos[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Создаем поверхность для эффекта
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Плавное появление и исчезновение
        t = i / (frames - 1)
        if t < 0.15:
            alpha = int(255 * (t / 0.15))
        elif t > 0.75:
            alpha = int(255 * ((1 - t) / 0.25))
        else:
            alpha = 255
        
        # Позиция птицы над юнитом (выше на 50-60 пикселей)
        bird_y = cy - 55 - int(8 * math.sin(i * 0.2))  # Покачивание вверх-вниз
        bird_x = cx
        
        # Анимация крыльев: от поднятых (0) до опущенных (1) и обратно
        wing_cycle = (i % 20) / 20.0  # Цикл каждые 20 кадров
        if wing_cycle < 0.5:
            # Крылья поднимаются (0 -> 0.5)
            wing_angle = math.pi * (1 - wing_cycle * 2)  # От π до 0
        else:
            # Крылья опускаются (0.5 -> 1.0)
            wing_angle = math.pi * ((wing_cycle - 0.5) * 2)  # От 0 до π
        
        # Размер птицы
        bird_size = 35
        body_size = 12
        
        # Цвета (золотой)
        bird_color = (255, 215, 0, alpha)  # Золотой
        glow_color = (255, 255, 180, alpha // 3)  # Свечение
        body_color = (255, 200, 50, alpha)  # Более темное золото для тела
        
        # Внешнее свечение
        glow_radius = bird_size + 8
        pygame.draw.circle(overlay, glow_color, (bird_x, bird_y), glow_radius)
        
        # Тело птицы (эллипс)
        body_rect = pygame.Rect(bird_x - body_size//2, bird_y - body_size//2, 
                               body_size, body_size)
        pygame.draw.ellipse(overlay, body_color, body_rect)
        
        # Голова птицы (маленький круг)
        head_radius = 5
        head_x = bird_x + body_size // 3
        head_y = bird_y - body_size // 3
        pygame.draw.circle(overlay, body_color, (head_x, head_y), head_radius)
        
        # Клюв (маленький треугольник)
        beak_points = [
            (head_x + head_radius, head_y),
            (head_x + head_radius + 4, head_y - 2),
            (head_x + head_radius + 4, head_y + 2)
        ]
        pygame.draw.polygon(overlay, (255, 180, 0, alpha), beak_points)
        
        # Крылья (поднимаются и опускаются)
        wing_length = 18
        wing_width = 8
        
        # Левое крыло
        left_wing_base_x = bird_x - body_size // 2
        left_wing_base_y = bird_y
        left_wing_end_x = left_wing_base_x + int(wing_length * math.cos(wing_angle))
        left_wing_end_y = left_wing_base_y - int(wing_length * math.sin(wing_angle))
        # Рисуем крыло как эллипс
        left_wing_center_x = (left_wing_base_x + left_wing_end_x) // 2
        left_wing_center_y = (left_wing_base_y + left_wing_end_y) // 2
        wing_rect = pygame.Rect(left_wing_center_x - wing_width//2, 
                               left_wing_center_y - wing_length//2,
                               wing_width, wing_length)
        # Поворачиваем крыло (упрощенная версия - просто рисуем линию с расширением)
        pygame.draw.line(overlay, bird_color, 
                        (left_wing_base_x, left_wing_base_y),
                        (left_wing_end_x, left_wing_end_y), 6)
        
        # Правое крыло
        right_wing_base_x = bird_x + body_size // 2
        right_wing_base_y = bird_y
        right_wing_end_x = right_wing_base_x - int(wing_length * math.cos(wing_angle))
        right_wing_end_y = right_wing_base_y - int(wing_length * math.sin(wing_angle))
        pygame.draw.line(overlay, bird_color,
                        (right_wing_base_x, right_wing_base_y),
                        (right_wing_end_x, right_wing_end_y), 6)
        
        # Хвост (небольшой веер)
        tail_base_x = bird_x - body_size // 2
        tail_base_y = bird_y + body_size // 2
        for tail_idx in range(3):
            tail_angle = math.pi * 0.3 + tail_idx * 0.2
            tail_length = 10
            tail_end_x = tail_base_x - int(tail_length * math.cos(tail_angle))
            tail_end_y = tail_base_y + int(tail_length * math.sin(tail_angle))
            pygame.draw.line(overlay, bird_color,
                           (tail_base_x, tail_base_y),
                           (tail_end_x, tail_end_y), 3)
        
        # Золотые частицы вокруг птицы
        for particle_idx in range(8):
            particle_angle = (particle_idx * 2 * math.pi / 8) + i * 0.4
            particle_radius = 30 + int(10 * math.sin(i * 0.3 + particle_idx))
            particle_x = cx + int(particle_radius * math.cos(particle_angle))
            particle_y = cy - 55 + int(particle_radius * 0.6 * math.sin(particle_angle))
            particle_alpha = int(alpha * (0.5 + 0.5 * math.sin(i * 0.4 + particle_idx)))
            pygame.draw.circle(overlay, (255, 255, 150, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Применяем эффект к экрану
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_spell_reflection(screen, target_px, caster_px, redraw_callback=None):
    """Анимация предотвращения заклинания - поток маны прилетает к щиту рядом с юнитом и отталкивается"""
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = target_px
    
    # Определяем позицию щита рядом с юнитом (не в центр юнита)
    # Если есть кастер, щит будет на стороне от кастера
    if caster_px:
        # Вычисляем направление от кастера к цели
        dx = cx - caster_px[0]
        dy = cy - caster_px[1]
        dist = math.sqrt(dx*dx + dy*dy) if (dx*dx + dy*dy) > 0 else 1
        # Позиция щита рядом с юнитом, на пути от кастера
        shield_offset = 25  # Смещение от центра юнита
        shield_x = cx - int((dx / dist) * shield_offset)
        shield_y = cy - int((dy / dist) * shield_offset)
    else:
        # Если кастера нет, щит справа от юнита
        shield_x = cx + 20
        shield_y = cy
    
    # Позиция, откуда прилетает поток маны (дальше от кастера, если есть)
    if caster_px:
        # Поток маны прилетает с направления кастера, но к позиции рядом с юнитом
        start_offset = 60
        start_x = shield_x - int((dx / dist) * start_offset) if dist > 0 else shield_x - start_offset
        start_y = shield_y - int((dy / dist) * start_offset) if dist > 0 else shield_y
    else:
        start_x = shield_x - 50
        start_y = shield_y
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        
        # Щит появляется и растёт (рядом с юнитом)
        if t < 0.3:
            shield_alpha = int(220 * (t / 0.3))
            shield_size = int(25 * (t / 0.3))
        else:
            shield_alpha = 220
            shield_size = 25
        
        # Рисуем щит рядом с юнитом (круг с магическим свечением)
        pygame.draw.circle(overlay, (150, 200, 255, shield_alpha), (shield_x, shield_y), shield_size)
        pygame.draw.circle(overlay, (200, 230, 255, int(shield_alpha*0.8)), (shield_x, shield_y), shield_size + 4, 2)
        pygame.draw.circle(overlay, (100, 150, 255, int(shield_alpha*0.6)), (shield_x, shield_y), shield_size + 8, 2)
        
        # Поток маны летит к щиту
        if t < 0.5:
            mana_t = t / 0.5
            mana_x = int(start_x * (1 - mana_t) + shield_x * mana_t)
            mana_y = int(start_y * (1 - mana_t) + shield_y * mana_t)
            
            # Магический поток (не шар, а поток энергии)
            for j in range(4):
                mana_size = 10 - j * 2
                mana_alpha = int(200 * (1 - j * 0.2) * (1 - mana_t * 0.3))
                pygame.draw.circle(overlay, (100, 150, 255, mana_alpha), (mana_x, mana_y), mana_size)
            
            # След потока маны
            for k in range(6):
                trail_t = mana_t - k * 0.08
                if trail_t > 0:
                    trail_x = int(start_x * (1 - trail_t) + shield_x * trail_t)
                    trail_y = int(start_y * (1 - trail_t) + shield_y * trail_t)
                    trail_alpha = int(120 * (1 - trail_t))
                    trail_size = 6 - k
                    if trail_size > 0:
                        pygame.draw.circle(overlay, (150, 200, 255, trail_alpha), (trail_x, trail_y), trail_size)
        
        # Поток отталкивается от щита (рассеивается в стороны)
        if t > 0.5:
            bounce_t = (t - 0.5) / 0.5
            # Вычисляем направление от кастера для определения угла отскока
            if caster_px:
                angle_to_caster = math.atan2(dy, dx) if dist > 0 else 0
            else:
                angle_to_caster = 0
            
            # Поток рассеивается в стороны от щита
            for particle_idx in range(8):
                # Частицы разлетаются в разные стороны
                particle_angle = (particle_idx * (2*math.pi / 8.0)) + angle_to_caster + math.pi/2
                particle_dist = int(30 * bounce_t)
                particle_x = shield_x + int(particle_dist * math.cos(particle_angle))
                particle_y = shield_y + int(particle_dist * math.sin(particle_angle))
                
                particle_size = int(6 * (1 - bounce_t))
                particle_alpha = int(180 * (1 - bounce_t))
                if particle_size > 0:
                    pygame.draw.circle(overlay, (150, 200, 255, particle_alpha), (particle_x, particle_y), particle_size)
                    pygame.draw.circle(overlay, (200, 230, 255, int(particle_alpha*0.7)), (particle_x, particle_y), particle_size + 2, 1)
        
        # Искры при столкновении со щитом
        if 0.45 < t < 0.7:
            spark_t = (t - 0.45) / 0.25
            for spark_idx in range(16):
                spark_angle = (spark_idx * (2*math.pi / 16.0)) + random.uniform(-0.3, 0.3)
                spark_dist = int(25 * spark_t)
                spark_x = shield_x + int(spark_dist * math.cos(spark_angle))
                spark_y = shield_y + int(spark_dist * math.sin(spark_angle))
                spark_alpha = int(220 * (1 - spark_t))
                spark_size = random.randint(2, 4)
                pygame.draw.circle(overlay, (255, 255, 255, spark_alpha), (spark_x, spark_y), spark_size)
                pygame.draw.circle(overlay, (200, 230, 255, int(spark_alpha*0.8)), (spark_x, spark_y), spark_size + 1, 1)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)

def animate_quicksand_cast(screen, center_px, redraw_callback=None):
    """Анимация каста зыбучих песков - земля трясётся, появляются трещины"""
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 90  # Увеличено до 90 кадров для максимальной плавности
    cx, cy = center_px
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        
        # Земля трясётся
        shake_intensity = int(3 * (1 - t))
        shake_x = random.randint(-shake_intensity, shake_intensity) if shake_intensity > 0 else 0
        shake_y = random.randint(-shake_intensity, shake_intensity) if shake_intensity > 0 else 0
        
        # Трещины появляются
        for crack_idx in range(8):
            crack_angle = (crack_idx * (2*math.pi / 8.0))
            crack_length = int(30 * t)
            crack_start_x = cx + shake_x
            crack_start_y = cy + shake_y
            crack_end_x = crack_start_x + int(crack_length * math.cos(crack_angle))
            crack_end_y = crack_start_y + int(crack_length * math.sin(crack_angle))
            crack_alpha = int(150 * t)
            pygame.draw.line(overlay, (60, 45, 30, crack_alpha), (crack_start_x, crack_start_y), (crack_end_x, crack_end_y), 2)
        
        # Частицы грязи поднимаются
        for particle_idx in range(12):
            particle_angle = (particle_idx * (2*math.pi / 12.0))
            particle_dist = int(20 * t)
            particle_height = int(15 * t * (1 - t))
            particle_x = cx + shake_x + int(particle_dist * math.cos(particle_angle))
            particle_y = cy + shake_y - particle_height
            particle_size = random.randint(2, 4)
            particle_alpha = int(180 * t * (1 - t * 0.5))
            pygame.draw.circle(overlay, (80, 60, 40, particle_alpha), (particle_x, particle_y), particle_size)
        
        # Коричневое свечение
        if t > 0.3:
            glow_alpha = int(100 * (t - 0.3) / 0.7)
            pygame.draw.circle(overlay, (100, 75, 50, glow_alpha), (cx + shake_x, cy + shake_y), int(40 * t))
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_quicksand_creation(screen, quicksand_positions, redraw_callback=None):
    """Анимация создания зыбучих песков - появляются бурлящие лужи грязи"""
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        
        for qx, qy in quicksand_positions:
            # Лужа появляется и растёт
            if t < 0.5:
                pool_alpha = int(180 * (t / 0.5))
                pool_size = int(25 * (t / 0.5))
            else:
                pool_alpha = 180
                pool_size = 25
            
            # Основная лужа (коричневая/грязь)
            pygame.draw.circle(overlay, (80, 60, 40, pool_alpha), (qx, qy), pool_size)
            pygame.draw.circle(overlay, (100, 75, 50, int(pool_alpha*0.8)), (qx, qy), int(pool_size*0.9))
            
            # Бурлящие пузыри
            for bubble_idx in range(8):
                bubble_angle = (bubble_idx * (2*math.pi / 8.0)) + t * 2
                max_dist = max(5, int(pool_size * 0.7))  # Исправление: гарантируем минимум 5
                bubble_dist = random.randint(3, max_dist)  # Исправление: минимум 3 вместо 5
                bubble_x = qx + int(bubble_dist * math.cos(bubble_angle))
                bubble_y = qy + int(bubble_dist * math.sin(bubble_angle))
                bubble_size = random.randint(2, 5)
                bubble_alpha = int(pool_alpha * 0.6)
                pygame.draw.circle(overlay, (120, 90, 60, bubble_alpha), (bubble_x, bubble_y), bubble_size)
            
            # Частицы грязи
            for particle_idx in range(12):
                particle_angle = (particle_idx * (2*math.pi / 12.0)) + t * 3 + random.uniform(-0.3, 0.3)
                particle_dist = random.randint(int(pool_size * 0.8), int(pool_size * 1.2))
                particle_x = qx + int(particle_dist * math.cos(particle_angle))
                particle_y = qy + int(particle_dist * math.sin(particle_angle))
                particle_size = random.randint(1, 3)
                particle_alpha = int(pool_alpha * 0.4 * random.random())
                pygame.draw.circle(overlay, (90, 70, 45, particle_alpha), (particle_x, particle_y), particle_size)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(12)  # Уменьшена задержка для плавности

def animate_quicksand_trigger(screen, target_px, redraw_callback=None):
    """Анимация срабатывания зыбучих песков - улучшенная бурлящая лужа грязи"""
    import random
    import math
    import time
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 60  # Увеличено для плавности
    cx, cy = target_px
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        anim_time = time.time() * 3
        
        # Основная лужа (коричневая/грязь) - появляется и растёт
        pool_size = int(20 + 15 * min(1.0, t * 2))
        pool_alpha = int(220 * min(1.0, t * 1.5))
        
        # Основная лужа с градиентом
        pygame.draw.circle(overlay, (80, 60, 40, pool_alpha), (cx, cy), pool_size)
        pygame.draw.circle(overlay, (100, 75, 50, int(pool_alpha*0.9)), (cx, cy), int(pool_size*0.9))
        pygame.draw.circle(overlay, (120, 90, 60, int(pool_alpha*0.7)), (cx, cy), int(pool_size*0.7))
        
        # Бурлящие пузыри (больше и активнее)
        for bubble_idx in range(12):
            bubble_angle = (bubble_idx * (2*math.pi / 12.0)) + anim_time
            bubble_dist = random.randint(3, int(pool_size * 0.7))
            bubble_x = cx + int(bubble_dist * math.cos(bubble_angle))
            bubble_y = cy + int(bubble_dist * math.sin(bubble_angle))
            bubble_size = random.randint(3, 6)
            bubble_alpha = int(pool_alpha * 0.8)
            bubble_rise = int(5 * math.sin(anim_time + bubble_idx))
            pygame.draw.circle(overlay, (140, 110, 70, bubble_alpha), (bubble_x, bubble_y - bubble_rise), bubble_size)
            pygame.draw.circle(overlay, (160, 130, 90, int(bubble_alpha*0.6)), (bubble_x, bubble_y - bubble_rise), bubble_size - 1)
        
        # Частицы грязи (больше и активнее)
        for particle_idx in range(16):
            particle_angle = (particle_idx * (2*math.pi / 16.0)) + anim_time * 2 + random.uniform(-0.3, 0.3)
            particle_dist = random.randint(int(pool_size * 0.6), int(pool_size * 1.1))
            particle_x = cx + int(particle_dist * math.cos(particle_angle))
            particle_y = cy + int(particle_dist * math.sin(particle_angle))
            particle_size = random.randint(2, 4)
            particle_alpha = int(pool_alpha * 0.5 * random.random())
            particle_bounce = int(3 * math.sin(anim_time * 2 + particle_idx))
            pygame.draw.circle(overlay, (90, 70, 45, particle_alpha), (particle_x, particle_y + particle_bounce), particle_size)
        
        # Брызги грязи (вверх)
        if t > 0.2:
            splash_t = (t - 0.2) / 0.8
            for splash_idx in range(8):
                splash_angle = (splash_idx * (2*math.pi / 8.0)) + random.uniform(-0.2, 0.2)
                splash_dist = int(25 * splash_t)
                splash_height = int(20 * splash_t * (1 - splash_t))
                splash_x = cx + int(splash_dist * math.cos(splash_angle))
                splash_y = cy - splash_height
                splash_size = random.randint(2, 4)
                splash_alpha = int(150 * (1 - splash_t))
                pygame.draw.circle(overlay, (100, 75, 50, splash_alpha), (splash_x, splash_y), splash_size)
        
        # Волны на поверхности (улучшенные)
        for wave_idx in range(3):
            wave_radius = pool_size + wave_idx * 3
            wave_alpha = int(pool_alpha * 0.4 * (1 - wave_idx * 0.3) * (1 - t * 0.5))
            wave_offset = int(2 * math.sin(anim_time + wave_idx))
            pygame.draw.circle(overlay, (110, 85, 55, wave_alpha), (cx, cy), wave_radius + wave_offset, 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Уменьшена задержка для плавности

def animate_earth_shock(screen, target_px, redraw_callback=None):
    """Анимация шока земли - фиолетовый гравитационный купол, собираются частицы, купол крутится, схлопывается в чёрную дыру и взрывается"""
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    # Этап 1: Появление купола и сбор частиц (20 кадров)
    phase1_frames = 20
    for i in range(phase1_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (phase1_frames - 1) if phase1_frames > 1 else 1.0
        cx, cy = target_px
        
        # Купол появляется и растёт (уменьшен размер)
        dome_size = int(25 + 20 * t)  # Уменьшено с 40+30 до 25+20
        dome_alpha = int(200 * min(1.0, t * 1.5))
        
        # Фиолетовый гравитационный купол
        for layer in range(3):
            layer_size = dome_size - layer * 5  # Уменьшено с 8 до 5
            layer_alpha = int(dome_alpha * (1 - layer * 0.3))
            pygame.draw.circle(overlay, (180, 100, 255, layer_alpha), (cx, cy), layer_size, 2)
        
        # Частицы собираются к центру (уменьшен размер)
        for particle_idx in range(20):
            particle_angle = (particle_idx * (2*math.pi / 20.0))
            particle_start_dist = 40  # Уменьшено с 60 до 40
            particle_dist = particle_start_dist * (1 - t)
            particle_x = cx + int(particle_dist * math.cos(particle_angle))
            particle_y = cy + int(particle_dist * math.sin(particle_angle))
            particle_size = random.randint(1, 3)  # Уменьшено с 2-4 до 1-3
            particle_alpha = int(200 * (1 - t * 0.5))
            pygame.draw.circle(overlay, (200, 120, 255, particle_alpha), (particle_x, particle_y), particle_size)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)  # Ускорено с 30 до 20
    
    # Этап 2: Купол крутится (12 кадров) - ускорено
    phase2_frames = 12
    for i in range(phase2_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (phase2_frames - 1) if phase2_frames > 1 else 1.0
        cx, cy = target_px
        
        dome_size = 45  # Уменьшено с 70 до 45
        rotation_angle = t * 4 * math.pi
        
        # Вращающийся купол
        for layer in range(4):
            layer_size = dome_size - layer * 4  # Уменьшено с 6 до 4
            layer_alpha = int(220 * (1 - layer * 0.2))
            rotated_angle = rotation_angle + layer * 0.5
            
            # Спирали на куполе
            for spiral_idx in range(8):
                spiral_angle = (spiral_idx * (2*math.pi / 8.0)) + rotated_angle
                spiral_x = cx + int(layer_size * 0.8 * math.cos(spiral_angle))
                spiral_y = cy + int(layer_size * 0.8 * math.sin(spiral_angle))
                pygame.draw.circle(overlay, (180, 100, 255, layer_alpha), (spiral_x, spiral_y), 2)  # Уменьшено с 3 до 2
        
        # Внешний купол
        pygame.draw.circle(overlay, (180, 100, 255, 200), (cx, cy), dome_size, 3)
        pygame.draw.circle(overlay, (200, 120, 255, 150), (cx, cy), dome_size + 3, 2)  # Уменьшено с 5 до 3
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)  # Ускорено с 35 до 20
    
    # Этап 3: Схлопывание в чёрную дыру (15 кадров) - ускорено
    phase3_frames = 15
    for i in range(phase3_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (phase3_frames - 1) if phase3_frames > 1 else 1.0
        cx, cy = target_px
        
        # Купол схлопывается (уменьшен размер)
        collapse_size = int(45 * (1 - t))  # Уменьшено с 70 до 45
        
        # Чёрная дыра в центре (уменьшен размер)
        black_hole_size = int(3 + 10 * t)  # Уменьшено с 5+15 до 3+10
        pygame.draw.circle(overlay, (0, 0, 0, 255), (cx, cy), black_hole_size)
        pygame.draw.circle(overlay, (50, 0, 80, 200), (cx, cy), black_hole_size + 2)  # Уменьшено с 3 до 2
        
        # Внешний купол схлопывается
        if collapse_size > black_hole_size:
            pygame.draw.circle(overlay, (180, 100, 255, int(200 * (1 - t))), (cx, cy), collapse_size, 2)
        
        # Частицы втягиваются в дыру (уменьшен размер)
        for particle_idx in range(30):
            particle_angle = (particle_idx * (2*math.pi / 30.0))
            particle_dist = int((collapse_size - black_hole_size) * (1 - t) + black_hole_size)
            particle_x = cx + int(particle_dist * math.cos(particle_angle))
            particle_y = cy + int(particle_dist * math.sin(particle_angle))
            particle_size = random.randint(1, 2)  # Уменьшено с 1-3 до 1-2
            particle_alpha = int(150 * (1 - t))
            pygame.draw.circle(overlay, (200, 120, 255, particle_alpha), (particle_x, particle_y), particle_size)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)  # Ускорено с 30 до 20
    
    # Этап 4: Эпичный фиолетовый взрыв (15 кадров) - ускорено
    phase4_frames = 15
    for i in range(phase4_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (phase4_frames - 1) if phase4_frames > 1 else 1.0
        cx, cy = target_px
        
        # Взрыв распространяется (фиолетовый, уменьшен размер, но интенсивнее)
        explosion_size = int(15 + 60 * t)  # Уменьшено с 25+100 до 15+60
        explosion_alpha = int(255 * (1 - t * 0.5))  # Более интенсивная (было 0.6)
        
        # Множественные взрывные волны (фиолетовые, уменьшен размер, но интенсивнее)
        for wave in range(6):  # Увеличено с 5 до 6 волн
            wave_size = explosion_size - wave * 10  # Уменьшено с 11 до 10
            wave_alpha = int(explosion_alpha * (1 - wave * 0.12))  # Более интенсивная
            if wave_size > 0:
                # Фиолетовые волны с градиентом (более яркие)
                if wave == 0:
                    color = (200, 120, 255, wave_alpha)  # Более яркий
                    outer_color = (220, 140, 255, int(wave_alpha*0.8))  # Более яркий
                elif wave == 1:
                    color = (180, 100, 255, wave_alpha)  # Более яркий
                    outer_color = (200, 120, 255, int(wave_alpha*0.7))
                elif wave == 2:
                    color = (160, 80, 240, wave_alpha)
                    outer_color = (180, 100, 255, int(wave_alpha*0.6))
                elif wave == 3:
                    color = (140, 60, 220, wave_alpha)
                    outer_color = (160, 80, 240, int(wave_alpha*0.5))
                else:
                    color = (120, 40, 200, wave_alpha)
                    outer_color = (140, 60, 220, int(wave_alpha*0.4))
                
                pygame.draw.circle(overlay, color, (cx, cy), wave_size, 4)  # Увеличено с 3 до 4 для интенсивности
                pygame.draw.circle(overlay, outer_color, (cx, cy), wave_size + 6, 3)  # Увеличено с 5,2 до 6,3
        
        # Яркий фиолетовый центр (уменьшен размер, но интенсивнее)
        center_size = int(12 * (1 - t * 0.8))  # Уменьшено с 20 до 12
        if center_size > 0:
            pygame.draw.circle(overlay, (255, 255, 255, int(255 * (1 - t * 0.8))), (cx, cy), center_size)  # Более яркий
            pygame.draw.circle(overlay, (240, 180, 255, int(255 * (1 - t * 0.6))), (cx, cy), center_size + 6)  # Более яркий и больше
            pygame.draw.circle(overlay, (220, 150, 255, int(255 * (1 - t * 0.5))), (cx, cy), center_size + 10)  # Более яркий и больше
            pygame.draw.circle(overlay, (200, 120, 255, int(220 * (1 - t * 0.4))), (cx, cy), center_size + 14)  # Дополнительный слой
        
        # Эпичные фиолетовые искры взрыва (уменьшен размер, но больше и интенсивнее)
        for spark_idx in range(40):  # Увеличено с 32 до 40
            spark_angle = (spark_idx * (2*math.pi / 40.0)) + random.uniform(-0.4, 0.4)
            spark_dist = int(explosion_size * 0.95)  # Увеличено с 0.9 до 0.95
            spark_x = cx + int(spark_dist * math.cos(spark_angle))
            spark_y = cy + int(spark_dist * math.sin(spark_angle))
            spark_size = random.randint(3, 6)  # Увеличено с 2-5 до 3-6 для интенсивности
            spark_alpha = int(explosion_alpha * (0.8 + random.random() * 0.2))  # Более яркие
            
            # Фиолетовые искры с белым центром (более яркие)
            pygame.draw.circle(overlay, (220, 140, 255, spark_alpha), (spark_x, spark_y), spark_size)  # Более яркий
            pygame.draw.circle(overlay, (255, 255, 255, int(spark_alpha*0.95)), (spark_x, spark_y), max(2, spark_size - 1))  # Более яркий
            pygame.draw.circle(overlay, (200, 120, 255, int(spark_alpha*0.7)), (spark_x, spark_y), spark_size + 3, 2)  # Более яркий и больше
        
        # Дополнительные энергетические вспышки (уменьшен размер, но больше и интенсивнее)
        for flash_idx in range(12):  # Увеличено с 8 до 12
            flash_angle = (flash_idx * (2*math.pi / 12.0)) + t * 2
            flash_dist = int(explosion_size * 0.65)  # Увеличено с 0.6 до 0.65
            flash_x = cx + int(flash_dist * math.cos(flash_angle))
            flash_y = cy + int(flash_dist * math.sin(flash_angle))
            flash_size = int(8 * (1 - t))  # Увеличено с 7 до 8
            flash_alpha = int(240 * (1 - t))  # Более яркий (было 200)
            if flash_size > 0:
                pygame.draw.circle(overlay, (255, 255, 255, flash_alpha), (flash_x, flash_y), flash_size)
                pygame.draw.circle(overlay, (240, 180, 255, int(flash_alpha*0.9)), (flash_x, flash_y), flash_size + 3)  # Более яркий и больше
                pygame.draw.circle(overlay, (220, 150, 255, int(flash_alpha*0.7)), (flash_x, flash_y), flash_size + 6)  # Дополнительный слой
        
        # Гравитационные искажения (кольца, уменьшен размер)
        for ring_idx in range(4):
            ring_radius = int(explosion_size * 0.3 + ring_idx * 9)  # Уменьшено с 15 до 9
            ring_alpha = int(100 * (1 - t) * (1 - ring_idx * 0.2))
            if ring_radius > 0 and ring_alpha > 0:
                pygame.draw.circle(overlay, (150, 80, 255, ring_alpha), (cx, cy), ring_radius, 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)


def animate_prayer(screen, target_px, redraw_callback=None):
    """Анимация молитвы - крылья ангела окутывают юнит, летящие белые перья, небесный свет"""
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE
    
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = target_px
    
    # Массив перьев, которые падают на юнит (из проклятия, но белые)
    feathers = []
    for _ in range(35):  # Больше перьев для насыщенности
        # Позиция начала падения (над юнитом)
        start_x = cx + (random.random() - 0.5) * 80
        start_y = cy - CELL_SIZE - random.random() * 60
        # Скорость падения
        vel_x = (random.random() - 0.5) * 2.5
        vel_y = random.random() * 2.0 + 1.0
        # Размер и угол поворота
        size = random.random() * 5 + 3
        angle = random.random() * 2 * math.pi
        rotation_speed = (random.random() - 0.5) * 0.3
        feathers.append({
            'x': start_x,
            'y': start_y,
            'vel_x': vel_x,
            'vel_y': vel_y,
            'size': size,
            'angle': angle,
            'rotation_speed': rotation_speed,
            'alpha': 230
        })
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        
        # Небесный свет (яркие лучи сверху)
        if t < 0.6:
            light_alpha = int(200 * (t / 0.6))
        else:
            light_alpha = int(200 * (1 - (t - 0.6) / 0.4))
        
        # Лучи света сверху
        for ray_idx in range(8):
            ray_angle = (ray_idx * (2*math.pi / 8.0)) - math.pi/2  # Направлены вниз
            ray_length = int(100 * t * (1 - t * 0.5))
            ray_end_x = cx + int(ray_length * math.cos(ray_angle))
            ray_end_y = cy + int(ray_length * math.sin(ray_angle))
            ray_width = int(3 * (1 - t * 0.5))
            if ray_width > 0:
                pygame.draw.line(overlay, (255, 255, 255, light_alpha), (cx, cy - 50), (ray_end_x, ray_end_y), ray_width)
        
        # Крылья ангела (появляются и окутывают юнит)
        if t > 0.2:
            wing_t = (t - 0.2) / 0.8
            wing_size = int(40 + 20 * wing_t)
            wing_alpha = int(180 * min(1.0, wing_t * 1.5))
            
            # Левое крыло
            wing_left_x = cx - 30
            wing_left_y = cy
            for feather_layer in range(3):
                layer_size = wing_size - feather_layer * 5
                layer_alpha = int(wing_alpha * (1 - feather_layer * 0.2))
                # Перья крыла
                for feather_idx in range(5):
                    feather_angle = -math.pi/4 + (feather_idx * 0.2) + wing_t * 0.3
                    feather_x = wing_left_x + int(layer_size * 0.6 * math.cos(feather_angle))
                    feather_y = wing_left_y + int(layer_size * 0.6 * math.sin(feather_angle))
                    pygame.draw.circle(overlay, (255, 255, 255, layer_alpha), (feather_x, feather_y), 8 - feather_layer)
            
            # Правое крыло
            wing_right_x = cx + 30
            wing_right_y = cy
            for feather_layer in range(3):
                layer_size = wing_size - feather_layer * 5
                layer_alpha = int(wing_alpha * (1 - feather_layer * 0.2))
                # Перья крыла
                for feather_idx in range(5):
                    feather_angle = math.pi/4 - (feather_idx * 0.2) - wing_t * 0.3
                    feather_x = wing_right_x + int(layer_size * 0.6 * math.cos(feather_angle))
                    feather_y = wing_right_y + int(layer_size * 0.6 * math.sin(feather_angle))
                    pygame.draw.circle(overlay, (255, 255, 255, layer_alpha), (feather_x, feather_y), 8 - feather_layer)
        
        # Обновляем позиции перьев (из проклятия)
        for feather in feathers:
            feather['x'] += feather['vel_x']
            feather['y'] += feather['vel_y']
            feather['angle'] += feather['rotation_speed']  # Вращение
            # Замедление по мере падения
            if feather['y'] > cy - CELL_SIZE//2:
                feather['vel_y'] *= 0.93
                feather['alpha'] = max(60, feather['alpha'] - 8)
            else:
                feather['alpha'] = min(230, feather['alpha'] + 8)
        
        # Рисуем белые перья (из проклятия, но белые)
        for feather in feathers:
            if feather['y'] < cy + CELL_SIZE//2 and feather['alpha'] > 0:
                # Белое перо (из проклятия, но белое)
                px, py = int(feather['x']), int(feather['y'])
                alpha = int(feather['alpha'])
                size = int(feather['size'])
                
                # Тело пера (белое)
                feather_points = []
                for p in range(5):
                    p_angle = feather['angle'] + p * 0.3
                    p_x = px + int(size * 0.8 * math.cos(p_angle))
                    p_y = py + int(size * 0.4 * math.sin(p_angle))
                    feather_points.append((p_x, p_y))
                
                if len(feather_points) >= 3:
                    pygame.draw.polygon(overlay, (255, 255, 255, alpha), feather_points)
                    # Контур пера (светло-серый)
                    pygame.draw.polygon(overlay, (240, 240, 240, alpha), feather_points, 1)
        
        # Светящееся кольцо вокруг юнита
        if t > 0.3:
            ring_t = (t - 0.3) / 0.7
            ring_radius = int(30 + 20 * ring_t)
            ring_alpha = int(150 * (1 - ring_t * 0.5))
            pygame.draw.circle(overlay, (255, 255, 255, ring_alpha), (cx, cy), ring_radius, 3)
            pygame.draw.circle(overlay, (200, 230, 255, int(ring_alpha*0.7)), (cx, cy), ring_radius + 5, 2)
        
        # Центральное свечение
        center_alpha = int(255 * min(1.0, t * 1.2))
        pygame.draw.circle(overlay, (255, 255, 255, center_alpha), (cx, cy), int(15 * (1 - t * 0.5)))
        pygame.draw.circle(overlay, (200, 230, 255, int(center_alpha*0.8)), (cx, cy), int(20 * (1 - t * 0.5)))
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(12)  # Уменьшена задержка для плавности


def animate_blindness(screen, target_px, redraw_callback=None):
    """Анимация ослепления - появляются слепящие звезды с рандомно увеличивающимся и уменьшающимся эффектом"""
    import pygame
    import random
    import math
    import time
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 120  # Увеличено до 120 кадров для максимальной плавности
    cx, cy = target_px
    
    # Создаём несколько звезд с разными параметрами
    num_stars = 8
    stars = []
    for star_idx in range(num_stars):
        star_angle = (star_idx * (2*math.pi / num_stars))
        star_dist = random.randint(20, 50)
        star_x = cx + int(star_dist * math.cos(star_angle))
        star_y = cy + int(star_dist * math.sin(star_angle))
        star_speed = random.uniform(0.5, 1.5)
        star_phase = random.uniform(0, 2*math.pi)
        stars.append({
            'x': star_x,
            'y': star_y,
            'speed': star_speed,
            'phase': star_phase,
            'base_size': random.randint(5, 10)
        })
    
    start_time = time.time()
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        anim_time = (time.time() - start_time) * 3  # Используем относительное время
        
        # Слепящие звезды
        for star in stars:
            # Пульсация размера (случайная частота)
            pulse = math.sin(anim_time * star['speed'] + star['phase']) * 0.5 + 0.5
            star_size = int(star['base_size'] * (0.5 + pulse * 0.8))
            star_alpha = int(255 * (0.7 + pulse * 0.3) * (1 - t * 0.3))
            
            # Рисуем звезду (крест с ярким центром)
            # Основные лучи
            for ray_idx in range(4):
                ray_angle = ray_idx * (math.pi / 2)
                ray_end_x = star['x'] + int(star_size * math.cos(ray_angle))
                ray_end_y = star['y'] + int(star_size * math.sin(ray_angle))
                pygame.draw.line(overlay, (255, 255, 255, star_alpha), 
                               (star['x'], star['y']), (ray_end_x, ray_end_y), 2)
            
            # Диагональные лучи (короче)
            for ray_idx in range(4):
                ray_angle = ray_idx * (math.pi / 2) + math.pi/4
                ray_end_x = star['x'] + int(star_size * 0.7 * math.cos(ray_angle))
                ray_end_y = star['y'] + int(star_size * 0.7 * math.sin(ray_angle))
                pygame.draw.line(overlay, (255, 255, 200, int(star_alpha*0.8)), 
                               (star['x'], star['y']), (ray_end_x, ray_end_y), 1)
            
            # Яркий центр
            pygame.draw.circle(overlay, (255, 255, 255, star_alpha), (star['x'], star['y']), star_size // 3)
            pygame.draw.circle(overlay, (255, 255, 200, int(star_alpha*0.9)), (star['x'], star['y']), star_size // 2)
        
        # Слепящий свет (вспышки)
        if t < 0.7:
            flash_t = t / 0.7
            flash_alpha = int(150 * (1 - flash_t) * random.random())
            flash_size = int(60 * flash_t)
            pygame.draw.circle(overlay, (255, 255, 255, flash_alpha), (cx, cy), flash_size)
            pygame.draw.circle(overlay, (255, 255, 200, int(flash_alpha*0.7)), (cx, cy), flash_size + 10)
        
        # Вращающиеся световые кольца
        for ring_idx in range(3):
            ring_angle = anim_time + ring_idx * (2*math.pi / 3)
            ring_radius = int(30 + ring_idx * 15)
            ring_alpha = int(100 * (1 - t * 0.5) * (1 - ring_idx * 0.2))
            # Рисуем кольцо как дугу
            for arc_segment in range(8):
                arc_angle = ring_angle + arc_segment * (2*math.pi / 8)
                arc_start_x = cx + int(ring_radius * math.cos(arc_angle))
                arc_start_y = cy + int(ring_radius * math.sin(arc_angle))
                arc_end_x = cx + int(ring_radius * math.cos(arc_angle + 0.3))
                arc_end_y = cy + int(ring_radius * math.sin(arc_angle + 0.3))
                pygame.draw.line(overlay, (255, 255, 200, ring_alpha), 
                               (arc_start_x, arc_start_y), (arc_end_x, arc_end_y), 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)  # Уменьшена задержка для более плавного длинного раунда