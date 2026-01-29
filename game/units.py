import pygame
import time
from .spells import Spell
from .sound import load_sound
from .graphics import (
    load_image,
    load_crossbowman_texture,
    load_peasant_texture,
    load_spearman_texture,
    load_swordsman_texture,
    load_gryphon_texture,
    load_elf_archer_texture,
    load_elf_scout_texture,
    load_dryad_texture,
    load_druid_texture,
    load_pixie_texture,
    load_fairy_texture,
    load_ent_texture,
    load_unicorn_texture,
    load_skeleton_texture,
    load_zombie_texture,
    load_ghost_texture,
    load_vampire_texture,
    load_lich_texture,
    load_monk_texture,
    load_angel_texture,
    load_cavalryman_texture,
    load_greendragon_texture,
    load_imp_texture,
    load_gog_texture,
    load_demon_texture,
    load_cerberus_texture,
    load_succubus_texture,
    load_miner_texture,
    load_spearthrower_texture,
    load_bearrider_texture,
    load_runemage_texture,
    load_jarl_texture,
    load_scout_texture,
    load_beast_texture,
    load_minotaur_texture,
    load_witch_texture,
    load_lizardrider_texture,
    load_deathknight_texture,
    load_bonedragon_texture,
    load_reaper_texture,
    load_bloodpriestess_texture,
    load_devil_texture,
    load_hellhorse_texture,
    load_forgedragon_texture,
    load_mountainruler_texture,
    load_volkhv_texture,
    load_manticore_texture,
    load_reddragon_texture,
    load_beholder_texture,
)
from .config import CELL_SIZE, RED, GREEN, BLUE, PURPLE, LIGHT_BLUE, TOOLTIP_BG, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_WIDTH

TEAM_LABELS = {
    'human': 'Люди',
    'undead': 'Нежить',
    'elf': 'Эльфы',
    'demon': 'Демоны',
    'dwarf': 'Гномы',
    'shadow': 'Тени'
}

RESISTANCE_TYPES = ['physical', 'magic', 'poison', 'fire', 'cold', 'astral']

class AnimatedHumanoidMixin:
    """Общий функционал процедурной анимации для человекоподобных юнитов."""

    def _init_animation_system(
        self,
        texture_loader,
        animation_states,
        idle_cycle=('Idle', 'IdleBreath'),
        idle_switch_interval=650,
        idle_pause_duration=700,
        movement_cycle=None,
        turn_sequence_duration=120,
    ):
        self._texture_loader = texture_loader
        self._animation_states = animation_states
        self._frames = {state: texture_loader(state) for state in animation_states}
        self._idle_cycle = idle_cycle
        self._idle_switch_interval = idle_switch_interval
        self._idle_pause_duration = idle_pause_duration
        if movement_cycle is None:
            movement_cycle = ('Walk', 'WalkAlt')
        if isinstance(movement_cycle, str):
            movement_cycle = (movement_cycle,)
        self._movement_cycle = tuple(movement_cycle)
        self._turn_sequences = {}
        self._supports_turn_animation = False
        if 'TurnLeft' in animation_states and 'TurnRight' in animation_states:
            self._supports_turn_animation = True
            self._turn_sequences = {
                'to_left': [('TurnLeft', turn_sequence_duration)],
                'to_right': [('TurnRight', turn_sequence_duration)],
            }
        self.current_animation_state = idle_cycle[0] if idle_cycle else 'Idle'
        self.facing = -1 if self.x >= GRID_WIDTH // 2 else 1
        self._manual_face_timer = 0
        self._is_playing_sequence = False
        self._pending_sequence = []
        now = pygame.time.get_ticks()
        self._idle_pause_until = now
        self._last_idle_switch = now
        self._compose_image()

    def _compose_image(self):
        base = self._frames.get(self.current_animation_state) or self._frames.get('Idle')
        if base is None:
            return
        if self.facing >= 0:
            self.image = base
        else:
            self.image = pygame.transform.flip(base, True, False)

    def set_animation_state(self, state):
        if state not in self._animation_states:
            state = 'Idle'
        if state == self.current_animation_state:
            return
        self.current_animation_state = state
        now = pygame.time.get_ticks()
        if self._idle_cycle and state in self._idle_cycle:
            self._last_idle_switch = now
        else:
            self._idle_pause_until = now + self._idle_pause_duration
        self._compose_image()

    def set_facing_by_position(self, target_x):
        if target_x > self.x:
            new_facing = 1
        elif target_x < self.x:
            new_facing = -1
        else:
            new_facing = self.facing
        if new_facing != self.facing:
            previous_facing = self.facing
            self.facing = new_facing
            self._compose_image()
            self._manual_face_timer = 24
            self._play_turn_animation(previous_facing, new_facing)

    def face_unit(self, other_unit):
        if other_unit is not None:
            self.set_facing_by_position(other_unit.x)

    def _auto_face_nearest_enemy(self):
        if self._manual_face_timer > 0 or getattr(self, 'health', 0) <= 0 or self._is_playing_sequence:
            return
        game = getattr(self, 'game_ref', None)
        if not game:
            return
        enemies = [
            u for u in getattr(game, 'units', [])
            if u is not self and u.team != self.team and getattr(u, 'health', 0) > 0
        ]
        if not enemies:
            return
        nearest = min(enemies, key=lambda u: (u.x - self.x) ** 2 + (u.y - self.y) ** 2)
        self.set_facing_by_position(nearest.x)

    def draw(self, surface):
        now = pygame.time.get_ticks()
        if self._manual_face_timer > 0:
            self._manual_face_timer -= 1
        else:
            self._auto_face_nearest_enemy()
        if (
            not self._is_playing_sequence
            and self._idle_cycle
            and self.current_animation_state in self._idle_cycle
            and now >= self._idle_pause_until
            and now - self._last_idle_switch >= self._idle_switch_interval
        ):
            idx = self._idle_cycle.index(self.current_animation_state)
            next_idx = (idx + 1) % len(self._idle_cycle)
            self.current_animation_state = self._idle_cycle[next_idx]
            self._last_idle_switch = now
            self._compose_image()
        super().draw(surface)

    def _force_draw_and_delay(self, game, delay_ms):
        if game:
            game.draw()
            pygame.display.flip()
        pygame.time.delay(delay_ms)

    def _play_sequence(self, sequence, game, reset_to_idle=True):
        if not sequence:
            return
        self._is_playing_sequence = True
        for state, delay in sequence:
            self.set_animation_state(state)
            self._force_draw_and_delay(game, delay)
        if reset_to_idle:
            self.set_animation_state('Idle')
        self._is_playing_sequence = False

    def _play_turn_animation(self, previous_facing, new_facing):
        if not self._supports_turn_animation or self._is_playing_sequence:
            return
        game = getattr(self, 'game_ref', None)
        if not game:
            return
        if previous_facing == new_facing:
            return
        if new_facing > previous_facing:
            sequence = self._turn_sequences.get('to_right')
        else:
            sequence = self._turn_sequences.get('to_left')
        if not sequence:
            return
        self._play_sequence(sequence, game, reset_to_idle=False)
        if self._idle_cycle:
            self.set_animation_state(self._idle_cycle[0])
        else:
            self.set_animation_state('Idle')


