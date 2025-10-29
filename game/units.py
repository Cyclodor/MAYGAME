import pygame
import time
from .spells import Spell
from .sound import load_sound
from .graphics import load_image
from .config import CELL_SIZE, RED, GREEN, BLUE, PURPLE, LIGHT_BLUE, TOOLTIP_BG, SCREEN_WIDTH, SCREEN_HEIGHT

TEAM_LABELS = {
    'human': 'Люди',
    'undead': 'Нежить',
    'elf': 'Эльфы',
    'demon': 'Демоны'
}

class Unit:
    def __init__(self, x, y, team, unit_type):
        self.x = x
        self.y = y
        self.team = team
        self.unit_type = unit_type
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.defense = 5
        self.speed = 2  # Только перемещение
        self.initiative = 10  # Новое поле
        self.is_ranged = False  # Новое поле
        self.has_moved = False
        self.has_attacked = False
        self.has_counterattacked = False  # Флаг для контратаки в раунде
        self.move_points_left = self.speed  # Новое поле
        self.image = load_image(f'{unit_type}_{team}')
        self.death_sound = load_sound('death')
        self.attack_sound = load_sound('attack')
        self.hover_time = 0
        self.show_tooltip = False
        self.curse_turns = 0
        self.attack_buff_turns = 0  # Для благословения
        self.attack_debuff_turns = 0  # Для проклятия
        self.prev_health = self.health
        self.prev_attack = self.attack
        self.prev_defense = self.defense
        self.prev_speed = self.speed
        self.fade_health = 0.0
        self.fade_attack = 0.0
        self.fade_defense = 0.0
        self.fade_speed = 0.0
        self.fade_curse = 0.0
        self.fade_buff = 0.0
        self.fade_debuff = 0.0
        self.last_tooltip_update = time.time()
        self.base_defense = 15 if unit_type == 'hero' else 5
        self.rune_shield_turns = 0  # Только руна защиты

    def get_current_attack(self):
        atk = self.attack
        if self.attack_buff_turns > 0:
            atk = int(atk * 1.25)
        if self.attack_debuff_turns > 0:
            atk = int(atk * 0.75)
        return atk

    def apply_attack_buff(self, turns=2):
        self.attack_buff_turns = turns
        self.fade_buff = 1.0

    def apply_attack_debuff(self, turns=2):
        self.attack_debuff_turns = turns
        self.fade_debuff = 1.0

    def draw(self, surface):
        # Рисуем текстуру юнита
        surface.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        # Полоска здоровья
        health_width = (self.health / self.max_health) * CELL_SIZE
        pygame.draw.rect(surface, RED, (self.x * CELL_SIZE, self.y * CELL_SIZE - 5, CELL_SIZE, 5))
        pygame.draw.rect(surface, GREEN, (self.x * CELL_SIZE, self.y * CELL_SIZE - 5, health_width, 5))
        # Типтул только при наведении
        if getattr(self, 'show_tooltip', False):
            mouse_pos = pygame.mouse.get_pos()
            self.draw_tooltip(surface, mouse_pos)

    def draw_tooltip(self, surface, mouse_pos):
        now = time.time()
        dt = now - getattr(self, 'last_tooltip_update', now)
        self.last_tooltip_update = now
        def fade_color(fade):
            yellow = (255, 255, 0)
            white = (255, 255, 255)
            r = int(white[0] * (1-fade) + yellow[0] * fade)
            g = int(white[1] * (1-fade) + yellow[1] * fade)
            b = int(white[2] * (1-fade) + yellow[2] * fade)
            return (r, g, b)
        # Найти героя своей команды для бонуса
        hero = None
        if hasattr(self, 'game_ref') and self.game_ref:
            if hasattr(self.game_ref, 'hero1') and self.team == self.game_ref.hero1.team:
                hero = self.game_ref.hero1
            elif hasattr(self.game_ref, 'hero2') and self.team == self.game_ref.hero2.team:
                hero = self.game_ref.hero2
        atk_bonus = hero.attack if hero else 0
        def_bonus = hero.defense if hero else 0
        base_atk = self.attack - atk_bonus if atk_bonus else self.attack
        base_def = self.base_defense - def_bonus if def_bonus else self.base_defense
        base_atk_with_bonus = base_atk + atk_bonus
        base_def_with_bonus = base_def + def_bonus
        # Текущая атака/защита: если нет эффектов — равна базе+бонус, иначе с учётом эффекта
        current_atk = base_atk_with_bonus
        current_def = base_def_with_bonus
        if self.attack_buff_turns > 0:
            current_atk = int(current_atk * 1.25)
        if self.attack_debuff_turns > 0:
            current_atk = int(current_atk * 0.75)
        if getattr(self, 'rune_shield_turns', 0) > 0:
            current_def += 15
        # Учитываем каменную кожу в текущей защите
        if hasattr(self, 'stone_skin_turns') and getattr(self, 'stone_skin_turns', 0) > 0:
            current_def += getattr(self, 'stone_skin_bonus', 0)
        tooltip_text = [
            (f"Тип: {self.unit_type}", (255,255,255)),
            (f"Здоровье: {self.health}/{self.max_health}", fade_color(self.fade_health)),
            (f"Базовая атака: {base_atk}" + (f" ({base_atk_with_bonus})" if atk_bonus else ""), (180,255,180)),
            (f"Текущая атака: {current_atk}", fade_color(self.fade_attack)),
            (f"Базовая защита: {base_def}" + (f" ({base_def_with_bonus})" if def_bonus else ""), (180,180,180)),
            (f"Текущая защита: {current_def}", fade_color(self.fade_defense)),
            (f"Скорость: {self.speed}", (120,120,255) if hasattr(self, 'slow_turns') and getattr(self, 'slow_turns', 0) > 0 else fade_color(self.fade_speed)),
            (f"Инициатива: {self.initiative}", (255,220,120)),
        ]
        # Эффект Каменной кожи (показываем только длительность; защита уже учтена в текущем значении)
        if hasattr(self, 'stone_skin_turns') and getattr(self, 'stone_skin_turns', 0) > 0:
            tooltip_text.append((f"Каменная кожа: {self.stone_skin_turns} хода", (200,200,200)))
        # --- Эффекты ---
        if self.attack_buff_turns > 0:
            tooltip_text.append((f"Благословение: {self.attack_buff_turns} хода", (80,255,80)))
        if self.attack_debuff_turns > 0:
            tooltip_text.append((f"Проклятие: {self.attack_debuff_turns} хода", (255,80,80)))
        # Только руна защиты
        if getattr(self, 'rune_shield_turns', 0) > 0:
            tooltip_text.append((f"Руна защиты: {self.rune_shield_turns} хода", (80,255,120)))
        # Руна скорости
        if hasattr(self, 'haste_turns') and getattr(self, 'haste_turns', 0) > 0:
            tooltip_text.append((f"Руна скорости: {self.haste_turns} хода", (255,255,255)))
        if self.curse_turns > 0:
            tooltip_text.append((f"Проклятие: {self.curse_turns} хода", fade_color(self.fade_curse)))
        if hasattr(self, 'slow_turns') and getattr(self, 'slow_turns', 0) > 0:
            tooltip_text.append((f"Замедление: {self.slow_turns} хода", (120,120,255)))
        if hasattr(self, 'forget_turns') and getattr(self, 'forget_turns', 0) > 0:
            tooltip_text.append((f"Забвение: {self.forget_turns} хода", (200,200,255)))
        font = pygame.font.Font(None, 24)
        max_width = max(font.size(line[0])[0] for line in tooltip_text)
        tooltip_height = len(tooltip_text) * 22 + 8
        tooltip_surface = pygame.Surface((max_width + 20, tooltip_height + 20), pygame.SRCALPHA)
        tooltip_surface.fill(TOOLTIP_BG)
        for i, (line, color) in enumerate(tooltip_text):
            text_surface = font.render(line, True, color)
            tooltip_surface.blit(text_surface, (10, 10 + i * 22))
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1]
        panel_height = 80
        if tooltip_x + max_width > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - max_width - 20
        # Если тултип пересекает нижнюю панель, отображать его выше курсора
        if tooltip_y + tooltip_height > SCREEN_HEIGHT - panel_height:
            tooltip_y = mouse_pos[1] - tooltip_height - 10
        surface.blit(tooltip_surface, (tooltip_x, tooltip_y))
        self.prev_health = self.health
        self.prev_attack = self.get_current_attack()
        self.prev_defense = self.defense
        self.prev_speed = self.speed

    def take_damage(self, damage):
        self.health -= max(1, damage - self.defense)
        return self.health <= 0

    def reset_turn(self):
        self.has_moved = False
        self.has_attacked = False
        self.has_counterattacked = False  # Сброс флага контратаки в новом раунде
        self.move_points_left = self.speed
        # Забвение: пропуск хода
        if hasattr(self, 'forget_turns') and self.forget_turns > 0:
            self.forget_turns -= 1
            self.has_moved = True
            self.has_attacked = True
            print(f'Забвение: {self.unit_type} пропускает ход ({self.x},{self.y})')
        
        # Руна скорости
        if getattr(self, 'haste_turns', 0) > 0:
            self.haste_turns -= 1
            if self.haste_turns == 0:
                if hasattr(self, 'base_speed'):
                    self.speed = self.base_speed
                if hasattr(self, 'base_initiative'):
                    self.initiative = self.base_initiative
                print(f'Снимаем руну скорости с {self.unit_type} ({self.x},{self.y})')
        # Каменная кожа
        if hasattr(self, 'stone_skin_turns') and self.stone_skin_turns > 0:
            self.stone_skin_turns -= 1
            if self.stone_skin_turns == 0:
                # Вернуть бонус
                self.defense -= getattr(self, 'stone_skin_bonus', 0)
                self.stone_skin_bonus = 0
                print(f'Снимаем Каменную кожу с {self.unit_type} ({self.x},{self.y})')
        if self.curse_turns > 0:
            self.curse_turns -= 1
            if self.curse_turns == 0:
                print(f'Снимаем проклятие с {self.unit_type} ({self.x},{self.y})')
                self.defense = self.base_defense
        if self.attack_buff_turns > 0:
            self.attack_buff_turns -= 1
        if self.attack_debuff_turns > 0:
            self.attack_debuff_turns -= 1
        # Сброс замедления
        if hasattr(self, 'slow_turns') and self.slow_turns > 0:
            self.slow_turns -= 1
            if self.slow_turns == 0:
                # Возврат инициативы
                if hasattr(self, 'base_initiative'):
                    self.initiative = self.base_initiative
                # Пересчет очереди хода (если есть доступ к prepare_initiative_queue)
                if hasattr(self, 'game_ref') and self.game_ref:
                    self.game_ref.prepare_initiative_queue()
                self.speed = getattr(self, 'base_speed', self.speed+1)

    def can_attack(self, target_x, target_y, units=None):
        if hasattr(self, 'forget_turns') and getattr(self, 'forget_turns', 0) > 0:
            return False
        if getattr(self, 'is_ranged', False):
            # Проверяем расстояние до цели
            dx = abs(self.x - target_x)
            dy = abs(self.y - target_y)
            distance_to_target = dx + dy
            
            if self.x == target_x and self.y == target_y:
                return False
            
            # Для дальнобойных: если цель на расстоянии 1, можно только в ближнем бою
            if distance_to_target == 1:
                # Это ближний бой, можно атаковать
                return True
            
            # Для дальнобойной атаки проверяем, нет ли вражеских юнитов рядом (на расстоянии 1)
            if units is not None:
                # Проверяем все 4 соседние клетки
                adjacent_positions = [
                    (self.x + 1, self.y),
                    (self.x - 1, self.y),
                    (self.x, self.y + 1),
                    (self.x, self.y - 1)
                ]
                # Если рядом есть вражеский юнит, нельзя стрелять дальнобойно
                for adj_x, adj_y in adjacent_positions:
                    for unit in units:
                        if unit != self and unit.x == adj_x and unit.y == adj_y:
                            # Проверяем, что это враг (разные команды)
                            if hasattr(unit, 'team') and unit.team != self.team:
                                return False  # Рядом враг, нельзя стрелять дальнобойно
                
                # Проверяем препятствия на пути к цели
                if dx == 0:
                    step_x = 0
                    step_y = 1 if target_y > self.y else -1
                    steps = dy
                elif dy == 0:
                    step_x = 1 if target_x > self.x else -1
                    step_y = 0
                    steps = dx
                else:
                    step_x = 1 if target_x > self.x else -1
                    step_y = 1 if target_y > self.y else -1
                    steps = max(dx, dy)
                cx, cy = self.x, self.y
                for _ in range(1, steps):
                    cx += step_x
                    cy += step_y
                    if any(u.x == cx and u.y == cy for u in units if u != self):
                        return False
            return True
        else:
            distance = abs(self.x - target_x) + abs(self.y - target_y)
            return distance == 1

    def can_move(self, target_x, target_y, units):
        if hasattr(self, 'forget_turns') and getattr(self, 'forget_turns', 0) > 0:
            return False
        from collections import deque
        if self.move_points_left <= 0:
            return False
        panel_height = 80  # Высота нижней панели интерфейса
        max_y = (SCREEN_HEIGHT - panel_height) // CELL_SIZE - 1
        if target_y > max_y or target_y < 0 or target_x < 0 or target_x >= SCREEN_WIDTH // CELL_SIZE:
            return False
        visited = set()
        queue = deque()
        queue.append((self.x, self.y, 0))
        visited.add((self.x, self.y))
        while queue:
            cx, cy, dist = queue.popleft()
            if (cx, cy) == (target_x, target_y) and dist <= self.move_points_left:
                return True
            if dist >= self.move_points_left:
                continue
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx+dx, cy+dy
                if (nx, ny) not in visited and 0 <= nx < SCREEN_WIDTH // CELL_SIZE and 0 <= ny <= max_y:
                    if not any(u.x == nx and u.y == ny for u in units):
                        visited.add((nx, ny))
                        queue.append((nx, ny, dist+1))
        return False

    def update_hover(self, mouse_pos):
        if (self.x * CELL_SIZE <= mouse_pos[0] <= (self.x + 1) * CELL_SIZE and
            self.y * CELL_SIZE <= mouse_pos[1] <= (self.y + 1) * CELL_SIZE):
            self.hover_time += 1
            if self.hover_time >= 30:
                self.show_tooltip = True
        else:
            self.hover_time = 0
            self.show_tooltip = False

    def is_ranged(self):
        return self.attack_range > 1

    def ranged_damage(self, target_x, target_y):
        # Урон уменьшается с расстоянием, минимум 50% от базового, но не меньше 4
        distance = abs(self.x - target_x) + abs(self.y - target_y)
        base_damage = self.get_current_attack()
        # Если атака в ближнем бою (расстояние = 1), урон уменьшается вдвое для лучников
        if distance == 1:
            return max(1, base_damage // 2)  # Половина урона, минимум 1
        # Уменьшено влияние расстояния (было 0.04, стало 0.03)
        factor = max(0.5, 1 - 0.03 * (distance - 1))
        return max(4, int(base_damage * factor))

# --- Юниты людей ---
class Peasant(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'peasant')
        self.health = 50
        self.max_health = 50
        self.attack = 5
        self.defense = 2
        self.speed = 3
        self.initiative = 8
        self.attack_range = 1
        self.base_defense = 2

class Spearman(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'spearman')
        self.health = 70
        self.max_health = 70
        self.attack = 8
        self.defense = 4
        self.speed = 3
        self.initiative = 10
        self.attack_range = 1
        self.base_defense = 4

class Crossbowman(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'crossbowman')
        self.health = 55
        self.max_health = 55
        self.attack = 12
        self.defense = 2
        self.speed = 2
        self.initiative = 13
        self.is_ranged = True
        self.attack_range = 3
        self.base_defense = 2
        self.bow_draw_sound = load_sound('bow_draw')
        self.arrow_shot_sound = load_sound('arrow_shot')
        self.arrow_hit_sound = load_sound('arrow_hit')

class Swordsman(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'swordsman')
        self.health = 90
        self.max_health = 90
        self.attack = 15
        self.defense = 8
        self.speed = 3
        self.initiative = 11
        self.attack_range = 1
        self.base_defense = 8

class Gryphon(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'gryphon')
        self.health = 110
        self.max_health = 110
        self.attack = 18
        self.defense = 10
        self.speed = 5
        self.initiative = 14
        self.attack_range = 1
        self.base_defense = 10

# --- Юниты нежити ---
class Skeleton(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'skeleton')
        self.health = 35
        self.max_health = 35
        self.attack = 6
        self.defense = 2
        self.speed = 3
        self.initiative = 9
        self.attack_range = 1
        self.base_defense = 2

    # Используем базовый рендер через спрайт self.image

class Zombie(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'zombie')
        self.health = 80
        self.max_health = 80
        self.attack = 10
        self.defense = 7
        self.speed = 2
        self.initiative = 6
        self.attack_range = 1
        self.base_defense = 7

    # Используем базовый рендер через спрайт self.image

class Ghost(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'ghost')
        self.health = 30
        self.max_health = 30
        self.attack = 8
        self.defense = 2
        self.speed = 5
        self.initiative = 15
        self.attack_range = 1
        self.base_defense = 2

    # Используем базовый рендер через спрайт self.image

class Vampire(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'vampire')
        self.health = 70
        self.max_health = 70
        self.attack = 13
        self.defense = 5
        self.speed = 4
        self.initiative = 12
        self.attack_range = 1
        self.base_defense = 5

    # Используем базовый рендер через спрайт self.image

class Lich(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'lich')
        self.health = 60
        self.max_health = 60
        self.attack = 18
        self.defense = 4
        self.speed = 3
        self.initiative = 14
        self.is_ranged = True
        self.attack_range = 4
        self.base_defense = 4

    # Используем базовый рендер через спрайт self.image

 

# Старые классы Warrior, Archer, Knight больше не нужны 

class Hero(Unit):
    def __init__(self, x, y, team, spells=None, attack=0, defense=0, knowledge=3, spell_power=1):
        super().__init__(x, y, team, 'hero')
        self.attack = attack
        self.defense = defense
        self.knowledge = knowledge
        self.spell_power = spell_power
        self.mana = knowledge * 10
        self.max_mana = knowledge * 10
        self.mana_regen = 2
        self.spells = spells if spells is not None else []
        self.selected_spell = None
        self.used_spell_this_round = False
        self.image = load_image(f'hero_{team}')
        self.hover_time = 0
        self.show_tooltip = False
        self.last_tooltip_update = time.time()
        self.game_ref = None
        # Герой может атаковать дальнобойно
        self.is_ranged = True
        self.has_attacked = False

    def draw(self, surface):
        # Рисуем героя на поле (без полоски здоровья)
        surface.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        # Типтул только при наведении
        if getattr(self, 'show_tooltip', False):
            mouse_pos = pygame.mouse.get_pos()
            self.draw_tooltip(surface, mouse_pos)

    def draw_tooltip(self, surface, mouse_pos):
        # Типтул героя: атака, защита, знания, сила магии, мана
        now = time.time()
        dt = now - getattr(self, 'last_tooltip_update', now)
        self.last_tooltip_update = now
        font = pygame.font.Font(None, 24)
        tooltip_text = [
            (f"Герой ({TEAM_LABELS.get(self.team, self.team)})", (255,255,255)),
            (f"Атака: {self.attack}", (255,220,120)),
            (f"Дальнобойная атака: {self.attack * 3 + 1}", (255,180,120)),
            (f"Защита: {self.defense}", (180,180,255)),
            (f"Знания: {self.knowledge}", (120,255,255)),
            (f"Сила магии: {self.spell_power}", (180,120,255)),
            (f"Мана: {self.mana}/{self.max_mana}", (120,220,255)),
            (f"Регенерация: {max(1, int(self.knowledge * 0.5))} маны/ход", (180,220,255)),
        ]
        max_width = max(font.size(line[0])[0] for line in tooltip_text)
        tooltip_height = len(tooltip_text) * 20
        tooltip_surface = pygame.Surface((max_width + 20, tooltip_height + 20), pygame.SRCALPHA)
        tooltip_surface.fill(TOOLTIP_BG)
        for i, (line, color) in enumerate(tooltip_text):
            text_surface = font.render(line, True, color)
            tooltip_surface.blit(text_surface, (10, 10 + i * 20))
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1]
        panel_height = 80
        if tooltip_x + max_width > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - max_width - 20
        # Если тултип пересекает нижнюю панель, отображать его выше курсора
        if tooltip_y + tooltip_height > SCREEN_HEIGHT - panel_height:
            tooltip_y = mouse_pos[1] - tooltip_height - 10
        surface.blit(tooltip_surface, (tooltip_x, tooltip_y))

    def can_attack(self, target_x, target_y, units=None):
        # Герой может атаковать дальнобойно, если не атаковал в этом ходу
        if self.has_attacked:
            return False
        dx = abs(self.x - target_x)
        dy = abs(self.y - target_y)
        # Проверяем, что цель не на той же клетке
        if self.x == target_x and self.y == target_y:
            return False
        # Герой может атаковать на любом расстоянии
        return True

    def ranged_damage(self, target_x, target_y):
        # Герой наносит фиксированный урон: attack*3+1
        return self.attack * 3 + 1

    def take_damage(self, damage):
        # Герой не может получать урон
        return False

    def reset_turn(self):
        self.selected_spell = None
        self.used_spell_this_round = False
        self.has_attacked = False

    def can_move(self, target_x, target_y, units):
        return False

    def update_hover(self, mouse_pos):
        if (self.x * CELL_SIZE <= mouse_pos[0] <= (self.x + 1) * CELL_SIZE and
            self.y * CELL_SIZE <= mouse_pos[1] <= (self.y + 1) * CELL_SIZE):
            self.hover_time += 1
            if self.hover_time >= 30:
                self.show_tooltip = True
        else:
            self.hover_time = 0
            self.show_tooltip = False

    def update_spells(self):
        pass

    def update_mana(self):
        pass

    def apply_bonuses_to_army(self, units):
        for unit in units:
            if unit.team == self.team:
                unit.attack += self.attack
                unit.defense += self.defense

