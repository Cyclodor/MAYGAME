import pygame
from .config import *
from .units import Hero, Peasant, Spearman, Crossbowman, Swordsman, Gryphon, Skeleton, Zombie, Ghost, Vampire, Lich, Pixie, ElfScout, ElfArcher, Dryad, Ent, Imp, Gog, Demon, Cerberus, Succubus, Miner, Spearthrower, BearRider, RuneMage, Jarl, Scout, Beast, Minotaur, Witch, LizardRider
from .graphics import (
    draw_cell_texture,
    draw_animated_grass,
    animate_arrow,
    animate_magic_projectile,
    animate_arrow_fly,
    animate_fire_arrow_fly,
    animate_magic_fly,
    animate_stone_skin,
    animate_fire_explosion,
    animate_curse_voodoo,
    animate_raise_dead,
    animate_fireball,
    animate_bless_spell,
    animate_bless_spell_fly,
    animate_dispel_spell,
    animate_dispel_spell_fly,
    animate_slow_spell,
    animate_slow_spell_fly,
    animate_forget_spell,
    animate_forget_spell_fly,
    animate_rune_shield_spell,
    animate_rune_haste_spell,
    animate_frost_ring,
    animate_frost_impact,
)
from .spells import BlessSpell, CurseSpell, HealSpell, SlowSpell, FireArrowSpell, DispelSpell, RuneShieldSpell, RuneHasteSpell, ForgetSpell, FrostRingSpell, StoneSkinSpell, RaiseDeadSpell, FireballSpell
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
        self.area_preview_dismiss = False
        self.spellbook_rect = pygame.Rect(SCREEN_WIDTH - 150, 20, 140, 40)
        self.spellbook_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
        self.spellbook_surface.fill((0, 0, 0, 200))
        self.menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 60, 240, 120)
        self.exit_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 + 10, 120, 40)
        self.start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 - 40, 120, 40)
        self.round_number = 1
        # Разделитель раундов в очереди хода
        self._round_delimiter = object()
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
            'undead': [CurseSpell(), RaiseDeadSpell()],
            'elf': [SlowSpell(), StoneSkinSpell()],
            'demon': [FireArrowSpell(), FireballSpell()],
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
                if unit is self._round_delimiter:
                    # Разделительная перегородка раунда
                    pygame.draw.rect(self.screen, (160, 120, 60), (x + icon_size//2 - 2, y - 6, 4, icon_size + 12))
                    continue
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
                    # Иконка: человек с яркими волнами воды (максимальный контраст)
                    cx, cy = icon_box.center
                    # Силуэт с белым контуром
                    pygame.draw.circle(book_surface, (40,120,255), (cx, cy+6), 10)  # тело ещё насыщеннее
                    pygame.draw.circle(book_surface, (255,255,255), (cx, cy-6), 6)  # голова больше
                    # Очень яркие волны
                    for r in [16, 22]:
                        pygame.draw.arc(book_surface, (60,160,255), (cx-r, cy-r, 2*r, 2*r), math.radians(200), math.radians(340), 5)
                        pygame.draw.arc(book_surface, (240,250,255), (cx-r, cy-r, 2*r, 2*r), math.radians(20), math.radians(160), 5)
                    # Толстый белый контур фигуры
                    pygame.draw.circle(book_surface, (255,255,255), (cx, cy+6), 10, 3)
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
                elif spell.icon == 'fireball':
                    # Пылающий шар, падающий сверху
                    cx, cy = icon_box.center
                    # Шар (ядро)
                    pygame.draw.circle(book_surface, (255, 80, 20), (cx, cy), 12)
                    pygame.draw.circle(book_surface, (255, 160, 60), (cx, cy), 8)
                    pygame.draw.circle(book_surface, (255, 220, 120), (cx, cy), 4)
                    # Хвост пламени (несколько языков)
                    for angle_offset in [0, 0.5, 1.0]:
                        ang = angle_offset
                        flame_x = cx + int(10 * math.cos(ang))
                        flame_y = cy + 8
                        pygame.draw.polygon(book_surface, (255, 120, 40), [
                            (flame_x, flame_y), (flame_x-3, flame_y+8), (flame_x+3, flame_y+8)
                        ])
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
                elif spell.icon == 'stone_skin':
                    # Каменная кожа: щит-валун
                    cx, cy = icon_box.center
                    pygame.draw.ellipse(book_surface, (140, 130, 120), (cx-12, cy-10, 24, 20))
                    for a in [(-8,-4),(0,0),(6,-2)]:
                        pygame.draw.circle(book_surface, (120,110,100), (cx+a[0], cy+a[1]), 3)
                elif spell.icon == 'frost_ring':
                    # Кольцо холода: синее кольцо с пустым центром
                    cx, cy = icon_box.center
                    pygame.draw.circle(book_surface, (120, 200, 255), (cx, cy), 12, 3)
                    pygame.draw.circle(book_surface, (180, 220, 255), (cx, cy), 6, 2)
                elif spell.icon == 'raise_dead':
                    # Поднятие мертвецов: костлявая рука
                    cx, cy = icon_box.center
                    pygame.draw.rect(book_surface, (200,200,200), (cx-2, cy-8, 4, 14))
                    for dx in [-4,0,4]:
                        pygame.draw.rect(book_surface, (200,200,200), (cx+dx-1, cy-10, 2, 8))
                # --- Подсветка при наведении ---
                if pygame.Rect(book_x+sx, book_y+sy, spell_size, spell_size).collidepoint(mouse):
                    pygame.draw.rect(book_surface, (255,255,120), icon_rect, 4)
                    # Типтул с описанием заклинания (компактная версия)
                    font2 = pygame.font.Font(None, 20)
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
                            tip_lines.append("Зона: 3×3 клетки")
                    elif spell.icon == 'heal':
                        tip_lines.append("Восстанавливает 25 здоровья союзнику.")
                    if spell.icon not in ('bless', 'curse', 'shield', 'slow', 'firearrow', 'fireball', 'heal', 'rune_shield', 'rune_haste'):
                        tip_lines.append(spell.description)
                    # Автоматическое увеличение высоты типтула
                    tip_w = max(font2.size(line)[0] for line in tip_lines) + 16
                    tip_h = 20 * len(tip_lines) + 12
                    tiptul = pygame.Surface((tip_w, tip_h), pygame.SRCALPHA)
                    tiptul.fill((10,10,24,240))
                    for j, line in enumerate(tip_lines):
                        tiptul.blit(font2.render(line, True, (255,255,220)), (8, 6 + j*20))
                    tx = book_x + sx + spell_size + 10
                    ty = book_y + sy
                    if tx + tip_w > SCREEN_WIDTH:
                        tx = book_x + sx - tip_w - 10
                    if ty + tip_h > SCREEN_HEIGHT:
                        ty = SCREEN_HEIGHT - tip_h
                    tiptul_rect = (tx, ty)
            # Сначала книга, затем типтул поверх
            self.screen.blit(book_surface, (book_x, book_y))
            if tiptul and tiptul_rect:
                if not isinstance(tiptul_rect, pygame.Rect):
                    tiptul_rect = pygame.Rect(tiptul_rect[0], tiptul_rect[1], tiptul.get_width(), tiptul.get_height())
                s = pygame.Surface((tiptul_rect.width, tiptul_rect.height), pygame.SRCALPHA)
                s.fill((40,40,80,255))
                s.blit(tiptul, (0,0))
                self.screen.blit(s, tiptul_rect)
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
        # Меню внутри игры (деревянное средневековое в стиле главного меню)
        if self.menu_open:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((30, 20, 10, 200))
            self.screen.blit(overlay, (0,0))
            # Панель меню
            menu_w, menu_h = 380, 340
            self.menu_rect = pygame.Rect((SCREEN_WIDTH-menu_w)//2, (SCREEN_HEIGHT-menu_h)//2, menu_w, menu_h)
            # Градиент для панели
            for y_offset in range(menu_h):
                panel_gradient = (
                    int(150 - y_offset * 0.2),
                    int(110 - y_offset * 0.15),
                    int(80 - y_offset * 0.1)
                )
                pygame.draw.line(self.screen, panel_gradient,
                               (self.menu_rect.x, self.menu_rect.y + y_offset),
                               (self.menu_rect.x + menu_w, self.menu_rect.y + y_offset))
            pygame.draw.rect(self.screen, (70, 50, 35), self.menu_rect, 6, border_radius=16)
            inner_panel = pygame.Rect(self.menu_rect.x + 4, self.menu_rect.y + 4, menu_w - 8, menu_h - 8)
            pygame.draw.rect(self.screen, (170, 140, 110), inner_panel, 2, border_radius=14)
            # Узор на панели
            for i in range(5):
                x_pos = self.menu_rect.x + 30 + i * 70
                pygame.draw.line(self.screen, (100, 80, 60), (x_pos, self.menu_rect.y + 40), (x_pos, self.menu_rect.y + menu_h - 30), 2)
                for j in range(2):
                    knot_y = self.menu_rect.y + 60 + j * 100
                    pygame.draw.circle(self.screen, (90, 70, 50), (x_pos, knot_y), 3)
            # Заголовок
            title_font = pygame.font.Font(None, 48)
            menu_title = title_font.render("МЕНЮ", True, (255, 245, 220))
            title_shadow = title_font.render("МЕНЮ", True, (60, 50, 40))
            self.screen.blit(title_shadow, (self.menu_rect.x + (menu_w - menu_title.get_width())//2 + 2, self.menu_rect.y + 18))
            self.screen.blit(menu_title, (self.menu_rect.x + (menu_w - menu_title.get_width())//2, self.menu_rect.y + 16))
            # Кнопки в стиле главного меню
            font = pygame.font.Font(None, 32)
            btn_w, btn_h, btn_gap = 240, 60, 22
            btn_x = self.menu_rect.x + (menu_w-btn_w)//2
            btn_y = self.menu_rect.y + 80
            # Кнопка "Во весь экран"
            fullscreen_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            self.fullscreen_button_rect = fullscreen_rect
            # Градиент
            for y_offset in range(btn_h):
                btn_gradient = (
                    int(160 - y_offset * 0.3),
                    int(120 - y_offset * 0.25),
                    int(90 - y_offset * 0.2)
                )
                pygame.draw.line(self.screen, btn_gradient,
                               (btn_x, btn_y + y_offset),
                               (btn_x + btn_w, btn_y + y_offset))
            pygame.draw.rect(self.screen, (70, 50, 35), fullscreen_rect, 5, border_radius=14)
            inner_rect = pygame.Rect(btn_x + 3, btn_y + 3, btn_w - 6, btn_h - 6)
            pygame.draw.rect(self.screen, (180, 150, 120), inner_rect, 2, border_radius=12)
            # Узор
            for i in range(4):
                x_pos = btn_x + 30 + i * 50
                pygame.draw.line(self.screen, (100, 80, 60), (x_pos, btn_y + 10), (x_pos, btn_y + btn_h - 10), 2)
                for j in range(2):
                    knot_y = btn_y + 20 + j * 20
                    pygame.draw.circle(self.screen, (90, 70, 50), (x_pos, knot_y), 3)
            # Заклёпки
            for corner_x, corner_y in [(btn_x + 8, btn_y + 8), (btn_x + btn_w - 8, btn_y + 8),
                                       (btn_x + 8, btn_y + btn_h - 8), (btn_x + btn_w - 8, btn_y + btn_h - 8)]:
                pygame.draw.circle(self.screen, (180, 170, 160), (corner_x, corner_y), 5)
                pygame.draw.circle(self.screen, (220, 210, 200), (corner_x, corner_y), 3)
            fullscreen_text = font.render('Во весь экран (F)', True, (255, 245, 220))
            fullscreen_shadow = font.render('Во весь экран (F)', True, (60, 50, 40))
            self.screen.blit(fullscreen_shadow, (btn_x + (btn_w - fullscreen_shadow.get_width())//2 + 2, btn_y + 18))
            self.screen.blit(fullscreen_text, (btn_x + (btn_w - fullscreen_text.get_width())//2, btn_y + 16))
            # Кнопка "Новая игра"
            newgame_rect = pygame.Rect(btn_x, btn_y + btn_h + btn_gap, btn_w, btn_h)
            self.newgame_button_rect = newgame_rect
            # Градиент
            for y_offset in range(btn_h):
                btn_gradient = (
                    int(160 - y_offset * 0.3),
                    int(120 - y_offset * 0.25),
                    int(90 - y_offset * 0.2)
                )
                pygame.draw.line(self.screen, btn_gradient,
                               (btn_x, newgame_rect.y + y_offset),
                               (btn_x + btn_w, newgame_rect.y + y_offset))
            pygame.draw.rect(self.screen, (70, 50, 35), newgame_rect, 5, border_radius=14)
            inner_newgame = pygame.Rect(btn_x + 3, newgame_rect.y + 3, btn_w - 6, btn_h - 6)
            pygame.draw.rect(self.screen, (180, 150, 120), inner_newgame, 2, border_radius=12)
            # Узор
            for i in range(4):
                x_pos = btn_x + 30 + i * 50
                pygame.draw.line(self.screen, (100, 80, 60), (x_pos, newgame_rect.y + 10), (x_pos, newgame_rect.y + btn_h - 10), 2)
                for j in range(2):
                    knot_y = newgame_rect.y + 20 + j * 20
                    pygame.draw.circle(self.screen, (90, 70, 50), (x_pos, knot_y), 3)
            # Заклёпки
            for corner_x, corner_y in [(btn_x + 8, newgame_rect.y + 8), (btn_x + btn_w - 8, newgame_rect.y + 8),
                                       (btn_x + 8, newgame_rect.y + btn_h - 8), (btn_x + btn_w - 8, newgame_rect.y + btn_h - 8)]:
                pygame.draw.circle(self.screen, (180, 170, 160), (corner_x, corner_y), 5)
                pygame.draw.circle(self.screen, (220, 210, 200), (corner_x, corner_y), 3)
            newgame_text = font.render('Новая игра', True, (255, 245, 220))
            newgame_shadow = font.render('Новая игра', True, (60, 50, 40))
            self.screen.blit(newgame_shadow, (btn_x + (btn_w - newgame_shadow.get_width())//2 + 2, newgame_rect.y + 18))
            self.screen.blit(newgame_text, (btn_x + (btn_w - newgame_text.get_width())//2, newgame_rect.y + 16))
            # Кнопка "Выйти"
            exit_btn_w, exit_btn_h = 200, 55
            exit_btn_x = btn_x + (btn_w - exit_btn_w) // 2
            exit_rect = pygame.Rect(exit_btn_x, newgame_rect.y + btn_h + btn_gap, exit_btn_w, exit_btn_h)
            self.exit_button_rect = exit_rect
            # Градиент
            for y_offset in range(exit_btn_h):
                exit_gradient = (
                    int(150 - y_offset * 0.35),
                    int(110 - y_offset * 0.3),
                    int(80 - y_offset * 0.25)
                )
                pygame.draw.line(self.screen, exit_gradient,
                               (exit_btn_x, exit_rect.y + y_offset),
                               (exit_btn_x + exit_btn_w, exit_rect.y + y_offset))
            pygame.draw.rect(self.screen, (70, 50, 35), exit_rect, 5, border_radius=12)
            inner_exit = pygame.Rect(exit_btn_x + 3, exit_rect.y + 3, exit_btn_w - 6, exit_btn_h - 6)
            pygame.draw.rect(self.screen, (170, 140, 110), inner_exit, 2, border_radius=10)
            # Узор
            for i in range(3):
                x_pos = exit_btn_x + 25 + i * 50
                pygame.draw.line(self.screen, (100, 80, 60), (x_pos, exit_rect.y + 8), (x_pos, exit_rect.y + exit_btn_h - 8), 2)
            # Заклёпки
            for corner_x, corner_y in [(exit_btn_x + 6, exit_rect.y + 6), (exit_btn_x + exit_btn_w - 6, exit_rect.y + 6),
                                       (exit_btn_x + 6, exit_rect.y + exit_btn_h - 6), (exit_btn_x + exit_btn_w - 6, exit_rect.y + exit_btn_h - 6)]:
                pygame.draw.circle(self.screen, (180, 170, 160), (corner_x, corner_y), 4)
                pygame.draw.circle(self.screen, (220, 210, 200), (corner_x, corner_y), 2)
            exit_text = font.render('Выйти', True, (255, 245, 220))
            exit_shadow = font.render('Выйти', True, (60, 50, 40))
            self.screen.blit(exit_shadow, (exit_btn_x + (exit_btn_w - exit_shadow.get_width())//2 + 2, exit_rect.y + 15 + 2))
            self.screen.blit(exit_text, (exit_btn_x + (exit_btn_w - exit_text.get_width())//2, exit_rect.y + 15))

    def draw_menu(self):
        # Пейзаж в перспективе с замком
        self.screen.fill((120, 170, 220))  # небо ярче
        # Солнце
        pygame.draw.circle(self.screen, (255, 240, 180), (650, 80), 50)
        pygame.draw.circle(self.screen, (255, 255, 200), (650, 80), 45)
        # Облака
        for cx, cy in [(150, 60), (400, 40), (700, 50)]:
            for dx in [-25, 0, 25]:
                pygame.draw.circle(self.screen, (220, 230, 250), (cx + dx, cy), 20)
        # Горы заднего плана в перспективе
        mt_points = [(0, SCREEN_HEIGHT), (120, 320), (220, 300), (320, 330), (420, 310), (520, 340), (620, 305), (720, 320), (800, 300), (SCREEN_WIDTH, SCREEN_HEIGHT)]
        pygame.draw.polygon(self.screen, (160, 180, 200), mt_points)
        # Горы переднего плана в перспективе
        mt2_points = [(0, SCREEN_HEIGHT), (160, 480), (300, 460), (480, 500), (660, 470), (SCREEN_WIDTH, 490), (SCREEN_WIDTH, SCREEN_HEIGHT)]
        pygame.draw.polygon(self.screen, (120, 140, 160), mt2_points)
        # Замок в перспективе (вдали по центру-верху) - увеличенный масштаб
        # Точка схода перспективы - ближе к экрану
        vanishing_y = 320
        castle_center_x = SCREEN_WIDTH // 2
        castle_scale = 0.95  # увеличенный масштаб для перспективы
        castle_base_y = vanishing_y + 40
        
        # Стены замка в перспективе
        castle_w = int(120 * castle_scale)
        castle_h = int(120 * castle_scale)
        castle_x = castle_center_x - castle_w // 2
        castle_y = castle_base_y
        pygame.draw.rect(self.screen, (200, 190, 170), (castle_x, castle_y, castle_w, castle_h))
        # Две башни
        tower_w = int(35 * castle_scale)
        tower_h = int(60 * castle_scale)
        pygame.draw.rect(self.screen, (220, 200, 180), (castle_x - int(18 * castle_scale), castle_y - tower_h, tower_w, tower_h))
        pygame.draw.rect(self.screen, (220, 200, 180), (castle_x + castle_w - int(17 * castle_scale), castle_y - tower_h, tower_w, tower_h))
        # Конусообразные крыши башен
        left_tower_top = castle_x - int(18 * castle_scale) + tower_w // 2
        right_tower_top = castle_x + castle_w - int(17 * castle_scale) + tower_w // 2
        pygame.draw.polygon(self.screen, (140, 100, 80), [
            (left_tower_top - int(15 * castle_scale), castle_y - tower_h),
            (left_tower_top, castle_y - tower_h - int(25 * castle_scale)),
            (left_tower_top + int(15 * castle_scale), castle_y - tower_h)
        ])
        pygame.draw.polygon(self.screen, (140, 100, 80), [
            (right_tower_top - int(15 * castle_scale), castle_y - tower_h),
            (right_tower_top, castle_y - tower_h - int(25 * castle_scale)),
            (right_tower_top + int(15 * castle_scale), castle_y - tower_h)
        ])
        # Зубцы на стене
        for x in range(castle_x, castle_x + castle_w, int(15 * castle_scale)):
            pygame.draw.rect(self.screen, (180, 160, 140), (x, castle_y, int(10 * castle_scale), int(15 * castle_scale)))
        # Ворота
        gate_w = int(25 * castle_scale)
        gate_h = int(35 * castle_scale)
        pygame.draw.arc(self.screen, (100, 80, 60), (castle_x + int(47 * castle_scale), castle_y + int(75 * castle_scale), gate_w, gate_h), 3.14, 0, 3)
        pygame.draw.rect(self.screen, (100, 80, 60), (castle_x + int(57 * castle_scale), castle_y + int(95 * castle_scale), int(20 * castle_scale), int(25 * castle_scale)))
        
        # Флаг на правой башне — анимация развевается на ветру
        t = pygame.time.get_ticks() / 700.0
        flag_sway = math.sin(t) * 8
        flag_pole_x = right_tower_top
        flag_pole_y = castle_y - tower_h
        flag_pole_h = int(30 * castle_scale)
        pygame.draw.line(self.screen, (120, 100, 100), (flag_pole_x, flag_pole_y), (flag_pole_x, flag_pole_y - flag_pole_h), 3)
        flag_points = [
            (flag_pole_x, flag_pole_y - flag_pole_h),
            (flag_pole_x + int(25 * castle_scale) + int(flag_sway), flag_pole_y - flag_pole_h + int(5 * castle_scale)),
            (flag_pole_x + int(20 * castle_scale) + int(flag_sway * 0.7), flag_pole_y - flag_pole_h + int(15 * castle_scale))
        ]
        pygame.draw.polygon(self.screen, (200, 0, 0), flag_points)
        # Добавляем детали на флаг
        pygame.draw.line(self.screen, (255, 255, 255), (flag_pole_x, flag_pole_y - flag_pole_h), (flag_pole_x + int(25 * castle_scale) + int(flag_sway), flag_pole_y - flag_pole_h + int(5 * castle_scale)), 2)
        
        # Дорога в перспективе (сужается к горизонту, идёт от низа экрана к замку) - увеличенная
        # Нижняя часть дороги (близко) - шире
        path_bottom_y = SCREEN_HEIGHT - 20
        path_bottom_w = 420
        path_bottom_x = SCREEN_WIDTH // 2 - path_bottom_w // 2
        # Верхняя часть дороги (далеко, у замка) - шире
        path_top_w = 120
        path_top_x = castle_center_x - path_top_w // 2
        path_top_y = castle_base_y + castle_h + 15
        
        # Рисуем дорогу как трапецию в перспективе
        road_points = [
            (path_bottom_x, path_bottom_y),
            (path_bottom_x + path_bottom_w, path_bottom_y),
            (path_top_x + path_top_w, path_top_y),
            (path_top_x, path_top_y)
        ]
        pygame.draw.polygon(self.screen, (100, 85, 70), road_points)
        # Текстура дороги (камешки)
        for i in range(20):
            for j in range(8):
                t_x = path_bottom_x + (path_top_x - path_bottom_x) * (j / 7.0) + (path_bottom_w + (path_top_w - path_bottom_w) * (j / 7.0)) * (i / 19.0)
                t_y = path_bottom_y + (path_top_y - path_bottom_y) * (j / 7.0)
                pygame.draw.circle(self.screen, (85, 75, 60), (int(t_x), int(t_y)), 2)
        
        # Статическая армия воинов вдоль дороги (много воинов, увеличенная)
        num_soldiers = 16  # Больше воинов как армия
        for idx in range(num_soldiers):
            # Позиция в перспективе вдоль дороги
            road_t = idx / float(num_soldiers - 1)
            soldier_x = path_bottom_x + (path_top_x - path_bottom_x) * road_t + (path_bottom_w + (path_top_w - path_bottom_w) * road_t) * 0.3
            soldier_y = path_bottom_y + (path_top_y - path_bottom_y) * road_t - 10
            # Масштаб воина в перспективе - увеличенный
            soldier_scale = 0.9 + 0.4 * (1 - road_t)
            soldier_w = int(16 * soldier_scale)
            soldier_h = int(24 * soldier_scale)
            
            # Тело воина
            pygame.draw.rect(self.screen, (200, 180, 150), (int(soldier_x), int(soldier_y), soldier_w, soldier_h))
            # Голова
            head_r = int(6 * soldier_scale)
            pygame.draw.circle(self.screen, (255, 220, 190), (int(soldier_x + soldier_w // 2), int(soldier_y)), head_r)
            # Шлем
            pygame.draw.arc(self.screen, (180, 160, 150), (int(soldier_x - 2 * soldier_scale), int(soldier_y - 3 * soldier_scale), int(20 * soldier_scale), int(12 * soldier_scale)), 3.14, 0, 2)
            # Оружие
            pygame.draw.line(self.screen, (160, 160, 160), (int(soldier_x + soldier_w), int(soldier_y + 8 * soldier_scale)), (int(soldier_x + soldier_w + 10 * soldier_scale), int(soldier_y)), 3)
            # Щит
            pygame.draw.ellipse(self.screen, (100, 80, 80), (int(soldier_x - 5 * soldier_scale), int(soldier_y + 10 * soldier_scale), int(12 * soldier_scale), int(14 * soldier_scale)))
        
        # Знаменосец спереди (ближайший к камере) - увеличенный
        banner_x = path_bottom_x + int(path_bottom_w * 0.35)
        banner_y = path_bottom_y - 10
        banner_scale = 1.2
        # Воин-знаменосец
        pygame.draw.rect(self.screen, (220, 200, 170), (banner_x, banner_y, int(18 * banner_scale), int(28 * banner_scale)))
        pygame.draw.circle(self.screen, (255, 230, 200), (banner_x + int(9 * banner_scale), banner_y), int(7 * banner_scale))
        pygame.draw.arc(self.screen, (200, 180, 160), (banner_x, int(banner_y - 3 * banner_scale), int(18 * banner_scale), int(14 * banner_scale)), 3.14, 0, 2)
        # Знамя — анимация развевается на ветру
        banner_pole_x = banner_x + int(20 * banner_scale)
        banner_pole_y = banner_y + int(5 * banner_scale)
        banner_sway = math.sin(t) * 12
        pygame.draw.line(self.screen, (140, 120, 100), (banner_pole_x, banner_pole_y), (banner_pole_x, banner_pole_y - int(25 * banner_scale)), 4)
        # Флаг развевается
        flag_bottom = [
            (banner_pole_x, banner_pole_y - int(25 * banner_scale)),
            (banner_pole_x + int(55 * banner_scale) + int(banner_sway), banner_pole_y - int(20 * banner_scale)),
            (banner_pole_x + int(50 * banner_scale) + int(banner_sway * 0.7), banner_pole_y - int(10 * banner_scale)),
            (banner_pole_x, banner_pole_y - int(15 * banner_scale))
        ]
        pygame.draw.polygon(self.screen, (200, 200, 255), flag_bottom)
        flag_top = [
            (banner_pole_x, banner_pole_y - int(25 * banner_scale)),
            (banner_pole_x + int(55 * banner_scale) + int(banner_sway), banner_pole_y - int(20 * banner_scale)),
            (banner_pole_x, banner_pole_y - int(20 * banner_scale))
        ]
        pygame.draw.polygon(self.screen, (255, 255, 255), flag_top)
        
        # Деревья по бокам - увеличенные
        for tree_x in [40, SCREEN_WIDTH - 100]:
            tree_y = SCREEN_HEIGHT - 40
            # Ствол - крупнее
            pygame.draw.rect(self.screen, (100, 60, 40), (tree_x, tree_y, 16, 40))
            # Крона - крупнее
            pygame.draw.circle(self.screen, (60, 140, 60), (tree_x + 8, tree_y - 10), 24)
            pygame.draw.circle(self.screen, (40, 120, 50), (tree_x + 8, tree_y - 10), 18)
            pygame.draw.circle(self.screen, (50, 130, 55), (tree_x + 8, tree_y - 10), 14)
        
        # --- Кнопки справа по середине (красивые с градиентами) ---
        # Позиция кнопок: правая сторона, по вертикали по центру
        btn_panel_x = SCREEN_WIDTH - 280
        btn_panel_y = SCREEN_HEIGHT // 2 - 100
        btn_w, btn_h = 240, 65
        btn_gap = 25
        
        # Заголовок
        title_font = pygame.font.Font(None, 64)
        title = title_font.render('Фэнтези Битва', True, (220, 200, 180))
        shadow = title_font.render('Фэнтези Битва', True, (80, 60, 40))
        self.screen.blit(shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 33))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        # Кнопка "Новая игра" с красивой текстурой
        start_btn_y = btn_panel_y
        self.start_button_rect = pygame.Rect(btn_panel_x, start_btn_y, btn_w, btn_h)
        
        # Градиент дерева: от светлого к тёмному
        for y_offset in range(btn_h):
            wood_gradient = (
                int(160 - y_offset * 0.3),
                int(120 - y_offset * 0.25),
                int(90 - y_offset * 0.2)
            )
            pygame.draw.line(self.screen, wood_gradient, 
                           (btn_panel_x, start_btn_y + y_offset),
                           (btn_panel_x + btn_w, start_btn_y + y_offset))
        
        # Тёмная окантовка с узором
        pygame.draw.rect(self.screen, (70, 50, 35), self.start_button_rect, 5, border_radius=14)
        # Внутренняя светлая линия
        inner_rect = pygame.Rect(btn_panel_x + 3, start_btn_y + 3, btn_w - 6, btn_h - 6)
        pygame.draw.rect(self.screen, (180, 150, 120), inner_rect, 2, border_radius=12)
        
        # Узор дерева (вертикальные линии с сучками)
        for i in range(4):
            x_pos = btn_panel_x + 30 + i * 50
            pygame.draw.line(self.screen, (100, 80, 60), (x_pos, start_btn_y + 10), (x_pos, start_btn_y + btn_h - 10), 2)
            # Сучки на линиях
            for j in range(2):
                knot_y = start_btn_y + 20 + j * 25
                pygame.draw.circle(self.screen, (90, 70, 50), (x_pos, knot_y), 3)
        
        # Металлические заклёпки по углам
        for corner_x, corner_y in [(btn_panel_x + 8, start_btn_y + 8), 
                                   (btn_panel_x + btn_w - 8, start_btn_y + 8),
                                   (btn_panel_x + 8, start_btn_y + btn_h - 8),
                                   (btn_panel_x + btn_w - 8, start_btn_y + btn_h - 8)]:
            pygame.draw.circle(self.screen, (180, 170, 160), (corner_x, corner_y), 5)
            pygame.draw.circle(self.screen, (220, 210, 200), (corner_x, corner_y), 3)
        
        start_text = self.font.render('НОВАЯ ИГРА', True, (255, 245, 220))
        text_shadow = self.font.render('НОВАЯ ИГРА', True, (60, 50, 40))
        self.screen.blit(text_shadow, (btn_panel_x + (btn_w - text_shadow.get_width())//2 + 2, start_btn_y + 20 + 2))
        self.screen.blit(start_text, (btn_panel_x + (btn_w - start_text.get_width())//2, start_btn_y + 20))
        
        # Кнопка "Выход" с красивой текстурой
        exit_btn_y = start_btn_y + btn_h + btn_gap
        exit_btn_w, exit_btn_h = 200, 55
        exit_btn_x = btn_panel_x + (btn_w - exit_btn_w) // 2
        self.exit_button_rect = pygame.Rect(exit_btn_x, exit_btn_y, exit_btn_w, exit_btn_h)
        
        # Градиент для кнопки выхода
        for y_offset in range(exit_btn_h):
            exit_gradient = (
                int(150 - y_offset * 0.35),
                int(110 - y_offset * 0.3),
                int(80 - y_offset * 0.25)
            )
            pygame.draw.line(self.screen, exit_gradient,
                           (exit_btn_x, exit_btn_y + y_offset),
                           (exit_btn_x + exit_btn_w, exit_btn_y + y_offset))
        
        # Окантовка
        pygame.draw.rect(self.screen, (70, 50, 35), self.exit_button_rect, 5, border_radius=12)
        inner_exit_rect = pygame.Rect(exit_btn_x + 3, exit_btn_y + 3, exit_btn_w - 6, exit_btn_h - 6)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_exit_rect, 2, border_radius=10)
        
        # Узор дерева
        for i in range(3):
            x_pos = exit_btn_x + 25 + i * 50
            pygame.draw.line(self.screen, (100, 80, 60), (x_pos, exit_btn_y + 8), (x_pos, exit_btn_y + exit_btn_h - 8), 2)
        
        # Заклёпки
        for corner_x, corner_y in [(exit_btn_x + 6, exit_btn_y + 6),
                                   (exit_btn_x + exit_btn_w - 6, exit_btn_y + 6),
                                   (exit_btn_x + 6, exit_btn_y + exit_btn_h - 6),
                                   (exit_btn_x + exit_btn_w - 6, exit_btn_y + exit_btn_h - 6)]:
            pygame.draw.circle(self.screen, (180, 170, 160), (corner_x, corner_y), 4)
            pygame.draw.circle(self.screen, (220, 210, 200), (corner_x, corner_y), 2)
        
        exit_text = self.font.render('ВЫХОД', True, (255, 245, 220))
        exit_shadow = self.font.render('ВЫХОД', True, (60, 50, 40))
        self.screen.blit(exit_shadow, (exit_btn_x + (exit_btn_w - exit_shadow.get_width())//2 + 2, exit_btn_y + 15 + 2))
        self.screen.blit(exit_text, (exit_btn_x + (exit_btn_w - exit_text.get_width())//2, exit_btn_y + 15))

    def draw_choose_race(self, player=1):
        """Экран выбора расы для указанного игрока."""
        self.screen.fill((30, 30, 60))
        title_text = f"Выбор расы — Игрок {player}"
        title = self.font.render(title_text, True, (255,255,255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        # Список рас и простой порядок отрисовки
        races = [
            ('human', 'Люди', (200, 220, 255)),
            ('elf', 'Эльфы', (180, 255, 200)),
            ('undead', 'Нежить', (220, 200, 255)),
            ('demon', 'Демоны', (255, 200, 200)),
            ('dwarf', 'Гномы', (220, 220, 180)),
            ('shadow', 'Тени', (200, 200, 220)),
        ]
        self.sorted_races = races

        # Сетка кнопок 3x2
        btn_w, btn_h, gap = 200, 60, 24
        start_x = SCREEN_WIDTH//2 - (btn_w*3 + gap*2)//2
        start_y = 140

        race_rects = []
        for idx, (key, label, color) in enumerate(races):
            row = idx // 3
            col = idx % 3
            x = start_x + col * (btn_w + gap)
            y = start_y + row * (btn_h + gap)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            # Подсветка при наведении
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            base = (80, 100, 140)
            bg = tuple(min(255, int(b*0.4) + c//3) for b, c in zip(base, color))
            pygame.draw.rect(self.screen, bg, rect, border_radius=10)
            pygame.draw.rect(self.screen, (200,200,220) if hovered else (120,140,180), rect, 2, border_radius=10)
            text = self.font.render(label, True, (255,255,255))
            self.screen.blit(text, (rect.x + (btn_w - text.get_width())//2, rect.y + (btn_h - text.get_height())//2))
            race_rects.append(rect)

        self.race_rects = race_rects

        # Подсказка
        hint = pygame.font.Font(None, 24).render("Кликните по кнопке, чтобы выбрать расу", True, (220,220,220))
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, start_y + 2*(btn_h + gap) + 20))
        # Курсор-рука над кнопками
        mouse_pos = pygame.mouse.get_pos()
        over_button = any(rect.collidepoint(mouse_pos) for rect in self.race_rects)
        self.set_cursor(pygame.SYSTEM_CURSOR_HAND if over_button else pygame.SYSTEM_CURSOR_ARROW)

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
        # Предпросмотр зоны для area-заклинаний
        # Автоматически сбрасываем флаг dismiss при наличии выбранного area-заклинания
        if isinstance(self.selected_unit, Hero) and getattr(self.selected_unit, 'selected_spell', None) is not None:
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            if spell.target_type == 'area':
                self.area_preview_dismiss = False  # Автоматически показываем превью для area-заклинаний
                mouse_pos = pygame.mouse.get_pos()
                cx = (mouse_pos[0] // CELL_SIZE) * CELL_SIZE + CELL_SIZE//2
                cy = (mouse_pos[1] // CELL_SIZE) * CELL_SIZE + CELL_SIZE//2
                preview_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                if hasattr(spell, 'icon') and spell.icon == 'frost_ring':
                    # Зона 3x3 клетки синего цвета с выколотой клеткой в центре (как у огненного шара)
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                # Выколотая клетка в центре — рисуем только контур
                                pygame.draw.rect(preview_surface, (120, 200, 255, 100), 
                                                (cx - CELL_SIZE//2 + dx*CELL_SIZE, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
                            else:
                                # Обычные клетки зоны — полупрозрачные
                                pygame.draw.rect(preview_surface, (100, 180, 255, 80), 
                                                (cx - CELL_SIZE//2 + dx*CELL_SIZE, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                                pygame.draw.rect(preview_surface, (140, 210, 255, 120), 
                                                (cx - CELL_SIZE//2 + dx*CELL_SIZE, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
                elif hasattr(spell, 'icon') and spell.icon == 'fireball':
                    # Зона 3x3 клетки
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            pygame.draw.rect(preview_surface, (255, 100, 40, 80), 
                                            (cx - CELL_SIZE//2 + dx*CELL_SIZE, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                            pygame.draw.rect(preview_surface, (255, 140, 60, 120), 
                                            (cx - CELL_SIZE//2 + dx*CELL_SIZE, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
                self.screen.blit(preview_surface, (0,0))
        # --- Отдельный проход для типтулов, чтобы они были поверх ---
        mouse_pos = pygame.mouse.get_pos()
        # Определяем наведённого юнита
        hovered_unit = None
        for unit in self.units:
            if unit.x * CELL_SIZE <= mouse_pos[0] < (unit.x+1)*CELL_SIZE and unit.y * CELL_SIZE <= mouse_pos[1] < (unit.y+1)*CELL_SIZE:
                hovered_unit = unit
                break
        # Обновляем флаг show_tooltip и рисуем только у наведённого
        for unit in self.units:
            unit.show_tooltip = (unit is hovered_unit)
        if hovered_unit:
            hovered_unit.draw_tooltip(self.screen, mouse_pos)
        self.draw_ui()
        # Отрисовка отладочной информации поверх всего
        self.debugger.draw_debug_overlay(self.screen)
        pygame.display.flip()

    def update(self):
        """Минимальное обновление состояния игры за кадр."""
        if self.game_over:
            return
        self.check_game_over()
        self.update_cursor()

    def add_event(self, text):
        if not hasattr(self, 'event_log'):
            self.event_log = []
        self.event_log.append(str(text))
        # Подрезаем лог, чтобы не рос бесконечно
        if len(self.event_log) > 500:
            self.event_log = self.event_log[-500:]

    # ------------------- Курсор -------------------
    def set_cursor(self, system_cursor):
        try:
            if getattr(self, '_current_cursor', None) != system_cursor:
                pygame.mouse.set_cursor(pygame.cursors.Cursor(system_cursor))
                self._current_cursor = system_cursor
        except Exception:
            pass

    def update_cursor(self):
        # Экраны выбора
        if self.state in ('menu', 'choose_race_p1', 'choose_race_p2'):
            return  # устанавливается внутри отрисовки экранов
        mouse_pos = pygame.mouse.get_pos()
        # Рука над кликабельными UI
        if self.menu_open and hasattr(self, 'menu_rect') and self.menu_rect.collidepoint(mouse_pos):
            self.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return
        if self.history_panel_open and hasattr(self, 'history_panel_close_rect') and self.history_panel_close_rect.collidepoint(mouse_pos):
            self.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return
        if hasattr(self, 'book_button_rect') and self.book_button_rect.collidepoint(mouse_pos):
            self.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return
        if hasattr(self, 'skip_button_rect') and (self.skip_button_rect.collidepoint(mouse_pos) or pygame.Rect(self.skip_button_rect.x - 70, self.skip_button_rect.y, 48, 48).collidepoint(mouse_pos)):
            self.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return
        # Таргетинг заклинаний/атак
        grid_x, grid_y = mouse_pos[0] // CELL_SIZE, mouse_pos[1] // CELL_SIZE
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            if isinstance(self.selected_unit, Hero) and getattr(self.selected_unit, 'selected_spell', None) is not None:
                self.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                return
            if self.selected_unit and hasattr(self.selected_unit, 'can_attack'):
                try:
                    if self.selected_unit.can_attack(grid_x, grid_y, self.units):
                        self.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                        return
                except Exception:
                    pass
        # По умолчанию
        self.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def prepare_initiative_queue(self):
        """Создаёт очередь ходов на основе инициативы юнитов."""
        # Сбрасываем флаги хода для всех
        for unit in self.units:
            if hasattr(unit, 'reset_turn'):
                unit.reset_turn()
        # Сортируем по инициативе (выше — раньше). При равенстве — стабильно.
        self.turn_queue = sorted([u for u in self.units if not isinstance(u, Hero)], key=lambda u: getattr(u, 'initiative', 0), reverse=True)
        # Вставляем героев в начало своих команд, чтобы они могли кастовать первыми
        heroes = [u for u in self.units if isinstance(u, Hero)]
        for hero in heroes:
            self.turn_queue.insert(0, hero)
        # Добавляем разделитель конца раунда
        if self.turn_queue:
            self.turn_queue.append(self._round_delimiter)
        if self.turn_queue:
            self.selected_unit = self.turn_queue[0]

    def next_turn(self):
        """Переходит к следующему юниту в очереди, с учётом разделителя раундов."""
        if not hasattr(self, 'turn_queue') or not self.turn_queue:
            return
        # Удаляем мёртвых юнитов, но оставляем разделитель
        self.turn_queue = [u for u in self.turn_queue if (u is self._round_delimiter) or (u in self.units)]
        if not self.turn_queue:
            return
        finished = self.turn_queue.pop(0)
        # Реген маны героям при окончании хода, если не кастовали в этот ход
        if isinstance(finished, Hero):
            if not getattr(finished, 'used_spell_this_round', False):
                regen = max(1, int(getattr(finished, 'knowledge', 0) * 0.5))
                finished.mana = min(finished.max_mana, finished.mana + regen)
        if finished is self._round_delimiter:
            # Начало нового раунда
            self.round_number += 1
            for unit in self.units:
                if hasattr(unit, 'reset_turn'):
                    unit.reset_turn()
                # сбрасываем ожидание в новом раунде
                if hasattr(unit, 'has_waited'):
                    unit.has_waited = False
            # Разделитель отправляем в конец очереди текущего раунда
            self.turn_queue.append(self._round_delimiter)
        else:
            # Обычный юнит: если жив — в начало следующего раунда (после разделителя)
            if finished in self.units:
                try:
                    delim_index = self.turn_queue.index(self._round_delimiter)
                except ValueError:
                    # На всякий случай — если разделитель потерялся
                    self.turn_queue.append(self._round_delimiter)
                    delim_index = len(self.turn_queue) - 1
                # Добавляем в конец очереди (это область после разделителя)
                self.turn_queue.append(finished)
        # Назначаем активного юнита (пропуская разделитель)
        while self.turn_queue and self.turn_queue[0] is self._round_delimiter:
            # если разделитель оказался в начале — сдвигаем и начинаем новый раунд
            self.turn_queue.pop(0)
            self.turn_queue.append(self._round_delimiter)
            self.round_number += 1
            for unit in self.units:
                if hasattr(unit, 'reset_turn'):
                    unit.reset_turn()
                if hasattr(unit, 'has_waited'):
                    unit.has_waited = False
        if self.turn_queue:
            self.selected_unit = self.turn_queue[0]

    def can_attack_any(self, unit):
        for enemy in self.units:
            if enemy.team != unit.team:
                if unit.can_attack(enemy.x, enemy.y, self.units):
                    return True
        return False

    def get_reachable_cells(self, x, y, move_points):
        """Простая манхэттенская досягаемость без препятствий (минимально для запуска игры)."""
        reachable = set()
        for dx in range(-move_points, move_points + 1):
            remaining = move_points - abs(dx)
            for dy in range(-remaining, remaining + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    distance = abs(dx) + abs(dy)
                    if distance <= move_points:
                        # Не занимать клетки с юнитами другой команды
                        occupied = any(u.x == nx and u.y == ny for u in self.units)
                        if not occupied:
                            reachable.add((nx, ny))
        return reachable

    def get_path_length(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Анимации очереди — заглушки
    def animate_queue_move(self, old_queue, new_queue):
        pass

    def animate_queue_fade(self, unit):
        pass

    # Визуальные анимации заклинаний — простые заглушки
    def animate_spell_flash(self, target, color, redraw_callback=None):
        cx = target.x*CELL_SIZE+CELL_SIZE//2
        cy = target.y*CELL_SIZE+CELL_SIZE//2
        max_r = CELL_SIZE
        frames = 14
        for i in range(frames):
            pygame.event.pump()
            if redraw_callback:
                redraw_callback()
            r = int(max_r * (i+1) / frames)
            alpha = max(40, 200 - int(200 * i / frames))
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (cx, cy), r, 4)
            self.screen.blit(s, (0,0))
            pygame.display.flip()
            pygame.time.delay(20)

    def animate_firearrow(self, caster, target):
        start = (caster.x*CELL_SIZE+CELL_SIZE//2, caster.y*CELL_SIZE+CELL_SIZE//2)
        end = (target.x*CELL_SIZE+CELL_SIZE//2, target.y*CELL_SIZE+CELL_SIZE//2)
        # Полёт огненной стрелы с текстурами и пламенем
        animate_fire_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
        # Эпичный взрыв в точке попадания
        animate_fire_explosion(self.screen, end[0], end[1])

    def animate_explosion(self, x, y, color):
        pygame.draw.circle(self.screen, color, (x, y), 12)
        pygame.display.flip()

    def animate_roots(self, target):
        self.animate_spell_flash(target, (80,180,60), redraw_callback=self.draw)

    def animate_water_bless(self, target):
        self.animate_spell_flash(target, (120,180,255), redraw_callback=self.draw)

    def animate_curse(self, caster, target):
        self.animate_spell_flash(target, (200,0,0), redraw_callback=self.draw)

    def start_new_game(self):
        """Сброс в главное меню выбора рас."""
        self.player1_race = None
        self.player2_race = None
        self.units = []
        self.turn_queue = []
        self.state = 'choose_race_p1'

    def handle_key(self, key):
        """Обработка нажатий клавиш, включая делегирование отладочным хоткеям."""
        # Хоткеи отладчика (F1-F6)
        self.debugger.handle_debug_key(key)
        # ESC — открытие/закрытие внутриигрового меню или панелей
        if key == pygame.K_ESCAPE:
            if self.history_panel_open:
                self.history_panel_open = False
                return
            # Тоггл простого меню
            self.menu_open = not self.menu_open

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
                self.area_preview_dismiss = False  # Сброс флага при закрытии книги
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
                    self.area_preview_dismiss = False  # Сброс флага при выборе заклинания
                    # Курсор-книга при выборе (используем hand как замену)
                    self.set_cursor(pygame.SYSTEM_CURSOR_HAND)
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
            caster = self.selected_unit
            spell = caster.spells[caster.selected_spell]
            # Проверка маны
            if caster.mana < spell.mana_cost:
                return
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
            if spell.target_type == 'area':
                center_px = (x * CELL_SIZE + CELL_SIZE//2, y * CELL_SIZE + CELL_SIZE//2)
                # Отдельные анимации для area-спеллов
                if hasattr(spell, 'icon') and spell.icon == 'frost_ring':
                    # Спрятать превью сразу после нажатия
                    caster.selected_spell = None
                    animate_frost_ring(self.screen, center_px, radius_cells=1, redraw_callback=self.draw)
                    animate_frost_impact(self.screen, center_px, redraw_callback=self.draw)
                elif hasattr(spell, 'icon') and spell.icon == 'raise_dead':
                    caster.selected_spell = None
                    animate_raise_dead(self.screen, center_px, redraw_callback=self.draw)
                elif hasattr(spell, 'icon') and spell.icon == 'fireball':
                    caster_px = (caster.x * CELL_SIZE + CELL_SIZE//2, caster.y * CELL_SIZE + CELL_SIZE//2)
                    caster.selected_spell = None
                    animate_fireball(self.screen, caster_px, center_px, redraw_callback=self.draw)
                # Применение по области/клетке
                spell.apply((x, y), caster=caster)
                caster.mana = max(0, caster.mana - spell.mana_cost)
                caster.used_spell_this_round = True
                self.area_preview_dismiss = True
                self.next_turn()
                return
            if spell.target_type == 'enemy' and target and target.team != caster.team and caster.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                # Специальные анимации по типам
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(caster, target)
                elif hasattr(spell, 'icon') and spell.icon == 'slow':
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_slow_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                elif hasattr(spell, 'icon') and spell.icon == 'curse':
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_curse_voodoo(self.screen, target_px, redraw_callback=self.draw)
                elif hasattr(spell, 'icon') and spell.icon == 'forget':
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_forget_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_dispel_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                else:
                    # Полёт магического снаряда с цветом по типу кастера
                    if caster.unit_type == 'succubus':
                        color = (255, 80, 120)
                    elif caster.unit_type == 'gog':
                        color = (255, 120, 40)
                    elif caster.unit_type == 'lich':
                        color = (80, 255, 80)
                    else:
                        color = (120, 180, 255)
                    animate_magic_fly(self.screen,
                                      (caster.x * CELL_SIZE + CELL_SIZE//2, caster.y * CELL_SIZE + CELL_SIZE//2),
                                      (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                      color=color, redraw_callback=self.draw)
                spell.apply(target, caster=caster)
                caster.mana = max(0, caster.mana - spell.mana_cost)
                caster.selected_spell = None
                caster.used_spell_this_round = True
                self.area_preview_dismiss = True
                self.next_turn()
                return
            elif spell.target_type == 'ally':
                # Если клик по врагу — ничего не делаем
                if target and target.team != caster.team:
                    return
                if target and target.team == caster.team and caster.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    # --- Анимация для благословения и снятия чар ---
                    caster_px = (caster.x * CELL_SIZE + CELL_SIZE//2, caster.y * CELL_SIZE + CELL_SIZE//2)
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        animate_bless_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        animate_dispel_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'rune_shield':
                        animate_rune_shield_spell(self.screen, caster_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'rune_haste':
                        animate_rune_haste_spell(self.screen, caster_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'stone_skin':
                        animate_stone_skin(self.screen, target_px, redraw_callback=self.draw)
                    spell.apply(target, caster=caster)
                    caster.mana = max(0, caster.mana - spell.mana_cost)
                    caster.selected_spell = None
                    caster.used_spell_this_round = True
                    self.area_preview_dismiss = True
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
                # Убираем текущего юнита из начала очереди
                if self.turn_queue and self.turn_queue[0] is self.selected_unit:
                    unit = self.turn_queue.pop(0)
                else:
                    unit = self.selected_unit
                    if unit in self.turn_queue:
                        self.turn_queue.remove(unit)
                # Вставляем юнита в конец текущего раунда (перед разделителем)
                try:
                    delim_index = self.turn_queue.index(self._round_delimiter)
                except ValueError:
                    self.turn_queue.append(self._round_delimiter)
                    delim_index = len(self.turn_queue) - 1
                self.turn_queue.insert(delim_index, unit)
                # Анимация перемещения ленты очереди
                if self.turn_queue:
                    self.animate_queue_move(old_queue, self.turn_queue)
                    # Назначаем нового активного юнита, пропуская разделитель
                    while self.turn_queue and self.turn_queue[0] is self._round_delimiter:
                        self.turn_queue.pop(0)
                        self.turn_queue.append(self._round_delimiter)
                    if self.turn_queue:
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