class Unit:
    def __init__(self, x, y, team, unit_type):
        self.x = x
        self.y = y
        self.team = team
        self.unit_type = unit_type
        self.health = 100
        self.max_health = 100
        self.attack = 10  # Старый параметр (для совместимости)
        self.defense = 5  # Старый параметр (для совместимости)
        # Новая система атаки и защиты (будет переопределена после __init__)
        self.phys_attack = 10  # Физическая атака
        self.magic_attack = 0   # Магическая атака
        self.phys_defense = 5   # Физическая защита
        self.magic_defense = 5  # Магическая защита
        self.magic_resist = 0   # Сопротивление магии (%)
        self.attack_type = 'physical'  # 'physical' или 'magical'
        self._needs_stat_conversion = True  # Флаг для конвертации старых значений
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
        self._pixel_offset = [0, 0]
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
        self.squad_count = 1  # Количество юнитов в отряде (по умолчанию 1)
        self.luck = 0  # Удача (передается от героя, ограничение +6/-6)
        self.combat_spirit = 0  # Боевой дух (передается от героя)
        self.used_combat_spirit_this_round = False  # Флаг использования боевого духа в текущем раунде
        # Система здоровья отряда
        self.base_squad_count = 1  # Изначальное количество юнитов в отряде
        self.unit_hp = None  # HP одного юнита (будет установлено после инициализации)
        self.current_unit_hp = None  # HP последнего (текущего) юнита в отряде

        self.level = getattr(self, 'level', 1)
        self.base_level = getattr(self, 'base_level', self.level)

        default_leadership = getattr(self, 'leadership', 0)
        if not default_leadership:
            per_unit_hp = self.max_health // max(1, self.squad_count)
            default_leadership = max(1, int(per_unit_hp * max(1, self.squad_count)))
        self.leadership = default_leadership
        self.base_leadership = getattr(self, 'base_leadership', self.leadership)

        self.crit_multiplier = getattr(self, 'crit_multiplier', 2.0)
        self.crit_chance = getattr(self, 'crit_chance', None)
        self.base_crit_chance = getattr(self, 'base_crit_chance', self.crit_chance if self.crit_chance is not None else 0)

        self.damage_min = getattr(self, 'damage_min', None)
        self.damage_max = getattr(self, 'damage_max', None)
        self.base_damage_min = getattr(self, 'base_damage_min', self.damage_min)
        self.base_damage_max = getattr(self, 'base_damage_max', self.damage_max)

        existing_resistances = dict(getattr(self, 'resistances', {}) or {})
        for key in RESISTANCE_TYPES:
            existing_resistances.setdefault(key, 0)
        self.resistances = existing_resistances
        self.base_resistances = dict(getattr(self, 'base_resistances', self.resistances))

        self.traits = list(getattr(self, 'traits', []))
        self.talents = list(getattr(self, 'talents', []))
        
        # ВАЖНО: Конвертация должна вызываться ПОСЛЕ того, как подкласс установит свои значения
        # Поэтому мы НЕ вызываем её здесь, а будем вызывать в конце __init__ каждого подкласса
        # Но для удобства создадим helper-метод
    
    def convert_old_stats_to_new(self):
        """Автоматически конвертирует старые значения attack/defense в новую систему."""
        if not getattr(self, '_needs_stat_conversion', False):
            return
        
        # Определяем магических юнитов (атакуют магией)
        magical_units = [
            'lich', 'gog', 'succubus', 'runemage', 'witch',  # Маги
            'fairy', 'dryad', 'ghost'  # Магические существа
        ]
        
        # Устанавливаем тип атаки
        if self.unit_type in magical_units:
            self.attack_type = 'magical'
            self.magic_attack = self.attack
            self.phys_attack = 0
        else:
            self.attack_type = 'physical'
            self.phys_attack = self.attack
            self.magic_attack = 0
        
        # Устанавливаем защиты (базово равные)
        self.phys_defense = self.defense
        self.magic_defense = self.defense
        
        # Магические юниты имеют повышенное сопротивление магии
        if self.unit_type in magical_units:
            self.magic_resist = 25  # 25% сопротивление
        else:
            self.magic_resist = 0

        if not hasattr(self, 'base_phys_attack'):
            self.base_phys_attack = self.phys_attack
        if not hasattr(self, 'base_magic_attack'):
            self.base_magic_attack = self.magic_attack
        if not hasattr(self, 'base_phys_defense'):
            self.base_phys_defense = self.phys_defense
        if not hasattr(self, 'base_magic_defense'):
            self.base_magic_defense = self.magic_defense
        if not hasattr(self, 'base_magic_resist'):
            self.base_magic_resist = self.magic_resist

        if not hasattr(self, 'base_speed'):
            self.base_speed = self.speed
        if not hasattr(self, 'base_initiative'):
            self.base_initiative = self.initiative
        if not hasattr(self, 'base_health'):
            self.base_health = self.max_health

        attack_value = self.magic_attack if self.attack_type == 'magical' else self.phys_attack
        if self.damage_min is None or self.damage_max is None:
            spread = max(1, int(max(5, attack_value) * 0.25))
            base_min = max(1, attack_value - spread)
            base_max = max(base_min, attack_value + spread)
            self.damage_min = base_min
            self.damage_max = base_max
            self.base_damage_min = base_min
            self.base_damage_max = base_max
        else:
            if not hasattr(self, 'base_damage_min'):
                self.base_damage_min = self.damage_min
            if not hasattr(self, 'base_damage_max'):
                self.base_damage_max = self.damage_max

        if self.crit_chance is None:
            base_crit = max(0, min(100, 5 + getattr(self, 'luck', 0) * 5))
            self.crit_chance = base_crit
            self.base_crit_chance = base_crit
        else:
            if not hasattr(self, 'base_crit_chance'):
                self.base_crit_chance = self.crit_chance

        if not self.leadership:
            per_unit_hp = self.max_health // max(1, self.squad_count)
            calculated_leadership = max(1, int(max(1, self.squad_count) * max(1, per_unit_hp)))
            self.leadership = calculated_leadership
            self.base_leadership = calculated_leadership
        else:
            if not getattr(self, 'base_leadership', 0):
                self.base_leadership = self.leadership

        for key in RESISTANCE_TYPES:
            if key not in self.resistances:
                if key == 'physical':
                    value = min(75, int(self.phys_defense * 0.4))
                elif key == 'magic':
                    value = min(75, int(self.magic_defense * 0.4))
                elif key == 'astral':
                    value = self.magic_resist
                else:
                    value = 0
                self.resistances[key] = value
            self.base_resistances.setdefault(key, self.resistances[key])
        
        self._needs_stat_conversion = False

    def get_current_attack(self):
        # Возвращаем атаку в зависимости от типа атаки юнита
        if self.attack_type == 'magical':
            atk = self.magic_attack
        else:
            atk = self.phys_attack
        # Ослепление: снижаем урон на 35%
        if getattr(self, 'blindness_active', False):
            atk = int(atk * 0.65)
        
        # Гарантируем, что атака не отрицательна
        if atk < 0:
            atk = 0
        
        # Применяем баффы/дебаффы
        if self.attack_buff_turns > 0:
            atk = int(atk * 1.25)
        if self.attack_debuff_turns > 0:
            atk = int(atk * 0.75)
        
        # Гарантируем, что после баффов/дебаффов атака не отрицательна
        if atk < 0:
            atk = 0
        
        # Умножаем на количество юнитов в отряде
        squad_count = getattr(self, 'squad_count', 1)
        # Гарантируем, что squad_count не отрицателен
        if squad_count < 1:
            squad_count = 1
        atk = atk * squad_count
        
        # Финальная проверка - урон должен быть минимум 1
        return max(1, atk)
    
    def set_squad_count(self, count):
        """Устанавливает количество юнитов в отряде"""
        if self.unit_hp is None:
            # Первая установка - инициализируем систему здоровья отряда
            # unit_hp - это HP одного юнита (сохраняем текущее max_health как HP одного юнита)
            self.unit_hp = self.max_health
            self.current_unit_hp = self.max_health
            self.base_squad_count = count
        
        self.squad_count = count
        # Обновляем общее здоровье отряда
        # health = (squad_count - 1) * unit_hp + current_unit_hp
        if count > 0:
            self.current_unit_hp = self.unit_hp  # Все юниты здоровы при создании
            self.health = (count - 1) * self.unit_hp + self.current_unit_hp
            self.max_health = self.base_squad_count * self.unit_hp
    
    def get_defense_against(self, attack_type):
        """Возвращает защиту против определенного типа атаки."""
        if attack_type == 'magical':
            return self.magic_defense
        else:
            return self.phys_defense

    def apply_attack_buff(self, turns=2):
        self.attack_buff_turns = turns
        self.fade_buff = 1.0

    def apply_attack_debuff(self, turns=2):
        self.attack_debuff_turns = turns
        self.fade_debuff = 1.0

    def draw(self, surface):
        # Рисуем текстуру юнита сначала
        offset_x, offset_y = self._pixel_offset if hasattr(self, '_pixel_offset') else (0, 0)
        draw_x = self.x * CELL_SIZE + offset_x
        draw_y = self.y * CELL_SIZE + offset_y
        surface.blit(self.image, (draw_x, draw_y))
        # Если юнит под берсерком - накладываем красный оттенок
        if getattr(self, 'rune_berserker_active', False):
            red_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            red_overlay.fill((255, 100, 100, 120))  # Красный полупрозрачный слой
            surface.blit(red_overlay, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        # Полоска здоровья поверх текстуры юнита
        # Для отрядов показываем HP текущего юнита, для одиночных - общее
        if hasattr(self, 'squad_count') and hasattr(self, 'unit_hp') and self.unit_hp is not None and self.squad_count > 1:
            current_unit_hp = getattr(self, 'current_unit_hp', self.unit_hp)
            max_unit_hp = self.unit_hp
            health_ratio = 0 if max_unit_hp <= 0 else max(0.0, min(1.0, current_unit_hp / max_unit_hp))
        else:
            health_ratio = 0 if self.max_health <= 0 else max(0.0, min(1.0, self.health / self.max_health))
        back_rect = (draw_x, draw_y - 6, CELL_SIZE, 5)
        value_rect = (draw_x, draw_y - 6, int(CELL_SIZE * health_ratio), 5)
        pygame.draw.rect(surface, RED, back_rect)
        pygame.draw.rect(surface, GREEN, value_rect)
        # Отображение количества юнитов в отряде (если больше 1)
        squad_count = getattr(self, 'squad_count', 1)
        if squad_count > 1 and not isinstance(self, Hero):
            # Если юнит под берсерком - всегда красный для всех
            if getattr(self, 'rune_berserker_active', False):
                bg_color = (200, 0, 0, 220)  # Красный для берсерка
            else:
                # Определяем цвет по текущему ходу: синий для своего хода, красный для вражеского
                is_current_turn = False
                if hasattr(self, 'game_ref') and self.game_ref:
                    # Проверяем, чей сейчас ход (selected_unit)
                    if hasattr(self.game_ref, 'selected_unit') and self.game_ref.selected_unit:
                        is_current_turn = (self.team == self.game_ref.selected_unit.team)
                
                if is_current_turn:
                    bg_color = (0, 100, 200, 220)  # Синий для своего хода
                else:
                    bg_color = (200, 0, 0, 220)  # Красный для вражеского хода
            
            # Уменьшенный размер экранчика
            font = pygame.font.Font(None, 16)
            count_text = font.render(str(squad_count), True, (255, 255, 255))
            bg_width = max(count_text.get_width() + 4, 18)
            bg_height = count_text.get_height() + 2
            count_bg = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            count_bg.fill(bg_color)
            # Позиция: снизу посередине
            x_pos = self.x * CELL_SIZE + (CELL_SIZE - bg_width) // 2
            y_pos = self.y * CELL_SIZE + CELL_SIZE - bg_height - 2
            surface.blit(count_bg, (x_pos, y_pos))
            # Текст по центру
            text_x = x_pos + (bg_width - count_text.get_width()) // 2
            text_y = y_pos + (bg_height - count_text.get_height()) // 2
            surface.blit(count_text, (text_x, text_y))
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
        # Найти героя своей команды для бонуса (динамические значения берутся из текущих полей юнита)
        hero = None
        if hasattr(self, 'game_ref') and self.game_ref:
            if hasattr(self.game_ref, 'hero1') and self.team == self.game_ref.hero1.team:
                hero = self.game_ref.hero1
            elif hasattr(self.game_ref, 'hero2') and self.team == self.game_ref.hero2.team:
                hero = self.game_ref.hero2
        atk_bonus = hero.attack if hero else 0
        def_bonus = hero.defense if hero else 0
        base_atk = max(0, (self.attack - atk_bonus) if atk_bonus else self.attack)
        base_def = max(0, (self.base_defense - def_bonus) if def_bonus else self.base_defense)
        base_atk_with_bonus = base_atk + atk_bonus
        base_def_with_bonus = base_def + def_bonus
        # Текущая атака/защита: динамически из текущих полей
        current_atk = self.get_current_attack()
        current_def = self.defense
        if self.attack_buff_turns > 0:
            current_atk = int(current_atk * 1.25)
        if self.attack_debuff_turns > 0:
            current_atk = int(current_atk * 0.75)
        # Руна защиты теперь влияет на обе защиты напрямую, не на общую
        # Учитываем каменную кожу в текущей защите
        if hasattr(self, 'stone_skin_turns') and getattr(self, 'stone_skin_turns', 0) > 0:
            current_def += getattr(self, 'stone_skin_bonus', 0)
        # Определяем тип атаки для отображения
        attack_type_text = "Физ." if self.attack_type == 'physical' else "Маг."
        # Для отрядов показываем только размер отряда и HP текущего юнита
        if hasattr(self, 'squad_count') and hasattr(self, 'unit_hp') and self.unit_hp is not None:
            current_unit_hp = getattr(self, 'current_unit_hp', self.unit_hp)
            max_unit_hp = self.unit_hp
            base_squad_count = getattr(self, 'base_squad_count', self.squad_count)
            health_display = f"ХП: {current_unit_hp}/{max_unit_hp} | Отряд: {self.squad_count}/{base_squad_count}"
        else:
            health_display = f"Здоровье: {self.health}/{self.max_health}"
        
        # Определяем тип атаки для отображения - если руна магии активна, показываем оба типа
        if getattr(self, 'rune_magic_turns', 0) > 0 and self.magic_attack > 0:
            attack_display = f"Физ. атака: {self.phys_attack} | Маг. атака: {self.magic_attack}"
        else:
            attack_display = f"{attack_type_text} атака: {self.phys_attack if self.attack_type == 'physical' else self.magic_attack}"
        
        tooltip_text = [
            (f"Тип: {self.unit_type}", (255,255,255)),
            (health_display, fade_color(self.fade_health)),
            (attack_display, (255,180,180)),
            (f"Физ. защита: {self.phys_defense}", (180,180,255)),
            (f"Маг. защита: {self.magic_defense}", (200,180,255)),
            (f"Сопр. магии: {self.magic_resist}%", (255,200,255)),
            (f"Скорость: {self.speed}", (120,120,255) if hasattr(self, 'slow_turns') and getattr(self, 'slow_turns', 0) > 0 else fade_color(self.fade_speed)),
            (f"Инициатива: {self.initiative}", (255,220,120)),
        ]
        # Эффект Каменной кожи (показываем только длительность; защита уже учтена в текущем значении)
        if hasattr(self, 'stone_skin_turns') and getattr(self, 'stone_skin_turns', 0) > 0:
            tooltip_text.append((f"Каменная кожа: {self.stone_skin_turns} хода", (200,200,200)))
        # Защита (stance)
        if hasattr(self, '_defend_this_round') and getattr(self, '_defend_this_round', False):
            tooltip_text.append((f"В защите: +20% к защите", (100,180,255)))
        # --- Эффекты ---
        if self.attack_buff_turns > 0:
            tooltip_text.append((f"Благословение: {self.attack_buff_turns} хода", (80,255,80)))
        if self.attack_debuff_turns > 0:
            tooltip_text.append((f"Проклятие: {self.attack_debuff_turns} хода", (255,80,80)))
        # Только руна защиты
        if getattr(self, 'rune_shield_turns', 0) > 0:
            tooltip_text.append((f"Руна защиты: {self.rune_shield_turns} хода", (80,255,120)))
        # Руна магии
        if getattr(self, 'rune_magic_turns', 0) > 0:
            magic_bonus = getattr(self, 'rune_magic_bonus', 0)
            tooltip_text.append((f"Руна магии: {self.rune_magic_turns} хода", (200,150,255)))
            tooltip_text.append((f"Маг. атака: {self.magic_attack}", (200,150,255)))
        # Руна берсерка
        if getattr(self, 'rune_berserker_turns', 0) > 0:
            tooltip_text.append((f"Руна берсерка: {self.rune_berserker_turns} хода", (255,100,100)))
        # Огненный щит
        if hasattr(self, 'fire_shield_turns') and getattr(self, 'fire_shield_turns', 0) > 0:
            tooltip_text.append((f"Огненный щит: {self.fire_shield_turns} хода", (255,180,120)))
        # Ледяной щит
        if hasattr(self, 'ice_shield_turns') and getattr(self, 'ice_shield_turns', 0) > 0:
            tooltip_text.append((f"Ледяной щит: {self.ice_shield_turns} хода", (150,220,255)))
        # Контрудар
        if hasattr(self, 'counterstrike_turns') and getattr(self, 'counterstrike_turns', 0) > 0:
            tooltip_text.append((f"Контрудар: {self.counterstrike_turns} хода", (200,200,255)))
        # Слабость
        if hasattr(self, 'weakness_turns') and getattr(self, 'weakness_turns', 0) > 0:
            tooltip_text.append((f"Слабость: {self.weakness_turns} хода", (150,100,150)))
        # Ускорение (обычное заклинание)
        if hasattr(self, 'haste_turns') and getattr(self, 'haste_turns', 0) > 0:
            tooltip_text.append((f"Ускорение: {self.haste_turns} хода", (255,255,255)))
        # Руна скорости (рунический эффект)
        if hasattr(self, 'rune_haste_turns') and getattr(self, 'rune_haste_turns', 0) > 0:
            tooltip_text.append((f"Руна скорости: {self.rune_haste_turns} хода", (255,255,255)))
        if self.curse_turns > 0:
            tooltip_text.append((f"Проклятие: {self.curse_turns} хода", fade_color(self.fade_curse)))
        if hasattr(self, 'slow_turns') and getattr(self, 'slow_turns', 0) > 0:
            tooltip_text.append((f"Замедление: {self.slow_turns} хода", (120,120,255)))
        if hasattr(self, 'ice_arrow_turns') and getattr(self, 'ice_arrow_turns', 0) > 0:
            tooltip_text.append((f"Ледяная стрела: {self.ice_arrow_turns} хода (скорость -2, инициатива -4)", (150,220,255)))
        if hasattr(self, 'forget_turns') and getattr(self, 'forget_turns', 0) > 0:
            tooltip_text.append((f"Забвение: {self.forget_turns} хода", (200,200,255)))
        # Информация о клоне (фантоме)
        if getattr(self, 'is_phantom', False) and hasattr(self, 'phantom_turns'):
            tooltip_text.append((f"Фантом: осталось {self.phantom_turns} ходов", (150,200,255)))
        # Точность - только длительность
        if hasattr(self, 'accuracy_turns') and getattr(self, 'accuracy_turns', 0) > 0:
            tooltip_text.append((f"✨ Точность: {self.accuracy_turns} хода", (180,220,255)))
        # Молитва
        if hasattr(self, 'prayer_turns') and getattr(self, 'prayer_turns', 0) > 0:
            tooltip_text.append((f"Молитва: {self.prayer_turns} хода", (255,255,200)))
        # Ослепление
        if hasattr(self, 'blindness_turns') and getattr(self, 'blindness_turns', 0) > 0:
            tooltip_text.append((f"Ослепление: {self.blindness_turns} хода", (255,255,150)))
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

    def take_damage(self, damage, attack_type='physical', ignore_magic_defense=False):
        """
        Получить урон с учетом типа атаки и соответствующей защиты.
        attack_type: 'physical' или 'magical'
        ignore_magic_defense: если True, игнорирует магическую защиту (но не сопротивление магии)
        """
        # Выбираем подходящую защиту
        if attack_type == 'magical' and ignore_magic_defense:
            # Игнорируем магическую защиту (для шока земли)
            defense = 0
        else:
            defense = self.get_defense_against(attack_type)
        
        # Вычисляем урон после защиты
        actual = max(1, damage - defense)
        
        # Применяем сопротивление магии (только для магического урона)
        # Сопротивление магии снижает урон на процент (но не может отразить боевые заклинания)
        if attack_type == 'magical' and self.magic_resist > 0:
            resist_mult = (100 - self.magic_resist) / 100.0
            actual = max(1, int(actual * resist_mult))
        
        # Ледяной щит поглощает 35% физического урона
        if attack_type == 'physical' and hasattr(self, 'ice_shield_turns') and self.ice_shield_turns > 0:
            absorption = getattr(self, 'ice_shield_absorption', 0.35)
            absorbed = int(actual * absorption)
            actual = max(1, actual - absorbed)
        
        # Система отрядов: обрабатываем урон по юнитам
        if hasattr(self, 'squad_count') and hasattr(self, 'unit_hp') and self.unit_hp is not None and self.squad_count > 1:
            # Инициализируем current_unit_hp если нужно
            if self.current_unit_hp is None:
                self.current_unit_hp = self.unit_hp
            
            # Обрабатываем урон по текущему юниту
            remaining_damage = actual
            while remaining_damage > 0 and self.squad_count > 0:
                if remaining_damage >= self.current_unit_hp:
                    # Убиваем текущего юнита
                    remaining_damage -= self.current_unit_hp
                    self.squad_count -= 1
                    if self.squad_count > 0:
                        # Переходим к следующему юниту с полным здоровьем
                        self.current_unit_hp = self.unit_hp
                    else:
                        # Отряд уничтожен
                        self.current_unit_hp = 0
                        self.health = 0
                        break
                else:
                    # Текущий юнит ранен, но жив
                    self.current_unit_hp -= remaining_damage
                    remaining_damage = 0
            
            # Обновляем общее здоровье отряда
            if self.squad_count > 0:
                self.health = (self.squad_count - 1) * self.unit_hp + self.current_unit_hp
                self.max_health = self.base_squad_count * self.unit_hp
            else:
                self.health = 0
                self.max_health = self.base_squad_count * self.unit_hp
        else:
            # Стандартная система (без отрядов или одиночный юнит)
            self.health -= actual
            # Инициализируем unit_hp если это одиночный юнит
            if not hasattr(self, 'unit_hp') or self.unit_hp is None:
                self.unit_hp = self.max_health
                self.current_unit_hp = self.health
        
        try:
            self.last_damage_received = actual
        except Exception:
            pass
        was_killed = self.health <= 0
        game_ref = getattr(self, 'game_ref', None)
        try:
            if was_killed:
                if hasattr(self, 'on_death_animation'):
                    self.on_death_animation(game_ref)
            else:
                if hasattr(self, 'on_hurt_animation'):
                    self.on_hurt_animation(game_ref)
        except Exception:
            pass
        return was_killed
    
    def apply_precalculated_damage(self, total_damage):
        """
        Применяет уже рассчитанный урон (с учетом защиты) через систему отрядов.
        Используется для смешанного урона руны магии, где урон уже рассчитан.
        """
        # Система отрядов: обрабатываем урон по юнитам
        if hasattr(self, 'squad_count') and hasattr(self, 'unit_hp') and self.unit_hp is not None and self.squad_count > 1:
            # Инициализируем current_unit_hp если нужно
            if self.current_unit_hp is None:
                self.current_unit_hp = self.unit_hp
            
            # Обрабатываем урон по текущему юниту
            remaining_damage = total_damage
            while remaining_damage > 0 and self.squad_count > 0:
                if remaining_damage >= self.current_unit_hp:
                    # Убиваем текущего юнита
                    remaining_damage -= self.current_unit_hp
                    self.squad_count -= 1
                    if self.squad_count > 0:
                        # Переходим к следующему юниту с полным здоровьем
                        self.current_unit_hp = self.unit_hp
                    else:
                        # Отряд уничтожен
                        self.current_unit_hp = 0
                        self.health = 0
                        break
                else:
                    # Текущий юнит ранен, но жив
                    self.current_unit_hp -= remaining_damage
                    remaining_damage = 0
            
            # Обновляем общее здоровье отряда
            if self.squad_count > 0:
                self.health = (self.squad_count - 1) * self.unit_hp + self.current_unit_hp
                self.max_health = self.base_squad_count * self.unit_hp
            else:
                self.health = 0
                self.max_health = self.base_squad_count * self.unit_hp
        else:
            # Стандартная система (без отрядов или одиночный юнит)
            self.health = max(0, self.health - total_damage)
            # Инициализируем unit_hp если это одиночный юнит
            if not hasattr(self, 'unit_hp') or self.unit_hp is None:
                self.unit_hp = self.max_health
                self.current_unit_hp = self.health
        
        try:
            self.last_damage_received = total_damage
        except Exception:
            pass
        return self.health <= 0

    def end_turn_effects(self):
        """Уменьшает длительность эффектов в КОНЦЕ хода юнита"""
        # Забвение: уменьшаем счетчик
        if hasattr(self, 'forget_turns') and self.forget_turns > 0:
            self.forget_turns -= 1
            if self.forget_turns > 0:
                # Устанавливаем флаг для анимации в game на следующий ход
                self.skipped_turn_due_to_forget = True
        
        # Руна скорости: тикаем отдельный таймер
        if getattr(self, 'rune_haste_turns', 0) > 0:
            self.rune_haste_turns -= 1
            if self.rune_haste_turns == 0:
                # Сбрасываем к базе и применяем оставшиеся эффекты
                if hasattr(self, 'base_speed'):
                    self.speed = self.base_speed
                if hasattr(self, 'base_initiative'):
                    self.initiative = self.base_initiative
                # Если обычное ускорение ещё активно — применяем его
                if getattr(self, 'haste_turns', 0) > 0:
                    self.speed += 2
                    self.initiative += 5
                # Если замедление активно — применяем его
                if getattr(self, 'slow_turns', 0) > 0:
                    self.speed = max(1, self.speed - 1)
                    self.initiative = max(1, self.initiative - 5)
                if hasattr(self, 'game_ref') and self.game_ref:
                    self.game_ref.prepare_initiative_queue()
                print(f'Эффект Руны скорости закончился у {self.unit_type} ({self.x},{self.y})')
        # Ускорение: тикаем обычный таймер
        if getattr(self, 'haste_turns', 0) > 0:
            self.haste_turns -= 1
            if self.haste_turns == 0:
                # Сбрасываем к базе и применяем оставшиеся эффекты
                if hasattr(self, 'base_speed'):
                    self.speed = self.base_speed
                if hasattr(self, 'base_initiative'):
                    self.initiative = self.base_initiative
                # Если руна скорости ещё активна — применяем её
                if getattr(self, 'rune_haste_turns', 0) > 0:
                    self.speed += 2
                    self.initiative += 5
                # Если замедление активно — применяем его
                if getattr(self, 'slow_turns', 0) > 0:
                    self.speed = max(1, self.speed - 1)
                    self.initiative = max(1, self.initiative - 5)
                if hasattr(self, 'game_ref') and self.game_ref:
                    self.game_ref.prepare_initiative_queue()
                print(f'Эффект Ускорения закончился у {self.unit_type} ({self.x},{self.y})')
        # Каменная кожа
        if hasattr(self, 'stone_skin_turns') and self.stone_skin_turns > 0:
            self.stone_skin_turns -= 1
            if self.stone_skin_turns == 0:
                # Вернуть бонусы обеих защит
                self.phys_defense -= getattr(self, 'stone_skin_phys_bonus', 0)
                self.magic_defense -= getattr(self, 'stone_skin_magic_bonus', 0)
                self.stone_skin_phys_bonus = 0
                self.stone_skin_magic_bonus = 0
                print(f'Снимаем Каменную кожу с {self.unit_type} ({self.x},{self.y})')
        # Ледяной щит
        if hasattr(self, 'ice_shield_turns') and self.ice_shield_turns > 0:
            self.ice_shield_turns -= 1
            if self.ice_shield_turns == 0:
                # Снимаем бонусы защиты
                self.phys_defense -= getattr(self, 'ice_shield_phys_bonus', 0)
                self.ice_shield_phys_bonus = 0
                self.ice_shield_hp_bonus = 0
                self.ice_shield_absorption = 0
                print(f'Ледяной щит рассеялся у {self.unit_type} ({self.x},{self.y})')
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
        # Сброс эффекта ледяной стрелы
        if hasattr(self, 'ice_arrow_turns') and self.ice_arrow_turns > 0:
            self.ice_arrow_turns -= 1
            if self.ice_arrow_turns == 0:
                # Возвращаем скорость и инициативу
                if hasattr(self, 'base_speed'):
                    self.speed = self.base_speed
                if hasattr(self, 'base_initiative'):
                    self.initiative = self.base_initiative
                self.ice_arrow_speed_reduced = False
                # Пересчет очереди хода
                if hasattr(self, 'game_ref') and self.game_ref:
                    self.game_ref.prepare_initiative_queue()
                print(f'Эффект ледяной стрелы закончился у {self.unit_type} ({self.x},{self.y})')
        # Сброс эффекта точности
        if hasattr(self, 'accuracy_turns') and self.accuracy_turns > 0:
            self.accuracy_turns -= 1
            if self.accuracy_turns == 0:
                self.accuracy_active = False
                print(f'Эффект точности закончился у {self.unit_type} ({self.x},{self.y})')
        # Огненный щит: тикаем длительность
        if hasattr(self, 'fire_shield_turns') and getattr(self, 'fire_shield_turns', 0) > 0:
            self.fire_shield_turns -= 1
            if self.fire_shield_turns <= 0:
                self.fire_shield_turns = 0
                self.fire_shield_damage = 0
        # Руна защиты: тикаем длительность
        if getattr(self, 'rune_shield_turns', 0) > 0:
            self.rune_shield_turns -= 1
            if self.rune_shield_turns == 0:
                # Снимаем бонусы обеих защит
                self.phys_defense -= getattr(self, 'rune_shield_phys_bonus', 0)
                self.magic_defense -= getattr(self, 'rune_shield_magic_bonus', 0)
                self.rune_shield_phys_bonus = 0
                self.rune_shield_magic_bonus = 0
                print(f'Руна защиты рассеялась у {self.unit_type} ({self.x},{self.y})')
        # Руна берсерка: тикаем длительность
        if getattr(self, 'rune_berserker_turns', 0) > 0:
            # ОТЛАДКА: Логируем окончание хода
            try:
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
                from berserker_debug import get_debugger
                debugger = get_debugger()
                if debugger:
                    debugger.log_turn_end(self)
            except:
                pass
            
            self.rune_berserker_turns -= 1
            if self.rune_berserker_turns == 0:
                # ОТЛАДКА: Логируем окончание эффекта
                try:
                    debugger = get_debugger()
                    if debugger:
                        old_team = getattr(self, 'team', None)
                        debugger.log('BERSERKER_END', 
                                    f"Руна берсерка закончилась у {self.unit_type}",
                                    self,
                                    {'old_team': old_team})
                except:
                    pass
                
                # Восстанавливаем базовые значения атаки и защиты
                if hasattr(self, 'base_phys_attack_berserker'):
                    self.phys_attack = self.base_phys_attack_berserker
                if hasattr(self, 'base_magic_attack_berserker'):
                    self.magic_attack = self.base_magic_attack_berserker
                if hasattr(self, 'base_phys_defense_berserker'):
                    self.phys_defense = self.base_phys_defense_berserker
                if hasattr(self, 'base_magic_defense_berserker'):
                    self.magic_defense = self.base_magic_defense_berserker
                # Восстанавливаем оригинальную команду
                if hasattr(self, 'rune_berserker_original_team'):
                    old_team = getattr(self, 'team', None)
                    new_team = self.rune_berserker_original_team
                    self.team = new_team
                    
                    # ОТЛАДКА: Логируем восстановление команды
                    try:
                        debugger = get_debugger()
                        if debugger:
                            debugger.log_team_change(self, old_team, new_team, "Окончание руны берсерка")
                    except:
                        pass
                
                self.rune_berserker_active = False
                print(f'Руна берсерка рассеялась у {self.unit_type} ({self.x},{self.y})')
        # Контрудар: тикаем длительность
        if hasattr(self, 'counterstrike_turns') and self.counterstrike_turns > 0:
            self.counterstrike_turns -= 1
            if self.counterstrike_turns == 0:
                print(f'Контрудар закончился у {self.unit_type} ({self.x},{self.y})')
        # Слабость: тикаем длительность
        if hasattr(self, 'weakness_turns') and self.weakness_turns > 0:
            self.weakness_turns -= 1
            if self.weakness_turns == 0:
                # Восстанавливаем атаки
                self.phys_attack += getattr(self, 'weakness_phys_penalty', 0)
                self.magic_attack += getattr(self, 'weakness_magic_penalty', 0)
                self.weakness_phys_penalty = 0
                self.weakness_magic_penalty = 0
                print(f'Слабость рассеялась у {self.unit_type} ({self.x},{self.y})')
        # Ослепление: тикаем длительность
        if hasattr(self, 'blindness_turns') and getattr(self, 'blindness_turns', 0) > 0:
            self.blindness_turns -= 1
            if self.blindness_turns == 0:
                self.blindness_active = False
                print(f'Ослепление рассеялось у {self.unit_type} ({self.x},{self.y})')
        # Молитва: тикаем длительность и лечим каждый ход
        if hasattr(self, 'prayer_turns') and getattr(self, 'prayer_turns', 0) > 0:
            self.prayer_turns -= 1
            # Лечение каждый ход до максимума
            if hasattr(self, 'squad_count') and hasattr(self, 'current_unit_hp') and hasattr(self, 'unit_hp'):
                # Для отрядов лечим текущего юнита
                if self.current_unit_hp < self.unit_hp:
                    heal_amount = min(5, self.unit_hp - self.current_unit_hp)  # Лечим до 5 ХП за ход
                    self.current_unit_hp += heal_amount
                    self.health = (self.squad_count - 1) * self.unit_hp + self.current_unit_hp
                    if hasattr(self, 'game_ref') and self.game_ref:
                        self.game_ref.add_event(f"{self.unit_type.capitalize()} получает лечение от молитвы (+{heal_amount} ХП)")
            else:
                # Для обычных юнитов
                if self.health < self.max_health:
                    heal_amount = min(10, self.max_health - self.health)  # Лечим до 10 ХП за ход
                    self.health += heal_amount
                    if hasattr(self, 'game_ref') and self.game_ref:
                        self.game_ref.add_event(f"{self.unit_type.capitalize()} получает лечение от молитвы (+{heal_amount} ХП)")
            
            if self.prayer_turns == 0:
                # Снимаем бонусы молитвы
                if hasattr(self, 'prayer_applied') and self.prayer_applied:
                    if hasattr(self, 'attack_type') and self.attack_type == 'physical':
                        self.phys_attack = max(0, self.phys_attack - 2)
                    else:
                        self.magic_attack = max(0, self.magic_attack - 2)
                    self.phys_defense = max(0, self.phys_defense - 2)
                    self.magic_defense = max(0, self.magic_defense - 2)
                    self.speed = max(1, self.speed - 2)
                    self.initiative = max(1, self.initiative - 2)
                    self.prayer_applied = False
                    if hasattr(self, 'game_ref') and self.game_ref:
                        self.game_ref.prepare_initiative_queue()
                    print(f'Молитва рассеялась у {self.unit_type} ({self.x},{self.y})')

    def reset_turn(self):
        """Сбрасывает флаги действий в НАЧАЛЕ хода юнита"""
        self.has_moved = False
        self.has_attacked = False
        self.has_counterattacked = False
        # НЕ перезаписываем move_points_left если юнит ожидал и у него есть сохраненные ОД
        # move_points_left будет установлен в next_turn на основе _saved_move_points
        if not (hasattr(self, '_saved_move_points') or (hasattr(self, 'has_waited') and self.has_waited)):
            self.move_points_left = self.speed
        
        # Если юнит под забвением - блокируем его действия
        if hasattr(self, 'forget_turns') and self.forget_turns > 0:
            self.has_moved = True
            self.has_attacked = True
            self.skipped_turn_due_to_forget = True

    def can_attack(self, target_x, target_y, units=None):
        if hasattr(self, 'forget_turns') and getattr(self, 'forget_turns', 0) > 0:
            return False
        # Проверяем, находится ли юнит в зыбучих песках
        if getattr(self, 'stuck_in_quicksand', False):
            # Проверяем, что юнит всё ещё на клетке с зыбучими песками
            if hasattr(self, 'game_ref') and self.game_ref and hasattr(self.game_ref, 'quicksands'):
                for quicksand in self.game_ref.quicksands:
                    if quicksand['x'] == self.x and quicksand['y'] == self.y:
                        return False  # Юнит в зыбучих песках, не может атаковать
                # Если зыбучих песков на этой клетке больше нет, сбрасываем флаг
                self.stuck_in_quicksand = False
        # Ослепление: дальнобойные теряют возможность дальнобойной атаки
        if getattr(self, 'is_ranged', False) and getattr(self, 'blindness_active', False):
            # Ослепленные дальнобойные НЕ могут атаковать вообще (ни дальнобойно, ни в ближнем бою)
            return False
        if getattr(self, 'is_ranged', False) and not getattr(self, 'blindness_active', False):
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

    def can_move(self, target_x, target_y, units, barriers=None):
        if hasattr(self, 'forget_turns') and getattr(self, 'forget_turns', 0) > 0:
            return False
        # Юнит, застрявший в зыбучих песках, не может перемещаться
        if getattr(self, 'stuck_in_quicksand', False):
            # Проверяем, что юнит всё ещё на клетке с зыбучими песками
            if hasattr(self, 'game_ref') and self.game_ref and hasattr(self.game_ref, 'quicksands'):
                for quicksand in self.game_ref.quicksands:
                    if quicksand['x'] == self.x and quicksand['y'] == self.y:
                        return False  # Юнит в зыбучих песках, не может перемещаться
                # Если зыбучих песков на этой клетке больше нет, сбрасываем флаг
                self.stuck_in_quicksand = False
        from collections import deque
        if self.move_points_left <= 0:
            return False
        panel_height = 80  # Высота нижней панели интерфейса
        max_y = (SCREEN_HEIGHT - panel_height) // CELL_SIZE - 1
        if target_y > max_y or target_y < 0 or target_x < 0 or target_x >= SCREEN_WIDTH // CELL_SIZE:
            return False
        
        # Получаем список барьеров
        if barriers is None:
            if hasattr(self, 'game_ref') and self.game_ref and hasattr(self.game_ref, 'barriers'):
                barriers = self.game_ref.barriers
            else:
                barriers = []
        
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
                    # Проверяем, что клетка свободна от юнитов
                    has_unit = any(u.x == nx and u.y == ny for u in units)
                    # Проверяем барьеры - огненная стена разрешает прохождение, остальные блокируют
                    has_blocking_barrier = any(
                        b['x'] == nx and b['y'] == ny and b.get('type', 'rune_wall') != 'fire_wall' 
                        for b in barriers
                    )
                    
                    if not has_unit and not has_blocking_barrier:
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

    def get_ranged_damage_multiplier(self, target_x, target_y):
        """Возвращает множитель урона для дальнобойной атаки и информацию о штрафе"""
        distance = abs(self.x - target_x) + abs(self.y - target_y)
        
        # Проверяем эффект точности
        has_accuracy = getattr(self, 'accuracy_active', False) and getattr(self, 'accuracy_turns', 0) > 0
        
        # Если есть эффект точности - нет штрафа от расстояния
        if has_accuracy:
            if distance == 1:
                return 0.5, "1/2"  # Ближний бой - всё равно половина
            else:
                return 1.0, None  # Полный урон без штрафа
        
        # Новая система штрафа от расстояния
        # Если атака в ближнем бою (расстояние = 1), урон уменьшается вдвое
        if distance == 1:
            return 0.5, "1/2"
        # До 6 клеток включительно - полный урон
        elif distance <= 6:
            return 1.0, None
        # От 7 до ~10 клеток - 50% урона
        elif distance <= 10:
            return 0.5, "1/2"
        # От 11 до ~14 клеток - 25% урона (1/4)
        elif distance <= 14:
            return 0.25, "1/4"
        # Больше 14 клеток - 12.5% урона (1/8)
        else:
            return 0.125, "1/8"
    
    def ranged_damage(self, target_x, target_y):
        """Вычисляет урон дальнобойной атаки с учетом расстояния"""
        distance = abs(self.x - target_x) + abs(self.y - target_y)
        # get_current_attack уже учитывает squad_count, поэтому используем его
        base_damage = self.get_current_attack()
        # Гарантируем, что base_damage не отрицателен
        if base_damage < 1:
            base_damage = 1
        
        # Получаем множитель урона
        damage_multiplier, _ = self.get_ranged_damage_multiplier(target_x, target_y)
        
        # Если есть эффект точности - добавляем бонус 20%
        has_accuracy = getattr(self, 'accuracy_active', False) and getattr(self, 'accuracy_turns', 0) > 0
        if has_accuracy:
            base_damage = int(base_damage * 1.2)
        
        # Вычисляем итоговый урон
        result = int(base_damage * damage_multiplier)
        return max(1, result)

# --- Юниты людей ---
class Peasant(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath', 'Walk', 'WalkAlt',
            'AttackWindup', 'AttackStrike', 'AttackRecover',
            'HurtStart', 'HurtHold', 'HurtRecover',
            'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_peasant_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=720,
            idle_pause_duration=700,
        )
        self._melee_sequence = [
            ('AttackWindup', 120),
            ('AttackStrike', 160),
            ('AttackRecover', 120),
        ]
        self._counter_sequence = [
            ('AttackWindup', 100),
            ('AttackStrike', 140),
            ('AttackRecover', 120),
        ]
        self._hurt_sequence = [
            ('HurtStart', 110),
            ('HurtHold', 140),
            ('HurtRecover', 120),
        ]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._counter_sequence if is_counter else self._melee_sequence
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._play_sequence([('Death', 240)], game, reset_to_idle=False)
        self.set_animation_state('Corpse')


class Spearman(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath', 'Walk', 'WalkAlt',
            'AttackPrep', 'AttackThrust', 'AttackRecover',
            'HurtStart', 'HurtHold', 'HurtRecover',
            'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_spearman_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=680,
            idle_pause_duration=700,
        )
        self._melee_sequence = [
            ('AttackPrep', 130),
            ('AttackThrust', 150),
            ('AttackRecover', 130),
        ]
        self._counter_sequence = [
            ('AttackPrep', 110),
            ('AttackThrust', 140),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [
            ('HurtStart', 110),
            ('HurtHold', 140),
            ('HurtRecover', 120),
        ]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._counter_sequence if is_counter else self._melee_sequence
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._play_sequence([('Death', 260)], game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Crossbowman(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        # Используем только «живые» звуки выстрела, которые были даны пользователем
        # (основной звук выстрела обрабатывается в Game через self.shot_sound / self.shot2_sound)
        animation_states = [
            'Idle', 'IdleBreath', 'Walk', 'WalkAlt',
            'Attack', 'AttackAim', 'AttackRelease', 'AttackFollow', 'AttackRecover',
            'Attack02', 'Attack03',
            'MeleePrep', 'MeleeGuard', 'MeleeWindup', 'MeleeStrike', 'MeleeFollow', 'MeleeRecover',
            'Hurt', 'HurtStart', 'HurtHold', 'HurtRecover',
            'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_crossbowman_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=650,
            idle_pause_duration=700,
        )
        self.use_colored_corpse = True
        self._pending_post_attack_states = []

    def play_ranged_attack_animation(self, game, target):
        if target:
            self.set_facing_by_position(target.x)
        self._is_playing_sequence = True
        if self.bow_draw_sound:
            self.bow_draw_sound.play()
        sequence = [
            ('Attack', 130),
            ('AttackAim', 160),
            ('AttackRelease', 110),
        ]
        self._manual_face_timer = max(self._manual_face_timer, 45)
        for state, delay in sequence:
            self.set_animation_state(state)
            self._force_draw_and_delay(game, delay)
        self._pending_post_attack_states = [('AttackFollow', 100), ('AttackRecover', 130)]
        return True

    def finish_ranged_attack_animation(self, game=None):
        if self._pending_post_attack_states:
            for state, delay in self._pending_post_attack_states:
                self.set_animation_state(state)
                self._force_draw_and_delay(game, delay)
            self._pending_post_attack_states = []
        self.set_animation_state('Idle')
        self._is_playing_sequence = False

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        self._is_playing_sequence = True
        sequence = [
            ('MeleePrep', 90),
            ('MeleeWindup', 120 if not is_counter else 90),
            ('MeleeStrike', 150 if not is_counter else 110),
            ('MeleeFollow', 110),
            ('MeleeRecover', 120)
        ]
        for state, delay in sequence:
            self.set_animation_state(state)
            self._force_draw_and_delay(game, delay)
        self.set_animation_state('Idle')
        self._is_playing_sequence = False

    def on_hurt_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._is_playing_sequence = True
        for state, delay in [('HurtStart', 100), ('HurtHold', 120), ('HurtRecover', 110)]:
            self.set_animation_state(state)
            self._force_draw_and_delay(game, delay)
        self.set_animation_state('Idle')
        self._is_playing_sequence = False

    def on_death_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._is_playing_sequence = True
        self.set_animation_state('Death')
        self._force_draw_and_delay(game, 200)
        self.set_animation_state('Corpse')
        self._is_playing_sequence = False

    def get_corpse_surface(self):
        return self._frames.get('Corpse', self.image)

class Swordsman(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath', 'Walk', 'WalkAlt',
            'AttackPrep', 'AttackSlash', 'AttackRecover', 'Block',
            'HurtStart', 'HurtHold', 'HurtRecover',
            'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_swordsman_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=650,
            idle_pause_duration=720,
        )
        self._melee_sequence = [
            ('AttackPrep', 130),
            ('AttackSlash', 160),
            ('AttackRecover', 130),
        ]
        self._counter_sequence = [
            ('Block', 120),
            ('AttackSlash', 150),
            ('AttackRecover', 140),
        ]
        self._hurt_sequence = [
            ('HurtStart', 110),
            ('HurtHold', 140),
            ('HurtRecover', 130),
        ]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._counter_sequence if is_counter else self._melee_sequence
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._play_sequence([('Death', 260)], game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Gryphon(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath', 'Walk', 'WalkAlt',
            'AttackClaw', 'AttackBeak', 'AttackWing',
            'HurtStart', 'HurtHold', 'HurtRecover',
            'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_gryphon_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=600,
            idle_pause_duration=640,
        )
        self._melee_sequence = [
            ('AttackClaw', 140),
            ('AttackBeak', 130),
            ('AttackWing', 140),
        ]
        self._counter_sequence = [
            ('AttackBeak', 120),
            ('AttackClaw', 130),
        ]
        self._hurt_sequence = [
            ('HurtStart', 110),
            ('HurtHold', 140),
            ('HurtRecover', 130),
        ]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._counter_sequence if is_counter else self._melee_sequence
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._play_sequence([('Death', 240)], game, reset_to_idle=False)
        self.set_animation_state('Corpse')

# --- Юниты нежити ---
class Skeleton(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_skeleton_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=720,
            idle_pause_duration=580,
            turn_sequence_duration=120,
        )
        self._attack_sequence = [
            ('AttackPrep', 110),
            ('AttackStrike', 150),
            ('AttackRecover', 110),
        ]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')


class Zombie(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_zombie_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=800,
            idle_pause_duration=700,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=130,
        )
        self._attack_sequence = [
            ('AttackPrep', 150),
            ('AttackStrike', 190),
            ('AttackRecover', 150),
        ]
        self._hurt_sequence = [('Hurt', 200)]
        self._death_sequence = [('Death', 320)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(90, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')


class Ghost(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_ghost_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=820,
            idle_pause_duration=720,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=130,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 190)]
        self._death_sequence = [('Death', 310)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 30)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')


class Vampire(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_vampire_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=780,
            idle_pause_duration=640,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=130,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 180),
            ('AttackRecover', 140),
        ]
        self._hurt_sequence = [('Hurt', 190)]
        self._death_sequence = [('Death', 320)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(90, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')


class Lich(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_lich_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=800,
            idle_pause_duration=680,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=140,
        )
        self._attack_sequence = [
            ('AttackPrep', 140),
            ('AttackStrike', 190),
            ('AttackRecover', 140),
        ]
        self._hurt_sequence = [('Hurt', 200)]
        self._death_sequence = [('Death', 330)]

    def play_ranged_attack_animation(self, game, target):
        if target:
            self.set_facing_by_position(target.x)
        self._play_sequence(self._attack_sequence, game, reset_to_idle=False)
        return True

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')


# Старые классы Warrior, Archer, Knight больше не нужны 

class Hero(Unit):
    def __init__(self, x, y, team, spells=None, attack=0, defense=0, knowledge=3, spell_power=1, hero_class=None, luck=0, combat_spirit=0):
        super().__init__(x, y, team, 'hero')
        
        # Определяем класс героя по умолчанию для каждой расы
        # Используем unit_race если он уже установлен, иначе team (для совместимости)
        if hero_class is None:
            # Сначала проверяем, есть ли unit_race (используется после инициализации)
            race_for_class = getattr(self, 'unit_race', None) or team
            default_classes = {
                'human': 'warrior',
                'elf': 'archer',
                'undead': 'mage',
                'demon': 'warrior',
                'dwarf': 'warrior',
                'shadow': 'mage'
            }
            hero_class = default_classes.get(race_for_class, 'warrior')
        
        self.hero_class = hero_class
        self.attack = attack
        self.defense = defense
        self.knowledge = knowledge
        self.spell_power = spell_power
        self.luck = max(-6, min(6, luck))  # Ограничение +6/-6
        self.combat_spirit = max(-6, min(6, combat_spirit))  # Боевой дух (ограничение +6/-6)
        self.mana = knowledge * 10
        self.max_mana = knowledge * 10
        self.mana_regen = 2
        self.spells = spells if spells is not None else []
        self.selected_spell = None
        self.used_spell_this_round = False
        
        # Загружаем изображение в зависимости от расы и класса
        # Используем unit_race если есть, иначе team (для совместимости)
        race_for_image = getattr(self, 'unit_race', None) or team
        image_name = f'hero_{race_for_image}_{hero_class}'
        try:
            self.image = load_image(image_name)
        except:
            # Если изображения для класса нет, используем стандартное по расе
            try:
                self.image = load_image(f'hero_{race_for_image}')
            except:
                # Если и этого нет, используем команду (fallback)
                self.image = load_image(f'hero_{team}')
        
        self.hover_time = 0
        self.show_tooltip = False
        self.last_tooltip_update = time.time()
        self.game_ref = None
        
        # Устанавливаем тип атаки и дальность в зависимости от класса
        if hero_class == 'archer':
            self.is_ranged = True
            self.attack_type = 'physical'
        elif hero_class == 'mage':
            self.is_ranged = True
            self.attack_type = 'magical'
        else:  # warrior
            self.is_ranged = False
            self.attack_type = 'physical'
        
        self.has_attacked = False

    def draw(self, surface):
        # Рисуем героя на поле (без полоски здоровья)
        surface.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))
        # Если герой под берсерком - накладываем красный оттенок
        if getattr(self, 'rune_berserker_active', False):
            red_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            red_overlay.fill((255, 100, 100, 120))  # Красный полупрозрачный слой
            surface.blit(red_overlay, (self.x * CELL_SIZE, self.y * CELL_SIZE))
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
        # Названия классов на русском
        class_names = {
            'warrior': 'Воин',
            'archer': 'Лучник',
            'mage': 'Маг'
        }
        class_name = class_names.get(self.hero_class, self.hero_class)
        
        # Вычисляем базовую атаку в зависимости от класса
        if self.hero_class == 'mage':
            base_attack = 5 + self.spell_power
        else:  # warrior или archer
            base_attack = 5 + self.attack
        
        # Показываем команду и расу отдельно
        team_label = TEAM_LABELS.get(self.team, self.team)
        race_label = ""
        if hasattr(self, 'unit_race') and self.unit_race:
            from .core import RACE_LABELS
            race_label = f" - {RACE_LABELS.get(self.unit_race, self.unit_race)}"
        tooltip_text = [
            (f"Герой - {class_name} ({team_label}{race_label})", (255,255,255)),
            (f"Базовая атака: {base_attack}", (255,180,120)),
            (f"Атака: {self.attack}", (255,220,120)),
            (f"Защита: {self.defense}", (180,180,255)),
            (f"Сила магии: {self.spell_power}", (180,120,255)),
            (f"Знания: {self.knowledge}", (120,255,255)),
            (f"Мана: {self.mana}/{self.max_mana}", (120,220,255)),
            (f"Удача: {self.luck:+d} ({abs(self.luck) * 5}% шанс двойного урона)", (255,255,100)),
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
        # Проверяем, находится ли герой в зыбучих песках
        if getattr(self, 'stuck_in_quicksand', False):
            # Проверяем, что герой всё ещё на клетке с зыбучими песками
            if hasattr(self, 'game_ref') and self.game_ref and hasattr(self.game_ref, 'quicksands'):
                for quicksand in self.game_ref.quicksands:
                    if quicksand['x'] == self.x and quicksand['y'] == self.y:
                        return False  # Герой в зыбучих песках, не может атаковать
                # Если зыбучих песков на этой клетке больше нет, сбрасываем флаг
                self.stuck_in_quicksand = False
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

    def take_damage(self, damage, attack_type='physical'):
        # Герой не получает урон, но фиксируем полученный урон для реактивных эффектов (огненный щит)
        try:
            self.last_damage_received = max(1, int(damage))
        except Exception:
            pass
        return False

    def reset_turn(self):
        self.selected_spell = None
        self.used_spell_this_round = False
        self.has_attacked = False

    def can_move(self, target_x, target_y, units, barriers=None):
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
                # Передаем удачу от героя юнитам (ограничиваем до -6/+6)
                unit.luck = max(-6, min(6, self.luck))

class Pixie(AnimatedHumanoidMixin, Unit):
    """Фея (ранее Пикси) - молодая дриада."""
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'fairy')  # Используем 'fairy' вместо 'pixie'
        self.health = 25
        self.max_health = 25
        self.attack = 5
        self.defense = 1
        self.speed = 6
        self.initiative = 16
        self.attack_range = 1
        self.base_defense = 1
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdlePulse', 'IdleHover',
            'Walk', 'WalkAlt',
            'CastStart', 'CastRelease', 'CastRecover',
            'Hurt', 'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_fairy_texture,
            animation_states,
            idle_cycle=('Idle', 'IdlePulse', 'IdleHover'),
            idle_switch_interval=480,
            idle_pause_duration=360,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=90,
        )
        self._melee_sequence = [
            ('CastStart', 110),
            ('CastRelease', 150),
            ('CastRecover', 120),
        ]
        self._hurt_sequence = [('Hurt', 150)]
        self._death_sequence = [('Death', 220)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        self._play_sequence(self._melee_sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class ElfScout(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'HurtStart', 'HurtHold', 'HurtRecover',
            'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_elf_scout_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=620,
            idle_pause_duration=500,
            turn_sequence_duration=110,
        )
        self._attack_sequence = [
            ('AttackPrep', 110),
            ('AttackStrike', 150),
            ('AttackRecover', 120),
        ]
        self._counter_sequence = [
            ('AttackPrep', 90),
            ('AttackStrike', 130),
            ('AttackRecover', 100),
        ]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 260)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._counter_sequence if is_counter else self._attack_sequence
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class ElfArcher(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        # Не подгружаем синтетические звуки натяжения и полёта стрелы —
        # для выстрела используются только звуки «выстрел» / «выстрел 2», предоставленные пользователем
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'Attack', 'AttackDraw', 'AttackAim', 'Attack02', 'AttackRelease', 'Attack03', 'AttackFollow', 'AttackRecover',
            'MeleePrep', 'MeleeGuard', 'MeleeWindup', 'MeleeStrike', 'MeleeFollow', 'MeleeRecover',
            'Hurt', 'HurtStart', 'HurtHold', 'HurtRecover',
            'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_elf_archer_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=680,
            idle_pause_duration=560,
            turn_sequence_duration=120,
        )
        self._ranged_sequence = [('AttackDraw', 130), ('AttackRelease', 120)]
        self._ranged_recover = [('AttackRecover', 120)]
        self._melee_sequence = [
            ('MeleePrep', 120),
            ('MeleeStrike', 150),
            ('MeleeRecover', 120),
        ]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 280)]
        self._pending_post_attack_states = []

    def play_ranged_attack_animation(self, game, target):
        if target:
            self.set_facing_by_position(target.x)
        if self.bow_draw_sound:
            self.bow_draw_sound.play()
        self._manual_face_timer = max(self._manual_face_timer, 45)
        self._play_sequence(self._ranged_sequence, game, reset_to_idle=False)
        self._pending_post_attack_states = list(self._ranged_recover)
        return True

    def finish_ranged_attack_animation(self, game=None):
        if self._pending_post_attack_states:
            self._play_sequence(self._pending_post_attack_states, game)
            self._pending_post_attack_states = []
        self.set_animation_state('Idle')

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        self._play_sequence(self._melee_sequence, game)

    def on_hurt_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        attacker = getattr(game, 'selected_unit', None) if game else None
        if attacker and attacker is not self:
            self.set_facing_by_position(attacker.x)
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')


class Dryad(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleSway',
            'Walk', 'WalkAlt',
            'CastStart', 'CastRelease', 'CastRecover',
            'Hurt', 'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_dryad_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleSway'),
            idle_switch_interval=600,
            idle_pause_duration=480,
            turn_sequence_duration=120,
        )
        self._attack_sequence = [
            ('CastStart', 130),
            ('CastRelease', 160),
            ('CastRecover', 120),
        ]
        self._hurt_sequence = [('Hurt', 160)]
        self._death_sequence = [('Death', 280)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        self._play_sequence(self._attack_sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')


class Ent(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_ent_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=780,
            idle_pause_duration=620,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=140,
        )
        self._attack_sequence = [
            ('AttackPrep', 150),
            ('AttackStrike', 190),
            ('AttackRecover', 150),
        ]
        self._hurt_sequence = [('Hurt', 190)]
        self._death_sequence = [('Death', 320)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        self._play_sequence(self._attack_sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Imp(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_imp_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=600,
            idle_pause_duration=500,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=100,
        )
        self._attack_sequence = [
            ('AttackPrep', 120),
            ('AttackStrike', 150),
            ('AttackRecover', 100),
        ]
        self._hurt_sequence = [('Hurt', 150)]
        self._death_sequence = [('Death', 200)]

class Gog(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackAim', 'AttackRelease', 'AttackRecover',
            'Hurt', 'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_gog_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=650,
            idle_pause_duration=550,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=110,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackAim', 150),
            ('AttackRelease', 180),
            ('AttackRecover', 120),
        ]
        self._hurt_sequence = [('Hurt', 160)]
        self._death_sequence = [('Death', 240)]

class Demon(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_demon_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=120,
        )
        self._attack_sequence = [
            ('AttackPrep', 140),
            ('AttackStrike', 180),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 280)]

class Cerberus(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_cerberus_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=750,
            idle_pause_duration=650,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=130,
        )
        self._attack_sequence = [
            ('AttackPrep', 150),
            ('AttackStrike', 200),
            ('AttackRecover', 150),
        ]
        self._hurt_sequence = [('Hurt', 190)]
        self._death_sequence = [('Death', 300)]

class Succubus(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackAim', 'AttackRelease', 'AttackRecover',
            'Hurt', 'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_succubus_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=680,
            idle_pause_duration=580,
            movement_cycle=('Walk', 'WalkAlt'),
            turn_sequence_duration=115,
        )
        self._attack_sequence = [
            ('AttackPrep', 140),
            ('AttackAim', 160),
            ('AttackRelease', 190),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 165)]
        self._death_sequence = [('Death', 260)]

# --- Гномы ---
class Miner(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_miner_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 120),
            ('AttackStrike', 160),
            ('AttackRecover', 120),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Spearthrower(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'CastStart', 'CastRelease', 'CastRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_spearthrower_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._ranged_sequence = [
            ('CastStart', 140),
            ('CastRelease', 170),
        ]
        self._ranged_recover = [('CastRecover', 130)]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 300)]
        self._pending_post_attack_states = []

    def play_ranged_attack_animation(self, game, target):
        if target:
            self.set_facing_by_position(target.x)
        self._play_sequence(self._ranged_sequence, game, reset_to_idle=False)
        self._pending_post_attack_states = list(self._ranged_recover)
        return True

    def finish_ranged_attack_animation(self, game=None):
        if self._pending_post_attack_states:
            self._play_sequence(self._pending_post_attack_states, game)
            self._pending_post_attack_states = []
        self.set_animation_state('Idle')

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._ranged_sequence + self._ranged_recover
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class BearRider(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_bearrider_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class RuneMage(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'CastStart', 'CastRelease', 'CastRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_runemage_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._ranged_sequence = [
            ('CastStart', 140),
            ('CastRelease', 170),
        ]
        self._ranged_recover = [('CastRecover', 130)]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 300)]
        self._pending_post_attack_states = []

    def play_ranged_attack_animation(self, game, target):
        if target:
            self.set_facing_by_position(target.x)
        self._play_sequence(self._ranged_sequence, game, reset_to_idle=False)
        self._pending_post_attack_states = list(self._ranged_recover)
        return True

    def finish_ranged_attack_animation(self, game=None):
        if self._pending_post_attack_states:
            self._play_sequence(self._pending_post_attack_states, game)
            self._pending_post_attack_states = []
        self.set_animation_state('Idle')

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._ranged_sequence + self._ranged_recover
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Jarl(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_jarl_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

# --- Лига теней ---
class Scout(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_scout_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 120),
            ('AttackStrike', 160),
            ('AttackRecover', 120),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Beast(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_beast_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Minotaur(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_minotaur_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Witch(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'CastStart', 'CastRelease', 'CastRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_witch_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._ranged_sequence = [
            ('CastStart', 140),
            ('CastRelease', 170),
        ]
        self._ranged_recover = [('CastRecover', 130)]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 300)]
        self._pending_post_attack_states = []

    def play_ranged_attack_animation(self, game, target):
        if target:
            self.set_facing_by_position(target.x)
        self._play_sequence(self._ranged_sequence, game, reset_to_idle=False)
        self._pending_post_attack_states = list(self._ranged_recover)
        return True

    def finish_ranged_attack_animation(self, game=None):
        if self._pending_post_attack_states:
            self._play_sequence(self._pending_post_attack_states, game)
            self._pending_post_attack_states = []
        self.set_animation_state('Idle')

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._ranged_sequence + self._ranged_recover
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class LizardRider(AnimatedHumanoidMixin, Unit):
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
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_lizardrider_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

# --- Заглушки для будущих юнитов ---
# Люди
class Monk(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'monk')
        self.health = 60
        self.max_health = 60
        self.attack = 14
        self.defense = 6
        self.speed = 4
        self.initiative = 13
        self.attack_range = 1
        self.base_defense = 6
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_monk_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            # Чуть быстрее анимация при контратаке
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Angel(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'angel')
        self.health = 100
        self.max_health = 100
        self.attack = 20
        self.defense = 12
        self.speed = 5
        self.initiative = 16
        self.attack_range = 1
        self.base_defense = 12
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_angel_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=620,
            turn_sequence_duration=120,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 320)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Cavalryman(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'cavalryman')
        self.health = 80
        self.max_health = 80
        self.attack = 16
        self.defense = 8
        self.speed = 6
        self.initiative = 13
        self.attack_range = 1
        self.base_defense = 8
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_cavalryman_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=650,
            idle_pause_duration=580,
            turn_sequence_duration=120,
        )
        self._attack_sequence = [
            ('AttackPrep', 120),
            ('AttackStrike', 160),
            ('AttackRecover', 120),
        ]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 310)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

