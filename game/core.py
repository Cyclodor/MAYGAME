import pygame
import os
import sys
# Добавляем родительскую директорию в путь для импорта логгера
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from animation_logger import get_logger
from .config import *
from .units import Hero, Peasant, Spearman, Crossbowman, Swordsman, Gryphon, Skeleton, Zombie, Ghost, Vampire, Lich, Pixie, ElfScout, ElfArcher, Dryad, Ent, Imp, Gog, Demon, Cerberus, Succubus, Miner, Spearthrower, BearRider, RuneMage, Jarl, Scout, Beast, Minotaur, Witch, LizardRider, Monk, Angel, Cavalryman, DeathKnight, BoneDragon, Reaper, GreenDragon, Druid, Unicorn, BloodPriestess, Devil, HellHorse, Manticore, RedDragon, Beholder, ForgeDragon, MountainRuler, Volkhv
from .graphics import (
    draw_cell_texture,
    draw_animated_grass,
    animate_arrow,
    animate_magic_projectile,
    animate_arrow_fly,
    animate_fire_arrow_fly,
    animate_ice_arrow,
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
    animate_rune_magic_spell,
    animate_rune_berserker_spell,
    animate_air_haste_spell,
    animate_frost_ring,
    animate_frost_impact,
    animate_luck_horseshoe,
    animate_combat_spirit_bird,
    load_image,
)
from .hero_animations import animate_warrior_teleport
from .spells import BlessSpell, CurseSpell, SlowSpell, FireArrowSpell, DispelSpell, RuneShieldSpell, RuneHasteSpell, ForgetSpell, FrostRingSpell, StoneSkinSpell, RaiseDeadSpell, FireballSpell, UndeadHealSpell, HasteSpell, FireShieldSpell, HealSpell, ResurrectionSpell, IceShieldSpell, LightningSpell, EarthSpikesSpell, CounterstrikeSpell, RuneWallSpell, RuneMagicSpell, RuneBerserkerSpell, WeaknessSpell, ChainLightningSpell, AccuracySpell, QuicksandSpell, EarthShockSpell, PrayerSpell, BlindnessSpell
from .sound import load_sound, load_sound_mp3
from .debugger import GameDebugger
from .ai import AIController
import math
import random

DEBUG_MODE = False

TEAM_LABELS = {
    'human': 'Люди',
    'undead': 'Нежить',
    'elf': 'Эльфы',
    'demon': 'Демоны',
    'dwarf': 'Гномы',
    'shadow': 'Тени'
}

def toggle_debug_mode():
    global DEBUG_MODE
    DEBUG_MODE = not DEBUG_MODE
    print(f'DEBUG_MODE set to {DEBUG_MODE}')

class Game:
    def __init__(self, screen):
        self.screen = screen
        # Инициализируем логгер анимаций
        self.anim_logger = get_logger()
        self.anim_logger.log("GAME_INIT", "Игра инициализирована")
        self.units = []
        self.corpses = []  # Список трупов на поле боя
        self.barriers = []  # Список магических барьеров
        self.quicksands = []  # Список зыбучих песков (не барьеры, но ловушки)
        self.selected_unit = None
        self.current_team = 'human'
        self.game_over = False
        self.menu_open = False
        self.state = 'menu'  # 'menu', 'battle_setup', 'game'
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
        # Окно информации о юните
        self.unit_info_window_open = False
        self.unit_info_window_unit = None
        # Тултип юнита (при зажатии правой кнопки)
        self.unit_tooltip_unit = None
        self.unit_tooltip_show = False
        # Отслеживание двойного клика
        self.last_click_time = 0
        self.last_click_pos = None
        self.last_click_unit = None
        self.last_click_button = None  # Отслеживаем какая кнопка была нажата
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
        self.player1_hero_class = None  # Класс героя игрока 1
        self.player2_hero_class = None  # Класс героя игрока 2
        self.player1_type = 'human'  # 'human' или 'ai' (бот)
        self.player2_type = 'ai'  # 'human' или 'ai' (бот)
        self.player1_side = 'right'
        self.player2_side = 'left'
        # ИИ для ботов
        self.ai_controller_p1 = None  # ИИ для игрока 1
        self.ai_controller_p2 = None  # ИИ для игрока 2
        self.ai_think_timer = 0  # Таймер для задержки хода ИИ (для визуализации)
        self.ai_think_delay = 30  # Задержка перед ходом ИИ (в кадрах, ~0.5 сек при 60 FPS)
        self.spectator_mode = False  # Режим наблюдения (оба бота)
        self.is_paused = False  # Пауза игры
        # Переменные для кастомного курсора дальнобойных юнитов
        self._ranged_cursor_pos = None
        self._ranged_cursor_penalty = None
        # Инициализация дебаггера
        self.debugger = GameDebugger(self)
        # Инициализация менеджера анимаций
        from .animation_manager import AnimationManager
        self.animation_manager = AnimationManager(self)
        # Режим разработчика (креатив)
        self.creative_selected_team = 'human'
        self.creative_selected_unit = 'Hero_human_warrior'  # По умолчанию выбран герой-воин людей
        self.creative_selected_side = 1  # 1 или 2 - первая или вторая команда
        # Пулы юнитов по расам (включая героев для каждой расы)
        self.creative_units_by_race = {
            'human': [
                ('Hero_human_warrior', Hero), ('Hero_human_archer', Hero), ('Hero_human_mage', Hero),
                ('Peasant', Peasant), ('Spearman', Spearman), ('Swordsman', Swordsman), ('Crossbowman', Crossbowman), 
                ('Gryphon', Gryphon), ('Monk', Monk), ('Angel', Angel), ('Cavalryman', Cavalryman)
            ],
            'elf': [
                ('Hero_elf_warrior', Hero), ('Hero_elf_archer', Hero), ('Hero_elf_mage', Hero),
                ('Pixie', Pixie), ('ElfScout', ElfScout), ('ElfArcher', ElfArcher), ('Dryad', Dryad), 
                ('Ent', Ent), ('GreenDragon', GreenDragon), ('Druid', Druid), ('Unicorn', Unicorn)
            ],
            'undead': [
                ('Hero_undead_warrior', Hero), ('Hero_undead_archer', Hero), ('Hero_undead_mage', Hero),
                ('Skeleton', Skeleton), ('Zombie', Zombie), ('Ghost', Ghost), ('Vampire', Vampire), 
                ('Lich', Lich), ('DeathKnight', DeathKnight), ('BoneDragon', BoneDragon), ('Reaper', Reaper)
            ],
            'demon': [
                ('Hero_demon_warrior', Hero), ('Hero_demon_archer', Hero), ('Hero_demon_mage', Hero),
                ('Imp', Imp), ('Gog', Gog), ('Demon', Demon), ('Cerberus', Cerberus), 
                ('Succubus', Succubus), ('BloodPriestess', BloodPriestess), ('Devil', Devil), ('HellHorse', HellHorse)
            ],
            'dwarf': [
                ('Hero_dwarf_warrior', Hero), ('Hero_dwarf_archer', Hero), ('Hero_dwarf_mage', Hero),
                ('Miner', Miner), ('Spearthrower', Spearthrower), ('BearRider', BearRider), ('RuneMage', RuneMage), 
                ('Jarl', Jarl), ('ForgeDragon', ForgeDragon), ('MountainRuler', MountainRuler), ('Volkhv', Volkhv)
            ],
            'shadow': [
                ('Hero_shadow_warrior', Hero), ('Hero_shadow_archer', Hero), ('Hero_shadow_mage', Hero),
                ('Scout', Scout), ('Beast', Beast), ('Minotaur', Minotaur), ('Witch', Witch), 
                ('LizardRider', LizardRider), ('Manticore', Manticore), ('RedDragon', RedDragon), ('Beholder', Beholder)
            ],
        }
        # Общие герои (для обратной совместимости, но теперь герои есть в каждой расе)
        self.creative_units_common = []
        self.creative_selected_hero_class = 'warrior'  # Для совместимости
        self.creative_panel_rect = pygame.Rect(SCREEN_WIDTH - 220, 0, 220, SCREEN_HEIGHT)
        # Уменьшенные кнопки внизу
        self.creative_start_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 60, 160, 38)
        self.creative_back_rect = pygame.Rect(20, SCREEN_HEIGHT - 50, 150, 32)
        # Кнопка книги заклинаний
        self.creative_spellbook_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 160, 160, 32)

        # Настройки звука
        self.music_volume = 0.6
        self.sfx_volume = 0.8
        self.muted = False
        self._settings_path = os.path.join('data', 'settings.json')
        self._unit_overrides_path = os.path.join('data', 'unit_overrides.json')
        self._spell_overrides_path = os.path.join('data', 'spell_overrides.json')
        self._load_settings()
        self._apply_audio_volumes()
        # Загрузка оверрайдов юнитов
        self.unit_overrides = {}
        self._load_unit_overrides()
        # Загрузка оверрайдов заклинаний
        self.spell_overrides = {}
        self._load_spell_overrides()
        # Инициализация музыкальных и боевых флагов/ресурсов
        self._reset_battle_state()
        # Каталог заклинаний
        self._spells_catalog = self._build_spells_catalog()

    def _reset_battle_state(self):
        """Полный сброс флагов/данных боя при выходе из него."""
        self.game_over = False
        self.victory_state = None
        self.winner_team = None
        if hasattr(self, 'barriers'):
            self.barriers = []
        if hasattr(self, 'quicksands'):
            self.quicksands = []
        if hasattr(self, 'turn_queue'):
            self.turn_queue = []
        self.current_initiative_index = 0 if hasattr(self, 'current_initiative_index') else 0
        self.battle_intro_playing = False
        self.combat_music_playing = False
        self.current_intro_sound = None
        self.intro_channel = None
        # Сброс логики выбора человек/бот при пересоздании боя
        self.player1_type = 'human'
        self.player2_type = 'ai'
        self.spectator_mode = False
        # Очищаем трупы при сбросе состояния боя
        self.corpses = []
        # Остановить любую текущую музыку (меню/бой)
        try:
            from pygame import mixer
            mixer.music.stop()
        except Exception:
            pass
        # не чистим self.units здесь — это ответственность вызывающего (например, меню может начать новый сетап)
        # Загрузка звуков из Heroes 3
        self.button_click_sound = load_sound_mp3('нажатие на кнопки')
        # Оптимизация звука кнопок для мгновенного воспроизведения
        if self.button_click_sound:
            self.button_click_sound.set_volume(0.7)
        self.bless_sound = load_sound_mp3('благословение')
        self.slow_sound = load_sound_mp3('Заклинание замедление')
        self.victory_sound = load_sound_mp3('Звук победы в мире Меча и Магии III')
        self.defeat_sound = load_sound_mp3('Звук поражение в бою')
        self.magic_shot_sound = load_sound('выстрел мага')
        self.curse_sound = load_sound('проклятие')
        self.fireball_explosion_sound = load_sound('фаербол взрыв')
        self.shot_sound = load_sound('выстрел')
        self.shot2_sound = load_sound('выстрел 2')
        # Звуки ближнего боя для людей и монстров (списки для рандомизации)
        self.human_melee_sounds = [
            load_sound('человек атака'),
            load_sound('человек атака 2')
        ]
        self.monster_melee_sounds = [
            load_sound('монстер атака'),
            load_sound('монстр атака 2')
        ]
        # Фильтруем None (если звук не загрузился)
        self.human_melee_sounds = [s for s in self.human_melee_sounds if s is not None]
        self.monster_melee_sounds = [s for s in self.monster_melee_sounds if s is not None]
        # Звук полёта фаербола
        self.fireball_flight_sound = load_sound('полёт фаербола')
        # Звуки начала битвы - выбор случайного из 8 файлов
        self.battle_intro_sounds = [
            load_sound('BATTLE00'),
            load_sound('BATTLE01'),
            load_sound('BATTLE02'),
            load_sound('BATTLE03'),
            load_sound('BATTLE04'),
            load_sound('BATTLE05'),
            load_sound('BATTLE06'),
            load_sound('BATTLE07')
        ]
        # Убираем None из списка (на случай, если какой-то файл не загрузился)
        self.battle_intro_sounds = [s for s in self.battle_intro_sounds if s is not None]
        # Устанавливаем громкость интро-звуков согласно настройкам музыки
        intro_volume = 0.0 if getattr(self, 'muted', False) else getattr(self, 'music_volume', 0.6)
        for s in self.battle_intro_sounds:
            try:
                s.set_volume(intro_volume)
            except Exception:
                pass
        self.battle_intro_playing = False
        self.current_intro_sound = None
        self.intro_channel = None  # Канал для отслеживания intro звука
        self.menu_music_path = os.path.join('assets', 'sounds', 'главное меню.mp3')
        self.menu_music_playing = False
        # Боевая музыка - выбор случайной из 3 треков
        self.combat_music_paths = [
            os.path.join('assets', 'sounds', 'Heroes of Might & Magic 3 HD OST — Combat 4 (www.lightaudio.ru).mp3'),
            os.path.join('assets', 'sounds', 'Heroes of Might and Magic 3 — Combat 02 (www.lightaudio.ru).mp3'),
            os.path.join('assets', 'sounds', 'Heroes of Might and Magic 3 — Combat 3 (www.lightaudio.ru).mp3')
        ]
        self.combat_music_playing = False
        self.current_combat_music = None
        # Состояние победы/проигрыша
        self.victory_state = None  # None, 'victory', 'defeat'
        self.winner_team = None
        self.victory_screen_shown = False
        # Анимация перелистывания книги заклинаний
        self.spellbook_flip_animation = None
        self.spellbook_flip_progress = 0.0
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

    def _set_default_squad_count(self, unit):
        """Устанавливает размер отряда в зависимости от силы юнита"""
        if isinstance(unit, Hero):
            # Герои всегда одиночки, но инициализируем систему здоровья для них тоже
            if not hasattr(unit, 'unit_hp') or unit.unit_hp is None:
                unit.unit_hp = unit.max_health
                unit.current_unit_hp = unit.health
                unit.base_squad_count = 1
            return
        
        # Слабые юниты (большие отряды)
        weak_units = ['peasant', 'skeleton', 'pixie', 'imp', 'miner', 'scout']
        # Средние юниты (средние отряды)
        medium_units = ['spearman', 'crossbowman', 'zombie', 'ghost', 'elf_scout', 'elf_archer', 'gog', 'spearthrower']
        # Сильные юниты (маленькие отряды)
        strong_units = ['swordsman', 'gryphon', 'vampire', 'lich', 'dryad', 'ent', 'demon', 'cerberus', 'succubus', 
                       'bearrider', 'runemage', 'jarl', 'beast', 'minotaur', 'witch', 'lizardrider']
        # Очень сильные юниты (очень маленькие отряды)
        very_strong_units = ['monk', 'cavalryman', 'deathknight', 'reaper', 'druid', 'unicorn', 
                            'bloodpriestess', 'hellhorse', 'manticore', 'beholder', 'mountainruler', 'volkhv']
        # Элитные юниты (минимальные отряды)
        elite_units = ['angel', 'bonedragon', 'greendragon', 'devil', 'reddragon', 'forgedragon']
        
        unit_type = unit.unit_type.lower()
        
        if unit_type in weak_units:
            count = random.randint(20, 40)
        elif unit_type in medium_units:
            count = random.randint(12, 24)
        elif unit_type in strong_units:
            count = random.randint(6, 15)
        elif unit_type in very_strong_units:
            count = random.randint(3, 8)
        elif unit_type in elite_units:
            count = random.randint(1, 4)
        else:
            count = random.randint(8, 16)  # По умолчанию
        
        unit.set_squad_count(count)
    
    def initialize_units(self, p1_race=None, p2_race=None):
        self.units = []
        self.corpses = []  # Очищаем трупы при создании новой игры
        self.barriers = []  # Очищаем барьеры при создании новой игры
        self.quicksands = []  # Очищаем зыбучие пески при создании новой игры
        # p1 - справа, p2 - слева
        races = {
            'human': [Peasant, Spearman, Crossbowman, Swordsman, Gryphon],
            'undead': [Skeleton, Zombie, Ghost, Vampire, Lich],
            'elf': [Pixie, ElfScout, ElfArcher, Dryad, Ent],
            'demon': [Imp, Gog, Demon, Cerberus, Succubus],
            'dwarf': [Miner, Spearthrower, BearRider, RuneMage, Jarl],
            'shadow': [Scout, Beast, Minotaur, Witch, LizardRider]
        }
        # Создаем заклинания для каждой расы (создаем новые экземпляры каждый раз)
        def create_spells_for_race(race):
            """Создает список заклинаний для расы и применяет оверрайды"""
            spell_classes = {
                'human': [BlessSpell, DispelSpell, HasteSpell, HealSpell, ResurrectionSpell, PrayerSpell, BlindnessSpell],
                'undead': [CurseSpell, RaiseDeadSpell, UndeadHealSpell, WeaknessSpell],
                'elf': [SlowSpell, StoneSkinSpell, IceShieldSpell, LightningSpell, CounterstrikeSpell, ChainLightningSpell, AccuracySpell],
                'demon': [FireArrowSpell, FireballSpell, FireShieldSpell],
                'dwarf': [RuneShieldSpell, RuneHasteSpell, EarthSpikesSpell, RuneWallSpell, RuneMagicSpell, RuneBerserkerSpell, QuicksandSpell, EarthShockSpell],
                'shadow': [ForgetSpell, FrostRingSpell]
            }
            spells = []
            for spell_class in spell_classes.get(race, []):
                spell = spell_class()
                # ПРИМЕНЯЕМ ОВЕРРАЙДЫ СРАЗУ ПОСЛЕ СОЗДАНИЯ ЗАКЛИНАНИЯ
                self._apply_spell_overrides_to_instance(spell)
                spells.append(spell)
            return spells
        
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
            # Создаем заклинания с применением оверрайдов
            hero1_spells = create_spells_for_race(p1_race)
            # Добавляем класс героя
            hero1_params['hero_class'] = self.player1_hero_class
            self.hero1 = Hero(GRID_WIDTH-1, 0, p1_race, spells=hero1_spells, **hero1_params)
            self.hero1.used_spell_this_round = False
            self.hero1.game_ref = self
            # Применяем оверрайды к герою расы 1
            try:
                self._apply_unit_overrides_to_instance(self.hero1)
            except Exception:
                pass
            army = []
            for i, unit_cls in enumerate(races[p1_race]):
                unit = unit_cls(GRID_WIDTH-2, 1 + i*2, p1_race)
                unit.game_ref = self
                # Устанавливаем размер отряда (это также инициализирует unit_hp)
                self._set_default_squad_count(unit)
                # Убеждаемся, что unit_hp инициализирован даже для одиночных юнитов
                if not hasattr(unit, 'unit_hp') or unit.unit_hp is None:
                    unit.unit_hp = unit.max_health
                    unit.current_unit_hp = unit.health
                    unit.base_squad_count = getattr(unit, 'squad_count', 1)
                try:
                    self._apply_unit_overrides_to_instance(unit)
                except Exception:
                    pass
                army.append(unit)
            # ВАЖНО: Сначала применяем оверрайды ко всем юнитам, ПОТОМ добавляем бонусы героя
            # Это гарантирует, что параметры из JSON будут иметь приоритет
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
            # Создаем заклинания с применением оверрайдов
            hero2_spells = create_spells_for_race(p2_race)
            # Добавляем класс героя
            hero2_params['hero_class'] = self.player2_hero_class
            self.hero2 = Hero(0, 0, p2_race, spells=hero2_spells, **hero2_params)
            self.hero2.used_spell_this_round = False
            self.hero2.game_ref = self
            # Применяем оверрайды к герою расы 2
            try:
                self._apply_unit_overrides_to_instance(self.hero2)
            except Exception:
                pass
            army = []
            for i, unit_cls in enumerate(races[p2_race]):
                unit = unit_cls(1, 1 + i*2, p2_race)
                unit.game_ref = self
                # Устанавливаем размер отряда (это также инициализирует unit_hp)
                self._set_default_squad_count(unit)
                # Убеждаемся, что unit_hp инициализирован даже для одиночных юнитов
                if not hasattr(unit, 'unit_hp') or unit.unit_hp is None:
                    unit.unit_hp = unit.max_health
                    unit.current_unit_hp = unit.health
                    unit.base_squad_count = getattr(unit, 'squad_count', 1)
                try:
                    self._apply_unit_overrides_to_instance(unit)
                except Exception:
                    pass
                army.append(unit)
            # ВАЖНО: Сначала применяем оверрайды ко всем юнитам, ПОТОМ добавляем бонусы героя
            # Это гарантирует, что параметры из JSON будут иметь приоритет
            self.units.append(self.hero2)
            self.hero2.apply_bonuses_to_army(army)
            self.units.extend(army)
        # Применяем сохранённые оверрайды ко всем созданным юнитам ПОСЛЕДНИМИ
        # Это гарантирует, что параметры из JSON будут иметь абсолютный приоритет
        self._apply_overrides_to_all_units()

    def draw_grid(self):
        # Подсветка диапазона хода только для активного юнита (не героя)
        if self.selected_unit and not self.selected_unit.has_attacked and not isinstance(self.selected_unit, Hero):
            move_points = getattr(self.selected_unit, 'move_points_left', 0)
            if move_points > 0:
                reachable = self.get_reachable_cells(self.selected_unit.x, self.selected_unit.y, move_points)
                for (mx, my) in reachable:
                    dist = abs(mx - self.selected_unit.x) + abs(my - self.selected_unit.y)
                    max_alpha = 220  # Увеличенная яркость
                    min_alpha = 80  # Увеличенная минимальная яркость для четкости
                    if move_points > 1:
                        alpha = max(min_alpha, max_alpha - int((max_alpha-min_alpha) * (dist-1) / (move_points-1)))
                    else:
                        alpha = max_alpha
                    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    # Цвет заполняем без альфы, прозрачность задаём через set_alpha — совместимо с разными версиями pygame
                    surf.set_alpha(alpha)
                    surf.fill((80, 160, 255))
                    # Добавляем рамку для четкости (без альфы — прозрачность уже задана у поверхности)
                    pygame.draw.rect(surf, (120, 200, 255), (0, 0, CELL_SIZE, CELL_SIZE), 2)
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
        # В режиме наблюдения не рисуем кнопки управления, только тултипы
        if not self.spectator_mode:
            # Кнопка книги заклинаний (самая левая)
            is_hero = isinstance(self.selected_unit, Hero)
            can_cast = is_hero and self.selected_unit.spells and not getattr(self.selected_unit, 'used_spell_this_round', False)
            if can_cast:
                pygame.draw.rect(self.screen, (180, 120, 60), self.book_button_rect, border_radius=8)
                # Красивая книга
                pygame.draw.rect(self.screen, (220, 200, 120), (self.book_button_rect.x+6, self.book_button_rect.y+10, 36, 28), border_radius=4)
                pygame.draw.line(self.screen, (120,80,40), (self.book_button_rect.x+24, self.book_button_rect.y+10), (self.book_button_rect.x+24, self.book_button_rect.y+38), 3)
                # Страницы
                for i in range(3):
                    pygame.draw.line(self.screen, (150,120,80), (self.book_button_rect.x+12+i*4, self.book_button_rect.y+18), (self.book_button_rect.x+18+i*4, self.book_button_rect.y+18), 1)
            else:
                pygame.draw.rect(self.screen, (80, 80, 80), self.book_button_rect, border_radius=8)
                pygame.draw.rect(self.screen, (120, 120, 120), (self.book_button_rect.x+6, self.book_button_rect.y+10, 36, 28), border_radius=4)
                pygame.draw.line(self.screen, (60,60,60), (self.book_button_rect.x+24, self.book_button_rect.y+10), (self.book_button_rect.x+24, self.book_button_rect.y+38), 3)
            
            # Кнопка ожидания (вторая слева) - песочные часы
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                pygame.draw.rect(self.screen, (220, 200, 120), self.defend_button_rect, border_radius=8)
                # Песочные часы
                # Верхняя часть
                pygame.draw.polygon(self.screen, (240, 220, 140), [
                    (self.defend_button_rect.x+14, self.defend_button_rect.y+8),
                    (self.defend_button_rect.x+34, self.defend_button_rect.y+8),
                    (self.defend_button_rect.x+24, self.defend_button_rect.y+20)
                ])
                # Нижняя часть
                pygame.draw.polygon(self.screen, (240, 220, 140), [
                    (self.defend_button_rect.x+24, self.defend_button_rect.y+28),
                    (self.defend_button_rect.x+14, self.defend_button_rect.y+40),
                    (self.defend_button_rect.x+34, self.defend_button_rect.y+40)
                ])
                # Песок
                pygame.draw.circle(self.screen, (200, 180, 100), (self.defend_button_rect.x+24, self.defend_button_rect.y+35), 6)
            else:
                pygame.draw.rect(self.screen, (80, 80, 80), self.defend_button_rect, border_radius=8)
                pygame.draw.polygon(self.screen, (120, 120, 120), [
                    (self.defend_button_rect.x+14, self.defend_button_rect.y+8),
                    (self.defend_button_rect.x+34, self.defend_button_rect.y+8),
                    (self.defend_button_rect.x+24, self.defend_button_rect.y+20)
                ])
                pygame.draw.polygon(self.screen, (120, 120, 120), [
                    (self.defend_button_rect.x+24, self.defend_button_rect.y+28),
                    (self.defend_button_rect.x+14, self.defend_button_rect.y+40),
                    (self.defend_button_rect.x+34, self.defend_button_rect.y+40)
                ])
            
            # Кнопка защиты (третья) - красивый щит
            if self.selected_unit and not isinstance(self.selected_unit, Hero):
                pygame.draw.rect(self.screen, (100, 150, 200), self.skip_button_rect, border_radius=8)
                # Щит
                pygame.draw.ellipse(self.screen, (140, 180, 240), (self.skip_button_rect.x+8, self.skip_button_rect.y+8, 32, 20))
                pygame.draw.polygon(self.screen, (140, 180, 240), [
                    (self.skip_button_rect.x+10, self.skip_button_rect.y+18),
                    (self.skip_button_rect.x+38, self.skip_button_rect.y+18),
                    (self.skip_button_rect.x+24, self.skip_button_rect.y+38)
                ])
                # Крест на щите
                pygame.draw.line(self.screen, (180, 220, 255), (self.skip_button_rect.x+24, self.skip_button_rect.y+14), (self.skip_button_rect.x+24, self.skip_button_rect.y+28), 2)
                pygame.draw.line(self.screen, (180, 220, 255), (self.skip_button_rect.x+18, self.skip_button_rect.y+21), (self.skip_button_rect.x+30, self.skip_button_rect.y+21), 2)
            else:
                pygame.draw.rect(self.screen, (80, 80, 80), self.skip_button_rect, border_radius=8)
                pygame.draw.ellipse(self.screen, (120, 120, 120), (self.skip_button_rect.x+8, self.skip_button_rect.y+8, 32, 20))
                pygame.draw.polygon(self.screen, (120, 120, 120), [
                    (self.skip_button_rect.x+10, self.skip_button_rect.y+18),
                    (self.skip_button_rect.x+38, self.skip_button_rect.y+18),
                    (self.skip_button_rect.x+24, self.skip_button_rect.y+38)
                ])
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
        
        # В режиме наблюдения показываем подсказку
        if self.spectator_mode:
            spectator_font = pygame.font.Font(None, 24)
            spectator_text = spectator_font.render("Режим наблюдения - Нажмите ESC для выхода", True, (200, 200, 200))
            self.screen.blit(spectator_text, (SCREEN_WIDTH//2 - spectator_text.get_width()//2, SCREEN_HEIGHT - 100))
        # Книга заклинаний (на весь экран, с анимацией и иконками) - не показывается в режиме наблюдения и не показывается игроку когда ходит ИИ
        # Проверяем, не ход ли это ИИ
        is_ai_turn = False
        if self.selected_unit:
            if self.ai_controller_p1 and self.selected_unit.team == self.ai_controller_p1.ai_team:
                is_ai_turn = True
            elif self.ai_controller_p2 and self.selected_unit.team == self.ai_controller_p2.ai_team:
                is_ai_turn = True
        
        if self.spellbook_open and not self.spectator_mode and not is_ai_turn and isinstance(self.selected_unit, Hero) and self.selected_unit.spells:
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
            # Обработка анимации перелистывания
            flip_anim = getattr(self, 'spellbook_flip_animation', None)
            if flip_anim:
                # Во время анимации показываем промежуточное состояние
                progress = flip_anim['progress']
                if progress < 0.5:
                    # Показываем старую школу
                    current_display_school = flip_anim['from_school']
                else:
                    # Показываем новую школу
                    current_display_school = flip_anim['to_school']
            else:
                current_display_school = getattr(self, 'spellbook_selected_school', 'all')
            
            filtered_spells = spells_by_school.get(current_display_school, [])
            # --- Фон книги - фолиант архимага (магический) ---
            book_surface = pygame.Surface((book_w, book_h), pygame.SRCALPHA)
            
            # Анимация перелистывания - эффект страницы
            if flip_anim:
                progress = flip_anim['progress']
                # Эффект переворачивающейся страницы
                if flip_anim['direction'] == 1:
                    # Перелистывание вправо
                    flip_offset = int((progress - 0.5) * book_w * 2)
                else:
                    # Перелистывание влево
                    flip_offset = int((0.5 - progress) * book_w * 2)
                
                # Создаем эффект объема при перелистывании
                if 0.2 <= progress <= 0.8:
                    # Показываем тень от переворачивающейся страницы
                    shadow_alpha = int(abs(progress - 0.5) * 255 * 2)
                    shadow_surf = pygame.Surface((book_w, book_h), pygame.SRCALPHA)
                    shadow_surf.fill((0, 0, 0, shadow_alpha))
                    book_surface.blit(shadow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Магический пергамент с легким сиянием
            for y in range(book_h):
                # Создаем эффект магического пергамента с мягкими переливами
                variation = int(math.sin(y * 0.08 + 0.5) * 3 + math.cos(y * 0.12) * 2)
                color_r = max(245, min(255, 250 + variation))
                color_g = max(240, min(255, 245 + variation))
                color_b = max(230, min(250, 240 + variation))
                pygame.draw.line(book_surface, (color_r, color_g, color_b), 
                                (0, y), (book_w, y))
            
            # Магические узоры и символы
            random.seed(42)  # Для стабильности
            # Магические руны и символы
            for _ in range(20):
                x = random.randint(15, book_w - 15)
                y = random.randint(15, book_h - 15)
                size = random.randint(4, 8)
                # Светящиеся магические символы
                pygame.draw.circle(book_surface, (180, 200, 255, 30), (x, y), size)
                pygame.draw.circle(book_surface, (200, 220, 255, 50), (x, y), size // 2)
            
            # Магические линии и узоры
            for _ in range(12):
                x1 = random.randint(20, book_w - 20)
                y1 = random.randint(20, book_h - 20)
                length = random.randint(15, 35)
                angle = random.random() * 3.14159 * 2
                x2 = int(x1 + math.cos(angle) * length)
                y2 = int(y1 + math.sin(angle) * length)
                pygame.draw.line(book_surface, (200, 220, 255, 40), (x1, y1), (x2, y2), 2)
            
            # Блестящая обложка архимага
            # Градиентная обложка с магическим сиянием
            for y in range(book_h):
                glow_intensity = int(30 * (0.5 + 0.5 * math.sin(y * 0.1)))
                pygame.draw.line(book_surface, (100, 80, 150, glow_intensity),
                               (0, y), (book_w, y))
            pygame.draw.rect(book_surface, (60, 40, 100), (0,0,book_w,book_h), 14, border_radius=24)
            # Внутренняя рамка с магическим свечением
            pygame.draw.rect(book_surface, (120, 100, 180), (12,12,book_w-24,book_h-24), 4, border_radius=20)
            # Магические углы с рунами
            corner_size = 24
            for corner_x in [0, book_w - corner_size]:
                for corner_y in [0, book_h - corner_size]:
                    # Магические углы с сиянием
                    pygame.draw.polygon(book_surface, (120, 100, 180), [
                        (corner_x, corner_y),
                        (corner_x + corner_size, corner_y),
                        (corner_x + corner_size, corner_y + corner_size),
                        (corner_x, corner_y + corner_size)
                    ])
                    # Магические символы в углах
                    center_cx = corner_x + corner_size // 2
                    center_cy = corner_y + corner_size // 2
                    pygame.draw.circle(book_surface, (180, 160, 220, 180), (center_cx, center_cy), 8)
                    pygame.draw.circle(book_surface, (220, 200, 255, 100), (center_cx, center_cy), 4)
                    # Руны в углах
                    for i in range(4):
                        angle = i * math.pi / 2
                        rune_x = int(center_cx + math.cos(angle) * 6)
                        rune_y = int(center_cy + math.sin(angle) * 6)
                        pygame.draw.circle(book_surface, (255, 255, 255, 200), (rune_x, rune_y), 2)
            # --- Кнопка закрытия (крестик) ---
            close_rect = pygame.Rect(book_w-44, 12, 32, 32)
            pygame.draw.rect(book_surface, (200,60,60), close_rect, border_radius=8)
            pygame.draw.line(book_surface, (255,255,255), (book_w-36, 20), (book_w-20, 36), 4)
            pygame.draw.line(book_surface, (255,255,255), (book_w-20, 20), (book_w-36, 36), 4)
            self.spellbook_close_rect = pygame.Rect(book_x+book_w-44, book_y+12, 32, 32)
            # --- Отображение маны текущего героя ---
            if isinstance(self.selected_unit, Hero):
                mana_font = pygame.font.Font(None, 28)
                mana_text = f"Мана: {self.selected_unit.mana}/{self.selected_unit.max_mana}"
                mana_surf_shadow = mana_font.render(mana_text, True, (40, 30, 60))
                mana_surf = mana_font.render(mana_text, True, (255, 245, 220))
                # фон-плашка
                mana_bg = pygame.Surface((mana_surf.get_width()+16, mana_surf.get_height()+8), pygame.SRCALPHA)
                mana_bg.fill((60, 40, 100, 160))
                book_surface.blit(mana_bg, (16, 12))
                book_surface.blit(mana_surf_shadow, (24+2, 14+2))
                book_surface.blit(mana_surf, (24, 14))
            # --- Переплёт (спайн) - магический архимагский ---
            spine_x = book_w // 2
            # Основание переплета с магическим свечением
            for y in range(book_h):
                glow = int(50 + 30 * math.sin(y * 0.15))
                pygame.draw.line(book_surface, (100, 80, 150, glow),
                               (spine_x - 12, y), (spine_x + 12, y))
            pygame.draw.rect(book_surface, (80, 60, 120), (spine_x-12, 0, 24, book_h), border_radius=8)
            # Магические руны на переплете
            for i in range(5):
                y_pos = book_h // 6 + i * (book_h // 5)
                # Светящиеся руны
                pygame.draw.ellipse(book_surface, (160, 140, 200, 200), 
                                  (spine_x-10, y_pos-8, 20, 16))
                pygame.draw.ellipse(book_surface, (200, 180, 255, 150), 
                                  (spine_x-6, y_pos-4, 12, 8))
                # Магические точки
                pygame.draw.circle(book_surface, (255, 255, 255, 255), (spine_x, y_pos), 3)
                # Линии энергии
                pygame.draw.line(book_surface, (180, 160, 220), 
                               (spine_x-8, y_pos), (spine_x+8, y_pos), 2)
            # Центральная линия с магическим свечением
            for y in range(0, book_h, 3):
                alpha = int(150 + 100 * math.sin(y * 0.2))
                pygame.draw.line(book_surface, (180, 160, 255, alpha), 
                               (spine_x, y), (spine_x, min(y + 2, book_h)), 2)
            # Сияние по краям переплета
            pygame.draw.line(book_surface, (120, 100, 180, 180), (spine_x-12, 0), (spine_x-12, book_h), 3)
            pygame.draw.line(book_surface, (120, 100, 180, 180), (spine_x+12, 0), (spine_x+12, book_h), 3)
            # --- Закладки школ ---
            tab_w, tab_h = 56, 48
            # По умолчанию выбрана вкладка "все заклятия"
            selected_school = getattr(self, 'spellbook_selected_school', 'all')
            self.spellbook_selected_school = selected_school
            
            # Для отображения используем текущую (во время анимации может быть разной)
            display_school = current_display_school if 'current_display_school' in locals() else selected_school
            for i, (school, color) in enumerate(school_list):
                tab_x = book_x + 20 + i*(tab_w+8)
                tab_y = book_y - 36
                has_spells = len(spells_by_school[school]) > 0
                tab_color = color if has_spells else (120,120,120)
                if school == display_school:
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
            # 2 столбца на каждой странице (12 заклинаний на странице)
            spells_per_page = 12
            columns = 2
            rows = 6
            spell_size = 64
            page = getattr(self, 'spellbook_page', 0)
            total_pages = (len(filtered_spells) + spells_per_page - 1) // spells_per_page
            # --- Кнопки перелистывания (уголки страниц) ---
            self.spellbook_next_page_rect = None
            self.spellbook_prev_page_rect = None
            if total_pages > 1:
                if page < total_pages-1:
                    # Уголок вправо (правый нижний угол) - координаты относительно book_surface
                    next_page_rect_local = pygame.Rect(book_w-48, book_h-48, 40, 40)
                    # Сохраняем глобальные координаты для обработки кликов
                    self.spellbook_next_page_rect = pygame.Rect(book_x + book_w-48, book_y + book_h-48, 40, 40)
                    pygame.draw.polygon(book_surface, (200,180,120), [
                        (book_w-8, book_h-8), (book_w-48, book_h-8), (book_w-8, book_h-48)
                    ])
                    pygame.draw.line(book_surface, (120,100,60), (book_w-48, book_h-8), (book_w-8, book_h-48), 2)
                if page > 0:
                    # Уголок влево (левый нижний угол) - координаты относительно book_surface
                    prev_page_rect_local = pygame.Rect(8, book_h-48, 40, 40)
                    # Сохраняем глобальные координаты для обработки кликов
                    self.spellbook_prev_page_rect = pygame.Rect(book_x + 8, book_y + book_h-48, 40, 40)
                    pygame.draw.polygon(book_surface, (200,180,120), [
                        (8, book_h-8), (48, book_h-8), (8, book_h-48)
                    ])
                    pygame.draw.line(book_surface, (120,100,60), (48, book_h-8), (8, book_h-48), 2)
            # --- Иконки заклинаний на странице ---
            # Расположение: слева 2 столбца × 3 строки, справа 2 столбца × 3 строки (12 заклинаний)
            spell_size = 64
            spell_spacing = 10
            tiptul = None
            tiptul_rect = None
            start_idx = page * spells_per_page
            end_idx = min(start_idx + spells_per_page, len(filtered_spells))
            for idx, spell in enumerate(filtered_spells[start_idx:end_idx]):
                # Первые 6 заклинаний (0-5): левая сторона (2 столбца × 3 строки)
                # Следующие 6 заклинаний (6-11): правая сторона (2 столбца × 3 строки)
                if idx < 6:
                    # Левая сторона
                    col = idx % 2  # 0 или 1 внутри левого блока
                    row = idx // 2  # 0, 1, 2
                    sx = 60 + col * (spell_size + spell_spacing)
                    sy = 60 + row * 100
                else:
                    # Правая сторона
                    local_idx = idx - 6
                    col = local_idx % 2  # 0 или 1 внутри правого блока
                    row = local_idx // 2  # 0, 1, 2
                    sx = book_w//2 + 36 + col * (spell_size + spell_spacing)
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
                    # Кубок со святой водой: детализированный, с бликами и золотом
                    cx, cy = icon_box.center
                    # Золотая ножка кубка
                    pygame.draw.rect(book_surface, (200,160,60), (cx-3, cy+9, 6, 5))
                    pygame.draw.ellipse(book_surface, (220,180,80), (cx-5, cy+12, 10, 3))
                    # Чаша
                    pygame.draw.rect(book_surface, (220,180,80), (cx-8, cy-4, 16, 7))
                    pygame.draw.rect(book_surface, (240,200,100), (cx-8, cy-4, 16, 2))
                    # Священная вода
                    pygame.draw.ellipse(book_surface, (200,220,255), (cx-6, cy-2, 12, 5))
                    pygame.draw.ellipse(book_surface, (180,200,255), (cx-6, cy+1, 12, 4))
                    # Блики на чаше
                    pygame.draw.arc(book_surface, (255,255,220), (cx-7, cy-3, 14, 6), math.radians(10), math.radians(80), 2)
                    # Святое сияние над кубком
                    for i in range(5):
                        angle = math.radians(-90 + (i-2) * 15)
                        lx = cx + int(10 * math.sin(angle))
                        ly = cy - 8 - int(8 * abs(math.cos(angle)))
                        pygame.draw.line(book_surface, (255,255,200,150), (cx, cy-6), (lx, ly), 1)
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
                    # Череп с темной магией
                    cx, cy = icon_box.center
                    # Череп
                    pygame.draw.ellipse(book_surface, (220,220,220), (cx-10, cy-10, 20, 16))
                    pygame.draw.ellipse(book_surface, (200,200,200), (cx-10, cy-8, 20, 12))
                    # Глазницы с красным свечением
                    pygame.draw.ellipse(book_surface, (40,40,40), (cx-7, cy-6, 5, 6))
                    pygame.draw.ellipse(book_surface, (40,40,40), (cx+2, cy-6, 5, 6))
                    pygame.draw.circle(book_surface, (220,0,0), (cx-5, cy-4), 2)
                    pygame.draw.circle(book_surface, (220,0,0), (cx+4, cy-4), 2)
                    # Нос
                    pygame.draw.polygon(book_surface, (60,60,60), [(cx-1, cy), (cx+1, cy), (cx, cy+3)])
                    # Зубы
                    for i in range(5):
                        tx = cx - 6 + i * 3
                        pygame.draw.rect(book_surface, (200,200,200), (tx, cy+4, 2, 3))
                    # Темная аура проклятия
                    for i in range(4):
                        angle = math.radians(i*90)
                        px = cx + int(14*math.cos(angle))
                        py = cy + int(14*math.sin(angle))
                        pygame.draw.circle(book_surface, (140,0,100), (px, py), 3)
                        pygame.draw.circle(book_surface, (180,0,140), (px, py), 2)
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
                elif spell.icon == 'fire_wall':
                    # Огненная стена - вертикальная полоса пламени
                    cx, cy = icon_box.center
                    # Вертикальные языки пламени
                    for i in range(3):
                        wall_x = cx - 8 + i * 8
                        # Основание пламени
                        pygame.draw.polygon(book_surface, (255, 120, 40), [
                            (wall_x-3, cy+10), (wall_x+3, cy+10), (wall_x+2, cy+2), (wall_x-2, cy+2)
                        ])
                        # Верхние языки
                        pygame.draw.polygon(book_surface, (255, 200, 80), [
                            (wall_x-2, cy+2), (wall_x+2, cy+2), (wall_x+1, cy-8), (wall_x-1, cy-8)
                        ])
                        pygame.draw.polygon(book_surface, (255, 255, 150), [
                            (wall_x-1, cy-2), (wall_x+1, cy-2), (wall_x, cy-10)
                        ])
                elif spell.icon == 'meteor_rain':
                    # Метеоритный дождь - несколько падающих метеоритов
                    cx, cy = icon_box.center
                    # Несколько метеоритов сверху вниз
                    for i, offset in enumerate([-8, -2, 2, 8]):
                        meteor_x = cx + offset
                        meteor_y = cy - 12 + i * 8
                        # Метеорит
                        pygame.draw.circle(book_surface, (200, 100, 40), (meteor_x, meteor_y), 4)
                        pygame.draw.circle(book_surface, (255, 150, 80), (meteor_x, meteor_y), 2)
                        # Хвост метеорита
                        pygame.draw.line(book_surface, (255, 180, 120), (meteor_x, meteor_y+4), (meteor_x, meteor_y+10), 2)
                elif spell.icon == 'ice_arrow':
                    # Ледяная стрела с инеем
                    cx, cy = icon_box.center
                    # Древко стрелы
                    pygame.draw.line(book_surface, (180, 200, 220), (cx-8, cy+5), (cx+8, cy-5), 3)
                    # Наконечник изо льда
                    pygame.draw.polygon(book_surface, (200, 230, 255), [(cx+8, cy-5), (cx+12, cy-8), (cx+9, cy-1)])
                    pygame.draw.polygon(book_surface, (150, 200, 255), [(cx+9, cy-4), (cx+11, cy-7), (cx+9, cy-2)])
                    # Снежинки вокруг
                    for i in range(6):
                        angle = math.radians(i * 60)
                        snow_x = cx + int(10 * math.cos(angle))
                        snow_y = cy + int(10 * math.sin(angle))
                        pygame.draw.circle(book_surface, (220, 240, 255), (snow_x, snow_y), 1)
                        # Лучи снежинки
                        for j in range(4):
                            ray_angle = angle + math.radians(j * 90)
                            ray_x = snow_x + int(3 * math.cos(ray_angle))
                            ray_y = snow_y + int(3 * math.sin(ray_angle))
                            pygame.draw.circle(book_surface, (240, 250, 255), (ray_x, ray_y), 1)
                elif spell.icon == 'phantom':
                    # Фантом - призрачная фигура
                    cx, cy = icon_box.center
                    # Полупрозрачное тело фантома (синеватое)
                    pygame.draw.ellipse(book_surface, (100, 150, 255, 180), (cx-8, cy+2, 16, 12))
                    pygame.draw.circle(book_surface, (120, 180, 255, 180), (cx, cy-4), 6)
                    # Призрачный хвост
                    pygame.draw.polygon(book_surface, (80, 130, 255, 150), [
                        (cx-6, cy+14), (cx+6, cy+14), (cx+3, cy+20), (cx-3, cy+20)
                    ])
                    # Сияние вокруг
                    for i in range(8):
                        angle = math.radians(i * 45)
                        glow_x = cx + int(12 * math.cos(angle))
                        glow_y = cy + int(12 * math.sin(angle))
                        pygame.draw.circle(book_surface, (150, 200, 255, 100), (glow_x, glow_y), 2)
                elif spell.icon == 'heal':
                    # Иконка исцеления: зелёный крест с сиянием
                    cx, cy = icon_box.center
                    # Зелёное сияние
                    for i in range(3):
                        r = 14 - i * 3
                        alpha = 120 - i * 40
                        pygame.draw.circle(book_surface, (80,255,120,alpha), (cx, cy), r)
                    # Крест исцеления
                    pygame.draw.rect(book_surface, (60,255,100), (cx-2, cy-10, 4, 20))
                    pygame.draw.rect(book_surface, (60,255,100), (cx-10, cy-2, 20, 4))
                    # Блики на кресте
                    pygame.draw.rect(book_surface, (180,255,200), (cx-1, cy-9, 2, 18))
                    pygame.draw.rect(book_surface, (180,255,200), (cx-9, cy-1, 18, 2))
                    # Искры исцеления
                    for i in range(4):
                        angle = math.radians(45 + i*90)
                        sx = cx + int(12 * math.cos(angle))
                        sy = cy + int(12 * math.sin(angle))
                        pygame.draw.circle(book_surface, (120,255,180), (sx, sy), 2)
                elif spell.icon == 'shield':
                    # Иконка щита: металлический щит с бликом
                    cx, cy = icon_box.center
                    # Щит
                    pygame.draw.ellipse(book_surface, (80,120,200), (cx-11, cy-10, 22, 20))
                    pygame.draw.ellipse(book_surface, (120,160,240), (cx-9, cy-8, 18, 16))
                    # Центральная эмблема
                    pygame.draw.circle(book_surface, (200,200,220), (cx, cy), 5)
                    pygame.draw.circle(book_surface, (160,180,240), (cx, cy), 3)
                    # Блик на щите
                    pygame.draw.arc(book_surface, (200,220,255), (cx-8, cy-7, 16, 14), math.radians(30), math.radians(150), 2)
                    # Магическое защитное сияние
                    for i in range(3):
                        angle = math.radians(i*120)
                        sx = cx + int(10 * math.cos(angle))
                        sy = cy + int(10 * math.sin(angle))
                        pygame.draw.circle(book_surface, (150,190,255), (sx, sy), 2)
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
                elif spell.icon == 'haste':
                    # Иконка ускорения воздуха: бело-голубые крылья и потоки ветра
                    cx, cy = icon_box.center
                    pygame.draw.arc(book_surface, (200,240,255), (cx-12, cy-8, 24, 16), math.radians(200), math.radians(340), 3)
                    pygame.draw.arc(book_surface, (255,255,255), (cx-10, cy-6, 20, 12), math.radians(200), math.radians(340), 2)
                    for dx in [-6, -2, 2, 6]:
                        pygame.draw.line(book_surface, (180,220,255), (cx+dx, cy+6), (cx+dx+4, cy-6), 2)
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
                elif spell.icon == 'raise_undead':
                    # Исцеление нежити: череп с зелёным свечением
                    cx, cy = icon_box.center
                    pygame.draw.ellipse(book_surface, (200, 220, 200), (cx-10, cy-8, 20, 16))
                    pygame.draw.circle(book_surface, (60, 255, 120), (cx-4, cy-2), 2)
                    pygame.draw.circle(book_surface, (60, 255, 120), (cx+4, cy-2), 2)
                    for i in range(5):
                        pygame.draw.line(book_surface, (180, 200, 180), (cx-6+i*3, cy+5), (cx-6+i*3, cy+7), 1)
                elif spell.icon == 'fire_shield':
                    # Огненный щит: щит в пламени
                    cx, cy = icon_box.center
                    pygame.draw.ellipse(book_surface, (255, 140, 40), (cx-11, cy-10, 22, 20))
                    pygame.draw.ellipse(book_surface, (255, 200, 80), (cx-8, cy-7, 16, 14))
                    # Языки пламени по краям
                    for angle in [0, 1.57, 3.14, 4.71]:
                        fx = cx + int(10 * math.cos(angle))
                        fy = cy + int(10 * math.sin(angle))
                        pygame.draw.polygon(book_surface, (255, 120, 40), [
                            (fx, fy), (fx+int(4*math.cos(angle+0.3)), fy+int(4*math.sin(angle+0.3))),
                            (fx+int(4*math.cos(angle-0.3)), fy+int(4*math.sin(angle-0.3)))
                        ])
                elif spell.icon == 'resurrection':
                    # Воскрешение: ангельские крылья
                    cx, cy = icon_box.center
                    # Левое крыло
                    pygame.draw.arc(book_surface, (255, 255, 220), (cx-14, cy-6, 12, 16), math.radians(20), math.radians(160), 3)
                    pygame.draw.arc(book_surface, (240, 240, 200), (cx-12, cy-4, 10, 12), math.radians(20), math.radians(160), 2)
                    # Правое крыло
                    pygame.draw.arc(book_surface, (255, 255, 220), (cx+2, cy-6, 12, 16), math.radians(20), math.radians(160), 3)
                    pygame.draw.arc(book_surface, (240, 240, 200), (cx+4, cy-4, 10, 12), math.radians(20), math.radians(160), 2)
                    # Нимб
                    pygame.draw.circle(book_surface, (255, 255, 180), (cx, cy-10), 6, 2)
                elif spell.icon == 'ice_shield':
                    # Ледяной щит: щит из льда с кристаллами
                    cx, cy = icon_box.center
                    pygame.draw.ellipse(book_surface, (180, 220, 255), (cx-11, cy-10, 22, 20))
                    pygame.draw.ellipse(book_surface, (220, 240, 255), (cx-8, cy-7, 16, 14))
                    # Ледяные кристаллы
                    for angle in [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]:
                        fx = cx + int(9 * math.cos(angle))
                        fy = cy + int(9 * math.sin(angle))
                        pygame.draw.polygon(book_surface, (200, 235, 255), [
                            (fx, fy-3), (fx+2, fy), (fx, fy+3), (fx-2, fy)
                        ])
                elif spell.icon == 'lightning':
                    # Молния: зигзагообразная молния
                    cx, cy = icon_box.center
                    points = [(cx, cy-12), (cx-3, cy-4), (cx+3, cy-2), (cx-2, cy+4), (cx+4, cy+12)]
                    for i in range(len(points)-1):
                        pygame.draw.line(book_surface, (255, 255, 180), points[i], points[i+1], 4)
                        pygame.draw.line(book_surface, (255, 255, 255), points[i], points[i+1], 2)
                    # Искры вокруг
                    for angle in [0, 1.57, 3.14]:
                        sx = cx + int(8 * math.cos(angle))
                        sy = cy - 6 + int(8 * math.sin(angle))
                        pygame.draw.circle(book_surface, (255, 255, 200), (sx, sy), 2)
                elif spell.icon == 'chain_lightning':
                    # Цепная молния: несколько молний, соединённых вместе
                    cx, cy = icon_box.center
                    # Основная молния
                    points1 = [(cx-6, cy-12), (cx-4, cy-4), (cx-2, cy-2), (cx, cy+4), (cx+2, cy+12)]
                    for i in range(len(points1)-1):
                        pygame.draw.line(book_surface, (255, 255, 180), points1[i], points1[i+1], 3)
                        pygame.draw.line(book_surface, (255, 255, 255), points1[i], points1[i+1], 1)
                    # Вторая молния отскакивает
                    points2 = [(cx+2, cy+6), (cx+4, cy-2), (cx+6, cy-6), (cx+8, cy-10)]
                    for i in range(len(points2)-1):
                        pygame.draw.line(book_surface, (255, 255, 150), points2[i], points2[i+1], 2)
                    # Третья молния
                    points3 = [(cx-2, cy+8), (cx-4, cy+2), (cx-6, cy-2), (cx-8, cy-8)]
                    for i in range(len(points3)-1):
                        pygame.draw.line(book_surface, (255, 255, 150), points3[i], points3[i+1], 2)
                    # Искры вокруг
                    for angle in [0, 1.57, 3.14, 4.71]:
                        sx = cx + int(10 * math.cos(angle))
                        sy = cy + int(10 * math.sin(angle))
                        pygame.draw.circle(book_surface, (255, 255, 200), (sx, sy), 2)
                elif spell.icon == 'accuracy':
                    # Точность: линза с монеткой внутри
                    cx, cy = icon_box.center
                    # Линза (эллипс)
                    pygame.draw.ellipse(book_surface, (180, 220, 255, 200), (cx-12, cy-14, 24, 28), 2)
                    pygame.draw.ellipse(book_surface, (220, 240, 255, 150), (cx-10, cy-12, 20, 24))
                    # Монетка (круг)
                    pygame.draw.circle(book_surface, (255, 215, 0), (cx, cy), 6)
                    pygame.draw.circle(book_surface, (200, 150, 0), (cx, cy), 4)
                    # Блик на линзе
                    pygame.draw.ellipse(book_surface, (255, 255, 255, 180), (cx-6, cy-10, 8, 6))
                    # Лучи точности
                    for i in range(4):
                        angle = i * 1.57
                        start_x = cx + int(12 * math.cos(angle))
                        start_y = cy + int(12 * math.sin(angle))
                        end_x = cx + int(16 * math.cos(angle))
                        end_y = cy + int(16 * math.sin(angle))
                        pygame.draw.line(book_surface, (200, 220, 255), (start_x, start_y), (end_x, end_y), 2)
                elif spell.icon == 'quicksand':
                    # Зыбучие пески: бурлящая лужа грязи
                    cx, cy = icon_box.center
                    # Основная лужа (коричневая)
                    pygame.draw.circle(book_surface, (80, 60, 40), (cx, cy), 10)
                    pygame.draw.circle(book_surface, (100, 75, 50), (cx, cy), 8)
                    # Пузыри
                    for i in range(4):
                        angle = i * 1.57
                        bubble_x = cx + int(5 * math.cos(angle))
                        bubble_y = cy + int(5 * math.sin(angle))
                        pygame.draw.circle(book_surface, (120, 90, 60), (bubble_x, bubble_y), 2)
                    # Частицы грязи
                    for i in range(6):
                        angle = i * 1.047
                        particle_x = cx + int(8 * math.cos(angle))
                        particle_y = cy + int(8 * math.sin(angle))
                        pygame.draw.circle(book_surface, (90, 70, 45), (particle_x, particle_y), 1)
                elif spell.icon == 'earth_shock':
                    # Шок земли: фиолетовый гравитационный купол
                    cx, cy = icon_box.center
                    # Купол (фиолетовый)
                    for layer in range(3):
                        layer_size = 12 - layer * 3
                        pygame.draw.circle(book_surface, (180, 100, 255), (cx, cy), layer_size, 2)
                    # Центр (чёрная дыра)
                    pygame.draw.circle(book_surface, (0, 0, 0), (cx, cy), 4)
                    pygame.draw.circle(book_surface, (50, 0, 80), (cx, cy), 6, 1)
                    # Частицы вокруг
                    for i in range(8):
                        angle = i * 0.785
                        particle_x = cx + int(10 * math.cos(angle))
                        particle_y = cy + int(10 * math.sin(angle))
                        pygame.draw.circle(book_surface, (200, 120, 255), (particle_x, particle_y), 2)
                    # Взрывные волны
                    for wave in range(2):
                        wave_size = 14 - wave * 3
                        pygame.draw.circle(book_surface, (255, 150, 50), (cx, cy), wave_size, 1)
                elif spell.icon == 'prayer':
                    # Молитва: крылья ангела с перьями
                    cx, cy = icon_box.center
                    # Крылья (белые)
                    for wing_side in [-1, 1]:
                        wing_x = cx + wing_side * 8
                        for feather_idx in range(3):
                            feather_y = cy - 4 + feather_idx * 4
                            feather_size = 3 - feather_idx
                            pygame.draw.circle(book_surface, (255, 255, 255), (wing_x, feather_y), feather_size)
                    # Центральное свечение
                    pygame.draw.circle(book_surface, (255, 255, 200), (cx, cy), 6)
                    pygame.draw.circle(book_surface, (255, 255, 255), (cx, cy), 4)
                    # Лучи света
                    for i in range(6):
                        angle = i * 1.047
                        end_x = cx + int(10 * math.cos(angle))
                        end_y = cy + int(10 * math.sin(angle))
                        pygame.draw.line(book_surface, (255, 255, 200), (cx, cy), (end_x, end_y), 2)
                elif spell.icon == 'blindness':
                    # Ослепление: слепящие звезды
                    cx, cy = icon_box.center
                    # Звезды вокруг центра
                    for star_idx in range(4):
                        star_angle = star_idx * 1.57
                        star_x = cx + int(8 * math.cos(star_angle))
                        star_y = cy + int(8 * math.sin(star_angle))
                        # Звезда (крест)
                        for ray_idx in range(4):
                            ray_angle = ray_idx * (math.pi / 2)
                            ray_end_x = star_x + int(4 * math.cos(ray_angle))
                            ray_end_y = star_y + int(4 * math.sin(ray_angle))
                            pygame.draw.line(book_surface, (255, 255, 200), (star_x, star_y), (ray_end_x, ray_end_y), 2)
                        pygame.draw.circle(book_surface, (255, 255, 255), (star_x, star_y), 2)
                    # Центральная вспышка
                    pygame.draw.circle(book_surface, (255, 255, 255), (cx, cy), 6)
                    pygame.draw.circle(book_surface, (255, 255, 200), (cx, cy), 4)
                elif spell.icon == 'earth_spikes':
                    # Земляные шипы: множество каменных шипов
                    cx, cy = icon_box.center
                    for i in range(5):
                        angle = i * 0.6 - 1.2
                        spike_h = 8 + (i % 2) * 4
                        base_x = cx - 8 + i * 4
                        pygame.draw.polygon(book_surface, (140, 120, 100), [
                            (base_x-2, cy+8), (base_x+2, cy+8), (base_x, cy+8-spike_h)
                        ])
                        pygame.draw.polygon(book_surface, (180, 160, 140), [
                            (base_x-2, cy+8), (base_x, cy+8-spike_h), (base_x-1, cy+8-spike_h+2)
                        ])
                elif spell.icon == 'counterstrike':
                    # Контрудар: два скрещенных меча
                    cx, cy = icon_box.center
                    # Первый меч
                    pygame.draw.line(book_surface, (200, 200, 220), (cx-8, cy-8), (cx+4, cy+4), 3)
                    pygame.draw.rect(book_surface, (180, 160, 60), (cx-10, cy-10, 4, 4))
                    # Второй меч
                    pygame.draw.line(book_surface, (200, 200, 220), (cx+8, cy-8), (cx-4, cy+4), 3)
                    pygame.draw.rect(book_surface, (180, 160, 60), (cx+6, cy-10, 4, 4))
                    # Искры столкновения
                    for i in range(4):
                        angle = i * 1.57
                        sx = cx + int(6 * math.cos(angle))
                        sy = cy + int(6 * math.sin(angle))
                        pygame.draw.circle(book_surface, (255, 200, 80), (sx, sy), 2)
                elif spell.icon == 'rune_wall':
                    # Руническая стена: каменная стена с рунами
                    cx, cy = icon_box.center
                    # Камни стены
                    for i in range(3):
                        bx = cx - 8 + i * 8
                        pygame.draw.rect(book_surface, (120, 110, 100), (bx, cy-8, 7, 16))
                        pygame.draw.rect(book_surface, (140, 130, 120), (bx, cy-8, 7, 2))
                    # Светящиеся руны
                    for i in range(3):
                        rx = cx - 6 + i * 6
                        pygame.draw.circle(book_surface, (100, 200, 255), (rx, cy), 2)
                        pygame.draw.line(book_surface, (120, 220, 255), (rx, cy-3), (rx, cy+3), 1)
                elif spell.icon == 'weakness':
                    # Слабость: падающая фигурка
                    cx, cy = icon_box.center
                    # Фигурка человека в слабости
                    pygame.draw.circle(book_surface, (160, 140, 160), (cx, cy-6), 4)
                    pygame.draw.line(book_surface, (160, 140, 160), (cx, cy-2), (cx, cy+6), 3)
                    # Руки опущены
                    pygame.draw.line(book_surface, (160, 140, 160), (cx, cy), (cx-4, cy+4), 2)
                    pygame.draw.line(book_surface, (160, 140, 160), (cx, cy), (cx+4, cy+4), 2)
                    # Ноги
                    pygame.draw.line(book_surface, (160, 140, 160), (cx, cy+6), (cx-3, cy+10), 2)
                    pygame.draw.line(book_surface, (160, 140, 160), (cx, cy+6), (cx+3, cy+10), 2)
                    # Фиолетовая аура слабости
                    for i in range(3):
                        pygame.draw.circle(book_surface, (140, 0, 140, 100-i*30), (cx, cy), 8+i*3, 1)
                elif spell.icon == 'rune_magic':
                    # Руна магии: камень с синим магическим знаком
                    cx, cy = icon_box.center
                    # Камень (серый)
                    pygame.draw.ellipse(book_surface, (120, 120, 140), icon_box, 0)
                    pygame.draw.ellipse(book_surface, (80, 80, 100), icon_box.inflate(-8, -8), 2)
                    # Магический знак (синий)
                    # Звезда магии
                    for i in range(5):
                        angle = i * (2 * math.pi / 5) - math.pi / 2
                        x1 = cx + int(6 * math.cos(angle))
                        y1 = cy + int(6 * math.sin(angle))
                        x2 = cx + int(10 * math.cos(angle + math.pi / 5))
                        y2 = cy + int(10 * math.sin(angle + math.pi / 5))
                        pygame.draw.line(book_surface, (80, 150, 255), (cx, cy), (x1, y1), 2)
                        pygame.draw.line(book_surface, (120, 180, 255), (x1, y1), (x2, y2), 2)
                    # Центральный круг
                    pygame.draw.circle(book_surface, (100, 160, 255), (cx, cy), 4)
                    # Синие частицы
                    for i in range(6):
                        angle = i * (math.pi / 3)
                        px = cx + int(12 * math.cos(angle))
                        py = cy + int(12 * math.sin(angle))
                        pygame.draw.circle(book_surface, (100, 180, 255, 180), (px, py), 2)
                elif spell.icon == 'rune_berserker':
                    # Руна берсерка: камень с красным агрессивным знаком
                    cx, cy = icon_box.center
                    # Камень (темно-серый/красноватый)
                    pygame.draw.ellipse(book_surface, (140, 80, 80), icon_box, 0)
                    pygame.draw.ellipse(book_surface, (100, 50, 50), icon_box.inflate(-8, -8), 2)
                    # Агрессивный знак (красный)
                    # Зубчатый круг
                    pygame.draw.circle(book_surface, (255, 100, 60), (cx, cy), 10, 3)
                    # Зубчатые линии агрессии
                    for i in range(4):
                        angle = i * (math.pi / 2)
                        px1 = cx + int(6 * math.cos(angle))
                        py1 = cy + int(6 * math.sin(angle))
                        px2 = cx + int(10 * math.cos(angle))
                        py2 = cy + int(10 * math.sin(angle))
                        pygame.draw.line(book_surface, (255, 150, 80), (px1, py1), (px2, py2), 3)
                    # Центральный символ
                    pygame.draw.circle(book_surface, (255, 120, 40), (cx, cy), 4)
                    # Красные частицы ярости
                    for i in range(6):
                        angle = i * (math.pi / 3)
                        px = cx + int(12 * math.cos(angle))
                        py = cy + int(12 * math.sin(angle))
                        pygame.draw.circle(book_surface, (255, 120, 60, 180), (px, py), 2)
                # --- Подсветка при наведении ---
                if pygame.Rect(book_x+sx, book_y+sy, spell_size, spell_size).collidepoint(mouse):
                    pygame.draw.rect(book_surface, (255,255,120), icon_rect, 4)
                    # Типтул с описанием заклинания (улучшенная версия)
                    font_title = pygame.font.Font(None, 22)
                    font_desc = pygame.font.Font(None, 18)
                    font_params = pygame.font.Font(None, 18)
                    # --- Динамические значения для тултипа ---
                    hero = self.selected_unit if isinstance(self.selected_unit, Hero) else None
                    spell_power = getattr(hero, 'spell_power', 0) if hero else 0
                    
                    # Формируем тултип: название, описание, параметры
                    tip_lines = []
                    # 1. Название (жирный заголовок)
                    tip_lines.append(('title', spell.name))
                    # 2. Описание заклинания
                    if spell.description:
                        tip_lines.append(('desc', spell.description))
                    # 3. Пустая строка для разделения
                    tip_lines.append(('separator', ''))
                    # 4. Параметры
                    # Мана
                    tip_lines.append(('param', f"Мана: {spell.mana_cost}"))
                    # Урон (если есть)
                    if hasattr(spell, 'damage') and spell.damage > 0:
                        base_dmg = spell.damage
                        bonus = spell_power * 5
                        final_dmg = base_dmg + bonus
                        if bonus > 0:
                            tip_lines.append(('param', f"Урон: {base_dmg} (+{bonus}) = {final_dmg}"))
                        else:
                            tip_lines.append(('param', f"Урон: {base_dmg}"))
                    # Лечение (если есть - для Воскрешения и Поднятия мёртвых)
                    if hasattr(spell, 'heal_amount') and spell.heal_amount > 0:
                        base_heal = spell.heal_amount
                        if hasattr(spell, 'spell_power_multiplier'):
                            bonus_heal = spell_power * spell.spell_power_multiplier
                        elif spell.icon == 'resurrection':
                            # Для Воскрешения множитель = 10
                            bonus_heal = spell_power * 10
                        else:
                            bonus_heal = 0
                        final_heal = base_heal + bonus_heal
                        if bonus_heal > 0:
                            tip_lines.append(('param', f"Лечение: {base_heal} (+{bonus_heal}) = {final_heal}"))
                        else:
                            tip_lines.append(('param', f"Лечение: {base_heal}"))
                    # Длительность (если есть)
                    if hasattr(spell, 'duration') and spell.duration > 0:
                        base_dur = spell.duration
                        bonus_dur = spell_power
                        final_dur = base_dur + bonus_dur
                        if bonus_dur > 0:
                            tip_lines.append(('param', f"Длительность: {base_dur} (+{bonus_dur}) = {final_dur} ход"))
                        else:
                            tip_lines.append(('param', f"Длительность: {base_dur} ход"))
                    
                    # Ограничиваем ширину тултипа и оборачиваем текст
                    max_tip_width = 250
                    wrapped_lines = []
                    for line_type, line_text in tip_lines:
                        if line_type == 'separator':
                            wrapped_lines.append((line_type, ''))
                            continue
                        
                        # Выбираем шрифт в зависимости от типа строки
                        if line_type == 'title':
                            current_font = font_title
                        elif line_type == 'desc':
                            current_font = font_desc
                        else:
                            current_font = font_params
                        
                        line_width = current_font.size(line_text)[0]
                        if line_width > max_tip_width - 20:
                            # Разбиваем длинную строку
                            words = line_text.split()
                            current_line = ""
                            for word in words:
                                test_line = current_line + (" " if current_line else "") + word
                                if current_font.size(test_line)[0] <= max_tip_width - 20:
                                    current_line = test_line
                                else:
                                    if current_line:
                                        wrapped_lines.append((line_type, current_line))
                                    current_line = word
                            if current_line:
                                wrapped_lines.append((line_type, current_line))
                        else:
                            wrapped_lines.append((line_type, line_text))
                    
                    # Создаем красивый тултип
                    tip_w = max_tip_width
                    y_offset = 10
                    line_heights = []
                    for line_type, _ in wrapped_lines:
                        if line_type == 'title':
                            line_heights.append(24)
                        elif line_type == 'separator':
                            line_heights.append(8)
                        elif line_type == 'desc':
                            line_heights.append(20)
                        else:
                            line_heights.append(20)
                    tip_h = sum(line_heights) + 20
                    
                    tiptul = pygame.Surface((tip_w, tip_h), pygame.SRCALPHA)
                    # Градиентный фон тултипа
                    for y in range(tip_h):
                        alpha = 240 - int(20 * (y / tip_h))
                        pygame.draw.line(tiptul, (20, 20, 40, alpha), (0, y), (tip_w, y))
                    # Рамка
                    pygame.draw.rect(tiptul, (100, 100, 150), (0, 0, tip_w, tip_h), 2, border_radius=8)
                    
                    # Отрисовка текста
                    current_y = 10
                    for (line_type, line_text), line_h in zip(wrapped_lines, line_heights):
                        if line_type == 'separator':
                            current_y += line_h
                            continue
                        elif line_type == 'title':
                            text_surf = font_title.render(line_text, True, (255, 240, 180))
                            tiptul.blit(text_surf, (10, current_y))
                        elif line_type == 'desc':
                            text_surf = font_desc.render(line_text, True, (220, 220, 240))
                            tiptul.blit(text_surf, (10, current_y))
                        else:  # param
                            text_surf = font_params.render(line_text, True, (180, 200, 255))
                            tiptul.blit(text_surf, (10, current_y))
                        current_y += line_h
                    
                    # Позиционирование с учетом границ экрана
                    tx = book_x + sx + spell_size + 10
                    ty = book_y + sy
                    # Проверка выхода за правую границу
                    if tx + tip_w > SCREEN_WIDTH - 10:
                        tx = book_x + sx - tip_w - 10
                    # Проверка выхода за нижнюю границу
                    if ty + tip_h > SCREEN_HEIGHT - 10:
                        ty = SCREEN_HEIGHT - tip_h - 10
                    # Проверка выхода за верхнюю границу
                    if ty < 10:
                        ty = 10
                    tiptul_rect = (tx, ty)
            # Сначала книга, затем типтул поверх
            # Рисуем книгу с анимацией перелистывания
            if flip_anim:
                progress = flip_anim['progress']
                # Эффект сдвига страницы
                if 0.1 <= progress <= 0.9:
                    offset = int((progress - 0.5) * 20 * flip_anim['direction'])
                    self.screen.blit(book_surface, (book_x + offset, book_y))
                else:
                    self.screen.blit(book_surface, (book_x, book_y))
            else:
                self.screen.blit(book_surface, (book_x, book_y))
            if tiptul and tiptul_rect:
                if not isinstance(tiptul_rect, pygame.Rect):
                    tiptul_rect = pygame.Rect(tiptul_rect[0], tiptul_rect[1], tiptul.get_width(), tiptul.get_height())
                s = pygame.Surface((tiptul_rect.width, tiptul_rect.height), pygame.SRCALPHA)
                s.fill((40,40,80,255))
                s.blit(tiptul, (0,0))
                self.screen.blit(s, tiptul_rect)
        # Кнопка истории (только если не режим наблюдения)
        if not self.spectator_mode:
            pygame.draw.rect(self.screen, (80, 120, 200), self.history_button_rect, border_radius=8)
            font_hist = pygame.font.Font(None, 32)
            self.screen.blit(font_hist.render('H', True, (255,255,255)), (self.history_button_rect.x+14, self.history_button_rect.y+8))
        # Если открыта панель истории (только если не режим наблюдения)
        if self.history_panel_open and not self.spectator_mode:
            self.draw_history_panel()
        # Лента: кто ходит сейчас
        label = None
        if hasattr(self, 'turn_queue'):
            active = None
            if self.turn_queue:
                # Пропускаем разделитель раунда
                active = next((u for u in self.turn_queue if u is not self._round_delimiter), None)
                if active:
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
        
        # Индикатор паузы
        if self.is_paused:
            pause_font = pygame.font.Font(None, 48)
            pause_text = pause_font.render("ПАУЗА", True, (255, 100, 100))
            pause_bg = pygame.Surface((pause_text.get_width() + 20, pause_text.get_height() + 10), pygame.SRCALPHA)
            pause_bg.fill((0, 0, 0, 200))
            self.screen.blit(pause_bg, (SCREEN_WIDTH//2 - pause_bg.get_width()//2, 60))
            self.screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, 65))
        
        # Тултип юнита (при зажатии правой кнопки)
        if self.unit_tooltip_show and self.unit_tooltip_unit:
            self.draw_unit_tooltip(self.unit_tooltip_unit)
        
        # Окно информации о юните (при двойном клике)
        if self.unit_info_window_open and self.unit_info_window_unit:
            self.draw_unit_info_window(self.unit_info_window_unit)
        
        # Меню внутри игры (деревянное средневековое в стиле главного меню)
        if self.menu_open:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((30, 20, 10, 200))
            self.screen.blit(overlay, (0,0))
            # Панель меню
            menu_w, menu_h = 380, 400
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
            # Кнопка "Настройки"
            settings_rect = pygame.Rect(btn_x, btn_y + btn_h + btn_gap, btn_w, btn_h)
            self.pause_settings_button_rect = settings_rect
            for y_offset in range(btn_h):
                btn_gradient = (
                    int(140 - y_offset * 0.25),
                    int(120 - y_offset * 0.2),
                    int(100 - y_offset * 0.15)
                )
                pygame.draw.line(self.screen, btn_gradient,
                               (btn_x, settings_rect.y + y_offset),
                               (btn_x + btn_w, settings_rect.y + y_offset))
            pygame.draw.rect(self.screen, (70, 50, 35), settings_rect, 5, border_radius=14)
            inner_settings = pygame.Rect(btn_x + 3, settings_rect.y + 3, btn_w - 6, btn_h - 6)
            pygame.draw.rect(self.screen, (180, 150, 120), inner_settings, 2, border_radius=12)
            set_text = font.render('Настройки', True, (255, 245, 220))
            set_shadow = font.render('Настройки', True, (60, 50, 40))
            self.screen.blit(set_shadow, (btn_x + (btn_w - set_shadow.get_width())//2 + 2, settings_rect.y + 18))
            self.screen.blit(set_text, (btn_x + (btn_w - set_text.get_width())//2, settings_rect.y + 16))
            # Кнопка "Главное меню"
            mainmenu_rect = pygame.Rect(btn_x, settings_rect.y + btn_h + btn_gap, btn_w, btn_h)
            self.mainmenu_button_rect = mainmenu_rect
            # Градиент
            for y_offset in range(btn_h):
                btn_gradient = (
                    int(160 - y_offset * 0.3),
                    int(120 - y_offset * 0.25),
                    int(90 - y_offset * 0.2)
                )
                pygame.draw.line(self.screen, btn_gradient,
                               (btn_x, mainmenu_rect.y + y_offset),
                               (btn_x + btn_w, mainmenu_rect.y + y_offset))
            pygame.draw.rect(self.screen, (70, 50, 35), mainmenu_rect, 5, border_radius=14)
            inner_mainmenu = pygame.Rect(btn_x + 3, mainmenu_rect.y + 3, btn_w - 6, btn_h - 6)
            pygame.draw.rect(self.screen, (180, 150, 120), inner_mainmenu, 2, border_radius=12)
            # Узор
            for i in range(4):
                x_pos = btn_x + 30 + i * 50
                pygame.draw.line(self.screen, (100, 80, 60), (x_pos, mainmenu_rect.y + 10), (x_pos, mainmenu_rect.y + btn_h - 10), 2)
                for j in range(2):
                    knot_y = mainmenu_rect.y + 20 + j * 20
                    pygame.draw.circle(self.screen, (90, 70, 50), (x_pos, knot_y), 3)
            # Заклёпки
            for corner_x, corner_y in [(btn_x + 8, mainmenu_rect.y + 8), (btn_x + btn_w - 8, mainmenu_rect.y + 8),
                                       (btn_x + 8, mainmenu_rect.y + btn_h - 8), (btn_x + btn_w - 8, mainmenu_rect.y + btn_h - 8)]:
                pygame.draw.circle(self.screen, (180, 170, 160), (corner_x, corner_y), 5)
                pygame.draw.circle(self.screen, (220, 210, 200), (corner_x, corner_y), 3)
            mainmenu_text = font.render('Главное меню', True, (255, 245, 220))
            mainmenu_shadow = font.render('Главное меню', True, (60, 50, 40))
            self.screen.blit(mainmenu_shadow, (btn_x + (btn_w - mainmenu_shadow.get_width())//2 + 2, mainmenu_rect.y + 18))
            self.screen.blit(mainmenu_text, (btn_x + (btn_w - mainmenu_text.get_width())//2, mainmenu_rect.y + 16))
            # Кнопка "Выйти"
            exit_btn_w, exit_btn_h = 200, 55
            exit_btn_x = btn_x + (btn_w - exit_btn_w) // 2
            exit_rect = pygame.Rect(exit_btn_x, mainmenu_rect.y + btn_h + btn_gap, exit_btn_w, exit_btn_h)
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

        # Кнопка "Режим разработчика"
        dev_btn_y = exit_btn_y + exit_btn_h + btn_gap
        dev_btn_w, dev_btn_h = 220, 55
        dev_btn_x = btn_panel_x + (btn_w - dev_btn_w) // 2
        self.dev_button_rect = pygame.Rect(dev_btn_x, dev_btn_y, dev_btn_w, dev_btn_h)
        for y_offset in range(dev_btn_h):
            grad = (int(120 - y_offset * 0.25), int(140 - y_offset * 0.2), int(160 - y_offset * 0.15))
            pygame.draw.line(self.screen, grad, (dev_btn_x, dev_btn_y + y_offset), (dev_btn_x + dev_btn_w, dev_btn_y + y_offset))
        pygame.draw.rect(self.screen, (50, 50, 70), self.dev_button_rect, 5, border_radius=12)
        inner_dev = pygame.Rect(dev_btn_x + 3, dev_btn_y + 3, dev_btn_w - 6, dev_btn_h - 6)
        pygame.draw.rect(self.screen, (180, 180, 220), inner_dev, 2, border_radius=10)
        dev_text = self.font.render('РЕЖИМ РАЗРАБОТЧИКА', True, (240, 240, 255))
        dev_shadow = self.font.render('РЕЖИМ РАЗРАБОТЧИКА', True, (40, 40, 60))
        self.screen.blit(dev_shadow, (dev_btn_x + (dev_btn_w - dev_shadow.get_width())//2 + 2, dev_btn_y + 15 + 2))
        self.screen.blit(dev_text, (dev_btn_x + (dev_btn_w - dev_text.get_width())//2, dev_btn_y + 15))

        # Кнопка "Настройки"
        settings_btn_y = dev_btn_y + dev_btn_h + btn_gap
        settings_btn_w, settings_btn_h = 220, 55
        settings_btn_x = btn_panel_x + (btn_w - settings_btn_w) // 2
        self.settings_button_rect = pygame.Rect(settings_btn_x, settings_btn_y, settings_btn_w, settings_btn_h)
        for y_offset in range(settings_btn_h):
            grad = (int(140 - y_offset * 0.25), int(120 - y_offset * 0.2), int(100 - y_offset * 0.15))
            pygame.draw.line(self.screen, grad, (settings_btn_x, settings_btn_y + y_offset), (settings_btn_x + settings_btn_w, settings_btn_y + y_offset))
        pygame.draw.rect(self.screen, (70, 50, 35), self.settings_button_rect, 5, border_radius=12)
        inner_set = pygame.Rect(settings_btn_x + 3, settings_btn_y + 3, settings_btn_w - 6, settings_btn_h - 6)
        pygame.draw.rect(self.screen, (200, 180, 160), inner_set, 2, border_radius=10)
        set_text = self.font.render('НАСТРОЙКИ', True, (255, 245, 220))
        set_shadow = self.font.render('НАСТРОЙКИ', True, (60, 50, 40))
        self.screen.blit(set_shadow, (settings_btn_x + (settings_btn_w - set_shadow.get_width())//2 + 2, settings_btn_y + 15 + 2))
        self.screen.blit(set_text, (settings_btn_x + (settings_btn_w - set_text.get_width())//2, settings_btn_y + 15))

    def draw_battle_setup(self):
        """Панель настройки боя с выбором рас и типа игрока."""
        self.screen.fill((30, 30, 60))
        
        # Заголовок
        title = self.font.render("Настройка боя", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        # Список рас
        races = [
            ('human', 'Люди', (200, 220, 255)),
            ('elf', 'Эльфы', (180, 255, 200)),
            ('undead', 'Нежить', (220, 200, 255)),
            ('demon', 'Демоны', (255, 200, 200)),
            ('dwarf', 'Гномы', (220, 220, 180)),
            ('shadow', 'Тени', (200, 200, 220)),
        ]
        self.sorted_races = races

        # Размеры и позиции
        hero_panel_w, hero_panel_h = 300, 400  # Уменьшена высота панелей
        hero_panel_x1 = 100  # Игрок 1 слева
        hero_panel_x2 = SCREEN_WIDTH - hero_panel_w - 100  # Игрок 2 справа
        hero_panel_y = 80  # Немного выше
        
        # Отступы для элементов
        icon_size = 70  # Немного меньше иконка
        btn_w, btn_h = 180, 40
        race_btn_w, race_btn_h = 80, 32  # Немного меньше кнопки рас
        gap = 12  # Уменьшен отступ
        
        # === ИГРОК 1 ===
        p1_bg = pygame.Rect(hero_panel_x1, hero_panel_y, hero_panel_w, hero_panel_h)
        pygame.draw.rect(self.screen, (50, 50, 80), p1_bg, border_radius=12)
        pygame.draw.rect(self.screen, (120, 140, 180), p1_bg, 3, border_radius=12)
        
        # Заголовок игрока 1
        p1_title = pygame.font.Font(None, 32).render("Игрок 1", True, (255, 255, 255))
        self.screen.blit(p1_title, (hero_panel_x1 + hero_panel_w//2 - p1_title.get_width()//2, hero_panel_y + 15))
        
        # Переключатель Человек/Бот для игрока 1
        toggle_y1 = hero_panel_y + 55
        toggle_label = pygame.font.Font(None, 24).render("Тип:", True, (200, 200, 200))
        self.screen.blit(toggle_label, (hero_panel_x1 + 20, toggle_y1))
        
        human_btn_p1 = pygame.Rect(hero_panel_x1 + 80, toggle_y1, btn_w//2 - 5, btn_h)
        ai_btn_p1 = pygame.Rect(hero_panel_x1 + hero_panel_w - btn_w//2 - 20, toggle_y1, btn_w//2 - 5, btn_h)
        
        # Кнопка Человек
        human_color = (100, 180, 100) if self.player1_type == 'human' else (60, 60, 80)
        pygame.draw.rect(self.screen, human_color, human_btn_p1, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), human_btn_p1, 2, border_radius=8)
        human_text = pygame.font.Font(None, 22).render("Человек", True, (255, 255, 255))
        self.screen.blit(human_text, (human_btn_p1.x + human_btn_p1.w//2 - human_text.get_width()//2,
                                      human_btn_p1.y + human_btn_p1.h//2 - human_text.get_height()//2))
        
        # Кнопка Бот
        ai_color = (180, 100, 100) if self.player1_type == 'ai' else (60, 60, 80)
        pygame.draw.rect(self.screen, ai_color, ai_btn_p1, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), ai_btn_p1, 2, border_radius=8)
        ai_text = pygame.font.Font(None, 22).render("Бот", True, (255, 255, 255))
        self.screen.blit(ai_text, (ai_btn_p1.x + ai_btn_p1.w//2 - ai_text.get_width()//2,
                                   ai_btn_p1.y + ai_btn_p1.h//2 - ai_text.get_height()//2))
        
        self.player1_toggle_human_rect = human_btn_p1
        self.player1_toggle_ai_rect = ai_btn_p1
        
        # Иконка героя игрока 1
        icon_y = toggle_y1 + btn_h + gap
        icon_x = hero_panel_x1 + hero_panel_w//2 - icon_size//2
        
        # Рисуем иконку героя выбранной расы и класса
        if self.player1_race:
            try:
                # Используем класс героя если выбран, иначе дефолтный
                hero_class = self.player1_hero_class if self.player1_hero_class else None
                if hero_class:
                    hero_icon = load_image(f'hero_{self.player1_race}_{hero_class}')
                else:
                    hero_icon = load_image(f"hero_{self.player1_race}")
                hero_icon = pygame.transform.scale(hero_icon, (icon_size, icon_size))
                self.screen.blit(hero_icon, (icon_x, icon_y))
            except:
                pygame.draw.rect(self.screen, (100, 100, 100), 
                               (icon_x, icon_y, icon_size, icon_size), 3)
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), 
                           (icon_x, icon_y, icon_size, icon_size), 3)
            question = pygame.font.Font(None, 48).render("?", True, (150, 150, 150))
            self.screen.blit(question, (icon_x + icon_size//2 - question.get_width()//2,
                                       icon_y + icon_size//2 - question.get_height()//2))
        
        # Выбор расы для игрока 1
        race_start_y = icon_y + icon_size + gap + 10
        race_label = pygame.font.Font(None, 22).render("Выберите расу:", True, (200, 200, 200))
        self.screen.blit(race_label, (hero_panel_x1 + 20, race_start_y))
        
        race_btn_gap = 8
        race_start_x = hero_panel_x1 + (hero_panel_w - (race_btn_w*3 + race_btn_gap*2))//2
        race_start_y += 30
        
        p1_race_rects = []
        for idx, (key, label, color) in enumerate(races):
            row = idx // 3
            col = idx % 3
            x = race_start_x + col * (race_btn_w + race_btn_gap)
            y = race_start_y + row * (race_btn_h + race_btn_gap)
            rect = pygame.Rect(x, y, race_btn_w, race_btn_h)
            
            selected = (self.player1_race == key)
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            
            bg_color = color if selected else tuple(max(40, c - 80) for c in color)
            if hovered and not selected:
                bg_color = tuple(min(255, c + 30) for c in bg_color)
            
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=6)
            border_color = (255, 255, 255) if selected else ((200, 200, 200) if hovered else (100, 100, 100))
            border_width = 3 if selected else 2
            pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=6)
            
            short_label = label[:4] if len(label) <= 4 else label[:3]
            text = pygame.font.Font(None, 18).render(short_label, True, (255, 255, 255))
            self.screen.blit(text, (rect.x + race_btn_w//2 - text.get_width()//2,
                                   rect.y + race_btn_h//2 - text.get_height()//2))
            p1_race_rects.append((rect, key))
        
        self.player1_race_rects = p1_race_rects
        
        # Выпадающий список выбора класса героя для игрока 1 (справа от иконки, ниже кнопки бот/человек)
        if self.player1_race:
            dropdown_x = icon_x + icon_size + 10  # Справа от иконки
            dropdown_y = toggle_y1 + btn_h + 10  # Ниже кнопки бот/человек
            dropdown_w = 110
            dropdown_h = 28
            
            class_options = [('warrior', 'Воин'), ('archer', 'Лучник'), ('mage', 'Маг')]
            class_names = {'warrior': 'Воин', 'archer': 'Лучник', 'mage': 'Маг'}
            
            # Основная кнопка выпадающего списка
            current_class = self.player1_hero_class if self.player1_hero_class else 'warrior'
            current_class_name = class_names.get(current_class, current_class)
            
            dropdown_rect = pygame.Rect(dropdown_x, dropdown_y, dropdown_w, dropdown_h)
            hovered = dropdown_rect.collidepoint(pygame.mouse.get_pos())
            
            bg_color = (70, 90, 110) if hovered else (60, 70, 90)
            pygame.draw.rect(self.screen, bg_color, dropdown_rect, border_radius=5)
            pygame.draw.rect(self.screen, (180, 180, 200), dropdown_rect, 2, border_radius=5)
            
            # Текст кнопки
            class_text = pygame.font.Font(None, 20).render(current_class_name, True, (255, 255, 255))
            self.screen.blit(class_text, (dropdown_rect.x + 5, dropdown_rect.y + 7))
            
            # Стрелка вниз
            arrow_points = [
                (dropdown_rect.right - 15, dropdown_rect.centery - 3),
                (dropdown_rect.right - 10, dropdown_rect.centery + 3),
                (dropdown_rect.right - 5, dropdown_rect.centery - 3)
            ]
            pygame.draw.polygon(self.screen, (200, 200, 200), arrow_points)
            
            self.player1_class_dropdown_rect = dropdown_rect
            
            # Выпадающий список (если открыт)
            if getattr(self, 'player1_class_dropdown_open', False):
                self.player1_class_rects = []
                for idx, (class_key, class_label_text) in enumerate(class_options):
                    opt_rect = pygame.Rect(dropdown_x, dropdown_y + dropdown_h + idx * dropdown_h, dropdown_w, dropdown_h)
                    opt_hovered = opt_rect.collidepoint(pygame.mouse.get_pos())
                    
                    opt_bg = (80, 100, 120) if opt_hovered else (50, 60, 80)
                    pygame.draw.rect(self.screen, opt_bg, opt_rect)
                    pygame.draw.rect(self.screen, (150, 150, 170), opt_rect, 1)
                    
                    opt_text = pygame.font.Font(None, 20).render(class_label_text, True, (255, 255, 255))
                    self.screen.blit(opt_text, (opt_rect.x + 5, opt_rect.y + 7))
                    
                    self.player1_class_rects.append((opt_rect, class_key))
            else:
                self.player1_class_rects = []
        else:
            self.player1_class_dropdown_rect = None
            self.player1_class_rects = []
        
        # === ИГРОК 2 ===
        p2_bg = pygame.Rect(hero_panel_x2, hero_panel_y, hero_panel_w, hero_panel_h)
        pygame.draw.rect(self.screen, (50, 50, 80), p2_bg, border_radius=12)
        pygame.draw.rect(self.screen, (120, 140, 180), p2_bg, 3, border_radius=12)
        
        # Заголовок игрока 2
        p2_title = pygame.font.Font(None, 32).render("Игрок 2", True, (255, 255, 255))
        self.screen.blit(p2_title, (hero_panel_x2 + hero_panel_w//2 - p2_title.get_width()//2, hero_panel_y + 15))
        
        # Переключатель Человек/Бот для игрока 2
        toggle_y2 = hero_panel_y + 55
        toggle_label2 = pygame.font.Font(None, 24).render("Тип:", True, (200, 200, 200))
        self.screen.blit(toggle_label2, (hero_panel_x2 + 20, toggle_y2))
        
        human_btn_p2 = pygame.Rect(hero_panel_x2 + 80, toggle_y2, btn_w//2 - 5, btn_h)
        ai_btn_p2 = pygame.Rect(hero_panel_x2 + hero_panel_w - btn_w//2 - 20, toggle_y2, btn_w//2 - 5, btn_h)
        
        # Кнопка Человек
        human_color2 = (100, 180, 100) if self.player2_type == 'human' else (60, 60, 80)
        pygame.draw.rect(self.screen, human_color2, human_btn_p2, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), human_btn_p2, 2, border_radius=8)
        human_text2 = pygame.font.Font(None, 22).render("Человек", True, (255, 255, 255))
        self.screen.blit(human_text2, (human_btn_p2.x + human_btn_p2.w//2 - human_text2.get_width()//2,
                                       human_btn_p2.y + human_btn_p2.h//2 - human_text2.get_height()//2))
        
        # Кнопка Бот
        ai_color2 = (180, 100, 100) if self.player2_type == 'ai' else (60, 60, 80)
        pygame.draw.rect(self.screen, ai_color2, ai_btn_p2, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), ai_btn_p2, 2, border_radius=8)
        ai_text2 = pygame.font.Font(None, 22).render("Бот", True, (255, 255, 255))
        self.screen.blit(ai_text2, (ai_btn_p2.x + ai_btn_p2.w//2 - ai_text2.get_width()//2,
                                    ai_btn_p2.y + ai_btn_p2.h//2 - ai_text2.get_height()//2))
        
        self.player2_toggle_human_rect = human_btn_p2
        self.player2_toggle_ai_rect = ai_btn_p2
        
        # Иконка героя игрока 2
        icon_y2 = toggle_y2 + btn_h + gap
        icon_x2 = hero_panel_x2 + hero_panel_w//2 - icon_size//2
        
        if self.player2_race:
            try:
                # Используем класс героя если выбран, иначе дефолтный
                hero_class2 = self.player2_hero_class if self.player2_hero_class else None
                if hero_class2:
                    hero_icon2 = load_image(f'hero_{self.player2_race}_{hero_class2}')
                else:
                    hero_icon2 = load_image(f"hero_{self.player2_race}")
                hero_icon2 = pygame.transform.scale(hero_icon2, (icon_size, icon_size))
                self.screen.blit(hero_icon2, (icon_x2, icon_y2))
            except:
                pygame.draw.rect(self.screen, (100, 100, 100), 
                               (icon_x2, icon_y2, icon_size, icon_size), 3)
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), 
                           (icon_x2, icon_y2, icon_size, icon_size), 3)
            question2 = pygame.font.Font(None, 48).render("?", True, (150, 150, 150))
            self.screen.blit(question2, (icon_x2 + icon_size//2 - question2.get_width()//2,
                                        icon_y2 + icon_size//2 - question2.get_height()//2))
        
        # Выбор расы для игрока 2
        race_start_y2 = icon_y2 + icon_size + gap + 10
        race_label2 = pygame.font.Font(None, 22).render("Выберите расу:", True, (200, 200, 200))
        self.screen.blit(race_label2, (hero_panel_x2 + 20, race_start_y2))
        
        race_start_y2 += 30
        # Вычисляем правильную стартовую позицию для игрока 2
        race_start_x2 = hero_panel_x2 + (hero_panel_w - (race_btn_w*3 + race_btn_gap*2))//2
        
        p2_race_rects = []
        for idx, (key, label, color) in enumerate(races):
            row = idx // 3
            col = idx % 3
            x = race_start_x2 + col * (race_btn_w + race_btn_gap)
            y = race_start_y2 + row * (race_btn_h + race_btn_gap)
            rect = pygame.Rect(x, y, race_btn_w, race_btn_h)
            
            selected = (self.player2_race == key)
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            
            bg_color = color if selected else tuple(max(40, c - 80) for c in color)
            if hovered and not selected:
                bg_color = tuple(min(255, c + 30) for c in bg_color)
            
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=6)
            border_color = (255, 255, 255) if selected else ((200, 200, 200) if hovered else (100, 100, 100))
            border_width = 3 if selected else 2
            pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=6)
            
            short_label = label[:4] if len(label) <= 4 else label[:3]
            text = pygame.font.Font(None, 18).render(short_label, True, (255, 255, 255))
            self.screen.blit(text, (rect.x + race_btn_w//2 - text.get_width()//2,
                                   rect.y + race_btn_h//2 - text.get_height()//2))
            p2_race_rects.append((rect, key))
        
        self.player2_race_rects = p2_race_rects
        
        # Выпадающий список выбора класса героя для игрока 2 (справа от иконки, ниже кнопки бот/человек)
        if self.player2_race:
            dropdown_x2 = icon_x2 + icon_size + 10  # Справа от иконки
            dropdown_y2 = toggle_y2 + btn_h + 10  # Ниже кнопки бот/человек
            dropdown_w2 = 110
            dropdown_h2 = 28
            
            class_options = [('warrior', 'Воин'), ('archer', 'Лучник'), ('mage', 'Маг')]
            class_names = {'warrior': 'Воин', 'archer': 'Лучник', 'mage': 'Маг'}
            
            # Основная кнопка выпадающего списка
            current_class2 = self.player2_hero_class if self.player2_hero_class else 'warrior'
            current_class_name2 = class_names.get(current_class2, current_class2)
            
            dropdown_rect2 = pygame.Rect(dropdown_x2, dropdown_y2, dropdown_w2, dropdown_h2)
            hovered2 = dropdown_rect2.collidepoint(pygame.mouse.get_pos())
            
            bg_color2 = (70, 90, 110) if hovered2 else (60, 70, 90)
            pygame.draw.rect(self.screen, bg_color2, dropdown_rect2, border_radius=5)
            pygame.draw.rect(self.screen, (180, 180, 200), dropdown_rect2, 2, border_radius=5)
            
            # Текст кнопки
            class_text2 = pygame.font.Font(None, 20).render(current_class_name2, True, (255, 255, 255))
            self.screen.blit(class_text2, (dropdown_rect2.x + 5, dropdown_rect2.y + 7))
            
            # Стрелка вниз
            arrow_points2 = [
                (dropdown_rect2.right - 15, dropdown_rect2.centery - 3),
                (dropdown_rect2.right - 10, dropdown_rect2.centery + 3),
                (dropdown_rect2.right - 5, dropdown_rect2.centery - 3)
            ]
            pygame.draw.polygon(self.screen, (200, 200, 200), arrow_points2)
            
            self.player2_class_dropdown_rect = dropdown_rect2
            
            # Выпадающий список (если открыт)
            if getattr(self, 'player2_class_dropdown_open', False):
                self.player2_class_rects = []
                for idx, (class_key, class_label_text) in enumerate(class_options):
                    opt_rect2 = pygame.Rect(dropdown_x2, dropdown_y2 + dropdown_h2 + idx * dropdown_h2, dropdown_w2, dropdown_h2)
                    opt_hovered2 = opt_rect2.collidepoint(pygame.mouse.get_pos())
                    
                    opt_bg2 = (80, 100, 120) if opt_hovered2 else (50, 60, 80)
                    pygame.draw.rect(self.screen, opt_bg2, opt_rect2)
                    pygame.draw.rect(self.screen, (150, 150, 170), opt_rect2, 1)
                    
                    opt_text2 = pygame.font.Font(None, 20).render(class_label_text, True, (255, 255, 255))
                    self.screen.blit(opt_text2, (opt_rect2.x + 5, opt_rect2.y + 7))
                    
                    self.player2_class_rects.append((opt_rect2, class_key))
            else:
                self.player2_class_rects = []
        else:
            self.player2_class_dropdown_rect = None
            self.player2_class_rects = []
        
        # Кнопка "Начать бой"
        start_btn_w, start_btn_h = 200, 50
        start_btn_x = SCREEN_WIDTH//2 - start_btn_w//2
        start_btn_y = hero_panel_y + hero_panel_h + 20  # Уменьшен отступ
        
        start_btn = pygame.Rect(start_btn_x, start_btn_y, start_btn_w, start_btn_h)
        can_start = (self.player1_race is not None and self.player2_race is not None and 
                     self.player1_race != self.player2_race)
        
        start_color = (100, 180, 100) if can_start else (60, 60, 80)
        pygame.draw.rect(self.screen, start_color, start_btn, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), start_btn, 3 if can_start else 2, border_radius=10)
        
        start_text = pygame.font.Font(None, 28).render("Начать бой", True, (255, 255, 255))
        self.screen.blit(start_text, (start_btn.x + start_btn.w//2 - start_text.get_width()//2,
                                     start_btn.y + start_btn.h//2 - start_text.get_height()//2))
        self.start_battle_btn_rect = start_btn
        
        # Курсор-рука над кнопками
        mouse_pos = pygame.mouse.get_pos()
        over_button = (start_btn.collidepoint(mouse_pos)) or \
                     any(r[0].collidepoint(mouse_pos) for r in p1_race_rects + p2_race_rects) or \
                     human_btn_p1.collidepoint(mouse_pos) or ai_btn_p1.collidepoint(mouse_pos) or \
                     human_btn_p2.collidepoint(mouse_pos) or ai_btn_p2.collidepoint(mouse_pos)
        self.set_cursor(pygame.SYSTEM_CURSOR_HAND if over_button else pygame.SYSTEM_CURSOR_ARROW)

    def draw_history_panel(self):
        # Отдельная большая панель истории событий
        panel_w, panel_h = 600, 400
        panel_x = (SCREEN_WIDTH - panel_w)//2
        panel_y = (SCREEN_HEIGHT - panel_h)//2
        pygame.draw.rect(self.screen, (30,30,60), (panel_x, panel_y, panel_w, panel_h), border_radius=16)
        font = pygame.font.Font(None, 22)
        # Вычисляем сколько строк помещается (с учетом отступов)
        max_text_width = panel_w - 80  # Ширина минус отступы и место под стрелки
        line_height = 22
        lines_visible = (panel_h - 80) // line_height  # Высота минус отступы, делим на высоту строки
        offset = self.event_log_offset
        
        # Вычисляем строки с учетом переносов
        display_lines = []  # Список кортежей (idx события, список строк для отображения)
        total_lines = 0
        for idx in range(len(self.event_log) - 1 - offset, -1, -1):
            if idx < 0:
                break
            text = self.event_log[idx]
            display_text = text.replace('===','').strip() if text.startswith('===' ) else text
            # Разбиваем на строки
            wrapped_lines = []
            words = display_text.split(' ')
            current_line = ''
            for word in words:
                test_line = current_line + (' ' if current_line else '') + word
                test_surf = font.render(test_line, True, (255,255,255))
                if test_surf.get_width() <= max_text_width:
                    current_line = test_line
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = word
            if current_line:
                wrapped_lines.append(current_line)
            # Максимум 2 строки на событие
            wrapped_lines = wrapped_lines[:2]
            if total_lines + len(wrapped_lines) <= lines_visible:
                display_lines.append((idx, wrapped_lines))
                total_lines += len(wrapped_lines)
            else:
                break
        
        # Обновляем offset
        max_offset = max(0, len(self.event_log) - len(display_lines))
        offset = max(0, min(offset, max_offset))
        
        # Выводим строки
        y_offset = 0
        for idx, wrapped_lines in display_lines:
            text = self.event_log[idx]
            color = (255,220,120) if text.startswith('===') else (220,220,220)
            for line in wrapped_lines:
                if y_offset < lines_visible:
                    surf = font.render(line, True, color)
                    self.screen.blit(surf, (panel_x+30, panel_y+30 + y_offset*line_height))
                    y_offset += 1
        
        # Кнопка закрытия
        close_rect = pygame.Rect(panel_x+panel_w-40, panel_y+10, 30, 30)
        pygame.draw.rect(self.screen, (200,60,60), close_rect, border_radius=8)
        self.screen.blit(font.render('X', True, (255,255,255)), (close_rect.x+7, close_rect.y+2))
        # Стрелки прокрутки
        arrow_up = None
        arrow_down = None
        if len(self.event_log) > len(display_lines):
            arrow_up = pygame.Rect(panel_x+panel_w-40, panel_y+60, 30, 20)
            arrow_down = pygame.Rect(panel_x+panel_w-40, panel_y+panel_h-60, 30, 20)
            pygame.draw.polygon(self.screen, (200,200,120), [(arrow_up.x+15, arrow_up.y+4), (arrow_up.x+4, arrow_up.y+16), (arrow_up.x+26, arrow_up.y+16)])
            pygame.draw.polygon(self.screen, (200,200,120), [(arrow_down.x+15, arrow_down.y+16), (arrow_down.x+4, arrow_down.y+4), (arrow_down.x+26, arrow_down.y+4)])
        self.history_panel_close_rect = close_rect
        self.history_panel_arrow_up = arrow_up
        self.history_panel_arrow_down = arrow_down

    def draw_creative(self):
        # Фон и сетка
        self.screen.blit(self.background, (0, 0)) if hasattr(self, 'background') else self.screen.fill((20, 30, 40))
        self.draw_grid()
        # Отрисовать юнитов
        for unit in self.units:
            unit.draw(self.screen)
        # Правая панель выбора
        pygame.draw.rect(self.screen, (30, 30, 60), self.creative_panel_rect)
        pygame.draw.rect(self.screen, (120, 140, 180), self.creative_panel_rect, 2)
        font = pygame.font.Font(None, 26)
        self.screen.blit(font.render('Креатив режим', True, (220, 220, 240)), (self.creative_panel_rect.x + 12, 10))
        # Переключатель расы (прокручиваемая область) - слева
        races = [('human','Люди'), ('elf','Эльфы'), ('undead','Нежить'), ('demon','Демоны'), ('dwarf','Гномы'), ('shadow','Тени')]
        self.creative_race_scroll = getattr(self, 'creative_race_scroll', 0)
        race_view_top = 40
        race_view_h = 120
        # рамка окна
        pygame.draw.rect(self.screen, (28, 28, 48), (self.creative_panel_rect.x + 8, race_view_top - 4, self.creative_panel_rect.w - 16, race_view_h + 8), border_radius=8)
        visible_races = max(1, race_view_h // 34)
        start_r = min(self.creative_race_scroll, max(0, len(races) - visible_races))
        end_r = min(len(races), start_r + visible_races)
        y = race_view_top
        # Сброс прежних rect
        for key, _ in races:
            if hasattr(self, f'creative_team_rect_{key}'):
                delattr(self, f'creative_team_rect_{key}')
        for team_key, team_label in races[start_r:end_r]:
            rect = pygame.Rect(self.creative_panel_rect.x + 12, y, 90, 28)
            sel = (self.creative_selected_team == team_key)
            pygame.draw.rect(self.screen, (70, 110, 90) if sel else (60, 60, 80), rect, border_radius=6)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, 2, border_radius=6)
            self.screen.blit(pygame.font.Font(None, 22).render(team_label, True, (255,255,255)), (rect.x+8, rect.y+5))
            setattr(self, f'creative_team_rect_{team_key}', rect)
            y += 34
        # Скролл кнопки для рас
        self.creative_race_up = pygame.Rect(self.creative_panel_rect.x + 120, race_view_top - 2, 24, 20)
        self.creative_race_down = pygame.Rect(self.creative_panel_rect.x + 120, race_view_top + race_view_h - 18, 24, 20)
        # Переключатель команды (первая/вторая) - правее выбора расы
        side_x = self.creative_panel_rect.x + 150  # Правее области рас
        side_y = race_view_top
        side_label = font.render('Команда:', True, (220, 220, 240))
        self.screen.blit(side_label, (side_x, side_y))
        side_button_y = side_y + 20
        # Кнопка первой команды
        side1_rect = pygame.Rect(side_x, side_button_y, 90, 26)
        side1_sel = (self.creative_selected_side == 1)
        pygame.draw.rect(self.screen, (70, 110, 90) if side1_sel else (60, 60, 80), side1_rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 200, 200), side1_rect, 2, border_radius=6)
        self.screen.blit(pygame.font.Font(None, 22).render('Первая', True, (255,255,255)), (side1_rect.x+8, side1_rect.y+4))
        self.creative_side1_rect = side1_rect
        # Кнопка второй команды (под первой)
        side2_rect = pygame.Rect(side_x, side_button_y + 30, 90, 26)
        side2_sel = (self.creative_selected_side == 2)
        pygame.draw.rect(self.screen, (70, 110, 90) if side2_sel else (60, 60, 80), side2_rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 200, 200), side2_rect, 2, border_radius=6)
        self.screen.blit(pygame.font.Font(None, 22).render('Вторая', True, (255,255,255)), (side2_rect.x+8, side2_rect.y+4))
        self.creative_side2_rect = side2_rect
        pygame.draw.rect(self.screen, (80,80,120), self.creative_race_up, border_radius=4)
        pygame.draw.rect(self.screen, (80,80,120), self.creative_race_down, border_radius=4)
        self.screen.blit(pygame.font.Font(None, 20).render('▲', True, (255,255,255)), (self.creative_race_up.x+5, self.creative_race_up.y+1))
        self.screen.blit(pygame.font.Font(None, 20).render('▼', True, (255,255,255)), (self.creative_race_down.x+5, self.creative_race_down.y+1))
        # Список юнитов по выбранной расе (со скроллом)
        y += 6
        self.screen.blit(font.render('Юниты:', True, (220, 220, 240)), (self.creative_panel_rect.x + 12, y))
        y += 14  # опустить ниже, чтобы заголовок не перекрывался кнопками
        self.creative_unit_rects = []
        unit_pool = self.creative_units_by_race.get(self.creative_selected_team, []) + self.creative_units_common
        # Область списка и скролла
        list_top = y
        list_height = SCREEN_HEIGHT - 340  # Уменьшена высота, чтобы нижняя часть скрывалась скроллом
        pygame.draw.rect(self.screen, (35, 35, 60), (self.creative_panel_rect.x + 8, list_top, self.creative_panel_rect.w - 16, list_height), border_radius=8)
        # Индекс прокрутки
        self.creative_units_scroll = getattr(self, 'creative_units_scroll', 0)
        visible_count = max(1, (list_height - 16) // 30)
        start_idx = min(self.creative_units_scroll, max(0, len(unit_pool) - visible_count))
        end_idx = min(len(unit_pool), start_idx + visible_count)
        draw_y = list_top + 8
        # Убираем выпадающий список - теперь три отдельных героя в списке
        self.creative_hero_class_option_rects = []
        self.creative_hero_dropdown_rect = None
        # Проверяем, что выбранный юнит существует в списке
        unit_names = [name for name, _ in unit_pool]
        if self.creative_selected_unit not in unit_names:
            # Если выбранный юнит не найден (например, при смене расы), выбираем первого героя или первый юнит
            if unit_pool:
                # Ищем героя в списке, иначе берем первый элемент
                hero_unit = next((name for name, _ in unit_pool if name.startswith('Hero_')), None)
                self.creative_selected_unit = hero_unit if hero_unit else unit_pool[0][0]
            else:
                # Формируем имя героя по формату Hero_race_warrior
                self.creative_selected_unit = f'Hero_{self.creative_selected_team}_warrior'
        for name, _cls in unit_pool[start_idx:end_idx]:
            rect = pygame.Rect(self.creative_panel_rect.x + 12, draw_y, 180, 24)
            sel = (self.creative_selected_unit == name)
            pygame.draw.rect(self.screen, (100, 120, 160) if sel else (50, 60, 80), rect, border_radius=6)
            pygame.draw.rect(self.screen, (180, 180, 200), rect, 2, border_radius=6)
            # Для героев показываем класс и расу
            display_name = name
            if name.startswith('Hero_'):
                parts = name.split('_')
                # Формат: Hero_race_class (например, Hero_human_warrior) или Hero_class (например, Hero_warrior)
                if len(parts) >= 3:  # Hero_race_class
                    hero_race = parts[1]
                    hero_class = parts[2]
                    class_names = {'warrior': 'Воин', 'archer': 'Лучник', 'mage': 'Маг'}
                    class_name = class_names.get(hero_class, hero_class)
                    from .units import TEAM_LABELS
                    race_label = TEAM_LABELS.get(hero_race, hero_race)
                    display_name = f"{class_name} ({race_label})"
                elif len(parts) == 2:  # Hero_class
                    hero_class = parts[1]
                    class_names = {'warrior': 'Воин', 'archer': 'Лучник', 'mage': 'Маг'}
                    class_name = class_names.get(hero_class, hero_class)
                    from .units import TEAM_LABELS
                    display_name = f"{class_name} ({TEAM_LABELS.get(self.creative_selected_team, self.creative_selected_team)})"
            self.screen.blit(pygame.font.Font(None, 20).render(display_name, True, (240,240,255)), (rect.x+6, rect.y+3))
            self.creative_unit_rects.append((rect, name))
            draw_y += 30
        # Кнопки скролла
        self.creative_scroll_up = pygame.Rect(self.creative_panel_rect.x + 160, list_top + 4, 32, 24)
        self.creative_scroll_down = pygame.Rect(self.creative_panel_rect.x + 160, list_top + list_height - 28, 32, 24)
        pygame.draw.rect(self.screen, (80,80,120), self.creative_scroll_up, border_radius=6)
        pygame.draw.rect(self.screen, (80,80,120), self.creative_scroll_down, border_radius=6)
        self.screen.blit(pygame.font.Font(None, 22).render('▲', True, (255,255,255)), (self.creative_scroll_up.x+7, self.creative_scroll_up.y+1))
        self.screen.blit(pygame.font.Font(None, 22).render('▼', True, (255,255,255)), (self.creative_scroll_down.x+7, self.creative_scroll_down.y+1))
        
        # Кнопки снизу
        pygame.draw.rect(self.screen, (80, 130, 80), self.creative_start_rect, border_radius=10)
        pygame.draw.rect(self.screen, (220, 240, 220), self.creative_start_rect, 2, border_radius=10)
        self.screen.blit(pygame.font.Font(None, 24).render('Старт симуляции', True, (255,255,255)), (self.creative_start_rect.x + 8, self.creative_start_rect.y + 8))
        pygame.draw.rect(self.screen, (130, 80, 80), self.creative_back_rect, border_radius=8)
        pygame.draw.rect(self.screen, (240, 220, 220), self.creative_back_rect, 2, border_radius=8)
        self.screen.blit(pygame.font.Font(None, 22).render('Назад в меню', True, (255,255,255)), (self.creative_back_rect.x + 18, self.creative_back_rect.y + 6))
        
        # Кнопка редактора юнитов - между стартом симуляции и книгой заклинаний
        self.unit_editor_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 110, 160, 36)
        pygame.draw.rect(self.screen, (80, 80, 140), self.unit_editor_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 240), self.unit_editor_rect, 2, border_radius=8)
        self.screen.blit(pygame.font.Font(None, 21).render('Редактор юнитов', True, (255,255,255)), (self.unit_editor_rect.x + 14, self.unit_editor_rect.y + 8))
        
        # Кнопка редактирования книг заклинаний
        pygame.draw.rect(self.screen, (80, 120, 100), self.creative_spellbook_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 240, 220), self.creative_spellbook_rect, 2, border_radius=8)
        self.screen.blit(pygame.font.Font(None, 19).render('Книги заклинаний', True, (255,255,255)), (self.creative_spellbook_rect.x + 10, self.creative_spellbook_rect.y + 7))

    # ===================== Настройки (Settings) =====================
    def draw_settings(self):
        # Полупрозрачный оверлей как в паузе/меню
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((30, 20, 10, 200))
        self.screen.blit(overlay, (0,0))
        # Деревянная панель стиля главного меню
        panel_w, panel_h = 560, 360
        panel_x, panel_y = (SCREEN_WIDTH - panel_w)//2, (SCREEN_HEIGHT - panel_h)//2
        self.settings_panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        for y_offset in range(panel_h):
            panel_gradient = (
                int(150 - y_offset * 0.2),
                int(110 - y_offset * 0.15),
                int(80 - y_offset * 0.10)
            )
            pygame.draw.line(self.screen, panel_gradient,
                             (panel_x, panel_y + y_offset),
                             (panel_x + panel_w, panel_y + y_offset))
        pygame.draw.rect(self.screen, (70, 50, 35), self.settings_panel_rect, 6, border_radius=16)
        inner_panel = pygame.Rect(panel_x + 4, panel_y + 4, panel_w - 8, panel_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_panel, 2, border_radius=14)
        # Заголовок
        title_font = pygame.font.Font(None, 46)
        title = title_font.render('НАСТРОЙКИ', True, (255, 245, 220))
        title_shadow = title_font.render('НАСТРОЙКИ', True, (60, 50, 40))
        self.screen.blit(title_shadow, (panel_x + (panel_w - title.get_width())//2 + 2, panel_y + 18))
        self.screen.blit(title, (panel_x + (panel_w - title.get_width())//2, panel_y + 16))
        font = pygame.font.Font(None, 32)
        y = panel_y + 86
        # Музыка
        label_x = panel_x + 40
        val_x = panel_x + panel_w - 120
        btn_minus_x = panel_x + panel_w - 200
        btn_plus_x = panel_x + panel_w - 60
        self.music_minus_rect = pygame.Rect(btn_minus_x, y, 40, 40)
        self.music_plus_rect = pygame.Rect(btn_plus_x, y, 40, 40)
        for r in [self.music_minus_rect, self.music_plus_rect]:
            for yy in range(r.height):
                grad = (int(140 - yy*0.5), int(120 - yy*0.4), int(100 - yy*0.3))
                pygame.draw.line(self.screen, grad, (r.x, r.y+yy), (r.x+r.width, r.y+yy))
            pygame.draw.rect(self.screen, (70,50,35), r, 3, border_radius=8)
            pygame.draw.rect(self.screen, (180,150,120), pygame.Rect(r.x+2, r.y+2, r.width-4, r.height-4), 1, border_radius=7)
        self.screen.blit(font.render('-', True, (255,245,220)), (self.music_minus_rect.x+13, self.music_minus_rect.y+5))
        self.screen.blit(font.render('+', True, (255,245,220)), (self.music_plus_rect.x+10, self.music_plus_rect.y+5))
        self.screen.blit(font.render('Музыка', True, (255,245,220)), (label_x, y))
        self.screen.blit(font.render(f"{int(self.music_volume*100)}%", True, (255,245,220)), (val_x, y))
        y += 80
        # Звуки
        self.sfx_minus_rect = pygame.Rect(btn_minus_x, y, 40, 40)
        self.sfx_plus_rect = pygame.Rect(btn_plus_x, y, 40, 40)
        for r in [self.sfx_minus_rect, self.sfx_plus_rect]:
            for yy in range(r.height):
                grad = (int(140 - yy*0.5), int(120 - yy*0.4), int(100 - yy*0.3))
                pygame.draw.line(self.screen, grad, (r.x, r.y+yy), (r.x+r.width, r.y+yy))
            pygame.draw.rect(self.screen, (70,50,35), r, 3, border_radius=8)
            pygame.draw.rect(self.screen, (180,150,120), pygame.Rect(r.x+2, r.y+2, r.width-4, r.height-4), 1, border_radius=7)
        self.screen.blit(font.render('-', True, (255,245,220)), (self.sfx_minus_rect.x+13, self.sfx_minus_rect.y+5))
        self.screen.blit(font.render('+', True, (255,245,220)), (self.sfx_plus_rect.x+10, self.sfx_plus_rect.y+5))
        self.screen.blit(font.render('Звуки', True, (255,245,220)), (label_x, y))
        self.screen.blit(font.render(f"{int(self.sfx_volume*100)}%", True, (255,245,220)), (val_x, y))
        y += 80
        # Отключить звук
        self.mute_toggle_rect = pygame.Rect(panel_x + (panel_w-260)//2, y, 260, 48)
        for yy in range(self.mute_toggle_rect.height):
            grad = (int(90 - yy*0.3), int(70 - yy*0.2), int(50 - yy*0.15)) if self.muted else (int(120 - yy*0.3), int(100 - yy*0.25), int(80 - yy*0.2))
            pygame.draw.line(self.screen, grad,
                             (self.mute_toggle_rect.x, self.mute_toggle_rect.y + yy),
                             (self.mute_toggle_rect.x + self.mute_toggle_rect.width, self.mute_toggle_rect.y + yy))
        pygame.draw.rect(self.screen, (70,50,35), self.mute_toggle_rect, 3, border_radius=12)
        pygame.draw.rect(self.screen, (180,150,120), pygame.Rect(self.mute_toggle_rect.x+2, self.mute_toggle_rect.y+2, self.mute_toggle_rect.width-4, self.mute_toggle_rect.height-4), 1, border_radius=10)
        self.screen.blit(font.render('Звук выключен' if self.muted else 'Выключить звук', True, (255,245,220)), (self.mute_toggle_rect.x+22, self.mute_toggle_rect.y+10))
        # Кнопка назад
        back_w, back_h = 200, 50
        self.settings_back_rect = pygame.Rect(panel_x + (panel_w - back_w)//2, panel_y + panel_h - back_h - 20, back_w, back_h)
        for yy in range(back_h):
            grad = (int(150 - yy * 0.35), int(110 - yy * 0.30), int(80 - yy * 0.25))
            pygame.draw.line(self.screen, grad, (self.settings_back_rect.x, self.settings_back_rect.y + yy), (self.settings_back_rect.x + back_w, self.settings_back_rect.y + yy))
        pygame.draw.rect(self.screen, (70,50,35), self.settings_back_rect, 5, border_radius=12)
        pygame.draw.rect(self.screen, (170,140,110), pygame.Rect(self.settings_back_rect.x+3, self.settings_back_rect.y+3, back_w-6, back_h-6), 2, border_radius=10)
        back_font = pygame.font.Font(None, 30)
        back_text = back_font.render('Назад', True, (255,245,220))
        back_shadow = back_font.render('Назад', True, (60,50,40))
        self.screen.blit(back_shadow, (self.settings_back_rect.x + (back_w - back_shadow.get_width())//2 + 2, self.settings_back_rect.y + 14))
        self.screen.blit(back_text, (self.settings_back_rect.x + (back_w - back_text.get_width())//2, self.settings_back_rect.y + 12))

    def handle_settings_click(self, pos):
        if hasattr(self, 'music_minus_rect') and self.music_minus_rect.collidepoint(pos):
            self.music_volume = max(0.0, round(self.music_volume - 0.1, 2))
            self._apply_audio_volumes()
            self._save_settings()
            return
        if hasattr(self, 'music_plus_rect') and self.music_plus_rect.collidepoint(pos):
            self.music_volume = min(1.0, round(self.music_volume + 0.1, 2))
            self._apply_audio_volumes()
            self._save_settings()
            return
        if hasattr(self, 'sfx_minus_rect') and self.sfx_minus_rect.collidepoint(pos):
            self.sfx_volume = max(0.0, round(self.sfx_volume - 0.1, 2))
            self._apply_audio_volumes()
            self._save_settings()
            return
        if hasattr(self, 'sfx_plus_rect') and self.sfx_plus_rect.collidepoint(pos):
            self.sfx_volume = min(1.0, round(self.sfx_volume + 0.1, 2))
            self._apply_audio_volumes()
            self._save_settings()
            return
        if hasattr(self, 'mute_toggle_rect') and self.mute_toggle_rect.collidepoint(pos):
            self.muted = not self.muted
            self._apply_audio_volumes()
            self._save_settings()
            return
        if hasattr(self, 'settings_back_rect') and self.settings_back_rect.collidepoint(pos):
            # Если зашли в настройки из паузы — возвращаемся в пауз-меню
            if self.is_paused:
                self.state = 'game'
                self.menu_open = True
                return
            # Иначе возвращаемся в главное меню настроек
            self.state = 'menu'
            return

    def _apply_audio_volumes(self):
        from pygame import mixer
        mv = 0.0 if self.muted else self.music_volume
        sv = 0.0 if self.muted else self.sfx_volume
        try:
            mixer.music.set_volume(mv)
        except Exception:
            pass
        # Применяем к загруженным эффектам
        for lst in [getattr(self, 'human_melee_sounds', []), getattr(self, 'monster_melee_sounds', [])]:
            for s in lst:
                try:
                    s.set_volume(sv)
                except Exception:
                    pass
        for s in [getattr(self, 'shot_sound', None), getattr(self, 'shot2_sound', None), getattr(self, 'magic_shot_sound', None), getattr(self, 'button_click_sound', None)]:
            if s:
                try:
                    s.set_volume(sv)
                except Exception:
                    pass
        # Громкость длинных интро-звуков приравниваем к громкости музыки
        for s in getattr(self, 'battle_intro_sounds', []) or []:
            try:
                s.set_volume(mv)
            except Exception:
                pass
        if getattr(self, 'current_intro_sound', None):
            try:
                self.current_intro_sound.set_volume(mv)
            except Exception:
                pass

    def _load_settings(self):
        try:
            if os.path.exists(self._settings_path):
                import json
                with open(self._settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.music_volume = float(data.get('music_volume', self.music_volume))
                self.sfx_volume = float(data.get('sfx_volume', self.sfx_volume))
                self.muted = bool(data.get('muted', self.muted))
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")

    def _save_settings(self):
        try:
            os.makedirs(os.path.dirname(self._settings_path), exist_ok=True)
            import json
            with open(self._settings_path, 'w', encoding='utf-8') as f:
                json.dump({'music_volume': self.music_volume, 'sfx_volume': self.sfx_volume, 'muted': self.muted}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    # --------- Unit overrides persistence ---------
    def _load_unit_overrides(self):
        try:
            if os.path.exists(self._unit_overrides_path):
                import json
                with open(self._unit_overrides_path, 'r', encoding='utf-8') as f:
                    self.unit_overrides = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки параметров юнитов: {e}")

    def _save_unit_overrides(self):
        try:
            os.makedirs(os.path.dirname(self._unit_overrides_path), exist_ok=True)
            import json
            with open(self._unit_overrides_path, 'w', encoding='utf-8') as f:
                json.dump(self.unit_overrides, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения параметров юнитов: {e}")
    
    def _load_spell_overrides(self):
        """Загрузка пользовательских параметров заклинаний"""
        try:
            if os.path.exists(self._spell_overrides_path):
                import json
                with open(self._spell_overrides_path, 'r', encoding='utf-8') as f:
                    self.spell_overrides = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки параметров заклинаний: {e}")
    
    def _save_spell_overrides(self):
        """Сохранение пользовательских параметров заклинаний"""
        try:
            os.makedirs(os.path.dirname(self._spell_overrides_path), exist_ok=True)
            import json
            with open(self._spell_overrides_path, 'w', encoding='utf-8') as f:
                json.dump(self.spell_overrides, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения параметров заклинаний: {e}")
    
    def _apply_spell_overrides_to_instance(self, spell):
        """Применение пользовательских параметров к экземпляру заклинания"""
        if not spell or not hasattr(spell, 'icon'):
            return
        
        spell_key = spell.icon
        if spell_key in self.spell_overrides:
            overrides = self.spell_overrides[spell_key]
            for param, value in overrides.items():
                if hasattr(spell, param):
                    setattr(spell, param, value)

    def _apply_unit_overrides_to_instance(self, unit):
        # Для героев используем ключ вида Hero_<race>_<class>, чтобы настраивать по расам и классам
        data = None
        try:
            from .units import Hero as _Hero
            if isinstance(unit, _Hero):
                team = getattr(unit, 'team', '')
                hero_class = getattr(unit, 'hero_class', '')
                # Пытаемся найти специфичный оверрайд для race+class
                if team and hero_class:
                    data = self.unit_overrides.get(f"Hero_{team}_{hero_class}")
                # Если не нашли, ищем по расе
                if not data and team:
                    data = self.unit_overrides.get(f"Hero_{team}")
                # Если и это не нашли, используем общий Hero
                if not data:
                    data = self.unit_overrides.get('Hero')
        except Exception:
            pass
        if data is None:
            data = self.unit_overrides.get(unit.__class__.__name__)
        if not data:
            return
        # Сохраняем список примененных параметров для отслеживания
        applied_params = []
        # Применяем все параметры из JSON (кроме health и max_health для отрядов - они вычисляются автоматически)
        for key in ['attack','defense','speed','initiative','attack_range','is_ranged',
                    'knowledge','spell_power','mana','max_mana','mana_regen',
                    'phys_attack','magic_attack','phys_defense','magic_defense','magic_resist','attack_type','hero_class',
                    'squad_count','base_squad_count','luck','combat_spirit','unit_hp','current_unit_hp']:
            if key in data:
                try:
                    # У нежити боевой дух всегда 0, игнорируем изменения
                    if key == 'combat_spirit':
                        from .units import get_unit_race
                        unit_race = get_unit_race(unit)
                        if unit_race == 'undead':
                            continue  # Не применяем изменение боевого духа для нежити
                    # Применяем значение из JSON напрямую
                    setattr(unit, key, data[key])
                    applied_params.append(key)
                except Exception as e:
                    # Логируем ошибки применения параметров для отладки
                    print(f"Warning: Failed to apply {key} = {data[key]} to {unit.__class__.__name__}: {e}")
                    pass
        
        # Для отрядов: синхронизируем health и max_health на основе unit_hp и squad_count
        if hasattr(unit, 'squad_count') and getattr(unit, 'squad_count', 1) > 1:
            # Если unit_hp не был установлен из JSON, вычисляем его
            if not hasattr(unit, 'unit_hp') or unit.unit_hp is None:
                # Сначала проверяем max_health из JSON (для обратной совместимости)
                if 'max_health' in data:
                    unit.unit_hp = max(1, int(data['max_health']) // unit.squad_count)
                # Иначе используем текущий max_health
                elif hasattr(unit, 'max_health') and unit.max_health > 0:
                    unit.unit_hp = max(1, unit.max_health // unit.squad_count)
                else:
                    # Если max_health тоже нет, используем health (для обратной совместимости)
                    if 'health' in data:
                        unit.unit_hp = max(1, int(data['health']) // unit.squad_count)
                    elif hasattr(unit, 'health') and unit.health > 0:
                        unit.unit_hp = max(1, unit.health // unit.squad_count)
                    else:
                        unit.unit_hp = 1  # Значение по умолчанию
            
            # Если current_unit_hp не установлен, вычисляем из текущего health
            if not hasattr(unit, 'current_unit_hp') or unit.current_unit_hp is None:
                if hasattr(unit, 'health') and unit.health > 0:
                    unit_hp = getattr(unit, 'unit_hp', 1)
                    if unit_hp > 0:
                        remainder = unit.health % unit_hp
                        unit.current_unit_hp = remainder if remainder > 0 else unit_hp
                    else:
                        unit.current_unit_hp = 1
                else:
                    # Если health не установлен, текущий юнит полный
                    unit.current_unit_hp = unit.unit_hp
            
            # Пересчитываем health и max_health на основе unit_hp и squad_count
            unit.health = (unit.squad_count - 1) * unit.unit_hp + unit.current_unit_hp
            unit.max_health = unit.squad_count * unit.unit_hp
        else:
            # Для одиночных юнитов: применяем health и max_health из JSON если указаны
            if 'health' in data:
                try:
                    unit.health = int(data['health'])
                    applied_params.append('health')
                except Exception:
                    pass
            if 'max_health' in data:
                try:
                    unit.max_health = int(data['max_health'])
                    applied_params.append('max_health')
                except Exception:
                    pass
            # Если health указан, но max_health нет - устанавливаем max_health = health
            if 'health' in data and 'max_health' not in data:
                try:
                    unit.max_health = int(data['health'])
                except Exception:
                    pass
        # После применения оверрайдов убеждаемся, что у нежити боевой дух = 0
        try:
            from .units import get_unit_race
            unit_race = get_unit_race(unit)
            if unit_race == 'undead':
                unit.combat_spirit = 0
        except Exception:
            pass
        # Отладочная информация (для проверки применения параметров)
        # print(f"DEBUG: Applied overrides to {unit.__class__.__name__}: {[k for k in data.keys() if k in ['attack', 'defense', 'knowledge', 'spell_power', 'luck', 'combat_spirit']]}")
        # Синхронизируем is_ranged с hero_class для героев (если hero_class был изменен)
        try:
            from .units import Hero as _Hero
            if isinstance(unit, _Hero) and 'hero_class' in data:
                hero_class = getattr(unit, 'hero_class', None)
                if hero_class == 'archer' or hero_class == 'mage':
                    unit.is_ranged = True
                    if hero_class == 'archer':
                        unit.attack_type = 'physical'
                    else:  # mage
                        unit.attack_type = 'magical'
                else:  # warrior
                    unit.is_ranged = False
                    unit.attack_type = 'physical'
                # Обновляем изображение героя с новым классом
                team = getattr(unit, 'team', 'human')
                image_name = f'hero_{team}_{hero_class}'
                try:
                    unit.image = load_image(image_name)
                except:
                    # Если изображения для класса нет, используем стандартное
                    unit.image = load_image(f'hero_{team}')
        except Exception:
            pass
        # Если изменили attack или defense, нужно пересчитать phys_attack/magic_attack через convert_old_stats_to_new
        # НО только если эти параметры действительно были изменены через overrides
        # Сохраняем оригинальные значения из JSON перед преобразованием
        saved_attack = data.get('attack') if 'attack' in data else None
        saved_defense = data.get('defense') if 'defense' in data else None
        if 'attack' in data or 'defense' in data:
            try:
                if hasattr(unit, 'convert_old_stats_to_new'):
                    unit._needs_stat_conversion = True
                    unit.convert_old_stats_to_new()
                    # Восстанавливаем значения из JSON после преобразования, если они были заданы
                    if saved_attack is not None:
                        unit.attack = saved_attack
                    if saved_defense is not None:
                        unit.defense = saved_defense
            except Exception:
                pass
        # Корректируем здоровье в рамках max_health (НО только если health не был явно задан в overrides)
        if hasattr(unit, 'max_health') and hasattr(unit, 'health'):
            try:
                # Если health явно не задан в overrides, устанавливаем его равным max_health
                if 'health' not in data:
                    unit.health = unit.max_health  # считать, что юнит полон после изменения параметров
            except Exception:
                pass
        # Корректируем ману в рамках max_mana (НО только если mana не был явно задан в overrides)
        if hasattr(unit, 'max_mana') and hasattr(unit, 'mana'):
            try:
                # Если mana явно не задан в overrides, устанавливаем его равным max_mana
                if 'mana' not in data:
                    unit.mana = unit.max_mana
            except Exception:
                pass
        # Если squad_count был изменен из overrides, нужно обновить структуру отряда
        if 'squad_count' in data or 'base_squad_count' in data:
            try:
                # Если unit_hp еще не установлен, устанавливаем его из max_health
                if not hasattr(unit, 'unit_hp') or unit.unit_hp is None:
                    unit.unit_hp = unit.max_health
                    unit.current_unit_hp = getattr(unit, 'health', unit.max_health)
                    # Если base_squad_count еще не установлен, инициализируем его
                    if not hasattr(unit, 'base_squad_count'):
                        unit.base_squad_count = getattr(unit, 'squad_count', 1)
                # Обновляем base_squad_count если он задан
                if 'base_squad_count' in data:
                    unit.base_squad_count = int(data['base_squad_count'])
                # Обновляем squad_count если он задан
                if 'squad_count' in data:
                    unit.squad_count = int(data['squad_count'])
                # Убеждаемся, что current_unit_hp установлен
                if not hasattr(unit, 'current_unit_hp'):
                    unit.current_unit_hp = getattr(unit, 'health', unit.max_health)
                # Пересчитываем общее здоровье отряда
                unit.health = (unit.squad_count - 1) * unit.unit_hp + unit.current_unit_hp
                unit.max_health = unit.base_squad_count * unit.unit_hp
            except Exception:
                pass

    def _apply_overrides_to_all_units(self):
        for unit in self.units:
            try:
                self._apply_unit_overrides_to_instance(unit)
            except Exception:
                pass

    # --------- Spells catalog and editor ---------
    def _build_spells_catalog(self):
        from .spells import (
            BlessSpell, CurseSpell, SlowSpell, FireArrowSpell, DispelSpell,
            RuneShieldSpell, RuneHasteSpell, ForgetSpell, FrostRingSpell, RaiseDeadSpell, FireballSpell, StoneSkinSpell, UndeadHealSpell, HasteSpell, FireShieldSpell, HealSpell, ResurrectionSpell, IceShieldSpell, LightningSpell, EarthSpikesSpell, CounterstrikeSpell, RuneWallSpell, RuneMagicSpell, RuneBerserkerSpell, WeaknessSpell, FireWallSpell, MeteorRainSpell, IceArrowSpell, PhantomSpell, ChainLightningSpell, AccuracySpell, QuicksandSpell, EarthShockSpell, PrayerSpell, BlindnessSpell
        )
        classes = [BlessSpell, CurseSpell, SlowSpell, FireArrowSpell, DispelSpell,
                   RuneShieldSpell, RuneHasteSpell, ForgetSpell, FrostRingSpell, RaiseDeadSpell, FireballSpell, StoneSkinSpell, UndeadHealSpell, HasteSpell, FireShieldSpell, HealSpell, ResurrectionSpell, IceShieldSpell, LightningSpell, EarthSpikesSpell, CounterstrikeSpell, RuneWallSpell, RuneMagicSpell, RuneBerserkerSpell, WeaknessSpell, FireWallSpell, MeteorRainSpell, IceArrowSpell, PhantomSpell, ChainLightningSpell, AccuracySpell, QuicksandSpell, EarthShockSpell, PrayerSpell, BlindnessSpell]
        catalog = []
        for cls in classes:
            try:
                s = cls()
                catalog.append({'name': s.name, 'school': getattr(s, 'school', None), 'class': cls, 'icon': getattr(s, 'icon', None), 'target_type': getattr(s, 'target_type', 'enemy')})
            except Exception:
                pass
        return catalog

    def draw_spellbook_editor(self):
        self.screen.fill((25, 30, 45))
        title = pygame.font.Font(None, 46).render('Книги заклинаний (Креатив)', True, (240,240,255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 16))
        font = pygame.font.Font(None, 26)
        
        # Инициализация переменных если они не установлены
        if not hasattr(self, '_spellbook_selected_school'):
            self._spellbook_selected_school = 'all'
        if not hasattr(self, '_spellbook_selected_hero_idx'):
            self._spellbook_selected_hero_idx = 0
        
        # Вкладки героев со скроллом (максимум 2 героя)
        heroes = getattr(self, '_spellbook_heroes', [])
        # Ограничиваем до двух героев
        heroes = heroes[:2]
        self._spellbook_heroes = heroes  # Обновляем список
        # Если выбранный индекс выходит за границы, сбрасываем на первый
        if self._spellbook_selected_hero_idx >= len(heroes):
            self._spellbook_selected_hero_idx = 0
        
        self.spellbook_hero_tabs = []
        
        # Скролл для табов если героев много (теперь максимум 2)
        hero_tab_scroll = getattr(self, 'hero_tab_scroll', 0)
        max_visible_tabs = 2  # Максимум видимых табов (ограничено до 2 героев)
        start_tab = min(hero_tab_scroll, max(0, len(heroes) - max_visible_tabs))
        end_tab = min(len(heroes), start_tab + max_visible_tabs)
        
        tab_x = 20
        for idx in range(start_tab, end_tab):
            h = heroes[idx]
            rect = pygame.Rect(tab_x, 60, 220, 36)
            sel = (idx == getattr(self, '_spellbook_selected_hero_idx', 0))
            pygame.draw.rect(self.screen, (90,120,160) if sel else (60,70,90), rect, border_radius=8)
            pygame.draw.rect(self.screen, (210,220,240), rect, 2, border_radius=8)
            
            # Красивая подпись с классом и расой
            hero_class = getattr(h, 'hero_class', 'warrior')
            hero_team = getattr(h, 'team', 'human')
            class_labels = {'warrior': 'Воин', 'archer': 'Лучник', 'mage': 'Маг'}
            class_label = class_labels.get(hero_class, hero_class)
            team_label = TEAM_LABELS.get(hero_team, hero_team)
            # Формат: "Воин (Люди)" или "Лучник (Эльфы)"
            label = f"{class_label} ({team_label})"
            label_surf = font.render(label, True, (255,255,255))
            # Обрезаем если не влезает - сначала убираем расу
            if label_surf.get_width() > rect.w - 20:
                label = f"{class_label}"
                label_surf = font.render(label, True, (255,255,255))
            # Если все еще не влезает, используем короткое имя
            if label_surf.get_width() > rect.w - 20:
                label = f"Герой {idx+1}"
                label_surf = font.render(label, True, (255,255,255))
            self.screen.blit(label_surf, (rect.x+10, rect.y+7))
            self.spellbook_hero_tabs.append((rect, idx))
            tab_x += 240
        
        # Кнопки скролла табов если героев больше чем влезает
        if len(heroes) > max_visible_tabs:
            self.hero_tab_scroll_left = pygame.Rect(10, 68, 24, 24)
            self.hero_tab_scroll_right = pygame.Rect(tab_x, 68, 24, 24)
            pygame.draw.rect(self.screen, (80,80,120), self.hero_tab_scroll_left, border_radius=6)
            pygame.draw.rect(self.screen, (80,80,120), self.hero_tab_scroll_right, border_radius=6)
            self.screen.blit(pygame.font.Font(None, 20).render('◄', True, (255,255,255)), (self.hero_tab_scroll_left.x+5, self.hero_tab_scroll_left.y+2))
            self.screen.blit(pygame.font.Font(None, 20).render('►', True, (255,255,255)), (self.hero_tab_scroll_right.x+5, self.hero_tab_scroll_right.y+2))
        # Фильтр школ (вертикальная панель со скроллом)
        schools = ['all','light','darkness','fire','water','earth','air','rune']
        self.spellbook_school_rects = []
        panel_x = 20
        panel_top = 110
        panel_w = 150
        panel_h = SCREEN_HEIGHT - 200
        # фон панели школ
        pygame.draw.rect(self.screen, (40,50,70), (panel_x-2, panel_top-2, panel_w, panel_h), border_radius=8)
        # элементы
        item_h = 30
        vis_cnt_s = max(1, (panel_h - 16)//item_h)
        self.school_scroll = getattr(self, 'school_scroll', 0)
        start_s = min(self.school_scroll, max(0, len(schools) - vis_cnt_s))
        end_s = min(len(schools), start_s + vis_cnt_s)
        draw_y = panel_top + 6
        for sc in schools[start_s:end_s]:
            rect = pygame.Rect(panel_x, draw_y, panel_w-20, item_h-4)
            sel = (sc == getattr(self, '_spellbook_selected_school', 'all'))
            pygame.draw.rect(self.screen, (80,120,90) if sel else (60,60,80), rect, border_radius=6)
            pygame.draw.rect(self.screen, (200,200,220), rect, 2, border_radius=6)
            label = sc.capitalize() if sc!='all' else 'Все'
            self.screen.blit(font.render(label, True, (255,255,255)), (rect.x+10, rect.y+4))
            self.spellbook_school_rects.append((rect, sc))
            draw_y += item_h
        # стрелки скролла школ
        self.school_up = pygame.Rect(panel_x + panel_w - 24, panel_top, 20, 20)
        self.school_down = pygame.Rect(panel_x + panel_w - 24, panel_top + panel_h - 20, 20, 20)
        pygame.draw.rect(self.screen, (80,80,120), self.school_up, border_radius=4)
        pygame.draw.rect(self.screen, (80,80,120), self.school_down, border_radius=4)
        self.screen.blit(font.render('▲', True, (255,255,255)), (self.school_up.x+3, self.school_up.y-2))
        self.screen.blit(font.render('▼', True, (255,255,255)), (self.school_down.x+3, self.school_down.y-2))
        # Доступные заклинания
        hero_idx = getattr(self, '_spellbook_selected_hero_idx', 0)
        # Проверяем, что индекс не выходит за границы (героев максимум 2)
        if hero_idx >= len(heroes):
            hero_idx = 0
            self._spellbook_selected_hero_idx = 0
        sel_hero = heroes[hero_idx] if heroes and hero_idx < len(heroes) else None
        available = [it for it in self._spells_catalog if self._spellbook_selected_school in ('all', it['school'])]
        self.spell_add_rects = []
        x = panel_x + panel_w + 20
        y = 120
        self.screen.blit(font.render('Доступные:', True, (220,220,240)), (x, y))
        # Прокручиваемая область доступных
        avail_top = y + 30
        avail_height = SCREEN_HEIGHT - 190
        pygame.draw.rect(self.screen, (35,40,65), (x-2, avail_top-2, 300, avail_height), border_radius=8)
        vis_cnt = max(1, (avail_height - 16)//30)
        self.spell_avail_scroll = getattr(self, 'spell_avail_scroll', 0)
        start = min(self.spell_avail_scroll, max(0, len(available) - vis_cnt))
        end = min(len(available), start + vis_cnt)
        draw_y = avail_top + 6
        for it in available[start:end]:
            rect = pygame.Rect(x, draw_y, 260, 26)
            pygame.draw.rect(self.screen, (50,60,80), rect, border_radius=6)
            pygame.draw.rect(self.screen, (160,170,200), rect, 2, border_radius=6)
            label = it['name'] + (f" [{it['school']}]" if it['school'] else '')
            self.screen.blit(font.render(label, True, (240,240,255)), (rect.x+8, rect.y+4))
            self.spell_add_rects.append((rect, it))
            draw_y += 30
        # Скролл кнопки
        self.spell_avail_up = pygame.Rect(x+260, avail_top, 28, 22)
        self.spell_avail_down = pygame.Rect(x+260, avail_top+avail_height-22, 28, 22)
        pygame.draw.rect(self.screen, (80,80,120), self.spell_avail_up, border_radius=6)
        pygame.draw.rect(self.screen, (80,80,120), self.spell_avail_down, border_radius=6)
        self.screen.blit(font.render('▲', True, (255,255,255)), (self.spell_avail_up.x+6, self.spell_avail_up.y+1))
        self.screen.blit(font.render('▼', True, (255,255,255)), (self.spell_avail_down.x+6, self.spell_avail_down.y+1))
        # Текущая книга
        x = panel_x + panel_w + 20 + 300 + 40
        y = 120
        self.screen.blit(font.render('Книга героя:', True, (220,220,240)), (x, y))
        self.spell_remove_rects = []
        # Прокручиваемая область книги
        book_top = y + 30
        book_height = SCREEN_HEIGHT - 190
        pygame.draw.rect(self.screen, (45,40,35), (x-2, book_top-2, 340, book_height), border_radius=8)
        
        if not heroes or sel_hero is None:
            # Если героев нет, показываем сообщение
            no_heroes_text = [
                "Нет созданных героев",
                "",
                "Создайте героев в режиме",
                "креативного редактора,",
                "чтобы добавлять им",
                "заклинания в книгу"
            ]
            msg_y = book_top + book_height // 2 - len(no_heroes_text) * 15
            for line in no_heroes_text:
                text_surf = pygame.font.Font(None, 24).render(line, True, (180, 180, 200))
                text_x = x + (340 - text_surf.get_width()) // 2
                self.screen.blit(text_surf, (text_x, msg_y))
                msg_y += 30
        else:
            # Обычный код для книги героя
            vis_cnt_b = max(1, (book_height - 16)//30)
            self.spell_book_scroll = getattr(self, 'spell_book_scroll', 0)
            book_list = list(getattr(sel_hero, 'spells', [])) if sel_hero else []
            start_b = min(self.spell_book_scroll, max(0, len(book_list) - vis_cnt_b))
            end_b = min(len(book_list), start_b + vis_cnt_b)
            draw_y = book_top + 6
            for s in book_list[start_b:end_b]:
                rect = pygame.Rect(x, draw_y, 300, 26)
                pygame.draw.rect(self.screen, (80,70,60), rect, border_radius=6)
                pygame.draw.rect(self.screen, (200,180,150), rect, 2, border_radius=6)
                label = getattr(s, 'name', s.__class__.__name__)
                self.screen.blit(font.render(label, True, (255,245,220)), (rect.x+8, rect.y+4))
                self.spell_remove_rects.append((rect, s))
                draw_y += 30
            # Скролл кнопки
            self.spell_book_up = pygame.Rect(x+300, book_top, 28, 22)
            self.spell_book_down = pygame.Rect(x+300, book_top+book_height-22, 28, 22)
            pygame.draw.rect(self.screen, (120,100,80), self.spell_book_up, border_radius=6)
            pygame.draw.rect(self.screen, (120,100,80), self.spell_book_down, border_radius=6)
            self.screen.blit(font.render('▲', True, (255,255,255)), (self.spell_book_up.x+6, self.spell_book_up.y+1))
            self.screen.blit(font.render('▼', True, (255,255,255)), (self.spell_book_down.x+6, self.spell_book_down.y+1))
        # Кнопки
        self.spellbook_back_rect = pygame.Rect(20, SCREEN_HEIGHT-60, 180, 40)
        pygame.draw.rect(self.screen, (130,80,80), self.spellbook_back_rect, border_radius=8)
        pygame.draw.rect(self.screen, (240,220,220), self.spellbook_back_rect, 2, border_radius=8)
        self.screen.blit(pygame.font.Font(None, 28).render('Назад', True, (255,255,255)), (self.spellbook_back_rect.x+60, self.spellbook_back_rect.y+8))
        
        # Кнопка изменения параметров заклинаний
        self.spell_params_button_rect = pygame.Rect(220, SCREEN_HEIGHT-60, 260, 40)
        pygame.draw.rect(self.screen, (80,100,140), self.spell_params_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200,220,255), self.spell_params_button_rect, 2, border_radius=8)
        self.screen.blit(pygame.font.Font(None, 26).render('Изменить параметры', True, (255,255,255)), (self.spell_params_button_rect.x+20, self.spell_params_button_rect.y+10))

    def handle_spellbook_editor_click(self, pos):
        # Кнопка изменения параметров
        if hasattr(self, 'spell_params_button_rect') and self.spell_params_button_rect.collidepoint(pos):
            if self.button_click_sound:
                self.button_click_sound.play()
            self.state = 'spell_editor'
            return
        
        # Скролл табов героев
        if hasattr(self, 'hero_tab_scroll_left') and self.hero_tab_scroll_left.collidepoint(pos):
            self.hero_tab_scroll = max(0, getattr(self, 'hero_tab_scroll', 0) - 1)
            return
        
        if hasattr(self, 'hero_tab_scroll_right') and self.hero_tab_scroll_right.collidepoint(pos):
            heroes = getattr(self, '_spellbook_heroes', [])
            # Ограничиваем до двух героев и используем max_visible_tabs = 2
            heroes = heroes[:2]
            max_visible_tabs = 2
            max_scroll = max(0, len(heroes) - max_visible_tabs)
            self.hero_tab_scroll = min(max_scroll, getattr(self, 'hero_tab_scroll', 0) + 1)
            return
        
        # Табы героев
        if hasattr(self, 'spellbook_hero_tabs'):
            for rect, idx in self.spellbook_hero_tabs:
                if rect.collidepoint(pos):
                    self._spellbook_selected_hero_idx = idx
                    return
        # Фильтр школ
        if hasattr(self, 'spellbook_school_rects'):
            for rect, sc in self.spellbook_school_rects:
                if rect.collidepoint(pos):
                    self._spellbook_selected_school = sc
                    return
        # Скролл школ
        if hasattr(self, 'school_up') and self.school_up.collidepoint(pos):
            self.school_scroll = max(0, getattr(self, 'school_scroll', 0) - 1)
            return
        if hasattr(self, 'school_down') and self.school_down.collidepoint(pos):
            schools = ['all','light','darkness','fire','water','earth','air','rune']
            panel_h = SCREEN_HEIGHT - 200
            item_h = 30
            vis_cnt_s = max(1, (panel_h - 16)//item_h)
            max_scroll_s = max(0, len(schools) - vis_cnt_s)
            self.school_scroll = min(max_scroll_s, getattr(self, 'school_scroll', 0) + 1)
            return
        # Добавление заклинания
        heroes = getattr(self, '_spellbook_heroes', [])
        # Ограничиваем до двух героев
        heroes = heroes[:2]
        hero_idx = getattr(self, '_spellbook_selected_hero_idx', 0)
        # Проверяем, что индекс не выходит за границы
        if hero_idx >= len(heroes):
            hero_idx = 0
            self._spellbook_selected_hero_idx = 0
        sel_hero = heroes[hero_idx] if heroes else None
        if sel_hero and hasattr(self, 'spell_add_rects'):
            for rect, it in self.spell_add_rects:
                if rect.collidepoint(pos):
                    # Не дублировать одинаковые по имени
                    if not any(getattr(s, 'name', None) == it['name'] for s in getattr(sel_hero, 'spells', [])):
                        try:
                            s = it['class']()
                            sel_hero.spells.append(s)
                        except Exception:
                            pass
                    return
        # Скролл доступных
        if hasattr(self, 'spell_avail_up') and self.spell_avail_up.collidepoint(pos):
            self.spell_avail_scroll = max(0, getattr(self, 'spell_avail_scroll', 0) - 1)
            return
        if hasattr(self, 'spell_avail_down') and self.spell_avail_down.collidepoint(pos):
            available = [it for it in self._spells_catalog if self._spellbook_selected_school in ('all', it['school'])]
            avail_height = SCREEN_HEIGHT - 220
            vis_cnt = max(1, (avail_height - 16)//30)
            max_scroll = max(0, len(available) - vis_cnt)
            self.spell_avail_scroll = min(max_scroll, getattr(self, 'spell_avail_scroll', 0) + 1)
            return
        # Удаление заклинания
        if sel_hero and hasattr(self, 'spell_remove_rects'):
            for rect, s in self.spell_remove_rects:
                if rect.collidepoint(pos):
                    try:
                        sel_hero.spells.remove(s)
                    except Exception:
                        pass
                    return
        # Скролл книги
        if hasattr(self, 'spell_book_up') and self.spell_book_up.collidepoint(pos):
            self.spell_book_scroll = max(0, getattr(self, 'spell_book_scroll', 0) - 1)
            return
        if hasattr(self, 'spell_book_down') and self.spell_book_down.collidepoint(pos):
            heroes = getattr(self, '_spellbook_heroes', [])
            # Ограничиваем до двух героев
            heroes = heroes[:2]
            hero_idx = getattr(self, '_spellbook_selected_hero_idx', 0)
            # Проверяем, что индекс не выходит за границы
            if hero_idx >= len(heroes):
                hero_idx = 0
                self._spellbook_selected_hero_idx = 0
            sel_hero = heroes[hero_idx] if heroes else None
            book_list = list(getattr(sel_hero, 'spells', [])) if sel_hero else []
            book_height = SCREEN_HEIGHT - 190
            vis_cnt_b = max(1, (book_height - 16)//30)
            max_scroll_b = max(0, len(book_list) - vis_cnt_b)
            self.spell_book_scroll = min(max_scroll_b, getattr(self, 'spell_book_scroll', 0) + 1)
            return
        # Назад
        if hasattr(self, 'spellbook_back_rect') and self.spellbook_back_rect.collidepoint(pos):
            self.state = 'creative'
            # Очищаем мертвых юнитов при возврате в креатив
            self.units = [u for u in self.units if u.health > 0]
            return

    # Универсальная обработка прокрутки колесом мыши (вызывать из внешнего цикла событий)
    def on_mouse_wheel(self, y_delta):
        mx, my = pygame.mouse.get_pos()
        # Креатив: скролл рас
        race_view_top = 40
        race_view_h = 120
        race_view_rect = pygame.Rect(self.creative_panel_rect.x + 8, race_view_top - 4, self.creative_panel_rect.w - 16, race_view_h + 8)
        if self.state == 'creative' and race_view_rect.collidepoint(mx, my):
            races_len = 6
            visible_races = max(1, race_view_h // 34)
            max_scroll = max(0, races_len - visible_races)
            self.creative_race_scroll = int(max(0, min(max_scroll, getattr(self, 'creative_race_scroll', 0) - y_delta)))
            return
        # Креатив: скролл списка юнитов
        if self.state == 'creative':
            list_top = 40 + race_view_h + 14 + 14  # приблизительно ниже блока рас и заголовка
            list_height = SCREEN_HEIGHT - 340  # Обновлено для соответствия с draw_creative
            list_rect = pygame.Rect(self.creative_panel_rect.x + 8, list_top, self.creative_panel_rect.w - 16, list_height)
            if list_rect.collidepoint(mx, my):
                unit_pool = self.creative_units_by_race.get(self.creative_selected_team, []) + self.creative_units_common
                visible_count = max(1, (list_height - 16) // 30)
                max_scroll = max(0, len(unit_pool) - visible_count)
                current_scroll = getattr(self, 'creative_units_scroll', 0)
                # y_delta обычно отрицателен при прокрутке вниз, положителен при прокрутке вверх
                # В pygame MOUSEWHEEL событие имеет поля x и y, где y > 0 означает прокрутку вверх
                self.creative_units_scroll = int(max(0, min(max_scroll, current_scroll - y_delta)))
                return
        # Unit editor: скролл списка юнитов
        if self.state == 'unit_editor':
            # Область списка юнитов: x=200, y начинается с 80, высота уменьшена
            unit_list_rect = pygame.Rect(200, 80, 180, SCREEN_HEIGHT - 320)
            if unit_list_rect.collidepoint(mx, my):
                pool = list(self.creative_units_by_race.get(getattr(self, '_unit_editor_selected_race', 'human'), []))
                for hero_class in ['warrior', 'archer', 'mage']:
                    pool.append((f"Hero_{getattr(self, '_unit_editor_selected_race', 'human')}_{hero_class}", Hero))
                visible_count = max(1, (SCREEN_HEIGHT - 320) // 36)
                max_scroll = max(0, len(pool) - visible_count)
                if not hasattr(self, '_unit_editor_units_scroll'):
                    self._unit_editor_units_scroll = 0
                self._unit_editor_units_scroll = int(max(0, min(max_scroll, self._unit_editor_units_scroll - y_delta)))
                return
        # Unit editor: скролл параметров
        if self.state == 'unit_editor':
            param_area_rect = pygame.Rect(420, 80, 340, SCREEN_HEIGHT - 200)
            if param_area_rect.collidepoint(mx, my):
                unit_key = getattr(self, '_unit_editor_selected_unit', None)
                if unit_key:
                    if unit_key == 'Hero' or unit_key.startswith('Hero_'):
                        params_count = 7  # hero_class, attack, defense, knowledge, spell_power, max_mana, luck, combat_spirit
                    else:
                        params_count = 11  # health, max_health, phys_attack, magic_attack, phys_defense, magic_defense, magic_resist, speed, initiative, attack_range, attack_type
                    visible_params = (SCREEN_HEIGHT - 200) // 40
                    max_scroll = max(0, params_count - visible_params)
                    if not hasattr(self, '_unit_editor_scroll'):
                        self._unit_editor_scroll = 0
                    self._unit_editor_scroll = int(max(0, min(max_scroll, self._unit_editor_scroll - y_delta)))
                return
        # История событий: скролл колесом мыши
        if self.history_panel_open:
            panel_w, panel_h = 600, 400
            panel_x = (SCREEN_WIDTH - panel_w)//2
            panel_y = (SCREEN_HEIGHT - panel_h)//2
            history_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            if history_rect.collidepoint(mx, my):
                max_lines = (panel_h - 80) // 22
                max_offset = max(0, len(self.event_log) - max_lines)
                # y_delta > 0 = прокрутка вверх (старые события), < 0 = вниз (новые)
                if y_delta > 0:
                    self.event_log_offset = min(self.event_log_offset + y_delta, max_offset)
                else:
                    self.event_log_offset = max(self.event_log_offset + y_delta, 0)
                return
        # Spellbook: доступные
        if self.state == 'spellbook_editor':
            panel_x = 20
            panel_w = 150
            avail_top = 120 + 30
            avail_height = SCREEN_HEIGHT - 190
            avail_rect = pygame.Rect(panel_x + panel_w + 20 - 2, avail_top-2, 300, avail_height)
            if avail_rect.collidepoint(mx, my):
                available = [it for it in self._spells_catalog if self._spellbook_selected_school in ('all', it['school'])]
                vis_cnt = max(1, (avail_height - 16)//30)
                max_scroll = max(0, len(available) - vis_cnt)
                self.spell_avail_scroll = int(max(0, min(max_scroll, getattr(self, 'spell_avail_scroll', 0) - y_delta)))
                return
            # книга героя
            book_top = 120 + 30
            book_height = SCREEN_HEIGHT - 190
            book_x = panel_x + panel_w + 20 + 300 + 40
            book_rect = pygame.Rect(book_x - 2, book_top-2, 340, book_height)
            if book_rect.collidepoint(mx, my):
                heroes = getattr(self, '_spellbook_heroes', [])
                # Ограничиваем до двух героев
                heroes = heroes[:2]
                hero_idx = getattr(self, '_spellbook_selected_hero_idx', 0)
                # Проверяем, что индекс не выходит за границы
                if hero_idx >= len(heroes):
                    hero_idx = 0
                    self._spellbook_selected_hero_idx = 0
                sel_hero = heroes[hero_idx] if heroes and hero_idx < len(heroes) else None
                book_list = list(getattr(sel_hero, 'spells', [])) if sel_hero else []
                vis_cnt_b = max(1, (book_height - 16)//30)
                max_scroll_b = max(0, len(book_list) - vis_cnt_b)
                self.spell_book_scroll = int(max(0, min(max_scroll_b, getattr(self, 'spell_book_scroll', 0) - y_delta)))
                return
            # панель школ
            panel_top = 110
            panel_h = SCREEN_HEIGHT - 200
            school_rect = pygame.Rect(panel_x-2, panel_top-2, panel_w, panel_h)
            if school_rect.collidepoint(mx, my):
                schools = ['all','light','darkness','fire','water','earth','air','rune']
                item_h = 30
                vis_cnt_s = max(1, (panel_h - 16)//item_h)
                max_scroll_s = max(0, len(schools) - vis_cnt_s)
                self.school_scroll = int(max(0, min(max_scroll_s, getattr(self, 'school_scroll', 0) - y_delta)))
                return
        
        # Spell editor: скролл списка заклинаний
        if self.state == 'spell_editor':
            list_x = 30
            list_y = 80
            list_w = 300
            list_h = SCREEN_HEIGHT - 150
            spell_list_rect = pygame.Rect(list_x, list_y, list_w, list_h)
            if spell_list_rect.collidepoint(mx, my):
                spell_list = self._spells_catalog
                visible_count = max(1, (list_h - 20) // 35)
                max_scroll = max(0, len(spell_list) - visible_count)
                self.spell_editor_scroll = int(max(0, min(max_scroll, getattr(self, 'spell_editor_scroll', 0) - y_delta)))
                return

    def draw_spell_editor(self):
        """Редактор параметров заклинаний"""
        self.screen.fill((25, 30, 45))
        font = pygame.font.Font(None, 28)
        title_font = pygame.font.Font(None, 42)
        title = title_font.render('Редактор заклинаний', True, (240,240,255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        # Список всех заклинаний
        spell_list = self._spells_catalog
        
        # Панель со списком заклинаний
        list_x = 30
        list_y = 80
        list_w = 300
        list_h = SCREEN_HEIGHT - 150
        
        pygame.draw.rect(self.screen, (40, 50, 70), (list_x, list_y, list_w, list_h), border_radius=8)
        
        # Заклинания со скроллом
        self.spell_editor_scroll = getattr(self, 'spell_editor_scroll', 0)
        visible_count = max(1, (list_h - 20) // 35)
        start_idx = min(self.spell_editor_scroll, max(0, len(spell_list) - visible_count))
        end_idx = min(len(spell_list), start_idx + visible_count)
        
        self.spell_editor_spell_rects = []
        draw_y = list_y + 10
        
        selected_spell_icon = getattr(self, '_spell_editor_selected', None)
        
        for spell_info in spell_list[start_idx:end_idx]:
            rect = pygame.Rect(list_x + 10, draw_y, list_w - 60, 30)
            is_selected = (spell_info['icon'] == selected_spell_icon)
            
            pygame.draw.rect(self.screen, (80, 100, 140) if is_selected else (50, 60, 80), rect, border_radius=6)
            pygame.draw.rect(self.screen, (180, 180, 200), rect, 2, border_radius=6)
            
            label = spell_info['name']
            self.screen.blit(pygame.font.Font(None, 22).render(label, True, (240,240,255)), (rect.x+8, rect.y+5))
            
            self.spell_editor_spell_rects.append((rect, spell_info['icon']))
            draw_y += 35
        
        # Кнопки скролла
        scroll_up_rect = pygame.Rect(list_x + list_w - 40, list_y + 10, 30, 30)
        scroll_down_rect = pygame.Rect(list_x + list_w - 40, list_y + list_h - 40, 30, 30)
        pygame.draw.rect(self.screen, (80,80,120), scroll_up_rect, border_radius=6)
        pygame.draw.rect(self.screen, (80,80,120), scroll_down_rect, border_radius=6)
        self.screen.blit(pygame.font.Font(None, 22).render('▲', True, (255,255,255)), (scroll_up_rect.x+7, scroll_up_rect.y+3))
        self.screen.blit(pygame.font.Font(None, 22).render('▼', True, (255,255,255)), (scroll_down_rect.x+7, scroll_down_rect.y+3))
        self.spell_editor_scroll_up = scroll_up_rect
        self.spell_editor_scroll_down = scroll_down_rect
        
        # Панель редактирования параметров
        if selected_spell_icon:
            # Найдём выбранное заклинание
            selected_spell_data = next((s for s in spell_list if s['icon'] == selected_spell_icon), None)
            if selected_spell_data:
                params_x = list_x + list_w + 40
                params_y = 80
                params_w = SCREEN_WIDTH - params_x - 40
                
                self.screen.blit(font.render(f"Редактирование: {selected_spell_data['name']}", True, (220,220,240)), (params_x, params_y))
                
                # Получаем текущие параметры
                overrides = self.spell_overrides.get(selected_spell_icon, {})
                
                # Создаём временный экземпляр для получения дефолтных значений
                try:
                    temp_spell = selected_spell_data['class']()
                except:
                    temp_spell = None
                
                # Список всех возможных параметров для редактирования
                editable_params = [
                    ('damage', 'Урон', (255,220,180), 1, lambda x: x > 0),
                    ('mana_cost', 'Мана', (180,200,255), 1, lambda x: True),
                    ('duration', 'Длительность', (255,255,180), 1, lambda x: x > 0),
                    ('heal_amount', 'Лечение', (120,255,120), 1, lambda x: x > 0),
                    ('spell_power_multiplier', 'Множитель силы', (220,180,255), 1, lambda x: x > 0),
                    ('buff_amount', 'Баффы %', (180,255,180), 1, lambda x: x > 0),
                    ('debuff_amount', 'Дебаффы %', (255,180,180), 1, lambda x: x > 0),
                    ('initiative_reduction', 'Замедл. иниц.', (200,200,200), 1, lambda x: x > 0),
                    ('speed_reduction', 'Замедл. скор.', (200,200,200), 1, lambda x: x > 0),
                    ('speed_bonus', 'Бонус скор.', (180,255,200), 1, lambda x: x > 0),
                    ('initiative_bonus', 'Бонус иниц.', (180,255,200), 1, lambda x: x > 0),
                    ('defense_bonus', 'Бонус защиты', (200,220,255), 1, lambda x: x > 0),
                    ('base_percent', 'Баз. процент', (255,220,200), 1, lambda x: x > 0),
                    ('absorption_percent', 'Поглощение %', (150,200,255), 1, lambda x: x > 0),
                    ('hp_bonus_percent', 'HP бонус %', (200,255,200), 1, lambda x: x > 0),
                    ('defense_bonus_percent', 'Защита бонус %', (200,220,255), 1, lambda x: x > 0),
                ]
                
                y = params_y + 50
                self.spell_editor_controls = []
                
                # Отображаем все параметры, которые есть у заклинания
                for param_name, display_name, color, delta, should_display in editable_params:
                    if temp_spell is None:
                        continue
                    
                    default_value = getattr(temp_spell, param_name, None)
                    if default_value is None:
                        continue
                    
                    # Проверяем, нужно ли показывать этот параметр
                    if not should_display(default_value):
                        continue
                    
                    current_value = overrides.get(param_name, default_value)
                    
                    # Название параметра
                    label_text = font.render(f"{display_name}:", True, color)
                    self.screen.blit(label_text, (params_x, y))
                    
                    # Значение параметра (кликабельное для ручного ввода)
                    value_text = font.render(str(current_value), True, (255, 255, 255))
                    value_rect = pygame.Rect(params_x + 160, y-5, 80, 30)
                    pygame.draw.rect(self.screen, (50,60,80), value_rect, border_radius=6)
                    pygame.draw.rect(self.screen, (120,140,180), value_rect, 2, border_radius=6)
                    self.screen.blit(value_text, (value_rect.x + (value_rect.w - value_text.get_width())//2, value_rect.y+3))
                    
                    # Кнопки +/-
                    minus_rect = pygame.Rect(params_x + 250, y-5, 40, 30)
                    plus_rect = pygame.Rect(params_x + 300, y-5, 40, 30)
                    pygame.draw.rect(self.screen, (100,80,80), minus_rect, border_radius=6)
                    pygame.draw.rect(self.screen, (80,100,80), plus_rect, border_radius=6)
                    self.screen.blit(font.render('-', True, (255,255,255)), (minus_rect.x+13, minus_rect.y+3))
                    self.screen.blit(font.render('+', True, (255,255,255)), (plus_rect.x+13, plus_rect.y+3))
                    
                    self.spell_editor_controls.append((param_name, 'minus', minus_rect, -delta))
                    self.spell_editor_controls.append((param_name, 'plus', plus_rect, delta))
                    self.spell_editor_controls.append((param_name, 'value', value_rect, 0))
                    y += 45
                
                # Формула урона для заклинаний урона
                if temp_spell is not None:
                    damage_val = overrides.get('damage', getattr(temp_spell, 'damage', 0))
                    multiplier_val = overrides.get('spell_power_multiplier', getattr(temp_spell, 'spell_power_multiplier', None))
                    heal_val = overrides.get('heal_amount', getattr(temp_spell, 'heal_amount', None))
                    
                    # Формула для заклинаний урона
                    if damage_val > 0 and multiplier_val is not None and multiplier_val > 0:
                        y += 15
                        formula_text = f"Формула урона: {damage_val} + сила_магии × {multiplier_val}"
                        formula_surf = pygame.font.Font(None, 24).render(formula_text, True, (255, 255, 100))
                        self.screen.blit(formula_surf, (params_x, y))
                        y += 30
                        
                        # Примеры расчета
                        example_text = f"Пример: при силе магии 3 = {damage_val + 3 * multiplier_val} урона"
                        example_surf = pygame.font.Font(None, 20).render(example_text, True, (200, 200, 150))
                        self.screen.blit(example_surf, (params_x + 20, y))
                    
                    # Формула для заклинаний лечения
                    elif heal_val is not None and heal_val > 0 and multiplier_val is not None and multiplier_val > 0:
                        y += 15
                        formula_text = f"Формула лечения: {heal_val} + сила_магии × {multiplier_val}"
                        formula_surf = pygame.font.Font(None, 24).render(formula_text, True, (120, 255, 120))
                        self.screen.blit(formula_surf, (params_x, y))
                        y += 30
                        
                        # Примеры расчета
                        example_text = f"Пример: при силе магии 3 = {heal_val + 3 * multiplier_val} HP"
                        example_surf = pygame.font.Font(None, 20).render(example_text, True, (150, 200, 150))
                        self.screen.blit(example_surf, (params_x + 20, y))
        else:
            # Сброс контролов если ничего не выбрано
            self.spell_editor_controls = []
        
        # Кнопка "Назад"
        back_rect = pygame.Rect(20, SCREEN_HEIGHT - 60, 140, 40)
        pygame.draw.rect(self.screen, (130, 80, 80), back_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 120, 120), back_rect, 2, border_radius=8)
        self.screen.blit(font.render('Назад', True, (255,255,255)), (back_rect.x+35, back_rect.y+8))
        self.spell_editor_back_rect = back_rect
        
        # Панель ввода числа (если активна)
        if hasattr(self, 'spell_num_input') and self.spell_num_input:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            self.screen.blit(overlay, (0,0))
            box_w, box_h = 260, 300
            box_x = SCREEN_WIDTH//2 - box_w//2
            box_y = SCREEN_HEIGHT//2 - box_h//2
            box = pygame.Rect(box_x, box_y, box_w, box_h)
            pygame.draw.rect(self.screen, (40,50,70), box, border_radius=12)
            pygame.draw.rect(self.screen, (200,200,220), box, 2, border_radius=12)
            lbl = pygame.font.Font(None, 28).render(f"Введите {self.spell_num_input.get('param')}", True, (255,255,255))
            self.screen.blit(lbl, (box_x+20, box_y+12))
            # Поле ввода
            input_rect = pygame.Rect(box_x+20, box_y+44, box_w-40, 36)
            pygame.draw.rect(self.screen, (20,30,50), input_rect, border_radius=8)
            pygame.draw.rect(self.screen, (120,140,180), input_rect, 2, border_radius=8)
            cur_text = str(self.spell_num_input.get('value', ''))
            self.screen.blit(pygame.font.Font(None, 28).render(cur_text, True, (240,240,255)), (input_rect.x+8, input_rect.y+6))
            # Кнопки цифр 0-9, backspace, OK, Cancel
            self.spell_num_buttons = []
            digits = [str(i) for i in range(1,10)] + ['0']
            bx, by = box_x+20, box_y+96
            for idx, d in enumerate(digits):
                r = pygame.Rect(bx + (idx%3)*70, by + (idx//3)*46, 60, 36)
                pygame.draw.rect(self.screen, (70,90,120), r, border_radius=8)
                pygame.draw.rect(self.screen, (180,200,220), r, 1, border_radius=8)
                self.screen.blit(pygame.font.Font(None, 28).render(d, True, (255,255,255)), (r.x+22, r.y+6))
                self.spell_num_buttons.append(('digit', d, r))
            # Backspace
            back_r = pygame.Rect(bx, by+4*46, 130, 36)
            pygame.draw.rect(self.screen, (100,70,70), back_r, border_radius=8)
            pygame.draw.rect(self.screen, (200,150,150), back_r, 1, border_radius=8)
            self.screen.blit(pygame.font.Font(None, 24).render('Удалить', True, (255,255,255)), (back_r.x+30, back_r.y+8))
            self.spell_num_buttons.append(('back', '', back_r))
            # OK
            ok_r = pygame.Rect(bx+140, by+3*46, 60, 36)
            pygame.draw.rect(self.screen, (70,120,70), ok_r, border_radius=8)
            pygame.draw.rect(self.screen, (150,220,150), ok_r, 1, border_radius=8)
            self.screen.blit(pygame.font.Font(None, 26).render('OK', True, (255,255,255)), (ok_r.x+16, ok_r.y+6))
            self.spell_num_buttons.append(('ok', '', ok_r))
            # Cancel
            cancel_r = pygame.Rect(bx+140, by+4*46, 60, 36)
            pygame.draw.rect(self.screen, (120,70,70), cancel_r, border_radius=8)
            pygame.draw.rect(self.screen, (220,150,150), cancel_r, 1, border_radius=8)
            self.screen.blit(pygame.font.Font(None, 20).render('Отмена', True, (255,255,255)), (cancel_r.x+8, cancel_r.y+10))
            self.spell_num_buttons.append(('cancel', '', cancel_r))
    
    def handle_spell_editor_click(self, pos):
        """Обработка кликов в редакторе заклинаний"""
        # Если открыта панель ввода — обрабатываем только её
        if hasattr(self, 'spell_num_input') and self.spell_num_input and hasattr(self, 'spell_num_buttons'):
            for kind, val, r in self.spell_num_buttons:
                if r.collidepoint(pos):
                    if kind == 'digit':
                        self.spell_num_input['value'] = (self.spell_num_input.get('value','') + val)[:6]
                    elif kind == 'back':
                        self.spell_num_input['value'] = self.spell_num_input.get('value','')[:-1]
                    elif kind == 'ok':
                        try:
                            param = self.spell_num_input.get('param')
                            selected_icon = self._spell_editor_selected
                            self.spell_overrides.setdefault(selected_icon, {})
                            self.spell_overrides[selected_icon][param] = int(self.spell_num_input.get('value') or 0)
                            self._save_spell_overrides()
                        except Exception:
                            pass
                        self.spell_num_input = None
                    elif kind == 'cancel':
                        self.spell_num_input = None
                    return
            # Если открыт ввод и клик вне кнопок — блокируем остальной интерфейс
            return
        
        # Кнопка "Назад"
        if hasattr(self, 'spell_editor_back_rect') and self.spell_editor_back_rect.collidepoint(pos):
            if self.button_click_sound:
                self.button_click_sound.play()
            self.state = 'spellbook_editor'
            self._save_spell_overrides()
            return
        
        # Скролл
        if hasattr(self, 'spell_editor_scroll_up') and self.spell_editor_scroll_up.collidepoint(pos):
            self.spell_editor_scroll = max(0, getattr(self, 'spell_editor_scroll', 0) - 1)
            return
        
        if hasattr(self, 'spell_editor_scroll_down') and self.spell_editor_scroll_down.collidepoint(pos):
            spell_list = self._spells_catalog
            list_h = SCREEN_HEIGHT - 150
            visible_count = max(1, (list_h - 20) // 35)
            max_scroll = max(0, len(spell_list) - visible_count)
            self.spell_editor_scroll = min(max_scroll, getattr(self, 'spell_editor_scroll', 0) + 1)
            return
        
        # Выбор заклинания
        if hasattr(self, 'spell_editor_spell_rects'):
            for rect, spell_icon in self.spell_editor_spell_rects:
                if rect.collidepoint(pos):
                    self._spell_editor_selected = spell_icon
                    self.spell_editor_controls = []
                    return
        
        # Изменение параметров
        if hasattr(self, 'spell_editor_controls') and hasattr(self, '_spell_editor_selected'):
            selected_icon = self._spell_editor_selected
            self.spell_overrides.setdefault(selected_icon, {})
            
            for item in self.spell_editor_controls:
                param = item[0]
                action = item[1]
                rect = item[2]
                
                if rect.collidepoint(pos):
                    if action == 'value':
                        # Двойной клик по значению открывает панель ввода
                        now = pygame.time.get_ticks()
                        last = getattr(self, '_spell_edit_last_click', 0)
                        last_rect = getattr(self, '_spell_edit_last_rect', None)
                        if last_rect == rect and now - last < 450:
                            # Двойной клик - открываем панель ввода
                            spell_data = next((s for s in self._spells_catalog if s['icon'] == selected_icon), None)
                            if spell_data:
                                try:
                                    temp_spell = spell_data['class']()
                                    default_value = getattr(temp_spell, param, 0)
                                except:
                                    default_value = 0
                            else:
                                default_value = 0
                            current = self.spell_overrides[selected_icon].get(param, default_value)
                            self.spell_num_input = {'param': param, 'value': str(current)}
                        self._spell_edit_last_click = now
                        self._spell_edit_last_rect = rect
                        return
                    else:
                        # action == 'minus' или 'plus'
                        delta = item[3]
                        current = self.spell_overrides[selected_icon].get(param, None)
                        if current is None:
                            # Получаем дефолтное значение
                            spell_data = next((s for s in self._spells_catalog if s['icon'] == selected_icon), None)
                            if spell_data:
                                try:
                                    temp_spell = spell_data['class']()
                                    current = getattr(temp_spell, param, 0)
                                except:
                                    current = 0
                        
                        new_value = max(0, current + delta)
                        self.spell_overrides[selected_icon][param] = new_value
                        self._save_spell_overrides()
                        return

    def handle_creative_click(self, pos, button=1):
        # Кнопки
        if self.creative_start_rect.collidepoint(pos):
            if self.button_click_sound:
                self.button_click_sound.play()
            self.start_simulation_from_creative()
            return
        # Скролл списка юнитов
        if hasattr(self, 'creative_scroll_up') and self.creative_scroll_up.collidepoint(pos):
            self.creative_units_scroll = max(0, getattr(self, 'creative_units_scroll', 0) - 1)
            return
        if hasattr(self, 'creative_scroll_down') and self.creative_scroll_down.collidepoint(pos):
            unit_pool = self.creative_units_by_race.get(self.creative_selected_team, []) + self.creative_units_common
            list_top = 0  # не нужен для расчёта
            list_height = SCREEN_HEIGHT - 340  # Обновлено для соответствия с draw_creative
            visible_count = max(1, (list_height - 16) // 30)
            max_scroll = max(0, len(unit_pool) - visible_count)
            self.creative_units_scroll = min(max_scroll, getattr(self, 'creative_units_scroll', 0) + 1)
            return
        if self.creative_back_rect.collidepoint(pos):
            if self.button_click_sound:
                self.button_click_sound.play()
            self.state = 'menu'
            return
        if hasattr(self, 'unit_editor_rect') and self.unit_editor_rect.collidepoint(pos):
            if self.button_click_sound:
                self.button_click_sound.play()
            self.state = 'unit_editor'
            self._unit_editor_selected_race = self.creative_selected_team
            # По умолчанию первый юнит из пула + три класса героя выбранной расы
            pool = list(self.creative_units_by_race.get(self._unit_editor_selected_race, []))
            for hero_class in ['warrior', 'archer', 'mage']:
                pool.append((f"Hero_{self._unit_editor_selected_race}_{hero_class}", Hero))
            self._unit_editor_selected_unit = pool[0][0] if pool else f"Hero_{self._unit_editor_selected_race}_warrior"
            return
        if hasattr(self, 'creative_spellbook_rect') and self.creative_spellbook_rect.collidepoint(pos):
            if self.button_click_sound:
                self.button_click_sound.play()
            # Берём только героев с карты (которые размещены в Creative Mode)
            heroes = [u for u in self.units if isinstance(u, Hero)]
            # Открываем книгу даже без героев (можно редактировать параметры заклинаний)
            self._spellbook_heroes = heroes if heroes else []
            self._spellbook_selected_hero_idx = 0
            self._spellbook_selected_school = 'all'
            self.state = 'spellbook_editor'
            return
        # Выбор команды (первая/вторая)
        if hasattr(self, 'creative_side1_rect') and self.creative_side1_rect.collidepoint(pos):
            self.creative_selected_side = 1
            if self.button_click_sound:
                self.button_click_sound.play()
            return
        if hasattr(self, 'creative_side2_rect') and self.creative_side2_rect.collidepoint(pos):
            self.creative_selected_side = 2
            if self.button_click_sound:
                self.button_click_sound.play()
            return
        # Выбор расы
        for team_key in ['human','elf','undead','demon','dwarf','shadow']:
            r = getattr(self, f'creative_team_rect_{team_key}', None)
            if r and r.collidepoint(pos):
                self.creative_selected_team = team_key
                if self.button_click_sound:
                    self.button_click_sound.play()
                return
        # Скролл рас
        if hasattr(self, 'creative_race_up') and self.creative_race_up.collidepoint(pos):
            self.creative_race_scroll = max(0, getattr(self, 'creative_race_scroll', 0) - 1)
            return
        if hasattr(self, 'creative_race_down') and self.creative_race_down.collidepoint(pos):
            races_len = 6
            race_view_h = 120
            visible_races = max(1, race_view_h // 34)
            max_scroll = max(0, races_len - visible_races)
            self.creative_race_scroll = min(max_scroll, getattr(self, 'creative_race_scroll', 0) + 1)
            return
        # Выпадающий список класса героя больше не используется - все три класса в основном списке
        # Выбор юнита
        if hasattr(self, 'creative_unit_rects'):
            for rect, name in self.creative_unit_rects:
                if rect.collidepoint(pos):
                    self.creative_selected_unit = name
                    if self.button_click_sound:
                        self.button_click_sound.play()
                    return
        # Клик по полю: левая кнопка — поставить, правая — удалить
        gx = pos[0] // CELL_SIZE
        gy = pos[1] // CELL_SIZE
        # Игнорируем клики по панели
        if self.creative_panel_rect.collidepoint(pos):
            return
        # Удаление правой кнопкой
        if button == 3:
            for u in list(self.units):
                if u.x == gx and u.y == gy:
                    self.units.remove(u)
                    if self.button_click_sound:
                        self.button_click_sound.play()
                    break
            return
        # Постановка левой кнопкой
        if button == 1 and 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT and not any(u.x == gx and u.y == gy for u in self.units):
            pool = self.creative_units_by_race.get(self.creative_selected_team, []) + self.creative_units_common
            ctor = next((_cls for name, _cls in pool if name == self.creative_selected_unit), None)
            if ctor:
                # Особый случай героя - класс из имени (Hero_race_class или Hero_class)
                if ctor is Hero:
                    hero_class = 'warrior'  # По умолчанию
                    # Пытаемся извлечь класс из имени
                    if self.creative_selected_unit.startswith('Hero_'):
                        parts = self.creative_selected_unit.split('_')
                        # Формат: Hero_race_class (например, Hero_human_warrior) или Hero_class (например, Hero_warrior)
                        if len(parts) >= 3:
                            # Hero_race_class - берем последнюю часть как класс
                            hero_class = parts[2]
                        elif len(parts) >= 2:
                            # Hero_class - берем вторую часть как класс
                            hero_class = parts[1]
                    unit = Hero(gx, gy, self.creative_selected_team, hero_class=hero_class)
                else:
                    unit = ctor(gx, gy, self.creative_selected_team)
                # Если выбрана первая команда, можно добавлять любых юнитов (независимо от расы героя)
                # Для второй команды используем выбранную расу
                if self.creative_selected_side == 1:
                    # Первая команда - все юниты должны иметь единую команду для правильного расчета морали
                    unit.team = 'player1'
                else:
                    # Вторая команда - используем выбранную расу
                    unit.team = 'player2'
                self._apply_unit_overrides_to_instance(unit)
                # Устанавливаем размер отряда для юнитов
                self._set_default_squad_count(unit)
                if hasattr(unit, 'game_ref'):
                    unit.game_ref = self
                self.units.append(unit)

    def start_simulation_from_creative(self):
        # Подготовка игры на основе размещённых юнитов
        self.state = 'game'
        self.background = self.generate_battlefield()
        # Сброс боевых состояний
        self.game_over = False
        self.victory_state = None
        self.turn_queue = []
        # Применение звуковых настроек из файла настроек
        self._apply_audio_volumes()
        # Найти героев (если есть)
        heroes = [u for u in self.units if isinstance(u, Hero)]
        self.hero1 = next((h for h in heroes if h.team in ['human','elf']), heroes[0] if heroes else None)
        self.hero2 = next((h for h in heroes if h is not self.hero1), None)
        if hasattr(self, 'hero1') and self.hero1:
            self.hero1.game_ref = self
        if hasattr(self, 'hero2') and self.hero2:
            self.hero2.game_ref = self
        # Инициативная очередь
        self.prepare_initiative_queue()

    # ---------------- Unit Editor UI ----------------
    def draw_unit_editor(self):
        self.screen.fill((20, 30, 45))
        title = pygame.font.Font(None, 46).render('Редактор юнитов', True, (240,240,255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        font = pygame.font.Font(None, 28)
        
        # Инициализация переменных если они не установлены
        if not hasattr(self, '_unit_editor_selected_race'):
            self._unit_editor_selected_race = 'human'
        if not hasattr(self, '_unit_editor_selected_unit'):
            pool = list(self.creative_units_by_race.get(self._unit_editor_selected_race, []))
            pool.append((f"Hero_{self._unit_editor_selected_race}", Hero))
            self._unit_editor_selected_unit = pool[0][0] if pool else f"Hero_{self._unit_editor_selected_race}"
        
        # Выбор расы слева
        races = ['human','elf','undead','demon','dwarf','shadow']
        self.unit_editor_race_rects = []
        y = 80
        for r in races:
            rect = pygame.Rect(30, y, 140, 34)
            sel = (self._unit_editor_selected_race == r)
            pygame.draw.rect(self.screen, (70,110,90) if sel else (60,60,80), rect, border_radius=8)
            pygame.draw.rect(self.screen, (200,200,200), rect, 2, border_radius=8)
            label = TEAM_LABELS.get(r, r)
            self.screen.blit(font.render(label, True, (255,255,255)), (rect.x+10, rect.y+6))
            self.unit_editor_race_rects.append((rect, r))
            y += 42
        # Список юнитов по расе (герои уже включены в creative_units_by_race, не добавляем дубликаты)
        self.unit_editor_unit_rects = []
        pool = list(self.creative_units_by_race.get(self._unit_editor_selected_race, []))
        x = 200
        y_start = 80
        # Уменьшаем высоту списка, чтобы не перекрывалась кнопка "Книги заклинаний" (она на SCREEN_HEIGHT - 160)
        list_height = SCREEN_HEIGHT - 320  # Укороченный список для редактора
        
        # Инициализируем скролл для списка юнитов
        if not hasattr(self, '_unit_editor_units_scroll'):
            self._unit_editor_units_scroll = 0
        
        # Вычисляем видимое количество элементов
        visible_count = max(1, list_height // 36)
        max_scroll = max(0, len(pool) - visible_count)
        self._unit_editor_units_scroll = min(self._unit_editor_units_scroll, max_scroll)
        
        # Отрисовываем только видимые элементы
        start_idx = self._unit_editor_units_scroll
        end_idx = min(len(pool), start_idx + visible_count)
        y = y_start
        for idx in range(start_idx, end_idx):
            name, _ = pool[idx]
            rect = pygame.Rect(x, y, 180, 30)
            sel = (self._unit_editor_selected_unit == name)
            pygame.draw.rect(self.screen, (100,120,160) if sel else (50,60,80), rect, border_radius=6)
            pygame.draw.rect(self.screen, (180,180,200), rect, 2, border_radius=6)
            label = name
            if name.startswith('Hero_'):
                parts = name.split('_')
                if len(parts) == 3:  # Hero_race_class
                    race = parts[1]
                    hero_class = parts[2]
                    class_names = {'warrior': 'Воин', 'archer': 'Лучник', 'mage': 'Маг'}
                    class_name = class_names.get(hero_class, hero_class)
                    label = f"{class_name} ({TEAM_LABELS.get(race, race)})"
                else:  # Hero_race
                    race = parts[1]
                    label = f"Герой ({TEAM_LABELS.get(race, race)})"
            self.screen.blit(font.render(label, True, (240,240,255)), (rect.x+8, rect.y+5))
            self.unit_editor_unit_rects.append((rect, name))
            y += 36
        # Параметры справа
        unit_key = self._unit_editor_selected_unit
        # Для Героя показываем геройские параметры, для остальных — общие боевые
        if unit_key == 'Hero' or unit_key.startswith('Hero_'):
            params = ['attack','defense','knowledge','spell_power','max_mana','luck','combat_spirit']
        else:
            params = ['squad_count','health','phys_attack','magic_attack','phys_defense','magic_defense','magic_resist','speed','initiative','attack_range','attack_type']
        x = 420
        y = 80
        overrides = self.unit_overrides.get(unit_key, {})
        # Получаем базовые значения из класса
        base_val = {}
        try:
            unit_cls = None
            for pool in self.creative_units_by_race.values():
                for name, cls in pool:
                    if name == unit_key:
                        unit_cls = cls
                        break
                if unit_cls:
                    break
            if not unit_cls and (unit_key == 'Hero' or unit_key.startswith('Hero_')):
                unit_cls = Hero
            if unit_cls:
                # Для ключа Hero_<race>_<class> подставляем расу и класс
                tmp_team = 'human'
                tmp_class = None
                if unit_key.startswith('Hero_'):
                    parts = unit_key.split('_')
                    if len(parts) >= 2:
                        tmp_team = parts[1]
                    if len(parts) >= 3:
                        tmp_class = parts[2]
                if unit_cls is Hero:
                    tmp = Hero(0, 0, tmp_team, hero_class=tmp_class)
                else:
                    tmp = unit_cls(0, 0, tmp_team)
                base_val = {
                    'squad_count': getattr(tmp, 'squad_count', 1),
                    'health': getattr(tmp, 'health', 0),
                    'max_health': getattr(tmp, 'max_health', 0),
                    'attack': getattr(tmp, 'attack', 0),
                    'defense': getattr(tmp, 'defense', 0),
                    'speed': getattr(tmp, 'speed', 0),
                    'initiative': getattr(tmp, 'initiative', 0),
                    'attack_range': getattr(tmp, 'attack_range', 1) if hasattr(tmp, 'attack_range') else 1,
                    'is_ranged': bool(getattr(tmp, 'is_ranged', False)),
                    # Геройские поля
                    'knowledge': getattr(tmp, 'knowledge', 0),
                    'spell_power': getattr(tmp, 'spell_power', 0),
                    'mana': getattr(tmp, 'mana', 0),
                    'max_mana': getattr(tmp, 'max_mana', 0),
                    'mana_regen': getattr(tmp, 'mana_regen', 0),
                    'hero_class': getattr(tmp, 'hero_class', 'warrior'),
                    'luck': getattr(tmp, 'luck', 0),
                    'combat_spirit': getattr(tmp, 'combat_spirit', 0),
                    # Новые параметры
                    'phys_attack': getattr(tmp, 'phys_attack', 0),
                    'magic_attack': getattr(tmp, 'magic_attack', 0),
                    'phys_defense': getattr(tmp, 'phys_defense', 0),
                    'magic_defense': getattr(tmp, 'magic_defense', 0),
                    'magic_resist': getattr(tmp, 'magic_resist', 0),
                    'attack_type': getattr(tmp, 'attack_type', 'physical'),
                }
        except Exception:
            base_val = {}
        # Инициализируем скролл если его нет
        if not hasattr(self, '_unit_editor_scroll'):
            self._unit_editor_scroll = 0
        
        # Максимальная высота для параметров (до кнопки сохранить)
        max_param_height = SCREEN_HEIGHT - 200
        param_height_per_item = 40
        visible_params = max_param_height // param_height_per_item
        
        # Применяем скролл
        start_idx = self._unit_editor_scroll
        end_idx = min(len(params), start_idx + visible_params)
        visible_params_list = params[start_idx:end_idx]
        
        self.unit_editor_param_controls = []
        param_y = y
        for idx, p in enumerate(visible_params_list):
            pygame.draw.rect(self.screen, (40,50,70), (x, param_y, 340, 36), border_radius=8)
            self.screen.blit(font.render(p, True, (220,220,240)), (x+10, param_y+6))
            if p == 'is_ranged':
                val = bool(overrides.get(p, base_val.get(p, False)))
                rect = pygame.Rect(x+220, param_y+4, 100, 28)
                pygame.draw.rect(self.screen, (90,130,90) if val else (120,80,80), rect, border_radius=8)
                pygame.draw.rect(self.screen, (220,220,220), rect, 2, border_radius=8)
                self.screen.blit(font.render('Да' if val else 'Нет', True, (255,255,255)), (rect.x+30, rect.y+4))
                self.unit_editor_param_controls.append((p, 'toggle', rect))
            elif p == 'attack_type' or p == 'hero_class':
                # Выпадающий список для типа атаки и класса героя
                cur = overrides.get(p, base_val.get(p, 'physical' if p == 'attack_type' else 'warrior'))
                if p == 'attack_type':
                    options = ['physical', 'magical']
                else:  # hero_class
                    options = ['warrior', 'archer', 'mage']
                rect = pygame.Rect(x+220, param_y+4, 100, 28)
                pygame.draw.rect(self.screen, (60,70,90), rect, border_radius=6)
                pygame.draw.rect(self.screen, (180,180,200), rect, 2, border_radius=6)
                display_text = str(cur)[:8]  # Сокращаем длинные значения
                self.screen.blit(font.render(display_text, True, (240,240,255)), (rect.x+6, rect.y+4))
                self.unit_editor_param_controls.append((p, 'cycle', rect, options))
            else:
                minus = pygame.Rect(x+220, param_y+4, 28, 28)
                plus = pygame.Rect(x+330, param_y+4, 28, 28)
                pygame.draw.rect(self.screen, (80,80,120), minus, border_radius=6)
                pygame.draw.rect(self.screen, (80,80,120), plus, border_radius=6)
                self.screen.blit(font.render('-', True, (255,255,255)), (minus.x+7, minus.y+3))
                self.screen.blit(font.render('+', True, (255,255,255)), (plus.x+7, plus.y+3))
                cur = overrides.get(p, base_val.get(p, 0))
                value_rect = pygame.Rect(x+256, param_y+4, 66, 28)
                pygame.draw.rect(self.screen, (30,40,60), value_rect, border_radius=6)
                pygame.draw.rect(self.screen, (120,140,180), value_rect, 1, border_radius=6)
                self.screen.blit(font.render(str(cur), True, (240,240,255)), (value_rect.x+6, value_rect.y+4))
                self.unit_editor_param_controls.append((p, 'step', minus, plus))
                # Для двойного клика по значению — сохранить прямоугольник
                self.unit_editor_param_controls.append((p, 'value', value_rect))
            param_y += 44
        # Кнопки действия
        self.unit_editor_save_rect = pygame.Rect(SCREEN_WIDTH-220, SCREEN_HEIGHT-60, 200, 40)
        self.unit_editor_back_rect = pygame.Rect(20, SCREEN_HEIGHT-60, 180, 40)
        pygame.draw.rect(self.screen, (80,130,80), self.unit_editor_save_rect, border_radius=8)
        pygame.draw.rect(self.screen, (220,240,220), self.unit_editor_save_rect, 2, border_radius=8)
        self.screen.blit(pygame.font.Font(None, 28).render('Сохранить', True, (255,255,255)), (self.unit_editor_save_rect.x+46, self.unit_editor_save_rect.y+8))
        pygame.draw.rect(self.screen, (130,80,80), self.unit_editor_back_rect, border_radius=8)
        pygame.draw.rect(self.screen, (240,220,220), self.unit_editor_back_rect, 2, border_radius=8)
        self.screen.blit(pygame.font.Font(None, 28).render('Назад', True, (255,255,255)), (self.unit_editor_back_rect.x+60, self.unit_editor_back_rect.y+8))
        # Оверлей ввода числа (он-скрин клавиатура), если активен
        if hasattr(self, 'num_input') and self.num_input:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            self.screen.blit(overlay, (0,0))
            box_w, box_h = 260, 300
            box_x = SCREEN_WIDTH//2 - box_w//2
            box_y = SCREEN_HEIGHT//2 - box_h//2
            box = pygame.Rect(box_x, box_y, box_w, box_h)
            pygame.draw.rect(self.screen, (40,50,70), box, border_radius=12)
            pygame.draw.rect(self.screen, (200,200,220), box, 2, border_radius=12)
            lbl = pygame.font.Font(None, 28).render(f"Введите {self.num_input.get('param')}", True, (255,255,255))
            self.screen.blit(lbl, (box_x+20, box_y+12))
            # Поле ввода
            input_rect = pygame.Rect(box_x+20, box_y+44, box_w-40, 36)
            pygame.draw.rect(self.screen, (20,30,50), input_rect, border_radius=8)
            pygame.draw.rect(self.screen, (120,140,180), input_rect, 2, border_radius=8)
            cur_text = str(self.num_input.get('value', ''))
            self.screen.blit(pygame.font.Font(None, 28).render(cur_text, True, (240,240,255)), (input_rect.x+8, input_rect.y+6))
            # Кнопки цифр 0-9, backspace, OK, Cancel
            self.num_buttons = []
            digits = [str(i) for i in range(1,10)] + ['0']
            bx, by = box_x+20, box_y+96
            for idx, d in enumerate(digits):
                r = pygame.Rect(bx + (idx%3)*70, by + (idx//3)*46, 60, 36)
                pygame.draw.rect(self.screen, (70,90,120), r, border_radius=8)
                pygame.draw.rect(self.screen, (180,200,220), r, 1, border_radius=8)
                self.screen.blit(pygame.font.Font(None, 28).render(d, True, (255,255,255)), (r.x+22, r.y+6))
                self.num_buttons.append(('digit', d, r))
            # Backspace
            back_r = pygame.Rect(box_x+20, box_y+96 + 4*46, 90, 36)
            pygame.draw.rect(self.screen, (120,90,90), back_r, border_radius=8)
            self.screen.blit(pygame.font.Font(None, 24).render('Стереть', True, (255,255,255)), (back_r.x+12, back_r.y+7))
            self.num_buttons.append(('back', None, back_r))
            # OK и Отмена
            ok_r = pygame.Rect(box_x+120, box_y+96 + 4*46, 60, 36)
            cancel_r = pygame.Rect(box_x+190, box_y+96 + 4*46, 60, 36)
            pygame.draw.rect(self.screen, (80,120,90), ok_r, border_radius=8)
            pygame.draw.rect(self.screen, (120,80,80), cancel_r, border_radius=8)
            self.screen.blit(pygame.font.Font(None, 24).render('OK', True, (255,255,255)), (ok_r.x+16, ok_r.y+7))
            self.screen.blit(pygame.font.Font(None, 24).render('Отм', True, (255,255,255)), (cancel_r.x+8, cancel_r.y+7))
            self.num_buttons.append(('ok', None, ok_r))
            self.num_buttons.append(('cancel', None, cancel_r))

    def handle_unit_editor_click(self, pos):
        # Если открыта панель ввода — обрабатываем только её (блокируем остальной интерфейс)
        if hasattr(self, 'num_input') and self.num_input and hasattr(self, 'num_buttons'):
            for kind, val, r in self.num_buttons:
                if r.collidepoint(pos):
                    if kind == 'digit':
                        self.num_input['value'] = (self.num_input.get('value','') + val)[:6]
                    elif kind == 'back':
                        self.num_input['value'] = self.num_input.get('value','')[:-1]
                    elif kind == 'ok':
                        try:
                            p = self.num_input.get('param')
                            key = self._unit_editor_selected_unit
                            self.unit_overrides.setdefault(key, {})
                            self.unit_overrides[key][p] = int(self.num_input.get('value') or 0)
                            self._save_unit_overrides()
                            self._apply_overrides_to_all_units()
                        except Exception:
                            pass
                        self.num_input = None
                    elif kind == 'cancel':
                        self.num_input = None
                    return
            # Если открыт ввод и клик вне кнопок — блокируем остальной интерфейс
            return
        
        # Выбор расы
        if hasattr(self, 'unit_editor_race_rects'):
            for rect, r in self.unit_editor_race_rects:
                if rect.collidepoint(pos):
                    self._unit_editor_selected_race = r
                    pool = self.creative_units_by_race.get(r, [])
                    self._unit_editor_selected_unit = pool[0][0] if pool else self._unit_editor_selected_unit
                    return
        # Выбор юнита
        if hasattr(self, 'unit_editor_unit_rects'):
            for rect, name in self.unit_editor_unit_rects:
                if rect.collidepoint(pos):
                    self._unit_editor_selected_unit = name
                    return
        # Параметры
        if hasattr(self, 'unit_editor_param_controls'):
            key = self._unit_editor_selected_unit
            self.unit_overrides.setdefault(key, {})
            for item in self.unit_editor_param_controls:
                if item[1] == 'toggle':
                    p, _, rect = item
                    if rect.collidepoint(pos):
                        cur = bool(self.unit_overrides[key].get(p, False))
                        self.unit_overrides[key][p] = not cur
                        return
                elif item[1] == 'cycle':
                    p, _, rect, options = item
                    if rect.collidepoint(pos):
                        cur = self.unit_overrides[key].get(p, options[0])
                        cur_idx = options.index(cur) if cur in options else 0
                        next_idx = (cur_idx + 1) % len(options)
                        self.unit_overrides[key][p] = options[next_idx]
                        return
                elif item[1] == 'step':
                    p, _, minus, plus = item
                    if minus.collidepoint(pos):
                        cur = int(self.unit_overrides[key].get(p, 0) or 0)
                        self.unit_overrides[key][p] = max(0, cur - 1)
                        return
                    if plus.collidepoint(pos):
                        cur = int(self.unit_overrides[key].get(p, 0) or 0)
                        self.unit_overrides[key][p] = cur + 1
                        return
                elif item[1] == 'value':
                    p, _, value_rect = item
                    if value_rect.collidepoint(pos):
                        now = pygame.time.get_ticks()
                        last = getattr(self, '_unit_edit_last_click', 0)
                        last_rect = getattr(self, '_unit_edit_last_rect', None)
                        if last_rect == value_rect and now - last < 450:
                            # двойной клик — открыть ввод числа
                            current = self.unit_overrides[key].get(p, 0)
                            self.num_input = {'param': p, 'value': str(current)}
                        self._unit_edit_last_click = now
                        self._unit_edit_last_rect = value_rect
                        return
        # Кнопки
        if hasattr(self, 'unit_editor_save_rect') and self.unit_editor_save_rect.collidepoint(pos):
            self._save_unit_overrides()
            # Немедленно применяем изменения к уже размещённым юнитам,
            # чтобы они отражались и в тултипе, и по факту в бою
            self._apply_overrides_to_all_units()
            return
        if hasattr(self, 'unit_editor_back_rect') and self.unit_editor_back_rect.collidepoint(pos):
            self.state = 'creative'
            # Очищаем мертвых юнитов при возврате в креатив
            self.units = [u for u in self.units if u.health > 0]
            return

    def draw_victory_screen(self):
        """Отрисовка заставки победы"""
        # Темный фон с градиентом
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        
        # Золотое сияние в центре
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        for radius in range(100, 10, -10):
            alpha = int(200 * (1 - radius / 100))
            glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 215, 0, alpha), (radius, radius), radius)
            self.screen.blit(glow_surf, (center_x - radius, center_y - radius))
        
        # Текст победы
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("ПОБЕДА!", True, (255, 215, 0))
        title_shadow = title_font.render("ПОБЕДА!", True, (100, 80, 0))
        title_rect = title_text.get_rect(center=(center_x + 2, center_y - 60 + 2))
        self.screen.blit(title_shadow, title_rect)
        title_rect = title_text.get_rect(center=(center_x, center_y - 60))
        self.screen.blit(title_text, title_rect)
        
        # Информация о победителе
        if self.winner_team:
            winner_text = f"Победили: {TEAM_LABELS.get(self.winner_team, self.winner_team)}"
            winner_font = pygame.font.Font(None, 48)
            winner_surf = winner_font.render(winner_text, True, (255, 255, 200))
            winner_rect = winner_surf.get_rect(center=(center_x, center_y + 20))
            self.screen.blit(winner_surf, winner_rect)
        
        # Кнопка возврата в меню
        button_font = pygame.font.Font(None, 36)
        button_text = button_font.render("Нажмите для возврата в меню", True, (200, 200, 200))
        button_rect = button_text.get_rect(center=(center_x, SCREEN_HEIGHT - 80))
        self.screen.blit(button_text, button_rect)
    
    def draw_defeat_screen(self):
        """Отрисовка заставки поражения"""
        # Темный фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        self.screen.blit(overlay, (0, 0))
        
        # Красное свечение
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        for radius in range(100, 10, -10):
            alpha = int(150 * (1 - radius / 100))
            glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (180, 0, 0, alpha), (radius, radius), radius)
            self.screen.blit(glow_surf, (center_x - radius, center_y - radius))
        
        # Текст поражения
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("ПОРАЖЕНИЕ", True, (200, 50, 50))
        title_shadow = title_font.render("ПОРАЖЕНИЕ", True, (80, 0, 0))
        title_rect = title_text.get_rect(center=(center_x + 2, center_y - 60 + 2))
        self.screen.blit(title_shadow, title_rect)
        title_rect = title_text.get_rect(center=(center_x, center_y - 60))
        self.screen.blit(title_text, title_rect)
        
        # Кнопка возврата в меню
        button_font = pygame.font.Font(None, 36)
        button_text = button_font.render("Нажмите для возврата в меню", True, (180, 180, 180))
        button_rect = button_text.get_rect(center=(center_x, SCREEN_HEIGHT - 80))
        self.screen.blit(button_text, button_rect)

    def create_corpse(self, unit):
        """Создает труп из юнита и добавляет его в список трупов."""
        corpse = {
            'x': unit.x,
            'y': unit.y,
            'team': unit.team,
            'unit_type': unit.unit_type,
            'image': unit.image,  # Сохраняем оригинальное изображение
            'max_health': getattr(unit, 'max_health', 100),
            'unit_class': unit.__class__  # Сохраняем класс для воскрешения
        }
        self.corpses.append(corpse)
    
    def kill_unit(self, unit):
        """Убивает юнита, создает труп и удаляет из списков."""
        # Создаем труп
        self.create_corpse(unit)
        # Удаляем из списка юнитов
        if unit in self.units:
            self.units.remove(unit)
        # Удаляем из очереди хода
        if hasattr(self, 'turn_queue'):
            self.turn_queue = [u for u in self.turn_queue if u != unit]
    
    def draw_barriers(self):
        """Отрисовывает магические барьеры."""
        import pygame
        import random
        from .config import CELL_SIZE
        
        for barrier in self.barriers:
            x = barrier['x']
            y = barrier['y']
            barrier_type = barrier.get('type', 'rune_wall')
            
            barrier_rect = pygame.Rect(x * CELL_SIZE + 10, y * CELL_SIZE + 5, 
                                      CELL_SIZE - 20, CELL_SIZE - 10)
            
            # Создаем поверхность для барьера
            barrier_surface = pygame.Surface((CELL_SIZE - 20, CELL_SIZE - 10), pygame.SRCALPHA)
            
            if barrier_type == 'fire_wall':
                # Огненная стена - анимированное пламя
                import time
                t = time.time() * 3  # Скорость анимации
                cx = (CELL_SIZE - 20) // 2
                cy = (CELL_SIZE - 10) // 2
                
                # Основание огня
                flame_height = (CELL_SIZE - 10) - 5
                flame_points = []
                for i in range(8):
                    offset_x = int(math.sin(t * 2 + i * 0.8) * 5) + random.randint(-3, 3)
                    offset_y = cy - i * (flame_height // 8) + int(math.sin(t * 3 + i) * 2)
                    flame_points.append((cx + offset_x, offset_y))
                
                # Рисуем пламя (от яркого внизу к темному вверху)
                for i in range(len(flame_points) - 1):
                    px, py = flame_points[i]
                    next_px, next_py = flame_points[i + 1]
                    # Цвет меняется от желтого/белого внизу к красному вверху
                    intensity = int(255 - i * 30)
                    alpha = 200 - i * 20
                    if intensity < 100:
                        intensity = 100
                    pygame.draw.line(barrier_surface, (255, intensity, 0, alpha), 
                                   (px, py), (next_px, next_py), max(3, 6 - i // 2))
                
                # Яркое ядро огня внизу
                pygame.draw.circle(barrier_surface, (255, 255, 200, 180), (cx, cy), 8)
                pygame.draw.circle(barrier_surface, (255, 200, 0, 150), (cx, cy), 5)
                
                # Искры
                for _ in range(5):
                    spark_x = cx + random.randint(-15, 15)
                    spark_y = cy - random.randint(0, flame_height // 2)
                    spark_size = random.randint(1, 3)
                    spark_alpha = random.randint(100, 200)
                    pygame.draw.circle(barrier_surface, (255, 220, 0, spark_alpha), 
                                     (spark_x, spark_y), spark_size)
            else:
                # Обычный барьер (руна стены) - фиолетовый полупрозрачный барьер
                pygame.draw.rect(barrier_surface, (150, 100, 200, 120), 
                               (0, 0, CELL_SIZE - 20, CELL_SIZE - 10))
                pygame.draw.rect(barrier_surface, (180, 120, 220, 200), 
                               (0, 0, CELL_SIZE - 20, CELL_SIZE - 10), 3)
                
                # Руны на барьере
                cx = (CELL_SIZE - 20) // 2
                cy = (CELL_SIZE - 10) // 2
                rune_size = 10
                pygame.draw.line(barrier_surface, (200, 150, 255, 180), 
                               (cx, cy - rune_size), (cx, cy + rune_size), 2)
                pygame.draw.line(barrier_surface, (200, 150, 255, 180), 
                               (cx - rune_size, cy), (cx + rune_size, cy), 2)
            
            self.screen.blit(barrier_surface, (x * CELL_SIZE + 10, y * CELL_SIZE + 5))
    
    def draw_quicksands(self):
        """Отрисовывает зыбучие пески (только для кастера)"""
        import pygame
        import random
        import time
        import math
        from .config import CELL_SIZE
        
        if not hasattr(self, 'quicksands'):
            return
        
        for quicksand in self.quicksands:
            x = quicksand['x']
            y = quicksand['y']
            caster_team = quicksand.get('caster_team')
            
            # Показываем зыбучие пески только юнитам команды кастера
            # Проверяем, является ли текущий активный юнит из команды кастера
            show_quicksand = False
            if caster_team:
                # Проверяем текущий активный юнит (selected_unit или первый в очереди)
                current_unit = None
                if hasattr(self, 'selected_unit') and self.selected_unit:
                    current_unit = self.selected_unit
                elif hasattr(self, 'turn_queue') and self.turn_queue:
                    current_unit = self.turn_queue[0] if self.turn_queue else None
                
                # Показываем только если текущий активный юнит из команды кастера
                if current_unit and hasattr(current_unit, 'team') and current_unit.team == caster_team:
                    show_quicksand = True
            
            if show_quicksand:
                quicksand_rect = pygame.Rect(x * CELL_SIZE + 10, y * CELL_SIZE + 5, 
                                            CELL_SIZE - 20, CELL_SIZE - 10)
                
                # Создаем поверхность для зыбучих песков
                quicksand_surface = pygame.Surface((CELL_SIZE - 20, CELL_SIZE - 10), pygame.SRCALPHA)
                
                t = time.time() * 2  # Скорость анимации
                cx = (CELL_SIZE - 20) // 2
                cy = (CELL_SIZE - 10) // 2
                
                # Основная лужа (коричневая/грязь) - полупрозрачная, чтобы была видна как подсказка
                pool_size = int((CELL_SIZE - 20) * 0.7)
                pygame.draw.circle(quicksand_surface, (80, 60, 40, 120), (cx, cy), pool_size)
                pygame.draw.circle(quicksand_surface, (100, 75, 50, 100), (cx, cy), int(pool_size * 0.9))
                
                # Бурлящие пузыри
                for bubble_idx in range(6):
                    bubble_angle = (bubble_idx * (2*math.pi / 6.0)) + t
                    bubble_dist = random.randint(5, int(pool_size * 0.6))
                    bubble_x = cx + int(bubble_dist * math.cos(bubble_angle))
                    bubble_y = cy + int(bubble_dist * math.sin(bubble_angle))
                    bubble_size = random.randint(2, 4)
                    pygame.draw.circle(quicksand_surface, (120, 90, 60, 100), (bubble_x, bubble_y), bubble_size)
                
                # Частицы грязи
                for particle_idx in range(8):
                    particle_angle = (particle_idx * (2*math.pi / 8.0)) + t * 2
                    particle_dist = random.randint(int(pool_size * 0.7), int(pool_size * 1.0))
                    particle_x = cx + int(particle_dist * math.cos(particle_angle))
                    particle_y = cy + int(particle_dist * math.sin(particle_angle))
                    particle_size = random.randint(1, 2)
                    particle_alpha = random.randint(60, 90)
                    pygame.draw.circle(quicksand_surface, (90, 70, 45, particle_alpha), (particle_x, particle_y), particle_size)
                
                self.screen.blit(quicksand_surface, (quicksand_rect.x, quicksand_rect.y))
    
    def draw_corpses(self):
        """Отрисовывает трупы как серые полупрозрачные модели."""
        for corpse in self.corpses:
            # Создаем серую копию изображения
            gray_surface = pygame.Surface(corpse['image'].get_size(), pygame.SRCALPHA)
            for x in range(corpse['image'].get_width()):
                for y in range(corpse['image'].get_height()):
                    pixel = corpse['image'].get_at((x, y))
                    if pixel.a > 0:  # Если пиксель не прозрачный
                        # Преобразуем в оттенки серого
                        gray = int(0.299 * pixel.r + 0.587 * pixel.g + 0.114 * pixel.b)
                        gray_surface.set_at((x, y), (gray, gray, gray, 128))  # Полупрозрачность
            # Рисуем серый труп
            self.screen.blit(gray_surface, (corpse['x'] * CELL_SIZE, corpse['y'] * CELL_SIZE))

    def draw(self, hide_unit_at=None):
        """
        Отрисовка игры.
        hide_unit_at: (x, y) координаты юнита, которого НЕ нужно рисовать (для анимаций)
        """
        if self.state == 'menu':
            self.draw_menu()
            pygame.display.flip()
            return
        if self.state == 'creative':
            self.draw_creative()
            pygame.display.flip()
            return
        if self.state == 'settings':
            self.draw_settings()
            pygame.display.flip()
            return
        if self.state == 'unit_editor':
            self.draw_unit_editor()
            pygame.display.flip()
            return
        if self.state == 'spell_editor':
            self.draw_spell_editor()
            pygame.display.flip()
            return
        if self.state == 'spellbook_editor':
            self.draw_spellbook_editor()
            pygame.display.flip()
            return
        if self.state == 'battle_setup':
            self.draw_battle_setup()
            pygame.display.flip()
            return
        # Проверка экрана победы/поражения
        if self.game_over and self.victory_state:
            if self.victory_state == 'victory':
                self.draw_victory_screen()
            elif self.victory_state == 'defeat':
                self.draw_defeat_screen()
            pygame.display.flip()
            return
        self.screen.blit(self.background, (0, 0))
        t = pygame.time.get_ticks() / 1000.0
        draw_animated_grass(self.screen, t)
        self.draw_grid()
        # Отрисовка трупов перед юнитами
        self.draw_corpses()
        # Отрисовка юнитов
        for unit in self.units:
            # Пропускаем отрисовку юнита, если он скрыт
            if hide_unit_at and unit.x == hide_unit_at[0] and unit.y == hide_unit_at[1]:
                continue
            unit.draw(self.screen)
        # Отрисовка барьеров поверх юнитов (особенно для огненной стены)
        self.draw_barriers()
        # Отрисовка зыбучих песков (отдельно от барьеров)
        self.draw_quicksands()
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
                elif hasattr(spell, 'icon') and spell.icon == 'earth_spikes':
                    # Зона креста 5x5: 2 клетки в каждую сторону по горизонтали и вертикали
                    # Горизонталь
                    for dx in [-2, -1, 0, 1, 2]:
                        pygame.draw.rect(preview_surface, (120, 100, 80, 80), 
                                        (cx - CELL_SIZE//2 + dx*CELL_SIZE, cy - CELL_SIZE//2, CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(preview_surface, (150, 130, 100, 120), 
                                        (cx - CELL_SIZE//2 + dx*CELL_SIZE, cy - CELL_SIZE//2, CELL_SIZE, CELL_SIZE), 2)
                    # Вертикаль (не дублируя центр)
                    for dy in [-2, -1, 1, 2]:
                        pygame.draw.rect(preview_surface, (120, 100, 80, 80), 
                                        (cx - CELL_SIZE//2, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(preview_surface, (150, 130, 100, 120), 
                                        (cx - CELL_SIZE//2, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
                elif hasattr(spell, 'icon') and spell.icon == 'rune_wall':
                    # Зона 3 клетки по вертикали
                    for dy in [-1, 0, 1]:
                        pygame.draw.rect(preview_surface, (150, 100, 200, 80), 
                                        (cx - CELL_SIZE//2, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(preview_surface, (180, 120, 220, 120), 
                                        (cx - CELL_SIZE//2, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
                elif hasattr(spell, 'icon') and spell.icon == 'fire_wall':
                    # Зона 3 клетки по вертикали (вверх, текущая, вниз)
                    for dy in [-1, 0, 1]:
                        pygame.draw.rect(preview_surface, (255, 100, 0, 100), 
                                        (cx - CELL_SIZE//2, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(preview_surface, (255, 150, 50, 150), 
                                        (cx - CELL_SIZE//2, cy - CELL_SIZE//2 + dy*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
                elif hasattr(spell, 'icon') and spell.icon == 'meteor_rain':
                    # Preview для метеоритного дождя - показываем целевую клетку (первый метеорит попадет сюда)
                    pygame.draw.circle(preview_surface, (255, 200, 0, 120), (cx, cy), CELL_SIZE//2)
                    pygame.draw.circle(preview_surface, (255, 100, 0, 180), (cx, cy), CELL_SIZE//2, 3)
                    # Показываем что еще 3 метеорита будут случайными
                    hint_text = "4 метеорита (1 здесь, 3 случайных)"
                    hint = pygame.font.Font(None, 18).render(hint_text, True, (255, 200, 100))
                    hint_bg = pygame.Surface((hint.get_width()+10, hint.get_height()+6), pygame.SRCALPHA)
                    hint_bg.fill((0,0,0,160))
                    self.screen.blit(hint_bg, (cx - hint.get_width()//2 - 5, cy - CELL_SIZE - 30))
                    self.screen.blit(hint, (cx - hint.get_width()//2, cy - CELL_SIZE - 27))
                self.screen.blit(preview_surface, (0,0))
                if hasattr(spell, 'icon') and spell.icon == 'frost_ring':
                    hint = pygame.font.Font(None, 20).render('Кольцо холода: зона 3x3 (центр пуст)', True, (220,230,255))
                    hint_bg = pygame.Surface((hint.get_width()+10, hint.get_height()+6), pygame.SRCALPHA)
                    hint_bg.fill((0,0,0,160))
                    self.screen.blit(hint_bg, (cx - hint.get_width()//2 - 5, cy - CELL_SIZE - 24))
                    self.screen.blit(hint, (cx - hint.get_width()//2, cy - CELL_SIZE - 20))
        # --- Отдельный проход для типтулов, чтобы они были поверх ---
        mouse_pos = pygame.mouse.get_pos()
        # Определяем наведённого юнита
        hovered_unit = None
        for unit in self.units:
            if unit.x * CELL_SIZE <= mouse_pos[0] < (unit.x+1)*CELL_SIZE and unit.y * CELL_SIZE <= mouse_pos[1] < (unit.y+1)*CELL_SIZE:
                hovered_unit = unit
                break
        # Старый тултип отключен - теперь используется тултип при зажатии правой кнопки
        # for unit in self.units:
        #     unit.show_tooltip = (unit is hovered_unit)
        # if hovered_unit:
        #     hovered_unit.draw_tooltip(self.screen, mouse_pos)
        self.draw_ui()
        # Отрисовка кастомного курсора для дальнобойных юнитов
        self.draw_custom_ranged_cursor()
        # Отрисовка отладочной информации поверх всего
        self.debugger.draw_debug_overlay(self.screen)
        pygame.display.flip()

    def update(self):
        """Минимальное обновление состояния игры за кадр."""
        if self.state == 'game':
            if self.game_over:
                return
            self.check_game_over()
        self.update_cursor()
        
        # Обработка хода ИИ для обоих игроков
        if (self.state == 'game' and 
            not self.battle_intro_playing and 
            not self.game_over):
            
            # СНАЧАЛА проверяем берсерка - он работает автономно и ДО AI
            # КРИТИЧНО: Используем ту же строгую проверку, что и в next_turn
            is_berserker = False
            if (self.selected_unit and 
                not isinstance(self.selected_unit, Hero) and
                hasattr(self.selected_unit, 'rune_berserker_active') and
                hasattr(self.selected_unit, 'rune_berserker_turns') and
                hasattr(self.selected_unit, 'team')):
                # Проверяем все условия берсерка
                if (getattr(self.selected_unit, 'rune_berserker_active', False) and 
                    getattr(self.selected_unit, 'rune_berserker_turns', 0) > 0 and
                    isinstance(self.selected_unit.team, str) and 
                    self.selected_unit.team.startswith('berserker_')):
                    is_berserker = True
            
            if is_berserker:
                # Берсерк обрабатывается в next_turn, здесь просто пропускаем AI
                # ДОПОЛНИТЕЛЬНО: Сбрасываем таймер AI чтобы не было проблем
                self.ai_think_timer = 0
            else:
                # Определяем какой ИИ контроллер должен сделать ход
                active_ai_controller = None
                if self.selected_unit:
                    # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: Убеждаемся, что юнит НЕ является берсерком
                    # (на случай если он каким-то образом прошел проверку выше)
                    if (not isinstance(self.selected_unit, Hero) and
                        hasattr(self.selected_unit, 'rune_berserker_active') and
                        hasattr(self.selected_unit, 'rune_berserker_turns') and
                        hasattr(self.selected_unit, 'team')):
                        if (getattr(self.selected_unit, 'rune_berserker_active', False) and 
                            getattr(self.selected_unit, 'rune_berserker_turns', 0) > 0 and
                            isinstance(self.selected_unit.team, str) and 
                            self.selected_unit.team.startswith('berserker_')):
                            # Это все-таки берсерк - пропускаем AI
                            self.ai_think_timer = 0
                            active_ai_controller = None
                        elif (self.ai_controller_p1 and self.selected_unit.team == self.ai_controller_p1.ai_team):
                            active_ai_controller = self.ai_controller_p1
                        elif (self.ai_controller_p2 and self.selected_unit.team == self.ai_controller_p2.ai_team):
                            active_ai_controller = self.ai_controller_p2
                    else:
                        # Обычный юнит - проверяем AI контроллеры
                        if (self.ai_controller_p1 and self.selected_unit.team == self.ai_controller_p1.ai_team):
                            active_ai_controller = self.ai_controller_p1
                        elif (self.ai_controller_p2 and self.selected_unit.team == self.ai_controller_p2.ai_team):
                            active_ai_controller = self.ai_controller_p2
                
                if active_ai_controller and active_ai_controller.is_ai_turn():
                    # Увеличиваем таймер
                    if self.ai_think_timer < self.ai_think_delay:
                        self.ai_think_timer += 1
                    else:
                        # Достаточно времени прошло, делаем ход ИИ
                        try:
                            active_ai_controller.make_decision()
                            self.ai_think_timer = 0  # Сброс таймера для следующего хода
                        except Exception as e:
                            print(f"Ошибка ИИ: {e}")
                            # В случае ошибки пропускаем ход
                            if self.selected_unit and self.selected_unit.team == active_ai_controller.ai_team:
                                skip_pos = (self.skip_button_rect.x + self.skip_button_rect.width // 2,
                                           self.skip_button_rect.y + self.skip_button_rect.height // 2)
                                self.handle_click(skip_pos)
                else:
                    # Не ход ИИ, сбрасываем таймер
                    self.ai_think_timer = 0
        
        # Управление фоновой музыкой главного меню
        from pygame import mixer
        if (self.state == 'menu') or (self.state == 'settings' and not self.is_paused):
            if not self.menu_music_playing and os.path.exists(self.menu_music_path):
                try:
                    mixer.music.load(self.menu_music_path)
                    mixer.music.play(-1)  # -1 = бесконечный повтор
                    mixer.music.set_volume(0.0 if self.muted else self.music_volume)
                    self.menu_music_playing = True
                except Exception as e:
                    print(f"Ошибка загрузки музыки меню: {e}")
        else:
            if self.menu_music_playing and not (self.state == 'settings' and not self.is_paused):
                mixer.music.stop()
                self.menu_music_playing = False
        
        # Обновление анимации перелистывания книги
        if self.spellbook_flip_animation:
            self.spellbook_flip_animation['progress'] += 0.15
            if self.spellbook_flip_animation['progress'] >= 1.0:
                self.spellbook_flip_animation = None
        
        # Управление боевой музыкой и звуком начала битвы
        from pygame import mixer
        if self.state == 'game' and not self.game_over:
            # Проверяем, играет ли сейчас intro звук
            if self.battle_intro_playing:
                # Проверяем, закончился ли intro звук (канал не занят или None)
                if self.intro_channel is None:
                    # Канал потерян, считаем что звук закончился
                    self.battle_intro_playing = False
                elif not self.intro_channel.get_busy():
                    # Канал свободен - звук закончился
                    self.battle_intro_playing = False
                
                if not self.battle_intro_playing:
                    # Intro закончился, запускаем основную боевую музыку
                    self.current_intro_sound = None
                    self.intro_channel = None
                    self.current_combat_music = random.choice(self.combat_music_paths)
                    if os.path.exists(self.current_combat_music):
                        try:
                            mixer.music.load(self.current_combat_music)
                            mixer.music.play(-1)  # бесконечный повтор
                            mixer.music.set_volume(0.0 if self.muted else self.music_volume)
                            self.combat_music_playing = True
                        except Exception as e:
                            print(f"Ошибка загрузки боевой музыки: {e}")
            elif not self.combat_music_playing and not self.battle_intro_playing:
                # Начинаем битву - запускаем случайный intro звук
                if self.battle_intro_sounds:
                    self.current_intro_sound = random.choice(self.battle_intro_sounds)
                    if self.current_intro_sound:
                        try:
                            # Устанавливаем громкость intro звука согласно настройкам музыки
                            intro_volume = 0.0 if self.muted else self.music_volume
                            self.current_intro_sound.set_volume(intro_volume)
                            # Ищем свободный канал для intro звука
                            self.intro_channel = self.current_intro_sound.play()
                            if self.intro_channel:
                                self.battle_intro_playing = True
                            else:
                                # Не удалось получить канал, сразу запускаем музыку
                                self.battle_intro_playing = False
                                self.current_combat_music = random.choice(self.combat_music_paths)
                                if os.path.exists(self.current_combat_music):
                                    try:
                                        mixer.music.load(self.current_combat_music)
                                        mixer.music.play(-1)
                                        mixer.music.set_volume(0.0 if self.muted else self.music_volume)
                                        self.combat_music_playing = True
                                    except Exception as e2:
                                        print(f"Ошибка загрузки боевой музыки: {e2}")
                        except Exception as e:
                            print(f"Ошибка воспроизведения intro звука: {e}")
                            self.battle_intro_playing = False
                            # Если intro не запустился, сразу запускаем основную музыку
                            self.current_combat_music = random.choice(self.combat_music_paths)
                            if os.path.exists(self.current_combat_music):
                                try:
                                    mixer.music.load(self.current_combat_music)
                                    mixer.music.play(-1)
                                    mixer.music.set_volume(0.0 if self.muted else self.music_volume)
                                    self.combat_music_playing = True
                                except Exception as e2:
                                    print(f"Ошибка загрузки боевой музыки: {e2}")
                else:
                    # Если нет intro звуков, сразу запускаем основную музыку
                    self.current_combat_music = random.choice(self.combat_music_paths)
                    if os.path.exists(self.current_combat_music):
                        try:
                            mixer.music.load(self.current_combat_music)
                            mixer.music.play(-1)
                            mixer.music.set_volume(0.6)
                            self.combat_music_playing = True
                        except Exception as e:
                            print(f"Ошибка загрузки боевой музыки: {e}")
        elif self.combat_music_playing and (self.game_over or (self.state != 'game' and not (self.state == 'settings' and self.is_paused))):
            mixer.music.stop()
            self.combat_music_playing = False
            # Останавливаем intro звук, если он играет
            if self.battle_intro_playing:
                if self.intro_channel:
                    self.intro_channel.stop()
                elif self.current_intro_sound:
                    self.current_intro_sound.stop()
                self.battle_intro_playing = False
                self.current_intro_sound = None
                self.intro_channel = None

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

    def draw_custom_ranged_cursor(self):
        """Отрисовывает кастомный курсор (сломанная стрела) для дальнобойных юнитов со штрафом"""
        if not hasattr(self, '_ranged_cursor_pos') or not self._ranged_cursor_pos:
            return
        
        if not hasattr(self, '_ranged_cursor_penalty') or not self._ranged_cursor_penalty:
            return
        
        mouse_x, mouse_y = self._ranged_cursor_pos
        penalty_text = self._ranged_cursor_penalty
        
        # Рисуем сломанную стрелу
        # Вычисляем направление стрелы от выбранного юнита к мыши
        if self.selected_unit and hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged():
            start_x = self.selected_unit.x * CELL_SIZE + CELL_SIZE // 2
            start_y = self.selected_unit.y * CELL_SIZE + CELL_SIZE // 2
            dx = mouse_x - start_x
            dy = mouse_y - start_y
            angle = math.atan2(dy, dx)
            
            # Рисуем сломанную стрелу около курсора (смещение чтобы не закрывать цель)
            arrow_len = 20
            arrow_tip_x = mouse_x - int(arrow_len * math.cos(angle))
            arrow_tip_y = mouse_y - int(arrow_len * math.sin(angle))
            
            # Наконечник стрелы (треугольник)
            tip_size = 8
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            # Перпендикулярный вектор для ширины наконечника
            perp_x = -sin_a
            perp_y = cos_a
            
            tip_points = [
                (arrow_tip_x, arrow_tip_y),
                (arrow_tip_x - int(tip_size * cos_a) + int(tip_size * 0.5 * perp_x),
                 arrow_tip_y - int(tip_size * sin_a) + int(tip_size * 0.5 * perp_y)),
                (arrow_tip_x - int(tip_size * cos_a) - int(tip_size * 0.5 * perp_x),
                 arrow_tip_y - int(tip_size * sin_a) - int(tip_size * 0.5 * perp_y))
            ]
            pygame.draw.polygon(self.screen, (200, 150, 100), tip_points)  # Коричневая/сломанная стрела
            
            # Древко стрелы (ломаная линия)
            tail_x = arrow_tip_x - int(arrow_len * cos_a)
            tail_y = arrow_tip_y - int(arrow_len * sin_a)
            mid_x = (arrow_tip_x + tail_x) // 2 + int(3 * perp_x)  # Излом в середине
            mid_y = (arrow_tip_y + tail_y) // 2 + int(3 * perp_y)
            
            pygame.draw.line(self.screen, (150, 100, 60), (arrow_tip_x, arrow_tip_y), (mid_x, mid_y), 3)
            pygame.draw.line(self.screen, (150, 100, 60), (mid_x, mid_y), (tail_x, tail_y), 3)
            
            # Текст штрафа над курсором
            font = pygame.font.Font(None, 24)
            text_surface = font.render(penalty_text, True, (255, 200, 100))
            text_x = mouse_x - text_surface.get_width() // 2
            text_y = mouse_y - 30
            
            # Фон для текста
            bg_surface = pygame.Surface((text_surface.get_width() + 8, text_surface.get_height() + 4), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            self.screen.blit(bg_surface, (text_x - 4, text_y - 2))
            self.screen.blit(text_surface, (text_x, text_y))

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
                        # Сохраняем информацию о дальнобойном юните и штрафе для отрисовки курсора
                        if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged():
                            _, penalty_text = self.selected_unit.get_ranged_damage_multiplier(grid_x, grid_y)
                            self._ranged_cursor_penalty = penalty_text
                            self._ranged_cursor_pos = mouse_pos
                        else:
                            self._ranged_cursor_penalty = None
                            self._ranged_cursor_pos = None
                        self.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Используем обычную стрелку, кастомный курсор отрисуем отдельно
                        return
                except Exception:
                    pass
        # По умолчанию
        self._ranged_cursor_penalty = None
        self._ranged_cursor_pos = None
        self.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def update_morale_and_combat_spirit(self):
        """Обновляет мораль и передает боевой дух от героев к юнитам"""
        from .units import Hero, get_unit_race, calculate_morale, apply_morale_modifiers
        
        # Передаем боевой дух и удачу от героев к юнитам
        heroes = [u for u in self.units if isinstance(u, Hero)]
        for hero in heroes:
            team_units = [u for u in self.units if u.team == hero.team and not isinstance(u, Hero)]
            for unit in team_units:
                # У нежити боевой дух всегда нейтральный (0)
                unit_race = get_unit_race(unit)
                if unit_race == 'undead':
                    unit.combat_spirit = 0
                else:
                    unit.combat_spirit = hero.combat_spirit
                unit.luck = hero.luck
        
        # Обновляем мораль для всех юнитов
        for unit in self.units:
            if not isinstance(unit, Hero):
                # У нежити мораль всегда нейтральная и не изменяется
                unit_race = get_unit_race(unit)
                if unit_race == 'undead':
                    unit.morale = 'neutral'
                else:
                    # Рассчитываем мораль
                    unit.morale = calculate_morale(unit, self.units)
                # Применяем модификаторы морали
                apply_morale_modifiers(unit)

    def prepare_initiative_queue(self):
        """Создаёт очередь ходов на основе инициативы юнитов."""
        # Обновляем мораль и боевой дух перед подготовкой очереди
        self.update_morale_and_combat_spirit()
        
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
        
        # Уменьшаем эффекты в КОНЦЕ хода юнита (перед проверкой боевого духа)
        if finished is not self._round_delimiter and hasattr(finished, 'end_turn_effects'):
            finished.end_turn_effects()
        
        # Проверка дополнительного хода от боевого духа (для обычных юнитов)
        extra_turn = False
        if finished is not self._round_delimiter and not isinstance(finished, Hero):
            combat_spirit = getattr(finished, 'combat_spirit', 0)
            used_combat_spirit = getattr(finished, 'used_combat_spirit_this_round', False)
            # Проверяем боевой дух только если юнит еще не использовал его в этом раунде
            if combat_spirit > 0 and not used_combat_spirit:
                # Шанс дополнительного хода: 3% за поинт (максимум 18% при боевом духе 6)
                chance = min(combat_spirit * 3, 100)  # Ограничиваем максимум 100%
                if random.randint(1, 100) <= chance:
                    extra_turn = True
                    # Отмечаем, что юнит использовал боевой дух в этом раунде
                    finished.used_combat_spirit_this_round = True
                    # Анимация золотой птицы
                    from .graphics import animate_combat_spirit_bird
                    unit_pos = (finished.x * CELL_SIZE + CELL_SIZE // 2, 
                               finished.y * CELL_SIZE + CELL_SIZE // 2)
                    animate_combat_spirit_bird(self.screen, unit_pos, redraw_callback=self.draw)
                    self.add_event(f"Боевой дух! {finished.unit_type.capitalize()} получает дополнительный ход!")
                    # Вставляем юнита в начало очереди для немедленного дополнительного хода
                    self.turn_queue.insert(0, finished)
                    # Сбрасываем флаги действий для дополнительного хода
                    finished.has_moved = False
                    finished.has_attacked = False
                    finished.move_points_left = finished.speed
                    # Сразу делаем юнита активным для дополнительного хода
                    self.selected_unit = finished
                    # Прерываем выполнение next_turn, чтобы юнит сразу начал дополнительный ход
                    return
        
        # Обрабатываем фантомов - уменьшаем время существования и удаляем при истечении
        if finished is not self._round_delimiter and hasattr(finished, 'is_phantom') and finished.is_phantom:
            if hasattr(finished, 'phantom_turns') and finished.phantom_turns > 0:
                finished.phantom_turns -= 1
                if finished.phantom_turns <= 0:
                    # Фантом исчезает
                    self.kill_unit(finished)
                    self.animation_manager.animate_queue_fade(finished)
                    if hasattr(self, 'add_event'):
                        self.add_event(f"Фантом {finished.unit_type} исчез")
        
        # Реген маны героям при окончании хода, если не кастовали в этот ход
        if isinstance(finished, Hero):
            if not getattr(finished, 'used_spell_this_round', False):
                regen = max(1, int(getattr(finished, 'knowledge', 0) * 0.5))
                finished.mana = min(finished.max_mana, finished.mana + regen)
        if finished is self._round_delimiter:
            # Начало нового раунда
            self.round_number += 1
            # Логируем начало раунда
            if hasattr(self, 'anim_logger'):
                self.anim_logger.log_round_start(self.round_number)
            
            for unit in self.units:
                # сбрасываем ожидание в новом раунде
                if hasattr(unit, 'has_waited'):
                    unit.has_waited = False
                # сбрасываем контратаку в новом раунде
                if hasattr(unit, 'has_counterattacked'):
                    unit.has_counterattacked = False
                # сбрасываем флаг использования боевого духа в новом раунде
                if hasattr(unit, 'used_combat_spirit_this_round'):
                    unit.used_combat_spirit_this_round = False
                
                # Сброс флага защиты (бонус действует только 1 раунд)
                if not isinstance(unit, Hero) and getattr(unit, '_defend_this_round', False):
                    # Логируем сброс защиты ДО изменений
                    if hasattr(self, 'anim_logger'):
                        old_phys = getattr(unit, 'phys_defense', 0)
                        old_mag = getattr(unit, 'magic_defense', 0)
                        old_res = getattr(unit, 'magic_resist', 0)
                    
                    # Восстанавливаем оригинальные значения (если они были сохранены)
                    if hasattr(unit, '_original_phys_defense'):
                        unit.phys_defense = unit._original_phys_defense
                        delattr(unit, '_original_phys_defense')
                    elif hasattr(unit, 'phys_defense'):
                        unit.phys_defense = int(unit.phys_defense / 1.2)
                    
                    if hasattr(unit, '_original_magic_defense'):
                        unit.magic_defense = unit._original_magic_defense
                        delattr(unit, '_original_magic_defense')
                    elif hasattr(unit, 'magic_defense'):
                        unit.magic_defense = int(unit.magic_defense / 1.2)
                    
                    if hasattr(unit, '_original_magic_resist'):
                        unit.magic_resist = unit._original_magic_resist
                        delattr(unit, '_original_magic_resist')
                    elif hasattr(unit, 'magic_resist'):
                        unit.magic_resist = int(unit.magic_resist / 1.2)
                    
                    unit._defend_this_round = False
                    
                    # Логируем результат сброса ПОСЛЕ изменений
                    if hasattr(self, 'anim_logger'):
                        details = f"{unit.unit_type}: Физ.защ {old_phys}->{getattr(unit, 'phys_defense', 0)}, Маг.защ {old_mag}->{getattr(unit, 'magic_defense', 0)}, Сопр.маг {old_res}->{getattr(unit, 'magic_resist', 0)}"
                        self.anim_logger.log("DEFENSE_RESET", details)
            # Обрабатываем барьеры: уменьшаем длительность
            if hasattr(self, 'barriers'):
                barriers_to_remove = []
                for barrier in self.barriers:
                    barrier['turns'] -= 1
                    if barrier['turns'] <= 0:
                        barriers_to_remove.append(barrier)
                for barrier in barriers_to_remove:
                    self.barriers.remove(barrier)
                    self.add_event(f"Барьер рассеялся ({barrier['x']}, {barrier['y']})")
            
            # Уменьшаем срок действия зыбучих песков
            if hasattr(self, 'quicksands'):
                quicksands_to_remove = []
                for quicksand in self.quicksands:
                    quicksand['turns'] -= 1
                    if quicksand['turns'] <= 0:
                        quicksands_to_remove.append(quicksand)
                # Удаляем зыбучие пески и сбрасываем флаг у юнитов, которые были застрявшими
                for quicksand in quicksands_to_remove:
                    # Сбрасываем флаг у всех юнитов, которые были на этой клетке
                    for unit in self.units:
                        if hasattr(unit, 'stuck_in_quicksand') and unit.stuck_in_quicksand:
                            if unit.x == quicksand['x'] and unit.y == quicksand['y']:
                                unit.stuck_in_quicksand = False
                    self.quicksands.remove(quicksand)
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
            # Логируем начало раунда
            if hasattr(self, 'anim_logger'):
                self.anim_logger.log_round_start(self.round_number)
            
            for unit in self.units:
                if hasattr(unit, 'has_waited'):
                    unit.has_waited = False
                # При начале нового раунда - удаляем сохраненные ОД от предыдущего раунда
                # и даем всем полные ОД (новый раунд = полный сброс)
                if not isinstance(unit, Hero):
                    # Удаляем сохраненные ОД если были (они были от предыдущего раунда)
                    if hasattr(unit, '_saved_move_points'):
                        delattr(unit, '_saved_move_points')
                    # Даем полные ОД всем юнитам в новом раунде
                    unit.move_points_left = unit.speed
                
                # Сброс флага защиты (бонус действует только 1 раунд)
                if not isinstance(unit, Hero) and getattr(unit, '_defend_this_round', False):
                    # Логируем сброс защиты ДО изменений
                    if hasattr(self, 'anim_logger'):
                        old_phys = getattr(unit, 'phys_defense', 0)
                        old_mag = getattr(unit, 'magic_defense', 0)
                        old_res = getattr(unit, 'magic_resist', 0)
                    
                    # Восстанавливаем оригинальные значения (если они были сохранены)
                    if hasattr(unit, '_original_phys_defense'):
                        unit.phys_defense = unit._original_phys_defense
                        delattr(unit, '_original_phys_defense')
                    elif hasattr(unit, 'phys_defense'):
                        unit.phys_defense = int(unit.phys_defense / 1.2)
                    
                    if hasattr(unit, '_original_magic_defense'):
                        unit.magic_defense = unit._original_magic_defense
                        delattr(unit, '_original_magic_defense')
                    elif hasattr(unit, 'magic_defense'):
                        unit.magic_defense = int(unit.magic_defense / 1.2)
                    
                    if hasattr(unit, '_original_magic_resist'):
                        unit.magic_resist = unit._original_magic_resist
                        delattr(unit, '_original_magic_resist')
                    elif hasattr(unit, 'magic_resist'):
                        unit.magic_resist = int(unit.magic_resist / 1.2)
                    
                    unit._defend_this_round = False
                    
                    # Логируем результат сброса ПОСЛЕ изменений
                    if hasattr(self, 'anim_logger'):
                        details = f"{unit.unit_type}: Физ.защ {old_phys}->{getattr(unit, 'phys_defense', 0)}, Маг.защ {old_mag}->{getattr(unit, 'magic_defense', 0)}, Сопр.маг {old_res}->{getattr(unit, 'magic_resist', 0)}"
                        self.anim_logger.log("DEFENSE_RESET", details)
        if self.turn_queue:
            self.selected_unit = self.turn_queue[0]
            # КРИТИЧНО: Проверяем, что следующий юнит НЕ является берсерком (если он не должен быть)
            # Если это не берсерк, но он имеет флаги берсерка - это ошибка, сбрасываем их
            if (self.selected_unit and 
                not isinstance(self.selected_unit, Hero) and
                hasattr(self.selected_unit, 'team')):
                # Проверяем наличие атрибутов берсерка
                has_berserker_attrs = (hasattr(self.selected_unit, 'rune_berserker_active') and
                                      hasattr(self.selected_unit, 'rune_berserker_turns'))
                
                if has_berserker_attrs:
                    # Проверяем, действительно ли это берсерк
                    is_berserker = (getattr(self.selected_unit, 'rune_berserker_active', False) and 
                                   getattr(self.selected_unit, 'rune_berserker_turns', 0) > 0 and
                                   isinstance(self.selected_unit.team, str) and 
                                   self.selected_unit.team.startswith('berserker_'))
                    
                    # Если это НЕ берсерк, но команда начинается с berserker_ - это ошибка, исправляем
                    if not is_berserker and isinstance(self.selected_unit.team, str) and self.selected_unit.team.startswith('berserker_'):
                        # Ошибка: юнит имеет команду берсерка, но не является берсерком
                        # Восстанавливаем оригинальную команду если она была сохранена
                        if hasattr(self.selected_unit, 'rune_berserker_original_team'):
                            self.selected_unit.team = self.selected_unit.rune_berserker_original_team
                            self.add_event(f"ИСПРАВЛЕНО: {self.selected_unit.unit_type.capitalize()} имел неправильную команду берсерка")
                        else:
                            # Если оригинальная команда не сохранена, пытаемся определить её по умолчанию
                            # Это не должно произойти, но на всякий случай
                            if hasattr(self.selected_unit, 'game_ref') and self.selected_unit.game_ref:
                                # Пытаемся определить команду по другим юнитам той же расы
                                for unit in self.units:
                                    if (unit.unit_type == self.selected_unit.unit_type and 
                                        unit != self.selected_unit and
                                        not isinstance(unit, Hero) and
                                        not (hasattr(unit, 'team') and isinstance(unit.team, str) and unit.team.startswith('berserker_'))):
                                        self.selected_unit.team = unit.team
                                        break
            # Сначала сбрасываем флаги действий в НАЧАЛЕ хода юнита
            if hasattr(self.selected_unit, 'reset_turn'):
                self.selected_unit.reset_turn()
            # ПОСЛЕ reset_turn восстанавливаем сохраненные ОД если юнит ожидал (только для не-героев)
            if not isinstance(self.selected_unit, Hero):
                if hasattr(self.selected_unit, '_saved_move_points'):
                    # Юнит ожидал - присваиваем конкретно те ОД, которые были сохранены при нажатии ожидания
                    saved_points = self.selected_unit._saved_move_points
                    self.selected_unit.move_points_left = saved_points  # Конкретное присваивание
                    delattr(self.selected_unit, '_saved_move_points')
                    # Сбрасываем флаг ожидания после восстановления ОД
                    if hasattr(self.selected_unit, 'has_waited'):
                        self.selected_unit.has_waited = False
                elif hasattr(self.selected_unit, 'has_waited') and self.selected_unit.has_waited:
                    # Юнит ожидал, но сохраненные ОД уже были использованы - не восстанавливаем полные ОД
                    # Оставляем текущие ОД (которые могли быть потрачены)
                    if not hasattr(self.selected_unit, 'move_points_left') or self.selected_unit.move_points_left <= 0:
                        # Если ОД уже полностью потрачены, оставляем 0
                        self.selected_unit.move_points_left = 0
                    # Сбрасываем флаг ожидания
                    self.selected_unit.has_waited = False
            # Проверяем огненную стену в начале хода юнита (не раунда)
            if hasattr(self, 'barriers') and not isinstance(self.selected_unit, Hero):
                for barrier in self.barriers:
                    if barrier['x'] == self.selected_unit.x and barrier['y'] == self.selected_unit.y and barrier.get('type') == 'fire_wall':
                        # Наносим урон от огненной стены
                        damage = barrier.get('damage', 15)
                        spell_power = barrier.get('spell_power', 0)
                        spell_power_multiplier = barrier.get('spell_power_multiplier', 3)
                        total_damage = damage + spell_power * spell_power_multiplier
                        
                        health_before = self.selected_unit.health
                        squad_count_before = getattr(self.selected_unit, 'squad_count', 1)
                        unit_died = self.selected_unit.take_damage(total_damage, attack_type='magical')
                        actual_damage = health_before - self.selected_unit.health
                        squad_count_after = getattr(self.selected_unit, 'squad_count', 1)
                        units_lost = squad_count_before - squad_count_after
                        
                        if unit_died:
                            self.kill_unit(self.selected_unit)
                            self.animation_manager.animate_queue_fade(self.selected_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} сгорел в огненной стене в начале хода (урон: {actual_damage})"
                            if units_lost > 0:
                                event_msg += f", уничтожено {units_lost} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                            # Переходим к следующему ходу если юнит умер
                            if self.selected_unit not in self.units:
                                self.next_turn()
                                return
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} обжегся в огненной стене в начале хода (урон: {actual_damage})"
                            if units_lost > 0:
                                event_msg += f", потеряно {units_lost} юнитов из отряда"
                            self.add_event(event_msg)
                        break  # Один барьер на клетку
            # Проверяем, пропустил ли юнит ход из-за забвения
            # Двойная проверка: и флаг, и сам эффект (на случай если снятие чар было применено)
            if (hasattr(self.selected_unit, 'skipped_turn_due_to_forget') and 
                self.selected_unit.skipped_turn_due_to_forget and 
                getattr(self.selected_unit, 'forget_turns', 0) > 0):
                self.selected_unit.skipped_turn_due_to_forget = False
                # Показываем анимацию забвения
                unit_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                animate_forget_spell(self.screen, unit_pos, unit_pos, redraw_callback=self.draw)
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} пропускает ход из-за забвения")
                # Автоматически переходим к следующему юниту
                pygame.time.delay(500)  # Задержка чтобы игрок увидел анимацию
                self.next_turn()
                return
            
            # Автономный бот для берсерка - атакует ближайшего любого юнита (РАБОТАЕТ ДО AI)
            # ВАЖНО: Проверяем, что это действительно берсерк, а не просто следующий юнит в очереди
            # Также проверяем, что команда юнита соответствует берсерку (уникальная команда)
            # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: убеждаемся что это не герой и что юнит действительно под эффектом
            # КРИТИЧНО: Проверяем ВСЕ условия вместе, чтобы исключить ложные срабатывания
            is_berserker = False
            if (self.selected_unit and 
                not isinstance(self.selected_unit, Hero) and
                hasattr(self.selected_unit, 'rune_berserker_active') and
                hasattr(self.selected_unit, 'rune_berserker_turns') and
                hasattr(self.selected_unit, 'team')):
                # Проверяем все условия берсерка
                if (getattr(self.selected_unit, 'rune_berserker_active', False) and 
                    getattr(self.selected_unit, 'rune_berserker_turns', 0) > 0 and
                    isinstance(self.selected_unit.team, str) and 
                    self.selected_unit.team.startswith('berserker_')):
                    is_berserker = True
            
            if is_berserker:
                # Берсерк работает независимо - продолжаем атаковать/двигаться пока есть возможности
                max_actions = 50  # Защита от бесконечного цикла
                action_count = 0
                
                while action_count < max_actions:
                    action_count += 1
                    
                    # Находим ближайшего юнита (любого, кроме самого себя и героев)
                    nearest_unit = None
                    nearest_distance = float('inf')
                    for unit in self.units:
                        if unit != self.selected_unit and unit.health > 0 and not isinstance(unit, Hero):
                            distance = abs(self.selected_unit.x - unit.x) + abs(self.selected_unit.y - unit.y)
                            if distance < nearest_distance:
                                nearest_distance = distance
                                nearest_unit = unit
                    
                    if not nearest_unit:
                        # Нет целей - пропускаем ход
                        self.add_event(f"{self.selected_unit.unit_type.capitalize()} (берсерк) не нашел целей")
                        self.next_turn()
                        return
                    
                    # Проверяем, можем ли атаковать
                    if not self.selected_unit.has_attacked and self.selected_unit.can_attack(nearest_unit.x, nearest_unit.y, self.units):
                        # Атакуем ближайшего юнита
                        self.handle_click((nearest_unit.x * CELL_SIZE + CELL_SIZE//2, nearest_unit.y * CELL_SIZE + CELL_SIZE//2), is_ai_action=True)
                        # После атаки проверяем, можем ли еще атаковать или двигаться
                        if self.selected_unit.has_attacked and self.selected_unit.move_points_left <= 0:
                            # Ход завершен
                            self.next_turn()
                            return
                        # Продолжаем цикл для следующей атаки/движения
                        continue
                    
                    # Если не можем атаковать, пытаемся двигаться
                    if self.selected_unit.move_points_left > 0:
                        target_x, target_y = nearest_unit.x, nearest_unit.y
                        # Простой путь - двигаемся в направлении цели
                        dx = 1 if target_x > self.selected_unit.x else -1 if target_x < self.selected_unit.x else 0
                        dy = 1 if target_y > self.selected_unit.y else -1 if target_y < self.selected_unit.y else 0
                        
                        # Пробуем двигаться по X или Y
                        new_x, new_y = self.selected_unit.x, self.selected_unit.y
                        moved = False
                        if dx != 0 and self.selected_unit.can_move(self.selected_unit.x + dx, self.selected_unit.y, self.units, self.barriers):
                            new_x = self.selected_unit.x + dx
                            moved = True
                        elif dy != 0 and self.selected_unit.can_move(self.selected_unit.x, self.selected_unit.y + dy, self.units, self.barriers):
                            new_y = self.selected_unit.y + dy
                            moved = True
                        
                        if moved:
                            path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, new_x, new_y)
                            if path_len <= self.selected_unit.move_points_left:
                                self.animate_unit_move(self.selected_unit, new_x, new_y)
                                self.selected_unit.move_points_left -= path_len
                                self.add_event(f"{self.selected_unit.unit_type.capitalize()} (берсерк) движется к цели")
                                # После движения проверяем, можем ли атаковать
                                if not self.selected_unit.has_attacked and self.selected_unit.can_attack(nearest_unit.x, nearest_unit.y, self.units):
                                    # Атакуем сразу после движения
                                    self.handle_click((nearest_unit.x * CELL_SIZE + CELL_SIZE//2, nearest_unit.y * CELL_SIZE + CELL_SIZE//2), is_ai_action=True)
                                    if self.selected_unit.has_attacked and self.selected_unit.move_points_left <= 0:
                                        # Ход завершен
                                        self.next_turn()
                                        return
                                    # Продолжаем цикл
                                    continue
                        else:
                            # Не можем двигаться - пропускаем ход
                            self.add_event(f"{self.selected_unit.unit_type.capitalize()} (берсерк) не может добраться до цели")
                            self.next_turn()
                            return
                    else:
                        # Нет очков движения и не можем атаковать - ход завершен
                        if self.selected_unit.has_attacked:
                            self.next_turn()
                            return
                        else:
                            # Не можем ни атаковать, ни двигаться - пропускаем ход
                            self.add_event(f"{self.selected_unit.unit_type.capitalize()} (берсерк) не может добраться до цели")
                            self.next_turn()
                            return
                
                # Если вышли из цикла (защита от бесконечного цикла)
                # Явно завершаем ход берсерка и переходим к следующему
                self.add_event(f"{self.selected_unit.unit_type.capitalize()} (берсерк) завершил ход")
                # Сохраняем ссылку на текущего берсерка для проверки
                berserker_unit = self.selected_unit
                # Сбрасываем флаги движения перед переходом к следующему юниту
                if hasattr(berserker_unit, 'has_moved'):
                    berserker_unit.has_moved = True  # Берсерк завершил движение
                if hasattr(berserker_unit, 'has_attacked'):
                    berserker_unit.has_attacked = True  # Берсерк завершил атаку
                self.next_turn()
                # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: Убеждаемся, что следующий юнит НЕ является берсерком
                # Если следующий юнит - это тот же берсерк, это ошибка, пропускаем его
                if (self.selected_unit and 
                    self.selected_unit == berserker_unit and
                    hasattr(self.selected_unit, 'rune_berserker_active') and
                    getattr(self.selected_unit, 'rune_berserker_active', False)):
                    # Следующий юнит все еще берсерк - это ошибка, пропускаем ход
                    self.add_event(f"ОШИБКА: Следующий юнит все еще берсерк, пропускаем")
                    self.next_turn()
                # Убеждаемся, что следующий юнит не имеет остаточных состояний движения
                if self.selected_unit and self.selected_unit != berserker_unit:
                    # Сбрасываем любые остаточные флаги движения у следующего юнита
                    if hasattr(self.selected_unit, 'has_moved') and not isinstance(self.selected_unit, Hero):
                        # Не сбрасываем has_moved для следующего юнита - он еще не ходил
                        pass
                return

    def calculate_damage_with_rune_magic(self, attacker, target, is_ranged=False, target_x=None, target_y=None):
        """Вычисляет урон с учетом руны магии (смешанный физ+маг урон).
        Возвращает кортеж (phys_damage, magic_damage) для применения через take_damage дважды.
        Использует тот же метод расчета, что и get_current_attack/ranged_damage, но разделяет на физический и магический компоненты.
        
        :param is_ranged: True для дальнобойных атак (нужно учитывать множитель дальности)
        :param target_x, target_y: Координаты цели (для расчета множителя дальности)
        """
        if getattr(attacker, 'rune_magic_turns', 0) > 0:
            # Базовые значения атаки
            base_phys = attacker.phys_attack
            base_magic = getattr(attacker, 'magic_attack', 0)
            
            # Применяем ослепление
            if getattr(attacker, 'blindness_active', False):
                base_phys = int(base_phys * 0.65)
                base_magic = int(base_magic * 0.65)
            
            # Применяем баффы/дебаффы
            if attacker.attack_buff_turns > 0:
                base_phys = int(base_phys * 1.25)
                base_magic = int(base_magic * 1.25)
            if attacker.attack_debuff_turns > 0:
                base_phys = int(base_phys * 0.75)
                base_magic = int(base_magic * 0.75)
            
            # Умножаем на количество юнитов в отряде (как в get_current_attack)
            squad_count = getattr(attacker, 'squad_count', 1)
            if squad_count < 1:
                squad_count = 1
            
            phys_damage = base_phys * squad_count
            magic_damage = base_magic * squad_count
            
            # Для дальнобойных атак учитываем множитель дальности и точность
            if is_ranged and target_x is not None and target_y is not None:
                # Получаем множитель дальности (как в ranged_damage)
                damage_multiplier, _ = attacker.get_ranged_damage_multiplier(target_x, target_y)
                
                # Применяем множитель дальности к обоим типам урона
                phys_damage = int(phys_damage * damage_multiplier)
                magic_damage = int(magic_damage * damage_multiplier)
                
                # Если есть эффект точности - добавляем бонус 20%
                has_accuracy = getattr(attacker, 'accuracy_active', False) and getattr(attacker, 'accuracy_turns', 0) > 0
                if has_accuracy:
                    phys_damage = int(phys_damage * 1.2)
                    magic_damage = int(magic_damage * 1.2)
            
            # Гарантируем минимум 1 урон
            phys_damage = max(1, phys_damage)
            magic_damage = max(0, magic_damage)  # Магический урон может быть 0
            
            # Применяем удачу (шанс двойного урона = luck * 5%)
            luck = getattr(attacker, 'luck', 0)
            if luck > 0:
                import random
                luck_chance = luck * 5  # Шанс в процентах
                if random.randint(1, 100) <= luck_chance:
                    phys_damage *= 2
                    magic_damage *= 2
                    if hasattr(self, 'add_event'):
                        self.add_event(f"Удача! {attacker.unit_type.capitalize()} наносит двойной урон!")
                    # Анимация подковы над атакующим юнитом
                    attacker_pos = (attacker.x * CELL_SIZE + CELL_SIZE//2, attacker.y * CELL_SIZE + CELL_SIZE//2)
                    animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
            
            # Возвращаем оба урона отдельно - они будут применены через take_damage
            # take_damage сам учтет защиту и сопротивление магии
            return (phys_damage, magic_damage)
        else:
            # Обычный урон
            return None

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

    def animate_unit_move(self, unit, dest_x, dest_y):
        """Пошаговая анимация перемещения по манхэттен-пути (без диагоналей)."""
        # Строим простой путь: сначала по X, затем по Y
        path = []
        cx, cy = unit.x, unit.y
        step_x = 1 if dest_x > cx else -1
        while cx != dest_x:
            cx += step_x
            path.append((cx, cy))
        step_y = 1 if dest_y > cy else -1
        while cy != dest_y:
            cy += step_y
            path.append((cx, cy))
        # Проигрываем шаги
        for px, py in path:
            # Проверяем, есть ли зыбучие пески на новой клетке
            quicksand_trap = None
            if hasattr(self, 'quicksands'):
                for quicksand in self.quicksands:
                    if quicksand['x'] == px and quicksand['y'] == py:
                        quicksand_trap = quicksand
                        break
            
            if quicksand_trap:
                # Юнит принудительно пропускает ход при наступлении на зыбучие пески
                unit.move_points_left = 0
                unit.has_moved = True
                unit.has_attacked = True  # Принудительно пропускаем ход
                
                # Прерываем движение - устанавливаем позицию юнита
                unit.x = px
                unit.y = py
                
                # Устанавливаем флаг, что юнит застрял в зыбучих песках
                # Юнит будет застрявшим, пока зыбучие пески не исчезнут
                unit.stuck_in_quicksand = True
                
                # Показываем анимацию бурлящей лужи ПОСЛЕ того как юнит наступил
                try:
                    from .graphics import animate_quicksand_trigger
                    from .config import CELL_SIZE
                    trigger_px = (px * CELL_SIZE + CELL_SIZE // 2, py * CELL_SIZE + CELL_SIZE // 2)
                    animate_quicksand_trigger(self.screen, trigger_px, redraw_callback=self.draw)
                except Exception as e:
                    print(f"Ошибка анимации зыбучих песков при наступлении: {e}")
                
                self.add_event(f"{unit.unit_type.capitalize()} попал в зыбучие пески и застрял!")
                
                # НЕ удаляем зыбучие пески сразу - они будут удалены когда turns закончатся
                # Это позволит юниту оставаться застрявшим
                
                return
            
            # Проверяем, есть ли огненная стена на новой клетке
            for barrier in self.barriers:
                if barrier['x'] == px and barrier['y'] == py and barrier.get('type') == 'fire_wall':
                    # Наносим урон при прохождении через огненную стену
                    damage = barrier.get('damage', 15)
                    spell_power = barrier.get('spell_power', 0)
                    spell_power_multiplier = barrier.get('spell_power_multiplier', 3)
                    total_damage = damage + spell_power * spell_power_multiplier
                    
                    health_before = unit.health
                    squad_count_before = getattr(unit, 'squad_count', 1)
                    unit_died = unit.take_damage(total_damage, attack_type='magical')
                    actual_damage = health_before - unit.health
                    squad_count_after = getattr(unit, 'squad_count', 1)
                    units_lost = squad_count_before - squad_count_after
                    
                    if unit_died:
                        self.kill_unit(unit)
                        self.animation_manager.animate_queue_fade(unit)
                        event_msg = f"{unit.unit_type.capitalize()} сгорел в огненной стене (урон: {actual_damage})"
                        if units_lost > 0:
                            event_msg += f", уничтожено {units_lost} юнитов из отряда"
                        self.add_event(event_msg)
                        self.check_game_over()
                        return  # Юнит погиб, движение прервано
                    else:
                        event_msg = f"{unit.unit_type.capitalize()} обжегся в огненной стене (урон: {actual_damage})"
                        if units_lost > 0:
                            event_msg += f", потеряно {units_lost} юнитов из отряда"
                        self.add_event(event_msg)
                    
                    # Визуальный эффект - вспышка огня
                    try:
                        from .config import CELL_SIZE
                        for flash in range(5):
                            self.draw()
                            flash_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                            alpha = int(200 * (1 - flash / 5))
                            pygame.draw.rect(flash_surface, (255, 100, 0, alpha), 
                                           (0, 0, CELL_SIZE, CELL_SIZE))
                            self.screen.blit(flash_surface, (px * CELL_SIZE, py * CELL_SIZE))
                            pygame.display.flip()
                            pygame.time.delay(30)
                    except Exception:
                        pass
                    break  # Урон применен один раз за проход
            
            unit.x, unit.y = px, py
            self.draw()
            pygame.display.flip()
            pygame.time.delay(60)

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

    def animate_resurrection(self, center_pos):
        """Анимация воскрешения: золотое свечение с частицами света"""
        import math
        cx = center_pos[0] * CELL_SIZE + CELL_SIZE // 2
        cy = center_pos[1] * CELL_SIZE + CELL_SIZE // 2
        frames = 20
        for i in range(frames):
            pygame.event.pump()
            self.draw()
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            # Золотые частицы света, вращающиеся и стягивающиеся к центру
            for k in range(12):
                ang = (i * 0.3 + k) * 0.6
                rad = 20 + max(0, 30 - i * 1.5)
                px = cx + int(math.cos(ang) * rad)
                py = cy + int(math.sin(ang) * rad)
                # Золотые/желтые частицы
                pygame.draw.circle(s, (255, 255, 180, 150), (px, py), 4)
                pygame.draw.circle(s, (255, 255, 220, 100), (px, py), 2)
            # Золотое лечебное свечение
            r = 10 + i * 1.5
            a = max(0, 200 - i * 8)
            pygame.draw.circle(s, (255, 255, 150, a), (cx, cy), int(r), 4)
            pygame.draw.circle(s, (255, 255, 200, max(0, a - 40)), (cx, cy), int(max(2, r - 5)), 2)
            self.screen.blit(s, (0, 0))
            pygame.display.flip()
            pygame.time.delay(20)
    
    def animate_undead_heal_cast(self, target):
        # Анимация исцеления нежити: призрачные кости и голубоватое свечение
        cx = target.x*CELL_SIZE+CELL_SIZE//2
        cy = target.y*CELL_SIZE+CELL_SIZE//2
        frames = 16
        for i in range(frames):
            pygame.event.pump()
            self.draw()
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            # Призрачные "кости" — светлые частицы, вращающиеся и стягивающиеся к центру
            for k in range(10):
                ang = (i*0.4 + k) * 0.8
                rad = 16 + max(0, 24 - i*2)
                px = cx + int(math.cos(ang) * rad)
                py = cy + int(math.sin(ang) * rad)
                pygame.draw.circle(s, (200, 220, 240, 120), (px, py), 3)
                pygame.draw.circle(s, (230, 240, 255, 90), (px, py), 1)
            # Голубое лечебное свечение
            r = 8 + i*2
            a = max(0, 180 - i*10)
            pygame.draw.circle(s, (120, 200, 255, a), (cx, cy), r, 3)
            self.screen.blit(s, (0,0))
            pygame.display.flip()
            pygame.time.delay(18)

    def animate_fire_shield_cast(self, target, hide_unit_at=None):
        # Кратковременное появление огненного купола на цели
        cx = target.x*CELL_SIZE+CELL_SIZE//2
        cy = target.y*CELL_SIZE+CELL_SIZE//2
        max_r = CELL_SIZE
        frames = 12
        for i in range(frames):
            pygame.event.pump()
            self.draw(hide_unit_at=hide_unit_at)
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            r = int(max_r * (i+1) / frames)
            alpha = max(60, 220 - int(200 * i / frames))
            pygame.draw.circle(s, (255, 120, 40, alpha), (cx, cy), r, 4)
            pygame.draw.circle(s, (255, 200, 120, max(20, alpha-40)), (cx, cy), max(2, r-6), 2)
            self.screen.blit(s, (0,0))
            pygame.display.flip()
            pygame.time.delay(16)

    def animate_fire_shield_burst(self, defender, attacker, hide_unit_at=None):
        # Анимация срабатывания щита - такая же пылающая аура, как при касте
        self.animate_fire_shield_cast(defender, hide_unit_at=hide_unit_at)

    def start_new_game(self):
        """Сброс в главное меню выбора рас."""
        # Сброс состояния победы/поражения
        self.game_over = False
        self.victory_state = None
        self.winner_team = None
        self.victory_screen_shown = False
        # Остановка боевой музыки и intro звука для перезапуска
        from pygame import mixer
        if self.combat_music_playing:
            mixer.music.stop()
            self.combat_music_playing = False
        if self.battle_intro_playing:
            if self.intro_channel:
                self.intro_channel.stop()
            elif self.current_intro_sound:
                self.current_intro_sound.stop()
            self.battle_intro_playing = False
            self.current_intro_sound = None
            self.intro_channel = None
        self.player1_race = None
        self.player2_race = None
        self.player1_type = 'human'
        self.player2_type = 'ai'
        self.spectator_mode = False
        self.is_paused = False
        self.units = []
        self.corpses = []  # Очищаем трупы
        self.turn_queue = []
        self.state = 'battle_setup'

    def handle_key(self, key):
        """Обработка нажатий клавиш, включая делегирование отладочным хоткеям."""
        # Хоткеи отладчика (F1-F6)
        self.debugger.handle_debug_key(key)
        # ESC — открытие/закрытие внутриигрового меню или панелей
        if key == pygame.K_ESCAPE:
            # Звук нажатия на кнопку
            if self.button_click_sound:
                self.button_click_sound.play()
            if self.history_panel_open:
                self.history_panel_open = False
                return
            # В режиме наблюдения ESC возвращает в меню настройки
            if self.spectator_mode:
                self.state = 'battle_setup'
                self.game_over = False
                self.units = []
                self.selected_unit = None
                from pygame import mixer
                if self.combat_music_playing:
                    mixer.music.stop()
                    self.combat_music_playing = False
                if self.battle_intro_playing:
                    if self.intro_channel:
                        self.intro_channel.stop()
                    elif self.current_intro_sound:
                        self.current_intro_sound.stop()
                    self.battle_intro_playing = False
                self.menu_music_playing = False
                return
            # Тоггл простого меню
            if self.state == 'game' and not self.game_over:
                # В игре - открываем/закрываем меню и автоматически ставим/убираем паузу
                self.menu_open = not self.menu_open
                if self.menu_open:
                    # При открытии меню ставим паузу
                    self.is_paused = True
                else:
                    # При закрытии меню убираем паузу
                    self.is_paused = False
            else:
                # Вне игры - тоггл простого меню
                self.menu_open = not self.menu_open

    def perform_counterattack(self, attacker, defender, is_melee, target_is_melee_unit, skip_initial_redraw=False, hide_unit_at=None):
        """Реакции на атаку (огненный щит), затем стандартная контратака (если ближний бой)."""
        # 1) Реактивный урон огненного щита (не считается контратакой) - ТОЛЬКО для ближних атак
        if is_melee and defender and attacker and getattr(defender, 'fire_shield_turns', 0) > 0 and defender.health > 0:
            try:
                self.animate_fire_shield_burst(defender, attacker, hide_unit_at=hide_unit_at)
            except Exception:
                pass
            # Новая формула: 15% от макс HP + сила магии кастера
            max_hp = getattr(defender, 'max_health', 100)
            spell_power = getattr(defender, 'fire_shield_spell_power', 0)
            shield_damage = max(1, int(max_hp * 0.15) + spell_power)
            if shield_damage > 0:
                if attacker.take_damage(shield_damage, attack_type='magical'):
                    self.kill_unit(attacker)
                    self.animate_queue_fade(attacker)
                    self.add_event(f"{defender.unit_type.capitalize()} обжёг {attacker.unit_type} огненным щитом")
                    self.check_game_over()
                    # Если атакующий погиб — контратаки не будет
                    return True
                else:
                    self.add_event(f"{defender.unit_type.capitalize()} обжёг {attacker.unit_type} огненным щитом")

        # 2) Стандартная логика контратаки - только для ближнего боя
        # Герои не получают и не наносят контратаки
        from .units import Hero
        if isinstance(attacker, Hero) or isinstance(defender, Hero):
            return False
        
        # Проверка контратаки:
        # - Юниты под забвением не контратакуют
        # - Если у защитника есть контрудар (counterstrike_turns > 0), он всегда контратакует
        # - Иначе контратакует только если еще не контратаковал в этом раунде
        is_forgotten = hasattr(defender, 'forget_turns') and getattr(defender, 'forget_turns', 0) > 0
        has_counterstrike = hasattr(defender, 'counterstrike_turns') and getattr(defender, 'counterstrike_turns', 0) > 0
        can_counter = (has_counterstrike or not (hasattr(defender, 'has_counterattacked') and defender.has_counterattacked)) and not is_forgotten
        
        if not (is_melee and defender.health > 0 and can_counter):
            return False
        
        # Ждем завершения первой атаки (урон и звук)
        # Обновляем экран, чтобы показать урон (пропускаем, если идет анимация воина)
        if not skip_initial_redraw:
            self.draw()
            pygame.display.flip()
            pygame.time.delay(400)  # Задержка для первой атаки только если есть перерисовка
        
        # Теперь выполняем контратаку
        # Дальнобойные в ближнем бою бьют вполсилы
        if hasattr(defender, 'is_ranged') and defender.is_ranged:
            counter_damage = max(1, defender.get_current_attack() // 2)
        else:
            counter_damage = defender.get_current_attack()
        
        # Передаем тип атаки защитника
        defender_attack_type = getattr(defender, 'attack_type', 'physical')
        
        # Сохраняем здоровье для вычисления урона
        health_before = attacker.health
        squad_count_before = getattr(attacker, 'squad_count', 1)
        attacker_died = attacker.take_damage(counter_damage, attack_type=defender_attack_type)
        actual_damage = health_before - attacker.health
        squad_count_after = getattr(attacker, 'squad_count', 1)
        units_lost = squad_count_before - squad_count_after
        
        if attacker_died:
            self.kill_unit(attacker)
            self.animate_queue_fade(attacker)
            event_msg = f"{defender.unit_type.capitalize()} контратаковал и убил {attacker.unit_type.capitalize()} (урон: {actual_damage})"
            if units_lost > 0:
                event_msg += f", уничтожено {units_lost} юнитов из отряда"
            self.add_event(event_msg)
            self.check_game_over()
        else:
            event_msg = f"{defender.unit_type.capitalize()} контратаковал {attacker.unit_type.capitalize()} (урон: {actual_damage})"
            if units_lost > 0:
                event_msg += f", потеряно {units_lost} юнитов из отряда"
            self.add_event(event_msg)
            
            # 3) Проверяем огненный щит АТАКУЮЩЕГО после получения урона от контратаки
            # Это ближний бой (контратака), поэтому щит срабатывает
            if attacker and attacker.health > 0 and getattr(attacker, 'fire_shield_turns', 0) > 0 and defender.health > 0:
                try:
                    self.animate_fire_shield_burst(attacker, defender)
                except Exception:
                    pass
                # Новая формула: 15% от макс HP + сила магии кастера
                max_hp = getattr(attacker, 'max_health', 100)
                spell_power = getattr(attacker, 'fire_shield_spell_power', 0)
                shield_damage = max(1, int(max_hp * 0.15) + spell_power)
                if shield_damage > 0:
                    if defender.take_damage(shield_damage, attack_type='magical'):
                        self.kill_unit(defender)
                        self.animate_queue_fade(defender)
                        self.add_event(f"{attacker.unit_type.capitalize()} обжёг {defender.unit_type} огненным щитом")
                        self.check_game_over()
                    else:
                        self.add_event(f"{attacker.unit_type.capitalize()} обжёг {defender.unit_type} огненным щитом")
        
        # Отмечаем, что защитник контратаковал (только если нет контрудара)
        if not has_counterstrike:
            defender.has_counterattacked = True
        
        # Звук контратаки (после задержки)
        if defender.team in ['human', 'elf']:
            if self.human_melee_sounds:
                random.choice(self.human_melee_sounds).play()
        else:
            if self.monster_melee_sounds:
                random.choice(self.monster_melee_sounds).play()
        
        # Обновляем экран после контратаки
        self.draw()
        pygame.display.flip()
        return True

    def check_game_over(self):
        # Завершение боя: если осталась только одна команда или у какой-то команды не осталось юнитов
        if self.game_over:
            return
        teams_present = set(u.team for u in self.units)
        if len(teams_present) <= 1:
            # Победила последняя оставшаяся команда (или никого нет)
            self.game_over = True
            self.winner_team = next(iter(teams_present)) if teams_present else None
            if self.winner_team is None:
                self.victory_state = 'defeat'
            else:
                # Правильная логика определения победы/поражения
                # Определяем, есть ли игроки-люди
                has_human_player = (self.player1_type == 'human') or (self.player2_type == 'human')
                
                if has_human_player:
                    # Если есть хотя бы один игрок-человек
                    if self.winner_team == self.player1_race:
                        # Победила команда игрока 1
                        if self.player1_type == 'human':
                            # Игрок 1 (человек) выиграл
                            self.victory_state = 'victory'
                        else:
                            # Бот 1 победил, игрок 2 проиграл (если есть)
                            if self.player2_type == 'human':
                                self.victory_state = 'defeat'
                            else:
                                # Оба боты
                                self.victory_state = 'defeat'
                    elif self.winner_team == self.player2_race:
                        # Победила команда игрока 2
                        if self.player2_type == 'human':
                            # Игрок 2 (человек) выиграл
                            self.victory_state = 'victory'
                        else:
                            # Бот 2 победил, игрок 1 проиграл (если есть)
                            if self.player1_type == 'human':
                                self.victory_state = 'defeat'
                            else:
                                # Оба боты
                                self.victory_state = 'defeat'
                    else:
                        # Неизвестная раса победила - поражение для игрока
                        self.victory_state = 'defeat'
                else:
                    # Оба боты - поражение для наблюдателя
                    self.victory_state = 'defeat'
            from pygame import mixer
            if self.combat_music_playing:
                mixer.music.stop()
                self.combat_music_playing = False
            if self.victory_state == 'victory' and self.victory_sound:
                self.victory_sound.play()
            elif self.victory_state == 'defeat' and self.defeat_sound:
                self.defeat_sound.play()
            print(f"Игра окончена! Победили {TEAM_LABELS.get(self.winner_team, self.winner_team) if self.winner_team else 'Никто'}!")
            return

    def handle_click(self, pos, is_ai_action=False, button=1):
        # Блокируем действия во время проигрывания intro звука
        if self.state == 'game' and self.battle_intro_playing:
            return
        
        # Если игра окончена, клик возвращает в меню (высший приоритет)
        if self.game_over and self.victory_state:
            # Звук нажатия на кнопку
            if self.button_click_sound:
                try:
                    self.button_click_sound.stop()
                except:
                    pass
                self.button_click_sound.play()
            # Возврат в главное меню
            self.state = 'menu'
            self.game_over = False
            self.victory_state = None
            self.winner_team = None
            self.units = []
            self.selected_unit = None
            self.turn_queue = []
            self.current_initiative_index = 0
            self.event_log = []
            self.spellbook_open = False
            self.history_panel_open = False
            # Остановка боевой музыки и intro звука, сброс флага меню музыки для её перезапуска
            from pygame import mixer
            if self.combat_music_playing:
                mixer.music.stop()
                self.combat_music_playing = False
            if self.battle_intro_playing:
                if self.intro_channel:
                    self.intro_channel.stop()
                elif self.current_intro_sound:
                    self.current_intro_sound.stop()
                self.battle_intro_playing = False
                self.current_intro_sound = None
                self.intro_channel = None
            self.menu_music_playing = False  # Сброс для перезапуска музыки меню
            return
        
        # Проверяем меню ПЕРЕД блокировкой паузы, чтобы кнопки меню работали
        if self.menu_open:
            if self.exit_button_rect.collidepoint(pos):
                # Звук нажатия на кнопку - мгновенное воспроизведение
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                pygame.quit()
                exit()
            if hasattr(self, 'fullscreen_button_rect') and self.fullscreen_button_rect.collidepoint(pos):
                # Звук нажатия на кнопку - мгновенное воспроизведение
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                pygame.display.toggle_fullscreen()
                return
            # Кнопка "Настройки" (в паузе)
            if hasattr(self, 'pause_settings_button_rect') and self.pause_settings_button_rect.collidepoint(pos):
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                self.state = 'settings'
                self.menu_open = False
                self.is_paused = True
                return
            if hasattr(self, 'mainmenu_button_rect') and self.mainmenu_button_rect.collidepoint(pos):
                # Звук нажатия на кнопку - мгновенное воспроизведение
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                # Возврат в главное меню
                self._reset_battle_state()
                self.state = 'menu'
                self.menu_open = False
                self.is_paused = False  # Убираем паузу при закрытии меню
                # Остановка всех активных процессов игры
                self.units = []
                self.selected_unit = None
                self.turn_queue = []
                self.current_initiative_index = 0
                self.event_log = []
                self.game_over = False
                self.spellbook_open = False
                self.history_panel_open = False
                # Остановка боевой музыки и сброс флага меню музыки для её перезапуска
                from pygame import mixer
                if self.combat_music_playing:
                    mixer.music.stop()
                    self.combat_music_playing = False
                self.menu_music_playing = False  # Сброс для перезапуска музыки меню
                return
            if not self.menu_rect.collidepoint(pos):
                self.menu_open = False
                self.is_paused = False  # Убираем паузу при закрытии меню
            return
        
        # Блокируем действия во время паузы (кроме экранов интерфейса типа настроек/меню)
        if self.is_paused and self.state not in ('settings', 'menu') and not is_ai_action:
            return
        
        # В режиме наблюдения (оба бота) блокируем действия игрока, но разрешаем ИИ
        if self.spectator_mode and self.state == 'game' and not is_ai_action:
            # Разрешаем только ESC (обрабатывается через handle_key) и действия ИИ
            return
        
        # Блокируем действия игрока во время хода AI (кроме меню, которое обрабатывается отдельно)
        # ИИ может совершать клики, передавая is_ai_action=True
        if self.state == 'game' and self.selected_unit and not is_ai_action:
            is_ai_turn = False
            if self.ai_controller_p1 and self.selected_unit.team == self.ai_controller_p1.ai_team:
                is_ai_turn = True
            elif self.ai_controller_p2 and self.selected_unit.team == self.ai_controller_p2.ai_team:
                is_ai_turn = True
            
            if is_ai_turn:
                # Во время хода AI разрешаем только закрытие панели истории
                if self.history_panel_open and not self.spectator_mode:
                    if hasattr(self, 'history_panel_close_rect') and self.history_panel_close_rect.collidepoint(pos):
                        if self.button_click_sound:
                            try:
                                self.button_click_sound.stop()
                            except:
                                pass
                            self.button_click_sound.play()
                        self.history_panel_open = False
                        return
                # Блокируем все остальные действия во время хода AI
                return
        
        # Если игра окончена, клик возвращает в меню
        if self.game_over and self.victory_state:
            # Звук нажатия на кнопку
            if self.button_click_sound:
                try:
                    self.button_click_sound.stop()
                except:
                    pass
                self.button_click_sound.play()
            # Возврат в главное меню
            self.state = 'menu'
            self.game_over = False
            self.victory_state = None
            self.winner_team = None
            self.units = []
            self.selected_unit = None
            self.turn_queue = []
            self.current_initiative_index = 0
            self.event_log = []
            self.spellbook_open = False
            self.history_panel_open = False
            # Остановка боевой музыки и intro звука, сброс флага меню музыки для её перезапуска
            from pygame import mixer
            if self.combat_music_playing:
                mixer.music.stop()
                self.combat_music_playing = False
            if self.battle_intro_playing:
                if self.intro_channel:
                    self.intro_channel.stop()
                elif self.current_intro_sound:
                    self.current_intro_sound.stop()
                self.battle_intro_playing = False
                self.current_intro_sound = None
                self.intro_channel = None
            self.menu_music_playing = False  # Сброс для перезапуска музыки меню
            return
        # Блокируем взаимодействие с игрой если открыто окно информации о юните
        if self.unit_info_window_open:
            # Вычисляем позицию кнопки закрытия (если окно открыто, то юнит есть)
            if self.unit_info_window_unit:
                window_w, window_h = 600, 500
                window_x = (SCREEN_WIDTH - window_w) // 2
                window_y = (SCREEN_HEIGHT - window_h) // 2
                close_size = 30
                close_x = window_x + window_w - close_size - 10
                close_y = window_y + 10
                close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
                
                # Обрабатываем только клики по кнопке закрытия
                if close_button_rect.collidepoint(pos):
                    if self.button_click_sound:
                        self.button_click_sound.play()
                    self.unit_info_window_open = False
                    self.unit_info_window_unit = None
            return
        # Кнопка истории (не работает в режиме наблюдения)
        if self.history_button_rect.collidepoint(pos) and not self.spectator_mode:
            # Звук нажатия на кнопку
            if self.button_click_sound:
                self.button_click_sound.play()
            self.history_panel_open = True
            return
        # Если открыта панель истории (не работает в режиме наблюдения)
        if self.history_panel_open and not self.spectator_mode:
            if self.history_panel_close_rect.collidepoint(pos):
                # Звук нажатия на кнопку - мгновенное воспроизведение
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                self.history_panel_open = False
                return
            if self.history_panel_arrow_up and self.history_panel_arrow_up.collidepoint(pos):
                # Звук нажатия на кнопку - мгновенное воспроизведение
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                # Стрелка вверх = прокрутка вверх (показываем более старые события)
                max_lines = (400 - 80) // 22
                max_offset = max(0, len(self.event_log) - max_lines)
                self.event_log_offset = min(self.event_log_offset + 1, max_offset)
                return
            if self.history_panel_arrow_down and self.history_panel_arrow_down.collidepoint(pos):
                # Звук нажатия на кнопку - мгновенное воспроизведение
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                # Стрелка вниз = прокрутка вниз (показываем более новые события)
                self.event_log_offset = max(self.event_log_offset - 1, 0)
                return
        if self.state == 'menu':
            if self.start_button_rect.collidepoint(pos):
                # Звук нажатия на кнопку - мгновенное воспроизведение
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                self.state = 'battle_setup'
                return
            if self.exit_button_rect.collidepoint(pos):
                # Звук нажатия на кнопку - мгновенное воспроизведение
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                pygame.quit()
                exit()
            if hasattr(self, 'dev_button_rect') and self.dev_button_rect.collidepoint(pos):
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                # Вход в креатив-режим
                self._reset_battle_state()
                self.state = 'creative'
                self.units = []
                self.selected_unit = None
                return
            if hasattr(self, 'settings_button_rect') and self.settings_button_rect.collidepoint(pos):
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
                # Без сброса состояния/музыки — продолжаем фоновую музыку меню
                self.state = 'settings'
                return
            return
        if self.state == 'creative':
            self.handle_creative_click(pos, button=button)
            return
        if self.state == 'settings':
            self.handle_settings_click(pos)
            return
        if self.state == 'unit_editor':
            self.handle_unit_editor_click(pos)
            return
        if self.state == 'spell_editor':
            self.handle_spell_editor_click(pos)
            return
        if self.state == 'spellbook_editor':
            self.handle_spellbook_editor_click(pos)
            return
        if self.state == 'battle_setup':
            # Переключатель типа игрока 1
            if hasattr(self, 'player1_toggle_human_rect') and self.player1_toggle_human_rect.collidepoint(pos):
                if self.button_click_sound:
                    self.button_click_sound.play()
                self.player1_type = 'human'
                return
            if hasattr(self, 'player1_toggle_ai_rect') and self.player1_toggle_ai_rect.collidepoint(pos):
                if self.button_click_sound:
                    self.button_click_sound.play()
                self.player1_type = 'ai'
                return
            
            # Переключатель типа игрока 2
            if hasattr(self, 'player2_toggle_human_rect') and self.player2_toggle_human_rect.collidepoint(pos):
                if self.button_click_sound:
                    self.button_click_sound.play()
                self.player2_type = 'human'
                return
            if hasattr(self, 'player2_toggle_ai_rect') and self.player2_toggle_ai_rect.collidepoint(pos):
                if self.button_click_sound:
                    self.button_click_sound.play()
                self.player2_type = 'ai'
                return
            
            # Выбор расы для игрока 1
            if hasattr(self, 'player1_race_rects'):
                for rect, race_key in self.player1_race_rects:
                    if rect.collidepoint(pos):
                        if self.button_click_sound:
                            self.button_click_sound.play()
                        self.player1_race = race_key
                        # Устанавливаем дефолтный класс при смене расы
                        default_classes = {
                            'human': 'warrior',
                            'elf': 'archer',
                            'undead': 'mage',
                            'demon': 'warrior',
                            'dwarf': 'warrior',
                            'shadow': 'mage'
                        }
                        self.player1_hero_class = default_classes.get(race_key, 'warrior')
                        return
            
            # Выпадающий список класса для игрока 1
            if hasattr(self, 'player1_class_dropdown_rect') and self.player1_class_dropdown_rect:
                if self.player1_class_dropdown_rect.collidepoint(pos):
                    if self.button_click_sound:
                        self.button_click_sound.play()
                    # Переключаем состояние выпадающего списка
                    self.player1_class_dropdown_open = not getattr(self, 'player1_class_dropdown_open', False)
                    # Закрываем другой список если открыт
                    self.player2_class_dropdown_open = False
                    return
            
            # Выбор класса из выпадающего списка игрока 1
            if hasattr(self, 'player1_class_rects') and getattr(self, 'player1_class_dropdown_open', False):
                for rect, class_key in self.player1_class_rects:
                    if rect.collidepoint(pos):
                        if self.button_click_sound:
                            self.button_click_sound.play()
                        self.player1_hero_class = class_key
                        self.player1_class_dropdown_open = False
                        return
            
            # Выбор расы для игрока 2
            if hasattr(self, 'player2_race_rects'):
                for rect, race_key in self.player2_race_rects:
                    if rect.collidepoint(pos):
                        # Разрешаем выбор, но проверяем уникальность при старте боя
                        if self.button_click_sound:
                            self.button_click_sound.play()
                        self.player2_race = race_key
                        # Устанавливаем дефолтный класс при смене расы
                        default_classes = {
                            'human': 'warrior',
                            'elf': 'archer',
                            'undead': 'mage',
                            'demon': 'warrior',
                            'dwarf': 'warrior',
                            'shadow': 'mage'
                        }
                        self.player2_hero_class = default_classes.get(race_key, 'warrior')
                        return
            
            # Выпадающий список класса для игрока 2
            if hasattr(self, 'player2_class_dropdown_rect') and self.player2_class_dropdown_rect:
                if self.player2_class_dropdown_rect.collidepoint(pos):
                    if self.button_click_sound:
                        self.button_click_sound.play()
                    # Переключаем состояние выпадающего списка
                    self.player2_class_dropdown_open = not getattr(self, 'player2_class_dropdown_open', False)
                    # Закрываем другой список если открыт
                    self.player1_class_dropdown_open = False
                    return
            
            # Выбор класса из выпадающего списка игрока 2
            if hasattr(self, 'player2_class_rects') and getattr(self, 'player2_class_dropdown_open', False):
                for rect, class_key in self.player2_class_rects:
                    if rect.collidepoint(pos):
                        if self.button_click_sound:
                            self.button_click_sound.play()
                        self.player2_hero_class = class_key
                        self.player2_class_dropdown_open = False
                        return
            
            # Кнопка "Начать бой"
            if hasattr(self, 'start_battle_btn_rect') and self.start_battle_btn_rect.collidepoint(pos):
                if self.button_click_sound:
                    self.button_click_sound.play()
                # Проверяем условия запуска
                if (self.player1_race is not None and self.player2_race is not None and 
                    self.player1_race != self.player2_race):
                    # Определяем режим наблюдения (оба бота)
                    self.spectator_mode = (self.player1_type == 'ai' and self.player2_type == 'ai')
                    
                    # Запускаем игру
                    self.state = 'game'
                    self.background = self.generate_battlefield()
                    # Применение звуковых настроек из файла настроек
                    self._apply_audio_volumes()
                    self.initialize_units(self.player1_race, self.player2_race)
                    self.prepare_initiative_queue()
                    if hasattr(self, 'turn_queue') and self.turn_queue:
                        self.selected_unit = self.turn_queue[0]
                    
                    # Инициализация ИИ для обоих игроков если нужно
                    if self.player1_type == 'ai':
                        self.ai_controller_p1 = AIController(self, self.player1_race)
                    if self.player2_type == 'ai':
                        self.ai_controller_p2 = AIController(self, self.player2_race)
                    self.ai_think_timer = 0
                # Если условия не выполнены, все равно обрабатываем клик (звук уже проигран)
                    return
            return
        # Книга заклинаний можно открывать для любого героя с заклинаниями, если не использовано в этом раунде (не работает в режиме наблюдения)
        if (not self.spectator_mode
            and isinstance(self.selected_unit, Hero)
            and self.selected_unit.spells
            and not getattr(self.selected_unit, 'used_spell_this_round', False)
            and self.book_button_rect.collidepoint(pos)):
            # Звук нажатия на кнопку
            if self.button_click_sound:
                self.button_click_sound.play()
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
                # Звук нажатия на кнопку - мгновенное воспроизведение
                if self.button_click_sound:
                    try:
                        self.button_click_sound.stop()
                    except:
                        pass
                    self.button_click_sound.play()
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
                    # Звук нажатия на кнопку - проигрываем сразу без задержки
                    if self.button_click_sound:
                        # Останавливаем предыдущий звук если играет
                        try:
                            self.button_click_sound.stop()
                        except:
                            pass
                        # Воспроизводим сразу без задержки
                        self.button_click_sound.play()
                    # Запускаем анимацию перелистывания, если школа изменилась
                    old_school = getattr(self, 'spellbook_selected_school', 'all')
                    if school != old_school:
                        # Определяем направление по индексу
                        school_names = [s[0] for s in school_list]
                        old_idx = school_names.index(old_school) if old_school in school_names else 0
                        new_idx = school_names.index(school) if school in school_names else 0
                        self.spellbook_flip_animation = {
                            'from_school': old_school,
                            'to_school': school,
                            'progress': 0.0,
                            'direction': 1 if new_idx > old_idx else -1
                        }
                    self.spellbook_selected_school = school
                    self.spellbook_page = 0
                    return
            # --- Обработка кликов по кнопкам перелистывания страниц ---
            if hasattr(self, 'spellbook_next_page_rect') and self.spellbook_next_page_rect and self.spellbook_next_page_rect.collidepoint(pos):
                page = getattr(self, 'spellbook_page', 0)
                spells = self.selected_unit.spells
                selected_school = getattr(self, 'spellbook_selected_school', 'all')
                filtered_spells = [s for s in spells if selected_school == 'all' or getattr(s, 'school', None) == selected_school]
                spells_per_page = 12
                total_pages = (len(filtered_spells) + spells_per_page - 1) // spells_per_page
                if page < total_pages - 1:
                    self.spellbook_page = page + 1
                    if self.button_click_sound:
                        self.button_click_sound.play()
                    return
            if hasattr(self, 'spellbook_prev_page_rect') and self.spellbook_prev_page_rect and self.spellbook_prev_page_rect.collidepoint(pos):
                page = getattr(self, 'spellbook_page', 0)
                if page > 0:
                    self.spellbook_page = page - 1
                    if self.button_click_sound:
                        self.button_click_sound.play()
                    return
            # --- Выбор заклинания (с учетом нового расположения: 2 столбца слева, 2 столбца справа) ---
            spells = self.selected_unit.spells
            selected_school = getattr(self, 'spellbook_selected_school', 'all')
            filtered_spells = [s for s in spells if selected_school == 'all' or getattr(s, 'school', None) == selected_school]
            spells_per_page = 12
            spell_spacing = 10
            page = getattr(self, 'spellbook_page', 0)
            start_idx = page * spells_per_page
            end_idx = min(start_idx + spells_per_page, len(filtered_spells))
            for idx, spell in enumerate(filtered_spells[start_idx:end_idx]):
                # Первые 6 заклинаний (0-5): левая сторона (2 столбца × 3 строки)
                # Следующие 6 заклинаний (6-11): правая сторона (2 столбца × 3 строки)
                if idx < 6:
                    # Левая сторона
                    col = idx % 2  # 0 или 1 внутри левого блока
                    row = idx // 2  # 0, 1, 2
                    sx = book_x + 60 + col * (spell_size + spell_spacing)
                    sy = book_y + 60 + row * 100
                else:
                    # Правая сторона
                    local_idx = idx - 6
                    col = local_idx % 2  # 0 или 1 внутри правого блока
                    row = local_idx // 2  # 0, 1, 2
                    sx = book_x + book_w//2 + 36 + col * (spell_size + spell_spacing)
                    sy = book_y + 60 + row * 100
                icon_rect = pygame.Rect(sx, sy, spell_size, spell_size)
                if icon_rect.collidepoint(pos):
                    # Звук нажатия на кнопку
                    if self.button_click_sound:
                        self.button_click_sound.play()
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
            # Блокируем взаимодействие с игрой если книга открыта (после обработки всех кликов по книге)
            return
        
        # Блокируем взаимодействие с игрой если книга открыта (кроме кликов внутри книги)
        if self.spellbook_open and isinstance(self.selected_unit, Hero) and self.selected_unit.spells:
            return  # Блокируем все клики вне книги - нельзя взаимодействовать с игрой пока открыта книга
        
        # Обработка кнопки "Пропустить" (ожидание)
        if self.skip_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            if self.button_click_sound:
                self.button_click_sound.play()
            # Сохраняем текущие ОД для восстановления в следующем ходу
            if hasattr(self.selected_unit, 'move_points_left'):
                self.selected_unit._saved_move_points = self.selected_unit.move_points_left
                self.selected_unit.has_waited = True
            self.next_turn()
            return
        
        # Обработка кнопки "Защита"
        if self.defend_button_rect.collidepoint(pos) and self.selected_unit and not isinstance(self.selected_unit, Hero):
            if self.button_click_sound:
                self.button_click_sound.play()
            # Устанавливаем флаг защиты на этот раунд
            self.selected_unit._defend_this_round = True
            # Защита также завершает ход
            self.next_turn()
            return
        
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
                # Для RaiseDead - проверка занятости клетки перед применением
                if hasattr(spell, 'icon') and spell.icon == 'raise_dead':
                    if target is not None:  # Клетка занята юнитом
                        return
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
                    # Callback для звука взрыва фаербола
                    def play_fireball_explosion():
                        if self.fireball_explosion_sound:
                            self.fireball_explosion_sound.play()
                    # Callback для звука полёта фаербола
                    def play_fireball_flight():
                        if self.fireball_flight_sound:
                            self.fireball_flight_sound.play()
                    animate_fireball(self.screen, caster_px, center_px, redraw_callback=self.draw, explosion_sound_callback=play_fireball_explosion, flight_sound_callback=play_fireball_flight)
                elif hasattr(spell, 'icon') and spell.icon == 'meteor_rain':
                    # Метеоритный дождь использует анимацию в самом заклинании
                    caster.selected_spell = None
                elif hasattr(spell, 'icon') and spell.icon == 'ice_arrow':
                    # Ледяная стрела использует анимацию в самом заклинании
                    caster.selected_spell = None
                elif hasattr(spell, 'icon') and spell.icon == 'phantom':
                    # Фантом использует анимацию в самом заклинании
                    caster.selected_spell = None
                elif hasattr(spell, 'icon') and spell.icon == 'chain_lightning':
                    # Цепная молния использует анимацию в самом заклинании
                    caster.selected_spell = None
                elif hasattr(spell, 'icon') and spell.icon == 'quicksand':
                    # Зыбучие пески используют анимацию в самом заклинании
                    pass
                elif hasattr(spell, 'icon') and spell.icon == 'earth_shock':
                    # Шок земли использует анимацию в самом заклинании
                    pass
                elif hasattr(spell, 'icon') and spell.icon == 'prayer':
                    # Молитва использует анимацию в самом заклинании
                    pass
                elif hasattr(spell, 'icon') and spell.icon == 'blindness':
                    # Ослепление использует анимацию в самом заклинании
                    pass
                # Применение по области/клетке
                spell_success = spell.apply((x, y), caster=caster)
                # Если заклинание не сработало, герой не тратит ход
                if spell_success is False:
                    self.area_preview_dismiss = True
                    return
                caster.mana = max(0, caster.mana - spell.mana_cost)
                caster.used_spell_this_round = True
                self.area_preview_dismiss = True
                self.next_turn()
                return
            if spell.target_type == 'enemy' and target and target.team != caster.team and caster.mana >= spell.mana_cost:
                self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                
                # Получаем информацию о заклинании для анимации
                spell_name = getattr(spell, 'name', '')
                spell_icon = getattr(spell, 'icon', '')
                
                # Проверяем мгновенные заклинания (без анимации полета снаряда)
                instant_spells = [
                    'lightning', 'weakness', 'bless', 'curse', 'slow', 'haste',
                    'heal', 'dispel', 'stone_skin', 'ice_shield', 'fire_shield',
                    'counterstrike', 'rune_shield', 'rune_haste', 'raise_dead',
                    'resurrection', 'undead_heal', 'forget', 'earth_spikes', 'rune_wall'
                ]
                is_instant_spell = (spell_icon in instant_spells or 
                                  spell_name in ['Молния', 'Слабость', 'Благословение', 'Проклятие', 
                                                'Замедление', 'Ускорение', 'Лечение', 'Снятие чар'] or
                                  any(keyword in spell_icon.lower() for keyword in ['lightning', 'weakness', 'bless', 'curse']))
                
                # Отладочное логирование
                self.anim_logger.log("SPELL_CHECK", f"name='{spell_name}' icon='{spell_icon}' instant={is_instant_spell}")
                
                # Логируем анимацию заклинания
                self.anim_logger.log_spell_animation(spell_name, spell_icon, caster, target, is_instant_spell)
                
                # Специальные анимации по типам
                if hasattr(spell, 'icon') and spell.icon == 'firearrow':
                    self.animate_firearrow(caster, target)
                elif hasattr(spell, 'icon') and spell.icon == 'slow':
                    # Звук заклинания замедления
                    if self.slow_sound:
                        try:
                            self.slow_sound.stop()
                        except:
                            pass
                        self.slow_sound.play()
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_slow_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                elif hasattr(spell, 'icon') and spell.icon == 'curse':
                    # Воспроизводим звук проклятия
                    if self.curse_sound:
                        self.curse_sound.play()
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_curse_voodoo(self.screen, target_px, redraw_callback=self.draw)
                elif hasattr(spell, 'icon') and spell.icon == 'forget':
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_forget_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_dispel_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                elif hasattr(spell, 'icon') and spell.icon == 'ice_arrow':
                    # Ледяная стрела использует анимацию в самом заклинании, без магического шарика
                    pass
                elif hasattr(spell, 'icon') and spell.icon == 'chain_lightning':
                    # Цепная молния использует анимацию в самом заклинании
                    pass
                elif hasattr(spell, 'icon') and spell.icon == 'quicksand':
                    # Зыбучие пески используют анимацию в самом заклинании
                    pass
                elif hasattr(spell, 'icon') and spell.icon == 'earth_shock':
                    # Шок земли использует анимацию в самом заклинании
                    pass
                elif hasattr(spell, 'icon') and spell.icon == 'prayer':
                    # Молитва использует анимацию в самом заклинании
                    pass
                elif hasattr(spell, 'icon') and spell.icon == 'blindness':
                    # Ослепление использует анимацию в самом заклинании
                    pass
                elif hasattr(spell, 'icon') and spell.icon == 'rune_berserker':
                    # Анимация руны берсерка проигрывается сразу на цели (без полета снаряда)
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_rune_berserker_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                elif hasattr(spell, 'icon') and spell.icon == 'rune_magic':
                    # Анимация руны магии
                    caster_px = (caster.x * CELL_SIZE + CELL_SIZE//2, caster.y * CELL_SIZE + CELL_SIZE//2)
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_rune_magic_spell(self.screen, caster_px, target_px, redraw_callback=self.draw)
                elif not is_instant_spell:
                    # Полёт магического снаряда только для НЕ мгновенных заклинаний
                    self.anim_logger.log("PROJECTILE_ANIMATION", f"Снаряд для {spell_name}")
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
                # Для мгновенных заклинаний (lightning, weakness) - никакой анимации полета
                spell_success = spell.apply(target, caster=caster)
                # Если заклинание не сработало, герой не тратит ход
                if spell_success is False:
                    caster.selected_spell = None
                    self.area_preview_dismiss = True
                    return
                caster.mana = max(0, caster.mana - spell.mana_cost)
                caster.selected_spell = None
                caster.used_spell_this_round = True
                self.area_preview_dismiss = True
                self.next_turn()
                return
            elif spell.target_type == 'both':
                # Обработка заклинаний, которые могут применяться и к союзникам, и к врагам (например, воскрешение, поднятие мёртвых)
                # Специальная логика для raise_undead: воскрешение трупов или лечение живых нежить
                if hasattr(spell, 'icon') and spell.icon == 'raise_undead' and caster.mana >= spell.mana_cost:
                    # Получаем координаты клика
                    mx, my = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                    
                    # Сначала проверяем труп нежити на этой клетке
                    corpse_found = None
                    for corpse in self.corpses:
                        if corpse['x'] == mx and corpse['y'] == my:
                            # Поднятие мёртвых работает только на нежить
                            if corpse['team'] == 'undead':
                                corpse_found = corpse
                                break
                    
                    if corpse_found:
                        # Анимация поднятия мёртвых (до применения)
                        try:
                            # Используем анимацию для нежити
                            for unit in self.units:
                                if unit.x == mx and unit.y == my:
                                    self.animate_undead_heal_cast(unit)
                                    break
                            else:
                                # Если нет юнита на клетке, создаем временный объект для анимации
                                class TempUnit:
                                    def __init__(self, x, y):
                                        self.x = x
                                        self.y = y
                                temp_unit = TempUnit(mx, my)
                                self.animate_undead_heal_cast(temp_unit)
                        except:
                            pass
                        # Воскрешаем труп через метод apply заклинания
                        spell_success = spell.apply((mx, my), caster=caster)
                        if spell_success:
                            caster.mana = max(0, caster.mana - spell.mana_cost)
                            caster.selected_spell = None
                            caster.used_spell_this_round = True
                            self.area_preview_dismiss = True
                            self.next_turn()
                        else:
                            # Если не удалось воскресить, не тратим ману
                            caster.selected_spell = None
                            self.area_preview_dismiss = True
                        return
                    
                    # Если трупа нет, проверяем живую нежить на этой клетке
                    # Проверяем напрямую через список юнитов, а не через target
                    living_unit = None
                    for unit in self.units:
                        if unit.x == mx and unit.y == my:
                            if unit.team == 'undead':
                                living_unit = unit
                                break
                    
                    if living_unit:
                        # Анимация поднятия мёртвых (до применения)
                        try:
                            self.animate_undead_heal_cast(living_unit)
                        except:
                            pass
                        # Лечим/воскрешаем живую нежить через метод apply заклинания
                        spell_success = spell.apply((mx, my), caster=caster)
                        if spell_success:
                            caster.mana = max(0, caster.mana - spell.mana_cost)
                            caster.selected_spell = None
                            caster.used_spell_this_round = True
                            self.area_preview_dismiss = True
                            self.next_turn()
                        else:
                            caster.selected_spell = None
                            self.area_preview_dismiss = True
                        return
                    else:
                        # Нет ни трупа, ни живой нежити для лечения/воскрешения
                        caster.selected_spell = None
                        self.area_preview_dismiss = True
                        return
                # Специальная логика для resurrection: воскрешение трупов или лечение живых союзников (не нежить)
                elif hasattr(spell, 'icon') and spell.icon == 'resurrection' and caster.mana >= spell.mana_cost:
                    # Получаем координаты клика
                    mx, my = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                    
                    # Логирование попытки каста
                    try:
                        import resurrection_debug as debug
                        target_unit = None
                        for u in self.units:
                            if u.x == mx and u.y == my:
                                target_unit = u
                                break
                        debug.log_spell_cast(caster, spell, (mx, my), target_unit is not None)
                    except:
                        pass
                    
                    # Сначала проверяем труп на этой клетке
                    corpse_found = None
                    for corpse in self.corpses:
                        if corpse['x'] == mx and corpse['y'] == my:
                            # Воскрешение не работает на нежить
                            if corpse['team'] != 'undead':
                                corpse_found = corpse
                                break
                    
                    if corpse_found:
                        # Воскрешаем труп через метод apply заклинания
                        # Анимация воскрешения (до применения)
                        try:
                            self.animate_resurrection((mx, my))
                        except:
                            pass
                        spell_success = spell.apply((mx, my), caster=caster)
                        if spell_success:
                            caster.mana = max(0, caster.mana - spell.mana_cost)
                            caster.selected_spell = None
                            caster.used_spell_this_round = True
                            self.area_preview_dismiss = True
                            self.next_turn()
                        else:
                            # Если не удалось воскресить, не тратим ману
                            caster.selected_spell = None
                            self.area_preview_dismiss = True
                        return
                    
                    # Если трупа нет, проверяем живого союзника на этой клетке
                    # Проверяем напрямую через список юнитов, а не через target
                    living_unit = None
                    for unit in self.units:
                        if unit.x == mx and unit.y == my:
                            if unit.team == caster.team and unit.team != 'undead':
                                living_unit = unit
                                break
                    
                    if living_unit:
                        # Анимация воскрешения (до применения)
                        try:
                            self.animate_resurrection((mx, my))
                        except:
                            pass
                        # Лечим/воскрешаем живого союзника через метод apply заклинания
                        spell_success = spell.apply((mx, my), caster=caster)
                        if spell_success:
                            caster.mana = max(0, caster.mana - spell.mana_cost)
                            caster.selected_spell = None
                            caster.used_spell_this_round = True
                            self.area_preview_dismiss = True
                            self.next_turn()
                        else:
                            caster.selected_spell = None
                            self.area_preview_dismiss = True
                        return
                    else:
                        # Нет ни трупа, ни живого союзника для лечения/воскрешения
                        return
            elif spell.target_type == 'ally':
                # Разрешаем Снятие чар по врагу для развеивания баффов
                # Также разрешаем применение на врагов для других заклинаний, если они могут применяться на врагов
                if target and target.team != caster.team:
                    # Проверяем, может ли заклинание применяться на врагов
                    if hasattr(spell, 'icon') and spell.icon == 'dispel':
                        # Снятие чар можно применять на врагов
                        pass
                    elif getattr(spell, 'can_target_enemy', False):
                        # Заклинание имеет флаг разрешения применения на врагов
                        pass
                    else:
                        # Заклинание не может применяться на врагов
                        return
                
                # Проверяем ману и применяем заклинание (на союзников или врагов для dispel и rune_berserker)
                if target and caster.mana >= spell.mana_cost:
                    # Для dispel и rune_berserker можно применять на врагов
                    if hasattr(spell, 'icon') and (spell.icon == 'dispel' or spell.icon == 'rune_berserker') and target.team != caster.team:
                        self.add_event(f"Герой применил {spell.name} на {target.unit_type} (враг)")
                    elif target.team == caster.team:
                        self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    else:
                        return  # Нельзя применять на врагов
                    # --- Анимация для благословения и снятия чар ---
                    caster_px = (caster.x * CELL_SIZE + CELL_SIZE//2, caster.y * CELL_SIZE + CELL_SIZE//2)
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    if hasattr(spell, 'icon') and spell.icon == 'bless':
                        # Звук благословения из Heroes 3
                        if self.bless_sound:
                            self.bless_sound.play()
                        animate_bless_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'dispel':
                        animate_dispel_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'rune_shield':
                        animate_rune_shield_spell(self.screen, caster_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'rune_haste':
                        animate_rune_haste_spell(self.screen, caster_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'rune_magic':
                        animate_rune_magic_spell(self.screen, caster_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'rune_berserker':
                        # Анимация руны берсерка проигрывается сразу на цели (без полета снаряда)
                        animate_rune_berserker_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'haste':
                        # Анимация ускорения воздуха
                        animate_air_haste_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'stone_skin':
                        animate_stone_skin(self.screen, target_px, redraw_callback=self.draw)
                    elif hasattr(spell, 'icon') and spell.icon == 'fire_shield':
                        # Анимация огненного щита
                        self.animate_fire_shield_cast(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'raise_undead':
                        # Анимация поднятия мёртвых
                        self.animate_undead_heal_cast(target)
                    elif hasattr(spell, 'icon') and spell.icon == 'resurrection':
                        # Воскрешение принимает координаты, а не объект
                        spell_success = spell.apply((target.x, target.y), caster=caster)
                        # Если заклинание не сработало, герой не тратит ход
                        if spell_success is False:
                            caster.selected_spell = None
                            self.area_preview_dismiss = True
                            return
                        caster.mana = max(0, caster.mana - spell.mana_cost)
                        caster.selected_spell = None
                        caster.used_spell_this_round = True
                        self.area_preview_dismiss = True
                        # Герой передает ход после использования заклинания
                        self.next_turn()
                        return
                    # Применение союзных баффов/эффектов и завершение хода
                    # Для лечения анимация уже в HealSpell.apply
                    spell_success = spell.apply(target, caster=caster)
                    # Если заклинание не сработало, герой не тратит ход
                    if spell_success is False:
                        caster.selected_spell = None
                        self.area_preview_dismiss = True
                        return
                    caster.mana = max(0, caster.mana - spell.mana_cost)
                    caster.selected_spell = None
                    caster.used_spell_this_round = True
                    self.area_preview_dismiss = True
                    # Герой передает ход после использования заклинания
                    self.next_turn()
                    return
                    
                # Если это Снятие чар по вражеской цели
                if target and (hasattr(spell, 'icon') and spell.icon == 'dispel') and caster.mana >= spell.mana_cost:
                    self.add_event(f"Герой применил {spell.name} на {target.unit_type}")
                    target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
                    animate_dispel_spell(self.screen, target_px, target_px, redraw_callback=self.draw)
                    spell.apply(target, caster=caster)
                    caster.mana = max(0, caster.mana - spell.mana_cost)
                    caster.selected_spell = None
                    caster.used_spell_this_round = True
                    self.area_preview_dismiss = True
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
            if self.selected_unit.can_move(x, y, self.units, self.barriers):
                path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, x, y)
                if path_len <= self.selected_unit.move_points_left:
                    self.animate_unit_move(self.selected_unit, x, y)
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
                # Проверяем расстояние для определения типа атаки
                distance = abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)
                is_melee = (distance == 1)
                damage_already_applied = False  # Флаг для отслеживания применения урона
                
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    # Лучники и дальнобойные юниты
                    if is_melee:
                        # Ближний бой для лучников - только ближний бой, без стрел
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = max(1, self.selected_unit.get_current_attack() // 2)  # Половина урона
                        # Запоминаем параметры для контратаки (даже для лучников в ближнем бою)
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                    else:
                        # Дальняя атака - стреляем стрелами/снарядами, контратаки нет
                        target_is_melee_unit = False  # Дальняя атака, контратаки нет
                        start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                        end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                        
                        # Проверяем, является ли атакующий героем
                        is_hero = isinstance(self.selected_unit, Hero)
                        hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                        
                        # Определяем тип снаряда в зависимости от юнита/героя
                        if is_hero and hero_class == 'archer':
                            # Герой-лучник: стреляет стрелами
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            pygame.time.delay(150)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
                        elif self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                            # Обычные лучники стреляют стрелами - воспроизводим звуки
                            # Звук натяжения лука
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            # Небольшая задержка для звука натяжения
                            pygame.time.delay(150)
                            # Звук выстрела - используем новые звуки выстрелов (случайный выбор)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            # Анимация полета стрелы
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            # Звук попадания
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
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
                            # Воспроизводим звук выстрела магов
                            if self.magic_shot_sound:
                                self.magic_shot_sound.play()
                            animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                        # Перерисовываем экран, чтобы убрать снаряд
                        self.draw()
                        pygame.display.flip()
                        # Для дальнобойной атаки проверяем руну магии с учетом множителя дальности
                        mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit, is_ranged=True, target_x=x, target_y=y)
                        if mixed_damage is not None:
                            # Для руны магии используем смешанный урон
                            damage = None  # Будет применен через mixed_damage
                        else:
                            # Обычный расчет урона для дальнобойных
                            damage = self.selected_unit.ranged_damage(x, y)
                        
                        # Применяем урон для дальнобойных атак
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            elif damage is not None:
                                clicked_unit.take_damage(damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
                else:
                    # Обычные ближние бойцы и герои-воины
                    # Проверяем героя-воина - у него особая анимация
                    is_hero = isinstance(self.selected_unit, Hero)
                    hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                    
                    if is_hero and hero_class == 'warrior':
                        # Герой-воин: телепортация к цели
                        damage = self.selected_unit.get_current_attack()
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Сохраняем здоровье до атаки для вычисления урона
                        health_before = clicked_unit.health
                        # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                        squad_count_before_warrior = getattr(clicked_unit, 'squad_count', 1)
                        
                        # Создаем callback для применения урона (ТОЛЬКО урон, без последствий)
                        def apply_warrior_damage():
                            nonlocal damage_already_applied
                            damage_already_applied = True
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                        
                        # Вычисляем позицию рядом с целью
                        dx = clicked_unit.x - self.selected_unit.x
                        dy = clicked_unit.y - self.selected_unit.y
                        # Позиция рядом с целью (смещение в направлении атакующего)
                        if abs(dx) > abs(dy):
                            attack_x = clicked_unit.x - (1 if dx > 0 else -1)
                            attack_y = clicked_unit.y
                        else:
                            attack_x = clicked_unit.x
                            attack_y = clicked_unit.y - (1 if dy > 0 else -1)
                        
                        # Запускаем анимацию телепортации
                        animate_warrior_teleport(self.screen, 
                                                (self.selected_unit.x * CELL_SIZE, self.selected_unit.y * CELL_SIZE),
                                                (attack_x * CELL_SIZE, attack_y * CELL_SIZE),
                                                self.selected_unit.image,
                                                redraw_callback=self.draw,
                                                attack_sound_callback=lambda: (random.choice(self.human_melee_sounds).play() if self.human_melee_sounds and hasattr(random, 'choice') else None) if self.selected_unit.team in ['human', 'elf', 'dwarf'] else (random.choice(self.monster_melee_sounds).play() if self.monster_melee_sounds and hasattr(random, 'choice') else None),
                                                damage_callback=apply_warrior_damage,
                                                hide_attacker_pos=(self.selected_unit.x, self.selected_unit.y))
                        
                        # Вычисляем нанесенный урон
                        actual_damage = health_before - clicked_unit.health
                        
                        # ПОСЛЕ анимации обрабатываем последствия
                        squad_count_after_warrior = getattr(clicked_unit, 'squad_count', 1)
                        units_lost_warrior = squad_count_before_warrior - squad_count_after_warrior
                        if clicked_unit.health <= 0:
                            self.kill_unit(clicked_unit)
                            self.animate_queue_fade(clicked_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", уничтожено {units_lost_warrior} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", потеряно {units_lost_warrior} юнитов из отряда ({squad_count_after_warrior}/{squad_count_before_warrior})"
                            self.add_event(event_msg)
                            # Контратака происходит ПОСЛЕ анимации
                            self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки для героя-воина и переходим к следующему ходу
                        self.selected_unit.has_attacked = True
                        self.next_turn()
                        return
                    else:
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = self.selected_unit.get_current_attack()
                        # Запоминаем параметры для контратаки
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Применяем урон для обычных ближних бойцов
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                                # Контратака происходит ПОСЛЕ нанесения урона
                                self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
    
    def draw_unit_tooltip(self, unit):
        """Отрисовка тултипа юнита при зажатии правой кнопки мыши"""
        from .units import Hero
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)
        
        # Собираем информацию о юните
        lines = []
        lines.append(f"{unit.unit_type.capitalize()}")
        lines.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
        
        # Для героев показываем те же параметры что в окне информации (кроме удачи и боевого духа)
        if isinstance(unit, Hero):
            # Базовые параметры
            base_attack = getattr(unit, 'base_attack', None)
            if base_attack is None:
                # Вычисляем базовую атаку в зависимости от класса
                if unit.hero_class == 'mage':
                    base_attack = 5 + unit.spell_power
                else:  # warrior или archer
                    base_attack = 5 + unit.attack
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            knowledge = getattr(unit, 'knowledge', 0)
            spell_power = getattr(unit, 'spell_power', 0)
            mana = getattr(unit, 'mana', 0)
            max_mana = getattr(unit, 'max_mana', 0)
            
            lines.append(f"Базовая атака: {base_attack}")
            lines.append(f"Атака: {attack}")
            lines.append(f"Защита: {defense}")
            lines.append(f"Знания: {knowledge}")
            lines.append(f"Сила магии: {spell_power}")
            lines.append(f"Мана: {mana}/{max_mana}")
        else:
            # Для обычных юнитов показываем стандартную информацию
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                lines.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    lines.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    lines.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            # Атака и защита
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    lines.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    lines.append(f"Атака (маг): {unit.magic_attack}")
                lines.append(f"Защита (физ): {unit.phys_defense}")
                lines.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    lines.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                lines.append(f"Атака: {getattr(unit, 'attack', 0)}")
                lines.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            lines.append(f"Скорость: {unit.speed}")
            lines.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                lines.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    lines.append(f"Дальность: {unit.attack_range}")
        
        # Вычисляем размеры тултипа
        max_width = 0
        for line in lines:
            if line:
                width = font_small.size(line)[0]
                max_width = max(max_width, width)
        
        padding = 10
        line_height = 22
        tooltip_w = max_width + padding * 2
        tooltip_h = len(lines) * line_height + padding * 2
        
        # Позиция тултипа (рядом с курсором, но не выходя за экран)
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        if tooltip_x + tooltip_w > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_w - 20
        if tooltip_y + tooltip_h > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_h - 20
        
        # Фон тултипа
        tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surface.fill((40, 40, 80, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 150), (0, 0, tooltip_w, tooltip_h), 2)
        
        # Текст
        y_offset = padding
        for i, line in enumerate(lines):
            if line:
                if i == 0:  # Заголовок
                    text = font_bold.render(line, True, (255, 255, 180))
                else:
                    text = font_small.render(line, True, (220, 220, 220))
                tooltip_surface.blit(text, (padding, y_offset))
                y_offset += line_height
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_unit_info_window(self, unit):
        """Отрисовка окна информации о юните (при двойном клике)"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна
        window_w, window_h = 600, 500
        window_x = (SCREEN_WIDTH - window_w) // 2
        window_y = (SCREEN_HEIGHT - window_h) // 2
        
        # Фон окна (деревянный стиль)
        window_surface = pygame.Surface((window_w, window_h))
        for y in range(window_h):
            gradient = (
                int(150 - y * 0.2),
                int(110 - y * 0.15),
                int(80 - y * 0.1)
            )
            pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
        
        self.screen.blit(window_surface, (window_x, window_y))
        
        # Рамка
        pygame.draw.rect(self.screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=16)
        inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_rect, 2, border_radius=14)
        
        # Крестик для закрытия
        close_size = 30
        close_x = window_x + window_w - close_size - 10
        close_y = window_y + 10
        self.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        pygame.draw.rect(self.screen, (180, 60, 60), self.unit_info_close_button_rect, border_radius=5)
        font_close = pygame.font.Font(None, 32)
        close_text = font_close.render("×", True, (255, 255, 255))
        self.screen.blit(close_text, (close_x + 8, close_y + 2))
        
        # Заголовок
        font_title = pygame.font.Font(None, 48)
        title = font_title.render(f"{unit.unit_type.capitalize()}", True, (255, 245, 220))
        title_shadow = font_title.render(f"{unit.unit_type.capitalize()}", True, (60, 50, 40))
        title_x = window_x + (window_w - title.get_width()) // 2
        self.screen.blit(title_shadow, (title_x + 2, window_y + 20))
        self.screen.blit(title, (title_x, window_y + 18))
        
        # Изображение юнита (слева вверху)
        img_size = 120
        img_x = window_x + 30
        img_y = window_y + 80
        if hasattr(unit, 'image') and unit.image:
            img_scaled = pygame.transform.scale(unit.image, (img_size, img_size))
            self.screen.blit(img_scaled, (img_x, img_y))
        
        # Параметры (справа от изображения)
        font_small = pygame.font.Font(None, 24)
        param_x = img_x + img_size + 30
        param_y = window_y + 80
        line_height = 24  # Уменьшаем высоту строки для более компактного отображения
        max_param_width = window_w - param_x - 30  # Максимальная ширина для параметров
        
        # Проверяем, является ли юнит героем
        from .units import Hero
        is_hero = isinstance(unit, Hero)
        
        if is_hero:
            # Для героя показываем только параметры героя
            # Вычисляем базовую атаку в зависимости от класса
            if unit.hero_class == 'mage':
                base_attack = 5 + unit.spell_power
            else:  # warrior или archer
                base_attack = 5 + unit.attack
            
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            params.append(f"Базовая атака: {base_attack}")
            params.append(f"Атака: {unit.attack}")
            params.append(f"Защита: {unit.defense}")
            params.append(f"Сила магии: {unit.spell_power}")
            params.append(f"Знания: {unit.knowledge}")
            params.append(f"Мана: {unit.mana}/{unit.max_mana}")
            params.append(f"Удача: {unit.luck:+d} ({abs(unit.luck) * 5}% шанс двойного урона)")
            params.append(f"Боевой дух: {unit.combat_spirit:+d} ({abs(unit.combat_spirit) * 3}% шанс доп. хода)")
        else:
            # Для обычного юнита показываем параметры юнита
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                params.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    params.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    params.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    params.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    params.append(f"Атака (маг): {unit.magic_attack}")
                params.append(f"Защита (физ): {unit.phys_defense}")
                params.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    params.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                params.append(f"Атака: {getattr(unit, 'attack', 0)}")
                params.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            params.append(f"Скорость: {unit.speed}")
            params.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                params.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    params.append(f"Дальность: {unit.attack_range}")
            # Удача показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'luck'):
                luck = getattr(unit, 'luck', 0)
                params.append(f"Удача: {luck:+d} ({abs(luck) * 5}% шанс двойного урона)")
            # Боевой дух показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'combat_spirit'):
                combat_spirit = getattr(unit, 'combat_spirit', 0)
                params.append(f"Боевой дух: {combat_spirit:+d} ({abs(combat_spirit) * 3}% шанс доп. хода)")
            # Мораль показывается только в окне информации (не в тултипе), только для юнитов
            if hasattr(unit, 'morale') and not isinstance(unit, Hero):
                morale = getattr(unit, 'morale', 'good')
                morale_names = {
                    'excellent': 'Отличная',
                    'good': 'Хорошая',
                    'neutral': 'Нейтральная',
                    'bad': 'Плохая',
                    'awful': 'Ужасная'
                }
                morale_name = morale_names.get(morale, morale)
                params.append(f"Мораль: {morale_name}")
        
        # Отображаем параметры с переносом во второй столбец при необходимости
        current_y = param_y
        column1_x = param_x
        column1_max_y = param_y  # Максимальная высота первого столбца
        column2_x = param_x + max_param_width // 2 + 20  # Второй столбец правее
        max_params_per_column = 12  # Максимальное количество параметров в первом столбце
        current_column = 1
        column2_y = param_y  # Высота для второго столбца
        
        for i, param in enumerate(params):
            # Если параметров много, переходим во второй столбец
            if i >= max_params_per_column and current_column == 1:
                current_column = 2
                column2_y = param_y  # Начинаем с верха для второго столбца
                column1_max_y = current_y  # Сохраняем максимальную высоту первого столбца
            
            # Определяем позицию X в зависимости от столбца
            if current_column == 2:
                param_x_current = column2_x
                max_param_width_current = window_w - column2_x - 30
                current_y = column2_y
            else:
                param_x_current = column1_x
                max_param_width_current = max_param_width
                column1_max_y = current_y  # Обновляем максимальную высоту первого столбца
            
            # Проверяем, не выходит ли текст за пределы окна
            text_width = font_small.size(param)[0]
            if text_width > max_param_width_current:
                # Если текст слишком длинный, разбиваем на несколько строк
                words = param.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font_small.size(test_line)[0] <= max_param_width_current:
                        current_line = test_line
                    else:
                        if current_line:
                            text = font_small.render(current_line, True, (220, 220, 220))
                            self.screen.blit(text, (param_x_current, current_y))
                            current_y += line_height
                            if current_column == 2:
                                column2_y = current_y
                            else:
                                column1_max_y = current_y
                        current_line = word
                if current_line:
                    text = font_small.render(current_line, True, (220, 220, 220))
                    self.screen.blit(text, (param_x_current, current_y))
                    current_y += line_height
                    if current_column == 2:
                        column2_y = current_y
                    else:
                        column1_max_y = current_y
            else:
                text = font_small.render(param, True, (220, 220, 220))
                self.screen.blit(text, (param_x_current, current_y))
                current_y += line_height
                if current_column == 2:
                    column2_y = current_y
                else:
                    column1_max_y = current_y
        
        # Поля для способностей и пассивок (внизу) - динамически позиционируем
        # Оставляем минимум 120 пикселей снизу, но ограничиваем максимальное смещение
        min_effects_space = 120
        # Если использовались два столбца, берем максимальную высоту обоих столбцов
        if current_column == 2:
            param_bottom = max(column1_max_y, column2_y) + 20
        else:
            param_bottom = column1_max_y + 20  # Отступ снизу после параметров
        max_effects_y = window_y + window_h - min_effects_space  # Максимальная позиция (не ниже 120px от низа)
        abilities_y = min(max_effects_y, param_bottom + 20)  # Берем минимум, чтобы не уходило слишком далеко
        pygame.draw.line(self.screen, (100, 80, 60), (window_x + 20, abilities_y), (window_x + window_w - 20, abilities_y), 2)
        font_label = pygame.font.Font(None, 26)
        label = font_label.render("Временные эффекты:", True, (200, 180, 140))
        self.screen.blit(label, (window_x + 20, abilities_y + 10))
        
        # Собираем все временные эффекты
        effects = []
        effects_y = abilities_y + 35
        line_height_effects = 20
        max_lines = 3  # Максимум 3 строки эффектов
        
        # Защита
        if hasattr(unit, '_defend_this_round') and getattr(unit, '_defend_this_round', False):
            effects.append(("В защите", (100, 180, 255)))
        
        # Благословение/Проклятие
        if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
            effects.append((f"Благословение ({unit.attack_buff_turns} ход.)", (80, 255, 80)))
        if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
            effects.append((f"Проклятие ({unit.attack_debuff_turns} ход.)", (255, 80, 80)))
        
        # Руны
        if hasattr(unit, 'rune_shield_turns') and getattr(unit, 'rune_shield_turns', 0) > 0:
            effects.append((f"Руна защиты ({unit.rune_shield_turns} ход.)", (80, 255, 120)))
        if hasattr(unit, 'rune_magic_turns') and getattr(unit, 'rune_magic_turns', 0) > 0:
            effects.append((f"Руна магии ({unit.rune_magic_turns} ход.)", (200, 150, 255)))
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            effects.append((f"Руна берсерка ({unit.rune_berserker_turns} ход.)", (255, 80, 80)))
        if hasattr(unit, 'rune_haste_turns') and getattr(unit, 'rune_haste_turns', 0) > 0:
            effects.append((f"Руна скорости ({unit.rune_haste_turns} ход.)", (120, 200, 255)))
        
        # Замедление/Ускорение
        if hasattr(unit, 'slow_turns') and getattr(unit, 'slow_turns', 0) > 0:
            effects.append((f"Замедление ({unit.slow_turns} ход.)", (255, 120, 120)))
        if hasattr(unit, 'haste_turns') and getattr(unit, 'haste_turns', 0) > 0:
            effects.append((f"Ускорение ({unit.haste_turns} ход.)", (120, 255, 120)))
        
        # Ослепление
        if hasattr(unit, 'blindness_turns') and getattr(unit, 'blindness_turns', 0) > 0:
            effects.append((f"Ослепление ({unit.blindness_turns} ход.)", (200, 200, 80)))
        
        # Молитва
        if hasattr(unit, 'prayer_turns') and getattr(unit, 'prayer_turns', 0) > 0:
            effects.append((f"Молитва ({unit.prayer_turns} ход.)", (255, 255, 200)))
        
        # Точность
        if hasattr(unit, 'accuracy_turns') and getattr(unit, 'accuracy_turns', 0) > 0:
            effects.append((f"Точность ({unit.accuracy_turns} ход.)", (255, 200, 100)))
        
        # Каменная кожа
        if hasattr(unit, 'stone_skin_turns') and getattr(unit, 'stone_skin_turns', 0) > 0:
            effects.append((f"Каменная кожа ({unit.stone_skin_turns} ход.)", (200, 200, 200)))
        
        # Огненный щит
        if hasattr(unit, 'fire_shield_turns') and getattr(unit, 'fire_shield_turns', 0) > 0:
            effects.append((f"Огненный щит ({unit.fire_shield_turns} ход.)", (255, 100, 50)))
        
        # Ледяной щит
        if hasattr(unit, 'ice_shield_turns') and getattr(unit, 'ice_shield_turns', 0) > 0:
            effects.append((f"Ледяной щит ({unit.ice_shield_turns} ход.)", (100, 200, 255)))
        
        # Контрудар
        if hasattr(unit, 'counterstrike_turns') and getattr(unit, 'counterstrike_turns', 0) > 0:
            effects.append((f"Контрудар ({unit.counterstrike_turns} ход.)", (255, 180, 100)))
        
        # Слабость
        if hasattr(unit, 'weakness_turns') and getattr(unit, 'weakness_turns', 0) > 0:
            effects.append((f"Слабость ({unit.weakness_turns} ход.)", (200, 100, 100)))
        
        # Забвение
        if hasattr(unit, 'forget_turns') and getattr(unit, 'forget_turns', 0) > 0:
            effects.append((f"Забвение ({unit.forget_turns} ход.)", (150, 150, 150)))
        
        # Отображаем эффекты
        if effects:
            for i, (effect_name, effect_color) in enumerate(effects[:max_lines]):
                effect_text = font_small.render(effect_name, True, effect_color)
                self.screen.blit(effect_text, (window_x + 20, effects_y + i * line_height_effects))
            if len(effects) > max_lines:
                more_text = font_small.render(f"... и еще {len(effects) - max_lines}", True, (150, 150, 150))
                self.screen.blit(more_text, (window_x + 20, effects_y + max_lines * line_height_effects))
        else:
            no_effects = font_small.render("Нет активных эффектов", True, (150, 150, 150))
            self.screen.blit(no_effects, (window_x + 20, effects_y))
        
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Отладочное логирование начала применения заклинания
            self.anim_logger.log("SPELL_CAST_START", f"Герой кастует {spell.name} ({spell.icon}) target_type={spell.target_type}")
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
                spell_name = getattr(spell, 'name', '')
                spell_icon = getattr(spell, 'icon', '')
                # Проверяем мгновенные заклинания (без анимации полета снаряда)
                instant_spells = [
                    'lightning', 'weakness', 'bless', 'curse', 'slow', 'haste',
                    'heal', 'dispel', 'stone_skin', 'ice_shield', 'fire_shield',
                    'counterstrike', 'rune_shield', 'rune_haste', 'raise_dead',
                    'resurrection', 'undead_heal', 'forget', 'earth_spikes', 'rune_wall'
                ]
                is_instant_spell = (spell_icon in instant_spells or 
                                  spell_name in ['Молния', 'Слабость', 'Благословение', 'Проклятие', 
                                                'Замедление', 'Ускорение', 'Лечение', 'Снятие чар'] or
                                  any(keyword in spell_icon.lower() for keyword in ['lightning', 'weakness', 'bless', 'curse']))
                
                # Отладочное логирование
                self.anim_logger.log("SPELL_CHECK", f"name='{spell_name}' icon='{spell_icon}' instant={is_instant_spell}")
                
                # Логируем анимацию заклинания
                self.anim_logger.log_spell_animation(spell_name, spell_icon, self.selected_unit, target, is_instant_spell)
                
                if spell_icon == 'firearrow':
                    self.anim_logger.log("FIREARROW_ANIMATION", f"Огненная стрела от {self.selected_unit.unit_type} к {target.unit_type}")
                    self.animate_firearrow(self.selected_unit, target)
                elif not is_instant_spell:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    # Воспроизводим звук выстрела магов
                    if self.magic_shot_sound:
                        self.magic_shot_sound.play()
                    self.anim_logger.log_projectile_animation("magic_bolt", 
                        (self.selected_unit.x, self.selected_unit.y), 
                        (target.x, target.y), color)
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                # Применяем заклинание (для Молнии и Слабости - мгновенно, без анимации)
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
            if self.selected_unit.can_move(x, y, self.units, self.barriers):
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
                # Проверяем расстояние для определения типа атаки
                distance = abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)
                is_melee = (distance == 1)
                damage_already_applied = False  # Флаг для отслеживания применения урона
                
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    # Лучники и дальнобойные юниты
                    if is_melee:
                        # Ближний бой для лучников - только ближний бой, без стрел
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = max(1, self.selected_unit.get_current_attack() // 2)  # Половина урона
                        # Запоминаем параметры для контратаки (даже для лучников в ближнем бою)
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                    else:
                        # Дальняя атака - стреляем стрелами/снарядами, контратаки нет
                        target_is_melee_unit = False  # Дальняя атака, контратаки нет
                        start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                        end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                        
                        # Проверяем, является ли атакующий героем
                        is_hero = isinstance(self.selected_unit, Hero)
                        hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                        
                        # Определяем тип снаряда в зависимости от юнита/героя
                        if is_hero and hero_class == 'archer':
                            # Герой-лучник: стреляет стрелами
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            pygame.time.delay(150)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
                        elif self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                            # Обычные лучники стреляют стрелами - воспроизводим звуки
                            # Звук натяжения лука
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            # Небольшая задержка для звука натяжения
                            pygame.time.delay(150)
                            # Звук выстрела - используем новые звуки выстрелов (случайный выбор)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            # Анимация полета стрелы
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            # Звук попадания
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
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
                            # Воспроизводим звук выстрела магов
                            if self.magic_shot_sound:
                                self.magic_shot_sound.play()
                            animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                        # Перерисовываем экран, чтобы убрать снаряд
                        self.draw()
                        pygame.display.flip()
                        # Для дальнобойной атаки проверяем руну магии с учетом множителя дальности
                        mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit, is_ranged=True, target_x=x, target_y=y)
                        if mixed_damage is not None:
                            # Для руны магии используем смешанный урон
                            damage = None  # Будет применен через mixed_damage
                        else:
                            # Обычный расчет урона для дальнобойных
                            damage = self.selected_unit.ranged_damage(x, y)
                        
                        # Применяем урон для дальнобойных атак
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            elif damage is not None:
                                clicked_unit.take_damage(damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
                else:
                    # Обычные ближние бойцы и герои-воины
                    # Проверяем героя-воина - у него особая анимация
                    is_hero = isinstance(self.selected_unit, Hero)
                    hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                    
                    if is_hero and hero_class == 'warrior':
                        # Герой-воин: телепортация к цели
                        damage = self.selected_unit.get_current_attack()
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Сохраняем здоровье до атаки для вычисления урона
                        health_before = clicked_unit.health
                        # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                        squad_count_before_warrior = getattr(clicked_unit, 'squad_count', 1)
                        
                        # Создаем callback для применения урона (ТОЛЬКО урон, без последствий)
                        def apply_warrior_damage():
                            nonlocal damage_already_applied
                            damage_already_applied = True
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                        
                        # Вычисляем позицию рядом с целью
                        dx = clicked_unit.x - self.selected_unit.x
                        dy = clicked_unit.y - self.selected_unit.y
                        # Позиция рядом с целью (смещение в направлении атакующего)
                        if abs(dx) > abs(dy):
                            attack_x = clicked_unit.x - (1 if dx > 0 else -1)
                            attack_y = clicked_unit.y
                        else:
                            attack_x = clicked_unit.x
                            attack_y = clicked_unit.y - (1 if dy > 0 else -1)
                        
                        # Запускаем анимацию телепортации
                        animate_warrior_teleport(self.screen, 
                                                (self.selected_unit.x * CELL_SIZE, self.selected_unit.y * CELL_SIZE),
                                                (attack_x * CELL_SIZE, attack_y * CELL_SIZE),
                                                self.selected_unit.image,
                                                redraw_callback=self.draw,
                                                attack_sound_callback=lambda: (random.choice(self.human_melee_sounds).play() if self.human_melee_sounds and hasattr(random, 'choice') else None) if self.selected_unit.team in ['human', 'elf', 'dwarf'] else (random.choice(self.monster_melee_sounds).play() if self.monster_melee_sounds and hasattr(random, 'choice') else None),
                                                damage_callback=apply_warrior_damage,
                                                hide_attacker_pos=(self.selected_unit.x, self.selected_unit.y))
                        
                        # Вычисляем нанесенный урон
                        actual_damage = health_before - clicked_unit.health
                        
                        # ПОСЛЕ анимации обрабатываем последствия
                        squad_count_after_warrior = getattr(clicked_unit, 'squad_count', 1)
                        units_lost_warrior = squad_count_before_warrior - squad_count_after_warrior
                        if clicked_unit.health <= 0:
                            self.kill_unit(clicked_unit)
                            self.animate_queue_fade(clicked_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", уничтожено {units_lost_warrior} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", потеряно {units_lost_warrior} юнитов из отряда ({squad_count_after_warrior}/{squad_count_before_warrior})"
                            self.add_event(event_msg)
                            # Контратака происходит ПОСЛЕ анимации
                            self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки для героя-воина и переходим к следующему ходу
                        self.selected_unit.has_attacked = True
                        self.next_turn()
                        return
                    else:
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = self.selected_unit.get_current_attack()
                        # Запоминаем параметры для контратаки
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Применяем урон для обычных ближних бойцов
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                                # Контратака происходит ПОСЛЕ нанесения урона
                                self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
    
    def draw_unit_tooltip(self, unit):
        """Отрисовка тултипа юнита при зажатии правой кнопки мыши"""
        from .units import Hero
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)
        
        # Собираем информацию о юните
        lines = []
        lines.append(f"{unit.unit_type.capitalize()}")
        lines.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
        
        # Для героев показываем те же параметры что в окне информации (кроме удачи и боевого духа)
        if isinstance(unit, Hero):
            # Базовые параметры
            base_attack = getattr(unit, 'base_attack', None)
            if base_attack is None:
                # Вычисляем базовую атаку в зависимости от класса
                if unit.hero_class == 'mage':
                    base_attack = 5 + unit.spell_power
                else:  # warrior или archer
                    base_attack = 5 + unit.attack
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            knowledge = getattr(unit, 'knowledge', 0)
            spell_power = getattr(unit, 'spell_power', 0)
            mana = getattr(unit, 'mana', 0)
            max_mana = getattr(unit, 'max_mana', 0)
            
            lines.append(f"Базовая атака: {base_attack}")
            lines.append(f"Атака: {attack}")
            lines.append(f"Защита: {defense}")
            lines.append(f"Знания: {knowledge}")
            lines.append(f"Сила магии: {spell_power}")
            lines.append(f"Мана: {mana}/{max_mana}")
        else:
            # Для обычных юнитов показываем стандартную информацию
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                lines.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    lines.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    lines.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            # Атака и защита
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    lines.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    lines.append(f"Атака (маг): {unit.magic_attack}")
                lines.append(f"Защита (физ): {unit.phys_defense}")
                lines.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    lines.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                lines.append(f"Атака: {getattr(unit, 'attack', 0)}")
                lines.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            lines.append(f"Скорость: {unit.speed}")
            lines.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                lines.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    lines.append(f"Дальность: {unit.attack_range}")
        
        # Вычисляем размеры тултипа
        max_width = 0
        for line in lines:
            if line:
                width = font_small.size(line)[0]
                max_width = max(max_width, width)
        
        padding = 10
        line_height = 22
        tooltip_w = max_width + padding * 2
        tooltip_h = len(lines) * line_height + padding * 2
        
        # Позиция тултипа (рядом с курсором, но не выходя за экран)
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        if tooltip_x + tooltip_w > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_w - 20
        if tooltip_y + tooltip_h > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_h - 20
        
        # Фон тултипа
        tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surface.fill((40, 40, 80, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 150), (0, 0, tooltip_w, tooltip_h), 2)
        
        # Текст
        y_offset = padding
        for i, line in enumerate(lines):
            if line:
                if i == 0:  # Заголовок
                    text = font_bold.render(line, True, (255, 255, 180))
                else:
                    text = font_small.render(line, True, (220, 220, 220))
                tooltip_surface.blit(text, (padding, y_offset))
                y_offset += line_height
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_unit_info_window(self, unit):
        """Отрисовка окна информации о юните (при двойном клике)"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна
        window_w, window_h = 600, 500
        window_x = (SCREEN_WIDTH - window_w) // 2
        window_y = (SCREEN_HEIGHT - window_h) // 2
        
        # Фон окна (деревянный стиль)
        window_surface = pygame.Surface((window_w, window_h))
        for y in range(window_h):
            gradient = (
                int(150 - y * 0.2),
                int(110 - y * 0.15),
                int(80 - y * 0.1)
            )
            pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
        
        self.screen.blit(window_surface, (window_x, window_y))
        
        # Рамка
        pygame.draw.rect(self.screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=16)
        inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_rect, 2, border_radius=14)
        
        # Крестик для закрытия
        close_size = 30
        close_x = window_x + window_w - close_size - 10
        close_y = window_y + 10
        self.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        pygame.draw.rect(self.screen, (180, 60, 60), self.unit_info_close_button_rect, border_radius=5)
        font_close = pygame.font.Font(None, 32)
        close_text = font_close.render("×", True, (255, 255, 255))
        self.screen.blit(close_text, (close_x + 8, close_y + 2))
        
        # Заголовок
        font_title = pygame.font.Font(None, 48)
        title = font_title.render(f"{unit.unit_type.capitalize()}", True, (255, 245, 220))
        title_shadow = font_title.render(f"{unit.unit_type.capitalize()}", True, (60, 50, 40))
        title_x = window_x + (window_w - title.get_width()) // 2
        self.screen.blit(title_shadow, (title_x + 2, window_y + 20))
        self.screen.blit(title, (title_x, window_y + 18))
        
        # Изображение юнита (слева вверху)
        img_size = 120
        img_x = window_x + 30
        img_y = window_y + 80
        if hasattr(unit, 'image') and unit.image:
            img_scaled = pygame.transform.scale(unit.image, (img_size, img_size))
            self.screen.blit(img_scaled, (img_x, img_y))
        
        # Параметры (справа от изображения)
        font_small = pygame.font.Font(None, 24)
        param_x = img_x + img_size + 30
        param_y = window_y + 80
        line_height = 24  # Уменьшаем высоту строки для более компактного отображения
        max_param_width = window_w - param_x - 30  # Максимальная ширина для параметров
        
        # Проверяем, является ли юнит героем
        from .units import Hero
        is_hero = isinstance(unit, Hero)
        
        if is_hero:
            # Для героя показываем только параметры героя
            # Вычисляем базовую атаку в зависимости от класса
            if unit.hero_class == 'mage':
                base_attack = 5 + unit.spell_power
            else:  # warrior или archer
                base_attack = 5 + unit.attack
            
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            params.append(f"Базовая атака: {base_attack}")
            params.append(f"Атака: {unit.attack}")
            params.append(f"Защита: {unit.defense}")
            params.append(f"Сила магии: {unit.spell_power}")
            params.append(f"Знания: {unit.knowledge}")
            params.append(f"Мана: {unit.mana}/{unit.max_mana}")
            params.append(f"Удача: {unit.luck:+d} ({abs(unit.luck) * 5}% шанс двойного урона)")
            params.append(f"Боевой дух: {unit.combat_spirit:+d} ({abs(unit.combat_spirit) * 3}% шанс доп. хода)")
        else:
            # Для обычного юнита показываем параметры юнита
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                params.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    params.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    params.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    params.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    params.append(f"Атака (маг): {unit.magic_attack}")
                params.append(f"Защита (физ): {unit.phys_defense}")
                params.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    params.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                params.append(f"Атака: {getattr(unit, 'attack', 0)}")
                params.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            params.append(f"Скорость: {unit.speed}")
            params.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                params.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    params.append(f"Дальность: {unit.attack_range}")
            # Удача показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'luck'):
                luck = getattr(unit, 'luck', 0)
                params.append(f"Удача: {luck:+d} ({abs(luck) * 5}% шанс двойного урона)")
            # Боевой дух показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'combat_spirit'):
                combat_spirit = getattr(unit, 'combat_spirit', 0)
                params.append(f"Боевой дух: {combat_spirit:+d} ({abs(combat_spirit) * 3}% шанс доп. хода)")
            # Мораль показывается только в окне информации (не в тултипе), только для юнитов
            if hasattr(unit, 'morale') and not isinstance(unit, Hero):
                morale = getattr(unit, 'morale', 'good')
                morale_names = {
                    'excellent': 'Отличная',
                    'good': 'Хорошая',
                    'neutral': 'Нейтральная',
                    'bad': 'Плохая',
                    'awful': 'Ужасная'
                }
                morale_name = morale_names.get(morale, morale)
                params.append(f"Мораль: {morale_name}")
        
        # Отображаем параметры с переносом во второй столбец при необходимости
        current_y = param_y
        column1_x = param_x
        column1_max_y = param_y  # Максимальная высота первого столбца
        column2_x = param_x + max_param_width // 2 + 20  # Второй столбец правее
        max_params_per_column = 12  # Максимальное количество параметров в первом столбце
        current_column = 1
        column2_y = param_y  # Высота для второго столбца
        
        for i, param in enumerate(params):
            # Если параметров много, переходим во второй столбец
            if i >= max_params_per_column and current_column == 1:
                current_column = 2
                column2_y = param_y  # Начинаем с верха для второго столбца
                column1_max_y = current_y  # Сохраняем максимальную высоту первого столбца
            
            # Определяем позицию X в зависимости от столбца
            if current_column == 2:
                param_x_current = column2_x
                max_param_width_current = window_w - column2_x - 30
                current_y = column2_y
            else:
                param_x_current = column1_x
                max_param_width_current = max_param_width
                column1_max_y = current_y  # Обновляем максимальную высоту первого столбца
            
            # Проверяем, не выходит ли текст за пределы окна
            text_width = font_small.size(param)[0]
            if text_width > max_param_width_current:
                # Если текст слишком длинный, разбиваем на несколько строк
                words = param.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font_small.size(test_line)[0] <= max_param_width_current:
                        current_line = test_line
                    else:
                        if current_line:
                            text = font_small.render(current_line, True, (220, 220, 220))
                            self.screen.blit(text, (param_x_current, current_y))
                            current_y += line_height
                            if current_column == 2:
                                column2_y = current_y
                            else:
                                column1_max_y = current_y
                        current_line = word
                if current_line:
                    text = font_small.render(current_line, True, (220, 220, 220))
                    self.screen.blit(text, (param_x_current, current_y))
                    current_y += line_height
                    if current_column == 2:
                        column2_y = current_y
                    else:
                        column1_max_y = current_y
            else:
                text = font_small.render(param, True, (220, 220, 220))
                self.screen.blit(text, (param_x_current, current_y))
                current_y += line_height
                if current_column == 2:
                    column2_y = current_y
                else:
                    column1_max_y = current_y
        
        # Поля для способностей и пассивок (внизу) - динамически позиционируем
        # Оставляем минимум 120 пикселей снизу, но ограничиваем максимальное смещение
        min_effects_space = 120
        # Если использовались два столбца, берем максимальную высоту обоих столбцов
        if current_column == 2:
            param_bottom = max(column1_max_y, column2_y) + 20
        else:
            param_bottom = column1_max_y + 20  # Отступ снизу после параметров
        max_effects_y = window_y + window_h - min_effects_space  # Максимальная позиция (не ниже 120px от низа)
        abilities_y = min(max_effects_y, param_bottom + 20)  # Берем минимум, чтобы не уходило слишком далеко
        pygame.draw.line(self.screen, (100, 80, 60), (window_x + 20, abilities_y), (window_x + window_w - 20, abilities_y), 2)
        font_label = pygame.font.Font(None, 26)
        label = font_label.render("Временные эффекты:", True, (200, 180, 140))
        self.screen.blit(label, (window_x + 20, abilities_y + 10))
        
        # Собираем все временные эффекты
        effects = []
        effects_y = abilities_y + 35
        line_height_effects = 20
        max_lines = 3  # Максимум 3 строки эффектов
        
        # Защита
        if hasattr(unit, '_defend_this_round') and getattr(unit, '_defend_this_round', False):
            effects.append(("В защите", (100, 180, 255)))
        
        # Благословение/Проклятие
        if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
            effects.append((f"Благословение ({unit.attack_buff_turns} ход.)", (80, 255, 80)))
        if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
            effects.append((f"Проклятие ({unit.attack_debuff_turns} ход.)", (255, 80, 80)))
        
        # Руны
        if hasattr(unit, 'rune_shield_turns') and getattr(unit, 'rune_shield_turns', 0) > 0:
            effects.append((f"Руна защиты ({unit.rune_shield_turns} ход.)", (80, 255, 120)))
        if hasattr(unit, 'rune_magic_turns') and getattr(unit, 'rune_magic_turns', 0) > 0:
            effects.append((f"Руна магии ({unit.rune_magic_turns} ход.)", (200, 150, 255)))
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            effects.append((f"Руна берсерка ({unit.rune_berserker_turns} ход.)", (255, 80, 80)))
        if hasattr(unit, 'rune_haste_turns') and getattr(unit, 'rune_haste_turns', 0) > 0:
            effects.append((f"Руна скорости ({unit.rune_haste_turns} ход.)", (120, 200, 255)))
        
        # Замедление/Ускорение
        if hasattr(unit, 'slow_turns') and getattr(unit, 'slow_turns', 0) > 0:
            effects.append((f"Замедление ({unit.slow_turns} ход.)", (255, 120, 120)))
        if hasattr(unit, 'haste_turns') and getattr(unit, 'haste_turns', 0) > 0:
            effects.append((f"Ускорение ({unit.haste_turns} ход.)", (120, 255, 120)))
        
        # Ослепление
        if hasattr(unit, 'blindness_turns') and getattr(unit, 'blindness_turns', 0) > 0:
            effects.append((f"Ослепление ({unit.blindness_turns} ход.)", (200, 200, 80)))
        
        # Молитва
        if hasattr(unit, 'prayer_turns') and getattr(unit, 'prayer_turns', 0) > 0:
            effects.append((f"Молитва ({unit.prayer_turns} ход.)", (255, 255, 200)))
        
        # Точность
        if hasattr(unit, 'accuracy_turns') and getattr(unit, 'accuracy_turns', 0) > 0:
            effects.append((f"Точность ({unit.accuracy_turns} ход.)", (255, 200, 100)))
        
        # Каменная кожа
        if hasattr(unit, 'stone_skin_turns') and getattr(unit, 'stone_skin_turns', 0) > 0:
            effects.append((f"Каменная кожа ({unit.stone_skin_turns} ход.)", (200, 200, 200)))
        
        # Огненный щит
        if hasattr(unit, 'fire_shield_turns') and getattr(unit, 'fire_shield_turns', 0) > 0:
            effects.append((f"Огненный щит ({unit.fire_shield_turns} ход.)", (255, 100, 50)))
        
        # Ледяной щит
        if hasattr(unit, 'ice_shield_turns') and getattr(unit, 'ice_shield_turns', 0) > 0:
            effects.append((f"Ледяной щит ({unit.ice_shield_turns} ход.)", (100, 200, 255)))
        
        # Контрудар
        if hasattr(unit, 'counterstrike_turns') and getattr(unit, 'counterstrike_turns', 0) > 0:
            effects.append((f"Контрудар ({unit.counterstrike_turns} ход.)", (255, 180, 100)))
        
        # Слабость
        if hasattr(unit, 'weakness_turns') and getattr(unit, 'weakness_turns', 0) > 0:
            effects.append((f"Слабость ({unit.weakness_turns} ход.)", (200, 100, 100)))
        
        # Забвение
        if hasattr(unit, 'forget_turns') and getattr(unit, 'forget_turns', 0) > 0:
            effects.append((f"Забвение ({unit.forget_turns} ход.)", (150, 150, 150)))
        
        # Отображаем эффекты
        if effects:
            for i, (effect_name, effect_color) in enumerate(effects[:max_lines]):
                effect_text = font_small.render(effect_name, True, effect_color)
                self.screen.blit(effect_text, (window_x + 20, effects_y + i * line_height_effects))
            if len(effects) > max_lines:
                more_text = font_small.render(f"... и еще {len(effects) - max_lines}", True, (150, 150, 150))
                self.screen.blit(more_text, (window_x + 20, effects_y + max_lines * line_height_effects))
        else:
            no_effects = font_small.render("Нет активных эффектов", True, (150, 150, 150))
            self.screen.blit(no_effects, (window_x + 20, effects_y))
        
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Отладочное логирование начала применения заклинания
            self.anim_logger.log("SPELL_CAST_START", f"Герой кастует {spell.name} ({spell.icon}) target_type={spell.target_type}")
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
                spell_name = getattr(spell, 'name', '')
                spell_icon = getattr(spell, 'icon', '')
                # Проверяем мгновенные заклинания (без анимации полета снаряда)
                instant_spells = [
                    'lightning', 'weakness', 'bless', 'curse', 'slow', 'haste',
                    'heal', 'dispel', 'stone_skin', 'ice_shield', 'fire_shield',
                    'counterstrike', 'rune_shield', 'rune_haste', 'raise_dead',
                    'resurrection', 'undead_heal', 'forget', 'earth_spikes', 'rune_wall'
                ]
                is_instant_spell = (spell_icon in instant_spells or 
                                  spell_name in ['Молния', 'Слабость', 'Благословение', 'Проклятие', 
                                                'Замедление', 'Ускорение', 'Лечение', 'Снятие чар'] or
                                  any(keyword in spell_icon.lower() for keyword in ['lightning', 'weakness', 'bless', 'curse']))
                
                # Отладочное логирование
                self.anim_logger.log("SPELL_CHECK", f"name='{spell_name}' icon='{spell_icon}' instant={is_instant_spell}")
                
                # Логируем анимацию заклинания
                self.anim_logger.log_spell_animation(spell_name, spell_icon, self.selected_unit, target, is_instant_spell)
                
                if spell_icon == 'firearrow':
                    self.anim_logger.log("FIREARROW_ANIMATION", f"Огненная стрела от {self.selected_unit.unit_type} к {target.unit_type}")
                    self.animate_firearrow(self.selected_unit, target)
                elif not is_instant_spell:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    # Воспроизводим звук выстрела магов
                    if self.magic_shot_sound:
                        self.magic_shot_sound.play()
                    self.anim_logger.log_projectile_animation("magic_bolt", 
                        (self.selected_unit.x, self.selected_unit.y), 
                        (target.x, target.y), color)
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                # Применяем заклинание (для Молнии и Слабости - мгновенно, без анимации)
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
            if self.selected_unit.can_move(x, y, self.units, self.barriers):
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
                # Проверяем расстояние для определения типа атаки
                distance = abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)
                is_melee = (distance == 1)
                damage_already_applied = False  # Флаг для отслеживания применения урона
                
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    # Лучники и дальнобойные юниты
                    if is_melee:
                        # Ближний бой для лучников - только ближний бой, без стрел
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = max(1, self.selected_unit.get_current_attack() // 2)  # Половина урона
                        # Запоминаем параметры для контратаки (даже для лучников в ближнем бою)
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                    else:
                        # Дальняя атака - стреляем стрелами/снарядами, контратаки нет
                        target_is_melee_unit = False  # Дальняя атака, контратаки нет
                        start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                        end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                        
                        # Проверяем, является ли атакующий героем
                        is_hero = isinstance(self.selected_unit, Hero)
                        hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                        
                        # Определяем тип снаряда в зависимости от юнита/героя
                        if is_hero and hero_class == 'archer':
                            # Герой-лучник: стреляет стрелами
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            pygame.time.delay(150)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
                        elif self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                            # Обычные лучники стреляют стрелами - воспроизводим звуки
                            # Звук натяжения лука
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            # Небольшая задержка для звука натяжения
                            pygame.time.delay(150)
                            # Звук выстрела - используем новые звуки выстрелов (случайный выбор)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            # Анимация полета стрелы
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            # Звук попадания
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
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
                            # Воспроизводим звук выстрела магов
                            if self.magic_shot_sound:
                                self.magic_shot_sound.play()
                            animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                        # Перерисовываем экран, чтобы убрать снаряд
                        self.draw()
                        pygame.display.flip()
                        # Для дальнобойной атаки проверяем руну магии с учетом множителя дальности
                        mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit, is_ranged=True, target_x=x, target_y=y)
                        if mixed_damage is not None:
                            # Для руны магии используем смешанный урон
                            damage = None  # Будет применен через mixed_damage
                        else:
                            # Обычный расчет урона для дальнобойных
                            damage = self.selected_unit.ranged_damage(x, y)
                        
                        # Применяем урон для дальнобойных атак
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            elif damage is not None:
                                clicked_unit.take_damage(damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
                else:
                    # Обычные ближние бойцы и герои-воины
                    # Проверяем героя-воина - у него особая анимация
                    is_hero = isinstance(self.selected_unit, Hero)
                    hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                    
                    if is_hero and hero_class == 'warrior':
                        # Герой-воин: телепортация к цели
                        damage = self.selected_unit.get_current_attack()
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Сохраняем здоровье до атаки для вычисления урона
                        health_before = clicked_unit.health
                        # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                        squad_count_before_warrior = getattr(clicked_unit, 'squad_count', 1)
                        
                        # Создаем callback для применения урона (ТОЛЬКО урон, без последствий)
                        def apply_warrior_damage():
                            nonlocal damage_already_applied
                            damage_already_applied = True
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                        
                        # Вычисляем позицию рядом с целью
                        dx = clicked_unit.x - self.selected_unit.x
                        dy = clicked_unit.y - self.selected_unit.y
                        # Позиция рядом с целью (смещение в направлении атакующего)
                        if abs(dx) > abs(dy):
                            attack_x = clicked_unit.x - (1 if dx > 0 else -1)
                            attack_y = clicked_unit.y
                        else:
                            attack_x = clicked_unit.x
                            attack_y = clicked_unit.y - (1 if dy > 0 else -1)
                        
                        # Запускаем анимацию телепортации
                        animate_warrior_teleport(self.screen, 
                                                (self.selected_unit.x * CELL_SIZE, self.selected_unit.y * CELL_SIZE),
                                                (attack_x * CELL_SIZE, attack_y * CELL_SIZE),
                                                self.selected_unit.image,
                                                redraw_callback=self.draw,
                                                attack_sound_callback=lambda: (random.choice(self.human_melee_sounds).play() if self.human_melee_sounds and hasattr(random, 'choice') else None) if self.selected_unit.team in ['human', 'elf', 'dwarf'] else (random.choice(self.monster_melee_sounds).play() if self.monster_melee_sounds and hasattr(random, 'choice') else None),
                                                damage_callback=apply_warrior_damage,
                                                hide_attacker_pos=(self.selected_unit.x, self.selected_unit.y))
                        
                        # Вычисляем нанесенный урон
                        actual_damage = health_before - clicked_unit.health
                        
                        # ПОСЛЕ анимации обрабатываем последствия
                        squad_count_after_warrior = getattr(clicked_unit, 'squad_count', 1)
                        units_lost_warrior = squad_count_before_warrior - squad_count_after_warrior
                        if clicked_unit.health <= 0:
                            self.kill_unit(clicked_unit)
                            self.animate_queue_fade(clicked_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", уничтожено {units_lost_warrior} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", потеряно {units_lost_warrior} юнитов из отряда ({squad_count_after_warrior}/{squad_count_before_warrior})"
                            self.add_event(event_msg)
                            # Контратака происходит ПОСЛЕ анимации
                            self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки для героя-воина и переходим к следующему ходу
                        self.selected_unit.has_attacked = True
                        self.next_turn()
                        return
                    else:
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = self.selected_unit.get_current_attack()
                        # Запоминаем параметры для контратаки
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Применяем урон для обычных ближних бойцов
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                                # Контратака происходит ПОСЛЕ нанесения урона
                                self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
    
    def draw_unit_tooltip(self, unit):
        """Отрисовка тултипа юнита при зажатии правой кнопки мыши"""
        from .units import Hero
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)
        
        # Собираем информацию о юните
        lines = []
        lines.append(f"{unit.unit_type.capitalize()}")
        lines.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
        
        # Для героев показываем те же параметры что в окне информации (кроме удачи и боевого духа)
        if isinstance(unit, Hero):
            # Базовые параметры
            base_attack = getattr(unit, 'base_attack', None)
            if base_attack is None:
                # Вычисляем базовую атаку в зависимости от класса
                if unit.hero_class == 'mage':
                    base_attack = 5 + unit.spell_power
                else:  # warrior или archer
                    base_attack = 5 + unit.attack
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            knowledge = getattr(unit, 'knowledge', 0)
            spell_power = getattr(unit, 'spell_power', 0)
            mana = getattr(unit, 'mana', 0)
            max_mana = getattr(unit, 'max_mana', 0)
            
            lines.append(f"Базовая атака: {base_attack}")
            lines.append(f"Атака: {attack}")
            lines.append(f"Защита: {defense}")
            lines.append(f"Знания: {knowledge}")
            lines.append(f"Сила магии: {spell_power}")
            lines.append(f"Мана: {mana}/{max_mana}")
        else:
            # Для обычных юнитов показываем стандартную информацию
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                lines.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    lines.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    lines.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            # Атака и защита
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    lines.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    lines.append(f"Атака (маг): {unit.magic_attack}")
                lines.append(f"Защита (физ): {unit.phys_defense}")
                lines.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    lines.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                lines.append(f"Атака: {getattr(unit, 'attack', 0)}")
                lines.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            lines.append(f"Скорость: {unit.speed}")
            lines.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                lines.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    lines.append(f"Дальность: {unit.attack_range}")
        
        # Вычисляем размеры тултипа
        max_width = 0
        for line in lines:
            if line:
                width = font_small.size(line)[0]
                max_width = max(max_width, width)
        
        padding = 10
        line_height = 22
        tooltip_w = max_width + padding * 2
        tooltip_h = len(lines) * line_height + padding * 2
        
        # Позиция тултипа (рядом с курсором, но не выходя за экран)
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        if tooltip_x + tooltip_w > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_w - 20
        if tooltip_y + tooltip_h > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_h - 20
        
        # Фон тултипа
        tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surface.fill((40, 40, 80, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 150), (0, 0, tooltip_w, tooltip_h), 2)
        
        # Текст
        y_offset = padding
        for i, line in enumerate(lines):
            if line:
                if i == 0:  # Заголовок
                    text = font_bold.render(line, True, (255, 255, 180))
                else:
                    text = font_small.render(line, True, (220, 220, 220))
                tooltip_surface.blit(text, (padding, y_offset))
                y_offset += line_height
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_unit_info_window(self, unit):
        """Отрисовка окна информации о юните (при двойном клике)"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна
        window_w, window_h = 600, 500
        window_x = (SCREEN_WIDTH - window_w) // 2
        window_y = (SCREEN_HEIGHT - window_h) // 2
        
        # Фон окна (деревянный стиль)
        window_surface = pygame.Surface((window_w, window_h))
        for y in range(window_h):
            gradient = (
                int(150 - y * 0.2),
                int(110 - y * 0.15),
                int(80 - y * 0.1)
            )
            pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
        
        self.screen.blit(window_surface, (window_x, window_y))
        
        # Рамка
        pygame.draw.rect(self.screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=16)
        inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_rect, 2, border_radius=14)
        
        # Крестик для закрытия
        close_size = 30
        close_x = window_x + window_w - close_size - 10
        close_y = window_y + 10
        self.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        pygame.draw.rect(self.screen, (180, 60, 60), self.unit_info_close_button_rect, border_radius=5)
        font_close = pygame.font.Font(None, 32)
        close_text = font_close.render("×", True, (255, 255, 255))
        self.screen.blit(close_text, (close_x + 8, close_y + 2))
        
        # Заголовок
        font_title = pygame.font.Font(None, 48)
        title = font_title.render(f"{unit.unit_type.capitalize()}", True, (255, 245, 220))
        title_shadow = font_title.render(f"{unit.unit_type.capitalize()}", True, (60, 50, 40))
        title_x = window_x + (window_w - title.get_width()) // 2
        self.screen.blit(title_shadow, (title_x + 2, window_y + 20))
        self.screen.blit(title, (title_x, window_y + 18))
        
        # Изображение юнита (слева вверху)
        img_size = 120
        img_x = window_x + 30
        img_y = window_y + 80
        if hasattr(unit, 'image') and unit.image:
            img_scaled = pygame.transform.scale(unit.image, (img_size, img_size))
            self.screen.blit(img_scaled, (img_x, img_y))
        
        # Параметры (справа от изображения)
        font_small = pygame.font.Font(None, 24)
        param_x = img_x + img_size + 30
        param_y = window_y + 80
        line_height = 24  # Уменьшаем высоту строки для более компактного отображения
        max_param_width = window_w - param_x - 30  # Максимальная ширина для параметров
        
        # Проверяем, является ли юнит героем
        from .units import Hero
        is_hero = isinstance(unit, Hero)
        
        if is_hero:
            # Для героя показываем только параметры героя
            # Вычисляем базовую атаку в зависимости от класса
            if unit.hero_class == 'mage':
                base_attack = 5 + unit.spell_power
            else:  # warrior или archer
                base_attack = 5 + unit.attack
            
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            params.append(f"Базовая атака: {base_attack}")
            params.append(f"Атака: {unit.attack}")
            params.append(f"Защита: {unit.defense}")
            params.append(f"Сила магии: {unit.spell_power}")
            params.append(f"Знания: {unit.knowledge}")
            params.append(f"Мана: {unit.mana}/{unit.max_mana}")
            params.append(f"Удача: {unit.luck:+d} ({abs(unit.luck) * 5}% шанс двойного урона)")
            params.append(f"Боевой дух: {unit.combat_spirit:+d} ({abs(unit.combat_spirit) * 3}% шанс доп. хода)")
        else:
            # Для обычного юнита показываем параметры юнита
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                params.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    params.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    params.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    params.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    params.append(f"Атака (маг): {unit.magic_attack}")
                params.append(f"Защита (физ): {unit.phys_defense}")
                params.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    params.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                params.append(f"Атака: {getattr(unit, 'attack', 0)}")
                params.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            params.append(f"Скорость: {unit.speed}")
            params.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                params.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    params.append(f"Дальность: {unit.attack_range}")
            # Удача показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'luck'):
                luck = getattr(unit, 'luck', 0)
                params.append(f"Удача: {luck:+d} ({abs(luck) * 5}% шанс двойного урона)")
            # Боевой дух показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'combat_spirit'):
                combat_spirit = getattr(unit, 'combat_spirit', 0)
                params.append(f"Боевой дух: {combat_spirit:+d} ({abs(combat_spirit) * 3}% шанс доп. хода)")
            # Мораль показывается только в окне информации (не в тултипе), только для юнитов
            if hasattr(unit, 'morale') and not isinstance(unit, Hero):
                morale = getattr(unit, 'morale', 'good')
                morale_names = {
                    'excellent': 'Отличная',
                    'good': 'Хорошая',
                    'neutral': 'Нейтральная',
                    'bad': 'Плохая',
                    'awful': 'Ужасная'
                }
                morale_name = morale_names.get(morale, morale)
                params.append(f"Мораль: {morale_name}")
        
        # Отображаем параметры с переносом во второй столбец при необходимости
        current_y = param_y
        column1_x = param_x
        column1_max_y = param_y  # Максимальная высота первого столбца
        column2_x = param_x + max_param_width // 2 + 20  # Второй столбец правее
        max_params_per_column = 12  # Максимальное количество параметров в первом столбце
        current_column = 1
        column2_y = param_y  # Высота для второго столбца
        
        for i, param in enumerate(params):
            # Если параметров много, переходим во второй столбец
            if i >= max_params_per_column and current_column == 1:
                current_column = 2
                column2_y = param_y  # Начинаем с верха для второго столбца
                column1_max_y = current_y  # Сохраняем максимальную высоту первого столбца
            
            # Определяем позицию X в зависимости от столбца
            if current_column == 2:
                param_x_current = column2_x
                max_param_width_current = window_w - column2_x - 30
                current_y = column2_y
            else:
                param_x_current = column1_x
                max_param_width_current = max_param_width
                column1_max_y = current_y  # Обновляем максимальную высоту первого столбца
            
            # Проверяем, не выходит ли текст за пределы окна
            text_width = font_small.size(param)[0]
            if text_width > max_param_width_current:
                # Если текст слишком длинный, разбиваем на несколько строк
                words = param.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font_small.size(test_line)[0] <= max_param_width_current:
                        current_line = test_line
                    else:
                        if current_line:
                            text = font_small.render(current_line, True, (220, 220, 220))
                            self.screen.blit(text, (param_x_current, current_y))
                            current_y += line_height
                            if current_column == 2:
                                column2_y = current_y
                            else:
                                column1_max_y = current_y
                        current_line = word
                if current_line:
                    text = font_small.render(current_line, True, (220, 220, 220))
                    self.screen.blit(text, (param_x_current, current_y))
                    current_y += line_height
                    if current_column == 2:
                        column2_y = current_y
                    else:
                        column1_max_y = current_y
            else:
                text = font_small.render(param, True, (220, 220, 220))
                self.screen.blit(text, (param_x_current, current_y))
                current_y += line_height
                if current_column == 2:
                    column2_y = current_y
                else:
                    column1_max_y = current_y
        
        # Поля для способностей и пассивок (внизу) - динамически позиционируем
        # Оставляем минимум 120 пикселей снизу, но ограничиваем максимальное смещение
        min_effects_space = 120
        # Если использовались два столбца, берем максимальную высоту обоих столбцов
        if current_column == 2:
            param_bottom = max(column1_max_y, column2_y) + 20
        else:
            param_bottom = column1_max_y + 20  # Отступ снизу после параметров
        max_effects_y = window_y + window_h - min_effects_space  # Максимальная позиция (не ниже 120px от низа)
        abilities_y = min(max_effects_y, param_bottom + 20)  # Берем минимум, чтобы не уходило слишком далеко
        pygame.draw.line(self.screen, (100, 80, 60), (window_x + 20, abilities_y), (window_x + window_w - 20, abilities_y), 2)
        font_label = pygame.font.Font(None, 26)
        label = font_label.render("Временные эффекты:", True, (200, 180, 140))
        self.screen.blit(label, (window_x + 20, abilities_y + 10))
        
        # Собираем все временные эффекты
        effects = []
        effects_y = abilities_y + 35
        line_height_effects = 20
        max_lines = 3  # Максимум 3 строки эффектов
        
        # Защита
        if hasattr(unit, '_defend_this_round') and getattr(unit, '_defend_this_round', False):
            effects.append(("В защите", (100, 180, 255)))
        
        # Благословение/Проклятие
        if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
            effects.append((f"Благословение ({unit.attack_buff_turns} ход.)", (80, 255, 80)))
        if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
            effects.append((f"Проклятие ({unit.attack_debuff_turns} ход.)", (255, 80, 80)))
        
        # Руны
        if hasattr(unit, 'rune_shield_turns') and getattr(unit, 'rune_shield_turns', 0) > 0:
            effects.append((f"Руна защиты ({unit.rune_shield_turns} ход.)", (80, 255, 120)))
        if hasattr(unit, 'rune_magic_turns') and getattr(unit, 'rune_magic_turns', 0) > 0:
            effects.append((f"Руна магии ({unit.rune_magic_turns} ход.)", (200, 150, 255)))
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            effects.append((f"Руна берсерка ({unit.rune_berserker_turns} ход.)", (255, 80, 80)))
        if hasattr(unit, 'rune_haste_turns') and getattr(unit, 'rune_haste_turns', 0) > 0:
            effects.append((f"Руна скорости ({unit.rune_haste_turns} ход.)", (120, 200, 255)))
        
        # Замедление/Ускорение
        if hasattr(unit, 'slow_turns') and getattr(unit, 'slow_turns', 0) > 0:
            effects.append((f"Замедление ({unit.slow_turns} ход.)", (255, 120, 120)))
        if hasattr(unit, 'haste_turns') and getattr(unit, 'haste_turns', 0) > 0:
            effects.append((f"Ускорение ({unit.haste_turns} ход.)", (120, 255, 120)))
        
        # Ослепление
        if hasattr(unit, 'blindness_turns') and getattr(unit, 'blindness_turns', 0) > 0:
            effects.append((f"Ослепление ({unit.blindness_turns} ход.)", (200, 200, 80)))
        
        # Молитва
        if hasattr(unit, 'prayer_turns') and getattr(unit, 'prayer_turns', 0) > 0:
            effects.append((f"Молитва ({unit.prayer_turns} ход.)", (255, 255, 200)))
        
        # Точность
        if hasattr(unit, 'accuracy_turns') and getattr(unit, 'accuracy_turns', 0) > 0:
            effects.append((f"Точность ({unit.accuracy_turns} ход.)", (255, 200, 100)))
        
        # Каменная кожа
        if hasattr(unit, 'stone_skin_turns') and getattr(unit, 'stone_skin_turns', 0) > 0:
            effects.append((f"Каменная кожа ({unit.stone_skin_turns} ход.)", (200, 200, 200)))
        
        # Огненный щит
        if hasattr(unit, 'fire_shield_turns') and getattr(unit, 'fire_shield_turns', 0) > 0:
            effects.append((f"Огненный щит ({unit.fire_shield_turns} ход.)", (255, 100, 50)))
        
        # Ледяной щит
        if hasattr(unit, 'ice_shield_turns') and getattr(unit, 'ice_shield_turns', 0) > 0:
            effects.append((f"Ледяной щит ({unit.ice_shield_turns} ход.)", (100, 200, 255)))
        
        # Контрудар
        if hasattr(unit, 'counterstrike_turns') and getattr(unit, 'counterstrike_turns', 0) > 0:
            effects.append((f"Контрудар ({unit.counterstrike_turns} ход.)", (255, 180, 100)))
        
        # Слабость
        if hasattr(unit, 'weakness_turns') and getattr(unit, 'weakness_turns', 0) > 0:
            effects.append((f"Слабость ({unit.weakness_turns} ход.)", (200, 100, 100)))
        
        # Забвение
        if hasattr(unit, 'forget_turns') and getattr(unit, 'forget_turns', 0) > 0:
            effects.append((f"Забвение ({unit.forget_turns} ход.)", (150, 150, 150)))
        
        # Отображаем эффекты
        if effects:
            for i, (effect_name, effect_color) in enumerate(effects[:max_lines]):
                effect_text = font_small.render(effect_name, True, effect_color)
                self.screen.blit(effect_text, (window_x + 20, effects_y + i * line_height_effects))
            if len(effects) > max_lines:
                more_text = font_small.render(f"... и еще {len(effects) - max_lines}", True, (150, 150, 150))
                self.screen.blit(more_text, (window_x + 20, effects_y + max_lines * line_height_effects))
        else:
            no_effects = font_small.render("Нет активных эффектов", True, (150, 150, 150))
            self.screen.blit(no_effects, (window_x + 20, effects_y))
        
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Отладочное логирование начала применения заклинания
            self.anim_logger.log("SPELL_CAST_START", f"Герой кастует {spell.name} ({spell.icon}) target_type={spell.target_type}")
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
                spell_name = getattr(spell, 'name', '')
                spell_icon = getattr(spell, 'icon', '')
                # Проверяем мгновенные заклинания (без анимации полета снаряда)
                instant_spells = [
                    'lightning', 'weakness', 'bless', 'curse', 'slow', 'haste',
                    'heal', 'dispel', 'stone_skin', 'ice_shield', 'fire_shield',
                    'counterstrike', 'rune_shield', 'rune_haste', 'raise_dead',
                    'resurrection', 'undead_heal', 'forget', 'earth_spikes', 'rune_wall'
                ]
                is_instant_spell = (spell_icon in instant_spells or 
                                  spell_name in ['Молния', 'Слабость', 'Благословение', 'Проклятие', 
                                                'Замедление', 'Ускорение', 'Лечение', 'Снятие чар'] or
                                  any(keyword in spell_icon.lower() for keyword in ['lightning', 'weakness', 'bless', 'curse']))
                
                # Отладочное логирование
                self.anim_logger.log("SPELL_CHECK", f"name='{spell_name}' icon='{spell_icon}' instant={is_instant_spell}")
                
                # Логируем анимацию заклинания
                self.anim_logger.log_spell_animation(spell_name, spell_icon, self.selected_unit, target, is_instant_spell)
                
                if spell_icon == 'firearrow':
                    self.anim_logger.log("FIREARROW_ANIMATION", f"Огненная стрела от {self.selected_unit.unit_type} к {target.unit_type}")
                    self.animate_firearrow(self.selected_unit, target)
                elif not is_instant_spell:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    # Воспроизводим звук выстрела магов
                    if self.magic_shot_sound:
                        self.magic_shot_sound.play()
                    self.anim_logger.log_projectile_animation("magic_bolt", 
                        (self.selected_unit.x, self.selected_unit.y), 
                        (target.x, target.y), color)
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                # Применяем заклинание (для Молнии и Слабости - мгновенно, без анимации)
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
            if self.selected_unit.can_move(x, y, self.units, self.barriers):
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
                # Проверяем расстояние для определения типа атаки
                distance = abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)
                is_melee = (distance == 1)
                damage_already_applied = False  # Флаг для отслеживания применения урона
                
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    # Лучники и дальнобойные юниты
                    if is_melee:
                        # Ближний бой для лучников - только ближний бой, без стрел
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = max(1, self.selected_unit.get_current_attack() // 2)  # Половина урона
                        # Запоминаем параметры для контратаки (даже для лучников в ближнем бою)
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                    else:
                        # Дальняя атака - стреляем стрелами/снарядами, контратаки нет
                        target_is_melee_unit = False  # Дальняя атака, контратаки нет
                        start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                        end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                        
                        # Проверяем, является ли атакующий героем
                        is_hero = isinstance(self.selected_unit, Hero)
                        hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                        
                        # Определяем тип снаряда в зависимости от юнита/героя
                        if is_hero and hero_class == 'archer':
                            # Герой-лучник: стреляет стрелами
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            pygame.time.delay(150)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
                        elif self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                            # Обычные лучники стреляют стрелами - воспроизводим звуки
                            # Звук натяжения лука
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            # Небольшая задержка для звука натяжения
                            pygame.time.delay(150)
                            # Звук выстрела - используем новые звуки выстрелов (случайный выбор)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            # Анимация полета стрелы
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            # Звук попадания
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
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
                            # Воспроизводим звук выстрела магов
                            if self.magic_shot_sound:
                                self.magic_shot_sound.play()
                            animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                        # Перерисовываем экран, чтобы убрать снаряд
                        self.draw()
                        pygame.display.flip()
                        # Для дальнобойной атаки проверяем руну магии с учетом множителя дальности
                        mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit, is_ranged=True, target_x=x, target_y=y)
                        if mixed_damage is not None:
                            # Для руны магии используем смешанный урон
                            damage = None  # Будет применен через mixed_damage
                        else:
                            # Обычный расчет урона для дальнобойных
                            damage = self.selected_unit.ranged_damage(x, y)
                        
                        # Применяем урон для дальнобойных атак
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            elif damage is not None:
                                clicked_unit.take_damage(damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
                else:
                    # Обычные ближние бойцы и герои-воины
                    # Проверяем героя-воина - у него особая анимация
                    is_hero = isinstance(self.selected_unit, Hero)
                    hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                    
                    if is_hero and hero_class == 'warrior':
                        # Герой-воин: телепортация к цели
                        damage = self.selected_unit.get_current_attack()
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Сохраняем здоровье до атаки для вычисления урона
                        health_before = clicked_unit.health
                        # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                        squad_count_before_warrior = getattr(clicked_unit, 'squad_count', 1)
                        
                        # Создаем callback для применения урона (ТОЛЬКО урон, без последствий)
                        def apply_warrior_damage():
                            nonlocal damage_already_applied
                            damage_already_applied = True
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                        
                        # Вычисляем позицию рядом с целью
                        dx = clicked_unit.x - self.selected_unit.x
                        dy = clicked_unit.y - self.selected_unit.y
                        # Позиция рядом с целью (смещение в направлении атакующего)
                        if abs(dx) > abs(dy):
                            attack_x = clicked_unit.x - (1 if dx > 0 else -1)
                            attack_y = clicked_unit.y
                        else:
                            attack_x = clicked_unit.x
                            attack_y = clicked_unit.y - (1 if dy > 0 else -1)
                        
                        # Запускаем анимацию телепортации
                        animate_warrior_teleport(self.screen, 
                                                (self.selected_unit.x * CELL_SIZE, self.selected_unit.y * CELL_SIZE),
                                                (attack_x * CELL_SIZE, attack_y * CELL_SIZE),
                                                self.selected_unit.image,
                                                redraw_callback=self.draw,
                                                attack_sound_callback=lambda: (random.choice(self.human_melee_sounds).play() if self.human_melee_sounds and hasattr(random, 'choice') else None) if self.selected_unit.team in ['human', 'elf', 'dwarf'] else (random.choice(self.monster_melee_sounds).play() if self.monster_melee_sounds and hasattr(random, 'choice') else None),
                                                damage_callback=apply_warrior_damage,
                                                hide_attacker_pos=(self.selected_unit.x, self.selected_unit.y))
                        
                        # Вычисляем нанесенный урон
                        actual_damage = health_before - clicked_unit.health
                        
                        # ПОСЛЕ анимации обрабатываем последствия
                        squad_count_after_warrior = getattr(clicked_unit, 'squad_count', 1)
                        units_lost_warrior = squad_count_before_warrior - squad_count_after_warrior
                        if clicked_unit.health <= 0:
                            self.kill_unit(clicked_unit)
                            self.animate_queue_fade(clicked_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", уничтожено {units_lost_warrior} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", потеряно {units_lost_warrior} юнитов из отряда ({squad_count_after_warrior}/{squad_count_before_warrior})"
                            self.add_event(event_msg)
                            # Контратака происходит ПОСЛЕ анимации
                            self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки для героя-воина и переходим к следующему ходу
                        self.selected_unit.has_attacked = True
                        self.next_turn()
                        return
                    else:
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = self.selected_unit.get_current_attack()
                        # Запоминаем параметры для контратаки
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Применяем урон для обычных ближних бойцов
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                                # Контратака происходит ПОСЛЕ нанесения урона
                                self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
    
    def draw_unit_tooltip(self, unit):
        """Отрисовка тултипа юнита при зажатии правой кнопки мыши"""
        from .units import Hero
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)
        
        # Собираем информацию о юните
        lines = []
        lines.append(f"{unit.unit_type.capitalize()}")
        lines.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
        
        # Для героев показываем те же параметры что в окне информации (кроме удачи и боевого духа)
        if isinstance(unit, Hero):
            # Базовые параметры
            base_attack = getattr(unit, 'base_attack', None)
            if base_attack is None:
                # Вычисляем базовую атаку в зависимости от класса
                if unit.hero_class == 'mage':
                    base_attack = 5 + unit.spell_power
                else:  # warrior или archer
                    base_attack = 5 + unit.attack
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            knowledge = getattr(unit, 'knowledge', 0)
            spell_power = getattr(unit, 'spell_power', 0)
            mana = getattr(unit, 'mana', 0)
            max_mana = getattr(unit, 'max_mana', 0)
            
            lines.append(f"Базовая атака: {base_attack}")
            lines.append(f"Атака: {attack}")
            lines.append(f"Защита: {defense}")
            lines.append(f"Знания: {knowledge}")
            lines.append(f"Сила магии: {spell_power}")
            lines.append(f"Мана: {mana}/{max_mana}")
        else:
            # Для обычных юнитов показываем стандартную информацию
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                lines.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    lines.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    lines.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            # Атака и защита
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    lines.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    lines.append(f"Атака (маг): {unit.magic_attack}")
                lines.append(f"Защита (физ): {unit.phys_defense}")
                lines.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    lines.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                lines.append(f"Атака: {getattr(unit, 'attack', 0)}")
                lines.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            lines.append(f"Скорость: {unit.speed}")
            lines.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                lines.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    lines.append(f"Дальность: {unit.attack_range}")
        
        # Вычисляем размеры тултипа
        max_width = 0
        for line in lines:
            if line:
                width = font_small.size(line)[0]
                max_width = max(max_width, width)
        
        padding = 10
        line_height = 22
        tooltip_w = max_width + padding * 2
        tooltip_h = len(lines) * line_height + padding * 2
        
        # Позиция тултипа (рядом с курсором, но не выходя за экран)
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        if tooltip_x + tooltip_w > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_w - 20
        if tooltip_y + tooltip_h > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_h - 20
        
        # Фон тултипа
        tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surface.fill((40, 40, 80, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 150), (0, 0, tooltip_w, tooltip_h), 2)
        
        # Текст
        y_offset = padding
        for i, line in enumerate(lines):
            if line:
                if i == 0:  # Заголовок
                    text = font_bold.render(line, True, (255, 255, 180))
                else:
                    text = font_small.render(line, True, (220, 220, 220))
                tooltip_surface.blit(text, (padding, y_offset))
                y_offset += line_height
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_unit_info_window(self, unit):
        """Отрисовка окна информации о юните (при двойном клике)"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна
        window_w, window_h = 600, 500
        window_x = (SCREEN_WIDTH - window_w) // 2
        window_y = (SCREEN_HEIGHT - window_h) // 2
        
        # Фон окна (деревянный стиль)
        window_surface = pygame.Surface((window_w, window_h))
        for y in range(window_h):
            gradient = (
                int(150 - y * 0.2),
                int(110 - y * 0.15),
                int(80 - y * 0.1)
            )
            pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
        
        self.screen.blit(window_surface, (window_x, window_y))
        
        # Рамка
        pygame.draw.rect(self.screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=16)
        inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_rect, 2, border_radius=14)
        
        # Крестик для закрытия
        close_size = 30
        close_x = window_x + window_w - close_size - 10
        close_y = window_y + 10
        self.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        pygame.draw.rect(self.screen, (180, 60, 60), self.unit_info_close_button_rect, border_radius=5)
        font_close = pygame.font.Font(None, 32)
        close_text = font_close.render("×", True, (255, 255, 255))
        self.screen.blit(close_text, (close_x + 8, close_y + 2))
        
        # Заголовок
        font_title = pygame.font.Font(None, 48)
        title = font_title.render(f"{unit.unit_type.capitalize()}", True, (255, 245, 220))
        title_shadow = font_title.render(f"{unit.unit_type.capitalize()}", True, (60, 50, 40))
        title_x = window_x + (window_w - title.get_width()) // 2
        self.screen.blit(title_shadow, (title_x + 2, window_y + 20))
        self.screen.blit(title, (title_x, window_y + 18))
        
        # Изображение юнита (слева вверху)
        img_size = 120
        img_x = window_x + 30
        img_y = window_y + 80
        if hasattr(unit, 'image') and unit.image:
            img_scaled = pygame.transform.scale(unit.image, (img_size, img_size))
            self.screen.blit(img_scaled, (img_x, img_y))
        
        # Параметры (справа от изображения)
        font_small = pygame.font.Font(None, 24)
        param_x = img_x + img_size + 30
        param_y = window_y + 80
        line_height = 24  # Уменьшаем высоту строки для более компактного отображения
        max_param_width = window_w - param_x - 30  # Максимальная ширина для параметров
        
        # Проверяем, является ли юнит героем
        from .units import Hero
        is_hero = isinstance(unit, Hero)
        
        if is_hero:
            # Для героя показываем только параметры героя
            # Вычисляем базовую атаку в зависимости от класса
            if unit.hero_class == 'mage':
                base_attack = 5 + unit.spell_power
            else:  # warrior или archer
                base_attack = 5 + unit.attack
            
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            params.append(f"Базовая атака: {base_attack}")
            params.append(f"Атака: {unit.attack}")
            params.append(f"Защита: {unit.defense}")
            params.append(f"Сила магии: {unit.spell_power}")
            params.append(f"Знания: {unit.knowledge}")
            params.append(f"Мана: {unit.mana}/{unit.max_mana}")
            params.append(f"Удача: {unit.luck:+d} ({abs(unit.luck) * 5}% шанс двойного урона)")
            params.append(f"Боевой дух: {unit.combat_spirit:+d} ({abs(unit.combat_spirit) * 3}% шанс доп. хода)")
        else:
            # Для обычного юнита показываем параметры юнита
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                params.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    params.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    params.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    params.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    params.append(f"Атака (маг): {unit.magic_attack}")
                params.append(f"Защита (физ): {unit.phys_defense}")
                params.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    params.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                params.append(f"Атака: {getattr(unit, 'attack', 0)}")
                params.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            params.append(f"Скорость: {unit.speed}")
            params.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                params.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    params.append(f"Дальность: {unit.attack_range}")
            # Удача показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'luck'):
                luck = getattr(unit, 'luck', 0)
                params.append(f"Удача: {luck:+d} ({abs(luck) * 5}% шанс двойного урона)")
            # Боевой дух показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'combat_spirit'):
                combat_spirit = getattr(unit, 'combat_spirit', 0)
                params.append(f"Боевой дух: {combat_spirit:+d} ({abs(combat_spirit) * 3}% шанс доп. хода)")
            # Мораль показывается только в окне информации (не в тултипе), только для юнитов
            if hasattr(unit, 'morale') and not isinstance(unit, Hero):
                morale = getattr(unit, 'morale', 'good')
                morale_names = {
                    'excellent': 'Отличная',
                    'good': 'Хорошая',
                    'neutral': 'Нейтральная',
                    'bad': 'Плохая',
                    'awful': 'Ужасная'
                }
                morale_name = morale_names.get(morale, morale)
                params.append(f"Мораль: {morale_name}")
        
        # Отображаем параметры с переносом во второй столбец при необходимости
        current_y = param_y
        column1_x = param_x
        column1_max_y = param_y  # Максимальная высота первого столбца
        column2_x = param_x + max_param_width // 2 + 20  # Второй столбец правее
        max_params_per_column = 12  # Максимальное количество параметров в первом столбце
        current_column = 1
        column2_y = param_y  # Высота для второго столбца
        
        for i, param in enumerate(params):
            # Если параметров много, переходим во второй столбец
            if i >= max_params_per_column and current_column == 1:
                current_column = 2
                column2_y = param_y  # Начинаем с верха для второго столбца
                column1_max_y = current_y  # Сохраняем максимальную высоту первого столбца
            
            # Определяем позицию X в зависимости от столбца
            if current_column == 2:
                param_x_current = column2_x
                max_param_width_current = window_w - column2_x - 30
                current_y = column2_y
            else:
                param_x_current = column1_x
                max_param_width_current = max_param_width
                column1_max_y = current_y  # Обновляем максимальную высоту первого столбца
            
            # Проверяем, не выходит ли текст за пределы окна
            text_width = font_small.size(param)[0]
            if text_width > max_param_width_current:
                # Если текст слишком длинный, разбиваем на несколько строк
                words = param.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font_small.size(test_line)[0] <= max_param_width_current:
                        current_line = test_line
                    else:
                        if current_line:
                            text = font_small.render(current_line, True, (220, 220, 220))
                            self.screen.blit(text, (param_x_current, current_y))
                            current_y += line_height
                            if current_column == 2:
                                column2_y = current_y
                            else:
                                column1_max_y = current_y
                        current_line = word
                if current_line:
                    text = font_small.render(current_line, True, (220, 220, 220))
                    self.screen.blit(text, (param_x_current, current_y))
                    current_y += line_height
                    if current_column == 2:
                        column2_y = current_y
                    else:
                        column1_max_y = current_y
            else:
                text = font_small.render(param, True, (220, 220, 220))
                self.screen.blit(text, (param_x_current, current_y))
                current_y += line_height
                if current_column == 2:
                    column2_y = current_y
                else:
                    column1_max_y = current_y
        
        # Поля для способностей и пассивок (внизу) - динамически позиционируем
        # Оставляем минимум 120 пикселей снизу, но ограничиваем максимальное смещение
        min_effects_space = 120
        # Если использовались два столбца, берем максимальную высоту обоих столбцов
        if current_column == 2:
            param_bottom = max(column1_max_y, column2_y) + 20
        else:
            param_bottom = column1_max_y + 20  # Отступ снизу после параметров
        max_effects_y = window_y + window_h - min_effects_space  # Максимальная позиция (не ниже 120px от низа)
        abilities_y = min(max_effects_y, param_bottom + 20)  # Берем минимум, чтобы не уходило слишком далеко
        pygame.draw.line(self.screen, (100, 80, 60), (window_x + 20, abilities_y), (window_x + window_w - 20, abilities_y), 2)
        font_label = pygame.font.Font(None, 26)
        label = font_label.render("Временные эффекты:", True, (200, 180, 140))
        self.screen.blit(label, (window_x + 20, abilities_y + 10))
        
        # Собираем все временные эффекты
        effects = []
        effects_y = abilities_y + 35
        line_height_effects = 20
        max_lines = 3  # Максимум 3 строки эффектов
        
        # Защита
        if hasattr(unit, '_defend_this_round') and getattr(unit, '_defend_this_round', False):
            effects.append(("В защите", (100, 180, 255)))
        
        # Благословение/Проклятие
        if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
            effects.append((f"Благословение ({unit.attack_buff_turns} ход.)", (80, 255, 80)))
        if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
            effects.append((f"Проклятие ({unit.attack_debuff_turns} ход.)", (255, 80, 80)))
        
        # Руны
        if hasattr(unit, 'rune_shield_turns') and getattr(unit, 'rune_shield_turns', 0) > 0:
            effects.append((f"Руна защиты ({unit.rune_shield_turns} ход.)", (80, 255, 120)))
        if hasattr(unit, 'rune_magic_turns') and getattr(unit, 'rune_magic_turns', 0) > 0:
            effects.append((f"Руна магии ({unit.rune_magic_turns} ход.)", (200, 150, 255)))
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            effects.append((f"Руна берсерка ({unit.rune_berserker_turns} ход.)", (255, 80, 80)))
        if hasattr(unit, 'rune_haste_turns') and getattr(unit, 'rune_haste_turns', 0) > 0:
            effects.append((f"Руна скорости ({unit.rune_haste_turns} ход.)", (120, 200, 255)))
        
        # Замедление/Ускорение
        if hasattr(unit, 'slow_turns') and getattr(unit, 'slow_turns', 0) > 0:
            effects.append((f"Замедление ({unit.slow_turns} ход.)", (255, 120, 120)))
        if hasattr(unit, 'haste_turns') and getattr(unit, 'haste_turns', 0) > 0:
            effects.append((f"Ускорение ({unit.haste_turns} ход.)", (120, 255, 120)))
        
        # Ослепление
        if hasattr(unit, 'blindness_turns') and getattr(unit, 'blindness_turns', 0) > 0:
            effects.append((f"Ослепление ({unit.blindness_turns} ход.)", (200, 200, 80)))
        
        # Молитва
        if hasattr(unit, 'prayer_turns') and getattr(unit, 'prayer_turns', 0) > 0:
            effects.append((f"Молитва ({unit.prayer_turns} ход.)", (255, 255, 200)))
        
        # Точность
        if hasattr(unit, 'accuracy_turns') and getattr(unit, 'accuracy_turns', 0) > 0:
            effects.append((f"Точность ({unit.accuracy_turns} ход.)", (255, 200, 100)))
        
        # Каменная кожа
        if hasattr(unit, 'stone_skin_turns') and getattr(unit, 'stone_skin_turns', 0) > 0:
            effects.append((f"Каменная кожа ({unit.stone_skin_turns} ход.)", (200, 200, 200)))
        
        # Огненный щит
        if hasattr(unit, 'fire_shield_turns') and getattr(unit, 'fire_shield_turns', 0) > 0:
            effects.append((f"Огненный щит ({unit.fire_shield_turns} ход.)", (255, 100, 50)))
        
        # Ледяной щит
        if hasattr(unit, 'ice_shield_turns') and getattr(unit, 'ice_shield_turns', 0) > 0:
            effects.append((f"Ледяной щит ({unit.ice_shield_turns} ход.)", (100, 200, 255)))
        
        # Контрудар
        if hasattr(unit, 'counterstrike_turns') and getattr(unit, 'counterstrike_turns', 0) > 0:
            effects.append((f"Контрудар ({unit.counterstrike_turns} ход.)", (255, 180, 100)))
        
        # Слабость
        if hasattr(unit, 'weakness_turns') and getattr(unit, 'weakness_turns', 0) > 0:
            effects.append((f"Слабость ({unit.weakness_turns} ход.)", (200, 100, 100)))
        
        # Забвение
        if hasattr(unit, 'forget_turns') and getattr(unit, 'forget_turns', 0) > 0:
            effects.append((f"Забвение ({unit.forget_turns} ход.)", (150, 150, 150)))
        
        # Отображаем эффекты
        if effects:
            for i, (effect_name, effect_color) in enumerate(effects[:max_lines]):
                effect_text = font_small.render(effect_name, True, effect_color)
                self.screen.blit(effect_text, (window_x + 20, effects_y + i * line_height_effects))
            if len(effects) > max_lines:
                more_text = font_small.render(f"... и еще {len(effects) - max_lines}", True, (150, 150, 150))
                self.screen.blit(more_text, (window_x + 20, effects_y + max_lines * line_height_effects))
        else:
            no_effects = font_small.render("Нет активных эффектов", True, (150, 150, 150))
            self.screen.blit(no_effects, (window_x + 20, effects_y))
        
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Отладочное логирование начала применения заклинания
            self.anim_logger.log("SPELL_CAST_START", f"Герой кастует {spell.name} ({spell.icon}) target_type={spell.target_type}")
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
                spell_name = getattr(spell, 'name', '')
                spell_icon = getattr(spell, 'icon', '')
                # Проверяем мгновенные заклинания (без анимации полета снаряда)
                instant_spells = [
                    'lightning', 'weakness', 'bless', 'curse', 'slow', 'haste',
                    'heal', 'dispel', 'stone_skin', 'ice_shield', 'fire_shield',
                    'counterstrike', 'rune_shield', 'rune_haste', 'raise_dead',
                    'resurrection', 'undead_heal', 'forget', 'earth_spikes', 'rune_wall'
                ]
                is_instant_spell = (spell_icon in instant_spells or 
                                  spell_name in ['Молния', 'Слабость', 'Благословение', 'Проклятие', 
                                                'Замедление', 'Ускорение', 'Лечение', 'Снятие чар'] or
                                  any(keyword in spell_icon.lower() for keyword in ['lightning', 'weakness', 'bless', 'curse']))
                
                # Отладочное логирование
                self.anim_logger.log("SPELL_CHECK", f"name='{spell_name}' icon='{spell_icon}' instant={is_instant_spell}")
                
                # Логируем анимацию заклинания
                self.anim_logger.log_spell_animation(spell_name, spell_icon, self.selected_unit, target, is_instant_spell)
                
                if spell_icon == 'firearrow':
                    self.anim_logger.log("FIREARROW_ANIMATION", f"Огненная стрела от {self.selected_unit.unit_type} к {target.unit_type}")
                    self.animate_firearrow(self.selected_unit, target)
                elif not is_instant_spell:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    # Воспроизводим звук выстрела магов
                    if self.magic_shot_sound:
                        self.magic_shot_sound.play()
                    self.anim_logger.log_projectile_animation("magic_bolt", 
                        (self.selected_unit.x, self.selected_unit.y), 
                        (target.x, target.y), color)
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                # Применяем заклинание (для Молнии и Слабости - мгновенно, без анимации)
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
            if self.selected_unit.can_move(x, y, self.units, self.barriers):
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
                # Проверяем расстояние для определения типа атаки
                distance = abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)
                is_melee = (distance == 1)
                damage_already_applied = False  # Флаг для отслеживания применения урона
                
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    # Лучники и дальнобойные юниты
                    if is_melee:
                        # Ближний бой для лучников - только ближний бой, без стрел
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = max(1, self.selected_unit.get_current_attack() // 2)  # Половина урона
                        # Запоминаем параметры для контратаки (даже для лучников в ближнем бою)
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                    else:
                        # Дальняя атака - стреляем стрелами/снарядами, контратаки нет
                        target_is_melee_unit = False  # Дальняя атака, контратаки нет
                        start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                        end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                        
                        # Проверяем, является ли атакующий героем
                        is_hero = isinstance(self.selected_unit, Hero)
                        hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                        
                        # Определяем тип снаряда в зависимости от юнита/героя
                        if is_hero and hero_class == 'archer':
                            # Герой-лучник: стреляет стрелами
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            pygame.time.delay(150)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
                        elif self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                            # Обычные лучники стреляют стрелами - воспроизводим звуки
                            # Звук натяжения лука
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            # Небольшая задержка для звука натяжения
                            pygame.time.delay(150)
                            # Звук выстрела - используем новые звуки выстрелов (случайный выбор)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            # Анимация полета стрелы
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            # Звук попадания
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
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
                            # Воспроизводим звук выстрела магов
                            if self.magic_shot_sound:
                                self.magic_shot_sound.play()
                            animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                        # Перерисовываем экран, чтобы убрать снаряд
                        self.draw()
                        pygame.display.flip()
                        # Для дальнобойной атаки проверяем руну магии с учетом множителя дальности
                        mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit, is_ranged=True, target_x=x, target_y=y)
                        if mixed_damage is not None:
                            # Для руны магии используем смешанный урон
                            damage = None  # Будет применен через mixed_damage
                        else:
                            # Обычный расчет урона для дальнобойных
                            damage = self.selected_unit.ranged_damage(x, y)
                        
                        # Применяем урон для дальнобойных атак
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            elif damage is not None:
                                clicked_unit.take_damage(damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
                else:
                    # Обычные ближние бойцы и герои-воины
                    # Проверяем героя-воина - у него особая анимация
                    is_hero = isinstance(self.selected_unit, Hero)
                    hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                    
                    if is_hero and hero_class == 'warrior':
                        # Герой-воин: телепортация к цели
                        damage = self.selected_unit.get_current_attack()
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Сохраняем здоровье до атаки для вычисления урона
                        health_before = clicked_unit.health
                        # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                        squad_count_before_warrior = getattr(clicked_unit, 'squad_count', 1)
                        
                        # Создаем callback для применения урона (ТОЛЬКО урон, без последствий)
                        def apply_warrior_damage():
                            nonlocal damage_already_applied
                            damage_already_applied = True
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                        
                        # Вычисляем позицию рядом с целью
                        dx = clicked_unit.x - self.selected_unit.x
                        dy = clicked_unit.y - self.selected_unit.y
                        # Позиция рядом с целью (смещение в направлении атакующего)
                        if abs(dx) > abs(dy):
                            attack_x = clicked_unit.x - (1 if dx > 0 else -1)
                            attack_y = clicked_unit.y
                        else:
                            attack_x = clicked_unit.x
                            attack_y = clicked_unit.y - (1 if dy > 0 else -1)
                        
                        # Запускаем анимацию телепортации
                        animate_warrior_teleport(self.screen, 
                                                (self.selected_unit.x * CELL_SIZE, self.selected_unit.y * CELL_SIZE),
                                                (attack_x * CELL_SIZE, attack_y * CELL_SIZE),
                                                self.selected_unit.image,
                                                redraw_callback=self.draw,
                                                attack_sound_callback=lambda: (random.choice(self.human_melee_sounds).play() if self.human_melee_sounds and hasattr(random, 'choice') else None) if self.selected_unit.team in ['human', 'elf', 'dwarf'] else (random.choice(self.monster_melee_sounds).play() if self.monster_melee_sounds and hasattr(random, 'choice') else None),
                                                damage_callback=apply_warrior_damage,
                                                hide_attacker_pos=(self.selected_unit.x, self.selected_unit.y))
                        
                        # Вычисляем нанесенный урон
                        actual_damage = health_before - clicked_unit.health
                        
                        # ПОСЛЕ анимации обрабатываем последствия
                        squad_count_after_warrior = getattr(clicked_unit, 'squad_count', 1)
                        units_lost_warrior = squad_count_before_warrior - squad_count_after_warrior
                        if clicked_unit.health <= 0:
                            self.kill_unit(clicked_unit)
                            self.animate_queue_fade(clicked_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", уничтожено {units_lost_warrior} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", потеряно {units_lost_warrior} юнитов из отряда ({squad_count_after_warrior}/{squad_count_before_warrior})"
                            self.add_event(event_msg)
                            # Контратака происходит ПОСЛЕ анимации
                            self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки для героя-воина и переходим к следующему ходу
                        self.selected_unit.has_attacked = True
                        self.next_turn()
                        return
                    else:
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = self.selected_unit.get_current_attack()
                        # Запоминаем параметры для контратаки
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Применяем урон для обычных ближних бойцов
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                                # Контратака происходит ПОСЛЕ нанесения урона
                                self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
    
    def draw_unit_tooltip(self, unit):
        """Отрисовка тултипа юнита при зажатии правой кнопки мыши"""
        from .units import Hero
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)
        
        # Собираем информацию о юните
        lines = []
        lines.append(f"{unit.unit_type.capitalize()}")
        lines.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
        
        # Для героев показываем те же параметры что в окне информации (кроме удачи и боевого духа)
        if isinstance(unit, Hero):
            # Базовые параметры
            base_attack = getattr(unit, 'base_attack', None)
            if base_attack is None:
                # Вычисляем базовую атаку в зависимости от класса
                if unit.hero_class == 'mage':
                    base_attack = 5 + unit.spell_power
                else:  # warrior или archer
                    base_attack = 5 + unit.attack
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            knowledge = getattr(unit, 'knowledge', 0)
            spell_power = getattr(unit, 'spell_power', 0)
            mana = getattr(unit, 'mana', 0)
            max_mana = getattr(unit, 'max_mana', 0)
            
            lines.append(f"Базовая атака: {base_attack}")
            lines.append(f"Атака: {attack}")
            lines.append(f"Защита: {defense}")
            lines.append(f"Знания: {knowledge}")
            lines.append(f"Сила магии: {spell_power}")
            lines.append(f"Мана: {mana}/{max_mana}")
        else:
            # Для обычных юнитов показываем стандартную информацию
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                lines.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    lines.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    lines.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            # Атака и защита
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    lines.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    lines.append(f"Атака (маг): {unit.magic_attack}")
                lines.append(f"Защита (физ): {unit.phys_defense}")
                lines.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    lines.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                lines.append(f"Атака: {getattr(unit, 'attack', 0)}")
                lines.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            lines.append(f"Скорость: {unit.speed}")
            lines.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                lines.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    lines.append(f"Дальность: {unit.attack_range}")
        
        # Вычисляем размеры тултипа
        max_width = 0
        for line in lines:
            if line:
                width = font_small.size(line)[0]
                max_width = max(max_width, width)
        
        padding = 10
        line_height = 22
        tooltip_w = max_width + padding * 2
        tooltip_h = len(lines) * line_height + padding * 2
        
        # Позиция тултипа (рядом с курсором, но не выходя за экран)
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        if tooltip_x + tooltip_w > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_w - 20
        if tooltip_y + tooltip_h > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_h - 20
        
        # Фон тултипа
        tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surface.fill((40, 40, 80, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 150), (0, 0, tooltip_w, tooltip_h), 2)
        
        # Текст
        y_offset = padding
        for i, line in enumerate(lines):
            if line:
                if i == 0:  # Заголовок
                    text = font_bold.render(line, True, (255, 255, 180))
                else:
                    text = font_small.render(line, True, (220, 220, 220))
                tooltip_surface.blit(text, (padding, y_offset))
                y_offset += line_height
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_unit_info_window(self, unit):
        """Отрисовка окна информации о юните (при двойном клике)"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна
        window_w, window_h = 600, 500
        window_x = (SCREEN_WIDTH - window_w) // 2
        window_y = (SCREEN_HEIGHT - window_h) // 2
        
        # Фон окна (деревянный стиль)
        window_surface = pygame.Surface((window_w, window_h))
        for y in range(window_h):
            gradient = (
                int(150 - y * 0.2),
                int(110 - y * 0.15),
                int(80 - y * 0.1)
            )
            pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
        
        self.screen.blit(window_surface, (window_x, window_y))
        
        # Рамка
        pygame.draw.rect(self.screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=16)
        inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_rect, 2, border_radius=14)
        
        # Крестик для закрытия
        close_size = 30
        close_x = window_x + window_w - close_size - 10
        close_y = window_y + 10
        self.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        pygame.draw.rect(self.screen, (180, 60, 60), self.unit_info_close_button_rect, border_radius=5)
        font_close = pygame.font.Font(None, 32)
        close_text = font_close.render("×", True, (255, 255, 255))
        self.screen.blit(close_text, (close_x + 8, close_y + 2))
        
        # Заголовок
        font_title = pygame.font.Font(None, 48)
        title = font_title.render(f"{unit.unit_type.capitalize()}", True, (255, 245, 220))
        title_shadow = font_title.render(f"{unit.unit_type.capitalize()}", True, (60, 50, 40))
        title_x = window_x + (window_w - title.get_width()) // 2
        self.screen.blit(title_shadow, (title_x + 2, window_y + 20))
        self.screen.blit(title, (title_x, window_y + 18))
        
        # Изображение юнита (слева вверху)
        img_size = 120
        img_x = window_x + 30
        img_y = window_y + 80
        if hasattr(unit, 'image') and unit.image:
            img_scaled = pygame.transform.scale(unit.image, (img_size, img_size))
            self.screen.blit(img_scaled, (img_x, img_y))
        
        # Параметры (справа от изображения)
        font_small = pygame.font.Font(None, 24)
        param_x = img_x + img_size + 30
        param_y = window_y + 80
        line_height = 24  # Уменьшаем высоту строки для более компактного отображения
        max_param_width = window_w - param_x - 30  # Максимальная ширина для параметров
        
        # Проверяем, является ли юнит героем
        from .units import Hero
        is_hero = isinstance(unit, Hero)
        
        if is_hero:
            # Для героя показываем только параметры героя
            # Вычисляем базовую атаку в зависимости от класса
            if unit.hero_class == 'mage':
                base_attack = 5 + unit.spell_power
            else:  # warrior или archer
                base_attack = 5 + unit.attack
            
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            params.append(f"Базовая атака: {base_attack}")
            params.append(f"Атака: {unit.attack}")
            params.append(f"Защита: {unit.defense}")
            params.append(f"Сила магии: {unit.spell_power}")
            params.append(f"Знания: {unit.knowledge}")
            params.append(f"Мана: {unit.mana}/{unit.max_mana}")
            params.append(f"Удача: {unit.luck:+d} ({abs(unit.luck) * 5}% шанс двойного урона)")
            params.append(f"Боевой дух: {unit.combat_spirit:+d} ({abs(unit.combat_spirit) * 3}% шанс доп. хода)")
        else:
            # Для обычного юнита показываем параметры юнита
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                params.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    params.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    params.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    params.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    params.append(f"Атака (маг): {unit.magic_attack}")
                params.append(f"Защита (физ): {unit.phys_defense}")
                params.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    params.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                params.append(f"Атака: {getattr(unit, 'attack', 0)}")
                params.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            params.append(f"Скорость: {unit.speed}")
            params.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                params.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    params.append(f"Дальность: {unit.attack_range}")
            # Удача показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'luck'):
                luck = getattr(unit, 'luck', 0)
                params.append(f"Удача: {luck:+d} ({abs(luck) * 5}% шанс двойного урона)")
            # Боевой дух показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'combat_spirit'):
                combat_spirit = getattr(unit, 'combat_spirit', 0)
                params.append(f"Боевой дух: {combat_spirit:+d} ({abs(combat_spirit) * 3}% шанс доп. хода)")
            # Мораль показывается только в окне информации (не в тултипе), только для юнитов
            if hasattr(unit, 'morale') and not isinstance(unit, Hero):
                morale = getattr(unit, 'morale', 'good')
                morale_names = {
                    'excellent': 'Отличная',
                    'good': 'Хорошая',
                    'neutral': 'Нейтральная',
                    'bad': 'Плохая',
                    'awful': 'Ужасная'
                }
                morale_name = morale_names.get(morale, morale)
                params.append(f"Мораль: {morale_name}")
        
        # Отображаем параметры с переносом во второй столбец при необходимости
        current_y = param_y
        column1_x = param_x
        column1_max_y = param_y  # Максимальная высота первого столбца
        column2_x = param_x + max_param_width // 2 + 20  # Второй столбец правее
        max_params_per_column = 12  # Максимальное количество параметров в первом столбце
        current_column = 1
        column2_y = param_y  # Высота для второго столбца
        
        for i, param in enumerate(params):
            # Если параметров много, переходим во второй столбец
            if i >= max_params_per_column and current_column == 1:
                current_column = 2
                column2_y = param_y  # Начинаем с верха для второго столбца
                column1_max_y = current_y  # Сохраняем максимальную высоту первого столбца
            
            # Определяем позицию X в зависимости от столбца
            if current_column == 2:
                param_x_current = column2_x
                max_param_width_current = window_w - column2_x - 30
                current_y = column2_y
            else:
                param_x_current = column1_x
                max_param_width_current = max_param_width
                column1_max_y = current_y  # Обновляем максимальную высоту первого столбца
            
            # Проверяем, не выходит ли текст за пределы окна
            text_width = font_small.size(param)[0]
            if text_width > max_param_width_current:
                # Если текст слишком длинный, разбиваем на несколько строк
                words = param.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font_small.size(test_line)[0] <= max_param_width_current:
                        current_line = test_line
                    else:
                        if current_line:
                            text = font_small.render(current_line, True, (220, 220, 220))
                            self.screen.blit(text, (param_x_current, current_y))
                            current_y += line_height
                            if current_column == 2:
                                column2_y = current_y
                            else:
                                column1_max_y = current_y
                        current_line = word
                if current_line:
                    text = font_small.render(current_line, True, (220, 220, 220))
                    self.screen.blit(text, (param_x_current, current_y))
                    current_y += line_height
                    if current_column == 2:
                        column2_y = current_y
                    else:
                        column1_max_y = current_y
            else:
                text = font_small.render(param, True, (220, 220, 220))
                self.screen.blit(text, (param_x_current, current_y))
                current_y += line_height
                if current_column == 2:
                    column2_y = current_y
                else:
                    column1_max_y = current_y
        
        # Поля для способностей и пассивок (внизу) - динамически позиционируем
        # Оставляем минимум 120 пикселей снизу, но ограничиваем максимальное смещение
        min_effects_space = 120
        # Если использовались два столбца, берем максимальную высоту обоих столбцов
        if current_column == 2:
            param_bottom = max(column1_max_y, column2_y) + 20
        else:
            param_bottom = column1_max_y + 20  # Отступ снизу после параметров
        max_effects_y = window_y + window_h - min_effects_space  # Максимальная позиция (не ниже 120px от низа)
        abilities_y = min(max_effects_y, param_bottom + 20)  # Берем минимум, чтобы не уходило слишком далеко
        pygame.draw.line(self.screen, (100, 80, 60), (window_x + 20, abilities_y), (window_x + window_w - 20, abilities_y), 2)
        font_label = pygame.font.Font(None, 26)
        label = font_label.render("Временные эффекты:", True, (200, 180, 140))
        self.screen.blit(label, (window_x + 20, abilities_y + 10))
        
        # Собираем все временные эффекты
        effects = []
        effects_y = abilities_y + 35
        line_height_effects = 20
        max_lines = 3  # Максимум 3 строки эффектов
        
        # Защита
        if hasattr(unit, '_defend_this_round') and getattr(unit, '_defend_this_round', False):
            effects.append(("В защите", (100, 180, 255)))
        
        # Благословение/Проклятие
        if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
            effects.append((f"Благословение ({unit.attack_buff_turns} ход.)", (80, 255, 80)))
        if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
            effects.append((f"Проклятие ({unit.attack_debuff_turns} ход.)", (255, 80, 80)))
        
        # Руны
        if hasattr(unit, 'rune_shield_turns') and getattr(unit, 'rune_shield_turns', 0) > 0:
            effects.append((f"Руна защиты ({unit.rune_shield_turns} ход.)", (80, 255, 120)))
        if hasattr(unit, 'rune_magic_turns') and getattr(unit, 'rune_magic_turns', 0) > 0:
            effects.append((f"Руна магии ({unit.rune_magic_turns} ход.)", (200, 150, 255)))
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            effects.append((f"Руна берсерка ({unit.rune_berserker_turns} ход.)", (255, 80, 80)))
        if hasattr(unit, 'rune_haste_turns') and getattr(unit, 'rune_haste_turns', 0) > 0:
            effects.append((f"Руна скорости ({unit.rune_haste_turns} ход.)", (120, 200, 255)))
        
        # Замедление/Ускорение
        if hasattr(unit, 'slow_turns') and getattr(unit, 'slow_turns', 0) > 0:
            effects.append((f"Замедление ({unit.slow_turns} ход.)", (255, 120, 120)))
        if hasattr(unit, 'haste_turns') and getattr(unit, 'haste_turns', 0) > 0:
            effects.append((f"Ускорение ({unit.haste_turns} ход.)", (120, 255, 120)))
        
        # Ослепление
        if hasattr(unit, 'blindness_turns') and getattr(unit, 'blindness_turns', 0) > 0:
            effects.append((f"Ослепление ({unit.blindness_turns} ход.)", (200, 200, 80)))
        
        # Молитва
        if hasattr(unit, 'prayer_turns') and getattr(unit, 'prayer_turns', 0) > 0:
            effects.append((f"Молитва ({unit.prayer_turns} ход.)", (255, 255, 200)))
        
        # Точность
        if hasattr(unit, 'accuracy_turns') and getattr(unit, 'accuracy_turns', 0) > 0:
            effects.append((f"Точность ({unit.accuracy_turns} ход.)", (255, 200, 100)))
        
        # Каменная кожа
        if hasattr(unit, 'stone_skin_turns') and getattr(unit, 'stone_skin_turns', 0) > 0:
            effects.append((f"Каменная кожа ({unit.stone_skin_turns} ход.)", (200, 200, 200)))
        
        # Огненный щит
        if hasattr(unit, 'fire_shield_turns') and getattr(unit, 'fire_shield_turns', 0) > 0:
            effects.append((f"Огненный щит ({unit.fire_shield_turns} ход.)", (255, 100, 50)))
        
        # Ледяной щит
        if hasattr(unit, 'ice_shield_turns') and getattr(unit, 'ice_shield_turns', 0) > 0:
            effects.append((f"Ледяной щит ({unit.ice_shield_turns} ход.)", (100, 200, 255)))
        
        # Контрудар
        if hasattr(unit, 'counterstrike_turns') and getattr(unit, 'counterstrike_turns', 0) > 0:
            effects.append((f"Контрудар ({unit.counterstrike_turns} ход.)", (255, 180, 100)))
        
        # Слабость
        if hasattr(unit, 'weakness_turns') and getattr(unit, 'weakness_turns', 0) > 0:
            effects.append((f"Слабость ({unit.weakness_turns} ход.)", (200, 100, 100)))
        
        # Забвение
        if hasattr(unit, 'forget_turns') and getattr(unit, 'forget_turns', 0) > 0:
            effects.append((f"Забвение ({unit.forget_turns} ход.)", (150, 150, 150)))
        
        # Отображаем эффекты
        if effects:
            for i, (effect_name, effect_color) in enumerate(effects[:max_lines]):
                effect_text = font_small.render(effect_name, True, effect_color)
                self.screen.blit(effect_text, (window_x + 20, effects_y + i * line_height_effects))
            if len(effects) > max_lines:
                more_text = font_small.render(f"... и еще {len(effects) - max_lines}", True, (150, 150, 150))
                self.screen.blit(more_text, (window_x + 20, effects_y + max_lines * line_height_effects))
        else:
            no_effects = font_small.render("Нет активных эффектов", True, (150, 150, 150))
            self.screen.blit(no_effects, (window_x + 20, effects_y))
        
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Отладочное логирование начала применения заклинания
            self.anim_logger.log("SPELL_CAST_START", f"Герой кастует {spell.name} ({spell.icon}) target_type={spell.target_type}")
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
                spell_name = getattr(spell, 'name', '')
                spell_icon = getattr(spell, 'icon', '')
                # Проверяем мгновенные заклинания (без анимации полета снаряда)
                instant_spells = [
                    'lightning', 'weakness', 'bless', 'curse', 'slow', 'haste',
                    'heal', 'dispel', 'stone_skin', 'ice_shield', 'fire_shield',
                    'counterstrike', 'rune_shield', 'rune_haste', 'raise_dead',
                    'resurrection', 'undead_heal', 'forget', 'earth_spikes', 'rune_wall'
                ]
                is_instant_spell = (spell_icon in instant_spells or 
                                  spell_name in ['Молния', 'Слабость', 'Благословение', 'Проклятие', 
                                                'Замедление', 'Ускорение', 'Лечение', 'Снятие чар'] or
                                  any(keyword in spell_icon.lower() for keyword in ['lightning', 'weakness', 'bless', 'curse']))
                
                # Отладочное логирование
                self.anim_logger.log("SPELL_CHECK", f"name='{spell_name}' icon='{spell_icon}' instant={is_instant_spell}")
                
                # Логируем анимацию заклинания
                self.anim_logger.log_spell_animation(spell_name, spell_icon, self.selected_unit, target, is_instant_spell)
                
                if spell_icon == 'firearrow':
                    self.anim_logger.log("FIREARROW_ANIMATION", f"Огненная стрела от {self.selected_unit.unit_type} к {target.unit_type}")
                    self.animate_firearrow(self.selected_unit, target)
                elif not is_instant_spell:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    # Воспроизводим звук выстрела магов
                    if self.magic_shot_sound:
                        self.magic_shot_sound.play()
                    self.anim_logger.log_projectile_animation("magic_bolt", 
                        (self.selected_unit.x, self.selected_unit.y), 
                        (target.x, target.y), color)
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                # Применяем заклинание (для Молнии и Слабости - мгновенно, без анимации)
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
            if self.selected_unit.can_move(x, y, self.units, self.barriers):
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
                # Проверяем расстояние для определения типа атаки
                distance = abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)
                is_melee = (distance == 1)
                damage_already_applied = False  # Флаг для отслеживания применения урона
                
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    # Лучники и дальнобойные юниты
                    if is_melee:
                        # Ближний бой для лучников - только ближний бой, без стрел
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = max(1, self.selected_unit.get_current_attack() // 2)  # Половина урона
                        # Запоминаем параметры для контратаки (даже для лучников в ближнем бою)
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                    else:
                        # Дальняя атака - стреляем стрелами/снарядами, контратаки нет
                        target_is_melee_unit = False  # Дальняя атака, контратаки нет
                        start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                        end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                        
                        # Проверяем, является ли атакующий героем
                        is_hero = isinstance(self.selected_unit, Hero)
                        hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                        
                        # Определяем тип снаряда в зависимости от юнита/героя
                        if is_hero and hero_class == 'archer':
                            # Герой-лучник: стреляет стрелами
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            pygame.time.delay(150)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
                        elif self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                            # Обычные лучники стреляют стрелами - воспроизводим звуки
                            # Звук натяжения лука
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            # Небольшая задержка для звука натяжения
                            pygame.time.delay(150)
                            # Звук выстрела - используем новые звуки выстрелов (случайный выбор)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            # Анимация полета стрелы
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            # Звук попадания
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
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
                            # Воспроизводим звук выстрела магов
                            if self.magic_shot_sound:
                                self.magic_shot_sound.play()
                            animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                        # Перерисовываем экран, чтобы убрать снаряд
                        self.draw()
                        pygame.display.flip()
                        # Для дальнобойной атаки проверяем руну магии с учетом множителя дальности
                        mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit, is_ranged=True, target_x=x, target_y=y)
                        if mixed_damage is not None:
                            # Для руны магии используем смешанный урон
                            damage = None  # Будет применен через mixed_damage
                        else:
                            # Обычный расчет урона для дальнобойных
                            damage = self.selected_unit.ranged_damage(x, y)
                        
                        # Применяем урон для дальнобойных атак
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            elif damage is not None:
                                clicked_unit.take_damage(damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
                else:
                    # Обычные ближние бойцы и герои-воины
                    # Проверяем героя-воина - у него особая анимация
                    is_hero = isinstance(self.selected_unit, Hero)
                    hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                    
                    if is_hero and hero_class == 'warrior':
                        # Герой-воин: телепортация к цели
                        damage = self.selected_unit.get_current_attack()
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Сохраняем здоровье до атаки для вычисления урона
                        health_before = clicked_unit.health
                        # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                        squad_count_before_warrior = getattr(clicked_unit, 'squad_count', 1)
                        
                        # Создаем callback для применения урона (ТОЛЬКО урон, без последствий)
                        def apply_warrior_damage():
                            nonlocal damage_already_applied
                            damage_already_applied = True
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                        
                        # Вычисляем позицию рядом с целью
                        dx = clicked_unit.x - self.selected_unit.x
                        dy = clicked_unit.y - self.selected_unit.y
                        # Позиция рядом с целью (смещение в направлении атакующего)
                        if abs(dx) > abs(dy):
                            attack_x = clicked_unit.x - (1 if dx > 0 else -1)
                            attack_y = clicked_unit.y
                        else:
                            attack_x = clicked_unit.x
                            attack_y = clicked_unit.y - (1 if dy > 0 else -1)
                        
                        # Запускаем анимацию телепортации
                        animate_warrior_teleport(self.screen, 
                                                (self.selected_unit.x * CELL_SIZE, self.selected_unit.y * CELL_SIZE),
                                                (attack_x * CELL_SIZE, attack_y * CELL_SIZE),
                                                self.selected_unit.image,
                                                redraw_callback=self.draw,
                                                attack_sound_callback=lambda: (random.choice(self.human_melee_sounds).play() if self.human_melee_sounds and hasattr(random, 'choice') else None) if self.selected_unit.team in ['human', 'elf', 'dwarf'] else (random.choice(self.monster_melee_sounds).play() if self.monster_melee_sounds and hasattr(random, 'choice') else None),
                                                damage_callback=apply_warrior_damage,
                                                hide_attacker_pos=(self.selected_unit.x, self.selected_unit.y))
                        
                        # Вычисляем нанесенный урон
                        actual_damage = health_before - clicked_unit.health
                        
                        # ПОСЛЕ анимации обрабатываем последствия
                        squad_count_after_warrior = getattr(clicked_unit, 'squad_count', 1)
                        units_lost_warrior = squad_count_before_warrior - squad_count_after_warrior
                        if clicked_unit.health <= 0:
                            self.kill_unit(clicked_unit)
                            self.animate_queue_fade(clicked_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", уничтожено {units_lost_warrior} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", потеряно {units_lost_warrior} юнитов из отряда ({squad_count_after_warrior}/{squad_count_before_warrior})"
                            self.add_event(event_msg)
                            # Контратака происходит ПОСЛЕ анимации
                            self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки для героя-воина и переходим к следующему ходу
                        self.selected_unit.has_attacked = True
                        self.next_turn()
                        return
                    else:
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = self.selected_unit.get_current_attack()
                        # Запоминаем параметры для контратаки
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Применяем урон для обычных ближних бойцов
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                                # Контратака происходит ПОСЛЕ нанесения урона
                                self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
    
    def draw_unit_tooltip(self, unit):
        """Отрисовка тултипа юнита при зажатии правой кнопки мыши"""
        from .units import Hero
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)
        
        # Собираем информацию о юните
        lines = []
        lines.append(f"{unit.unit_type.capitalize()}")
        lines.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
        
        # Для героев показываем те же параметры что в окне информации (кроме удачи и боевого духа)
        if isinstance(unit, Hero):
            # Базовые параметры
            base_attack = getattr(unit, 'base_attack', None)
            if base_attack is None:
                # Вычисляем базовую атаку в зависимости от класса
                if unit.hero_class == 'mage':
                    base_attack = 5 + unit.spell_power
                else:  # warrior или archer
                    base_attack = 5 + unit.attack
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            knowledge = getattr(unit, 'knowledge', 0)
            spell_power = getattr(unit, 'spell_power', 0)
            mana = getattr(unit, 'mana', 0)
            max_mana = getattr(unit, 'max_mana', 0)
            
            lines.append(f"Базовая атака: {base_attack}")
            lines.append(f"Атака: {attack}")
            lines.append(f"Защита: {defense}")
            lines.append(f"Знания: {knowledge}")
            lines.append(f"Сила магии: {spell_power}")
            lines.append(f"Мана: {mana}/{max_mana}")
        else:
            # Для обычных юнитов показываем стандартную информацию
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                lines.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    lines.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    lines.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            # Атака и защита
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    lines.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    lines.append(f"Атака (маг): {unit.magic_attack}")
                lines.append(f"Защита (физ): {unit.phys_defense}")
                lines.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    lines.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                lines.append(f"Атака: {getattr(unit, 'attack', 0)}")
                lines.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            lines.append(f"Скорость: {unit.speed}")
            lines.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                lines.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    lines.append(f"Дальность: {unit.attack_range}")
        
        # Вычисляем размеры тултипа
        max_width = 0
        for line in lines:
            if line:
                width = font_small.size(line)[0]
                max_width = max(max_width, width)
        
        padding = 10
        line_height = 22
        tooltip_w = max_width + padding * 2
        tooltip_h = len(lines) * line_height + padding * 2
        
        # Позиция тултипа (рядом с курсором, но не выходя за экран)
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        if tooltip_x + tooltip_w > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_w - 20
        if tooltip_y + tooltip_h > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_h - 20
        
        # Фон тултипа
        tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surface.fill((40, 40, 80, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 150), (0, 0, tooltip_w, tooltip_h), 2)
        
        # Текст
        y_offset = padding
        for i, line in enumerate(lines):
            if line:
                if i == 0:  # Заголовок
                    text = font_bold.render(line, True, (255, 255, 180))
                else:
                    text = font_small.render(line, True, (220, 220, 220))
                tooltip_surface.blit(text, (padding, y_offset))
                y_offset += line_height
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_unit_info_window(self, unit):
        """Отрисовка окна информации о юните (при двойном клике)"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна
        window_w, window_h = 600, 500
        window_x = (SCREEN_WIDTH - window_w) // 2
        window_y = (SCREEN_HEIGHT - window_h) // 2
        
        # Фон окна (деревянный стиль)
        window_surface = pygame.Surface((window_w, window_h))
        for y in range(window_h):
            gradient = (
                int(150 - y * 0.2),
                int(110 - y * 0.15),
                int(80 - y * 0.1)
            )
            pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
        
        self.screen.blit(window_surface, (window_x, window_y))
        
        # Рамка
        pygame.draw.rect(self.screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=16)
        inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_rect, 2, border_radius=14)
        
        # Крестик для закрытия
        close_size = 30
        close_x = window_x + window_w - close_size - 10
        close_y = window_y + 10
        self.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        pygame.draw.rect(self.screen, (180, 60, 60), self.unit_info_close_button_rect, border_radius=5)
        font_close = pygame.font.Font(None, 32)
        close_text = font_close.render("×", True, (255, 255, 255))
        self.screen.blit(close_text, (close_x + 8, close_y + 2))
        
        # Заголовок
        font_title = pygame.font.Font(None, 48)
        title = font_title.render(f"{unit.unit_type.capitalize()}", True, (255, 245, 220))
        title_shadow = font_title.render(f"{unit.unit_type.capitalize()}", True, (60, 50, 40))
        title_x = window_x + (window_w - title.get_width()) // 2
        self.screen.blit(title_shadow, (title_x + 2, window_y + 20))
        self.screen.blit(title, (title_x, window_y + 18))
        
        # Изображение юнита (слева вверху)
        img_size = 120
        img_x = window_x + 30
        img_y = window_y + 80
        if hasattr(unit, 'image') and unit.image:
            img_scaled = pygame.transform.scale(unit.image, (img_size, img_size))
            self.screen.blit(img_scaled, (img_x, img_y))
        
        # Параметры (справа от изображения)
        font_small = pygame.font.Font(None, 24)
        param_x = img_x + img_size + 30
        param_y = window_y + 80
        line_height = 24  # Уменьшаем высоту строки для более компактного отображения
        max_param_width = window_w - param_x - 30  # Максимальная ширина для параметров
        
        # Проверяем, является ли юнит героем
        from .units import Hero
        is_hero = isinstance(unit, Hero)
        
        if is_hero:
            # Для героя показываем только параметры героя
            # Вычисляем базовую атаку в зависимости от класса
            if unit.hero_class == 'mage':
                base_attack = 5 + unit.spell_power
            else:  # warrior или archer
                base_attack = 5 + unit.attack
            
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            params.append(f"Базовая атака: {base_attack}")
            params.append(f"Атака: {unit.attack}")
            params.append(f"Защита: {unit.defense}")
            params.append(f"Сила магии: {unit.spell_power}")
            params.append(f"Знания: {unit.knowledge}")
            params.append(f"Мана: {unit.mana}/{unit.max_mana}")
            params.append(f"Удача: {unit.luck:+d} ({abs(unit.luck) * 5}% шанс двойного урона)")
            params.append(f"Боевой дух: {unit.combat_spirit:+d} ({abs(unit.combat_spirit) * 3}% шанс доп. хода)")
        else:
            # Для обычного юнита показываем параметры юнита
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                params.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    params.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    params.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    params.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    params.append(f"Атака (маг): {unit.magic_attack}")
                params.append(f"Защита (физ): {unit.phys_defense}")
                params.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    params.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                params.append(f"Атака: {getattr(unit, 'attack', 0)}")
                params.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            params.append(f"Скорость: {unit.speed}")
            params.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                params.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    params.append(f"Дальность: {unit.attack_range}")
            # Удача показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'luck'):
                luck = getattr(unit, 'luck', 0)
                params.append(f"Удача: {luck:+d} ({abs(luck) * 5}% шанс двойного урона)")
            # Боевой дух показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'combat_spirit'):
                combat_spirit = getattr(unit, 'combat_spirit', 0)
                params.append(f"Боевой дух: {combat_spirit:+d} ({abs(combat_spirit) * 3}% шанс доп. хода)")
            # Мораль показывается только в окне информации (не в тултипе), только для юнитов
            if hasattr(unit, 'morale') and not isinstance(unit, Hero):
                morale = getattr(unit, 'morale', 'good')
                morale_names = {
                    'excellent': 'Отличная',
                    'good': 'Хорошая',
                    'neutral': 'Нейтральная',
                    'bad': 'Плохая',
                    'awful': 'Ужасная'
                }
                morale_name = morale_names.get(morale, morale)
                params.append(f"Мораль: {morale_name}")
        
        # Отображаем параметры с переносом во второй столбец при необходимости
        current_y = param_y
        column1_x = param_x
        column1_max_y = param_y  # Максимальная высота первого столбца
        column2_x = param_x + max_param_width // 2 + 20  # Второй столбец правее
        max_params_per_column = 12  # Максимальное количество параметров в первом столбце
        current_column = 1
        column2_y = param_y  # Высота для второго столбца
        
        for i, param in enumerate(params):
            # Если параметров много, переходим во второй столбец
            if i >= max_params_per_column and current_column == 1:
                current_column = 2
                column2_y = param_y  # Начинаем с верха для второго столбца
                column1_max_y = current_y  # Сохраняем максимальную высоту первого столбца
            
            # Определяем позицию X в зависимости от столбца
            if current_column == 2:
                param_x_current = column2_x
                max_param_width_current = window_w - column2_x - 30
                current_y = column2_y
            else:
                param_x_current = column1_x
                max_param_width_current = max_param_width
                column1_max_y = current_y  # Обновляем максимальную высоту первого столбца
            
            # Проверяем, не выходит ли текст за пределы окна
            text_width = font_small.size(param)[0]
            if text_width > max_param_width_current:
                # Если текст слишком длинный, разбиваем на несколько строк
                words = param.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font_small.size(test_line)[0] <= max_param_width_current:
                        current_line = test_line
                    else:
                        if current_line:
                            text = font_small.render(current_line, True, (220, 220, 220))
                            self.screen.blit(text, (param_x_current, current_y))
                            current_y += line_height
                            if current_column == 2:
                                column2_y = current_y
                            else:
                                column1_max_y = current_y
                        current_line = word
                if current_line:
                    text = font_small.render(current_line, True, (220, 220, 220))
                    self.screen.blit(text, (param_x_current, current_y))
                    current_y += line_height
                    if current_column == 2:
                        column2_y = current_y
                    else:
                        column1_max_y = current_y
            else:
                text = font_small.render(param, True, (220, 220, 220))
                self.screen.blit(text, (param_x_current, current_y))
                current_y += line_height
                if current_column == 2:
                    column2_y = current_y
                else:
                    column1_max_y = current_y
        
        # Поля для способностей и пассивок (внизу) - динамически позиционируем
        # Оставляем минимум 120 пикселей снизу, но ограничиваем максимальное смещение
        min_effects_space = 120
        # Если использовались два столбца, берем максимальную высоту обоих столбцов
        if current_column == 2:
            param_bottom = max(column1_max_y, column2_y) + 20
        else:
            param_bottom = column1_max_y + 20  # Отступ снизу после параметров
        max_effects_y = window_y + window_h - min_effects_space  # Максимальная позиция (не ниже 120px от низа)
        abilities_y = min(max_effects_y, param_bottom + 20)  # Берем минимум, чтобы не уходило слишком далеко
        pygame.draw.line(self.screen, (100, 80, 60), (window_x + 20, abilities_y), (window_x + window_w - 20, abilities_y), 2)
        font_label = pygame.font.Font(None, 26)
        label = font_label.render("Временные эффекты:", True, (200, 180, 140))
        self.screen.blit(label, (window_x + 20, abilities_y + 10))
        
        # Собираем все временные эффекты
        effects = []
        effects_y = abilities_y + 35
        line_height_effects = 20
        max_lines = 3  # Максимум 3 строки эффектов
        
        # Защита
        if hasattr(unit, '_defend_this_round') and getattr(unit, '_defend_this_round', False):
            effects.append(("В защите", (100, 180, 255)))
        
        # Благословение/Проклятие
        if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
            effects.append((f"Благословение ({unit.attack_buff_turns} ход.)", (80, 255, 80)))
        if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
            effects.append((f"Проклятие ({unit.attack_debuff_turns} ход.)", (255, 80, 80)))
        
        # Руны
        if hasattr(unit, 'rune_shield_turns') and getattr(unit, 'rune_shield_turns', 0) > 0:
            effects.append((f"Руна защиты ({unit.rune_shield_turns} ход.)", (80, 255, 120)))
        if hasattr(unit, 'rune_magic_turns') and getattr(unit, 'rune_magic_turns', 0) > 0:
            effects.append((f"Руна магии ({unit.rune_magic_turns} ход.)", (200, 150, 255)))
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            effects.append((f"Руна берсерка ({unit.rune_berserker_turns} ход.)", (255, 80, 80)))
        if hasattr(unit, 'rune_haste_turns') and getattr(unit, 'rune_haste_turns', 0) > 0:
            effects.append((f"Руна скорости ({unit.rune_haste_turns} ход.)", (120, 200, 255)))
        
        # Замедление/Ускорение
        if hasattr(unit, 'slow_turns') and getattr(unit, 'slow_turns', 0) > 0:
            effects.append((f"Замедление ({unit.slow_turns} ход.)", (255, 120, 120)))
        if hasattr(unit, 'haste_turns') and getattr(unit, 'haste_turns', 0) > 0:
            effects.append((f"Ускорение ({unit.haste_turns} ход.)", (120, 255, 120)))
        
        # Ослепление
        if hasattr(unit, 'blindness_turns') and getattr(unit, 'blindness_turns', 0) > 0:
            effects.append((f"Ослепление ({unit.blindness_turns} ход.)", (200, 200, 80)))
        
        # Молитва
        if hasattr(unit, 'prayer_turns') and getattr(unit, 'prayer_turns', 0) > 0:
            effects.append((f"Молитва ({unit.prayer_turns} ход.)", (255, 255, 200)))
        
        # Точность
        if hasattr(unit, 'accuracy_turns') and getattr(unit, 'accuracy_turns', 0) > 0:
            effects.append((f"Точность ({unit.accuracy_turns} ход.)", (255, 200, 100)))
        
        # Каменная кожа
        if hasattr(unit, 'stone_skin_turns') and getattr(unit, 'stone_skin_turns', 0) > 0:
            effects.append((f"Каменная кожа ({unit.stone_skin_turns} ход.)", (200, 200, 200)))
        
        # Огненный щит
        if hasattr(unit, 'fire_shield_turns') and getattr(unit, 'fire_shield_turns', 0) > 0:
            effects.append((f"Огненный щит ({unit.fire_shield_turns} ход.)", (255, 100, 50)))
        
        # Ледяной щит
        if hasattr(unit, 'ice_shield_turns') and getattr(unit, 'ice_shield_turns', 0) > 0:
            effects.append((f"Ледяной щит ({unit.ice_shield_turns} ход.)", (100, 200, 255)))
        
        # Контрудар
        if hasattr(unit, 'counterstrike_turns') and getattr(unit, 'counterstrike_turns', 0) > 0:
            effects.append((f"Контрудар ({unit.counterstrike_turns} ход.)", (255, 180, 100)))
        
        # Слабость
        if hasattr(unit, 'weakness_turns') and getattr(unit, 'weakness_turns', 0) > 0:
            effects.append((f"Слабость ({unit.weakness_turns} ход.)", (200, 100, 100)))
        
        # Забвение
        if hasattr(unit, 'forget_turns') and getattr(unit, 'forget_turns', 0) > 0:
            effects.append((f"Забвение ({unit.forget_turns} ход.)", (150, 150, 150)))
        
        # Отображаем эффекты
        if effects:
            for i, (effect_name, effect_color) in enumerate(effects[:max_lines]):
                effect_text = font_small.render(effect_name, True, effect_color)
                self.screen.blit(effect_text, (window_x + 20, effects_y + i * line_height_effects))
            if len(effects) > max_lines:
                more_text = font_small.render(f"... и еще {len(effects) - max_lines}", True, (150, 150, 150))
                self.screen.blit(more_text, (window_x + 20, effects_y + max_lines * line_height_effects))
        else:
            no_effects = font_small.render("Нет активных эффектов", True, (150, 150, 150))
            self.screen.blit(no_effects, (window_x + 20, effects_y))
        
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Отладочное логирование начала применения заклинания
            self.anim_logger.log("SPELL_CAST_START", f"Герой кастует {spell.name} ({spell.icon}) target_type={spell.target_type}")
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
                spell_name = getattr(spell, 'name', '')
                spell_icon = getattr(spell, 'icon', '')
                # Проверяем мгновенные заклинания (без анимации полета снаряда)
                instant_spells = [
                    'lightning', 'weakness', 'bless', 'curse', 'slow', 'haste',
                    'heal', 'dispel', 'stone_skin', 'ice_shield', 'fire_shield',
                    'counterstrike', 'rune_shield', 'rune_haste', 'raise_dead',
                    'resurrection', 'undead_heal', 'forget', 'earth_spikes', 'rune_wall'
                ]
                is_instant_spell = (spell_icon in instant_spells or 
                                  spell_name in ['Молния', 'Слабость', 'Благословение', 'Проклятие', 
                                                'Замедление', 'Ускорение', 'Лечение', 'Снятие чар'] or
                                  any(keyword in spell_icon.lower() for keyword in ['lightning', 'weakness', 'bless', 'curse']))
                
                # Отладочное логирование
                self.anim_logger.log("SPELL_CHECK", f"name='{spell_name}' icon='{spell_icon}' instant={is_instant_spell}")
                
                # Логируем анимацию заклинания
                self.anim_logger.log_spell_animation(spell_name, spell_icon, self.selected_unit, target, is_instant_spell)
                
                if spell_icon == 'firearrow':
                    self.anim_logger.log("FIREARROW_ANIMATION", f"Огненная стрела от {self.selected_unit.unit_type} к {target.unit_type}")
                    self.animate_firearrow(self.selected_unit, target)
                elif not is_instant_spell:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    # Воспроизводим звук выстрела магов
                    if self.magic_shot_sound:
                        self.magic_shot_sound.play()
                    self.anim_logger.log_projectile_animation("magic_bolt", 
                        (self.selected_unit.x, self.selected_unit.y), 
                        (target.x, target.y), color)
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                # Применяем заклинание (для Молнии и Слабости - мгновенно, без анимации)
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
            if self.selected_unit.can_move(x, y, self.units, self.barriers):
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
                # Проверяем расстояние для определения типа атаки
                distance = abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)
                is_melee = (distance == 1)
                damage_already_applied = False  # Флаг для отслеживания применения урона
                
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    # Лучники и дальнобойные юниты
                    if is_melee:
                        # Ближний бой для лучников - только ближний бой, без стрел
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = max(1, self.selected_unit.get_current_attack() // 2)  # Половина урона
                        # Запоминаем параметры для контратаки (даже для лучников в ближнем бою)
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                    else:
                        # Дальняя атака - стреляем стрелами/снарядами, контратаки нет
                        target_is_melee_unit = False  # Дальняя атака, контратаки нет
                        start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                        end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                        
                        # Проверяем, является ли атакующий героем
                        is_hero = isinstance(self.selected_unit, Hero)
                        hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                        
                        # Определяем тип снаряда в зависимости от юнита/героя
                        if is_hero and hero_class == 'archer':
                            # Герой-лучник: стреляет стрелами
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            pygame.time.delay(150)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
                        elif self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                            # Обычные лучники стреляют стрелами - воспроизводим звуки
                            # Звук натяжения лука
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            # Небольшая задержка для звука натяжения
                            pygame.time.delay(150)
                            # Звук выстрела - используем новые звуки выстрелов (случайный выбор)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            # Анимация полета стрелы
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            # Звук попадания
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
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
                            # Воспроизводим звук выстрела магов
                            if self.magic_shot_sound:
                                self.magic_shot_sound.play()
                            animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                        # Перерисовываем экран, чтобы убрать снаряд
                        self.draw()
                        pygame.display.flip()
                        # Для дальнобойной атаки проверяем руну магии с учетом множителя дальности
                        mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit, is_ranged=True, target_x=x, target_y=y)
                        if mixed_damage is not None:
                            # Для руны магии используем смешанный урон
                            damage = None  # Будет применен через mixed_damage
                        else:
                            # Обычный расчет урона для дальнобойных
                            damage = self.selected_unit.ranged_damage(x, y)
                        
                        # Применяем урон для дальнобойных атак
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            elif damage is not None:
                                clicked_unit.take_damage(damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
                else:
                    # Обычные ближние бойцы и герои-воины
                    # Проверяем героя-воина - у него особая анимация
                    is_hero = isinstance(self.selected_unit, Hero)
                    hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                    
                    if is_hero and hero_class == 'warrior':
                        # Герой-воин: телепортация к цели
                        damage = self.selected_unit.get_current_attack()
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Сохраняем здоровье до атаки для вычисления урона
                        health_before = clicked_unit.health
                        # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                        squad_count_before_warrior = getattr(clicked_unit, 'squad_count', 1)
                        
                        # Создаем callback для применения урона (ТОЛЬКО урон, без последствий)
                        def apply_warrior_damage():
                            nonlocal damage_already_applied
                            damage_already_applied = True
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                        
                        # Вычисляем позицию рядом с целью
                        dx = clicked_unit.x - self.selected_unit.x
                        dy = clicked_unit.y - self.selected_unit.y
                        # Позиция рядом с целью (смещение в направлении атакующего)
                        if abs(dx) > abs(dy):
                            attack_x = clicked_unit.x - (1 if dx > 0 else -1)
                            attack_y = clicked_unit.y
                        else:
                            attack_x = clicked_unit.x
                            attack_y = clicked_unit.y - (1 if dy > 0 else -1)
                        
                        # Запускаем анимацию телепортации
                        animate_warrior_teleport(self.screen, 
                                                (self.selected_unit.x * CELL_SIZE, self.selected_unit.y * CELL_SIZE),
                                                (attack_x * CELL_SIZE, attack_y * CELL_SIZE),
                                                self.selected_unit.image,
                                                redraw_callback=self.draw,
                                                attack_sound_callback=lambda: (random.choice(self.human_melee_sounds).play() if self.human_melee_sounds and hasattr(random, 'choice') else None) if self.selected_unit.team in ['human', 'elf', 'dwarf'] else (random.choice(self.monster_melee_sounds).play() if self.monster_melee_sounds and hasattr(random, 'choice') else None),
                                                damage_callback=apply_warrior_damage,
                                                hide_attacker_pos=(self.selected_unit.x, self.selected_unit.y))
                        
                        # Вычисляем нанесенный урон
                        actual_damage = health_before - clicked_unit.health
                        
                        # ПОСЛЕ анимации обрабатываем последствия
                        squad_count_after_warrior = getattr(clicked_unit, 'squad_count', 1)
                        units_lost_warrior = squad_count_before_warrior - squad_count_after_warrior
                        if clicked_unit.health <= 0:
                            self.kill_unit(clicked_unit)
                            self.animate_queue_fade(clicked_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", уничтожено {units_lost_warrior} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", потеряно {units_lost_warrior} юнитов из отряда ({squad_count_after_warrior}/{squad_count_before_warrior})"
                            self.add_event(event_msg)
                            # Контратака происходит ПОСЛЕ анимации
                            self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки для героя-воина и переходим к следующему ходу
                        self.selected_unit.has_attacked = True
                        self.next_turn()
                        return
                    else:
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = self.selected_unit.get_current_attack()
                        # Запоминаем параметры для контратаки
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Применяем урон для обычных ближних бойцов
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                                # Контратака происходит ПОСЛЕ нанесения урона
                                self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
    
    def draw_unit_tooltip(self, unit):
        """Отрисовка тултипа юнита при зажатии правой кнопки мыши"""
        from .units import Hero
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)
        
        # Собираем информацию о юните
        lines = []
        lines.append(f"{unit.unit_type.capitalize()}")
        lines.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
        
        # Для героев показываем те же параметры что в окне информации (кроме удачи и боевого духа)
        if isinstance(unit, Hero):
            # Базовые параметры
            base_attack = getattr(unit, 'base_attack', None)
            if base_attack is None:
                # Вычисляем базовую атаку в зависимости от класса
                if unit.hero_class == 'mage':
                    base_attack = 5 + unit.spell_power
                else:  # warrior или archer
                    base_attack = 5 + unit.attack
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            knowledge = getattr(unit, 'knowledge', 0)
            spell_power = getattr(unit, 'spell_power', 0)
            mana = getattr(unit, 'mana', 0)
            max_mana = getattr(unit, 'max_mana', 0)
            
            lines.append(f"Базовая атака: {base_attack}")
            lines.append(f"Атака: {attack}")
            lines.append(f"Защита: {defense}")
            lines.append(f"Знания: {knowledge}")
            lines.append(f"Сила магии: {spell_power}")
            lines.append(f"Мана: {mana}/{max_mana}")
        else:
            # Для обычных юнитов показываем стандартную информацию
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                lines.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    lines.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    lines.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            # Атака и защита
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    lines.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    lines.append(f"Атака (маг): {unit.magic_attack}")
                lines.append(f"Защита (физ): {unit.phys_defense}")
                lines.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    lines.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                lines.append(f"Атака: {getattr(unit, 'attack', 0)}")
                lines.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            lines.append(f"Скорость: {unit.speed}")
            lines.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                lines.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    lines.append(f"Дальность: {unit.attack_range}")
        
        # Вычисляем размеры тултипа
        max_width = 0
        for line in lines:
            if line:
                width = font_small.size(line)[0]
                max_width = max(max_width, width)
        
        padding = 10
        line_height = 22
        tooltip_w = max_width + padding * 2
        tooltip_h = len(lines) * line_height + padding * 2
        
        # Позиция тултипа (рядом с курсором, но не выходя за экран)
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        if tooltip_x + tooltip_w > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_w - 20
        if tooltip_y + tooltip_h > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_h - 20
        
        # Фон тултипа
        tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surface.fill((40, 40, 80, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 150), (0, 0, tooltip_w, tooltip_h), 2)
        
        # Текст
        y_offset = padding
        for i, line in enumerate(lines):
            if line:
                if i == 0:  # Заголовок
                    text = font_bold.render(line, True, (255, 255, 180))
                else:
                    text = font_small.render(line, True, (220, 220, 220))
                tooltip_surface.blit(text, (padding, y_offset))
                y_offset += line_height
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_unit_info_window(self, unit):
        """Отрисовка окна информации о юните (при двойном клике)"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна
        window_w, window_h = 600, 500
        window_x = (SCREEN_WIDTH - window_w) // 2
        window_y = (SCREEN_HEIGHT - window_h) // 2
        
        # Фон окна (деревянный стиль)
        window_surface = pygame.Surface((window_w, window_h))
        for y in range(window_h):
            gradient = (
                int(150 - y * 0.2),
                int(110 - y * 0.15),
                int(80 - y * 0.1)
            )
            pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
        
        self.screen.blit(window_surface, (window_x, window_y))
        
        # Рамка
        pygame.draw.rect(self.screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=16)
        inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_rect, 2, border_radius=14)
        
        # Крестик для закрытия
        close_size = 30
        close_x = window_x + window_w - close_size - 10
        close_y = window_y + 10
        self.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        pygame.draw.rect(self.screen, (180, 60, 60), self.unit_info_close_button_rect, border_radius=5)
        font_close = pygame.font.Font(None, 32)
        close_text = font_close.render("×", True, (255, 255, 255))
        self.screen.blit(close_text, (close_x + 8, close_y + 2))
        
        # Заголовок
        font_title = pygame.font.Font(None, 48)
        title = font_title.render(f"{unit.unit_type.capitalize()}", True, (255, 245, 220))
        title_shadow = font_title.render(f"{unit.unit_type.capitalize()}", True, (60, 50, 40))
        title_x = window_x + (window_w - title.get_width()) // 2
        self.screen.blit(title_shadow, (title_x + 2, window_y + 20))
        self.screen.blit(title, (title_x, window_y + 18))
        
        # Изображение юнита (слева вверху)
        img_size = 120
        img_x = window_x + 30
        img_y = window_y + 80
        if hasattr(unit, 'image') and unit.image:
            img_scaled = pygame.transform.scale(unit.image, (img_size, img_size))
            self.screen.blit(img_scaled, (img_x, img_y))
        
        # Параметры (справа от изображения)
        font_small = pygame.font.Font(None, 24)
        param_x = img_x + img_size + 30
        param_y = window_y + 80
        line_height = 24  # Уменьшаем высоту строки для более компактного отображения
        max_param_width = window_w - param_x - 30  # Максимальная ширина для параметров
        
        # Проверяем, является ли юнит героем
        from .units import Hero
        is_hero = isinstance(unit, Hero)
        
        if is_hero:
            # Для героя показываем только параметры героя
            # Вычисляем базовую атаку в зависимости от класса
            if unit.hero_class == 'mage':
                base_attack = 5 + unit.spell_power
            else:  # warrior или archer
                base_attack = 5 + unit.attack
            
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            params.append(f"Базовая атака: {base_attack}")
            params.append(f"Атака: {unit.attack}")
            params.append(f"Защита: {unit.defense}")
            params.append(f"Сила магии: {unit.spell_power}")
            params.append(f"Знания: {unit.knowledge}")
            params.append(f"Мана: {unit.mana}/{unit.max_mana}")
            params.append(f"Удача: {unit.luck:+d} ({abs(unit.luck) * 5}% шанс двойного урона)")
            params.append(f"Боевой дух: {unit.combat_spirit:+d} ({abs(unit.combat_spirit) * 3}% шанс доп. хода)")
        else:
            # Для обычного юнита показываем параметры юнита
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                params.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    params.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    params.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    params.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    params.append(f"Атака (маг): {unit.magic_attack}")
                params.append(f"Защита (физ): {unit.phys_defense}")
                params.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    params.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                params.append(f"Атака: {getattr(unit, 'attack', 0)}")
                params.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            params.append(f"Скорость: {unit.speed}")
            params.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                params.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    params.append(f"Дальность: {unit.attack_range}")
            # Удача показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'luck'):
                luck = getattr(unit, 'luck', 0)
                params.append(f"Удача: {luck:+d} ({abs(luck) * 5}% шанс двойного урона)")
            # Боевой дух показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'combat_spirit'):
                combat_spirit = getattr(unit, 'combat_spirit', 0)
                params.append(f"Боевой дух: {combat_spirit:+d} ({abs(combat_spirit) * 3}% шанс доп. хода)")
            # Мораль показывается только в окне информации (не в тултипе), только для юнитов
            if hasattr(unit, 'morale') and not isinstance(unit, Hero):
                morale = getattr(unit, 'morale', 'good')
                morale_names = {
                    'excellent': 'Отличная',
                    'good': 'Хорошая',
                    'neutral': 'Нейтральная',
                    'bad': 'Плохая',
                    'awful': 'Ужасная'
                }
                morale_name = morale_names.get(morale, morale)
                params.append(f"Мораль: {morale_name}")
        
        # Отображаем параметры с переносом во второй столбец при необходимости
        current_y = param_y
        column1_x = param_x
        column1_max_y = param_y  # Максимальная высота первого столбца
        column2_x = param_x + max_param_width // 2 + 20  # Второй столбец правее
        max_params_per_column = 12  # Максимальное количество параметров в первом столбце
        current_column = 1
        column2_y = param_y  # Высота для второго столбца
        
        for i, param in enumerate(params):
            # Если параметров много, переходим во второй столбец
            if i >= max_params_per_column and current_column == 1:
                current_column = 2
                column2_y = param_y  # Начинаем с верха для второго столбца
                column1_max_y = current_y  # Сохраняем максимальную высоту первого столбца
            
            # Определяем позицию X в зависимости от столбца
            if current_column == 2:
                param_x_current = column2_x
                max_param_width_current = window_w - column2_x - 30
                current_y = column2_y
            else:
                param_x_current = column1_x
                max_param_width_current = max_param_width
                column1_max_y = current_y  # Обновляем максимальную высоту первого столбца
            
            # Проверяем, не выходит ли текст за пределы окна
            text_width = font_small.size(param)[0]
            if text_width > max_param_width_current:
                # Если текст слишком длинный, разбиваем на несколько строк
                words = param.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font_small.size(test_line)[0] <= max_param_width_current:
                        current_line = test_line
                    else:
                        if current_line:
                            text = font_small.render(current_line, True, (220, 220, 220))
                            self.screen.blit(text, (param_x_current, current_y))
                            current_y += line_height
                            if current_column == 2:
                                column2_y = current_y
                            else:
                                column1_max_y = current_y
                        current_line = word
                if current_line:
                    text = font_small.render(current_line, True, (220, 220, 220))
                    self.screen.blit(text, (param_x_current, current_y))
                    current_y += line_height
                    if current_column == 2:
                        column2_y = current_y
                    else:
                        column1_max_y = current_y
            else:
                text = font_small.render(param, True, (220, 220, 220))
                self.screen.blit(text, (param_x_current, current_y))
                current_y += line_height
                if current_column == 2:
                    column2_y = current_y
                else:
                    column1_max_y = current_y
        
        # Поля для способностей и пассивок (внизу) - динамически позиционируем
        # Оставляем минимум 120 пикселей снизу, но ограничиваем максимальное смещение
        min_effects_space = 120
        # Если использовались два столбца, берем максимальную высоту обоих столбцов
        if current_column == 2:
            param_bottom = max(column1_max_y, column2_y) + 20
        else:
            param_bottom = column1_max_y + 20  # Отступ снизу после параметров
        max_effects_y = window_y + window_h - min_effects_space  # Максимальная позиция (не ниже 120px от низа)
        abilities_y = min(max_effects_y, param_bottom + 20)  # Берем минимум, чтобы не уходило слишком далеко
        pygame.draw.line(self.screen, (100, 80, 60), (window_x + 20, abilities_y), (window_x + window_w - 20, abilities_y), 2)
        font_label = pygame.font.Font(None, 26)
        label = font_label.render("Временные эффекты:", True, (200, 180, 140))
        self.screen.blit(label, (window_x + 20, abilities_y + 10))
        
        # Собираем все временные эффекты
        effects = []
        effects_y = abilities_y + 35
        line_height_effects = 20
        max_lines = 3  # Максимум 3 строки эффектов
        
        # Защита
        if hasattr(unit, '_defend_this_round') and getattr(unit, '_defend_this_round', False):
            effects.append(("В защите", (100, 180, 255)))
        
        # Благословение/Проклятие
        if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
            effects.append((f"Благословение ({unit.attack_buff_turns} ход.)", (80, 255, 80)))
        if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
            effects.append((f"Проклятие ({unit.attack_debuff_turns} ход.)", (255, 80, 80)))
        
        # Руны
        if hasattr(unit, 'rune_shield_turns') and getattr(unit, 'rune_shield_turns', 0) > 0:
            effects.append((f"Руна защиты ({unit.rune_shield_turns} ход.)", (80, 255, 120)))
        if hasattr(unit, 'rune_magic_turns') and getattr(unit, 'rune_magic_turns', 0) > 0:
            effects.append((f"Руна магии ({unit.rune_magic_turns} ход.)", (200, 150, 255)))
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            effects.append((f"Руна берсерка ({unit.rune_berserker_turns} ход.)", (255, 80, 80)))
        if hasattr(unit, 'rune_haste_turns') and getattr(unit, 'rune_haste_turns', 0) > 0:
            effects.append((f"Руна скорости ({unit.rune_haste_turns} ход.)", (120, 200, 255)))
        
        # Замедление/Ускорение
        if hasattr(unit, 'slow_turns') and getattr(unit, 'slow_turns', 0) > 0:
            effects.append((f"Замедление ({unit.slow_turns} ход.)", (255, 120, 120)))
        if hasattr(unit, 'haste_turns') and getattr(unit, 'haste_turns', 0) > 0:
            effects.append((f"Ускорение ({unit.haste_turns} ход.)", (120, 255, 120)))
        
        # Ослепление
        if hasattr(unit, 'blindness_turns') and getattr(unit, 'blindness_turns', 0) > 0:
            effects.append((f"Ослепление ({unit.blindness_turns} ход.)", (200, 200, 80)))
        
        # Молитва
        if hasattr(unit, 'prayer_turns') and getattr(unit, 'prayer_turns', 0) > 0:
            effects.append((f"Молитва ({unit.prayer_turns} ход.)", (255, 255, 200)))
        
        # Точность
        if hasattr(unit, 'accuracy_turns') and getattr(unit, 'accuracy_turns', 0) > 0:
            effects.append((f"Точность ({unit.accuracy_turns} ход.)", (255, 200, 100)))
        
        # Каменная кожа
        if hasattr(unit, 'stone_skin_turns') and getattr(unit, 'stone_skin_turns', 0) > 0:
            effects.append((f"Каменная кожа ({unit.stone_skin_turns} ход.)", (200, 200, 200)))
        
        # Огненный щит
        if hasattr(unit, 'fire_shield_turns') and getattr(unit, 'fire_shield_turns', 0) > 0:
            effects.append((f"Огненный щит ({unit.fire_shield_turns} ход.)", (255, 100, 50)))
        
        # Ледяной щит
        if hasattr(unit, 'ice_shield_turns') and getattr(unit, 'ice_shield_turns', 0) > 0:
            effects.append((f"Ледяной щит ({unit.ice_shield_turns} ход.)", (100, 200, 255)))
        
        # Контрудар
        if hasattr(unit, 'counterstrike_turns') and getattr(unit, 'counterstrike_turns', 0) > 0:
            effects.append((f"Контрудар ({unit.counterstrike_turns} ход.)", (255, 180, 100)))
        
        # Слабость
        if hasattr(unit, 'weakness_turns') and getattr(unit, 'weakness_turns', 0) > 0:
            effects.append((f"Слабость ({unit.weakness_turns} ход.)", (200, 100, 100)))
        
        # Забвение
        if hasattr(unit, 'forget_turns') and getattr(unit, 'forget_turns', 0) > 0:
            effects.append((f"Забвение ({unit.forget_turns} ход.)", (150, 150, 150)))
        
        # Отображаем эффекты
        if effects:
            for i, (effect_name, effect_color) in enumerate(effects[:max_lines]):
                effect_text = font_small.render(effect_name, True, effect_color)
                self.screen.blit(effect_text, (window_x + 20, effects_y + i * line_height_effects))
            if len(effects) > max_lines:
                more_text = font_small.render(f"... и еще {len(effects) - max_lines}", True, (150, 150, 150))
                self.screen.blit(more_text, (window_x + 20, effects_y + max_lines * line_height_effects))
        else:
            no_effects = font_small.render("Нет активных эффектов", True, (150, 150, 150))
            self.screen.blit(no_effects, (window_x + 20, effects_y))
        
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Отладочное логирование начала применения заклинания
            self.anim_logger.log("SPELL_CAST_START", f"Герой кастует {spell.name} ({spell.icon}) target_type={spell.target_type}")
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
                spell_name = getattr(spell, 'name', '')
                spell_icon = getattr(spell, 'icon', '')
                # Проверяем мгновенные заклинания (без анимации полета снаряда)
                instant_spells = [
                    'lightning', 'weakness', 'bless', 'curse', 'slow', 'haste',
                    'heal', 'dispel', 'stone_skin', 'ice_shield', 'fire_shield',
                    'counterstrike', 'rune_shield', 'rune_haste', 'raise_dead',
                    'resurrection', 'undead_heal', 'forget', 'earth_spikes', 'rune_wall'
                ]
                is_instant_spell = (spell_icon in instant_spells or 
                                  spell_name in ['Молния', 'Слабость', 'Благословение', 'Проклятие', 
                                                'Замедление', 'Ускорение', 'Лечение', 'Снятие чар'] or
                                  any(keyword in spell_icon.lower() for keyword in ['lightning', 'weakness', 'bless', 'curse']))
                
                # Отладочное логирование
                self.anim_logger.log("SPELL_CHECK", f"name='{spell_name}' icon='{spell_icon}' instant={is_instant_spell}")
                
                # Логируем анимацию заклинания
                self.anim_logger.log_spell_animation(spell_name, spell_icon, self.selected_unit, target, is_instant_spell)
                
                if spell_icon == 'firearrow':
                    self.anim_logger.log("FIREARROW_ANIMATION", f"Огненная стрела от {self.selected_unit.unit_type} к {target.unit_type}")
                    self.animate_firearrow(self.selected_unit, target)
                elif not is_instant_spell:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    # Воспроизводим звук выстрела магов
                    if self.magic_shot_sound:
                        self.magic_shot_sound.play()
                    self.anim_logger.log_projectile_animation("magic_bolt", 
                        (self.selected_unit.x, self.selected_unit.y), 
                        (target.x, target.y), color)
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                # Применяем заклинание (для Молнии и Слабости - мгновенно, без анимации)
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
            if self.selected_unit.can_move(x, y, self.units, self.barriers):
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
                # Проверяем расстояние для определения типа атаки
                distance = abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)
                is_melee = (distance == 1)
                damage_already_applied = False  # Флаг для отслеживания применения урона
                
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    # Лучники и дальнобойные юниты
                    if is_melee:
                        # Ближний бой для лучников - только ближний бой, без стрел
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = max(1, self.selected_unit.get_current_attack() // 2)  # Половина урона
                        # Запоминаем параметры для контратаки (даже для лучников в ближнем бою)
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                    else:
                        # Дальняя атака - стреляем стрелами/снарядами, контратаки нет
                        target_is_melee_unit = False  # Дальняя атака, контратаки нет
                        start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                        end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                        
                        # Проверяем, является ли атакующий героем
                        is_hero = isinstance(self.selected_unit, Hero)
                        hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                        
                        # Определяем тип снаряда в зависимости от юнита/героя
                        if is_hero and hero_class == 'archer':
                            # Герой-лучник: стреляет стрелами
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            pygame.time.delay(150)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
                        elif self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                            # Обычные лучники стреляют стрелами - воспроизводим звуки
                            # Звук натяжения лука
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            # Небольшая задержка для звука натяжения
                            pygame.time.delay(150)
                            # Звук выстрела - используем новые звуки выстрелов (случайный выбор)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            # Анимация полета стрелы
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            # Звук попадания
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
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
                            # Воспроизводим звук выстрела магов
                            if self.magic_shot_sound:
                                self.magic_shot_sound.play()
                            animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                        # Перерисовываем экран, чтобы убрать снаряд
                        self.draw()
                        pygame.display.flip()
                        # Для дальнобойной атаки проверяем руну магии с учетом множителя дальности
                        mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit, is_ranged=True, target_x=x, target_y=y)
                        if mixed_damage is not None:
                            # Для руны магии используем смешанный урон
                            damage = None  # Будет применен через mixed_damage
                        else:
                            # Обычный расчет урона для дальнобойных
                            damage = self.selected_unit.ranged_damage(x, y)
                        
                        # Применяем урон для дальнобойных атак
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            elif damage is not None:
                                clicked_unit.take_damage(damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
                else:
                    # Обычные ближние бойцы и герои-воины
                    # Проверяем героя-воина - у него особая анимация
                    is_hero = isinstance(self.selected_unit, Hero)
                    hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                    
                    if is_hero and hero_class == 'warrior':
                        # Герой-воин: телепортация к цели
                        damage = self.selected_unit.get_current_attack()
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Сохраняем здоровье до атаки для вычисления урона
                        health_before = clicked_unit.health
                        # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                        squad_count_before_warrior = getattr(clicked_unit, 'squad_count', 1)
                        
                        # Создаем callback для применения урона (ТОЛЬКО урон, без последствий)
                        def apply_warrior_damage():
                            nonlocal damage_already_applied
                            damage_already_applied = True
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                        
                        # Вычисляем позицию рядом с целью
                        dx = clicked_unit.x - self.selected_unit.x
                        dy = clicked_unit.y - self.selected_unit.y
                        # Позиция рядом с целью (смещение в направлении атакующего)
                        if abs(dx) > abs(dy):
                            attack_x = clicked_unit.x - (1 if dx > 0 else -1)
                            attack_y = clicked_unit.y
                        else:
                            attack_x = clicked_unit.x
                            attack_y = clicked_unit.y - (1 if dy > 0 else -1)
                        
                        # Запускаем анимацию телепортации
                        animate_warrior_teleport(self.screen, 
                                                (self.selected_unit.x * CELL_SIZE, self.selected_unit.y * CELL_SIZE),
                                                (attack_x * CELL_SIZE, attack_y * CELL_SIZE),
                                                self.selected_unit.image,
                                                redraw_callback=self.draw,
                                                attack_sound_callback=lambda: (random.choice(self.human_melee_sounds).play() if self.human_melee_sounds and hasattr(random, 'choice') else None) if self.selected_unit.team in ['human', 'elf', 'dwarf'] else (random.choice(self.monster_melee_sounds).play() if self.monster_melee_sounds and hasattr(random, 'choice') else None),
                                                damage_callback=apply_warrior_damage,
                                                hide_attacker_pos=(self.selected_unit.x, self.selected_unit.y))
                        
                        # Вычисляем нанесенный урон
                        actual_damage = health_before - clicked_unit.health
                        
                        # ПОСЛЕ анимации обрабатываем последствия
                        squad_count_after_warrior = getattr(clicked_unit, 'squad_count', 1)
                        units_lost_warrior = squad_count_before_warrior - squad_count_after_warrior
                        if clicked_unit.health <= 0:
                            self.kill_unit(clicked_unit)
                            self.animate_queue_fade(clicked_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", уничтожено {units_lost_warrior} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", потеряно {units_lost_warrior} юнитов из отряда ({squad_count_after_warrior}/{squad_count_before_warrior})"
                            self.add_event(event_msg)
                            # Контратака происходит ПОСЛЕ анимации
                            self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки для героя-воина и переходим к следующему ходу
                        self.selected_unit.has_attacked = True
                        self.next_turn()
                        return
                    else:
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = self.selected_unit.get_current_attack()
                        # Запоминаем параметры для контратаки
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Применяем урон для обычных ближних бойцов
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                                # Контратака происходит ПОСЛЕ нанесения урона
                                self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
    
    def draw_unit_tooltip(self, unit):
        """Отрисовка тултипа юнита при зажатии правой кнопки мыши"""
        from .units import Hero
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)
        
        # Собираем информацию о юните
        lines = []
        lines.append(f"{unit.unit_type.capitalize()}")
        lines.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
        
        # Для героев показываем те же параметры что в окне информации (кроме удачи и боевого духа)
        if isinstance(unit, Hero):
            # Базовые параметры
            base_attack = getattr(unit, 'base_attack', None)
            if base_attack is None:
                # Вычисляем базовую атаку в зависимости от класса
                if unit.hero_class == 'mage':
                    base_attack = 5 + unit.spell_power
                else:  # warrior или archer
                    base_attack = 5 + unit.attack
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            knowledge = getattr(unit, 'knowledge', 0)
            spell_power = getattr(unit, 'spell_power', 0)
            mana = getattr(unit, 'mana', 0)
            max_mana = getattr(unit, 'max_mana', 0)
            
            lines.append(f"Базовая атака: {base_attack}")
            lines.append(f"Атака: {attack}")
            lines.append(f"Защита: {defense}")
            lines.append(f"Знания: {knowledge}")
            lines.append(f"Сила магии: {spell_power}")
            lines.append(f"Мана: {mana}/{max_mana}")
        else:
            # Для обычных юнитов показываем стандартную информацию
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                lines.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    lines.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    lines.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            # Атака и защита
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    lines.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    lines.append(f"Атака (маг): {unit.magic_attack}")
                lines.append(f"Защита (физ): {unit.phys_defense}")
                lines.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    lines.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                lines.append(f"Атака: {getattr(unit, 'attack', 0)}")
                lines.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            lines.append(f"Скорость: {unit.speed}")
            lines.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                lines.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    lines.append(f"Дальность: {unit.attack_range}")
        
        # Вычисляем размеры тултипа
        max_width = 0
        for line in lines:
            if line:
                width = font_small.size(line)[0]
                max_width = max(max_width, width)
        
        padding = 10
        line_height = 22
        tooltip_w = max_width + padding * 2
        tooltip_h = len(lines) * line_height + padding * 2
        
        # Позиция тултипа (рядом с курсором, но не выходя за экран)
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        if tooltip_x + tooltip_w > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_w - 20
        if tooltip_y + tooltip_h > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_h - 20
        
        # Фон тултипа
        tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surface.fill((40, 40, 80, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 150), (0, 0, tooltip_w, tooltip_h), 2)
        
        # Текст
        y_offset = padding
        for i, line in enumerate(lines):
            if line:
                if i == 0:  # Заголовок
                    text = font_bold.render(line, True, (255, 255, 180))
                else:
                    text = font_small.render(line, True, (220, 220, 220))
                tooltip_surface.blit(text, (padding, y_offset))
                y_offset += line_height
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_unit_info_window(self, unit):
        """Отрисовка окна информации о юните (при двойном клике)"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна
        window_w, window_h = 600, 500
        window_x = (SCREEN_WIDTH - window_w) // 2
        window_y = (SCREEN_HEIGHT - window_h) // 2
        
        # Фон окна (деревянный стиль)
        window_surface = pygame.Surface((window_w, window_h))
        for y in range(window_h):
            gradient = (
                int(150 - y * 0.2),
                int(110 - y * 0.15),
                int(80 - y * 0.1)
            )
            pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
        
        self.screen.blit(window_surface, (window_x, window_y))
        
        # Рамка
        pygame.draw.rect(self.screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=16)
        inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_rect, 2, border_radius=14)
        
        # Крестик для закрытия
        close_size = 30
        close_x = window_x + window_w - close_size - 10
        close_y = window_y + 10
        self.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        pygame.draw.rect(self.screen, (180, 60, 60), self.unit_info_close_button_rect, border_radius=5)
        font_close = pygame.font.Font(None, 32)
        close_text = font_close.render("×", True, (255, 255, 255))
        self.screen.blit(close_text, (close_x + 8, close_y + 2))
        
        # Заголовок
        font_title = pygame.font.Font(None, 48)
        title = font_title.render(f"{unit.unit_type.capitalize()}", True, (255, 245, 220))
        title_shadow = font_title.render(f"{unit.unit_type.capitalize()}", True, (60, 50, 40))
        title_x = window_x + (window_w - title.get_width()) // 2
        self.screen.blit(title_shadow, (title_x + 2, window_y + 20))
        self.screen.blit(title, (title_x, window_y + 18))
        
        # Изображение юнита (слева вверху)
        img_size = 120
        img_x = window_x + 30
        img_y = window_y + 80
        if hasattr(unit, 'image') and unit.image:
            img_scaled = pygame.transform.scale(unit.image, (img_size, img_size))
            self.screen.blit(img_scaled, (img_x, img_y))
        
        # Параметры (справа от изображения)
        font_small = pygame.font.Font(None, 24)
        param_x = img_x + img_size + 30
        param_y = window_y + 80
        line_height = 24  # Уменьшаем высоту строки для более компактного отображения
        max_param_width = window_w - param_x - 30  # Максимальная ширина для параметров
        
        # Проверяем, является ли юнит героем
        from .units import Hero
        is_hero = isinstance(unit, Hero)
        
        if is_hero:
            # Для героя показываем только параметры героя
            # Вычисляем базовую атаку в зависимости от класса
            if unit.hero_class == 'mage':
                base_attack = 5 + unit.spell_power
            else:  # warrior или archer
                base_attack = 5 + unit.attack
            
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            params.append(f"Базовая атака: {base_attack}")
            params.append(f"Атака: {unit.attack}")
            params.append(f"Защита: {unit.defense}")
            params.append(f"Сила магии: {unit.spell_power}")
            params.append(f"Знания: {unit.knowledge}")
            params.append(f"Мана: {unit.mana}/{unit.max_mana}")
            params.append(f"Удача: {unit.luck:+d} ({abs(unit.luck) * 5}% шанс двойного урона)")
            params.append(f"Боевой дух: {unit.combat_spirit:+d} ({abs(unit.combat_spirit) * 3}% шанс доп. хода)")
        else:
            # Для обычного юнита показываем параметры юнита
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                params.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    params.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    params.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    params.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    params.append(f"Атака (маг): {unit.magic_attack}")
                params.append(f"Защита (физ): {unit.phys_defense}")
                params.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    params.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                params.append(f"Атака: {getattr(unit, 'attack', 0)}")
                params.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            params.append(f"Скорость: {unit.speed}")
            params.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                params.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    params.append(f"Дальность: {unit.attack_range}")
            # Удача показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'luck'):
                luck = getattr(unit, 'luck', 0)
                params.append(f"Удача: {luck:+d} ({abs(luck) * 5}% шанс двойного урона)")
            # Боевой дух показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'combat_spirit'):
                combat_spirit = getattr(unit, 'combat_spirit', 0)
                params.append(f"Боевой дух: {combat_spirit:+d} ({abs(combat_spirit) * 3}% шанс доп. хода)")
            # Мораль показывается только в окне информации (не в тултипе), только для юнитов
            if hasattr(unit, 'morale') and not isinstance(unit, Hero):
                morale = getattr(unit, 'morale', 'good')
                morale_names = {
                    'excellent': 'Отличная',
                    'good': 'Хорошая',
                    'neutral': 'Нейтральная',
                    'bad': 'Плохая',
                    'awful': 'Ужасная'
                }
                morale_name = morale_names.get(morale, morale)
                params.append(f"Мораль: {morale_name}")
        
        # Отображаем параметры с переносом во второй столбец при необходимости
        current_y = param_y
        column1_x = param_x
        column1_max_y = param_y  # Максимальная высота первого столбца
        column2_x = param_x + max_param_width // 2 + 20  # Второй столбец правее
        max_params_per_column = 12  # Максимальное количество параметров в первом столбце
        current_column = 1
        column2_y = param_y  # Высота для второго столбца
        
        for i, param in enumerate(params):
            # Если параметров много, переходим во второй столбец
            if i >= max_params_per_column and current_column == 1:
                current_column = 2
                column2_y = param_y  # Начинаем с верха для второго столбца
                column1_max_y = current_y  # Сохраняем максимальную высоту первого столбца
            
            # Определяем позицию X в зависимости от столбца
            if current_column == 2:
                param_x_current = column2_x
                max_param_width_current = window_w - column2_x - 30
                current_y = column2_y
            else:
                param_x_current = column1_x
                max_param_width_current = max_param_width
                column1_max_y = current_y  # Обновляем максимальную высоту первого столбца
            
            # Проверяем, не выходит ли текст за пределы окна
            text_width = font_small.size(param)[0]
            if text_width > max_param_width_current:
                # Если текст слишком длинный, разбиваем на несколько строк
                words = param.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font_small.size(test_line)[0] <= max_param_width_current:
                        current_line = test_line
                    else:
                        if current_line:
                            text = font_small.render(current_line, True, (220, 220, 220))
                            self.screen.blit(text, (param_x_current, current_y))
                            current_y += line_height
                            if current_column == 2:
                                column2_y = current_y
                            else:
                                column1_max_y = current_y
                        current_line = word
                if current_line:
                    text = font_small.render(current_line, True, (220, 220, 220))
                    self.screen.blit(text, (param_x_current, current_y))
                    current_y += line_height
                    if current_column == 2:
                        column2_y = current_y
                    else:
                        column1_max_y = current_y
            else:
                text = font_small.render(param, True, (220, 220, 220))
                self.screen.blit(text, (param_x_current, current_y))
                current_y += line_height
                if current_column == 2:
                    column2_y = current_y
                else:
                    column1_max_y = current_y
        
        # Поля для способностей и пассивок (внизу) - динамически позиционируем
        # Оставляем минимум 120 пикселей снизу, но ограничиваем максимальное смещение
        min_effects_space = 120
        # Если использовались два столбца, берем максимальную высоту обоих столбцов
        if current_column == 2:
            param_bottom = max(column1_max_y, column2_y) + 20
        else:
            param_bottom = column1_max_y + 20  # Отступ снизу после параметров
        max_effects_y = window_y + window_h - min_effects_space  # Максимальная позиция (не ниже 120px от низа)
        abilities_y = min(max_effects_y, param_bottom + 20)  # Берем минимум, чтобы не уходило слишком далеко
        pygame.draw.line(self.screen, (100, 80, 60), (window_x + 20, abilities_y), (window_x + window_w - 20, abilities_y), 2)
        font_label = pygame.font.Font(None, 26)
        label = font_label.render("Временные эффекты:", True, (200, 180, 140))
        self.screen.blit(label, (window_x + 20, abilities_y + 10))
        
        # Собираем все временные эффекты
        effects = []
        effects_y = abilities_y + 35
        line_height_effects = 20
        max_lines = 3  # Максимум 3 строки эффектов
        
        # Защита
        if hasattr(unit, '_defend_this_round') and getattr(unit, '_defend_this_round', False):
            effects.append(("В защите", (100, 180, 255)))
        
        # Благословение/Проклятие
        if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
            effects.append((f"Благословение ({unit.attack_buff_turns} ход.)", (80, 255, 80)))
        if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
            effects.append((f"Проклятие ({unit.attack_debuff_turns} ход.)", (255, 80, 80)))
        
        # Руны
        if hasattr(unit, 'rune_shield_turns') and getattr(unit, 'rune_shield_turns', 0) > 0:
            effects.append((f"Руна защиты ({unit.rune_shield_turns} ход.)", (80, 255, 120)))
        if hasattr(unit, 'rune_magic_turns') and getattr(unit, 'rune_magic_turns', 0) > 0:
            effects.append((f"Руна магии ({unit.rune_magic_turns} ход.)", (200, 150, 255)))
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            effects.append((f"Руна берсерка ({unit.rune_berserker_turns} ход.)", (255, 80, 80)))
        if hasattr(unit, 'rune_haste_turns') and getattr(unit, 'rune_haste_turns', 0) > 0:
            effects.append((f"Руна скорости ({unit.rune_haste_turns} ход.)", (120, 200, 255)))
        
        # Замедление/Ускорение
        if hasattr(unit, 'slow_turns') and getattr(unit, 'slow_turns', 0) > 0:
            effects.append((f"Замедление ({unit.slow_turns} ход.)", (255, 120, 120)))
        if hasattr(unit, 'haste_turns') and getattr(unit, 'haste_turns', 0) > 0:
            effects.append((f"Ускорение ({unit.haste_turns} ход.)", (120, 255, 120)))
        
        # Ослепление
        if hasattr(unit, 'blindness_turns') and getattr(unit, 'blindness_turns', 0) > 0:
            effects.append((f"Ослепление ({unit.blindness_turns} ход.)", (200, 200, 80)))
        
        # Молитва
        if hasattr(unit, 'prayer_turns') and getattr(unit, 'prayer_turns', 0) > 0:
            effects.append((f"Молитва ({unit.prayer_turns} ход.)", (255, 255, 200)))
        
        # Точность
        if hasattr(unit, 'accuracy_turns') and getattr(unit, 'accuracy_turns', 0) > 0:
            effects.append((f"Точность ({unit.accuracy_turns} ход.)", (255, 200, 100)))
        
        # Каменная кожа
        if hasattr(unit, 'stone_skin_turns') and getattr(unit, 'stone_skin_turns', 0) > 0:
            effects.append((f"Каменная кожа ({unit.stone_skin_turns} ход.)", (200, 200, 200)))
        
        # Огненный щит
        if hasattr(unit, 'fire_shield_turns') and getattr(unit, 'fire_shield_turns', 0) > 0:
            effects.append((f"Огненный щит ({unit.fire_shield_turns} ход.)", (255, 100, 50)))
        
        # Ледяной щит
        if hasattr(unit, 'ice_shield_turns') and getattr(unit, 'ice_shield_turns', 0) > 0:
            effects.append((f"Ледяной щит ({unit.ice_shield_turns} ход.)", (100, 200, 255)))
        
        # Контрудар
        if hasattr(unit, 'counterstrike_turns') and getattr(unit, 'counterstrike_turns', 0) > 0:
            effects.append((f"Контрудар ({unit.counterstrike_turns} ход.)", (255, 180, 100)))
        
        # Слабость
        if hasattr(unit, 'weakness_turns') and getattr(unit, 'weakness_turns', 0) > 0:
            effects.append((f"Слабость ({unit.weakness_turns} ход.)", (200, 100, 100)))
        
        # Забвение
        if hasattr(unit, 'forget_turns') and getattr(unit, 'forget_turns', 0) > 0:
            effects.append((f"Забвение ({unit.forget_turns} ход.)", (150, 150, 150)))
        
        # Отображаем эффекты
        if effects:
            for i, (effect_name, effect_color) in enumerate(effects[:max_lines]):
                effect_text = font_small.render(effect_name, True, effect_color)
                self.screen.blit(effect_text, (window_x + 20, effects_y + i * line_height_effects))
            if len(effects) > max_lines:
                more_text = font_small.render(f"... и еще {len(effects) - max_lines}", True, (150, 150, 150))
                self.screen.blit(more_text, (window_x + 20, effects_y + max_lines * line_height_effects))
        else:
            no_effects = font_small.render("Нет активных эффектов", True, (150, 150, 150))
            self.screen.blit(no_effects, (window_x + 20, effects_y))
        
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Отладочное логирование начала применения заклинания
            self.anim_logger.log("SPELL_CAST_START", f"Герой кастует {spell.name} ({spell.icon}) target_type={spell.target_type}")
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
                spell_name = getattr(spell, 'name', '')
                spell_icon = getattr(spell, 'icon', '')
                # Проверяем мгновенные заклинания (без анимации полета снаряда)
                instant_spells = [
                    'lightning', 'weakness', 'bless', 'curse', 'slow', 'haste',
                    'heal', 'dispel', 'stone_skin', 'ice_shield', 'fire_shield',
                    'counterstrike', 'rune_shield', 'rune_haste', 'raise_dead',
                    'resurrection', 'undead_heal', 'forget', 'earth_spikes', 'rune_wall'
                ]
                is_instant_spell = (spell_icon in instant_spells or 
                                  spell_name in ['Молния', 'Слабость', 'Благословение', 'Проклятие', 
                                                'Замедление', 'Ускорение', 'Лечение', 'Снятие чар'] or
                                  any(keyword in spell_icon.lower() for keyword in ['lightning', 'weakness', 'bless', 'curse']))
                
                # Отладочное логирование
                self.anim_logger.log("SPELL_CHECK", f"name='{spell_name}' icon='{spell_icon}' instant={is_instant_spell}")
                
                # Логируем анимацию заклинания
                self.anim_logger.log_spell_animation(spell_name, spell_icon, self.selected_unit, target, is_instant_spell)
                
                if spell_icon == 'firearrow':
                    self.anim_logger.log("FIREARROW_ANIMATION", f"Огненная стрела от {self.selected_unit.unit_type} к {target.unit_type}")
                    self.animate_firearrow(self.selected_unit, target)
                elif not is_instant_spell:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    # Воспроизводим звук выстрела магов
                    if self.magic_shot_sound:
                        self.magic_shot_sound.play()
                    self.anim_logger.log_projectile_animation("magic_bolt", 
                        (self.selected_unit.x, self.selected_unit.y), 
                        (target.x, target.y), color)
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                # Применяем заклинание (для Молнии и Слабости - мгновенно, без анимации)
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
            if self.selected_unit.can_move(x, y, self.units, self.barriers):
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
                # Проверяем расстояние для определения типа атаки
                distance = abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)
                is_melee = (distance == 1)
                damage_already_applied = False  # Флаг для отслеживания применения урона
                
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    # Лучники и дальнобойные юниты
                    if is_melee:
                        # Ближний бой для лучников - только ближний бой, без стрел
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = max(1, self.selected_unit.get_current_attack() // 2)  # Половина урона
                        # Запоминаем параметры для контратаки (даже для лучников в ближнем бою)
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                    else:
                        # Дальняя атака - стреляем стрелами/снарядами, контратаки нет
                        target_is_melee_unit = False  # Дальняя атака, контратаки нет
                        start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                        end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                        
                        # Проверяем, является ли атакующий героем
                        is_hero = isinstance(self.selected_unit, Hero)
                        hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                        
                        # Определяем тип снаряда в зависимости от юнита/героя
                        if is_hero and hero_class == 'archer':
                            # Герой-лучник: стреляет стрелами
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            pygame.time.delay(150)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
                        elif self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                            # Обычные лучники стреляют стрелами - воспроизводим звуки
                            # Звук натяжения лука
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            # Небольшая задержка для звука натяжения
                            pygame.time.delay(150)
                            # Звук выстрела - используем новые звуки выстрелов (случайный выбор)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            # Анимация полета стрелы
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            # Звук попадания
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
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
                            # Воспроизводим звук выстрела магов
                            if self.magic_shot_sound:
                                self.magic_shot_sound.play()
                            animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                        # Перерисовываем экран, чтобы убрать снаряд
                        self.draw()
                        pygame.display.flip()
                        # Для дальнобойной атаки проверяем руну магии с учетом множителя дальности
                        mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit, is_ranged=True, target_x=x, target_y=y)
                        if mixed_damage is not None:
                            # Для руны магии используем смешанный урон
                            damage = None  # Будет применен через mixed_damage
                        else:
                            # Обычный расчет урона для дальнобойных
                            damage = self.selected_unit.ranged_damage(x, y)
                        
                        # Применяем урон для дальнобойных атак
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            elif damage is not None:
                                clicked_unit.take_damage(damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
                else:
                    # Обычные ближние бойцы и герои-воины
                    # Проверяем героя-воина - у него особая анимация
                    is_hero = isinstance(self.selected_unit, Hero)
                    hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                    
                    if is_hero and hero_class == 'warrior':
                        # Герой-воин: телепортация к цели
                        damage = self.selected_unit.get_current_attack()
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Сохраняем здоровье до атаки для вычисления урона
                        health_before = clicked_unit.health
                        # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                        squad_count_before_warrior = getattr(clicked_unit, 'squad_count', 1)
                        
                        # Создаем callback для применения урона (ТОЛЬКО урон, без последствий)
                        def apply_warrior_damage():
                            nonlocal damage_already_applied
                            damage_already_applied = True
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                        
                        # Вычисляем позицию рядом с целью
                        dx = clicked_unit.x - self.selected_unit.x
                        dy = clicked_unit.y - self.selected_unit.y
                        # Позиция рядом с целью (смещение в направлении атакующего)
                        if abs(dx) > abs(dy):
                            attack_x = clicked_unit.x - (1 if dx > 0 else -1)
                            attack_y = clicked_unit.y
                        else:
                            attack_x = clicked_unit.x
                            attack_y = clicked_unit.y - (1 if dy > 0 else -1)
                        
                        # Запускаем анимацию телепортации
                        animate_warrior_teleport(self.screen, 
                                                (self.selected_unit.x * CELL_SIZE, self.selected_unit.y * CELL_SIZE),
                                                (attack_x * CELL_SIZE, attack_y * CELL_SIZE),
                                                self.selected_unit.image,
                                                redraw_callback=self.draw,
                                                attack_sound_callback=lambda: (random.choice(self.human_melee_sounds).play() if self.human_melee_sounds and hasattr(random, 'choice') else None) if self.selected_unit.team in ['human', 'elf', 'dwarf'] else (random.choice(self.monster_melee_sounds).play() if self.monster_melee_sounds and hasattr(random, 'choice') else None),
                                                damage_callback=apply_warrior_damage,
                                                hide_attacker_pos=(self.selected_unit.x, self.selected_unit.y))
                        
                        # Вычисляем нанесенный урон
                        actual_damage = health_before - clicked_unit.health
                        
                        # ПОСЛЕ анимации обрабатываем последствия
                        squad_count_after_warrior = getattr(clicked_unit, 'squad_count', 1)
                        units_lost_warrior = squad_count_before_warrior - squad_count_after_warrior
                        if clicked_unit.health <= 0:
                            self.kill_unit(clicked_unit)
                            self.animate_queue_fade(clicked_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", уничтожено {units_lost_warrior} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", потеряно {units_lost_warrior} юнитов из отряда ({squad_count_after_warrior}/{squad_count_before_warrior})"
                            self.add_event(event_msg)
                            # Контратака происходит ПОСЛЕ анимации
                            self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки для героя-воина и переходим к следующему ходу
                        self.selected_unit.has_attacked = True
                        self.next_turn()
                        return
                    else:
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = self.selected_unit.get_current_attack()
                        # Запоминаем параметры для контратаки
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Применяем урон для обычных ближних бойцов
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                                # Контратака происходит ПОСЛЕ нанесения урона
                                self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
    
    def draw_unit_tooltip(self, unit):
        """Отрисовка тултипа юнита при зажатии правой кнопки мыши"""
        from .units import Hero
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)
        
        # Собираем информацию о юните
        lines = []
        lines.append(f"{unit.unit_type.capitalize()}")
        lines.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
        
        # Для героев показываем те же параметры что в окне информации (кроме удачи и боевого духа)
        if isinstance(unit, Hero):
            # Базовые параметры
            base_attack = getattr(unit, 'base_attack', None)
            if base_attack is None:
                # Вычисляем базовую атаку в зависимости от класса
                if unit.hero_class == 'mage':
                    base_attack = 5 + unit.spell_power
                else:  # warrior или archer
                    base_attack = 5 + unit.attack
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            knowledge = getattr(unit, 'knowledge', 0)
            spell_power = getattr(unit, 'spell_power', 0)
            mana = getattr(unit, 'mana', 0)
            max_mana = getattr(unit, 'max_mana', 0)
            
            lines.append(f"Базовая атака: {base_attack}")
            lines.append(f"Атака: {attack}")
            lines.append(f"Защита: {defense}")
            lines.append(f"Знания: {knowledge}")
            lines.append(f"Сила магии: {spell_power}")
            lines.append(f"Мана: {mana}/{max_mana}")
        else:
            # Для обычных юнитов показываем стандартную информацию
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                lines.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    lines.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    lines.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            # Атака и защита
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    lines.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    lines.append(f"Атака (маг): {unit.magic_attack}")
                lines.append(f"Защита (физ): {unit.phys_defense}")
                lines.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    lines.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                lines.append(f"Атака: {getattr(unit, 'attack', 0)}")
                lines.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            lines.append(f"Скорость: {unit.speed}")
            lines.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                lines.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    lines.append(f"Дальность: {unit.attack_range}")
        
        # Вычисляем размеры тултипа
        max_width = 0
        for line in lines:
            if line:
                width = font_small.size(line)[0]
                max_width = max(max_width, width)
        
        padding = 10
        line_height = 22
        tooltip_w = max_width + padding * 2
        tooltip_h = len(lines) * line_height + padding * 2
        
        # Позиция тултипа (рядом с курсором, но не выходя за экран)
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        if tooltip_x + tooltip_w > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_w - 20
        if tooltip_y + tooltip_h > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_h - 20
        
        # Фон тултипа
        tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surface.fill((40, 40, 80, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 150), (0, 0, tooltip_w, tooltip_h), 2)
        
        # Текст
        y_offset = padding
        for i, line in enumerate(lines):
            if line:
                if i == 0:  # Заголовок
                    text = font_bold.render(line, True, (255, 255, 180))
                else:
                    text = font_small.render(line, True, (220, 220, 220))
                tooltip_surface.blit(text, (padding, y_offset))
                y_offset += line_height
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_unit_info_window(self, unit):
        """Отрисовка окна информации о юните (при двойном клике)"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна
        window_w, window_h = 600, 500
        window_x = (SCREEN_WIDTH - window_w) // 2
        window_y = (SCREEN_HEIGHT - window_h) // 2
        
        # Фон окна (деревянный стиль)
        window_surface = pygame.Surface((window_w, window_h))
        for y in range(window_h):
            gradient = (
                int(150 - y * 0.2),
                int(110 - y * 0.15),
                int(80 - y * 0.1)
            )
            pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
        
        self.screen.blit(window_surface, (window_x, window_y))
        
        # Рамка
        pygame.draw.rect(self.screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=16)
        inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_rect, 2, border_radius=14)
        
        # Крестик для закрытия
        close_size = 30
        close_x = window_x + window_w - close_size - 10
        close_y = window_y + 10
        self.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        pygame.draw.rect(self.screen, (180, 60, 60), self.unit_info_close_button_rect, border_radius=5)
        font_close = pygame.font.Font(None, 32)
        close_text = font_close.render("×", True, (255, 255, 255))
        self.screen.blit(close_text, (close_x + 8, close_y + 2))
        
        # Заголовок
        font_title = pygame.font.Font(None, 48)
        title = font_title.render(f"{unit.unit_type.capitalize()}", True, (255, 245, 220))
        title_shadow = font_title.render(f"{unit.unit_type.capitalize()}", True, (60, 50, 40))
        title_x = window_x + (window_w - title.get_width()) // 2
        self.screen.blit(title_shadow, (title_x + 2, window_y + 20))
        self.screen.blit(title, (title_x, window_y + 18))
        
        # Изображение юнита (слева вверху)
        img_size = 120
        img_x = window_x + 30
        img_y = window_y + 80
        if hasattr(unit, 'image') and unit.image:
            img_scaled = pygame.transform.scale(unit.image, (img_size, img_size))
            self.screen.blit(img_scaled, (img_x, img_y))
        
        # Параметры (справа от изображения)
        font_small = pygame.font.Font(None, 24)
        param_x = img_x + img_size + 30
        param_y = window_y + 80
        line_height = 24  # Уменьшаем высоту строки для более компактного отображения
        max_param_width = window_w - param_x - 30  # Максимальная ширина для параметров
        
        # Проверяем, является ли юнит героем
        from .units import Hero
        is_hero = isinstance(unit, Hero)
        
        if is_hero:
            # Для героя показываем только параметры героя
            # Вычисляем базовую атаку в зависимости от класса
            if unit.hero_class == 'mage':
                base_attack = 5 + unit.spell_power
            else:  # warrior или archer
                base_attack = 5 + unit.attack
            
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            params.append(f"Базовая атака: {base_attack}")
            params.append(f"Атака: {unit.attack}")
            params.append(f"Защита: {unit.defense}")
            params.append(f"Сила магии: {unit.spell_power}")
            params.append(f"Знания: {unit.knowledge}")
            params.append(f"Мана: {unit.mana}/{unit.max_mana}")
            params.append(f"Удача: {unit.luck:+d} ({abs(unit.luck) * 5}% шанс двойного урона)")
            params.append(f"Боевой дух: {unit.combat_spirit:+d} ({abs(unit.combat_spirit) * 3}% шанс доп. хода)")
        else:
            # Для обычного юнита показываем параметры юнита
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                params.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    params.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    params.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    params.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    params.append(f"Атака (маг): {unit.magic_attack}")
                params.append(f"Защита (физ): {unit.phys_defense}")
                params.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    params.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                params.append(f"Атака: {getattr(unit, 'attack', 0)}")
                params.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            params.append(f"Скорость: {unit.speed}")
            params.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                params.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    params.append(f"Дальность: {unit.attack_range}")
            # Удача показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'luck'):
                luck = getattr(unit, 'luck', 0)
                params.append(f"Удача: {luck:+d} ({abs(luck) * 5}% шанс двойного урона)")
            # Боевой дух показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'combat_spirit'):
                combat_spirit = getattr(unit, 'combat_spirit', 0)
                params.append(f"Боевой дух: {combat_spirit:+d} ({abs(combat_spirit) * 3}% шанс доп. хода)")
            # Мораль показывается только в окне информации (не в тултипе), только для юнитов
            if hasattr(unit, 'morale') and not isinstance(unit, Hero):
                morale = getattr(unit, 'morale', 'good')
                morale_names = {
                    'excellent': 'Отличная',
                    'good': 'Хорошая',
                    'neutral': 'Нейтральная',
                    'bad': 'Плохая',
                    'awful': 'Ужасная'
                }
                morale_name = morale_names.get(morale, morale)
                params.append(f"Мораль: {morale_name}")
        
        # Отображаем параметры с переносом во второй столбец при необходимости
        current_y = param_y
        column1_x = param_x
        column1_max_y = param_y  # Максимальная высота первого столбца
        column2_x = param_x + max_param_width // 2 + 20  # Второй столбец правее
        max_params_per_column = 12  # Максимальное количество параметров в первом столбце
        current_column = 1
        column2_y = param_y  # Высота для второго столбца
        
        for i, param in enumerate(params):
            # Если параметров много, переходим во второй столбец
            if i >= max_params_per_column and current_column == 1:
                current_column = 2
                column2_y = param_y  # Начинаем с верха для второго столбца
                column1_max_y = current_y  # Сохраняем максимальную высоту первого столбца
            
            # Определяем позицию X в зависимости от столбца
            if current_column == 2:
                param_x_current = column2_x
                max_param_width_current = window_w - column2_x - 30
                current_y = column2_y
            else:
                param_x_current = column1_x
                max_param_width_current = max_param_width
                column1_max_y = current_y  # Обновляем максимальную высоту первого столбца
            
            # Проверяем, не выходит ли текст за пределы окна
            text_width = font_small.size(param)[0]
            if text_width > max_param_width_current:
                # Если текст слишком длинный, разбиваем на несколько строк
                words = param.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font_small.size(test_line)[0] <= max_param_width_current:
                        current_line = test_line
                    else:
                        if current_line:
                            text = font_small.render(current_line, True, (220, 220, 220))
                            self.screen.blit(text, (param_x_current, current_y))
                            current_y += line_height
                            if current_column == 2:
                                column2_y = current_y
                            else:
                                column1_max_y = current_y
                        current_line = word
                if current_line:
                    text = font_small.render(current_line, True, (220, 220, 220))
                    self.screen.blit(text, (param_x_current, current_y))
                    current_y += line_height
                    if current_column == 2:
                        column2_y = current_y
                    else:
                        column1_max_y = current_y
            else:
                text = font_small.render(param, True, (220, 220, 220))
                self.screen.blit(text, (param_x_current, current_y))
                current_y += line_height
                if current_column == 2:
                    column2_y = current_y
                else:
                    column1_max_y = current_y
        
        # Поля для способностей и пассивок (внизу) - динамически позиционируем
        # Оставляем минимум 120 пикселей снизу, но ограничиваем максимальное смещение
        min_effects_space = 120
        # Если использовались два столбца, берем максимальную высоту обоих столбцов
        if current_column == 2:
            param_bottom = max(column1_max_y, column2_y) + 20
        else:
            param_bottom = column1_max_y + 20  # Отступ снизу после параметров
        max_effects_y = window_y + window_h - min_effects_space  # Максимальная позиция (не ниже 120px от низа)
        abilities_y = min(max_effects_y, param_bottom + 20)  # Берем минимум, чтобы не уходило слишком далеко
        pygame.draw.line(self.screen, (100, 80, 60), (window_x + 20, abilities_y), (window_x + window_w - 20, abilities_y), 2)
        font_label = pygame.font.Font(None, 26)
        label = font_label.render("Временные эффекты:", True, (200, 180, 140))
        self.screen.blit(label, (window_x + 20, abilities_y + 10))
        
        # Собираем все временные эффекты
        effects = []
        effects_y = abilities_y + 35
        line_height_effects = 20
        max_lines = 3  # Максимум 3 строки эффектов
        
        # Защита
        if hasattr(unit, '_defend_this_round') and getattr(unit, '_defend_this_round', False):
            effects.append(("В защите", (100, 180, 255)))
        
        # Благословение/Проклятие
        if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
            effects.append((f"Благословение ({unit.attack_buff_turns} ход.)", (80, 255, 80)))
        if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
            effects.append((f"Проклятие ({unit.attack_debuff_turns} ход.)", (255, 80, 80)))
        
        # Руны
        if hasattr(unit, 'rune_shield_turns') and getattr(unit, 'rune_shield_turns', 0) > 0:
            effects.append((f"Руна защиты ({unit.rune_shield_turns} ход.)", (80, 255, 120)))
        if hasattr(unit, 'rune_magic_turns') and getattr(unit, 'rune_magic_turns', 0) > 0:
            effects.append((f"Руна магии ({unit.rune_magic_turns} ход.)", (200, 150, 255)))
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            effects.append((f"Руна берсерка ({unit.rune_berserker_turns} ход.)", (255, 80, 80)))
        if hasattr(unit, 'rune_haste_turns') and getattr(unit, 'rune_haste_turns', 0) > 0:
            effects.append((f"Руна скорости ({unit.rune_haste_turns} ход.)", (120, 200, 255)))
        
        # Замедление/Ускорение
        if hasattr(unit, 'slow_turns') and getattr(unit, 'slow_turns', 0) > 0:
            effects.append((f"Замедление ({unit.slow_turns} ход.)", (255, 120, 120)))
        if hasattr(unit, 'haste_turns') and getattr(unit, 'haste_turns', 0) > 0:
            effects.append((f"Ускорение ({unit.haste_turns} ход.)", (120, 255, 120)))
        
        # Ослепление
        if hasattr(unit, 'blindness_turns') and getattr(unit, 'blindness_turns', 0) > 0:
            effects.append((f"Ослепление ({unit.blindness_turns} ход.)", (200, 200, 80)))
        
        # Молитва
        if hasattr(unit, 'prayer_turns') and getattr(unit, 'prayer_turns', 0) > 0:
            effects.append((f"Молитва ({unit.prayer_turns} ход.)", (255, 255, 200)))
        
        # Точность
        if hasattr(unit, 'accuracy_turns') and getattr(unit, 'accuracy_turns', 0) > 0:
            effects.append((f"Точность ({unit.accuracy_turns} ход.)", (255, 200, 100)))
        
        # Каменная кожа
        if hasattr(unit, 'stone_skin_turns') and getattr(unit, 'stone_skin_turns', 0) > 0:
            effects.append((f"Каменная кожа ({unit.stone_skin_turns} ход.)", (200, 200, 200)))
        
        # Огненный щит
        if hasattr(unit, 'fire_shield_turns') and getattr(unit, 'fire_shield_turns', 0) > 0:
            effects.append((f"Огненный щит ({unit.fire_shield_turns} ход.)", (255, 100, 50)))
        
        # Ледяной щит
        if hasattr(unit, 'ice_shield_turns') and getattr(unit, 'ice_shield_turns', 0) > 0:
            effects.append((f"Ледяной щит ({unit.ice_shield_turns} ход.)", (100, 200, 255)))
        
        # Контрудар
        if hasattr(unit, 'counterstrike_turns') and getattr(unit, 'counterstrike_turns', 0) > 0:
            effects.append((f"Контрудар ({unit.counterstrike_turns} ход.)", (255, 180, 100)))
        
        # Слабость
        if hasattr(unit, 'weakness_turns') and getattr(unit, 'weakness_turns', 0) > 0:
            effects.append((f"Слабость ({unit.weakness_turns} ход.)", (200, 100, 100)))
        
        # Забвение
        if hasattr(unit, 'forget_turns') and getattr(unit, 'forget_turns', 0) > 0:
            effects.append((f"Забвение ({unit.forget_turns} ход.)", (150, 150, 150)))
        
        # Отображаем эффекты
        if effects:
            for i, (effect_name, effect_color) in enumerate(effects[:max_lines]):
                effect_text = font_small.render(effect_name, True, effect_color)
                self.screen.blit(effect_text, (window_x + 20, effects_y + i * line_height_effects))
            if len(effects) > max_lines:
                more_text = font_small.render(f"... и еще {len(effects) - max_lines}", True, (150, 150, 150))
                self.screen.blit(more_text, (window_x + 20, effects_y + max_lines * line_height_effects))
        else:
            no_effects = font_small.render("Нет активных эффектов", True, (150, 150, 150))
            self.screen.blit(no_effects, (window_x + 20, effects_y))
        
        # --- Только после обработки интерфейса ---
        if not self.selected_unit or self.selected_unit.has_attacked:
            return
        
        # Если герой выбрал заклинание - не обрабатываем обычные атаки и перемещения
        if isinstance(self.selected_unit, Hero) and self.selected_unit.selected_spell is not None:
            # Обработка применения заклинания (вся логика ниже)
            x = pos[0] // CELL_SIZE
            y = pos[1] // CELL_SIZE
            spell = self.selected_unit.spells[self.selected_unit.selected_spell]
            # Отладочное логирование начала применения заклинания
            self.anim_logger.log("SPELL_CAST_START", f"Герой кастует {spell.name} ({spell.icon}) target_type={spell.target_type}")
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
                spell_name = getattr(spell, 'name', '')
                spell_icon = getattr(spell, 'icon', '')
                # Проверяем мгновенные заклинания (без анимации полета снаряда)
                instant_spells = [
                    'lightning', 'weakness', 'bless', 'curse', 'slow', 'haste',
                    'heal', 'dispel', 'stone_skin', 'ice_shield', 'fire_shield',
                    'counterstrike', 'rune_shield', 'rune_haste', 'raise_dead',
                    'resurrection', 'undead_heal', 'forget', 'earth_spikes', 'rune_wall'
                ]
                is_instant_spell = (spell_icon in instant_spells or 
                                  spell_name in ['Молния', 'Слабость', 'Благословение', 'Проклятие', 
                                                'Замедление', 'Ускорение', 'Лечение', 'Снятие чар'] or
                                  any(keyword in spell_icon.lower() for keyword in ['lightning', 'weakness', 'bless', 'curse']))
                
                # Отладочное логирование
                self.anim_logger.log("SPELL_CHECK", f"name='{spell_name}' icon='{spell_icon}' instant={is_instant_spell}")
                
                # Логируем анимацию заклинания
                self.anim_logger.log_spell_animation(spell_name, spell_icon, self.selected_unit, target, is_instant_spell)
                
                if spell_icon == 'firearrow':
                    self.anim_logger.log("FIREARROW_ANIMATION", f"Огненная стрела от {self.selected_unit.unit_type} к {target.unit_type}")
                    self.animate_firearrow(self.selected_unit, target)
                elif not is_instant_spell:
                    # Маги и герои стреляют магическими снарядами с разными цветами
                    if self.selected_unit.unit_type == 'succubus':
                        color = (255, 80, 120)  # красный
                    elif self.selected_unit.unit_type == 'gog':
                        color = (255, 120, 40)  # оранжевый
                    elif self.selected_unit.unit_type == 'lich':
                        color = (80, 255, 80)   # зеленый
                    else:
                        color = (120, 180, 255)  # синий для остальных
                    # Воспроизводим звук выстрела магов
                    if self.magic_shot_sound:
                        self.magic_shot_sound.play()
                    self.anim_logger.log_projectile_animation("magic_bolt", 
                        (self.selected_unit.x, self.selected_unit.y), 
                        (target.x, target.y), color)
                    animate_magic_fly(self.screen, (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE//2),
                                     (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2),
                                     color=color, redraw_callback=self.draw)
                # Применяем заклинание (для Молнии и Слабости - мгновенно, без анимации)
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
            if self.selected_unit.can_move(x, y, self.units, self.barriers):
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
                # Проверяем расстояние для определения типа атаки
                distance = abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)
                is_melee = (distance == 1)
                damage_already_applied = False  # Флаг для отслеживания применения урона
                
                if hasattr(self.selected_unit, 'is_ranged') and self.selected_unit.is_ranged:
                    # Лучники и дальнобойные юниты
                    if is_melee:
                        # Ближний бой для лучников - только ближний бой, без стрел
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = max(1, self.selected_unit.get_current_attack() // 2)  # Половина урона
                        # Запоминаем параметры для контратаки (даже для лучников в ближнем бою)
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                    else:
                        # Дальняя атака - стреляем стрелами/снарядами, контратаки нет
                        target_is_melee_unit = False  # Дальняя атака, контратаки нет
                        start = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                        end = (clicked_unit.x * CELL_SIZE + CELL_SIZE//2, clicked_unit.y * CELL_SIZE + CELL_SIZE//2)
                        
                        # Проверяем, является ли атакующий героем
                        is_hero = isinstance(self.selected_unit, Hero)
                        hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                        
                        # Определяем тип снаряда в зависимости от юнита/героя
                        if is_hero and hero_class == 'archer':
                            # Герой-лучник: стреляет стрелами
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            pygame.time.delay(150)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
                        elif self.selected_unit.unit_type in ['crossbowman', 'elf_archer']:
                            # Обычные лучники стреляют стрелами - воспроизводим звуки
                            # Звук натяжения лука
                            if hasattr(self.selected_unit, 'bow_draw_sound') and self.selected_unit.bow_draw_sound:
                                self.selected_unit.bow_draw_sound.play()
                            # Небольшая задержка для звука натяжения
                            pygame.time.delay(150)
                            # Звук выстрела - используем новые звуки выстрелов (случайный выбор)
                            if self.shot_sound and self.shot2_sound:
                                shot_sound = random.choice([self.shot_sound, self.shot2_sound])
                                shot_sound.play()
                            elif self.shot_sound:
                                self.shot_sound.play()
                            elif self.shot2_sound:
                                self.shot2_sound.play()
                            elif hasattr(self.selected_unit, 'arrow_shot_sound') and self.selected_unit.arrow_shot_sound:
                                self.selected_unit.arrow_shot_sound.play()
                            # Анимация полета стрелы
                            animate_arrow_fly(self.screen, start, end, redraw_callback=self.draw)
                            # Звук попадания
                            if hasattr(self.selected_unit, 'arrow_hit_sound') and self.selected_unit.arrow_hit_sound:
                                self.selected_unit.arrow_hit_sound.play()
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
                            # Воспроизводим звук выстрела магов
                            if self.magic_shot_sound:
                                self.magic_shot_sound.play()
                            animate_magic_fly(self.screen, start, end, color=color, redraw_callback=self.draw)
                        # Перерисовываем экран, чтобы убрать снаряд
                        self.draw()
                        pygame.display.flip()
                        # Для дальнобойной атаки проверяем руну магии с учетом множителя дальности
                        mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit, is_ranged=True, target_x=x, target_y=y)
                        if mixed_damage is not None:
                            # Для руны магии используем смешанный урон
                            damage = None  # Будет применен через mixed_damage
                        else:
                            # Обычный расчет урона для дальнобойных
                            damage = self.selected_unit.ranged_damage(x, y)
                        
                        # Применяем урон для дальнобойных атак
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            elif damage is not None:
                                clicked_unit.take_damage(damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
                else:
                    # Обычные ближние бойцы и герои-воины
                    # Проверяем героя-воина - у него особая анимация
                    is_hero = isinstance(self.selected_unit, Hero)
                    hero_class = getattr(self.selected_unit, 'hero_class', None) if is_hero else None
                    
                    if is_hero and hero_class == 'warrior':
                        # Герой-воин: телепортация к цели
                        damage = self.selected_unit.get_current_attack()
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Сохраняем здоровье до атаки для вычисления урона
                        health_before = clicked_unit.health
                        # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                        squad_count_before_warrior = getattr(clicked_unit, 'squad_count', 1)
                        
                        # Создаем callback для применения урона (ТОЛЬКО урон, без последствий)
                        def apply_warrior_damage():
                            nonlocal damage_already_applied
                            damage_already_applied = True
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                        
                        # Вычисляем позицию рядом с целью
                        dx = clicked_unit.x - self.selected_unit.x
                        dy = clicked_unit.y - self.selected_unit.y
                        # Позиция рядом с целью (смещение в направлении атакующего)
                        if abs(dx) > abs(dy):
                            attack_x = clicked_unit.x - (1 if dx > 0 else -1)
                            attack_y = clicked_unit.y
                        else:
                            attack_x = clicked_unit.x
                            attack_y = clicked_unit.y - (1 if dy > 0 else -1)
                        
                        # Запускаем анимацию телепортации
                        animate_warrior_teleport(self.screen, 
                                                (self.selected_unit.x * CELL_SIZE, self.selected_unit.y * CELL_SIZE),
                                                (attack_x * CELL_SIZE, attack_y * CELL_SIZE),
                                                self.selected_unit.image,
                                                redraw_callback=self.draw,
                                                attack_sound_callback=lambda: (random.choice(self.human_melee_sounds).play() if self.human_melee_sounds and hasattr(random, 'choice') else None) if self.selected_unit.team in ['human', 'elf', 'dwarf'] else (random.choice(self.monster_melee_sounds).play() if self.monster_melee_sounds and hasattr(random, 'choice') else None),
                                                damage_callback=apply_warrior_damage,
                                                hide_attacker_pos=(self.selected_unit.x, self.selected_unit.y))
                        
                        # Вычисляем нанесенный урон
                        actual_damage = health_before - clicked_unit.health
                        
                        # ПОСЛЕ анимации обрабатываем последствия
                        squad_count_after_warrior = getattr(clicked_unit, 'squad_count', 1)
                        units_lost_warrior = squad_count_before_warrior - squad_count_after_warrior
                        if clicked_unit.health <= 0:
                            self.kill_unit(clicked_unit)
                            self.animate_queue_fade(clicked_unit)
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", уничтожено {units_lost_warrior} юнитов из отряда"
                            self.add_event(event_msg)
                            self.check_game_over()
                        else:
                            event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                            if units_lost_warrior > 0:
                                event_msg += f", потеряно {units_lost_warrior} юнитов из отряда ({squad_count_after_warrior}/{squad_count_before_warrior})"
                            self.add_event(event_msg)
                            # Контратака происходит ПОСЛЕ анимации
                            self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки для героя-воина и переходим к следующему ходу
                        self.selected_unit.has_attacked = True
                        self.next_turn()
                        return
                    else:
                        # Звук ближнего боя в зависимости от типа юнита
                        if self.selected_unit.team in ['human', 'elf']:
                            if self.human_melee_sounds:
                                random.choice(self.human_melee_sounds).play()
                        else:
                            if self.monster_melee_sounds:
                                random.choice(self.monster_melee_sounds).play()
                        damage = self.selected_unit.get_current_attack()
                        # Запоминаем параметры для контратаки
                        target_is_melee_unit = not (hasattr(clicked_unit, 'is_ranged') and clicked_unit.is_ranged)
                        
                        # Применяем урон для обычных ближних бойцов
                        if not damage_already_applied:
                            # Сохраняем здоровье до атаки для вычисления урона
                            health_before = clicked_unit.health
                            # Сохраняем squad_count ДО нанесения урона (для отслеживания потерь)
                            squad_count_before = getattr(clicked_unit, 'squad_count', 1)
                            
                            # Проверяем руну магии для смешанного урона
                            mixed_damage = self.calculate_damage_with_rune_magic(self.selected_unit, clicked_unit)
                            if mixed_damage is not None:
                                # Применяем физический и магический урон отдельно
                                phys_dmg, magic_dmg = mixed_damage
                                unit_died = clicked_unit.take_damage(phys_dmg, attack_type='physical')
                                if not unit_died and magic_dmg > 0:
                                    unit_died = clicked_unit.take_damage(magic_dmg, attack_type='magical')
                            else:
                                # Применяем удачу к обычному урону (шанс двойного урона = luck * 5%)
                                luck = getattr(self.selected_unit, 'luck', 0)
                                final_damage = damage
                                if luck > 0:
                                    luck_chance = luck * 5  # Шанс в процентах
                                    if random.randint(1, 100) <= luck_chance:
                                        final_damage = damage * 2
                                        self.add_event(f"Удача! {self.selected_unit.unit_type.capitalize()} наносит двойной урон!")
                                        # Анимация подковы над атакующим юнитом
                                        attacker_pos = (self.selected_unit.x * CELL_SIZE + CELL_SIZE//2, self.selected_unit.y * CELL_SIZE + CELL_SIZE//2)
                                        animate_luck_horseshoe(self.screen, attacker_pos, redraw_callback=self.draw)
                                clicked_unit.take_damage(final_damage, attack_type=getattr(self.selected_unit, 'attack_type', 'physical'))
                            
                            # Вычисляем нанесенный урон
                            actual_damage = health_before - clicked_unit.health
                            
                            # Обрабатываем последствия
                            squad_count_after = getattr(clicked_unit, 'squad_count', 1)
                            units_lost = squad_count_before - squad_count_after
                            if clicked_unit.health <= 0:
                                self.kill_unit(clicked_unit)
                                self.animate_queue_fade(clicked_unit)
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} убил {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                                self.add_event(event_msg)
                                self.check_game_over()
                            else:
                                event_msg = f"{self.selected_unit.unit_type.capitalize()} атаковал {clicked_unit.unit_type} (урон: {actual_damage})"
                                if units_lost > 0:
                                    event_msg += f", потеряно {units_lost} юнитов из отряда ({squad_count_after}/{squad_count_before})"
                                self.add_event(event_msg)
                                # Контратака происходит ПОСЛЕ нанесения урона
                                self.perform_counterattack(self.selected_unit, clicked_unit, True, target_is_melee_unit)
                        
                        # Устанавливаем флаг атаки
                        self.selected_unit.has_attacked = True
                        
                        # Переходим к следующему ходу
                        self.next_turn()
                        return
    
    def draw_unit_tooltip(self, unit):
        """Отрисовка тултипа юнита при зажатии правой кнопки мыши"""
        from .units import Hero
        mouse_pos = pygame.mouse.get_pos()
        font_small = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 28)
        
        # Собираем информацию о юните
        lines = []
        lines.append(f"{unit.unit_type.capitalize()}")
        lines.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
        
        # Для героев показываем те же параметры что в окне информации (кроме удачи и боевого духа)
        if isinstance(unit, Hero):
            # Базовые параметры
            base_attack = getattr(unit, 'base_attack', None)
            if base_attack is None:
                # Вычисляем базовую атаку в зависимости от класса
                if unit.hero_class == 'mage':
                    base_attack = 5 + unit.spell_power
                else:  # warrior или archer
                    base_attack = 5 + unit.attack
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            knowledge = getattr(unit, 'knowledge', 0)
            spell_power = getattr(unit, 'spell_power', 0)
            mana = getattr(unit, 'mana', 0)
            max_mana = getattr(unit, 'max_mana', 0)
            
            lines.append(f"Базовая атака: {base_attack}")
            lines.append(f"Атака: {attack}")
            lines.append(f"Защита: {defense}")
            lines.append(f"Знания: {knowledge}")
            lines.append(f"Сила магии: {spell_power}")
            lines.append(f"Мана: {mana}/{max_mana}")
        else:
            # Для обычных юнитов показываем стандартную информацию
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                lines.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    lines.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    lines.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                lines.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            # Атака и защита
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    lines.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    lines.append(f"Атака (маг): {unit.magic_attack}")
                lines.append(f"Защита (физ): {unit.phys_defense}")
                lines.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    lines.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                lines.append(f"Атака: {getattr(unit, 'attack', 0)}")
                lines.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            lines.append(f"Скорость: {unit.speed}")
            lines.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                lines.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    lines.append(f"Дальность: {unit.attack_range}")
        
        # Вычисляем размеры тултипа
        max_width = 0
        for line in lines:
            if line:
                width = font_small.size(line)[0]
                max_width = max(max_width, width)
        
        padding = 10
        line_height = 22
        tooltip_w = max_width + padding * 2
        tooltip_h = len(lines) * line_height + padding * 2
        
        # Позиция тултипа (рядом с курсором, но не выходя за экран)
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        if tooltip_x + tooltip_w > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_w - 20
        if tooltip_y + tooltip_h > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_h - 20
        
        # Фон тултипа
        tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surface.fill((40, 40, 80, 240))
        pygame.draw.rect(tooltip_surface, (100, 100, 150), (0, 0, tooltip_w, tooltip_h), 2)
        
        # Текст
        y_offset = padding
        for i, line in enumerate(lines):
            if line:
                if i == 0:  # Заголовок
                    text = font_bold.render(line, True, (255, 255, 180))
                else:
                    text = font_small.render(line, True, (220, 220, 220))
                tooltip_surface.blit(text, (padding, y_offset))
                y_offset += line_height
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def draw_unit_info_window(self, unit):
        """Отрисовка окна информации о юните (при двойном клике)"""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна
        window_w, window_h = 600, 500
        window_x = (SCREEN_WIDTH - window_w) // 2
        window_y = (SCREEN_HEIGHT - window_h) // 2
        
        # Фон окна (деревянный стиль)
        window_surface = pygame.Surface((window_w, window_h))
        for y in range(window_h):
            gradient = (
                int(150 - y * 0.2),
                int(110 - y * 0.15),
                int(80 - y * 0.1)
            )
            pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
        
        self.screen.blit(window_surface, (window_x, window_y))
        
        # Рамка
        pygame.draw.rect(self.screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=16)
        inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
        pygame.draw.rect(self.screen, (170, 140, 110), inner_rect, 2, border_radius=14)
        
        # Крестик для закрытия
        close_size = 30
        close_x = window_x + window_w - close_size - 10
        close_y = window_y + 10
        self.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        pygame.draw.rect(self.screen, (180, 60, 60), self.unit_info_close_button_rect, border_radius=5)
        font_close = pygame.font.Font(None, 32)
        close_text = font_close.render("×", True, (255, 255, 255))
        self.screen.blit(close_text, (close_x + 8, close_y + 2))
        
        # Заголовок
        font_title = pygame.font.Font(None, 48)
        title = font_title.render(f"{unit.unit_type.capitalize()}", True, (255, 245, 220))
        title_shadow = font_title.render(f"{unit.unit_type.capitalize()}", True, (60, 50, 40))
        title_x = window_x + (window_w - title.get_width()) // 2
        self.screen.blit(title_shadow, (title_x + 2, window_y + 20))
        self.screen.blit(title, (title_x, window_y + 18))
        
        # Изображение юнита (слева вверху)
        img_size = 120
        img_x = window_x + 30
        img_y = window_y + 80
        if hasattr(unit, 'image') and unit.image:
            img_scaled = pygame.transform.scale(unit.image, (img_size, img_size))
            self.screen.blit(img_scaled, (img_x, img_y))
        
        # Параметры (справа от изображения)
        font_small = pygame.font.Font(None, 24)
        param_x = img_x + img_size + 30
        param_y = window_y + 80
        line_height = 24  # Уменьшаем высоту строки для более компактного отображения
        max_param_width = window_w - param_x - 30  # Максимальная ширина для параметров
        
        # Проверяем, является ли юнит героем
        from .units import Hero
        is_hero = isinstance(unit, Hero)
        
        if is_hero:
            # Для героя показываем только параметры героя
            # Вычисляем базовую атаку в зависимости от класса
            if unit.hero_class == 'mage':
                base_attack = 5 + unit.spell_power
            else:  # warrior или archer
                base_attack = 5 + unit.attack
            
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            params.append(f"Базовая атака: {base_attack}")
            params.append(f"Атака: {unit.attack}")
            params.append(f"Защита: {unit.defense}")
            params.append(f"Сила магии: {unit.spell_power}")
            params.append(f"Знания: {unit.knowledge}")
            params.append(f"Мана: {unit.mana}/{unit.max_mana}")
            params.append(f"Удача: {unit.luck:+d} ({abs(unit.luck) * 5}% шанс двойного урона)")
            params.append(f"Боевой дух: {unit.combat_spirit:+d} ({abs(unit.combat_spirit) * 3}% шанс доп. хода)")
        else:
            # Для обычного юнита показываем параметры юнита
            params = []
            params.append(f"Команда: {TEAM_LABELS.get(unit.team, unit.team)}")
            # Для отрядов показываем только ХП текущего юнита и размер отряда
            if hasattr(unit, 'squad_count') and hasattr(unit, 'unit_hp') and unit.unit_hp is not None and unit.squad_count > 1:
                current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                max_unit_hp = unit.unit_hp
                params.append(f"Здоровье: {int(current_unit_hp)}/{int(max_unit_hp)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            else:
                # Для одиночных юнитов показываем их ХП
                if hasattr(unit, 'unit_hp') and unit.unit_hp is not None:
                    current_unit_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
                    params.append(f"Здоровье: {int(current_unit_hp)}/{int(unit.unit_hp)}")
                else:
                    params.append(f"Здоровье: {int(unit.health)}/{int(unit.max_health)}")
                params.append(f"Отряд: {getattr(unit, 'squad_count', 1)}")
            
            if hasattr(unit, 'phys_attack') and hasattr(unit, 'magic_attack'):
                if unit.attack_type == 'physical':
                    params.append(f"Атака (физ): {unit.phys_attack}")
                else:
                    params.append(f"Атака (маг): {unit.magic_attack}")
                params.append(f"Защита (физ): {unit.phys_defense}")
                params.append(f"Защита (маг): {unit.magic_defense}")
                if hasattr(unit, 'magic_resist') and unit.magic_resist > 0:
                    params.append(f"Сопр. магии: {unit.magic_resist}%")
            else:
                params.append(f"Атака: {getattr(unit, 'attack', 0)}")
                params.append(f"Защита: {getattr(unit, 'defense', 0)}")
            
            params.append(f"Скорость: {unit.speed}")
            params.append(f"Инициатива: {unit.initiative}")
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                params.append("Тип: Дальнобойный")
                if hasattr(unit, 'attack_range'):
                    params.append(f"Дальность: {unit.attack_range}")
            # Удача показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'luck'):
                luck = getattr(unit, 'luck', 0)
                params.append(f"Удача: {luck:+d} ({abs(luck) * 5}% шанс двойного урона)")
            # Боевой дух показывается только в окне информации (не в тултипе)
            if hasattr(unit, 'combat_spirit'):
                combat_spirit = getattr(unit, 'combat_spirit', 0)
                params.append(f"Боевой дух: {combat_spirit:+d} ({abs(combat_spirit) * 3}% шанс доп. хода)")
            # Мораль показывается только в окне информации (не в тултипе), только для юнитов
            if hasattr(unit, 'morale') and not isinstance(unit, Hero):
                morale = getattr(unit, 'morale', 'good')
                morale_names = {
                    'excellent': 'Отличная',
                    'good': 'Хорошая',
                    'neutral': 'Нейтральная',
                    'bad': 'Плохая',
                    'awful': 'Ужасная'
                }
                morale_name = morale_names.get(morale, morale)
                params.append(f"Мораль: {morale_name}")
        
        # Отображаем параметры с переносом во второй столбец при необходимости
        current_y = param_y
        column1_x = param_x
        column1_max_y = param_y  # Максимальная высота первого столбца
        column2_x = param_x + max_param_width // 2 + 20  # Второй столбец правее
        max_params_per_column = 12  # Максимальное количество параметров в первом столбце
        current_column = 1
        column2_y = param_y  # Высота для второго столбца
        
        for i, param in enumerate(params):
            # Если параметров много, переходим во второй столбец
            if i >= max_params_per_column and current_column == 1:
                current_column = 2
                column2_y = param_y  # Начинаем с верха для второго столбца
                column1_max_y = current_y  # Сохраняем максимальную высоту первого столбца
            
            # Определяем позицию X в зависимости от столбца
            if current_column == 2:
                param_x_current = column2_x
                max_param_width_current = window_w - column2_x - 30
                current_y = column2_y
            else:
                param_x_current = column1_x
                max_param_width_current = max_param_width
                column1_max_y = current_y  # Обновляем максимальную высоту первого столбца
            
            # Проверяем, не выходит ли текст за пределы окна
            text_width = font_small.size(param)[0]
            if text_width > max_param_width_current:
                # Если текст слишком длинный, разбиваем на несколько строк
                words = param.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font_small.size(test_line)[0] <= max_param_width_current:
                        current_line = test_line
                    else:
                        if current_line:
                            text = font_small.render(current_line, True, (220, 220, 220))
                            self.screen.blit(text, (param_x_current, current_y))
                            current_y += line_height
                            if current_column == 2:
                                column2_y = current_y
                            else:
                                column1_max_y = current_y
                        current_line = word
                if current_line:
                    text = font_small.render(current_line, True, (220, 220, 220))
                    self.screen.blit(text, (param_x_current, current_y))
                    current_y += line_height
                    if current_column == 2:
                        column2_y = current_y
                    else:
                        column1_max_y = current_y
            else:
                text = font_small.render(param, True, (220, 220, 220))
                self.screen.blit(text, (param_x_current, current_y))
                current_y += line_height
                if current_column == 2:
                    column2_y = current_y
                else:
                    column1_max_y = current_y
        
        # Поля для способностей и пассивок (внизу) - динамически позиционируем
        # Оставляем минимум 120 пикселей снизу, но ограничиваем максимальное смещение
        min_effects_space = 120
        # Если использовались два столбца, берем максимальную высоту обоих столбцов
        if current_column == 2:
            param_bottom = max(column1_max_y, column2_y) + 20
        else:
            param_bottom = column1_max_y + 20  # Отступ снизу после параметров
        max_effects_y = window_y + window_h - min_effects_space  # Максимальная позиция (не ниже 120px от низа)
        abilities_y = min(max_effects_y, param_bottom + 20)  # Берем минимум, чтобы не уходило слишком далеко
        pygame.draw.line(self.screen, (100, 80, 60), (window_x + 20, abilities_y), (window_x + window_w - 20, abilities_y), 2)
        font_label = pygame.font.Font(None, 26)
        label = font_label.render("Временные эффекты:", True, (200, 180, 140))
        self.screen.blit(label, (window_x + 20, abilities_y + 10))
        
        # Собираем все временные эффекты
        effects = []
        effects_y = abilities_y + 35
        line_height_effects = 20
        max_lines = 3  # Максимум 3 строки эффектов
        
        # Защита
        if hasattr(unit, '_defend_this_round') and getattr(unit, '_defend_this_round', False):
            effects.append(("В защите", (100, 180, 255)))
        
        # Благословение/Проклятие
        if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
            effects.append((f"Благословение ({unit.attack_buff_turns} ход.)", (80, 255, 80)))
        if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
            effects.append((f"Проклятие ({unit.attack_debuff_turns} ход.)", (255, 80, 80)))
        
        # Руны
        if hasattr(unit, 'rune_shield_turns') and getattr(unit, 'rune_shield_turns', 0) > 0:
            effects.append((f"Руна защиты ({unit.rune_shield_turns} ход.)", (80, 255, 120)))
        if hasattr(unit, 'rune_magic_turns') and getattr(unit, 'rune_magic_turns', 0) > 0:
            effects.append((f"Руна магии ({unit.rune_magic_turns} ход.)", (200, 150, 255)))
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            effects.append((f"Руна берсерка ({unit.rune_berserker_turns} ход.)", (255, 80, 80)))
        if hasattr(unit, 'rune_haste_turns') and getattr(unit, 'rune_haste_turns', 0) > 0:
            effects.append((f"Руна скорости ({unit.rune_haste_turns} ход.)", (120, 200, 255)))
        
        # Замедление/Ускорение
        if hasattr(unit, 'slow_turns') and getattr(unit, 'slow_turns', 0) > 0:
            effects.append((f"Замедление ({unit.slow_turns} ход.)", (255, 120, 120)))
        if hasattr(unit, 'haste_turns') and getattr(unit, 'haste_turns', 0) > 0:
            effects.append((f"Ускорение ({unit.haste_turns} ход.)", (120, 255, 120)))
        
        # Ослепление
        if hasattr(unit, 'blindness_turns') and getattr(unit, 'blindness_turns', 0) > 0:
            effects.append((f"Ослепление ({unit.blindness_turns} ход.)", (200, 200, 80)))
        
        # Молитва
        if hasattr(unit, 'prayer_turns') and getattr(unit, 'prayer_turns', 0) > 0:
            effects.append((f"Молитва ({unit.prayer_turns} ход.)", (255, 255, 200)))
        
        # Точность
        if hasattr(unit, 'accuracy_turns') and getattr(unit, 'accuracy_turns', 0) > 0:
            effects.append((f"Точность ({unit.accuracy_turns} ход.)", (255, 200, 100)))
        
        # Каменная кожа
        if hasattr(unit, 'stone_skin_turns') and getattr(unit, 'stone_skin_turns', 0) > 0:
            effects.append((f"Каменная кожа ({unit.stone_skin_turns} ход.)", (200, 200, 200)))
        
        # Огненный щит
        if hasattr(unit, 'fire_shield_turns') and getattr(unit, 'fire_shield_turns', 0) > 0:
            effects.append((f"Огненный щит ({unit.fire_shield_turns} ход.)", (255, 100, 50)))
        
        # Ледяной щит
        if hasattr(unit, 'ice_shield_turns') and getattr(unit, 'ice_shield_turns', 0) > 0:
            effects.append((f"Ледяной щит ({unit.ice_shield_turns} ход.)", (100, 200, 255)))
        
        # Контрудар
        if hasattr(unit, 'counterstrike_turns') and getattr(unit, 'counterstrike_turns', 0) > 0:
            effects.append((f"Контрудар ({unit.counterstrike_turns} ход.)", (255, 180, 100)))
        
        # Слабость
        if hasattr(unit, 'weakness_turns') and getattr(unit, 'weakness_turns', 0) > 0:
            effects.append((f"Слабость ({unit.weakness_turns} ход.)", (200, 100, 100)))
        
        # Забвение
        if hasattr(unit, 'forget_turns') and getattr(unit, 'forget_turns', 0) > 0:
            effects.append((f"Забвение ({unit.forget_turns} ход.)", (150, 150, 150)))
        
        # Отображаем эффекты
        if effects:
            for i, (effect_name, effect_color) in enumerate(effects[:max_lines]):
                effect_text = font_small.render(effect_name, True, effect_color)
                self.screen.blit(effect_text, (window_x + 20, effects_y + i * line_height_effects))
            if len(effects) > max_lines:
                more_text = font_small.render(f"... и еще {len(effects) - max_lines}", True, (150, 150, 150))
                self.screen.blit(more_text, (window_x + 20, effects_y + max_lines * line_height_effects))
        else:
            no_effects = font_small.render("Нет активных эффектов", True, (150, 150, 150))
            self.screen.blit(no_effects, (window_x + 20, effects_y))
                
