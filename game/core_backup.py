import pygame
from .config import *
from .units import Hero, Peasant, Spearman, Crossbowman, Swordsman, Gryphon, Skeleton, Zombie, Ghost, Vampire, Lich, Pixie, ElfScout, ElfArcher, Dryad, Ent, Imp, Gog, Demon, Cerberus, Succubus, Miner, Spearthrower, BearRider, RuneMage, Jarl, Scout, Beast, Minotaur, Witch, LizardRider
from .graphics import draw_cell_texture, draw_animated_grass, animate_arrow, animate_magic_projectile, animate_arrow_fly, animate_magic_fly
from .spells import BlessSpell, CurseSpell, FireballSpell, HealSpell, ShieldSpell, SlowSpell, FireArrowSpell, DispelSpell, RuneShieldSpell, RuneHasteSpell, ForgetSpell, FrostRingSpell
from .debugger import GameDebugger
import math
import random

DEBUG_MODE = False

TEAM_LABELS = {
    'human': 'Люди',
    'undead': 'Нежить',
    'elf': 'Эльфы',
    'demon': 'Демоны'
}

def toggle_debug_mode():
    global DEBUG_MODE
    DEBUG_MODE = not DEBUG_MODE
    print(f'DEBUG_MODE set to {DEBUG_MODE}')

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.units = []
        self.selected_unit = None
        self.current_team = 'human'
        self.game_over = False
        self.menu_open = False
        self.state = 'menu'  # 'menu', 'choose_race_p1', 'choose_race_p2', 'game'
        self.background = self.generate_battlefield()
        self.font = pygame.font.Font(None, 36)
        self.highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        self.highlight_surface.fill((0, 255, 255, 80))
        self.initiative_queue = []
        self.current_initiative_index = 0
        self.event_log = []
        self.event_log_offset = 0
        self.history_panel_open = False
        self.skip_button_rect = pygame.Rect(SCREEN_WIDTH - 70, SCREEN_HEIGHT - 80 - 60, 48, 48)
        self.defend_button_rect = pygame.Rect(SCREEN_WIDTH - 140, SCREEN_HEIGHT - 80 - 60, 48, 48)
        self.book_button_rect = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 80 - 60, 48, 48)
        self.history_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 24, 10, 48, 48)
        self.spellbook_open = False
        self.spellbook_rect = pygame.Rect(SCREEN_WIDTH - 150, 20, 140, 40)
        self.spellbook_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
        self.spellbook_surface.fill((0, 0, 0, 200))
        self.menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 60, 240, 120)
        self.exit_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 + 10, 120, 40)
        self.start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 - 40, 120, 40)
        self.round_number = 1
        self.player1_race = None
        self.player2_race = None
        self.player1_side = 'right'
        self.player2_side = 'left'
        # Инициализация дебаггера
        self.debugger = GameDebugger(self)
        # self.prepare_initiative_queue() — вызывать только после инициализации юнитов!
        # Установить game_ref для всех юнитов (если есть)
        for unit in self.units:
            unit.game_ref = self

    def generate_battlefield(self):
        field = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                draw_cell_texture(field, x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(field, (90, 60, 30), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
        return field

    def initialize_units(self, p1_race=None, p2_race=None):
        self.units = []
        # p1 - справа, p2 - слева
        races = {
            'human': [Peasant, Spearman, Crossbowman, Swordsman, Gryphon],
            'undead': [Skeleton, Zombie, Ghost, Vampire, Lich],
            'elf': [Pixie, ElfScout, ElfArcher, Dryad, Ent],
            'demon': [Imp, Gog, Demon, Cerberus, Succubus],
            'dwarf': [Miner, Spearthrower, BearRider, RuneMage, Jarl],
            'shadow': [Scout, Beast, Minotaur, Witch, LizardRider]
        }
        hero_spells = {
            'human': [BlessSpell(), DispelSpell()],
            'undead': [CurseSpell()],
            'elf': [SlowSpell()],
            'demon': [FireArrowSpell()],
            'dwarf': [RuneShieldSpell(), RuneHasteSpell()],
            'shadow': [ForgetSpell(), FrostRingSpell()]
        }
        # --- Первый игрок (справа) ---
        if p1_race:
            if p1_race == 'human':
                hero1_params = dict(attack=3, defense=3, knowledge=2, spell_power=1)
            elif p1_race == 'elf':
                hero1_params = dict(attack=2, defense=2, knowledge=2, spell_power=2)
            elif p1_race == 'undead':
                hero1_params = dict(attack=1, defense=1, knowledge=3, spell_power=3)
            elif p1_race == 'demon':
                hero1_params = dict(attack=2, defense=1, knowledge=2, spell_power=3)
            elif p1_race == 'dwarf':
                hero1_params = dict(attack=3, defense=4, knowledge=2, spell_power=1)
            elif p1_race == 'shadow':
                hero1_params = dict(attack=2, defense=2, knowledge=3, spell_power=2)
            hero1_spells = hero_spells[p1_race]
            self.hero1 = Hero(GRID_WIDTH-1, 0, p1_race, spells=hero1_spells, **hero1_params)
            self.hero1.used_spell_this_round = False
            self.hero1.game_ref = self
            army = []
            for i, unit_cls in enumerate(races[p1_race]):
                unit = unit_cls(GRID_WIDTH-2, 1 + i*2, p1_race)
                unit.game_ref = self
                army.append(unit)
            self.units.append(self.hero1)
            self.hero1.apply_bonuses_to_army(army)
            self.units.extend(army)
        # --- Второй игрок (слева) ---
        if p2_race:
            if p2_race == 'human':
                hero2_params = dict(attack=3, defense=3, knowledge=2, spell_power=1)
            elif p2_race == 'elf':
                hero2_params = dict(attack=2, defense=2, knowledge=2, spell_power=2)
            elif p2_race == 'undead':
                hero2_params = dict(attack=1, defense=1, knowledge=3, spell_power=3)
            elif p2_race == 'demon':
                hero2_params = dict(attack=2, defense=1, knowledge=2, spell_power=3)
            elif p2_race == 'dwarf':
                hero2_params = dict(attack=3, defense=4, knowledge=2, spell_power=1)
            elif p2_race == 'shadow':
                hero2_params = dict(attack=2, defense=2, knowledge=3, spell_power=2)
            hero2_spells = hero_spells[p2_race]
            self.hero2 = Hero(0, 0, p2_race, spells=hero2_spells, **hero2_params)
            self.hero2.used_spell_this_round = False
            self.hero2.game_ref = self
            army = []
            for i, unit_cls in enumerate(races[p2_race]):
                unit = unit_cls(1, 1 + i*2, p2_race)
                unit.game_ref = self
                army.append(unit)
            self.units.append(self.hero2)
            self.hero2.apply_bonuses_to_army(army)
            self.units.extend(army)

    def draw_grid(self):
        # Подсветка диапазона хода только для активного юнита (не героя)
        if self.selected_unit and not self.selected_unit.has_attacked and not isinstance(self.selected_unit, Hero):
            move_points = getattr(self.selected_unit, 'move_points_left', 0)
            if move_points > 0:
                reachable = self.get_reachable_cells(self.selected_unit.x, self.selected_unit.y, move_points)
                for (mx, my) in reachable:
                    dist = abs(mx - self.selected_unit.x) + abs(my - self.selected_unit.y)
                    max_alpha = 180
                    min_alpha = 40
                    if move_points > 1:
                        alpha = max(min_alpha, max_alpha - int((max_alpha-min_alpha) * (dist-1) / (move_points-1)))
                    else:
                        alpha = max_alpha
                    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    surf.fill((60, 120, 255, alpha))
                    self.screen.blit(surf, (mx*CELL_SIZE, my*CELL_SIZE))

    def draw_ui(self):
        def pluralize(n, forms):
            n = abs(n)
            if n % 10 == 1 and n % 100 != 11:
                return forms[0]
            elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
                return forms[1]
            else:
                return forms[2]
        # Нижний интерфейс: очередь, кнопки, история, книга заклинаний
        panel_height = 80
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - panel_height, SCREEN_WIDTH, panel_height)
        pygame.draw.rect(self.screen, (30, 30, 60), panel_rect)
        icon_size = 48
        spacing = 10
        start_x = 20
        y = SCREEN_HEIGHT - panel_height + 10
        # --- Подпись раунда ---
        font_round = pygame.font.Font(None, 28)
        round_label = f"Раунд {self.round_number}"
        surf_round = font_round.render(round_label, True, (255, 220, 120))
        self.screen.blit(surf_round, (start_x, y - 28))
        # --- Лента очереди ---
        mouse = pygame.mouse.get_pos()
        hovered_unit = None
        for unit in self.units:
            if unit.x * CELL_SIZE <= mouse[0] < (unit.x+1)*CELL_SIZE and unit.y * CELL_SIZE <= mouse[1] < (unit.y+1)*CELL_SIZE:
                hovered_unit = unit
                break
        if hasattr(self, 'turn_queue'):
            max_visible = min(8, len(self.turn_queue))
            for i in range(max_visible):
                unit = self.turn_queue[i]
                x = start_x + i * (icon_size + spacing)
                rect = pygame.Rect(x, y, icon_size, icon_size)
                if i == 0:
                    color = (200, 200, 80)
                elif hovered_unit and unit == hovered_unit:
                    color = (120, 220, 255)
                else:
                    color = (80, 80, 120)
                pygame.draw.rect(self.screen, color, rect, border_radius=8)
                self.screen.blit(unit.image, (x, y))
                if hasattr(unit, 'health') and unit.health <= 0:
                    pygame.draw.line(self.screen, (200,0,0), (x, y), (x+icon_size, y+icon_size), 4)
                    pygame.draw.line(self.screen, (200,0,0), (x+icon_size, y), (x, y+icon_size), 4)
        # Кнопки теперь на уровне ленты очереди
        button_y = y
        self.skip_button_rect.y = button_y
        self.defend_button_rect.y = button_y
        self.book_button_rect.y = button_y
        wait_button_rect = pygame.Rect(self.skip_button_rect.x - 70, button_y, 48, 48)
        # Кнопка защиты (defend)
        if self.selected_unit and not isinstance(self.selected_unit, Hero):
            pygame.draw.rect(self.screen, (120, 180, 220), self.skip_button_rect, border_radius=8)
            pygame.draw.ellipse(self.screen, (180,180,220), (self.skip_button_rect.x+8, self.skip_button_rect.y+12, 32, 24))
            pygame.draw.rect(self.screen, (120,180,220), (self.skip_button_rect.x+20, self.skip_button_rect.y+24, 8, 16))
        else:
            pygame.draw.rect(self.screen, (80, 80, 80), self.skip_button_rect, border_radius=8)
            pygame.draw.ellipse(self.screen, (120,120,120), (self.skip_button_rect.x+8, self.skip_button_rect.y+12, 32, 24))
            pygame.draw.rect(self.screen, (120,120,120), (self.skip_button_rect.x+20, self.skip_button_rect.y+24, 8, 16))
        # Кнопка ждать (wait)
        if self.selected_unit and not isinstance(self.selected_unit, Hero):
            pygame.draw.rect(self.screen, (120, 180, 120), wait_button_rect, border_radius=8)
            pygame.draw.ellipse(self.screen, (200,200,120), (wait_button_rect.x+12, wait_button_rect.y+8, 24, 12))
            pygame.draw.rect(self.screen, (200,200,120), (wait_button_rect.x+20, wait_button_rect.y+20, 8, 16))
            pygame.draw.ellipse(self.screen, (200,200,120), (wait_button_rect.x+12, wait_button_rect.y+32, 24, 12))
        else:
            pygame.draw.rect(self.screen, (80, 80, 80), wait_button_rect, border_radius=8)
            pygame.draw.ellipse(self.screen, (120,120,120), (wait_button_rect.x+12, wait_button_rect.y+8, 24, 12))
            pygame.draw.rect(self.screen, (120,120,120), (wait_button_rect.x+20, wait_button_rect.y+20, 8, 16))
            pygame.draw.ellipse(self.screen, (120,120,120), (wait_button_rect.x+12, wait_button_rect.y+32, 24, 12))
        # Кнопка книги заклинаний
        is_hero = isinstance(self.selected_unit, Hero)
        can_cast = is_hero and self.selected_unit.spells and not getattr(self.selected_unit, 'used_spell_this_round', False)
        if can_cast:
            pygame.draw.rect(self.screen, (180, 120, 60), self.book_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (220, 200, 120), (self.book_button_rect.x+8, self.book_button_rect.y+12, 32, 24), border_radius=6)
            pygame.draw.line(self.screen, (120,80,40), (self.book_button_rect.x+16, self.book_button_rect.y+12), (self.book_button_rect.x+16, self.book_button_rect.y+36), 2)
        else:
            pygame.draw.rect(self.screen, (80, 80, 80), self.book_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (120, 120, 120), (self.book_button_rect.x+8, self.book_button_rect.y+12, 32, 24), border_radius=6)
            pygame.draw.line(self.screen, (60,60,60), (self.book_button_rect.x+16, self.book_button_rect.y+12), (self.book_button_rect.x+16, self.book_button_rect.y+36), 2)
            mouse = pygame.mouse.get_pos()
            if self.book_button_rect.collidepoint(mouse):
                font_tip = pygame.font.Font(None, 22)
                tip = "Книга доступна только героям"
                if is_hero and getattr(self.selected_unit, 'used_spell_this_round', False):
                    tip = "Заклинание уже использовано в этом раунде"
                elif is_hero and not self.selected_unit.spells:
                    tip = "Нет доступных заклинаний"
                surf_tip = font_tip.render(tip, True, (200,200,200))
                self.screen.blit(surf_tip, (self.book_button_rect.x-180, self.book_button_rect.y+8))
        # Книга заклинаний (на весь экран, с анимацией и иконками)
        if self.spellbook_open and isinstance(self.selected_unit, Hero) and self.selected_unit.spells:
            # Всегда сбрасываем вкладку на 'all' при открытии книги
            if not hasattr(self, 'spellbook_selected_school') or self._just_opened_spellbook:
                self.spellbook_selected_school = 'all'
            self._just_opened_spellbook = False
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((30, 30, 60, 230))
            self.screen.blit(overlay, (0,0))
            book_w, book_h = 600, 400
            book_x = (SCREEN_WIDTH - book_w)//2
            book_y = (SCREEN_HEIGHT - book_h)//2
            # --- Список школ ---
            school_list = [
                ('all', (180,180,180)),
                ('fire', (255,80,40)),
                ('water', (80,180,255)),
                ('earth', (60,180,60)),
                ('air', (180,220,255)),
                ('light', (255,255,180)),
                ('darkness', (120,0,120)),
                ('rune', (200,200,200)),
            ]
            spells = self.selected_unit.spells
            spells_by_school = {school: [s for s in spells if school == 'all' or getattr(s, 'school', None) == school] for school, _ in school_list}
            filtered_spells = spells_by_school.get(getattr(self, 'spellbook_selected_school', 'all'), [])
            # --- Фон книги ---
            book_surface = pygame.Surface((book_w, book_h), pygame.SRCALPHA)
            book_surface.fill((245, 230, 180, 240))  # светлый пергамент
            pygame.draw.rect(book_surface, (180,150,80), (0,0,book_w,book_h), 8, border_radius=24)  # рамка
            # --- Кнопка закрытия (крестик) ---
            close_rect = pygame.Rect(book_w-44, 12, 32, 32)
            pygame.draw.rect(book_surface, (200,60,60), close_rect, border_radius=8)
            pygame.draw.line(book_surface, (255,255,255), (book_w-36, 20), (book_w-20, 36), 4)
            pygame.draw.line(book_surface, (255,255,255), (book_w-20, 20), (book_w-36, 36), 4)
            self.spellbook_close_rect = pygame.Rect(book_x+book_w-44, book_y+12, 32, 32)
            # --- Переплёт (спайн) ---
            spine_x = book_w // 2
            pygame.draw.rect(book_surface, (160,120,60), (spine_x-8, 0, 16, book_h), border_radius=8)
            pygame.draw.line(book_surface, (120,80,40), (spine_x, 0), (spine_x, book_h), 3)
            # --- Закладки школ ---
            tab_w, tab_h = 56, 48
            # По умолчанию выбрана вкладка "все заклятия"
            selected_school = getattr(self, 'spellbook_selected_school', 'all')
            self.spellbook_selected_school = selected_school
            for i, (school, color) in enumerate(school_list):
                tab_x = book_x + 20 + i*(tab_w+8)
                tab_y = book_y - 36
                has_spells = len(spells_by_school[school]) > 0
                tab_color = color if has_spells else (120,120,120)
                if school == selected_school:
                    pygame.draw.rect(self.screen, (tab_color[0],tab_color[1],tab_color[2],220), (tab_x, tab_y, tab_w, tab_h), border_radius=12)
                    pygame.draw.rect(self.screen, (255,255,120), (tab_x, tab_y, tab_w, tab_h), 3, border_radius=12)
                else:
                    pygame.draw.rect(self.screen, tab_color, (tab_x, tab_y, tab_w, tab_h), border_radius=12)
                # Иконка школы
                cx, cy = tab_x+tab_w//2, tab_y+tab_h//2
                if school == 'all':
                    # Иконка: книга с магическим сиянием
                    pygame.draw.rect(self.screen, (220,220,200), (cx-12, cy-8, 24, 16), border_radius=6)
                    pygame.draw.line(self.screen, (180,150,80), (cx-10, cy-2), (cx+10, cy-2), 2)
                    pygame.draw.circle(self.screen, (120,200,255,120), (cx, cy+2), 12, 2)
                elif school == 'fire':
                    pygame.draw.polygon(self.screen, (255,80,40), [(cx,cy-10),(cx-10,cy+10),(cx+10,cy+10)])
                elif school == 'water':
                    pygame.draw.ellipse(self.screen, (80,180,255), (cx-12,cy-8,24,16))
                    pygame.draw.ellipse(self.screen, (180,220,255), (cx-8,cy-4,16,8))
                elif school == 'earth':
                    pygame.draw.rect(self.screen, (60,180,60), (cx-10,cy-6,20,12), border_radius=6)
                    pygame.draw.ellipse(self.screen, (80,220,80), (cx-8,cy-10,16,8))
                elif school == 'air':
                    pygame.draw.arc(self.screen, (180,220,255), (cx-12,cy-8,24,16), 0, 3.14, 3)
                elif school == 'light':
                    pygame.draw.circle(self.screen, (255,255,180), (cx,cy), 12)
                    pygame.draw.line(self.screen, (255,255,120), (cx,cy-14), (cx,cy+14), 3)
                    pygame.draw.line(self.screen, (255,255,120), (cx-14,cy), (cx+14,cy), 3)
                elif school == 'darkness':
                    pygame.draw.circle(self.screen, (120,0,120), (cx,cy), 12)
                    pygame.draw.circle(self.screen, (60,0,80), (cx,cy), 8)
                elif school == 'rune':
                    pygame.draw.polygon(self.screen, (200,200,200), [(cx,cy-10),(cx-10,cy+10),(cx+10,cy+10)])
                    pygame.draw.line(self.screen, (120,120,120), (cx-10,cy+10), (cx+10,cy+10), 2)
            # --- Обработка клика по закладкам школ ---
            mouse = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:
                for i, (school, _) in enumerate(school_list):
                    tab_x = book_x + 20 + i*(tab_w+8)
                    tab_y = book_y - 36
                    has_spells = len(spells_by_school[school]) > 0
                    if has_spells:
                        if pygame.Rect(tab_x, tab_y, tab_w, tab_h).collidepoint(mouse):
                            self.spellbook_selected_school = school
            # --- Пагинация и иконки заклинаний ---
            spells_per_page = 6
            columns = 2
            rows = 3
            spell_size = 64
            page = getattr(self, 'spellbook_page', 0)
            total_pages = (len(filtered_spells) + spells_per_page - 1) // spells_per_page
            # --- Кнопки перелистывания (уголки страниц) ---
            next_page_rect = None
            prev_page_rect = None
            if total_pages > 1:
                if page < total_pages-1:
                    # Уголок вправо (правый нижний угол)
                    next_page_rect = pygame.Rect(book_w-48, book_h-48, 40, 40)
                    pygame.draw.polygon(book_surface, (200,180,120), [
                        (book_w-8, book_h-8), (book_w-48, book_h-8), (book_w-8, book_h-48)
                    ])
                    pygame.draw.line(book_surface, (120,100,60), (book_w-48, book_h-8), (book_w-8, book_h-48), 2)
                if page > 0:
                    # Уголок влево (левый нижний угол)
                    prev_page_rect = pygame.Rect(8, book_h-48, 40, 40)
                    pygame.draw.polygon(book_surface, (200,180,120), [
                        (8, book_h-8), (48, book_h-8), (8, book_h-48)
                    ])
                    pygame.draw.line(book_surface, (120,100,60), (48, book_h-8), (8, book_h-48), 2)
            # --- Иконки заклинаний на странице ---
            spell_size = 64
            tiptul = None
            tiptul_rect = None
            start_idx = page * spells_per_page
            end_idx = min(start_idx + spells_per_page, len(filtered_spells))
            for idx, spell in enumerate(filtered_spells[start_idx:end_idx]):
                col = idx % 2
                row = idx // 2
                if col == 0:
                    sx = 60
                else:
                    sx = book_w//2 + 36
                sy = 60 + row * 100
                icon_rect = pygame.Rect(sx, sy, spell_size, spell_size)
                pygame.draw.rect(book_surface, (200,200,240), icon_rect, border_radius=12)
                # --- Стилистическая рамка по школе ---
                school = getattr(spell, 'school', None)
                frame_margin = 2
                frame_rect = icon_rect.inflate(-frame_margin*2, -frame_margin*2)
                # Draw a thick, bright, decorative border for each school
                if school == 'fire':
                    # Яркое пламя по краям
                    for i in range(12):
                        angle = math.radians(i*30)
                        fx = frame_rect.centerx + int((frame_rect.width//2-2) * math.cos(angle))
                        fy = frame_rect.centery + int((frame_rect.height//2-2) * math.sin(angle))
                        color = (255, 80+int(80*abs(math.sin(angle))), 40)
                        pygame.draw.polygon(book_surface, color, [
                            (fx, fy),
                            (fx+int(10*math.cos(angle+0.25)), fy+int(10*math.sin(angle+0.25))),
                            (fx+int(10*math.cos(angle-0.25)), fy+int(10*math.sin(angle-0.25)))
                        ])
                    pygame.draw.ellipse(book_surface, (255,120,40,180), frame_rect, 4)
                elif school == 'earth':
                    # Плющ/корни с листьями
                    for i in range(14):
                        angle = math.radians(i*25)
                        ex = frame_rect.centerx + int((frame_rect.width//2-2) * math.cos(angle))
                        ey = frame_rect.centery + int((frame_rect.height//2-2) * math.sin(angle))
                        color = (60, 180, 60)
                        pygame.draw.line(book_surface, color, (frame_rect.centerx, frame_rect.centery), (ex, ey), 5)
                        leaf_angle = angle + math.radians(12)
                        lx = ex + int(8*math.cos(leaf_angle))
                        ly = ey + int(8*math.sin(leaf_angle))
                        pygame.draw.ellipse(book_surface, (80,220,80), (lx-3, ly-6, 6, 12))
                    pygame.draw.ellipse(book_surface, (60,180,60,180), frame_rect, 5)
                elif school == 'light':
                    # Золотое сияние с лучами
                    pygame.draw.ellipse(book_surface, (255,255,180,220), frame_rect, 6)
                    for i in range(16):
                        angle = math.radians(i*22.5)
                        lx = frame_rect.centerx + int((frame_rect.width//2+8) * math.cos(angle))
                        ly = frame_rect.centery + int((frame_rect.height//2+8) * math.sin(angle))
                        pygame.draw.line(book_surface, (255,255,120), (frame_rect.centerx, frame_rect.centery), (lx, ly), 3)
                elif school == 'darkness':
                    # Темные завитки/туман с фиолетовым свечением
                    for i in range(10):
                        angle = math.radians(i*36)
                        dx = frame_rect.centerx + int((frame_rect.width//2-2) * math.cos(angle))
                        dy = frame_rect.centery + int((frame_rect.height//2-2) * math.sin(angle))
                        pygame.draw.circle(book_surface, (60,0,80,200), (dx, dy), 8)
                        pygame.draw.circle(book_surface, (120,0,120,120), (dx, dy), 4)
                    pygame.draw.ellipse(book_surface, (60,0,80,180), frame_rect, 5)
                # --- Сама иконка ---
                # Draw icon in a 32x32 area centered in icon_rect
                icon_cx, icon_cy = icon_rect.center
                icon_box = pygame.Rect(0, 0, 32, 32)
                icon_box.center = (icon_cx, icon_cy)
                if spell.icon == 'bless':
                    # Кубок со святой водой: детализированный, с бликами
                    cx, cy = icon_box.center
                    pygame.draw.ellipse(book_surface, (200,200,255), (cx-10, cy-4, 20, 8))
                    pygame.draw.rect(book_surface, (220,220,255), (cx-8, cy-4, 16, 7))
                    pygame.draw.rect(book_surface, (180,180,220), (cx-6, cy+3, 12, 6))
                    pygame.draw.rect(book_surface, (180,180,220), (cx-3, cy+9, 6, 4))
                    pygame.draw.ellipse(book_surface, (120,180,255), (cx-6, cy-1, 12, 4))
                    # Shine
                    pygame.draw.arc(book_surface, (255,255,255), (cx-8, cy-2, 16, 6), math.radians(10), math.radians(80), 2)
                elif spell.icon == 'dispel':
                    # Иконка: человек с расходящимися волнами воды
                    cx, cy = icon_box.center
                    # Тело
                    pygame.draw.circle(book_surface, (80,180,255), (cx, cy+6), 8)
                    pygame.draw.circle(book_surface, (220,220,255), (cx, cy+2), 4)
                    # Голова
                    pygame.draw.circle(book_surface, (255,255,255), (cx, cy-6), 5)
                    # Волны
                    for r in [16, 22]:
                        pygame.draw.arc(book_surface, (80,180,255), (cx-r, cy-r, 2*r, 2*r), math.radians(200), math.radians(340), 3)
                        pygame.draw.arc(book_surface, (180,220,255), (cx-r, cy-r, 2*r, 2*r), math.radians(20), math.radians(160), 3)
                elif spell.icon == 'curse':
                    # Посох трясётся в диагональном положении над целью
                    cx, cy = icon_box.center
                    pygame.draw.line(book_surface, (80,60,60), (cx, cy+10), (cx, cy-5), 4)
                    pygame.draw.circle(book_surface, (220,220,220), (cx, cy-7), 6)
                    pygame.draw.circle(book_surface, (200,0,0), (cx-2, cy-8), 2) # glowing eye
                    pygame.draw.circle(book_surface, (200,0,0), (cx+2, cy-8), 2) # glowing eye
                    pygame.draw.arc(book_surface, (120,0,0), (cx-4, cy-11, 8, 6), math.radians(200), math.radians(340), 2)
                    for i in range(7):
                        angle = math.radians(i*51)
                        px = cx + int(12*math.cos(angle))
                        py = cy + int(12*math.sin(angle))
                        pygame.draw.circle(book_surface, (200,0,0), (px, py), 2)
                elif spell.icon == 'slow':
                    # Терновые корни с тенью и деталями
                    cx, cy = icon_box.center
                    for i in range(7):
                        angle = math.radians(30*i-90)
                        length = 13 + (i%2)*6
                        ex = cx + int(length*math.cos(angle))
                        ey = cy + int(length*math.sin(angle))
                        pygame.draw.line(book_surface, (60,40,20), (cx, cy), (ex, ey), 5)
                        pygame.draw.line(book_surface, (30,20,10), (cx, cy+2), (ex, ey+2), 2)
                        for j in range(2):
                            leaf_angle = angle + math.radians(15*(j*2-1))
                            lx = ex + int(6*math.cos(leaf_angle))
                            ly = ey + int(6*math.sin(leaf_angle))
                            pygame.draw.ellipse(book_surface, (60,120,60), (lx-2, ly-4, 4, 8))
                elif spell.icon == 'firearrow':
                    # Детализированная огненная стрела с градиентом и пламенем
                    cx, cy = icon_box.center
                    # Древко
                    for i in range(3):
                        pygame.draw.line(book_surface, (180,120+20*i,40), (cx-8, cy+5-i), (cx+7, cy-5-i), 2)
                    # Перо
                    pygame.draw.polygon(book_surface, (255,180,60), [(cx-8, cy+5), (cx-11, cy+8), (cx-5, cy+7)])
                    pygame.draw.polygon(book_surface, (255,220,120), [(cx-7, cy+6), (cx-10, cy+9), (cx-6, cy+8)])
                    # Наконечник
                    pygame.draw.polygon(book_surface, (255,255,255), [(cx+7, cy-5), (cx+12, cy-8), (cx+9, cy-1)])
                    pygame.draw.polygon(book_surface, (200,200,200), [(cx+8, cy-4), (cx+11, cy-7), (cx+9, cy-2)])
                    # Пламя
                    pygame.draw.polygon(book_surface, (255,80,20), [(cx+7, cy-5), (cx+13, cy-11), (cx+10, cy-2)])
                    pygame.draw.polygon(book_surface, (255,180,60), [(cx+9, cy-4), (cx+12, cy-7), (cx+10, cy-1)])
                    pygame.draw.polygon(book_surface, (255,220,120), [(cx+10, cy-5), (cx+13, cy-9), (cx+11, cy-3)])
                elif spell.icon == 'heal':
                    # Иконка исцеления: зелёный кружок
                    pygame.draw.ellipse(book_surface, (120,255,120), icon_rect.inflate(-24,-24), 0)
                    pygame.draw.polygon(book_surface, (60,255,60), [icon_rect.topleft, icon_rect.topright, icon_rect.midbottom])
                    pygame.draw.circle(book_surface, (120,255,120), icon_rect.center, 10)
                elif spell.icon == 'shield':
                    # Иконка щита: синий кружок
                    pygame.draw.ellipse(book_surface, (120,120,255), icon_rect.inflate(-24,-24), 0)
                    pygame.draw.polygon(book_surface, (60,60,255), [icon_rect.topleft, icon_rect.topright, icon_rect.midbottom])
                    pygame.draw.circle(book_surface, (120,120,255), icon_rect.center, 10)
                elif spell.icon == 'rune_shield':
                    # Камень с зелёным руническим знаком и белыми частицами
                    cx, cy = icon_box.center
                    pygame.draw.ellipse(book_surface, (80,200,80), icon_box, 0)  # камень
                    pygame.draw.ellipse(book_surface, (40,100,40), icon_box.inflate(-8,-8), 2)
                    # Рунический знак (щит)
                    pygame.draw.polygon(book_surface, (60,255,120), [
                        (cx-6, cy-6), (cx+6, cy-6), (cx+8, cy+4), (cx, cy+10), (cx-8, cy+4)
                    ])
                    # Белые частицы
                    for i in range(7):
                        angle = math.radians(i*51)
                        px = cx + int(13*math.cos(angle))
                        py = cy + int(13*math.sin(angle))
                        pygame.draw.circle(book_surface, (255,255,255,180), (px, py), 2)
                elif spell.icon == 'rune_haste':
                    # Камень с белым руническим знаком и жёлтыми частицами
                    cx, cy = icon_box.center
                    pygame.draw.ellipse(book_surface, (200,200,200), icon_box, 0)  # камень
                    pygame.draw.ellipse(book_surface, (120,120,120), icon_box.inflate(-8,-8), 2)
                    # Рунический знак (молния)
                    pygame.draw.lines(book_surface, (255,255,255), False, [
                        (cx-5, cy-4), (cx, cy+2), (cx-2, cy+2), (cx+5, cy+10)
                    ], 3)
                    # Жёлтые частицы
                    for i in range(7):
                        angle = math.radians(i*51)
                        px = cx + int(13*math.cos(angle))
                        py = cy + int(13*math.sin(angle))
                        pygame.draw.circle(book_surface, (255,255,120,180), (px, py), 2)
                elif spell.icon == 'forget':
                    # Фиолетовый туман
                    cx, cy = icon_box.center
                    for i in range(10):
                        angle = math.radians(i*36)
                        dx = cx + int(10 * math.cos(angle))
                        dy = cy + int(10 * math.sin(angle))
                        pygame.draw.circle(book_surface, (120,0,120,120), (dx, dy), 7)
                    pygame.draw.ellipse(book_surface, (180,0,180,180), icon_box, 2)
                # --- Подсветка при наведении ---
                if pygame.Rect(book_x+sx, book_y+sy, spell_size, spell_size).collidepoint(mouse):
                    pygame.draw.rect(book_surface, (255,255,120), icon_rect, 4)
                    # Типтул с описанием заклинания
                    font2 = pygame.font.Font(None, 22)
                    # --- Dynamic values for tooltip ---
                    hero = self.selected_unit if isinstance(self.selected_unit, Hero) else None
                    spell_power = getattr(hero, 'spell_power', 0) if hero else 0
                    knowledge = getattr(hero, 'knowledge', 0) if hero else 0
                    tip_lines = [spell.name, f"Мана: {spell.mana_cost}"]
                    # Bless/Curse/Shield/Slow: duration
                    if spell.icon in ('bless', 'curse', 'shield', 'slow', 'rune_shield', 'rune_haste'):
                        base_dur = spell.duration
                        bonus = spell_power
                        final_dur = base_dur + bonus
                        dur_str = f"{base_dur}" + (f" ({final_dur})" if bonus else "")
                        if spell.icon == 'bless':
                            tip_lines.append(f"+25% к атаке на {dur_str} {pluralize(final_dur, ['ход', 'хода', 'ходов'])}")
                        elif spell.icon == 'curse':
                            tip_lines.append(f"-25% к атаке на {dur_str} {pluralize(final_dur, ['ход', 'хода', 'ходов'])}")
                        elif spell.icon == 'shield' or spell.icon == 'rune_shield':
                            tip_lines.append(f"+15 к защите на {dur_str} {pluralize(final_dur, ['ход', 'хода', 'ходов'])}")
                        elif spell.icon == 'slow':
                            tip_lines.append(f"-5 инициативы и -1 скорость на {dur_str} {pluralize(final_dur, ['ход', 'хода', 'ходов'])}")
                        elif spell.icon == 'rune_haste':
                            tip_lines.append(f"+2 скорость и +5 инициатива на {dur_str} {pluralize(final_dur, ['ход', 'хода', 'ходов'])}")
                    elif spell.icon in ('firearrow', 'fireball'):
                        base_dmg = spell.damage
                        bonus = spell_power * 5
                        final_dmg = base_dmg + bonus
                        dmg_str = f"{base_dmg}" + (f" ({final_dmg})" if bonus else "")
                        tip_lines.append(f"Урон: {dmg_str}")
                        if spell.icon == 'fireball':
                            tip_lines.append("Дальность: 3 клетки")
                    elif spell.icon == 'heal':
                        tip_lines.append("Восстанавливает 25 здоровья союзнику.")
                    if spell.icon not in ('bless', 'curse', 'shield', 'slow', 'firearrow', 'fireball', 'heal', 'rune_shield', 'rune_haste'):
                        tip_lines.append(spell.description)
                    # Автоматическое увеличение высоты типтула
                    tip_w = max(font2.size(line)[0] for line in tip_lines) + 24
                    tip_h = 28 * len(tip_lines) + 16
                    tiptul = pygame.Surface((tip_w, tip_h), pygame.SRCALPHA)
                    tiptul.fill((0,0,0,220))
                    for j, line in enumerate(tip_lines):
                        tiptul.blit(font2.render(line, True, (255,255,200)), (12, 10 + j*28))
                    tx = book_x + sx + spell_size + 10
                    ty = book_y + sy
                    if tx + tip_w > SCREEN_WIDTH:
                        tx = book_x + sx - tip_w - 10
                    if ty + tip_h > SCREEN_HEIGHT:
                        ty = SCREEN_HEIGHT - tip_h
                    tiptul_rect = (tx, ty)
            # --- Отрисовка типтула ---
            if tiptul and tiptul_rect:
                if not isinstance(tiptul_rect, pygame.Rect):
                    tiptul_rect = pygame.Rect(tiptul_rect[0], tiptul_rect[1], tiptul.get_width(), tiptul.get_height())
                # Убрать прозрачность
                s = pygame.Surface((tiptul_rect.width, tiptul_rect.height), pygame.SRCALPHA)
                s.fill((40,40,80,255))
                s.blit(tiptul, (0,0))
                self.screen.blit(s, tiptul_rect)
            self.screen.blit(book_surface, (book_x, book_y))
        # Кнопка истории
        pygame.draw.rect(self.screen, (80, 120, 200), self.history_button_rect, border_radius=8)
        font_hist = pygame.font.Font(None, 32)
        self.screen.blit(font_hist.render('H', True, (255,255,255)), (self.history_button_rect.x+14, self.history_button_rect.y+8))
        # Если открыта панель истории
        if self.history_panel_open:
            self.draw_history_panel()
        # Лента: кто ходит сейчас
        label = None
        if hasattr(self, 'turn_queue'):
            active = self.turn_queue[0]
            label = f"Ходит: {active.unit_type.capitalize()} ({TEAM_LABELS.get(active.team, active.team)})"
        elif hasattr(self, 'initiative_queue') and self.initiative_queue:
            active = self.initiative_queue[self.current_initiative_index]
            label = f"Ходит: {active.unit_type.capitalize()} ({TEAM_LABELS.get(active.team, active.team)})"
        elif self.selected_unit:
            # Если нет очереди, но есть выбранный юнит
            label = f"Выбран: {self.selected_unit.unit_type.capitalize()} ({TEAM_LABELS.get(self.selected_unit.team, self.selected_unit.team)})"
        if label:
            surf = self.font.render(label, True, (255,255,180))
            self.screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, SCREEN_HEIGHT - 80 + 50))
        # Меню
        if self.menu_open:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))
            # Увеличенное меню для Esc-меню
            menu_w, menu_h = 320, 260
            self.menu_rect = pygame.Rect((SCREEN_WIDTH-menu_w)//2, (SCREEN_HEIGHT-menu_h)//2, menu_w, menu_h)
            pygame.draw.rect(self.screen, (40, 40, 80), self.menu_rect, border_radius=12)
            menu_text = self.font.render("Меню", True, WHITE)
            self.screen.blit(menu_text, (self.menu_rect.x + 80, self.menu_rect.y + 10))
            # Кнопки вертикально друг под другом
            font = pygame.font.Font(None, 32)
            btn_w, btn_h, btn_gap = 180, 40, 18
            btn_x = self.menu_rect.x + (menu_w-btn_w)//2
            btn_y = self.menu_rect.y + 50
            # Во весь экран
            fullscreen_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            pygame.draw.rect(self.screen, (120, 180, 220), fullscreen_rect, border_radius=8)
            self.screen.blit(font.render('Во весь экран (F)', True, (255,255,255)), (fullscreen_rect.x + 10, fullscreen_rect.y + 5))
            self.fullscreen_button_rect = fullscreen_rect
            # Новая игра
            newgame_rect = pygame.Rect(btn_x, btn_y + btn_h + btn_gap, btn_w, btn_h)
            pygame.draw.rect(self.screen, (60, 200, 60), newgame_rect, border_radius=8)
            self.screen.blit(font.render('Новая игра', True, (255,255,255)), (newgame_rect.x + 10, newgame_rect.y + 5))
            self.newgame_button_rect = newgame_rect
            # Выйти
            exit_rect = pygame.Rect(btn_x, btn_y + 2*(btn_h + btn_gap), btn_w, btn_h)
            pygame.draw.rect(self.screen, (200, 60, 60), exit_rect, border_radius=8)
            self.screen.blit(font.render('Выйти', True, (255,255,255)), (exit_rect.x + 40, exit_rect.y + 5))
            self.exit_button_rect = exit_rect

    def draw_menu(self):
        self.screen.fill((60, 120, 180))
        # --- Величественный замок (слева, люди) ---
        # Стены
        pygame.draw.rect(self.screen, (180,180,200), (60, 220, 80, 120), border_radius=8)
        pygame.draw.rect(self.screen, (160,160,180), (50, 200, 20, 120), border_radius=6)
        pygame.draw.rect(self.screen, (160,160,180), (130, 200, 20, 120), border_radius=6)
        # Башни
        pygame.draw.rect(self.screen, (200,200,220), (45, 170, 30, 60), border_radius=10)
        pygame.draw.rect(self.screen, (200,200,220), (125, 170, 30, 60), border_radius=10)
        # Крыши башен
        pygame.draw.polygon(self.screen, (120,120,180), [(45,170),(60,150),(75,170)])
        pygame.draw.polygon(self.screen, (120,120,180), [(125,170),(140,150),(155,170)])
        # Зубцы
        for x in range(60, 140, 16):
            pygame.draw.rect(self.screen, (220,220,240), (x, 220, 10, 16), border_radius=2)
        # Окна
        for wx in [70, 90, 110]:
            pygame.draw.rect(self.screen, (100,100,140), (wx, 250, 10, 20), border_radius=3)
        # Ворота
        pygame.draw.rect(self.screen, (120,100,60), (90, 310, 20, 30), border_radius=6)
        pygame.draw.arc(self.screen, (100,80,40), (90, 300, 20, 20), 3.14, 0, 3)
        # Флаг
        pygame.draw.line(self.screen, (80,80,200), (100,150), (100,120), 4)
        pygame.draw.polygon(self.screen, (255,0,0), [(100,120),(130,130),(100,140)])
        # --- Величественный замок (справа, нежить) ---
        pygame.draw.rect(self.screen, (120,120,160), (660, 220, 80, 120), border_radius=8)
        pygame.draw.rect(self.screen, (80,80,120), (650, 200, 20, 120), border_radius=6)
        pygame.draw.rect(self.screen, (80,80,120), (740, 200, 20, 120), border_radius=6)
        pygame.draw.rect(self.screen, (180,180,200), (655, 170, 30, 60), border_radius=10)
        pygame.draw.rect(self.screen, (180,180,200), (735, 170, 30, 60), border_radius=10)
        pygame.draw.polygon(self.screen, (80,40,120), [(655,170),(670,150),(685,170)])
        pygame.draw.polygon(self.screen, (80,40,120), [(735,170),(750,150),(765,170)])
        for x in range(670, 740, 16):
            pygame.draw.rect(self.screen, (200,200,220), (x, 220, 10, 16), border_radius=2)
        for wx in [680, 700, 720]:
            pygame.draw.rect(self.screen, (80,60,120), (wx, 250, 10, 20), border_radius=3)
        pygame.draw.rect(self.screen, (60,40,100), (690, 310, 20, 30), border_radius=6)
        pygame.draw.arc(self.screen, (40,20,60), (690, 300, 20, 20), 3.14, 0, 3)
        pygame.draw.line(self.screen, (120,40,120), (700,150), (700,120), 4)
        pygame.draw.polygon(self.screen, (180,120,255), [(700,120),(730,130),(700,140)])
        # --- Левый рыцарь на коне (люди, HoMM3 стиль) ---
        # Тело коня
        pygame.draw.ellipse(self.screen, (120,80,40), (170, 340, 70, 28))
        # Голова
        pygame.draw.ellipse(self.screen, (120,80,40), (230, 330, 24, 16))
        # Шея
        pygame.draw.polygon(self.screen, (120,80,40), [(220,350),(240,340),(240,345),(225,355)])
        # Ноги
        pygame.draw.rect(self.screen, (80,60,30), (180, 362, 8, 28), border_radius=3)
        pygame.draw.rect(self.screen, (80,60,30), (210, 362, 8, 28), border_radius=3)
        pygame.draw.rect(self.screen, (80,60,30), (240, 362, 8, 28), border_radius=3)
        pygame.draw.rect(self.screen, (80,60,30), (260, 362, 8, 28), border_radius=3)
        # Копыта
        for x in [180,210,240,260]:
            pygame.draw.ellipse(self.screen, (60,40,20), (x, 388, 8, 6))
        # Хвост
        pygame.draw.polygon(self.screen, (100,60,30), [(170,355),(160,370),(175,370)])
        # Грива
        for i in range(5):
            pygame.draw.line(self.screen, (200,180,100), (230+i*4,332), (232+i*4,325), 2)
        # Всадник
        pygame.draw.rect(self.screen, (180,160,100), (210, 310, 20, 30), border_radius=6)
        pygame.draw.circle(self.screen, (255,224,189), (220, 305), 10)
        pygame.draw.rect(self.screen, (120,120,160), (215, 320, 10, 18), border_radius=4)
        pygame.draw.polygon(self.screen, (255,215,0), [(220,305),(230,295),(210,295)])
        # Щит
        pygame.draw.ellipse(self.screen, (60,60,200), (200, 325, 18, 24))
        # Копьё
        pygame.draw.line(self.screen, (180,180,180), (240,320), (280,270), 6)
        pygame.draw.polygon(self.screen, (200,200,220), [(280,270),(288,265),(282,278)])
        # --- Правый рыцарь на коне (нежить, HoMM3 стиль) ---
        pygame.draw.ellipse(self.screen, (80,40,120), (570, 340, 70, 28))
        pygame.draw.ellipse(self.screen, (80,40,120), (630, 330, 24, 16))
        pygame.draw.polygon(self.screen, (80,40,120), [(620,350),(650,340),(650,345),(625,355)])
        pygame.draw.rect(self.screen, (40,20,60), (580, 362, 8, 28), border_radius=3)
        pygame.draw.rect(self.screen, (40,20,60), (610, 362, 8, 28), border_radius=3)
        pygame.draw.rect(self.screen, (40,20,60), (640, 362, 8, 28), border_radius=3)
        pygame.draw.rect(self.screen, (40,20,60), (660, 362, 8, 28), border_radius=3)
        for x in [580,610,640,660]:
            pygame.draw.ellipse(self.screen, (20,10,40), (x, 388, 8, 6))
        pygame.draw.polygon(self.screen, (80,60,120), [(570,355),(560,370),(575,370)])
        for i in range(5):
            pygame.draw.line(self.screen, (180,120,255), (630+i*4,332), (632+i*4,325), 2)
        pygame.draw.rect(self.screen, (120,100,180), (610, 310, 20, 30), border_radius=6)
        pygame.draw.circle(self.screen, (200,200,220), (620, 305), 10)
        pygame.draw.rect(self.screen, (80,60,120), (615, 320, 10, 18), border_radius=4)
        pygame.draw.polygon(self.screen, (180,120,255), [(620,305),(630,295),(610,295)])
        pygame.draw.ellipse(self.screen, (80,60,120), (600, 325, 18, 24))
        pygame.draw.line(self.screen, (180,180,180), (650,320), (690,270), 6)
        pygame.draw.polygon(self.screen, (200,200,220), [(690,270),(698,265),(692,278)])
        # --- Название и кнопки ---
        title = self.font.render('Фэнтези Битва', True, (255,255,255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
        # Кнопка "Новая игра" — шире и центрирована
        btn_w, btn_h = 200, 48
        btn_x = SCREEN_WIDTH//2 - btn_w//2
        btn_y = 180
        self.start_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, (60, 200, 60), self.start_button_rect, border_radius=8)
        start_text = self.font.render('Новая игра', True, (255,255,255))
        self.screen.blit(start_text, (btn_x + (btn_w - start_text.get_width())//2, btn_y + 8))
        # Кнопка "Выход"
        exit_btn_w, exit_btn_h = 160, 44
        exit_btn_x = SCREEN_WIDTH//2 - exit_btn_w//2
        exit_btn_y = btn_y + btn_h + 24
        self.exit_button_rect = pygame.Rect(exit_btn_x, exit_btn_y, exit_btn_w, exit_btn_h)
        pygame.draw.rect(self.screen, (200, 60, 60), self.exit_button_rect, border_radius=8)
        exit_text = self.font.render('Выход', True, (255,255,255))
        self.screen.blit(exit_text, (self.exit_button_rect.x + 20, self.exit_button_rect.y + 5))
        # (Кнопка "Во весь экран" убрана из основного меню)

    def draw_history_panel(self):
        # Отдельная большая панель истории событий
        panel_w, panel_h = 600, 400
        panel_x = (SCREEN_WIDTH - panel_w)//2
        panel_y = (SCREEN_HEIGHT - panel_h)//2
        pygame.draw.rect(self.screen, (30,30,60), (panel_x, panel_y, panel_w, panel_h), border_radius=16)
        font = pygame.font.Font(None, 22)
        lines = min(len(self.event_log), 18)
        offset = self.event_log_offset
        max_offset = max(0, len(self.event_log) - lines)
        offset = max(0, min(offset, max_offset))
        for i in range(lines):
            idx = len(self.event_log) - 1 - offset - i
            if idx >= 0:
                text = self.event_log[idx]
                color = (255,220,120) if text.startswith('===') else (220,220,220)
                surf = font.render(text.replace('===','').strip() if text.startswith('===' ) else text, True, color)
                self.screen.blit(surf, (panel_x+30, panel_y+30 + i*22))
        # Кнопка закрытия
        close_rect = pygame.Rect(panel_x+panel_w-40, panel_y+10, 30, 30)
        pygame.draw.rect(self.screen, (200,60,60), close_rect, border_radius=8)
        self.screen.blit(font.render('X', True, (255,255,255)), (close_rect.x+7, close_rect.y+2))
        # Стрелки прокрутки
        if len(self.event_log) > lines:
            arrow_up = pygame.Rect(panel_x+panel_w-40, panel_y+60, 30, 20)
            arrow_down = pygame.Rect(panel_x+panel_w-40, panel_y+panel_h-60, 30, 20)
            pygame.draw.polygon(self.screen, (200,200,120), [(arrow_up.x+15, arrow_up.y+4), (arrow_up.x+4, arrow_up.y+16), (arrow_up.x+26, arrow_up.y+16)])
            pygame.draw.polygon(self.screen, (200,200,120), [(arrow_down.x+15, arrow_down.y+16), (arrow_down.x+4, arrow_down.y+4), (arrow_down.x+26, arrow_down.y+4)])
        self.history_panel_close_rect = close_rect
        self.history_panel_arrow_up = arrow_up if len(self.event_log) > lines else None
        self.history_panel_arrow_down = arrow_down if len(self.event_log) > lines else None

    def draw(self):
        if self.state == 'menu':
            self.draw_menu()
            pygame.display.flip()
            return
        if self.state == 'choose_race_p1':
            self.draw_choose_race(player=1)
            pygame.display.flip()
            return
        if self.state == 'choose_race_p2':
            self.draw_choose_race(player=2)
            pygame.display.flip()
            return
        self.screen.blit(self.background, (0, 0))
        t = pygame.time.get_ticks() / 1000.0
        draw_animated_grass(self.screen, t)
        self.draw_grid()
        for unit in self.units:
            unit.draw(self.screen)
        # --- Отдельный проход для типтулов, чтобы они были поверх ---
        mouse_pos = pygame.mouse.get_pos()
        for unit in self.units:
            if getattr(unit, 'show_tooltip', False):
                unit.draw_tooltip(self.screen, mouse_pos)
        self.draw_ui()
        # Отрисовка отладочной информации поверх всего
        self.debugger.draw_debug_overlay(self.screen)
        pygame.display.flip()

    def check_game_over(self):
        # Проигрыш героя, если все его юниты погибли
        heroes = [u for u in self.units if isinstance(u, Hero)]
        for hero in heroes:
            allies = [u for u in self.units if u.team == hero.team and u != hero]
            if not allies:
                self.game_over = True
                winner = [h for h in heroes if h != hero][0].team if len(heroes) > 1 else 'Никто'
                print(f"Игра окончена! Победили {TEAM_LABELS.get(winner, winner)}!")
                return

    def handle_click(self, pos):
        # Проверяем, не должен ли текущий юнит пропустить ход из-за забвения
        if self.selected_unit and not isinstance(self.selected_unit, Hero):
            if getattr(self.selected_unit, 'forget_turns', 0) > 0:
                self.selected_unit.forget_turns -= 1
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} пропускает ход из-за забвения")
                # Принудительно переходим к следующему ходу
                self.next_turn()
                return
        # Кнопка истории
        wait_button_rect = pygame.Rect(self.skip_button_rect.x - 70, self.skip_button_rect.y, 48, 48)
        if self.history_button_rect.collidepoint(pos):
            self.history_panel_open = True
            return
        # Если открыта панель истории
        if self.history_panel_open:
            if self.history_panel_close_rect.collidepoint(pos):
                self.history_panel_open = False
                return
            if self.history_panel_arrow_up and self.history_panel_arrow_up.collidepoint(pos):
                self.event_log_offset = min(self.event_log_offset + 1, max(0, len(self.event_log)-18))
                return
            if self.history_panel_arrow_down and self.history_panel_arrow_down.collidepoint(pos):
                self.event_log_offset = max(self.event_log_offset - 1, 0)
                return
        if self.state == 'menu':
            if self.start_button_rect.collidepoint(pos):
                self.state = 'choose_race_p1'
                return
            if self.exit_button_rect.collidepoint(pos):
                pygame.quit()
                exit()
            return
        if self.state == 'choose_race_p1':
            for i, (race, _, _) in enumerate(self.sorted_races):
                if self.race_rects[i].collidepoint(pos):
                    self.player1_race = race
                    self.state = 'choose_race_p2'
                    return
            return
        if self.state == 'choose_race_p2':
            for i, (race, _, _) in enumerate(self.sorted_races):
                if self.race_rects[i].collidepoint(pos) and race != self.player1_race:
                    self.player2_race = race
                    self.state = 'game'
                    self.background = self.generate_battlefield()
                    self.initialize_units(self.player1_race, self.player2_race)
                    self.prepare_initiative_queue()
                    if hasattr(self, 'turn_queue') and self.turn_queue:
                        self.selected_unit = self.turn_queue[0]
                    return
            return
        if self.menu_open:
            if self.exit_button_rect.collidepoint(pos):
                pygame.quit()
                exit()
            if hasattr(self, 'fullscreen_button_rect') and self.fullscreen_button_rect.collidepoint(pos):
                pygame.display.toggle_fullscreen()
                return
            if hasattr(self, 'newgame_button_rect') and self.newgame_button_rect.collidepoint(pos):
                self.start_new_game()
                self.menu_open = False
                return
            if not self.menu_rect.collidepoint(pos):
                self.menu_open = False
            return
        # Книга заклинаний можно открывать для любого героя с заклинаниями, если не использовано в этом раунде
        if (isinstance(self.selected_unit, Hero)
            and self.selected_unit.spells
            and not getattr(self.selected_unit, 'used_spell_this_round', False)
            and self.book_button_rect.collidepoint(pos)):
            self.spellbook_open = not self.spellbook_open
            return
        # Если открыта книга — выбор заклинания
        if self.spellbook_open and isinstance(self.selected_unit, Hero) and self.selected_unit.spells:
            book_w, book_h = 600, 400
            book_x = (SCREEN_WIDTH - book_w)//2
            book_y = (SCREEN_HEIGHT - book_h)//2
            spell_size = 64
            # --- Обработка клика по крестику ---
            if hasattr(self, 'spellbook_close_rect') and self.spellbook_close_rect.collidepoint(pos):
                self.spellbook_open = False
                return
            # --- Обработка клика по закладкам школ ---
            school_list = [
                'all', 'fire', 'water', 'earth', 'air', 'light', 'darkness', 'rune'
            ]
            tab_w, tab_h = 56, 48
            for i, school in enumerate(school_list):
                tab_x = book_x + 20 + i*(tab_w+8)
                tab_y = book_y - 36
                spells = self.selected_unit.spells
                has_spells = any(s for s in spells if school == 'all' or getattr(s, 'school', None) == school)
                if has_spells and pygame.Rect(tab_x, tab_y, tab_w, tab_h).collidepoint(pos):
                    self.spellbook_selected_school = school
                    self.spellbook_page = 0
                    return
            # --- Выбор заклинания ---
            spells = self.selected_unit.spells
            selected_school = getattr(self, 'spellbook_selected_school', 'all')
            filtered_spells = [s for s in spells if selected_school == 'all' or getattr(s, 'school', None) == selected_school]
            spells_per_page = 6
            columns = 2
            rows = 3
            page = getattr(self, 'spellbook_page', 0)
            start_idx = page * spells_per_page
            end_idx = min(start_idx + spells_per_page, len(filtered_spells))
            for i, spell in enumerate(filtered_spells[start_idx:end_idx]):
                col = i % columns
                row = i // columns
                sx = book_x + (60 if col == 0 else (book_w//2 + 36))
                sy = book_y + 60 + row * 100
                icon_rect = pygame.Rect(sx, sy, spell_size, spell_size)
                if icon_rect.collidepoint(pos):
                    self.selected_unit.selected_spell = self.selected_unit.spells.index(spell)
                    self.spellbook_open = False
                    return
            # --- Удалить закрытие книги по клику вне книги ---
            # (больше не закрываем книгу по клику вне области)
            # book_rect = pygame.Rect(book_x, book_y, book_w, book_h)
            # if not book_rect.collidepoint(pos):
            #     self.spellbook_open = False
            #     return
        # Если выбран spell — клик по клетке применяет заклинание
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # --- Запретить применение заклинаний на героев ---
            if target and isinstance(target, Hero):
                # Можно разрешить только если у заклинания есть специальный флаг (например, allow_hero_target)
                if not getattr(spell, 'allow_hero_target', False):
                    return
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # --- Анимация каста по типу заклинания ---
                school_colors = {
                    'fire': (255,80,40),
                    'earth': (80,180,60),
                    'light': (255,255,180),
                    'darkness': (200,0,0)
                }
                if hasattr(spell, 'school') and spell.school in school_colors:
                    self.animate_spell_flash(self.selected_unit, school_colors[spell.school])
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                    self.animate_explosion(target.x*CELL_SIZE+CELL_SIZE//2, target.y*CELL_SIZE+CELL_SIZE//2, (255,120,40))
                elif hasattr(spell, 'icon') and spell.icon == 'slow':
                    self.animate_roots(target)
                elif hasattr(spell, 'icon') and spell.icon == 'bless':
                    self.animate_water_bless(target)
                elif hasattr(spell, 'icon') and spell.icon == 'curse':
                    self.animate_curse(self.selected_unit, target)
                elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                    # Иконка снятия чар: синий круг, белая волна и крест
                    pygame.draw.ellipse(book_surface, (80,180,255), icon_rect.inflate(-24,-24), 0)
                    pygame.draw.arc(book_surface, (255,255,255), icon_rect.inflate(-16,-16), math.radians(30), math.radians(150), 4)
                    pygame.draw.line(book_surface, (255,255,255), (icon_rect.centerx-8, icon_rect.centery-8), (icon_rect.centerx+8, icon_rect.centery+8), 3)
                    pygame.draw.line(book_surface, (255,255,255), (icon_rect.centerx+8, icon_rect.centery-8), (icon_rect.centerx-8, icon_rect.centery+8), 3)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
            print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
        if clicked_unit is None:
            # Пустая клетка — попытка перемещения
            if self.selected_unit.can_move(x, y, self.units):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.selected_unit.move_points_left -= path_len
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} переместился на ({x},{y})")
                    if (self.selected_unit.move_points_left <= 0 and not self.can_attack_any(self.selected_unit)):
                        self.next_turn()
                    return
                else:
                    print('Недостаточно очков хода для перемещения!')
        elif clicked_unit.team != self.selected_unit.team:
            # Если выбран неатакующий spell — не атаковать
            if (isinstance(self.selected_unit, Hero)
                and self.selected_unit.selected_spell is not None):
                spell = self.selected_unit.spells[self.selected_unit.selected_spell]
                if getattr(spell, 'target_type', None) == 'ally':
                    return
            # Вражеский юнит — попытка атаки (герои не могут быть целью)
            if isinstance(clicked_unit, Hero):
                print('Нельзя атаковать героев!')
                return
            if self.selected_unit.can_attack(x, y, self.units):
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                    end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                    # Определяем тип снаряда в зависимости от юнита
                    if self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                    else:
                        # Маги и герои стреляют магическими снарядами с разными цветами
                        if self.selected_unit.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif self.selected_unit.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif self.selected_unit.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.draw()
                    pygame.display.flip()
                    damage = self.selected_unit.ranged_damage(x, y)
                else:
                    damage = self.selected_unit.attack
                if clicked_unit.take_damage(damage):
                    if clicked_unit in self.units:
                        self.units.remove(clicked_unit)
                        # Remove all occurrences from the turn queue
                        if hasattr(self, 'turn_queue'):
                            self.turn_queue = [u for u in self.turn_queue if u != clicked_unit]
                        # Анимация исчезновения иконки из очереди
                        self.animate_queue_fade(clicked_unit)
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type}")
                    self.check_game_over()
                else:
                    self.add_event(f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type}")
                self.selected_unit.has_attacked = True
                self.next_turn()
                return
            else:
                print('can_attack вернул False!')
        else:
            print('Клик по своему юниту — ничего не делаем')
        
        # Обработка кликов по кнопкам
        if wait_button_rect.collidepoint(pos):
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    return  # Уже ждал в этом раунде
                self.selected_unit.has_waited = True
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} перемещается в конец очереди")
                # Сохраняем старую очередь для анимации
                old_queue = self.turn_queue.copy() if hasattr(self, 'turn_queue') and self.turn_queue else []
                # Убираем текущего юнита из очереди
                if self.turn_queue:
                    self.turn_queue.pop(0)
                # Перемещаем юнита в конец очереди
                if self.selected_unit in self.turn_queue:
                    idx = self.turn_queue.index(self.selected_unit)
                    unit = self.turn_queue.pop(idx)
                    self.turn_queue.append(unit)
                else:
                    pass  # fix: ensure indented block exists
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    self.selected_unit = self.turn_queue[0]
                    # Сбрасываем флаги для нового активного юнита
                    self.selected_unit.has_moved = False
                    self.selected_unit.has_attacked = False
                    self.selected_unit.move_points_left = self.selected_unit.speed
                    self.selected_unit._defend_this_round = False
                return
        # Кнопка защиты (defend) - доступна для всех юнитов кроме героев (теперь на месте skip_button_rect)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            self.selected_unit.defense = int(self.selected_unit.defense * 1.3)
            self.selected_unit._defend_this_round = True
            self.add_event(f"{self.selected_unit.unit_type.capitalize()} встал в защиту")
            # Переходим к следующему ходу
            self.next_turn()
            return
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Найти цель
            target = None
            for unit in self.units:
                if unit.x == x and unit.y == y:
                    target = unit
                    break
            # Проверить условия применения (например, цель — враг/союзник)
            if spell.target_type == 'enemy' and target and target.team != self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Визуальный эффект для атакующих заклинаний
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(self.selected_unit, target)
                else:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                spell.apply(target, caster=self.selected_unit)
                self.selected_unit.mana -= spell.mana_cost
                self.selected_unit.selected_spell = None
                self.selected_unit.used_spell_this_round = True
                # Герой передает ход после использования заклинания
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != self.selected_unit.team:
                    return
                if target and target.team == self.selected_unit.team and self.selected_unit.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        self.animate_water_bless(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        self.animate_spell_flash(target, (80,180,255))
                    spell.apply(target, caster=self.selected_unit)
                    self.selected_unit.mana -= spell.mana_cost
                    self.selected_unit.selected_spell = None
                    self.selected_unit.used_spell_this_round = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
            # Если заклинание не может быть применено — ничего не делаем
            return
        
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        clicked_unit = None
        for unit in self.units:
            if unit.x == x and unit.y == y:
                clicked_unit = unit
                break
            pygame.time.delay(14)