# Эльфы
class GreenDragon(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'greendragon')
        self.health = 120
        self.max_health = 120
        self.attack = 22
        self.defense = 14
        self.speed = 4
        self.initiative = 15
        self.attack_range = 1
        self.base_defense = 14
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_greendragon_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=680,
            idle_pause_duration=560,
            turn_sequence_duration=120,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 180),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 190)]
        self._death_sequence = [('Death', 320)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Druid(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'druid')
        self.health = 55
        self.max_health = 55
        self.attack = 16
        self.defense = 5
        self.speed = 4
        self.initiative = 12
        self.is_ranged = True
        self.attack_range = 4
        self.base_defense = 5
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'CastStart', 'CastRelease', 'CastRecover',
            'Hurt', 'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_druid_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=540,
            turn_sequence_duration=120,
        )
        self._ranged_sequence = [
            ('CastStart', 140),
            ('CastRelease', 170),
        ]
        self._ranged_recover = [('CastRecover', 130)]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 300)]
        self._pending_post_attack_states = []

    def play_ranged_attack_animation(self, game, target):
        if target:
            self.set_facing_by_position(target.x)
        self._play_sequence(self._ranged_sequence, game, reset_to_idle=False)
        self._pending_post_attack_states = list(self._ranged_recover)
        return True

    def finish_ranged_attack_animation(self, game=None):
        if self._pending_post_attack_states:
            self._play_sequence(self._pending_post_attack_states, game)
            self._pending_post_attack_states = []
        self.set_animation_state('Idle')

    def play_melee_animation(self, game, opponent, is_counter=False):
        # Используем тот же жест заклинания
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._ranged_sequence + self._ranged_recover
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Unicorn(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'unicorn')
        self.health = 90
        self.max_health = 90
        self.attack = 18
        self.defense = 10
        self.speed = 6
        self.initiative = 14
        self.attack_range = 1
        self.base_defense = 10
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'ChargePrep', 'ChargeImpact', 'ChargeRecover',
            'Hurt', 'TurnLeft', 'TurnRight', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_unicorn_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=600,
            idle_pause_duration=520,
            turn_sequence_duration=120,
        )
        self._attack_sequence = [
            ('ChargePrep', 130),
            ('ChargeImpact', 170),
            ('ChargeRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 160)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        self._play_sequence(self._attack_sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

# Нежить
class DeathKnight(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'deathknight')
        self.health = 95
        self.max_health = 95
        self.attack = 19
        self.defense = 11
        self.speed = 5
        self.initiative = 13
        self.attack_range = 1
        self.base_defense = 11
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_deathknight_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class BoneDragon(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'bonedragon')
        self.health = 130
        self.max_health = 130
        self.attack = 24
        self.defense = 15
        self.speed = 4
        self.initiative = 16
        self.attack_range = 1
        self.base_defense = 15
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_bonedragon_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 180),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 190)]
        self._death_sequence = [('Death', 320)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Reaper(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'reaper')
        self.health = 70
        self.max_health = 70
        self.attack = 17
        self.defense = 7
        self.speed = 5
        self.initiative = 14
        self.attack_range = 1
        self.base_defense = 7
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_reaper_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

# Демоны
class BloodPriestess(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'bloodpriestess')
        self.health = 65
        self.max_health = 65
        self.attack = 15
        self.defense = 6
        self.speed = 5
        self.initiative = 13
        self.is_ranged = True
        self.attack_range = 4
        self.base_defense = 6
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'CastStart', 'CastRelease', 'CastRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_bloodpriestess_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._ranged_sequence = [
            ('CastStart', 140),
            ('CastRelease', 170),
        ]
        self._ranged_recover = [('CastRecover', 130)]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 300)]
        self._pending_post_attack_states = []

    def play_ranged_attack_animation(self, game, target):
        if target:
            self.set_facing_by_position(target.x)
        self._play_sequence(self._ranged_sequence, game, reset_to_idle=False)
        self._pending_post_attack_states = list(self._ranged_recover)
        return True

    def finish_ranged_attack_animation(self, game=None):
        if self._pending_post_attack_states:
            self._play_sequence(self._pending_post_attack_states, game)
            self._pending_post_attack_states = []
        self.set_animation_state('Idle')

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._ranged_sequence + self._ranged_recover
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Devil(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'devil')
        self.health = 110
        self.max_health = 110
        self.attack = 21
        self.defense = 13
        self.speed = 5
        self.initiative = 15
        self.attack_range = 1
        self.base_defense = 13
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_devil_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class HellHorse(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'hellhorse')
        self.health = 85
        self.max_health = 85
        self.attack = 17
        self.defense = 9
        self.speed = 7
        self.initiative = 15
        self.attack_range = 1
        self.base_defense = 9
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_hellhorse_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

