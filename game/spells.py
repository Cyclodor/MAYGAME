from .config import GRID_WIDTH, GRID_HEIGHT
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
import random
import math
class Spell:
    def __init__(self, name, damage, mana_cost, cooldown, target_type='enemy', description='', icon=None, duration=0, school=None):
        self.name = name
        self.damage = damage
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.target_type = target_type
        self.description = description
        self.icon = icon  # строка-идентификатор для отрисовки
        self.duration = duration  # длительность эффекта (если есть)
        self.school = school  # школа магии
    
    def is_debuff(self):
        """Определяет, является ли заклинание дебаффом (может быть отражено сопротивлением магии)"""
        return self.damage == 0 and self.target_type == 'enemy' and self.duration > 0
    
    def check_magic_resist_reflection(self, target, caster=None):
        """Проверяет, отражается ли заклинание сопротивлением магии. Возвращает (отражено, game_ref)"""
        if not self.is_debuff():
            # Боевые заклинания не могут отражаться
            return False, None
        
        if not hasattr(target, 'magic_resist') or target.magic_resist <= 0:
            return False, None
        
        if not caster or not hasattr(caster, 'game_ref'):
            return False, None
        
        game = caster.game_ref
        
        # Проверяем шанс отражения (равен проценту сопротивления магии)
        import random
        reflection_chance = target.magic_resist / 100.0
        if random.random() < reflection_chance:
            # Заклинание отражено!
            return True, game
        
        return False, None

    def can_cast(self, current_mana):
        return self.current_cooldown == 0 and current_mana >= self.mana_cost

    def cast(self):
        self.current_cooldown = self.cooldown

    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class BlessSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Благословение",
            damage=0,
            mana_cost=5,
            cooldown=0,
            target_type='ally',
            description="Увеличивает атаку на 25% на 2 хода",
            icon='bless',
            duration=2,
            school='light'
        )
        self.buff_amount = 25  # процент увеличения атаки
    def apply(self, target, caster=None):
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        # Примечание: buff_amount можно использовать в будущем для настройки силы баффа
        target.apply_attack_buff(turns=turns)
        return True  # Успешное применение

class CurseSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Проклятие",
            damage=0,
            mana_cost=5,
            cooldown=0,
            target_type='enemy',
            description="Уменьшает атаку на 25% на 2 хода",
            icon='curse',
            duration=2,
            school='darkness'
        )
        self.debuff_amount = 25  # процент уменьшения атаки
    def apply(self, target, caster=None):
        # Проверяем отражение сопротивлением магии
        reflected, game = self.check_magic_resist_reflection(target, caster)
        if reflected and game:
            # Анимация отражения заклинания
            try:
                from .graphics import animate_spell_reflection
                from .config import CELL_SIZE
                target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
                caster_px = (caster.x * CELL_SIZE + CELL_SIZE // 2, caster.y * CELL_SIZE + CELL_SIZE // 2) if caster else None
                animate_spell_reflection(game.screen, target_px, caster_px, redraw_callback=game.draw)
            except Exception as e:
                print(f"Ошибка анимации отражения: {e}")
            game.add_event(f"{target.unit_type} отразил заклинание {self.name} благодаря сопротивлению магии!")
            return False  # Заклинание отражено, не применено
        
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        # Примечание: debuff_amount можно использовать в будущем для настройки силы дебаффа
        target.apply_attack_debuff(turns=turns)
        return True  # Успешное применение

# Удалено: заклинание Исцеление выведено из игры

# Удалено: заклинание Щит выведено из игры

class SlowSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Замедление",
            damage=0,
            mana_cost=7,
            cooldown=0,
            target_type='enemy',
            description="Уменьшает инициативу цели на 5 и скорость на 1 на 2 хода.",
            icon='slow',
            duration=2,
            school='earth'
        )
        self.initiative_reduction = 5  # уменьшение инициативы
        self.speed_reduction = 1  # уменьшение скорости
    def apply(self, target, caster=None):
        # Проверяем отражение сопротивлением магии
        reflected, game = self.check_magic_resist_reflection(target, caster)
        if reflected and game:
            # Анимация отражения заклинания
            try:
                from .graphics import animate_spell_reflection
                from .config import CELL_SIZE
                target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
                caster_px = (caster.x * CELL_SIZE + CELL_SIZE // 2, caster.y * CELL_SIZE + CELL_SIZE // 2) if caster else None
                animate_spell_reflection(game.screen, target_px, caster_px, redraw_callback=game.draw)
            except Exception as e:
                print(f"Ошибка анимации отражения: {e}")
            game.add_event(f"{target.unit_type} отразил заклинание {self.name} благодаря сопротивлению магии!")
            return False  # Заклинание отражено, не применено
        
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        if not hasattr(target, 'slow_turns') or target.slow_turns == 0:
            target.base_initiative = getattr(target, 'base_initiative', target.initiative)
            target.initiative = max(1, target.initiative - self.initiative_reduction)
            target.base_speed = getattr(target, 'base_speed', target.speed)
            target.speed = max(1, target.speed - self.speed_reduction)
            target.slow_turns = turns
        else:
            target.slow_turns = turns
        return True  # Успешное применение

class FireArrowSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Огненная стрела",
            damage=20,
            mana_cost=10,
            cooldown=0,
            target_type='enemy',
            description="Наносит 20 урона врагу.",
            icon='firearrow',
            duration=0,
            school='fire'
        )
        self.spell_power_multiplier = 5  # множитель силы магии для урона
    def apply(self, target, caster=None):
        dmg = self.damage
        if caster and hasattr(caster, 'spell_power'):
            dmg += self.spell_power_multiplier * caster.spell_power
        
        # Запоминаем здоровье до урона
        health_before = target.health
        squad_count_before = getattr(target, 'squad_count', 1)
        died = target.take_damage(dmg, attack_type='magical')
        actual_damage = health_before - target.health
        squad_count_after = getattr(target, 'squad_count', 1)
        units_lost = squad_count_before - squad_count_after
        
        if died and hasattr(caster, 'game_ref'):
            game = caster.game_ref
            game.kill_unit(target)
            game.animation_manager.animate_queue_fade(target)
            event_msg = f"Огненная стрела убила {target.unit_type} (урон: {actual_damage})"
            if units_lost > 0:
                event_msg += f", уничтожено {units_lost} юнитов из отряда"
            game.add_event(event_msg)
            game.check_game_over()
        elif hasattr(caster, 'game_ref'):
            game = caster.game_ref
            event_msg = f"Огненная стрела ранила {target.unit_type} (урон: {actual_damage})"
            if units_lost > 0:
                event_msg += f", потеряно {units_lost} юнитов из отряда"
            game.add_event(event_msg)
        
        return True  # Успешное применение

class DispelSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Снятие чар",
            damage=0,
            mana_cost=4,
            cooldown=0,
            target_type='ally',  # может применяться и к врагу (обрабатывается в core)
            description="Снимает все положительные и отрицательные эффекты с юнита.",
            icon='dispel',
            duration=0,
            school='water'
        )
    def apply(self, target, caster=None):
        # Сбросить все эффекты
        if hasattr(target, 'attack_buff_turns'):
            target.attack_buff_turns = 0
        if hasattr(target, 'attack_debuff_turns'):
            target.attack_debuff_turns = 0
        # Снимаем бонус Каменной кожи, если он был применён как постоянный
        if hasattr(target, 'stone_skin_bonus') and target.stone_skin_bonus:
            target.defense = max(0, target.defense - target.stone_skin_bonus)
            target.stone_skin_bonus = 0
        if hasattr(target, 'stone_skin_turns'):
            target.stone_skin_turns = 0
        if hasattr(target, 'curse_turns'):
            target.curse_turns = 0
        if hasattr(target, 'slow_turns'):
            target.slow_turns = 0
        if hasattr(target, 'forget_turns'):
            target.forget_turns = 0
            # Также сбрасываем флаг пропуска хода и разблокируем действия
            if hasattr(target, 'skipped_turn_due_to_forget'):
                target.skipped_turn_due_to_forget = False
            # Разблокируем действия юнита если он был заблокирован забвением
            if hasattr(target, 'has_moved') and hasattr(target, 'has_attacked'):
                target.has_moved = False
                target.has_attacked = False
            if hasattr(target, 'move_points_left') and hasattr(target, 'speed'):
                target.move_points_left = target.speed
        # Снимаем огненный щит
        if hasattr(target, 'fire_shield_turns'):
            target.fire_shield_turns = 0
        if hasattr(target, 'fire_shield_damage'):
            target.fire_shield_damage = 0
        if hasattr(target, 'fire_shield_pct'):
            target.fire_shield_pct = 0.0
        # Снимаем ледяной щит
        if hasattr(target, 'ice_shield_turns'):
            target.ice_shield_turns = 0
            # Снимаем бонусы ледяного щита
            if hasattr(target, 'ice_shield_phys_bonus'):
                target.phys_defense -= getattr(target, 'ice_shield_phys_bonus', 0)
                target.ice_shield_phys_bonus = 0
            if hasattr(target, 'ice_shield_hp_bonus'):
                target.ice_shield_hp_bonus = 0
            if hasattr(target, 'ice_shield_absorption'):
                target.ice_shield_absorption = 0
        # Снимаем обычное ускорение (это не руна скорости)
        if hasattr(target, 'haste_turns'):
            target.haste_turns = 0
        # Снимаем контрудар (заклинание)
        if hasattr(target, 'counterstrike_turns'):
            target.counterstrike_turns = 0
        # Снимаем слабость
        if hasattr(target, 'weakness_turns'):
            target.weakness_turns = 0
            # Восстанавливаем атаки
            if hasattr(target, 'weakness_phys_penalty'):
                target.phys_attack += getattr(target, 'weakness_phys_penalty', 0)
                target.weakness_phys_penalty = 0
            if hasattr(target, 'weakness_magic_penalty'):
                target.magic_attack += getattr(target, 'weakness_magic_penalty', 0)
                target.weakness_magic_penalty = 0
        # Снимаем ослепление
        if hasattr(target, 'blindness_turns'):
            target.blindness_turns = 0
            target.blindness_active = False
        # Снимаем молитву
        if hasattr(target, 'prayer_turns'):
            target.prayer_turns = 0
            if hasattr(target, 'prayer_applied') and target.prayer_applied:
                # Восстанавливаем значения атаки и защиты
                if hasattr(target, 'attack_type') and target.attack_type == 'physical':
                    target.phys_attack = max(0, target.phys_attack - 2)
                else:
                    target.magic_attack = max(0, target.magic_attack - 2)
                target.phys_defense = max(0, target.phys_defense - 2)
                target.magic_defense = max(0, target.magic_defense - 2)
                target.speed = max(1, target.speed - 2)
                target.initiative = max(1, target.initiative - 2)
                target.prayer_applied = False
        # Снимаем точность
        if hasattr(target, 'accuracy_turns'):
            target.accuracy_turns = 0
            target.accuracy_active = False
        # Пересчитываем скорость и инициативу от базовых значений
        if hasattr(target, 'initiative') and hasattr(target, 'base_initiative'):
            target.initiative = getattr(target, 'base_initiative', target.initiative)
        if hasattr(target, 'speed') and hasattr(target, 'base_speed'):
            target.speed = getattr(target, 'base_speed', target.speed)
        # Особенности школы рун: эффекты рун не снимаются — применяем их заново, если активны
        # намеренно НЕ трогаем rune_shield_turns / rune_haste_turns и их бонусы
        if getattr(target, 'rune_haste_turns', 0) > 0:
            if hasattr(target, 'speed'):
                target.speed += 2
            if hasattr(target, 'initiative'):
                target.initiative += 5
        # Немедленное применение изменений в текущем ходу
        if hasattr(target, 'move_points_left'):
            try:
                target.move_points_left = target.speed
            except Exception:
                pass
        if hasattr(target, 'game_ref') and target.game_ref:
            try:
                target.game_ref.prepare_initiative_queue()
            except Exception:
                pass
        return True  # Успешное применение

class HasteSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Ускорение",
            damage=0,
            mana_cost=7,
            cooldown=0,
            target_type='ally',
            description="Увеличивает скорость на 2 и инициативу на 5 на 2 хода.",
            icon='haste',
            duration=2,
            school='air'
        )
        self.speed_bonus = 2  # увеличение скорости
        self.initiative_bonus = 5  # увеличение инициативы
    def apply(self, target, caster=None):
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        # Используем общие поля, как у рунической спешки, чтобы логика снятия/окончания работала одинаково
        if not hasattr(target, 'haste_turns') or target.haste_turns == 0:
            target.base_speed = getattr(target, 'base_speed', target.speed)
            target.speed += self.speed_bonus
            target.base_initiative = getattr(target, 'base_initiative', target.initiative)
            target.initiative += self.initiative_bonus
            target.haste_turns = turns
        else:
            target.haste_turns = turns
        # Сделать эффект немедленным: обновляем очки перемещения
        if hasattr(target, 'move_points_left'):
            try:
                target.move_points_left = target.speed
            except Exception:
                pass
        # Обновляем инициативную очередь сразу, чтобы эффект был заметен в порядке ходов
        if hasattr(target, 'game_ref') and target.game_ref:
            target.game_ref.prepare_initiative_queue()
        return True  # Успешное применение

class RuneShieldSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Руна защиты",
            damage=0,
            mana_cost=7,
            cooldown=0,
            target_type='ally',
            description="Дает +15 к физической и магической защите на 2 хода.",
            icon='rune_shield',
            duration=2,
            school='rune'
        )
        self.defense_bonus = 15  # бонус к обоим типам защиты
    def apply(self, target, caster=None):
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        if getattr(target, 'rune_shield_turns', 0) == 0:
            # Увеличиваем оба типа защиты
            target.phys_defense += self.defense_bonus
            target.magic_defense += self.defense_bonus
            target.rune_shield_phys_bonus = self.defense_bonus
            target.rune_shield_magic_bonus = self.defense_bonus
        target.rune_shield_turns = turns
        return True  # Успешное применение

class RuneHasteSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Руна скорости",
            damage=0,
            mana_cost=7,
            cooldown=0,
            target_type='ally',
            description="Увеличивает скорость на 2 и инициативу на 5 на 2 хода.",
            icon='rune_haste',
            duration=2,
            school='rune'
        )
        self.speed_bonus = 2  # увеличение скорости
        self.initiative_bonus = 5  # увеличение инициативы
    def apply(self, target, caster=None):
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        if not hasattr(target, 'rune_haste_turns') or target.rune_haste_turns == 0:
            target.base_speed = getattr(target, 'base_speed', target.speed)
            target.speed += self.speed_bonus
            target.base_initiative = getattr(target, 'base_initiative', target.initiative)
            target.initiative += self.initiative_bonus
            target.rune_haste_turns = turns
        else:
            target.rune_haste_turns = turns
        # Сделать эффект немедленным: обновляем очки перемещения
        if hasattr(target, 'move_points_left'):
            try:
                target.move_points_left = target.speed
            except Exception:
                pass
        # Обновляем инициативную очередь сразу, чтобы эффект был заметен в порядке ходов
        if hasattr(target, 'game_ref') and target.game_ref:
            target.game_ref.prepare_initiative_queue()
        return True  # Успешное применение

class ForgetSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Забвение",
            damage=0,
            mana_cost=8,
            cooldown=0,
            target_type='enemy',
            description="Цель пропускает ход (длительность зависит от силы магии).",
            icon='forget',
            duration=1,
            school='darkness'
        )
    def apply(self, target, caster=None):
        # Проверяем отражение сопротивлением магии
        reflected, game = self.check_magic_resist_reflection(target, caster)
        if reflected and game:
            # Анимация отражения заклинания
            try:
                from .graphics import animate_spell_reflection
                from .config import CELL_SIZE
                target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
                caster_px = (caster.x * CELL_SIZE + CELL_SIZE // 2, caster.y * CELL_SIZE + CELL_SIZE // 2) if caster else None
                animate_spell_reflection(game.screen, target_px, caster_px, redraw_callback=game.draw)
            except Exception as e:
                print(f"Ошибка анимации отражения: {e}")
            game.add_event(f"{target.unit_type} отразил заклинание {self.name} благодаря сопротивлению магии!")
            return False  # Заклинание отражено, не применено
        
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        target.forget_turns = turns
        
        # Если это текущий активный юнит - блокируем его действия немедленно
        if hasattr(caster, 'game_ref') and caster.game_ref:
            game = caster.game_ref
            # Если цель - текущий активный юнит, блокируем его ход
            if hasattr(game, 'turn_queue') and game.turn_queue and game.turn_queue[0] == target:
                target.has_moved = True
                target.has_attacked = True
                target.move_points_left = 0
        
        return True  # Успешное применение

class FrostRingSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Кольцо холода",
            damage=18,
            mana_cost=12,
            cooldown=0,
            target_type='area',
            description="Бьёт по кругу радиусом 1 клетка вокруг выбранной клетки (центр не бьёт).",
            icon='frost_ring',
            duration=0,
            school='water'
        )
        self.spell_power_multiplier = 5  # множитель силы магии для урона
    def apply(self, center, caster=None):
        # center — (x, y), game_ref должен быть у caster
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        game = caster.game_ref
        x0, y0 = center
        
        # Собираем всех пораженных юнитов
        affected_units = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                tx, ty = x0 + dx, y0 + dy
                for unit in list(game.units):
                    if unit.x == tx and unit.y == ty and unit.team != caster.team:
                        if unit not in affected_units:
                            affected_units.append(unit)
        
        # Наносим урон всем пораженным юнитам
        for unit in affected_units:
            dmg = self.damage
            if caster and hasattr(caster, 'spell_power'):
                dmg += self.spell_power_multiplier * caster.spell_power
            
            health_before = unit.health
            unit_died = unit.take_damage(dmg, attack_type='magical')
            actual_damage = health_before - unit.health
            
            if unit_died:
                game.kill_unit(unit)
                game.animation_manager.animate_queue_fade(unit)
                game.add_event(f"Кольцо холода заморозило {unit.unit_type} (урон: {actual_damage})")
                game.check_game_over()
            else:
                game.add_event(f"Кольцо холода ранило {unit.unit_type} (урон: {actual_damage})")
        
        return True  # Успешное применение

class RaiseDeadSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Призыв скелета",
            damage=0,
            mana_cost=10,
            cooldown=0,
            target_type='area',
            description="Призывает скелета на выбранной пустой клетке.",
            # Используем идентификатор иконки, ожидаемый интерфейсом
            icon='raise_dead',
            duration=0,
            school='darkness'
        )
    
    def apply(self, center, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        game = caster.game_ref
        x, y = center
        # Проверка границ и занятости клетки
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return False
        if any(u.x == x and u.y == y for u in game.units):
            game.add_event("Клетка занята!")
            return False
        # Красивая анимация призыва: темные частицы, руны, всплеск и подъем скелета из земли
        try:
            import pygame, random, math
            from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
            cx = x * CELL_SIZE + CELL_SIZE // 2
            cy = y * CELL_SIZE + CELL_SIZE // 2
            cell_rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)

            # Этап 1 (теперь первым): рунный всплеск и мерцание
            for step in range(60):  # Увеличено до 60 кадров для максимальной плавности
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                radius = 10 + step * 3
                pygame.draw.circle(s, (150, 0, 180, 90), (cx, cy), radius, 3)
                pygame.draw.circle(s, (220, 120, 255, 80), (cx, cy), max(2, radius-6), 2)
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(8)  # Уменьшена задержка для плавности

            # Этап 2 (теперь вторым): темные частицы вращаются и стягиваются к центру
            particles = []  # [px, py, ang, rad, speed]
            for _ in range(100):  # Увеличено количество частиц до 100
                ang = random.random() * math.tau
                rad = random.randint(10, CELL_SIZE//2 + 8)
                speed = random.uniform(0.6, 1.2)
                px = cx + int(math.cos(ang) * rad)
                py = cy + int(math.sin(ang) * rad)
                particles.append([px, py, ang, rad, speed])
            for step in range(100):  # Увеличено до 100 кадров для максимальной плавности
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                # Тёмный вихрь
                for p in particles:
                    p[2] += 0.25  # вращение
                    p[3] = max(2, p[3] - p[4])  # стягивание к центру
                    p[0] = cx + int(math.cos(p[2]) * p[3])
                    p[1] = cy + int(math.sin(p[2]) * p[3])
                    pygame.draw.circle(s, (40, 0, 60, 170), (int(p[0]), int(p[1])), 3)
                    pygame.draw.circle(s, (120, 0, 120, 110), (int(p[0]), int(p[1])), 1)
                # Трещины земли
                crack = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                for i in range(6):
                    angle = random.random() * math.tau
                    length = random.randint(8, CELL_SIZE//2)
                    ex = CELL_SIZE//2 + int(math.cos(angle) * length)
                    ey = CELL_SIZE//2 + int(math.sin(angle) * length)
                    pygame.draw.line(crack, (60, 40, 30, 200), (CELL_SIZE//2, CELL_SIZE//2), (ex, ey), 2)
                s.blit(crack, (x*CELL_SIZE, y*CELL_SIZE))
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(8)  # Уменьшена задержка для плавности

            # Этап 3: призрачное свечение и всплески энергии в центре
            for step in range(80):  # Увеличено до 80 кадров для максимальной плавности
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pulse_r = 8 + step * 2
                pulse_a = max(0, 180 - step * 10)
                pygame.draw.circle(s, (120, 200, 255, pulse_a), (cx, cy), pulse_r, 3)
                pygame.draw.circle(s, (70, 150, 220, max(0, pulse_a-40)), (cx, cy), max(2, pulse_r-5), 2)
                # Призрачные огни
                for i in range(6):
                    ang = (step*0.4 + i) * 0.8
                    rr = 10 + step
                    fx = cx + int(math.cos(ang) * rr)
                    fy = cy + int(math.sin(ang) * rr)
                    pygame.draw.circle(s, (80, 180, 255, 90), (fx, fy), 4)
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(8)  # Уменьшена задержка для плавности
        except Exception:
            pass
        # Призыв скелета команды кастера
        from .units import Skeleton
        skel = Skeleton(x, y, caster.team)
        skel.game_ref = game
        game.units.append(skel)
        # Добавляем в очередь хода
        if hasattr(game, 'turn_queue') and hasattr(game, '_round_delimiter'):
            try:
                delim_index = game.turn_queue.index(game._round_delimiter)
                game.turn_queue.insert(delim_index, skel)
            except (ValueError, AttributeError):
                game.turn_queue.append(skel)
        return True  # Успешное применение

class UndeadHealSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Поднятие мёртвых",
            damage=0,
            mana_cost=8,
            cooldown=0,
            target_type='both',  # может применяться и на живых, и на мертвых нежить
            description="Воскрешает павшую нежить или лечит живую. Работает только на нежить.",
            icon='raise_undead',
            duration=0,
            school='darkness'
        )
        self.heal_amount = 25  # базовое лечение
        self.spell_power_multiplier = 5  # множитель силы магии

    def apply(self, center, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        game = caster.game_ref
        x, y = center
        
        # Проверка границ
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return False
        
        # Вычисляем количество лечения: базовое + сила магии * 5
        heal = self.heal_amount
        if caster and hasattr(caster, 'spell_power'):
            heal += self.spell_power_multiplier * caster.spell_power
        
        # Сначала проверяем, есть ли живой юнит на клетке
        living_unit = None
        corpse_found = None
        for u in game.units:
            if u.x == x and u.y == y:
                living_unit = u
                break
        # Проверяем трупы нежити
        for corpse in game.corpses:
            if corpse['x'] == x and corpse['y'] == y:
                if corpse['team'] == 'undead':
                    corpse_found = corpse
                break
        
        # Если есть живой юнит - лечим/воскрешаем его
        if living_unit:
            # Проверяем, что это нежить
            if living_unit.team != 'undead':
                game.add_event("Поднятие мёртвых действует только на нежить!")
                return False
        
        # Система отрядов: воскрешение может восстановить мертвых юнитов в отряде нежити
            if hasattr(living_unit, 'squad_count') and hasattr(living_unit, 'unit_hp') and living_unit.unit_hp is not None:
            # Проверяем, можем ли воскресить мертвых или вылечить раненого
                base_squad = getattr(living_unit, 'base_squad_count', None)
                if base_squad is None or base_squad <= living_unit.squad_count:
                    # Если base_squad_count не установлен, пытаемся определить из max_health
                    if living_unit.unit_hp > 0:
                        calculated_base = living_unit.max_health // living_unit.unit_hp
                        if calculated_base > 0:
                            base_squad = max(calculated_base, living_unit.squad_count)
                        else:
                            base_squad = max(living_unit.squad_count, 1)
                    else:
                        base_squad = max(living_unit.squad_count, 1)
                
                # Всегда сохраняем base_squad_count если он был вычислен
                if not hasattr(living_unit, 'base_squad_count') or living_unit.base_squad_count < base_squad:
                    living_unit.base_squad_count = base_squad
                
                max_possible_units = base_squad
                dead_units = max_possible_units - living_unit.squad_count
                
                if dead_units > 0 and living_unit.unit_hp > 0:
                    # Логика частичного воскрешения: сначала лечим текущего до полного, потом воскрешаем частично (даже если лечения недостаточно)
                    remaining_heal = heal
                    
                    # Шаг 1: Если текущий юнит ранен, сначала лечим его до полного здоровья
                    if living_unit.current_unit_hp < living_unit.unit_hp:
                        hp_needed_to_full = living_unit.unit_hp - living_unit.current_unit_hp
                        if remaining_heal >= hp_needed_to_full:
                            remaining_heal -= hp_needed_to_full
                            living_unit.current_unit_hp = living_unit.unit_hp
                        else:
                            # Если лечения недостаточно для полного лечения, просто лечим сколько можем
                            living_unit.current_unit_hp += remaining_heal
                            remaining_heal = 0
                        # Обновляем общее здоровье отряда
                        living_unit.health = (living_unit.squad_count - 1) * living_unit.unit_hp + living_unit.current_unit_hp
                    
                    # Шаг 2: Воскрешаем мертвых юнитов частично (даже если лечения недостаточно для полного воскрешения)
                    squad_count_before_heal = living_unit.squad_count
                    if remaining_heal > 0 and dead_units > 0:
                        # Воскрешаем столько юнитов, сколько можем полностью (если есть достаточно лечения)
                        full_resurrect_count = min(dead_units, remaining_heal // living_unit.unit_hp)
                        if full_resurrect_count > 0:
                            living_unit.squad_count += full_resurrect_count
                            remaining_heal -= full_resurrect_count * living_unit.unit_hp
                            event_msg = f"Воскрешено {full_resurrect_count} нежити в отряде {living_unit.unit_type.capitalize()}! (отряд: {squad_count_before_heal} -> {living_unit.squad_count}/{max_possible_units})"
                            game.add_event(event_msg)
                        
                        # Если осталось лечение и еще есть мертвые юниты - воскрешаем частично последнего
                        if remaining_heal > 0 and living_unit.squad_count < max_possible_units:
                            # Воскрешаем еще одного юнита, но с частичным HP
                            living_unit.squad_count += 1
                            # Текущий юнит становится тем, кто был воскрешен с частичным HP
                            living_unit.current_unit_hp = remaining_heal  # Новый юнит имеет только оставшееся лечение
                            remaining_heal = 0
                            event_msg = f"Воскрешена нежить {living_unit.unit_type.capitalize()} с частичным здоровьем! (отряд: {living_unit.squad_count - 1} -> {living_unit.squad_count}/{max_possible_units}, HP: {living_unit.current_unit_hp}/{living_unit.unit_hp})"
                            game.add_event(event_msg)
                    elif remaining_heal > 0 and dead_units > 0:
                        # Если лечения недостаточно даже для одного полного воскрешения, воскрешаем частично
                        living_unit.squad_count += 1
                        living_unit.current_unit_hp = remaining_heal
                        remaining_heal = 0
                        event_msg = f"Воскрешена нежить {living_unit.unit_type.capitalize()} с частичным здоровьем! (отряд: {squad_count_before_heal} -> {living_unit.squad_count}/{max_possible_units}, HP: {living_unit.current_unit_hp}/{living_unit.unit_hp})"
                        game.add_event(event_msg)
                    
                    # Обновляем структуру отряда
                    if living_unit.squad_count > squad_count_before_heal:
                        living_unit.base_squad_count = max_possible_units
                        living_unit.max_health = max_possible_units * living_unit.unit_hp
                        living_unit.health = (living_unit.squad_count - 1) * living_unit.unit_hp + living_unit.current_unit_hp
                    
                    # Анимация поднятия мёртвых
                    try:
                        game.animate_undead_heal_cast(living_unit)
                    except:
                        pass
                    
                    # Если воскресили хотя бы одного юнита (полностью или частично) - успех
                    if living_unit.squad_count > squad_count_before_heal:
                        return True
                    elif remaining_heal == 0:
                        # Все лечение потрачено на лечение текущего юнита (если был ранен)
                        return True
                    else:
                        # Недостаточно силы даже для частичного воскрешения
                        # Но если полечили текущего - это тоже успех
                        if living_unit.current_unit_hp >= living_unit.unit_hp:
                            game.add_event(f"{living_unit.unit_type.capitalize()} уже полностью здоров, но недостаточно лечения для воскрешения.")
                        return False
                else:
                    # unit_hp == 0 или нет мертвых юнитов, просто лечим текущего
                    if living_unit.current_unit_hp < living_unit.unit_hp:
                        health_before = living_unit.current_unit_hp
                        living_unit.current_unit_hp = min(living_unit.unit_hp, living_unit.current_unit_hp + heal)
                        actual_heal = living_unit.current_unit_hp - health_before
                        living_unit.health = (living_unit.squad_count - 1) * living_unit.unit_hp + living_unit.current_unit_hp
                        if actual_heal > 0:
                            game.add_event(f"Нежить {living_unit.unit_type.capitalize()} исцелена на {actual_heal} HP!")
                        # Анимация поднятия мёртвых
                        try:
                            game.animate_undead_heal_cast(living_unit)
                        except:
                            pass
                        return True
                    else:
                        game.add_event(f"{living_unit.unit_type.capitalize()} уже полностью здоров!")
                        return False
        else:
            # Старая система (без отрядов)
                # Проверяем, что юнит ранен
                if living_unit.health >= living_unit.max_health:
                    game.add_event(f"{living_unit.unit_type.capitalize()} уже полностью здоров!")
                    return False
                
                # Лечим
                health_before = living_unit.health
                living_unit.health = min(living_unit.max_health, living_unit.health + heal)
                actual_heal = living_unit.health - health_before
                
                # Анимация поднятия мёртвых
                try:
                    game.animate_undead_heal_cast(living_unit)
                except:
                    pass
                
                game.add_event(f"{living_unit.unit_type.capitalize()} исцелен на {actual_heal} HP!")
                return True
        
        # Если живого юнита нет, ищем труп нежити для воскрешения
        if corpse_found:
            # Воскрешаем труп нежити с частичным воскрешением отряда
            unit_class = corpse_found.get('unit_class')
            if unit_class:
                try:
                    # Создаем нового юнита того же класса
                    new_unit = unit_class(corpse_found['x'], corpse_found['y'], 'undead')
                    new_unit.game_ref = game
                    # Инициализируем систему отрядов если нужно
                    game._set_default_squad_count(new_unit)
                    
                    # Применяем частичное воскрешение отряда на основе лечения
                    if hasattr(new_unit, 'squad_count') and hasattr(new_unit, 'unit_hp') and new_unit.unit_hp is not None:
                        base_squad = getattr(new_unit, 'base_squad_count', new_unit.squad_count)
                        max_possible_units = base_squad
                        
                        # Воскрешаем столько юнитов, сколько можем полностью
                        remaining_heal = heal
                        full_resurrect_count = min(max_possible_units, remaining_heal // new_unit.unit_hp)
                        
                        if full_resurrect_count > 0:
                            new_unit.squad_count = full_resurrect_count
                            remaining_heal -= full_resurrect_count * new_unit.unit_hp
                            
                            # Если осталось лечение - даем текущему юниту частичное HP
                            if remaining_heal > 0:
                                new_unit.current_unit_hp = min(new_unit.unit_hp, remaining_heal)
                                remaining_heal = 0
                            else:
                                new_unit.current_unit_hp = new_unit.unit_hp
                            
                            new_unit.base_squad_count = max_possible_units
                            new_unit.max_health = max_possible_units * new_unit.unit_hp
                            new_unit.health = (new_unit.squad_count - 1) * new_unit.unit_hp + new_unit.current_unit_hp
                            
                            if full_resurrect_count < max_possible_units:
                                event_msg = f"Воскрешена нежить {new_unit.unit_type.capitalize()} с частичным отрядом! (отряд: {new_unit.squad_count}/{max_possible_units}, HP: {new_unit.current_unit_hp}/{new_unit.unit_hp})"
                            else:
                                event_msg = f"Воскрешена нежить {new_unit.unit_type.capitalize()}! (отряд: {new_unit.squad_count}/{max_possible_units})"
                        else:
                            # Недостаточно лечения даже для одного юнита - воскрешаем частично
                            new_unit.squad_count = 1
                            new_unit.current_unit_hp = remaining_heal
                            new_unit.base_squad_count = max_possible_units
                            new_unit.max_health = max_possible_units * new_unit.unit_hp
                            new_unit.health = new_unit.current_unit_hp
                            event_msg = f"Воскрешена нежить {new_unit.unit_type.capitalize()} с частичным отрядом! (отряд: {new_unit.squad_count}/{max_possible_units}, HP: {new_unit.current_unit_hp}/{new_unit.unit_hp})"
                    else:
                        # Старая система (без отрядов)
                        new_unit.health = min(new_unit.max_health, heal)
                        event_msg = f"Герой воскресил {new_unit.unit_type}!"
                    
                    # Добавляем в игру
                    game.units.append(new_unit)
                    # Добавляем в очередь хода
                    if hasattr(game, 'turn_queue') and hasattr(game, '_round_delimiter'):
                        try:
                            delim_index = game.turn_queue.index(game._round_delimiter)
                            game.turn_queue.insert(delim_index, new_unit)
                        except (ValueError, AttributeError):
                            game.turn_queue.append(new_unit)
                    # Удаляем труп
                    game.corpses.remove(corpse_found)
                    # Анимация
                    try:
                        game.animate_undead_heal_cast(new_unit)
                    except:
                        pass
                    # Сообщение
                    game.add_event(event_msg)
                    return True
                except Exception as e:
                    game.add_event(f"Ошибка при воскрешении: {e}")
                    return False
            else:
                game.add_event(f"Не удалось определить класс нежити из трупа")
                return False
        else:
            # Нет ни живого юнита, ни трупа
            return False

class FireballSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Огненный шар",
            damage=25,
            mana_cost=12,
            cooldown=0,
            target_type='area',
            description="Сбрасывает с неба пылающий шар, бьёт по зоне 3x3 клетки.",
            icon='fireball',
            duration=0,
            school='fire'
        )
        self.spell_power_multiplier = 5  # множитель силы магии для урона
    
    def apply(self, center, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        game = caster.game_ref
        x, y = center
        
        # Применение урона по зоне 3x3
        affected_units = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                tx, ty = x + dx, y + dy
                if not (0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT):
                    continue
                for unit in list(game.units):
                    if unit.x == tx and unit.y == ty and unit.team != caster.team:
                        # Пропускаем героев
                        if hasattr(unit, 'unit_type') and unit.unit_type == 'hero':
                            continue
                        if unit not in affected_units:
                            affected_units.append(unit)
        
        # Наносим урон всем пораженным юнитам
        for unit in affected_units:
            dmg = self.damage
            if caster and hasattr(caster, 'spell_power'):
                dmg += self.spell_power_multiplier * caster.spell_power
            
            health_before = unit.health
            squad_count_before = getattr(unit, 'squad_count', 1)
            unit_died = unit.take_damage(dmg, attack_type='magical')
            actual_damage = health_before - unit.health
            squad_count_after = getattr(unit, 'squad_count', 1)
            units_lost = squad_count_before - squad_count_after
            
            if unit_died:
                game.kill_unit(unit)
                game.animation_manager.animate_queue_fade(unit)
                event_msg = f"Огненный шар убил {unit.unit_type} (урон: {actual_damage})"
                if units_lost > 0:
                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                game.add_event(event_msg)
                game.check_game_over()
            else:
                event_msg = f"Огненный шар поджёг {unit.unit_type} (урон: {actual_damage})"
                if units_lost > 0:
                    event_msg += f", потеряно {units_lost} юнитов из отряда"
                game.add_event(event_msg)
        
        return True  # Успешное применение

class StoneSkinSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Каменная кожа",
            damage=0,
            mana_cost=8,
            cooldown=0,
            target_type='ally',
            description="Повышает защиту на 15% + знание героя%.",
            icon='stone_skin',
            duration=0,
            school='earth'
        )
        self.base_percent = 15  # базовый процент увеличения защиты
    def apply(self, target, caster=None):
        if not target:
            return False
        knowledge = getattr(caster, 'knowledge', 0) if caster else 0
        percent = (self.base_percent / 100.0) + knowledge / 100.0
        # Повышаем обе защиты
        phys_bonus = int(max(1, target.phys_defense * percent))
        magic_bonus = int(max(1, target.magic_defense * percent))
        target.phys_defense += phys_bonus
        target.magic_defense += magic_bonus
        target.stone_skin_phys_bonus = phys_bonus
        target.stone_skin_magic_bonus = magic_bonus
        # Длительность: базово 2 + сила магии героя
        turns = 2 + (getattr(caster, 'spell_power', 0) if caster else 0)
        target.stone_skin_turns = turns
        return True  # Успешное применение

class FireShieldSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Огненный щит",
            damage=0,
            mana_cost=8,
            cooldown=0,
            target_type='ally',
            description="Накладывает огненный щит на 2 хода. При атаке щит наносит ответный урон.",
            icon='fire_shield',
            duration=2,
            school='fire'
        )

    def apply(self, target, caster=None):
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        # Бафф: процент отражения урона
        target.fire_shield_turns = turns
        # Сохраняем силу магии кастера для расчета урона
        target.fire_shield_spell_power = getattr(caster, 'spell_power', 0) if caster else 0
        return True  # Успешное применение

class ResurrectionSpell(Spell):
    """Заклинание света: Воскрешение - воскрешает мертвых союзников (кроме нежити) или лечит живых"""
    def __init__(self):
        super().__init__(
            name="Воскрешение",
            damage=0,
            mana_cost=12,
            cooldown=0,
            target_type='both',  # может применяться и на живых, и на мертвых
            description="Воскрешает павшего союзника или лечит живого. Не работает на нежить.",
            icon='resurrection',
            duration=0,
            school='light'
        )
        # Базовое количество HP для лечения/воскрешения
        self.heal_amount = 50
    
    def apply(self, center, caster=None):
        # Импортируем модуль отладки
        try:
            import sys
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, os.path.join(project_root, 'debug', 'resurrection'))
            import resurrection_debug as debug
            debug.log_spell_cast(caster, self, center, has_target=False)
        except:
            pass
        
        if not caster or not hasattr(caster, 'game_ref'):
            try:
                debug.log_result(False, "Нет кастера или game_ref")
            except:
                pass
            return False
        game = caster.game_ref
        x, y = center
        
        # Проверка границ
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            try:
                debug.log_result(False, "Выход за границы")
            except:
                pass
            return False
        
        # Вычисляем количество лечения: базовое + сила магии * 10
        heal = self.heal_amount
        if caster and hasattr(caster, 'spell_power'):
            heal += caster.spell_power * 10
        
        # Сначала проверяем, есть ли живой юнит на клетке
        living_unit = None
        corpse_found = None
        for u in game.units:
            if u.x == x and u.y == y:
                living_unit = u
                break
        # Проверяем трупы
        for corpse in game.corpses:
            if corpse['x'] == x and corpse['y'] == y:
                if corpse['team'] != 'undead':
                    corpse_found = corpse
                break
        
        try:
            debug.log_spell_check(caster, self, center, living_unit, corpse_found)
        except:
            pass
        
        # Если есть живой юнит - лечим/воскрешаем его
        if living_unit:
            # Не лечим нежить
            if living_unit.team == 'undead':
                game.add_event("Воскрешение не действует на нежить!")
                return False
            
            # Система отрядов: воскрешение может восстановить мертвых юнитов в отряде
            if hasattr(living_unit, 'squad_count') and hasattr(living_unit, 'unit_hp') and living_unit.unit_hp is not None:
                # Проверяем, можем ли воскресить мертвых или вылечить раненого
                base_squad = getattr(living_unit, 'base_squad_count', None)
                if base_squad is None or base_squad <= living_unit.squad_count:
                    # Если base_squad_count не установлен, пытаемся определить из max_health
                    # max_health должно быть base_squad_count * unit_hp
                    if living_unit.unit_hp > 0:
                        # Пытаемся определить из max_health
                        calculated_base = living_unit.max_health // living_unit.unit_hp
                        if calculated_base > 0:
                            base_squad = max(calculated_base, living_unit.squad_count)
                        else:
                            # Если не удалось определить, используем текущий squad_count или значение по умолчанию
                            base_squad = max(living_unit.squad_count, 1)
                    else:
                        base_squad = max(living_unit.squad_count, 1)
                
                # Всегда сохраняем base_squad_count если он был вычислен
                if not hasattr(living_unit, 'base_squad_count') or living_unit.base_squad_count < base_squad:
                    living_unit.base_squad_count = base_squad
                
                max_possible_units = base_squad
                dead_units = max_possible_units - living_unit.squad_count
                
                if dead_units > 0 and living_unit.unit_hp > 0:
                    # Логика частичного воскрешения: сначала лечим текущего до полного, потом воскрешаем частично (даже если лечения недостаточно)
                    remaining_heal = heal
                    
                    # Шаг 1: Если текущий юнит ранен, сначала лечим его до полного здоровья
                    if living_unit.current_unit_hp < living_unit.unit_hp:
                        hp_needed_to_full = living_unit.unit_hp - living_unit.current_unit_hp
                        if remaining_heal >= hp_needed_to_full:
                            remaining_heal -= hp_needed_to_full
                            living_unit.current_unit_hp = living_unit.unit_hp
                        else:
                            # Если лечения недостаточно для полного лечения, просто лечим сколько можем
                            living_unit.current_unit_hp += remaining_heal
                            remaining_heal = 0
                        # Обновляем общее здоровье отряда
                        living_unit.health = (living_unit.squad_count - 1) * living_unit.unit_hp + living_unit.current_unit_hp
                    
                    # Шаг 2: Воскрешаем мертвых юнитов частично (даже если лечения недостаточно для полного воскрешения)
                    squad_count_before_heal = living_unit.squad_count
                    if remaining_heal > 0 and dead_units > 0:
                        # Воскрешаем столько юнитов, сколько можем полностью (если есть достаточно лечения)
                        full_resurrect_count = min(dead_units, remaining_heal // living_unit.unit_hp)
                        if full_resurrect_count > 0:
                            living_unit.squad_count += full_resurrect_count
                            remaining_heal -= full_resurrect_count * living_unit.unit_hp
                            event_msg = f"Воскрешено {full_resurrect_count} юнитов в отряде {living_unit.unit_type.capitalize()}! (отряд: {squad_count_before_heal} -> {living_unit.squad_count}/{max_possible_units})"
                            game.add_event(event_msg)
                        
                        # Если осталось лечение и еще есть мертвые юниты - воскрешаем частично последнего
                        if remaining_heal > 0 and living_unit.squad_count < max_possible_units:
                            # Воскрешаем еще одного юнита, но с частичным HP
                            living_unit.squad_count += 1
                            # Текущий юнит становится тем, кто был воскрешен с частичным HP
                            living_unit.current_unit_hp = remaining_heal  # Новый юнит имеет только оставшееся лечение
                            remaining_heal = 0
                            event_msg = f"Воскрешен {living_unit.unit_type.capitalize()} с частичным здоровьем! (отряд: {living_unit.squad_count - 1} -> {living_unit.squad_count}/{max_possible_units}, HP: {living_unit.current_unit_hp}/{living_unit.unit_hp})"
                            game.add_event(event_msg)
                    elif remaining_heal > 0 and dead_units > 0:
                        # Если лечения недостаточно даже для одного полного воскрешения, воскрешаем частично
                        living_unit.squad_count += 1
                        living_unit.current_unit_hp = remaining_heal
                        remaining_heal = 0
                        event_msg = f"Воскрешен {living_unit.unit_type.capitalize()} с частичным здоровьем! (отряд: {squad_count_before_heal} -> {living_unit.squad_count}/{max_possible_units}, HP: {living_unit.current_unit_hp}/{living_unit.unit_hp})"
                        game.add_event(event_msg)
                    
                    # Обновляем структуру отряда
                    if living_unit.squad_count > squad_count_before_heal:
                        living_unit.base_squad_count = max_possible_units
                        living_unit.max_health = max_possible_units * living_unit.unit_hp
                        living_unit.health = (living_unit.squad_count - 1) * living_unit.unit_hp + living_unit.current_unit_hp
                    
                    # Если воскресили хотя бы одного юнита (полностью или частично) - успех
                    if living_unit.squad_count > squad_count_before_heal:
                        try:
                            import sys
                            import os
                            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                            sys.path.insert(0, os.path.join(project_root, 'debug', 'resurrection'))
                            import resurrection_debug as debug
                            debug.log_result(True, f"Воскрешено юнитов в отряде")
                        except:
                            pass
                        return True
                    elif remaining_heal == 0:
                        # Все лечение потрачено на лечение текущего юнита (если был ранен)
                        if living_unit.current_unit_hp < living_unit.unit_hp:
                            # Лечили текущего юнита, но не смогли воскресить
                            game.add_event(f"{living_unit.unit_type.capitalize()} исцелен на {heal} HP, но недостаточно лечения для воскрешения.")
                        return True
                    else:
                        # Недостаточно силы даже для частичного воскрешения (это не должно произойти, но на всякий случай)
                        game.add_event(f"Недостаточно силы для воскрешения {living_unit.unit_type.capitalize()}.")
                        return False
                else:
                    # unit_hp == 0, просто лечим
                    if living_unit.current_unit_hp < living_unit.unit_hp:
                        health_before = living_unit.current_unit_hp
                        living_unit.current_unit_hp = min(living_unit.unit_hp, living_unit.current_unit_hp + heal)
                        actual_heal = living_unit.current_unit_hp - health_before
                        living_unit.health = (living_unit.squad_count - 1) * living_unit.unit_hp + living_unit.current_unit_hp
                        game.add_event(f"{living_unit.unit_type.capitalize()} исцелен на {actual_heal} HP!")
                        return True
                
                # Если нет мертвых юнитов в отряде, просто лечим текущего
                if dead_units == 0 and living_unit.current_unit_hp < living_unit.unit_hp:
                    # Лечим текущего юнита
                    health_before = living_unit.current_unit_hp
                    living_unit.current_unit_hp = min(living_unit.unit_hp, living_unit.current_unit_hp + heal)
                    actual_heal = living_unit.current_unit_hp - health_before
                    living_unit.health = (living_unit.squad_count - 1) * living_unit.unit_hp + living_unit.current_unit_hp
                    game.add_event(f"{living_unit.unit_type.capitalize()} исцелен на {actual_heal} HP!")
                    return True
                else:
                    game.add_event(f"{living_unit.unit_type.capitalize()} уже полностью здоров!")
                    return False
            else:
                # Старая система (без отрядов)
                # Проверяем, что юнит ранен
                if living_unit.health >= living_unit.max_health:
                    game.add_event(f"{living_unit.unit_type.capitalize()} уже полностью здоров!")
                    return False
                
                # Лечим
                health_before = living_unit.health
                living_unit.health = min(living_unit.max_health, living_unit.health + heal)
                actual_heal = living_unit.health - health_before
            
            game.add_event(f"{living_unit.unit_type.capitalize()} исцелен на {actual_heal} HP!")
            return True
        
        # Если живого юнита нет, ищем труп для воскрешения
        corpse = None
        for c in game.corpses:
            if c['x'] == x and c['y'] == y:
                corpse = c
                break
        
        if not corpse:
            return False
        
        # Проверяем, что это не нежить
        if corpse['team'] == 'undead':
            game.add_event("Воскрешение не действует на нежить!")
            return False
        
        # Анимация воскрешения вызывается в core.py перед apply
        
        # Воскрешаем юнита с частичным воскрешением отряда
        unit_class = corpse.get('unit_class')
        if unit_class:
            try:
                # Создаем нового юнита того же класса
                new_unit = unit_class(x, y, corpse['team'])
                new_unit.game_ref = game
                # Инициализируем систему отрядов если нужно
                game._set_default_squad_count(new_unit)
                
                # Применяем частичное воскрешение отряда на основе лечения
                if hasattr(new_unit, 'squad_count') and hasattr(new_unit, 'unit_hp') and new_unit.unit_hp is not None:
                    base_squad = getattr(new_unit, 'base_squad_count', new_unit.squad_count)
                    max_possible_units = base_squad
                    
                    # Воскрешаем столько юнитов, сколько можем полностью
                    remaining_heal = heal
                    full_resurrect_count = min(max_possible_units, remaining_heal // new_unit.unit_hp)
                    
                    if full_resurrect_count > 0:
                        new_unit.squad_count = full_resurrect_count
                        remaining_heal -= full_resurrect_count * new_unit.unit_hp
                        
                        # Если осталось лечение - даем текущему юниту частичное HP
                        if remaining_heal > 0:
                            new_unit.current_unit_hp = min(new_unit.unit_hp, remaining_heal)
                            remaining_heal = 0
                        else:
                            new_unit.current_unit_hp = new_unit.unit_hp
                        
                        new_unit.base_squad_count = max_possible_units
                        new_unit.max_health = max_possible_units * new_unit.unit_hp
                        new_unit.health = (new_unit.squad_count - 1) * new_unit.unit_hp + new_unit.current_unit_hp
                        
                        if full_resurrect_count < max_possible_units:
                            event_msg = f"Воскрешен {new_unit.unit_type.capitalize()} с частичным отрядом! (отряд: {new_unit.squad_count}/{max_possible_units}, HP: {new_unit.current_unit_hp}/{new_unit.unit_hp})"
                        else:
                            event_msg = f"Воскрешен {new_unit.unit_type.capitalize()}! (отряд: {new_unit.squad_count}/{max_possible_units})"
                    else:
                        # Недостаточно лечения даже для одного юнита - воскрешаем частично
                        new_unit.squad_count = 1
                        new_unit.current_unit_hp = remaining_heal
                        new_unit.base_squad_count = max_possible_units
                        new_unit.max_health = max_possible_units * new_unit.unit_hp
                        new_unit.health = new_unit.current_unit_hp
                        event_msg = f"Воскрешен {new_unit.unit_type.capitalize()} с частичным отрядом! (отряд: {new_unit.squad_count}/{max_possible_units}, HP: {new_unit.current_unit_hp}/{new_unit.unit_hp})"
                else:
                    # Старая система (без отрядов)
                    new_unit.health = min(new_unit.max_health, heal)
                    event_msg = f"Воскрешен {new_unit.unit_type}!"
                
                # Добавляем в игру
                game.units.append(new_unit)
                # Добавляем в очередь хода
                if hasattr(game, 'turn_queue') and hasattr(game, '_round_delimiter'):
                    try:
                        delim_index = game.turn_queue.index(game._round_delimiter)
                        game.turn_queue.insert(delim_index, new_unit)
                    except (ValueError, AttributeError):
                        game.turn_queue.append(new_unit)
                game.corpses.remove(corpse)
                game.add_event(event_msg)
                return True  # Успешное применение
            except Exception as e:
                game.add_event(f"Ошибка при воскрешении: {e}")
                return False
        return False  # Неудачное применение

class HealSpell(Spell):
    """Заклинание света: Лечение - восстанавливает здоровье союзника"""
    def __init__(self):
        super().__init__(
            name="Лечение",
            damage=0,
            mana_cost=6,
            cooldown=0,
            target_type='ally',
            description="Восстанавливает здоровье союзному юниту. Не действует на нежить.",
            icon='heal',
            duration=0,
            school='light'
        )
        self.heal_amount = 20  # базовое лечение
        self.spell_power_multiplier = 5  # множитель силы магии
    
    def apply(self, target, caster=None):
        # Не лечим нежить
        if target.team == 'undead':
            if hasattr(caster, 'game_ref'):
                caster.game_ref.add_event("Лечение не действует на нежить!")
            return False
        
        # Вычисляем количество лечения: базово + сила магии * множитель
        heal = self.heal_amount
        if caster and hasattr(caster, 'spell_power'):
            heal += caster.spell_power * self.spell_power_multiplier
        
        # Система отрядов: лечение только текущего активного юнита, НЕ воскрешает
        if hasattr(target, 'squad_count') and hasattr(target, 'current_unit_hp') and hasattr(target, 'unit_hp'):
            health_before = target.current_unit_hp
            target.current_unit_hp = min(target.unit_hp, target.current_unit_hp + heal)
            actual_heal = target.current_unit_hp - health_before
            
            # Обновляем общее здоровье отряда
            target.health = (target.squad_count - 1) * target.unit_hp + target.current_unit_hp
            
            # Анимация лечения для отрядов: желтые плюсики поднимаются вверх
            if hasattr(caster, 'game_ref'):
                game = caster.game_ref
                try:
                    import pygame, random
                    from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
                    cx = target.x * CELL_SIZE + CELL_SIZE // 2
                    cy = target.y * CELL_SIZE + CELL_SIZE // 2
                    
                    # Создаем плюсики
                    plusses = []
                    for _ in range(8):
                        px = cx + random.randint(-20, 20)
                        py = cy + random.randint(-10, 10)
                        speed = random.uniform(1.5, 3.0)
                        plusses.append([px, py, speed, 255])  # x, y, скорость, альфа
                    
                    # Анимация подъема плюсиков
                    for step in range(120):  # Увеличено до 120 кадров для максимальной плавности
                        pygame.event.pump()
                        game.draw()
                        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                        
                        font = pygame.font.Font(None, 32)
                        for plus in plusses:
                            plus[1] -= plus[2]  # поднимаем вверх
                            plus[3] = max(0, plus[3] - 8)  # уменьшаем альфу
                            
                            # Рисуем плюсик
                            text = font.render('+', True, (255, 255, 0, int(plus[3])))
                            text_with_alpha = text.copy()
                            text_with_alpha.set_alpha(int(plus[3]))
                            s.blit(text_with_alpha, (int(plus[0]), int(plus[1])))
                        
                        # Светлое свечение вокруг цели
                        if step < 15:
                            glow_alpha = max(0, 120 - step * 8)
                            pygame.draw.circle(s, (255, 255, 200, glow_alpha), (cx, cy), 25 + step, 3)
                        
                        game.screen.blit(s, (0,0))
                        pygame.display.flip()
                        pygame.time.delay(10)  # Уменьшена задержка для плавности
                except Exception:
                    pass
                
                caster.game_ref.add_event(f"{target.unit_type.capitalize()} исцелён на {actual_heal} HP! (Текущий юнит в отряде)")
            return True
        
        # Старая система (без отрядов)
        health_before = target.health
        
        # Восстанавливаем здоровье
        target.health = min(target.max_health, target.health + heal)
        actual_heal = target.health - health_before
        
        # Анимация лечения: желтые плюсики поднимаются вверх
        if hasattr(caster, 'game_ref'):
            game = caster.game_ref
            try:
                import pygame, random
                from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
                cx = target.x * CELL_SIZE + CELL_SIZE // 2
                cy = target.y * CELL_SIZE + CELL_SIZE // 2
                
                # Создаем плюсики
                plusses = []
                for _ in range(8):
                    px = cx + random.randint(-20, 20)
                    py = cy + random.randint(-10, 10)
                    speed = random.uniform(1.5, 3.0)
                    plusses.append([px, py, speed, 255])  # x, y, скорость, альфа
                
                # Анимация подъема плюсиков
                for step in range(30):
                    pygame.event.pump()
                    game.draw()
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    font = pygame.font.Font(None, 32)
                    for plus in plusses:
                        plus[1] -= plus[2]  # поднимаем вверх
                        plus[3] = max(0, plus[3] - 8)  # уменьшаем альфу
                        
                        # Рисуем плюсик
                        text = font.render('+', True, (255, 255, 0, int(plus[3])))
                        text_with_alpha = text.copy()
                        text_with_alpha.set_alpha(int(plus[3]))
                        s.blit(text_with_alpha, (int(plus[0]), int(plus[1])))
                    
                    # Светлое свечение вокруг цели
                    if step < 15:
                        glow_alpha = max(0, 120 - step * 8)
                        pygame.draw.circle(s, (255, 255, 200, glow_alpha), (cx, cy), 25 + step, 3)
                    
                    game.screen.blit(s, (0,0))
                    pygame.display.flip()
                    pygame.time.delay(25)
                    
                game.add_event(f"{target.unit_type.capitalize()} исцелен на {actual_heal} HP!")
            except Exception:
                pass
        
        return True  # Успешное применение

class IceShieldSpell(Spell):
    """Заклинание воды: Ледяной щит - защищает от физического урона"""
    def __init__(self):
        super().__init__(
            name="Ледяной щит",
            damage=0,
            mana_cost=8,
            cooldown=0,
            target_type='ally',
            description="Покрывает союзника ледяной коркой. Поглощает 35% физ. урона и увеличивает защиту.",
            icon='ice_shield',
            duration=3,
            school='water'
        )
        self.absorption_percent = 35  # процент поглощения физического урона
        self.hp_bonus_percent = 5  # процент от макс хп для бонуса хп
        self.defense_bonus_percent = 20  # процент от физ защиты для бонуса защиты
    
    def apply(self, target, caster=None):
        # Длительность: базово 3 + сила магии
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        # Вычисляем бонусы защиты
        hp_bonus = int(target.max_health * (self.hp_bonus_percent / 100.0))
        phys_bonus = int(target.phys_defense * (self.defense_bonus_percent / 100.0))
        
        # Применяем бафф
        target.ice_shield_turns = turns
        target.ice_shield_absorption = self.absorption_percent / 100.0
        target.ice_shield_hp_bonus = hp_bonus
        target.ice_shield_phys_bonus = phys_bonus
        
        # Добавляем бонусы к защите
        target.phys_defense += phys_bonus
        target.health = min(target.max_health, target.health + hp_bonus)
        
        # Анимация: юнит покрывается ледяной коркой
        if hasattr(caster, 'game_ref'):
            game = caster.game_ref
            try:
                import pygame, random, math
                from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
                cx = target.x * CELL_SIZE + CELL_SIZE // 2
                cy = target.y * CELL_SIZE + CELL_SIZE // 2
                
                # Этап 1: Ледяные частицы собираются вокруг юнита
                particles = []
                for _ in range(100):  # Увеличено количество частиц до 100
                    angle = random.random() * math.tau
                    distance = random.randint(30, 60)
                    px = cx + int(math.cos(angle) * distance)
                    py = cy + int(math.sin(angle) * distance)
                    particles.append([px, py, angle, distance])
                
                for step in range(100):  # Увеличено до 100 кадров для максимальной плавности
                    pygame.event.pump()
                    game.draw()
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    # Частицы стягиваются к юниту
                    for p in particles:
                        p[3] = max(0, p[3] - 3)  # приближаются к центру
                        p[0] = cx + int(math.cos(p[2]) * p[3])
                        p[1] = cy + int(math.sin(p[2]) * p[3])
                        # Ледяные кристаллы
                        pygame.draw.circle(s, (150, 220, 255, 200), (int(p[0]), int(p[1])), 3)
                        pygame.draw.circle(s, (200, 240, 255, 150), (int(p[0]), int(p[1])), 1)
                    
                    game.screen.blit(s, (0,0))
                    pygame.display.flip()
                    pygame.time.delay(8)  # Уменьшена задержка для плавности
                
                # Этап 2: Ледяная корка покрывает юнита
                for step in range(80):  # Увеличено до 80 кадров для максимальной плавности
                    pygame.event.pump()
                    game.draw()
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    # Рисуем ледяную ауру вокруг юнита
                    radius = CELL_SIZE // 2 + 5
                    alpha = min(180, 80 + step * 8)
                    
                    # Внешний слой льда
                    pygame.draw.circle(s, (150, 220, 255, alpha), (cx, cy), radius, 4)
                    pygame.draw.circle(s, (200, 240, 255, alpha - 30), (cx, cy), radius - 3, 2)
                    
                    # Ледяные кристаллы вокруг
                    for i in range(12):  # Увеличено количество элементов
                        angle = (step * 0.2 + i) * (math.pi / 3)
                        x = cx + int(math.cos(angle) * (radius + 5))
                        y = cy + int(math.sin(angle) * (radius + 5))
                        # Рисуем кристалл (ромб)
                        points = [
                            (x, y - 5),
                            (x + 3, y),
                            (x, y + 5),
                            (x - 3, y)
                        ]
                        pygame.draw.polygon(s, (180, 230, 255, alpha), points)
                    
                    game.screen.blit(s, (0,0))
                    pygame.display.flip()
                    pygame.time.delay(25)
                    
                game.add_event(f"{target.unit_type.capitalize()} покрыт ледяным щитом!")
            except Exception:
                pass
        
        return True  # Успешное применение

class LightningSpell(Spell):
    """Заклинание ветра: Молния - бьёт врага молнией"""
    def __init__(self):
        super().__init__(
            name="Молния",
            damage=30,
            mana_cost=10,
            cooldown=0,
            target_type='enemy',
            description="Призывает молнию, которая бьёт по врагу. Урон зависит от силы магии.",
            icon='lightning',
            duration=0,
            school='air'
        )
        self.spell_power_multiplier = 8  # множитель силы магии для урона
    
    def apply(self, target, caster=None):
        # Вычисляем урон: базовый + сила магии * множитель
        damage = self.damage
        if caster and hasattr(caster, 'spell_power'):
            damage += caster.spell_power * self.spell_power_multiplier
        
        # Запоминаем здоровье до урона
        health_before = target.health
        
        # Запоминаем squad_count ДО применения урона
        squad_count_before = getattr(target, 'squad_count', 1)
        
        # Наносим урон (магический)
        unit_died = target.take_damage(damage, attack_type='magical')
        actual_damage = health_before - target.health
        squad_count_after = getattr(target, 'squad_count', 1)
        units_lost = squad_count_before - squad_count_after
        
        # Анимация молнии
        if hasattr(caster, 'game_ref'):
            game = caster.game_ref
            try:
                import pygame, random, math
                from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
                cx = target.x * CELL_SIZE + CELL_SIZE // 2
                cy = target.y * CELL_SIZE + CELL_SIZE // 2
                
                # Молния бьёт!
                for strike in range(8):  # Увеличено до 8 ударов молнии для максимального эффекта
                    pygame.event.pump()
                    game.draw()
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    # Рисуем зигзагообразную молнию от верха до цели
                    points = [(cx, 0)]
                    current_y = 0
                    current_x = cx
                    
                    while current_y < cy:
                        # Случайное отклонение
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
                    for i in range(3):
                        radius = 30 - i * 8
                        alpha = 255 - i * 60
                        pygame.draw.circle(s, (255, 255, 255, alpha), (cx, cy), radius)
                    
                    game.screen.blit(s, (0,0))
                    pygame.display.flip()
                    pygame.time.delay(15)  # Уменьшена задержка для плавности
                    
                    # Пауза между ударами
                    if strike < 2:
                        pygame.event.pump()
                        game.draw()
                        pygame.display.flip()
                        pygame.time.delay(12)  # Уменьшена задержка для плавности
                
                # Рассеивание
                for step in range(60):  # Увеличено до 60 кадров для максимальной плавности
                    pygame.event.pump()
                    game.draw()
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    # Искры
                    for _ in range(5):
                        sx = cx + random.randint(-20, 20)
                        sy = cy + random.randint(-20, 20)
                        spark_alpha = max(0, 200 - step * 20)
                        pygame.draw.circle(s, (200, 200, 255, spark_alpha), (sx, sy), 2)
                    
                    game.screen.blit(s, (0,0))
                    pygame.display.flip()
                    pygame.time.delay(10)  # Уменьшена задержка для плавности
                
                if unit_died:
                    game.kill_unit(target)
                    game.animation_manager.animate_queue_fade(target)
                    event_msg = f"Молния убила {target.unit_type} (урон: {actual_damage})"
                    if units_lost > 0:
                        event_msg += f", уничтожено {units_lost} юнитов из отряда"
                    game.add_event(event_msg)
                    game.check_game_over()
                else:
                    event_msg = f"Молния ударила {target.unit_type} (урон: {actual_damage})"
                    if units_lost > 0:
                        event_msg += f", потеряно {units_lost} юнитов из отряда"
                    game.add_event(event_msg)
            except Exception:
                pass
        else:
            # Если нет анимации, всё равно нужно убрать юнита
            if unit_died and hasattr(caster, 'game_ref'):
                game = caster.game_ref
                game.kill_unit(target)
                game.animation_manager.animate_queue_fade(target)
                event_msg = f"Молния убила {target.unit_type} (урон: {actual_damage})"
                if units_lost > 0:
                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                game.add_event(event_msg)
                game.check_game_over()
        
        return True  # Успешное применение

class EarthSpikesSpell(Spell):
    """Заклинание земли: Каменные шипы - наносит урон в зоне креста"""
    def __init__(self):
        super().__init__(
            name="Каменные шипы",
            damage=25,
            mana_cost=12,
            cooldown=0,
            target_type='area',
            description="Поднимает каменные шипы из земли в зоне креста (5x5). Наносит физический урон.",
            icon='earth_spikes',
            duration=0,
            school='earth'
        )
        self.spell_power_multiplier = 6  # множитель силы магии для урона
    
    def apply(self, center, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return
        game = caster.game_ref
        x, y = center
        
        # Вычисляем урон
        damage = self.damage
        if caster and hasattr(caster, 'spell_power'):
            damage += caster.spell_power * self.spell_power_multiplier
        
        # Определяем зону атаки: крест 5x5 (2 клетки в каждую сторону)
        affected_cells = []
        
        # Горизонталь
        for dx in range(-2, 3):
            cell_x = x + dx
            if 0 <= cell_x < GRID_WIDTH:
                affected_cells.append((cell_x, y))
        
        # Вертикаль
        for dy in range(-2, 3):
            cell_y = y + dy
            if 0 <= cell_y < GRID_HEIGHT:
                if (x, cell_y) not in affected_cells:  # не дублируем центр
                    affected_cells.append((x, cell_y))
        
        # Находим юнитов в зоне
        affected_units = []
        for unit in game.units:
            if (unit.x, unit.y) in affected_cells and unit != caster:
                affected_units.append(unit)
        
        # Анимация: каменные шипы поднимаются из земли
        try:
            import pygame, random, math
            from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
            
            # Этап 1: Земля трескается
            for step in range(10):
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                
                # Рисуем трещины в зоне поражения
                for cell_x, cell_y in affected_cells:
                    cx = cell_x * CELL_SIZE + CELL_SIZE // 2
                    cy = cell_y * CELL_SIZE + CELL_SIZE // 2
                    
                    # Трещины
                    for i in range(4):
                        angle = i * (math.pi / 2) + step * 0.1
                        length = min(CELL_SIZE // 2, step * 4)
                        ex = cx + int(math.cos(angle) * length)
                        ey = cy + int(math.sin(angle) * length)
                        pygame.draw.line(s, (100, 70, 40, 150), (cx, cy), (ex, ey), 2)
                
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(10)  # Уменьшена задержка для плавности
            
            # Этап 2: Шипы поднимаются
            for step in range(40):  # Увеличено с 15 до 40 кадров
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                
                for cell_x, cell_y in affected_cells:
                    cx = cell_x * CELL_SIZE + CELL_SIZE // 2
                    cy = cell_y * CELL_SIZE + CELL_SIZE // 2
                    
                    # Высота шипа растёт
                    spike_height = min(40, step * 3)
                    spike_base = 15
                    
                    # Рисуем несколько шипов вокруг центра клетки
                    for i in range(3):
                        offset_x = random.randint(-10, 10) if step == 0 else 0
                        offset_y = random.randint(-10, 10) if step == 0 else 0
                        spike_x = cx + offset_x
                        spike_y = cy + offset_y
                        
                        # Шип - треугольник
                        points = [
                            (spike_x, spike_y - spike_height),  # верх
                            (spike_x - spike_base // 2, spike_y),  # левый низ
                            (spike_x + spike_base // 2, spike_y)   # правый низ
                        ]
                        
                        # Каменный цвет
                        pygame.draw.polygon(s, (120, 120, 120, 200), points)
                        pygame.draw.polygon(s, (80, 80, 80, 255), points, 2)
                    
                    # Пыль
                    if step < 8:
                        for _ in range(3):
                            px = cx + random.randint(-15, 15)
                            py = cy + random.randint(-10, 10)
                            pygame.draw.circle(s, (150, 130, 100, 100), (px, py), 2)
                
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(12)  # Уменьшена задержка для плавности
            
            # Этап 3: Шипы опускаются
            for step in range(10):
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                
                for cell_x, cell_y in affected_cells:
                    cx = cell_x * CELL_SIZE + CELL_SIZE // 2
                    cy = cell_y * CELL_SIZE + CELL_SIZE // 2
                    
                    spike_height = max(0, 40 - step * 4)
                    spike_base = 15
                    alpha = max(0, 200 - step * 20)
                    
                    for i in range(3):
                        spike_x = cx
                        spike_y = cy
                        
                        points = [
                            (spike_x, spike_y - spike_height),
                            (spike_x - spike_base // 2, spike_y),
                            (spike_x + spike_base // 2, spike_y)
                        ]
                        
                        pygame.draw.polygon(s, (120, 120, 120, alpha), points)
                
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(10)  # Уменьшена задержка для плавности
                
        except Exception:
            pass
        
        # Наносим урон всем юнитам в зоне
        for unit in affected_units:
            health_before = unit.health
            squad_count_before = getattr(unit, 'squad_count', 1)
            unit_died = unit.take_damage(damage, attack_type='physical')
            actual_damage = health_before - unit.health
            squad_count_after = getattr(unit, 'squad_count', 1)
            units_lost = squad_count_before - squad_count_after
            
            if unit_died:
                game.kill_unit(unit)
                game.animation_manager.animate_queue_fade(unit)
                event_msg = f"Каменные шипы убили {unit.unit_type} (урон: {actual_damage})"
                if units_lost > 0:
                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                game.add_event(event_msg)
            else:
                event_msg = f"Каменные шипы ранили {unit.unit_type} (урон: {actual_damage})"
                if units_lost > 0:
                    event_msg += f", потеряно {units_lost} юнитов из отряда"
                game.add_event(event_msg)
        
        return True  # Успешное применение

class CounterstrikeSpell(Spell):
    """Заклинание ветра: Контрудар - позволяет контратаковать всех в ближнем бою"""
    def __init__(self):
        super().__init__(
            name="Контрудар",
            damage=0,
            mana_cost=8,
            cooldown=0,
            target_type='ally',
            description="Юнит контратакует всех врагов, атакующих его в ближнем бою.",
            icon='counterstrike',
            duration=3,
            school='air'
        )
    
    def apply(self, target, caster=None):
        # Длительность: базово 3 + сила магии
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        target.counterstrike_turns = turns
        
        # Анимация: 3 меча соединены концами в центре и вращаются в виде конуса
        if hasattr(caster, 'game_ref'):
            game = caster.game_ref
            try:
                import pygame, random, math
                from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
                cx = target.x * CELL_SIZE + CELL_SIZE // 2
                cy = target.y * CELL_SIZE + CELL_SIZE // 2 - 20  # выше юнита
                
                # Этап 1: Мечи появляются и формируют конус
                for step in range(120):  # Увеличено до 120 кадров для максимальной плавности
                    pygame.event.pump()
                    game.draw()
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    # Угол вращения всей конструкции
                    rotation_angle = step * 0.25
                    
                    # Длина меча от центра до конца
                    blade_len = min(30, 10 + step * 1.5)
                    alpha = min(255, step * 12)
                    
                    # 3 меча расходятся из центра под углами 120 градусов
                    for i in range(3):
                        angle = rotation_angle + i * (2 * math.pi / 3)  # 120 градусов между мечами
                        
                        # Конец меча (рукоять) - в центре
                        handle_x = cx
                        handle_y = cy
                        
                        # Кончик меча (лезвие) - расходится от центра
                        blade_tip_x = cx + int(math.cos(angle) * blade_len)
                        blade_tip_y = cy + int(math.sin(angle) * blade_len)
                        
                        # Рисуем лезвие (серебристо-голубое)
                        pygame.draw.line(s, (200, 220, 255, alpha), 
                                       (handle_x, handle_y), 
                                       (blade_tip_x, blade_tip_y), 4)
                        
                        # Добавляем "остриё" меча - маленький треугольник на конце
                        tip_size = 6
                        perpendicular = angle + math.pi / 2
                        tip_left_x = blade_tip_x + int(math.cos(perpendicular) * tip_size // 2)
                        tip_left_y = blade_tip_y + int(math.sin(perpendicular) * tip_size // 2)
                        tip_right_x = blade_tip_x - int(math.cos(perpendicular) * tip_size // 2)
                        tip_right_y = blade_tip_y - int(math.sin(perpendicular) * tip_size // 2)
                        
                        # Еще дальше вперед - острие
                        tip_forward_x = blade_tip_x + int(math.cos(angle) * tip_size)
                        tip_forward_y = blade_tip_y + int(math.sin(angle) * tip_size)
                        
                        pygame.draw.polygon(s, (220, 230, 255, alpha), 
                                          [(tip_forward_x, tip_forward_y),
                                           (tip_left_x, tip_left_y),
                                           (tip_right_x, tip_right_y)])
                    
                    # Центральная точка соединения (магический узел)
                    center_radius = max(2, 8 - step // 4)
                    pygame.draw.circle(s, (255, 255, 255, alpha), (cx, cy), center_radius)
                    pygame.draw.circle(s, (180, 200, 255, alpha // 2), (cx, cy), center_radius + 5, 2)
                    
                    # Магические искры вокруг конструкции
                    if step > 10:
                        for _ in range(3):
                            spark_angle = random.random() * math.tau
                            spark_dist = random.randint(15, blade_len + 5)
                            spark_x = cx + int(math.cos(spark_angle) * spark_dist)
                            spark_y = cy + int(math.sin(spark_angle) * spark_dist)
                            pygame.draw.circle(s, (180, 200, 255, alpha // 2), (spark_x, spark_y), 2)
                    
                    game.screen.blit(s, (0,0))
                    pygame.display.flip()
                    pygame.time.delay(10)  # Уменьшена задержка для плавности
                
                game.add_event(f"{target.unit_type.capitalize()} готов к контратаке!")
            except Exception:
                pass
        
        return True  # Успешное применение

class RuneWallSpell(Spell):
    """Заклинание рун: Руна стены - создает барьер из 3 клеток по вертикали"""
    def __init__(self):
        super().__init__(
            name="Руна стены",
            damage=0,
            mana_cost=10,
            cooldown=0,
            target_type='area',
            description="Создает магический барьер из 3 клеток по вертикали на 3 хода.",
            icon='rune_wall',
            duration=3,
            school='rune'
        )
    
    def apply(self, center, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return
        game = caster.game_ref
        x, y = center
        
        # Длительность: базово 3 + сила магии
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        # Определяем 3 клетки по вертикали (центр + 1 вверх + 1 вниз)
        wall_cells = []
        for dy in [-1, 0, 1]:
            cell_y = y + dy
            if 0 <= cell_y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                # Проверяем, что клетка пуста
                is_empty = not any(u.x == x and u.y == cell_y for u in game.units)
                if is_empty:
                    wall_cells.append((x, cell_y))
        
        if not wall_cells:
            if hasattr(game, 'add_event'):
                game.add_event("Невозможно создать стену здесь!")
            return False
        
        # Анимация: руны появляются и формируют барьер
        try:
            import pygame, random, math
            from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
            
            # Этап 1: Руны появляются
            for step in range(40):  # Увеличено с 15 до 40 кадров
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                
                for wx, wy in wall_cells:
                    cx = wx * CELL_SIZE + CELL_SIZE // 2
                    cy = wy * CELL_SIZE + CELL_SIZE // 2
                    
                    # Растущие руны
                    alpha = min(255, step * 20)
                    size = min(30, step * 2)
                    
                    # Магический круг
                    pygame.draw.circle(s, (150, 100, 200, alpha), (cx, cy), size, 3)
                    
                    # Руны внутри (упрощенно - кресты и линии)
                    if step > 5:
                        rune_size = min(15, (step - 5) * 2)
                        # Вертикальная линия
                        pygame.draw.line(s, (180, 120, 220, alpha), 
                                       (cx, cy - rune_size), (cx, cy + rune_size), 2)
                        # Горизонтальная линия
                        pygame.draw.line(s, (180, 120, 220, alpha), 
                                       (cx - rune_size, cy), (cx + rune_size, cy), 2)
                
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(10)  # Уменьшена задержка для плавности
            
            # Этап 2: Барьер формируется
            for step in range(10):
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                
                for wx, wy in wall_cells:
                    cx = wx * CELL_SIZE + CELL_SIZE // 2
                    cy = wy * CELL_SIZE + CELL_SIZE // 2
                    
                    # Барьер (полупрозрачная стена)
                    alpha = min(180, 80 + step * 10)
                    barrier_rect = pygame.Rect(wx * CELL_SIZE + 10, wy * CELL_SIZE + 5, 
                                               CELL_SIZE - 20, CELL_SIZE - 10)
                    pygame.draw.rect(s, (150, 100, 200, alpha), barrier_rect)
                    pygame.draw.rect(s, (180, 120, 220, alpha), barrier_rect, 3)
                    
                    # Светящиеся частицы
                    for _ in range(3):
                        px = cx + random.randint(-15, 15)
                        py = cy + random.randint(-15, 15)
                        pygame.draw.circle(s, (200, 150, 255, alpha), (px, py), 2)
                
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(25)
                
        except Exception:
            pass
        
        # Создаем барьеры на этих клетках
        for wx, wy in wall_cells:
            barrier = {
                'x': wx,
                'y': wy,
                'turns': turns,
                'type': 'rune_wall'
            }
            if not hasattr(game, 'barriers'):
                game.barriers = []
            game.barriers.append(barrier)
        
        if hasattr(game, 'add_event'):
            game.add_event(f"Создана руна стены ({len(wall_cells)} клеток)!")
        
        return True  # Успешное применение

class RuneMagicSpell(Spell):
    """Заклинание рун: Руна магии - зачаровывает урон, добавляет магическую атаку"""
    def __init__(self):
        super().__init__(
            name="Руна магии",
            damage=0,
            mana_cost=8,
            cooldown=0,
            target_type='ally',
            description="Зачаровывает урон юнита, добавляя магическую атаку равную физической. Длительность зависит от силы магии.",
            icon='rune_magic',
            duration=3,
            school='rune'
        )
    
    def apply(self, target, caster=None):
        if not target or not hasattr(target, 'phys_attack'):
            return False
        
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        # Если у юнита только физическая атака, добавляем магическую равную физической
        if target.magic_attack == 0 and target.phys_attack > 0:
            # Сохраняем базовую магическую атаку (если была)
            if not hasattr(target, 'base_magic_attack'):
                target.base_magic_attack = target.magic_attack
            # Добавляем магическую атаку равную физической
            target.magic_attack = target.phys_attack
            target.rune_magic_bonus = target.phys_attack
            target.rune_magic_turns = turns
            
            # Анимация каста уже вызывается в core.py при применении заклинания
            
            if hasattr(target, 'game_ref') and target.game_ref and hasattr(target.game_ref, 'add_event'):
                target.game_ref.add_event(f"Руна магии зачаровала {target.unit_type.capitalize()}!")
            return True
        
        # Если уже есть магическая атака, просто продлеваем эффект
        if hasattr(target, 'rune_magic_turns'):
            target.rune_magic_turns = turns
        
        return True

class RuneBerserkerSpell(Spell):
    """Заклинание рун: Руна берсерка - юнит становится враждебным для всех, +40% урон, -25% защита"""
    def __init__(self):
        super().__init__(
            name="Руна берсерка",
            damage=0,
            mana_cost=10,
            cooldown=0,
            target_type='enemy',
            description="Вражеский юнит становится враждебным для всех и атакует ближайший юнит. +40% физ/маг урон, -25% физ/маг защита.",
            icon='rune_berserker',
            duration=2,
            school='rune'
        )
    
    def apply(self, target, caster=None):
        if not target:
            return False
        
        # КРИТИЧНО: Проверяем, что это действительно целевой юнит, а не другой объект
        # Убеждаемся, что target имеет необходимые атрибуты юнита
        if not hasattr(target, 'team') or not hasattr(target, 'phys_attack'):
            return False
        
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        # КРИТИЧНО: Сохраняем базовые значения ТОЛЬКО если заклинание еще не было применено
        # Если заклинание уже активно, используем сохраненные базовые значения
        if not hasattr(target, 'rune_berserker_active') or not getattr(target, 'rune_berserker_active', False):
            # Сохраняем текущие значения как базовые (если они еще не сохранены)
            if not hasattr(target, 'base_phys_attack_berserker'):
                target.base_phys_attack_berserker = getattr(target, 'phys_attack', 0)
            if not hasattr(target, 'base_magic_attack_berserker'):
                target.base_magic_attack_berserker = getattr(target, 'magic_attack', 0)
            if not hasattr(target, 'base_phys_defense_berserker'):
                target.base_phys_defense_berserker = getattr(target, 'phys_defense', 0)
            if not hasattr(target, 'base_magic_defense_berserker'):
                target.base_magic_defense_berserker = getattr(target, 'magic_defense', 0)
        
        # КРИТИЧНО: Используем сохраненные базовые значения для расчета
        base_phys_attack = getattr(target, 'base_phys_attack_berserker', target.phys_attack)
        base_magic_attack = getattr(target, 'base_magic_attack_berserker', target.magic_attack)
        base_phys_defense = getattr(target, 'base_phys_defense_berserker', target.phys_defense)
        base_magic_defense = getattr(target, 'base_magic_defense_berserker', target.magic_defense)
        
        # Увеличиваем урон на 40% от базовых значений
        target.phys_attack = int(base_phys_attack * 1.4)
        target.magic_attack = int(base_magic_attack * 1.4)
        
        # Уменьшаем защиту на 25% от базовых значений
        target.phys_defense = int(base_phys_defense * 0.75)
        target.magic_defense = int(base_magic_defense * 0.75)
        
        # КРИТИЧНО: Сохраняем оригинальную команду ТОЛЬКО если она еще не сохранена
        # или если заклинание не было активно
        if not hasattr(target, 'rune_berserker_active') or not getattr(target, 'rune_berserker_active', False):
            # Сохраняем оригинальную команду только если она еще не сохранена
            if not hasattr(target, 'rune_berserker_original_team'):
                target.rune_berserker_original_team = target.team
        
        # Устанавливаем флаг враждебности и меняем команду на уникальную
        # ОТЛАДКА: Логируем применение
        old_team = getattr(target, 'team', None)
        if BERSERKER_DEBUG:
            debugger = get_debugger()
            if debugger:
                debugger.log_spell_apply(self, target, caster)
        
        target.rune_berserker_active = True
        target.rune_berserker_turns = turns
        
        # КРИТИЧНО: Используем более надежный способ создания уникальной команды
        # Используем комбинацию id объекта и текущего времени для гарантии уникальности
        import time
        unique_id = f'berserker_{id(target)}_{int(time.time() * 1000000)}'
        
        # ОТЛАДКА: Логируем изменение команды
        if BERSERKER_DEBUG:
            debugger = get_debugger()
            if debugger:
                debugger.log_team_change(target, old_team, unique_id, "Применение руны берсерка")
        
        target.team = unique_id
        
        # Анимация каста уже вызывается в core.py при применении заклинания
        
        if hasattr(target, 'game_ref') and target.game_ref and hasattr(target.game_ref, 'add_event'):
            target.game_ref.add_event(f"Руна берсерка активирована на {target.unit_type.capitalize()}!")
        
        return True

class WeaknessSpell(Spell):
    """Заклинание тьмы: Слабость - уменьшает атаку врага"""
    def __init__(self):
        super().__init__(
            name="Слабость",
            damage=0,
            mana_cost=7,
            cooldown=0,
            target_type='enemy',
            description="Снижает физическую и магическую атаку врага на 30%.",
            icon='weakness',
            duration=3,
            school='darkness'
        )
        self.debuff_amount = 30  # процент уменьшения атаки
    
    def apply(self, target, caster=None):
        # Проверяем отражение сопротивлением магии
        reflected, game = self.check_magic_resist_reflection(target, caster)
        if reflected and game:
            # Анимация отражения заклинания
            try:
                from .graphics import animate_spell_reflection
                from .config import CELL_SIZE
                target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
                caster_px = (caster.x * CELL_SIZE + CELL_SIZE // 2, caster.y * CELL_SIZE + CELL_SIZE // 2) if caster else None
                animate_spell_reflection(game.screen, target_px, caster_px, redraw_callback=game.draw)
            except Exception as e:
                print(f"Ошибка анимации отражения: {e}")
            game.add_event(f"{target.unit_type} отразил заклинание {self.name} благодаря сопротивлению магии!")
            return False  # Заклинание отражено, не применено
        
        # Длительность: базово 3 + сила магии
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        # Вычисляем уменьшение атаки
        percent = self.debuff_amount / 100.0
        phys_penalty = int(max(1, target.phys_attack * percent))
        magic_penalty = int(max(1, target.magic_attack * percent))
        
        # Применяем дебафф
        target.weakness_turns = turns
        target.weakness_phys_penalty = phys_penalty
        target.weakness_magic_penalty = magic_penalty
        target.phys_attack = max(1, target.phys_attack - phys_penalty)
        target.magic_attack = max(1, target.magic_attack - magic_penalty)
        
        # Анимация: меч над головой юнита ломается
        if hasattr(caster, 'game_ref'):
            game = caster.game_ref
            try:
                import pygame, random, math
                from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
                cx = target.x * CELL_SIZE + CELL_SIZE // 2
                cy = target.y * CELL_SIZE + CELL_SIZE // 2 - 30  # выше юнита
                
                # Этап 1: Меч появляется над юнитом
                for step in range(15):
                    pygame.event.pump()
                    game.draw()
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    alpha = min(255, step * 20)
                    
                    # Рисуем целый меч (вертикально вниз)
                    blade_len = 20
                    blade_start_y = cy - blade_len // 2
                    blade_end_y = cy + blade_len // 2
                    
                    # Лезвие (серое)
                    pygame.draw.line(s, (150, 150, 150, alpha), 
                                   (cx, blade_start_y), (cx, blade_end_y), 4)
                    
                    # Рукоять (темная)
                    handle_start_y = blade_start_y - 5
                    pygame.draw.line(s, (80, 80, 80, alpha), 
                                   (cx, handle_start_y), (cx, blade_start_y), 3)
                    # Гарда
                    pygame.draw.line(s, (100, 100, 100, alpha), 
                                   (cx - 8, blade_start_y), (cx + 8, blade_start_y), 3)
                    
                    game.screen.blit(s, (0,0))
                    pygame.display.flip()
                    pygame.time.delay(10)  # Уменьшена задержка для плавности
                
                # Этап 2: Темная аура окружает меч
                for step in range(60):  # Увеличено до 60 кадров для максимальной плавности
                    pygame.event.pump()
                    game.draw()
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    # Целый меч
                    blade_len = 20
                    blade_start_y = cy - blade_len // 2
                    blade_end_y = cy + blade_len // 2
                    pygame.draw.line(s, (150, 150, 150, 255), (cx, blade_start_y), (cx, blade_end_y), 4)
                    handle_start_y = blade_start_y - 5
                    pygame.draw.line(s, (80, 80, 80, 255), (cx, handle_start_y), (cx, blade_start_y), 3)
                    pygame.draw.line(s, (100, 100, 100, 255), (cx - 8, blade_start_y), (cx + 8, blade_start_y), 3)
                    
                    # Темная аура
                    aura_radius = 15 + step * 2
                    pygame.draw.circle(s, (80, 0, 80, max(0, 150 - step * 15)), (cx, cy), aura_radius, 2)
                    
                    # Темные частицы
                    for _ in range(3):
                        angle = random.random() * math.tau
                        px = cx + int(math.cos(angle) * aura_radius)
                        py = cy + int(math.sin(angle) * aura_radius)
                        pygame.draw.circle(s, (60, 0, 60, 180), (px, py), 2)
                    
                    game.screen.blit(s, (0,0))
                    pygame.display.flip()
                    pygame.time.delay(12)  # Уменьшена задержка для плавности
                
                # Этап 3: Меч ломается!
                for step in range(12):
                    pygame.event.pump()
                    game.draw()
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    # Верхняя половина меча (падает влево)
                    offset_x = -step * 2
                    offset_y = step * 1.5
                    rotation = step * 5  # градусы поворота
                    
                    upper_blade_len = 10
                    upper_start_y = cy - upper_blade_len
                    upper_end_y = cy
                    
                    # Рисуем верхнюю часть с наклоном
                    pygame.draw.line(s, (150, 150, 150, max(0, 255 - step * 20)), 
                                   (cx + offset_x, upper_start_y + offset_y), 
                                   (cx + offset_x, upper_end_y + offset_y), 3)
                    
                    # Нижняя половина меча (падает вправо)
                    offset_x2 = step * 2
                    offset_y2 = step * 1.5
                    
                    lower_blade_len = 10
                    lower_start_y = cy
                    lower_end_y = cy + lower_blade_len
                    
                    pygame.draw.line(s, (150, 150, 150, max(0, 255 - step * 20)), 
                                   (cx + offset_x2, lower_start_y + offset_y2), 
                                   (cx + offset_x2, lower_end_y + offset_y2), 3)
                    
                    # Искры в месте разлома
                    for _ in range(5):
                        spark_offset_x = random.randint(-5, 5)
                        spark_offset_y = random.randint(-5, 5)
                        spark_size = random.randint(1, 3)
                        pygame.draw.circle(s, (255, 200, 100, max(0, 200 - step * 15)), 
                                         (cx + spark_offset_x, cy + spark_offset_y), spark_size)
                    
                    game.screen.blit(s, (0,0))
                    pygame.display.flip()
                    pygame.time.delay(40)
                
                game.add_event(f"{target.unit_type.capitalize()} ослаблен!")
            except Exception:
                pass
        
        return True  # Успешное применение

class FireWallSpell(Spell):
    """Заклинание огня: Огненная стена - создает барьер из огня на 2 клетки по вертикали"""
    def __init__(self):
        super().__init__(
            name="Огненная стена",
            damage=15,  # Урон при прохождении через стену
            mana_cost=15,
            cooldown=0,
            target_type='area',
            description="Создает стену из огня на 3 клетки по вертикали. Прохождение через стену наносит урон.",
            icon='fire_wall',
            duration=3,
            school='fire'
        )
        self.spell_power_multiplier = 3  # множитель силы магии для урона
    
    def apply(self, center, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        game = caster.game_ref
        x, y = center
        
        # Длительность: базово 3 + сила магии
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        # Определяем 3 клетки по вертикали (центр + 1 вверх + 1 вниз)
        wall_cells = []
        for dy in [-1, 0, 1]:  # Вверх, текущая клетка и вниз
            cell_y = y + dy
            if 0 <= cell_y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                # Разрешаем создавать стену (не проверяем на юнитов, т.к. через нее можно проходить)
                wall_cells.append((x, cell_y))
        
        if not wall_cells:
            if hasattr(game, 'add_event'):
                game.add_event("Невозможно создать огненную стену здесь!")
            return False
        
        # Анимация создания стены
        try:
            import pygame
            from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
            
            # Этап 1: Огонь вспыхивает
            for step in range(20):
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                
                for wx, wy in wall_cells:
                    cx = wx * CELL_SIZE + CELL_SIZE // 2
                    cy = wy * CELL_SIZE + CELL_SIZE // 2
                    
                    # Растущее пламя
                    alpha = min(255, step * 15)
                    height = min(CELL_SIZE - 10, step * 3)
                    
                    # Пламя снизу вверх
                    flame_base_y = cy + CELL_SIZE // 2 - 5
                    flame_points = []
                    for i in range(5):
                        offset_x = random.randint(-8, 8)
                        offset_y = flame_base_y - (i * height // 5) + random.randint(-3, 3)
                        flame_points.append((cx + offset_x, offset_y))
                    
                    # Рисуем пламя
                    for i, (px, py) in enumerate(flame_points):
                        if i < len(flame_points) - 1:
                            next_px, next_py = flame_points[i + 1]
                            color_intensity = int(255 - i * 40)
                            pygame.draw.line(s, (255, color_intensity, 0, alpha), (px, py), (next_px, next_py), 4)
                    
                    # Искры
                    for _ in range(step // 2):
                        spark_x = cx + random.randint(-20, 20)
                        spark_y = cy + random.randint(-15, 15)
                        spark_size = random.randint(2, 4)
                        pygame.draw.circle(s, (255, 200, 0, alpha), (spark_x, spark_y), spark_size)
                
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(10)  # Уменьшена задержка для плавности
            
        except Exception as e:
            print(f"Ошибка анимации огненной стены: {e}")
        
        # Создаем барьеры огненной стены
        for wx, wy in wall_cells:
            barrier = {
                'x': wx,
                'y': wy,
                'turns': turns,
                'type': 'fire_wall',
                'damage': self.damage,
                'spell_power': getattr(caster, 'spell_power', 0) if caster else 0,
                'spell_power_multiplier': self.spell_power_multiplier
            }
            if not hasattr(game, 'barriers'):
                game.barriers = []
            game.barriers.append(barrier)
        
        if hasattr(game, 'add_event'):
            game.add_event(f"Создана огненная стена ({len(wall_cells)} клеток)!")
        
        return True  # Успешное применение

class MeteorRainSpell(Spell):
    """Заклинание огня: Метеоритный дождь - падает 4 метеорита на врагов"""
    def __init__(self):
        super().__init__(
            name="Метеоритный дождь",
            damage=30,
            mana_cost=20,
            cooldown=0,
            target_type='area',
            description="С неба падает 4 метеорита. Первый на выбранную цель, остальные на случайных врагов.",
            icon='meteor_rain',
            duration=0,
            school='fire'
        )
        self.spell_power_multiplier = 4  # множитель силы магии для урона
    
    def apply(self, center, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        game = caster.game_ref
        target_x, target_y = center
        
        # Находим всех вражеских юнитов (кроме героев)
        from .units import Hero
        enemies = [u for u in game.units if u.team != caster.team and not isinstance(u, Hero)]
        if not enemies:
            if hasattr(game, 'add_event'):
                game.add_event("Нет вражеских целей для метеоритного дождя!")
            return False
        
        # Первая цель - выбранная клетка (ищем ближайшего врага)
        target_unit = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = abs(enemy.x - target_x) + abs(enemy.y - target_y)
            if dist < min_dist:
                min_dist = dist
                target_unit = enemy
        
        # Если на выбранной клетке нет врага, выбираем ближайшего
        if not target_unit:
            target_unit = enemies[0]
        
        # Список целей: первый - выбранный, остальные 3 - случайные враги (могут повторяться)
        targets = [target_unit]
        for _ in range(3):
            if enemies:  # Проверяем что есть враги
                targets.append(random.choice(enemies))
        
        # Анимация падения метеоритов - все одновременно с маленьким промежутком
        try:
            from .graphics import animate_meteor_rain
            from .config import CELL_SIZE
            import pygame
            
            # Подготовка данных для всех метеоритов
            meteors_data = []
            for meteor_idx, target in enumerate(targets):
                # Проверяем что цель еще жива
                if target.health <= 0 or target not in game.units:
                    continue
                
                target_screen_x = target.x * CELL_SIZE + CELL_SIZE // 2
                target_screen_y = target.y * CELL_SIZE + CELL_SIZE // 2
                
                # Начальная позиция метеорита (сверху экрана с небольшим смещением)
                start_x = target_screen_x + random.randint(-50, 50)
                start_y = -80
                start_px = (start_x, start_y)
                end_px = (target_screen_x, target_screen_y)
                
                # Задержка между метеоритами в кадрах (маленький промежуток)
                delay_frames = meteor_idx * 2  # Каждый следующий метеорит начинает на 2 кадра позже
                meteors_data.append((start_px, end_px, delay_frames))
            
            # Если нет живых целей для анимации - выходим
            if not meteors_data:
                game.add_event("Нет живых целей для метеоритного дождя!")
                return False
            
            # Callback для звука взрыва (будет вызываться для каждого метеорита)
            def play_meteor_explosion():
                if hasattr(game, 'fireball_explosion_sound') and game.fireball_explosion_sound:
                    try:
                        game.fireball_explosion_sound.play()
                    except:
                        pass
            
            # Callback для звука полета
            def play_meteor_flight():
                if hasattr(game, 'fireball_flight_sound') and game.fireball_flight_sound:
                    try:
                        game.fireball_flight_sound.play()
                    except:
                        pass
            
            # Запускаем одновременную анимацию всех метеоритов
            animate_meteor_rain(
                game.screen,
                meteors_data,
                redraw_callback=game.draw,
                explosion_sound_callback=play_meteor_explosion,
                flight_sound_callback=play_meteor_flight
            )
            
            # Наносим урон всем целям ПОСЛЕ анимации
            base_dmg = self.damage
            if caster and hasattr(caster, 'spell_power'):
                base_dmg += self.spell_power_multiplier * caster.spell_power
            
            for target in targets:
                if target.health <= 0 or target not in game.units:
                    continue
                
                dmg = base_dmg
                
                # Находим всех юнитов в радиусе взрыва (волна взрыва вокруг клетки)
                # Радиус взрыва - все 8 соседних клеток + центр (3x3 зона)
                affected_units = []
                target_x, target_y = target.x, target.y
                for unit in game.units:
                    # Только враги получают урон
                    if unit.team != caster.team and not isinstance(unit, Hero):
                        dx = abs(unit.x - target_x)
                        dy = abs(unit.y - target_y)
                        
                        if dx <= 1 and dy <= 1:  # Все клетки в радиусе 1 (3x3 зона)
                            if unit == target:
                                # Основная цель получает полный урон
                                affected_units.append((unit, 1.0))
                            else:
                                # Остальные в радиусе получают 50% урона
                                affected_units.append((unit, 0.5))
                
                # Наносим урон всем пораженным юнитам
                for affected_unit, damage_multiplier in affected_units:
                    if affected_unit.health <= 0 or affected_unit not in game.units:
                        continue
                    
                    unit_dmg = int(dmg * damage_multiplier)
                    health_before = affected_unit.health
                    squad_count_before = getattr(affected_unit, 'squad_count', 1)
                    unit_died = affected_unit.take_damage(unit_dmg, attack_type='magical')
                    actual_damage = health_before - affected_unit.health
                    squad_count_after = getattr(affected_unit, 'squad_count', 1)
                    units_lost = squad_count_before - squad_count_after
                    
                    # Обрабатываем результат урона
                    if unit_died:
                        game.kill_unit(affected_unit)
                        game.animation_manager.animate_queue_fade(affected_unit)
                        if damage_multiplier < 1.0:
                            event_msg = f"Взрыв метеорита убил {affected_unit.unit_type} (урон: {actual_damage})"
                        else:
                            event_msg = f"Метеорит убил {affected_unit.unit_type} (урон: {actual_damage})"
                        if units_lost > 0:
                            event_msg += f", уничтожено {units_lost} юнитов из отряда"
                        game.add_event(event_msg)
                        game.check_game_over()
                    else:
                        if damage_multiplier < 1.0:
                            event_msg = f"Взрыв метеорита ранил {affected_unit.unit_type} (урон: {actual_damage})"
                        else:
                            event_msg = f"Метеорит ударил {affected_unit.unit_type} (урон: {actual_damage})"
                        if units_lost > 0:
                            event_msg += f", потеряно {units_lost} юнитов из отряда"
                        game.add_event(event_msg)
                
        except Exception as e:
            print(f"Ошибка анимации метеоритного дождя: {e}")
        
        return True  # Успешное применение

class IceArrowSpell(Spell):
    """Заклинание воды: Ледяная стрела - наносит урон и снижает скорость и инициативу"""
    def __init__(self):
        super().__init__(
            name="Ледяная стрела",
            damage=18,
            mana_cost=12,
            cooldown=0,
            target_type='enemy',
            description="Наносит урон и снижает скорость на 2 и инициативу на 4 на 2 хода.",
            icon='ice_arrow',
            duration=2,
            school='water'
        )
        self.spell_power_multiplier = 4
        self.speed_reduction = 2
        self.initiative_reduction = 4
    
    def apply(self, target, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        
        game = caster.game_ref
        
        # Анимация ледяной стрелы ПЕРЕД нанесением урона
        try:
            from .graphics import animate_ice_arrow
            from .config import CELL_SIZE
            caster_px = (caster.x * CELL_SIZE + CELL_SIZE//2, caster.y * CELL_SIZE + CELL_SIZE//2)
            target_px = (target.x * CELL_SIZE + CELL_SIZE//2, target.y * CELL_SIZE + CELL_SIZE//2)
            animate_ice_arrow(game.screen, caster_px, target_px, redraw_callback=game.draw)
        except Exception as e:
            print(f"Ошибка анимации ледяной стрелы: {e}")
        
        # Наносим урон ПОСЛЕ анимации попадания
        dmg = self.damage
        if caster and hasattr(caster, 'spell_power'):
            dmg += self.spell_power_multiplier * caster.spell_power
        
        health_before = target.health
        squad_count_before = getattr(target, 'squad_count', 1)
        died = target.take_damage(dmg, attack_type='magical')
        actual_damage = health_before - target.health
        squad_count_after = getattr(target, 'squad_count', 1)
        units_lost = squad_count_before - squad_count_after
        
        # Применяем эффект замедления ПОСЛЕ урона
        duration = self.duration
        if caster and hasattr(caster, 'spell_power'):
            duration += caster.spell_power
        
        # Сохраняем базовые значения если еще не сохранены
        if not hasattr(target, 'ice_arrow_speed_reduced'):
            target.base_speed = getattr(target, 'base_speed', target.speed)
            target.base_initiative = getattr(target, 'base_initiative', target.initiative)
            target.ice_arrow_speed_reduced = True
        
        target.speed = max(1, target.speed - self.speed_reduction)
        target.initiative = max(1, target.initiative - self.initiative_reduction)
        target.ice_arrow_turns = duration
        
        if died:
            game.kill_unit(target)
            game.animation_manager.animate_queue_fade(target)
            event_msg = f"Ледяная стрела убила {target.unit_type} (урон: {actual_damage})"
            if units_lost > 0:
                event_msg += f", уничтожено {units_lost} юнитов из отряда"
            game.add_event(event_msg)
            game.check_game_over()
        else:
            event_msg = f"Ледяная стрела ранила {target.unit_type} (урон: {actual_damage}), снижена скорость и инициатива"
            if units_lost > 0:
                event_msg += f", потеряно {units_lost} юнитов из отряда"
            game.add_event(event_msg)
        
        return True

class PhantomSpell(Spell):
    """Заклинание воды: Фантом - создает союзную копию юнита с синими текстурами"""
    def __init__(self):
        super().__init__(
            name="Фантом",
            damage=0,
            mana_cost=25,
            cooldown=0,
            target_type='ally',
            description="Создает призрачную копию союзного юнита. Копия имеет половину отряда и существует 3 хода.",
            icon='phantom',
            duration=3,
            school='water'
        )
        self.spell_power_multiplier = 0
    
    def apply(self, target, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        
        game = caster.game_ref
        from .config import GRID_WIDTH, GRID_HEIGHT
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
# Импорт отладчика берсерка
try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'debug', 'berserker'))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None
        
        # Проверяем что цель - союзник
        if target.team != caster.team:
            if hasattr(game, 'add_event'):
                game.add_event("Фантом можно применять только на союзников!")
            return False
        
        # Нельзя создавать фантома из героя
        from .units import Hero
        if isinstance(target, Hero):
            if hasattr(game, 'add_event'):
                game.add_event("Нельзя создать фантома из этого юнита!")
            return False
        
        duration = self.duration
        if caster and hasattr(caster, 'spell_power'):
            duration += caster.spell_power
        
        # Находим вражеского героя для определения стороны появления
        enemy_hero = None
        for unit in game.units:
            if isinstance(unit, Hero) and unit.team != caster.team:
                enemy_hero = unit
                break
        
        # Определяем позицию появления фантома (слева или справа сверху от юнита)
        if enemy_hero:
            # Если вражеский герой справа - фантом слева (от врага), иначе справа
            if enemy_hero.x > target.x:
                phantom_x = target.x - 1  # Слева от юнита (дальше от врага)
            else:
                phantom_x = target.x + 1  # Справа от юнита (дальше от врага)
        else:
            # По умолчанию слева
            phantom_x = target.x - 1
        
        phantom_y = target.y - 1  # Сверху на одну клетку
        
        # Если выбранная позиция занята или выходит за границы, пробуем альтернативную
        if not (0 <= phantom_x < GRID_WIDTH) or any(u.x == phantom_x and u.y == phantom_y for u in game.units):
            # Пробуем другую сторону
            if phantom_x == target.x - 1:
                phantom_x = target.x + 1
            else:
                phantom_x = target.x - 1
        
        # Финальная проверка что клетка свободна и в пределах карты
        if not (0 <= phantom_x < GRID_WIDTH and 0 <= phantom_y < GRID_HEIGHT) or any(u.x == phantom_x and u.y == phantom_y for u in game.units):
            if hasattr(game, 'add_event'):
                game.add_event("Невозможно создать фантома здесь!")
            return False
        
        # Анимация создания фантома
        try:
            import pygame
            from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
            
            # Анимация: призрачная копия отлетает в сторону
            target_screen_x = target.x * CELL_SIZE + CELL_SIZE // 2
            target_screen_y = target.y * CELL_SIZE + CELL_SIZE // 2
            phantom_screen_x = phantom_x * CELL_SIZE + CELL_SIZE // 2
            phantom_screen_y = phantom_y * CELL_SIZE + CELL_SIZE // 2
            
            frames = 20
            for frame in range(frames):
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                
                progress = frame / frames
                # Призрачная копия движется от цели к позиции фантома
                copy_x = target_screen_x + (phantom_screen_x - target_screen_x) * progress
                copy_y = target_screen_y + (phantom_screen_y - target_screen_y) * progress
                
                # Полупрозрачная синяя копия
                alpha = int(200 * (1 - progress * 0.5))
                copy_size = int(CELL_SIZE * (0.8 + progress * 0.2))
                
                # Синее свечение
                pygame.draw.circle(s, (100, 150, 255, alpha // 2), (int(copy_x), int(copy_y)), copy_size)
                pygame.draw.circle(s, (150, 200, 255, alpha), (int(copy_x), int(copy_y)), copy_size - 5)
                
                # Искры магии
                for _ in range(5):
                    spark_x = copy_x + random.randint(-15, 15)
                    spark_y = copy_y + random.randint(-15, 15)
                    spark_size = random.randint(2, 4)
                    pygame.draw.circle(s, (200, 220, 255, alpha), (int(spark_x), int(spark_y)), spark_size)
                
                game.screen.blit(s, (0, 0))
                pygame.display.flip()
                pygame.time.delay(10)  # Уменьшена задержка для плавности
        except Exception as e:
            print(f"Ошибка анимации создания фантома: {e}")
        
        # Создаем фантома - копию юнита
        phantom_unit_class = type(target)
        phantom = phantom_unit_class(phantom_x, phantom_y, target.team)
        phantom.is_phantom = True
        phantom.phantom_turns = duration
        phantom.phantom_source = target
        
        # Половина отряда
        original_squad = getattr(target, 'squad_count', 1)
        phantom.squad_count = max(1, original_squad // 2)
        if hasattr(target, 'unit_hp'):
            phantom.unit_hp = target.unit_hp
            phantom.current_unit_hp = target.current_unit_hp
        if hasattr(target, 'max_health'):
            phantom.health = (target.health * phantom.squad_count) // original_squad if original_squad > 0 else target.health
            phantom.max_health = (target.max_health * phantom.squad_count) // original_squad if original_squad > 0 else target.max_health
        
        # Создаем синюю версию изображения
        phantom_image = target.image.copy()
        # Применяем синий фильтр
        for x in range(phantom_image.get_width()):
            for y in range(phantom_image.get_height()):
                pixel = phantom_image.get_at((x, y))
                if pixel.a > 0:  # Если пиксель не прозрачный
                    # Усиливаем синий канал, ослабляем красный и зеленый
                    new_r = max(0, min(255, int(pixel.r * 0.3)))
                    new_g = max(0, min(255, int(pixel.g * 0.5)))
                    new_b = max(0, min(255, int(pixel.b * 1.5)))
                    phantom_image.set_at((x, y), (new_r, new_g, new_b, pixel.a))
        phantom.image = phantom_image
        
        # Добавляем фантома в игру
        game.units.append(phantom)
        # Добавляем в очередь хода
        if hasattr(game, 'turn_queue') and game.turn_queue:
            # Вставляем после текущего юнита или в конец текущего раунда
            try:
                if target in game.turn_queue:
                    target_idx = game.turn_queue.index(target)
                    game.turn_queue.insert(target_idx + 1, phantom)
                else:
                    # Вставляем перед разделителем раунда
                    try:
                        delim_idx = game.turn_queue.index(game._round_delimiter)
                        game.turn_queue.insert(delim_idx, phantom)
                    except ValueError:
                        game.turn_queue.append(phantom)
            except Exception:
                game.turn_queue.append(phantom)
        
        if hasattr(game, 'add_event'):
            game.add_event(f"Создан фантом {target.unit_type} ({phantom.squad_count} юнитов)!")
        
        return True

class ChainLightningSpell(Spell):
    """Заклинание воздуха: Цепная молния - бьёт цель и отскакивает по ближайшим врагам"""
    def __init__(self):
        super().__init__(
            name="Цепная молния",
            damage=25,
            mana_cost=15,
            cooldown=0,
            target_type='enemy',
            description="Молния бьёт цель и отскакивает по 3 ближайшим врагам, нанося уменьшенный на 25% урон.",
            icon='chain_lightning',
            duration=0,
            school='air'
        )
        self.spell_power_multiplier = 6  # множитель силы магии для урона
    
    def apply(self, target, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        
        game = caster.game_ref
        from .units import Hero
        
        # Находим всех вражеских юнитов (кроме героев)
        enemies = [u for u in game.units if u.team != caster.team and not isinstance(u, Hero)]
        if not enemies:
            game.add_event("Нет вражеских целей для цепной молнии!")
            return False
        
        # Список целей: первая - выбранная, остальные 3 - ближайшие враги
        targets = [target]
        hit_targets = {target}  # Множество уже поражённых целей
        
        # Находим 3 ближайших врага (не включая уже поражённых)
        for _ in range(3):
            nearest = None
            min_dist = float('inf')
            last_target = targets[-1]
            
            for enemy in enemies:
                if enemy in hit_targets or enemy.health <= 0:
                    continue
                # Расстояние от последней поражённой цели до этого врага
                dist = abs(enemy.x - last_target.x) + abs(enemy.y - last_target.y)
                if dist < min_dist:
                    min_dist = dist
                    nearest = enemy
            
            if nearest:
                targets.append(nearest)
                hit_targets.add(nearest)
        
        # Анимация цепной молнии
        try:
            from .graphics import animate_chain_lightning
            from .config import CELL_SIZE
            animate_chain_lightning(game.screen, caster, targets, redraw_callback=game.draw)
        except Exception as e:
            print(f"Ошибка анимации цепной молнии: {e}")
        
        # Наносим урон каждой цели
        base_damage = self.damage
        if caster and hasattr(caster, 'spell_power'):
            base_damage += caster.spell_power * self.spell_power_multiplier
        
        # Множитель урона уменьшается на 25% с каждой следующей целью
        damage_multiplier = 1.0
        for idx, tgt in enumerate(targets):
            if tgt.health <= 0 or tgt not in game.units:
                continue
            
            # Первая цель получает полный урон
            if idx == 0:
                damage = base_damage
            else:
                # Каждая следующая цель получает на 25% меньше урона относительно предыдущей
                damage_multiplier *= 0.75  # Уменьшаем множитель на 25%
                damage = int(base_damage * damage_multiplier)
            
            health_before = tgt.health
            squad_count_before = getattr(tgt, 'squad_count', 1)
            unit_died = tgt.take_damage(damage, attack_type='magical')
            actual_damage = health_before - tgt.health
            squad_count_after = getattr(tgt, 'squad_count', 1)
            units_lost = squad_count_before - squad_count_after
            
            if unit_died:
                game.kill_unit(tgt)
                game.animation_manager.animate_queue_fade(tgt)
                event_msg = f"Цепная молния убила {tgt.unit_type} (урон: {actual_damage})"
                if units_lost > 0:
                    event_msg += f", уничтожено {units_lost} юнитов из отряда"
                game.add_event(event_msg)
                game.check_game_over()
            else:
                event_msg = f"Цепная молния поразила {tgt.unit_type} (урон: {actual_damage})"
                if units_lost > 0:
                    event_msg += f", потеряно {units_lost} юнитов из отряда"
                game.add_event(event_msg)
        
        return True

class AccuracySpell(Spell):
    """Заклинание воздуха: Точность - убирает штраф от расстояния и увеличивает урон дальнобойным юнитам на 20%"""
    def __init__(self):
        super().__init__(
            name="Точность",
            damage=0,
            mana_cost=12,
            cooldown=0,
            target_type='ally',
            description="Убирает штраф на стрельбу от расстояния и увеличивает урон дальнобойным юнитам на 20%.",
            icon='accuracy',
            duration=3,
            school='air'
        )
        self.spell_power_multiplier = 0
    
    def apply(self, target, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        
        game = caster.game_ref
        
        # Проверяем что цель - союзник
        if target.team != caster.team:
            game.add_event("Точность можно применять только на союзников!")
            return False
        
        # Проверяем что юнит дальнобойный
        if not hasattr(target, 'is_ranged') or not target.is_ranged:
            game.add_event("Точность можно применять только на дальнобойных юнитов!")
            return False
        
        duration = self.duration
        if caster and hasattr(caster, 'spell_power'):
            duration += caster.spell_power
        
        # Анимация точности
        try:
            from .graphics import animate_accuracy
            from .config import CELL_SIZE
            target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
            animate_accuracy(game.screen, target_px, redraw_callback=game.draw)
        except Exception as e:
            print(f"Ошибка анимации точности: {e}")
        
        # Применяем эффект
        target.accuracy_turns = duration
        target.accuracy_active = True
        game.add_event(f"Точность применена на {target.unit_type}!")
        
        return True

class QuicksandSpell(Spell):
    """Заклинание земли: Зыбучие пески - создаёт лужи грязи, при наступлении юнит заканчивает ход"""
    def __init__(self):
        super().__init__(
            name="Зыбучие пески",
            damage=0,
            mana_cost=10,
            cooldown=0,
            target_type='area',
            description="Создаёт несколько бурлящих луж грязи. Юнит, наступивший на них, мгновенно заканчивает ход.",
            icon='quicksand',
            duration=3,
            school='earth'
        )
        self.spell_power_multiplier = 0
    
    def apply(self, center, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        
        game = caster.game_ref
        
        # Определяем позиции для зыбучих песков (3-5 луж)
        x0, y0 = center
        quicksand_positions = []
        
        # Создаём несколько луж вокруг центра в более обширной области
        positions_to_try = []
        for dx in range(-4, 5):  # Увеличена область с -2 до -4 и с 2 до 4
            for dy in range(-4, 5):
                if dx == 0 and dy == 0:
                    continue
                tx, ty = x0 + dx, y0 + dy
                if 0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT:
                    # Проверяем, нет ли юнита на этой клетке
                    is_empty = True
                    for unit in game.units:
                        if unit.x == tx and unit.y == ty:
                            is_empty = False
                            break
                    if is_empty:
                        positions_to_try.append((tx, ty))
        
        # Выбираем случайные позиции (6-9 штук)
        import random
        num_quicksands = min(random.randint(6, 9), len(positions_to_try))
        if num_quicksands > 0:
            quicksand_positions = random.sample(positions_to_try, num_quicksands)
        else:
            quicksand_positions = []
        
        if not quicksand_positions:
            game.add_event("Нет свободных клеток для зыбучих песков!")
            return False
        
        # Длительность зависит от силы магии
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        # Создаём зыбучие пески (не барьеры, а отдельная система)
        for qx, qy in quicksand_positions:
            game.quicksands.append({
                'x': qx,
                'y': qy,
                'turns': turns,
                'caster': caster,
                'caster_team': caster.team if caster and hasattr(caster, 'team') else None
            })
        
        # Анимация каста зыбучих песков
        try:
            from .graphics import animate_quicksand_cast, animate_quicksand_creation
            from .config import CELL_SIZE
            center_px = (x0 * CELL_SIZE + CELL_SIZE // 2, y0 * CELL_SIZE + CELL_SIZE // 2)
            animate_quicksand_cast(game.screen, center_px, redraw_callback=game.draw)
            
            # Анимация создания зыбучих песков
            quicksand_px_list = [(qx * CELL_SIZE + CELL_SIZE // 2, qy * CELL_SIZE + CELL_SIZE // 2) 
                                for qx, qy in quicksand_positions]
            animate_quicksand_creation(game.screen, quicksand_px_list, redraw_callback=game.draw)
        except Exception as e:
            print(f"Ошибка анимации зыбучих песков: {e}")
        
        game.add_event(f"Зыбучие пески созданы на {len(quicksand_positions)} клетках!")
        return True

class EarthShockSpell(Spell):
    """Заклинание земли: Шок земли - мощное заклинание, урон игнорирует маг защиту"""
    def __init__(self):
        super().__init__(
            name="Шок земли",
            damage=50,
            mana_cost=18,
            cooldown=0,
            target_type='enemy',
            description="Мощное заклинание, наносящее огромный урон, игнорируя магическую защиту.",
            icon='earth_shock',
            duration=0,
            school='earth'
        )
        self.spell_power_multiplier = 8  # Высокий множитель для силы магии
    
    def apply(self, target, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        
        game = caster.game_ref
        
        # Вычисляем урон: базовый + сила магии * множитель
        damage = self.damage
        if caster and hasattr(caster, 'spell_power'):
            damage += caster.spell_power * self.spell_power_multiplier
        
        # Анимация шока земли
        try:
            from .graphics import animate_earth_shock
            from .config import CELL_SIZE
            target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
            animate_earth_shock(game.screen, target_px, redraw_callback=game.draw)
        except Exception as e:
            print(f"Ошибка анимации шока земли: {e}")
        
        # Наносим урон, игнорируя магическую защиту
        # Сопротивление магии будет применено автоматически в take_damage
        health_before = target.health
        squad_count_before = getattr(target, 'squad_count', 1)
        
        # Наносим урон (минимальный урон 1)
        # take_damage автоматически применит сопротивление магии для снижения урона
        unit_died = target.take_damage(damage, attack_type='magical', ignore_magic_defense=True)
        
        actual_damage_dealt = health_before - target.health
        squad_count_after = getattr(target, 'squad_count', 1)
        units_lost = squad_count_before - squad_count_after
        
        if unit_died:
            game.kill_unit(target)
            game.animation_manager.animate_queue_fade(target)
            event_msg = f"Шок земли убил {target.unit_type} (урон: {actual_damage_dealt})"
            if units_lost > 0:
                event_msg += f", уничтожено {units_lost} юнитов из отряда"
            game.add_event(event_msg)
            game.check_game_over()
        else:
            event_msg = f"Шок земли поразил {target.unit_type} (урон: {actual_damage_dealt})"
            if units_lost > 0:
                event_msg += f", потеряно {units_lost} юнитов из отряда"
            game.add_event(event_msg)
        
        return True


class PrayerSpell(Spell):
    """Заклинание света: Молитва - повышает все параметры и залечивает каждый ход"""
    def __init__(self):
        super().__init__(
            name="Молитва",
            damage=0,
            mana_cost=15,
            cooldown=0,
            target_type='ally',
            description="Повышает все параметры юнита на 2 пункта и залечивает каждый ход до максимума.",
            icon='prayer',
            duration=5,
            school='light'
        )
    
    def apply(self, target, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        
        game = caster.game_ref
        
        # Длительность зависит от силы магии
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        # Анимация молитвы
        try:
            from .graphics import animate_prayer
            from .config import CELL_SIZE
            target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
            animate_prayer(game.screen, target_px, redraw_callback=game.draw)
        except Exception as e:
            print(f"Ошибка анимации молитвы: {e}")
        
        # Сохраняем базовые значения для отката
        if not hasattr(target, 'prayer_applied'):
            target.prayer_applied = True
            # Сохраняем базовые значения
            target.prayer_base_attack = getattr(target, 'phys_attack', 0) if hasattr(target, 'attack_type') and target.attack_type == 'physical' else getattr(target, 'magic_attack', 0)
            target.prayer_base_phys_defense = getattr(target, 'phys_defense', 0)
            target.prayer_base_magic_defense = getattr(target, 'magic_defense', 0)
            target.prayer_base_speed = getattr(target, 'speed', 0)
            target.prayer_base_initiative = getattr(target, 'initiative', 0)
        
        # Повышаем все параметры на 2 пункта
        if hasattr(target, 'attack_type') and target.attack_type == 'physical':
            target.phys_attack = getattr(target, 'phys_attack', 0) + 2
        else:
            target.magic_attack = getattr(target, 'magic_attack', 0) + 2
        
        target.phys_defense = getattr(target, 'phys_defense', 0) + 2
        target.magic_defense = getattr(target, 'magic_defense', 0) + 2
        target.speed = getattr(target, 'speed', 0) + 2
        target.initiative = getattr(target, 'initiative', 0) + 2
        
        # Устанавливаем длительность эффекта
        target.prayer_turns = turns
        
        game.add_event(f"Молитва применена на {target.unit_type}! Все параметры повышены на 2 пункта.")
        return True


class BlindnessSpell(Spell):
    """Заклинание света: Ослепление - дебафф для врагов"""
    def __init__(self):
        super().__init__(
            name="Ослепление",
            damage=0,
            mana_cost=12,
            cooldown=0,
            target_type='enemy',
            description="Ослепляет врага: дальнобойные теряют дальнобойную атаку, все наносят на 35% меньше урона, шанс промаха 35%.",
            icon='blindness',
            duration=3,
            school='light'
        )
    
    def apply(self, target, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        
        game = caster.game_ref
        
        # Проверяем отражение через сопротивление магии
        reflected, game_ref = self.check_magic_resist_reflection(target, caster)
        if reflected:
            # Анимация отражения
            try:
                from .graphics import animate_spell_reflection
                from .config import CELL_SIZE
                caster_px = (caster.x * CELL_SIZE + CELL_SIZE // 2, caster.y * CELL_SIZE + CELL_SIZE // 2)
                target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
                animate_spell_reflection(game.screen, target_px, caster_px, redraw_callback=game.draw)
            except Exception as e:
                print(f"Ошибка анимации отражения: {e}")
            
            # Заклинание отражено, эффект не накладывается (ни на цель, ни на кастера)
            game.add_event(f"Ослепление отражено! {target.unit_type.capitalize()} не был ослеплён!")
            return False  # Заклинание отражено, не применено
        
        # Длительность зависит от силы магии
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        
        # Анимация ослепления
        try:
            from .graphics import animate_blindness
            from .config import CELL_SIZE
            target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
            animate_blindness(game.screen, target_px, redraw_callback=game.draw)
        except Exception as e:
            print(f"Ошибка анимации ослепления: {e}")
        
        # Устанавливаем эффект ослепления
        target.blindness_turns = turns
        target.blindness_active = True
        
        game.add_event(f"{target.unit_type.capitalize()} ослеплён!")
        return True