class Pixie(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'pixie')
        self.health = 25
        self.max_health = 25
        self.attack = 5
        self.defense = 1
        self.speed = 6
        self.initiative = 16
        self.attack_range = 1
        self.base_defense = 1

class ElfScout(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'elf_scout')
        self.health = 40
        self.max_health = 40
        self.attack = 8
        self.defense = 2
        self.speed = 5
        self.initiative = 13
        self.attack_range = 1
        self.base_defense = 2

class ElfArcher(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'elf_archer')
        self.health = 45
        self.max_health = 45
        self.attack = 13
        self.defense = 2
        self.speed = 3
        self.initiative = 15
        self.is_ranged = True
        self.attack_range = 4
        self.base_defense = 2
        self.bow_draw_sound = load_sound('bow_draw')
        self.arrow_shot_sound = load_sound('arrow_shot')
        self.arrow_hit_sound = load_sound('arrow_hit')

class Dryad(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'dryad')
        self.health = 55
        self.max_health = 55
        self.attack = 10
        self.defense = 4
        self.speed = 3
        self.initiative = 10
        self.attack_range = 1
        self.base_defense = 4

class Ent(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'ent')
        self.health = 110
        self.max_health = 110
        self.attack = 16
        self.defense = 12
        self.speed = 2
        self.initiative = 7
        self.attack_range = 1
        self.base_defense = 12