# Гномы
class ForgeDragon(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'forgedragon')
        self.health = 125
        self.max_health = 125
        self.attack = 23
        self.defense = 16
        self.speed = 3
        self.initiative = 14
        self.attack_range = 1
        self.base_defense = 16
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_forgedragon_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 180),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 190)]
        self._death_sequence = [('Death', 320)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class MountainRuler(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'mountainruler')
        self.health = 100
        self.max_health = 100
        self.attack = 20
        self.defense = 14
        self.speed = 4
        self.initiative = 15
        self.attack_range = 1
        self.base_defense = 14
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_mountainruler_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Volkhv(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'volkhv')
        self.health = 75
        self.max_health = 75
        self.attack = 18
        self.defense = 8
        self.speed = 5
        self.initiative = 13
        self.is_ranged = True
        self.attack_range = 4
        self.base_defense = 8
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'CastStart', 'CastRelease', 'CastRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_volkhv_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._ranged_sequence = [
            ('CastStart', 140),
            ('CastRelease', 170),
        ]
        self._ranged_recover = [('CastRecover', 130)]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 300)]
        self._pending_post_attack_states = []

    def play_ranged_attack_animation(self, game, target):
        if target:
            self.set_facing_by_position(target.x)
        self._play_sequence(self._ranged_sequence, game, reset_to_idle=False)
        self._pending_post_attack_states = list(self._ranged_recover)
        return True

    def finish_ranged_attack_animation(self, game=None):
        if self._pending_post_attack_states:
            self._play_sequence(self._pending_post_attack_states, game)
            self._pending_post_attack_states = []
        self.set_animation_state('Idle')

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._ranged_sequence + self._ranged_recover
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