class Imp(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'imp')
        self.health = 25
        self.max_health = 25
        self.attack = 7
        self.defense = 2
        self.speed = 6
        self.initiative = 15
        self.attack_range = 1
        self.base_defense = 2

class Gog(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'gog')
        self.health = 40
        self.max_health = 40
        self.attack = 12
        self.defense = 2
        self.speed = 4
        self.initiative = 13
        self.is_ranged = True
        self.attack_range = 3
        self.base_defense = 2

class Demon(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'demon')
        self.health = 70
        self.max_health = 70
        self.attack = 14
        self.defense = 6
        self.speed = 4
        self.initiative = 11
        self.attack_range = 1
        self.base_defense = 6

class Cerberus(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'cerberus')
        self.health = 80
        self.max_health = 80
        self.attack = 15
        self.defense = 5
        self.speed = 6
        self.initiative = 14
        self.attack_range = 1
        self.base_defense = 5

class Succubus(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'succubus')
        self.health = 50
        self.max_health = 50
        self.attack = 14
        self.defense = 3
        self.speed = 5
        self.initiative = 14
        self.is_ranged = True
        self.attack_range = 4
        self.base_defense = 3

# --- Гномы ---
class Miner(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'miner')
        self.health = 30
        self.max_health = 30
        self.attack = 6
        self.defense = 3
        self.speed = 3
        self.initiative = 7
        self.attack_range = 1
        self.base_defense = 3