# Тени
class Manticore(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'manticore')
        self.health = 95
        self.max_health = 95
        self.attack = 19
        self.defense = 11
        self.speed = 6
        self.initiative = 14
        self.attack_range = 1
        self.base_defense = 11
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_manticore_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 170),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 180)]
        self._death_sequence = [('Death', 300)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class RedDragon(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'reddragon')
        self.health = 135
        self.max_health = 135
        self.attack = 25
        self.defense = 17
        self.speed = 4
        self.initiative = 17
        self.attack_range = 1
        self.base_defense = 17
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_reddragon_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._attack_sequence = [
            ('AttackPrep', 130),
            ('AttackStrike', 180),
            ('AttackRecover', 130),
        ]
        self._hurt_sequence = [('Hurt', 190)]
        self._death_sequence = [('Death', 320)]

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        seq = list(self._attack_sequence)
        if is_counter:
            seq = [(state, max(80, delay - 40)) for state, delay in seq]
        self._play_sequence(seq, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Beholder(AnimatedHumanoidMixin, Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'beholder')
        self.health = 80
        self.max_health = 80
        self.attack = 20
        self.defense = 10
        self.speed = 4
        self.initiative = 15
        self.is_ranged = True
        self.attack_range = 5
        self.base_defense = 10
        self.convert_old_stats_to_new()
        animation_states = [
            'Idle', 'IdleBreath',
            'Walk', 'WalkAlt',
            'AttackPrep', 'AttackStrike', 'AttackRecover',
            'Hurt', 'Death', 'Corpse'
        ]
        self._init_animation_system(
            load_beholder_texture,
            animation_states,
            idle_cycle=('Idle', 'IdleBreath'),
            idle_switch_interval=700,
            idle_pause_duration=600,
        )
        self._ranged_sequence = [
            ('AttackPrep', 140),
            ('AttackStrike', 170),
        ]
        self._ranged_recover = [('AttackRecover', 130)]
        self._hurt_sequence = [('Hurt', 170)]
        self._death_sequence = [('Death', 300)]
        self._pending_post_attack_states = []

    def play_ranged_attack_animation(self, game, target):
        if target:
            self.set_facing_by_position(target.x)
        self._play_sequence(self._ranged_sequence, game, reset_to_idle=False)
        self._pending_post_attack_states = list(self._ranged_recover)
        return True

    def finish_ranged_attack_animation(self, game=None):
        if self._pending_post_attack_states:
            self._play_sequence(self._pending_post_attack_states, game)
            self._pending_post_attack_states = []
        self.set_animation_state('Idle')

    def play_melee_animation(self, game, opponent, is_counter=False):
        if opponent:
            self.set_facing_by_position(opponent.x)
        sequence = self._ranged_sequence + self._ranged_recover
        self._play_sequence(sequence, game)

    def on_hurt_animation(self, game=None):
        self._play_sequence(self._hurt_sequence, game)

    def on_death_animation(self, game=None):
        self._play_sequence(self._death_sequence, game, reset_to_idle=False)
        self.set_animation_state('Corpse')

class Corpse:
    """Труп юнита - остаётся на поле после смерти, юниты могут проходить сквозь него"""
    def __init__(self, x, y, team, unit_type, max_health):
        self.x = x
        self.y = y
        self.team = team
        self.unit_type = unit_type
        self.max_health = max_health
        self.is_corpse = True
        # Загружаем изображение юнита для отображения в сером цвете
        try:
            self.original_image = load_image(f'{unit_type}_{team}')
        except:
            self.original_image = None
    
    def draw(self, screen):
        """Отрисовка трупа серым цветом"""
        if self.original_image:
            # Создаём серую версию изображения
            gray_surface = pygame.Surface(self.original_image.get_size())
            gray_surface.fill((128, 128, 128))  # Серый цвет
            gray_surface.blit(self.original_image, (0, 0), special_flags=pygame.BLEND_MULT)
            # Делаем полупрозрачным
            gray_surface.set_alpha(150)
            screen.blit(gray_surface, (self.x * CELL_SIZE, self.y * CELL_SIZE))


def get_unit_race(unit):
    """
    Возвращает расу юнита на основе его типа или сохраненной расы.
    :param unit: Объект юнита
    :return: Раса юнита (human, undead, elf, demon, dwarf, shadow)
    """
    # Если есть сохраненная раса - используем её (для креативного режима)
    if hasattr(unit, 'unit_race') and unit.unit_race:
        return unit.unit_race
    
    # Если команда - это реальная раса (не player1/player2/berserker_*), используем её
    team = getattr(unit, 'team', None)
    if team and team in ['human', 'undead', 'elf', 'demon', 'dwarf', 'shadow']:
        return team
    
    # Для берсерков - восстанавливаем оригинальную расу
    if team and isinstance(team, str) and team.startswith('berserker_'):
        if hasattr(unit, 'rune_berserker_original_team'):
            original_team = unit.rune_berserker_original_team
            if original_team in ['human', 'undead', 'elf', 'demon', 'dwarf', 'shadow']:
                return original_team
    
    # Определяем расу по типу юнита
    unit_type = getattr(unit, 'unit_type', None)
    if not unit_type:
        return None
    
    # Маппинг типов юнитов на расы
    unit_type_to_race = {
        # Люди
        'peasant': 'human', 'spearman': 'human', 'crossbowman': 'human', 
        'swordsman': 'human', 'gryphon': 'human',
        # Нежить
        'skeleton': 'undead', 'zombie': 'undead', 'ghost': 'undead', 
        'vampire': 'undead', 'lich': 'undead',
        # Эльфы
        'fairy': 'elf', 'pixie': 'elf', 'elf_scout': 'elf', 'elf_archer': 'elf', 
        'dryad': 'elf', 'ent': 'elf',
        # Демоны
        'imp': 'demon', 'gog': 'demon', 'demon': 'demon', 
        'cerberus': 'demon', 'succubus': 'demon',
        # Гномы
        'miner': 'dwarf', 'spearthrower': 'dwarf', 'bear_rider': 'dwarf', 
        'runemage': 'dwarf', 'jarl': 'dwarf',
        # Тени
        'scout': 'shadow', 'beast': 'shadow', 'minotaur': 'shadow', 
        'witch': 'shadow', 'lizard_rider': 'shadow'
    }
    
    # Для героев определяем по team (если это реальная раса)
    if unit_type == 'hero':
        if team and team in ['human', 'undead', 'elf', 'demon', 'dwarf', 'shadow']:
            return team
        # Если team - это player1/player2, пытаемся определить по другим юнитам команды
        if hasattr(unit, 'game_ref') and unit.game_ref:
            for u in unit.game_ref.units:
                if u.team == team and u.unit_type != 'hero':
                    race = get_unit_race(u)
                    if race:
                        return race
    
    return unit_type_to_race.get(unit_type, None)


def calculate_morale(unit, all_units):
    """
    Рассчитывает мораль юнита на основе расового состава команды.
    Мораль зависит только от состава своей команды, не от врагов.
    
    Правила:
    - Если команда состоит полностью из своей расы → мораль "good"
    - Нежить всегда имеет мораль "neutral"
    - Нежить понижает мораль на 1 для любой расы (кроме нежити)
    - Система нетерпимостей: на 3 юнитов с терпимостью приходится 1 нетерпимый → мораль -1
    
    :param unit: Объект юнита
    :param all_units: Список всех юнитов на поле
    :return: Значение морали ('excellent', 'good', 'neutral', 'bad', 'awful')
    """
    from .units import get_unit_race
    
    # У нежити мораль всегда нейтральная
    unit_race = get_unit_race(unit)
    if unit_race == 'undead':
        return 'neutral'
    
    # Проверяем, является ли юнит героем
    is_hero = lambda u: getattr(u, 'unit_type', None) == 'hero'
    
    # Получаем всех союзников (только обычных юнитов, не героев)
    allies = [u for u in all_units if u.team == unit.team and not is_hero(u)]
    
    # Если нет союзников - ужасная мораль
    if len(allies) == 0:
        return 'awful'
    
    # Подсчитываем количество юнитов каждой расы в команде
    race_counts = {}
    for ally in allies:
        race = get_unit_race(ally)
        race_counts[race] = race_counts.get(race, 0) + 1
    
    # Если команда состоит полностью из своей расы - хорошая мораль
    if len(race_counts) == 1 and unit_race in race_counts:
        return 'good'
    
    # Базовая мораль при смешанном составе
    base_morale = 'good'
    morale_levels = ['awful', 'bad', 'neutral', 'good', 'excellent']
    current_index = morale_levels.index(base_morale)
    
    # Нежить понижает мораль на 1 для любой расы
    if 'undead' in race_counts and race_counts['undead'] > 0:
        current_index -= 1
    
    # Система нетерпимостей: на каждые 3 юнита своей расы приходится 1 нетерпимый → мораль -1
    # Подсчитываем количество юнитов своей расы и других рас
    own_race_count = race_counts.get(unit_race, 0)
    other_races_count = sum(count for race, count in race_counts.items() if race != unit_race)
    
    # Если есть другие расы, проверяем соотношение нетерпимостей
    if other_races_count > 0 and own_race_count > 0:
        # На каждые 3 юнита своей расы приходится 1 нетерпимый → мораль -1
        # Примеры:
        # - 3 свои + 1 другой = 1 на 3 → -1 мораль
        # - 6 свои + 1 другой = 1 на 6 → -1 мораль (есть 1 нетерпимый на 3+ своих)
        # - 6 свои + 2 другие = 2 на 6 = 1 на 3 → -1 мораль
        # - 6 свои + 3 другие = 3 на 6 = 1 на 2 → -2 мораль (3 на 6 = больше чем 1 на 3)
        # - 9 свои + 3 другие = 3 на 9 = 1 на 3 → -1 мораль
        # - 9 свои + 4 другие = 4 на 9 → -2 мораль (4 на 9 = больше чем 1 на 3)
        
        # Вычисляем: сколько групп "3 свои + 1 нетерпимый" можно составить
        # Количество штрафов = ceil(нетерпимых * 3 / свои)
        import math
        if own_race_count >= 3:
            # Для каждых 3 своих может быть 1 нетерпимый без штрафа
            # Если нетерпимых больше - штраф за каждую "лишнюю" группу
            # Количество групп соотношения 1:3 = ceil(нетерпимых * 3 / свои)
            morale_penalty = math.ceil(other_races_count * 3.0 / own_race_count)
        else:
            # Если своих меньше 3, но есть нетерпимые - все равно -1 мораль
            morale_penalty = 1
        
        current_index -= morale_penalty
    
    # Ограничиваем индекс в пределах допустимых значений
    current_index = max(0, min(len(morale_levels) - 1, current_index))
    
    return morale_levels[current_index]


def apply_morale_modifiers(unit):
    """
    Применяет модификаторы морали к юниту.
    :param unit: Объект юнита
    """
    # Базовое значение морали уже установлено через calculate_morale
    # Здесь можно применять дополнительные модификаторы:
    # - от героев (если есть герой с бонусом к морали)
    # - от заклинаний (благословение, проклятие и т.д.)
    # - от артефактов
    
    # Пока что функция пустая, но можно расширить в будущем
    # Например, если у героя есть бонус к морали:
    # if hasattr(unit, 'game_ref') and unit.game_ref:
    #     heroes = [u for u in unit.game_ref.units if isinstance(u, Hero) and u.team == unit.team]
    #     for hero in heroes:
    #         if hasattr(hero, 'morale_bonus'):
    #             # Применяем бонус
    pass