class Spearthrower(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'spearthrower')
        self.health = 24
        self.max_health = 24
        self.attack = 7
        self.defense = 2
        self.speed = 4
        self.initiative = 8
        self.is_ranged = True
        self.attack_range = 3
        self.base_defense = 2

class BearRider(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'bearrider')
        self.health = 40
        self.max_health = 40
        self.attack = 10
        self.defense = 4
        self.speed = 5
        self.initiative = 10
        self.attack_range = 1
        self.base_defense = 4

class RuneMage(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'runemage')
        self.health = 22
        self.max_health = 22
        self.attack = 8
        self.defense = 2
        self.speed = 6
        self.initiative = 9
        self.is_ranged = True
        self.attack_range = 4
        self.base_defense = 2

class Jarl(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'jarl')
        self.health = 50
        self.max_health = 50
        self.attack = 12
        self.defense = 6
        self.speed = 4
        self.initiative = 11
        self.attack_range = 1
        self.base_defense = 6

# --- Лига теней ---
class Scout(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'scout')
        self.health = 20
        self.max_health = 20
        self.attack = 7
        self.defense = 2
        self.speed = 7
        self.initiative = 10
        self.attack_range = 1
        self.base_defense = 2

class Beast(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'beast')
        self.health = 32
        self.max_health = 32
        self.attack = 9
        self.defense = 3
        self.speed = 6
        self.initiative = 11
        self.attack_range = 1
        self.base_defense = 3

class Minotaur(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'minotaur')
        self.health = 44
        self.max_health = 44
        self.attack = 11
        self.defense = 5
        self.speed = 5
        self.initiative = 12
        self.attack_range = 1
        self.base_defense = 5

class Witch(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'witch')
        self.health = 24
        self.max_health = 24
        self.attack = 8
        self.defense = 2
        self.speed = 7
        self.initiative = 10
        self.is_ranged = True
        self.attack_range = 3
        self.base_defense = 2

class LizardRider(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'lizardrider')
        self.health = 38
        self.max_health = 38
        self.attack = 10
        self.defense = 4
        self.speed = 6
        self.initiative = 12
        self.attack_range = 1
        self.base_defense = 4