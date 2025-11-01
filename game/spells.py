from .config import GRID_WIDTH, GRID_HEIGHT
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
        died = target.take_damage(dmg, attack_type='magical')
        actual_damage = health_before - target.health
        
        if died and hasattr(caster, 'game_ref'):
            game = caster.game_ref
            game.kill_unit(target)
            game.animation_manager.animate_queue_fade(target)
            game.add_event(f"Огненная стрела убила {target.unit_type} (урон: {actual_damage})")
            game.check_game_over()
        elif hasattr(caster, 'game_ref'):
            game = caster.game_ref
            game.add_event(f"Огненная стрела ранила {target.unit_type} (урон: {actual_damage}, осталось: {target.health}/{target.max_health})")
        
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
                game.add_event(f"Кольцо холода ранило {unit.unit_type} (урон: {actual_damage}, осталось: {unit.health}/{unit.max_health})")
        
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
            for step in range(10):
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                radius = 10 + step * 3
                pygame.draw.circle(s, (150, 0, 180, 90), (cx, cy), radius, 3)
                pygame.draw.circle(s, (220, 120, 255, 80), (cx, cy), max(2, radius-6), 2)
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(16)

            # Этап 2 (теперь вторым): темные частицы вращаются и стягиваются к центру
            particles = []  # [px, py, ang, rad, speed]
            for _ in range(36):
                ang = random.random() * math.tau
                rad = random.randint(10, CELL_SIZE//2 + 8)
                speed = random.uniform(0.6, 1.2)
                px = cx + int(math.cos(ang) * rad)
                py = cy + int(math.sin(ang) * rad)
                particles.append([px, py, ang, rad, speed])
            for step in range(24):
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
                pygame.time.delay(18)

            # Этап 3: призрачное свечение и всплески энергии в центре
            for step in range(16):
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
                pygame.time.delay(18)
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
            target_type='ally',
            description="Лечит только нежить, собирая кости в целебную гору.",
            icon='raise_undead',
            duration=0,
            school='darkness'
        )
        self.heal_amount = 25  # базовое лечение
        self.spell_power_multiplier = 5  # множитель силы магии

    def apply(self, target, caster=None):
        # Лечит только нежить, если она ранена
        if not target or getattr(target, 'team', None) != 'undead':
            return False
        # Проверяем, нужно ли лечение
        current_hp = getattr(target, 'health', 0)
        max_hp = getattr(target, 'max_health', 0)
        if current_hp >= max_hp:
            return False  # Уже полное здоровье
        # Лечение с учетом силы магии
        heal = self.heal_amount
        if caster and hasattr(caster, 'spell_power'):
            heal += self.spell_power_multiplier * caster.spell_power
        target.health = min(max_hp, current_hp + heal)
        return True  # Успешное применение

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
            unit_died = unit.take_damage(dmg, attack_type='magical')
            actual_damage = health_before - unit.health
            
            if unit_died:
                game.kill_unit(unit)
                game.animation_manager.animate_queue_fade(unit)
                game.add_event(f"Огненный шар убил {unit.unit_type} (урон: {actual_damage})")
                game.check_game_over()
            else:
                game.add_event(f"Огненный шар поджёг {unit.unit_type} (урон: {actual_damage}, осталось: {unit.health}/{unit.max_health})")
        
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
        if not caster or not hasattr(caster, 'game_ref'):
            return False
        game = caster.game_ref
        x, y = center
        
        # Проверка границ
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return False
        
        # Вычисляем количество лечения: базовое + сила магии * 10
        heal = self.heal_amount
        if caster and hasattr(caster, 'spell_power'):
            heal += caster.spell_power * 10
        
        # Сначала проверяем, есть ли живой юнит на клетке
        living_unit = None
        for u in game.units:
            if u.x == x and u.y == y:
                living_unit = u
                break
        
        # Если есть живой юнит - лечим его
        if living_unit:
            # Не лечим нежить
            if living_unit.team == 'undead':
                game.add_event("Воскрешение не действует на нежить!")
                return False
            
            # Проверяем, что юнит ранен
            if living_unit.health >= living_unit.max_health:
                game.add_event(f"{living_unit.unit_type.capitalize()} уже полностью здоров!")
                return False
            
            # Лечим
            health_before = living_unit.health
            living_unit.health = min(living_unit.max_health, living_unit.health + heal)
            actual_heal = living_unit.health - health_before
            
            # Простая анимация лечения (желтое свечение)
            try:
                import pygame, random
                from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
                cx = x * CELL_SIZE + CELL_SIZE // 2
                cy = y * CELL_SIZE + CELL_SIZE // 2
                
                for step in range(15):
                    pygame.event.pump()
                    game.draw()
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    radius = 10 + step * 2
                    alpha = max(0, 150 - step * 10)
                    pygame.draw.circle(s, (255, 255, 200, alpha), (cx, cy), radius, 3)
                    game.screen.blit(s, (0,0))
                    pygame.display.flip()
                    pygame.time.delay(25)
            except Exception:
                pass
            
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
        
        # Анимация воскрешения: белые и желтые частицы, божественное свечение
        try:
            import pygame, random, math
            from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
            cx = x * CELL_SIZE + CELL_SIZE // 2
            cy = y * CELL_SIZE + CELL_SIZE // 2
            
            # Этап 1: божественный всплеск света
            for step in range(10):
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                radius = 10 + step * 3
                pygame.draw.circle(s, (255, 255, 200, 90), (cx, cy), radius, 3)
                pygame.draw.circle(s, (255, 240, 120, 80), (cx, cy), max(2, radius-6), 2)
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(16)
            
            # Этап 2: светлые частицы вращаются и стягиваются к центру
            particles = []
            for _ in range(36):
                ang = random.random() * math.tau
                rad = random.randint(10, CELL_SIZE//2 + 8)
                speed = random.uniform(0.6, 1.2)
                px = cx + int(math.cos(ang) * rad)
                py = cy + int(math.sin(ang) * rad)
                particles.append([px, py, ang, rad, speed])
            
            for step in range(24):
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                # Светлый вихрь
                for p in particles:
                    p[2] += 0.25  # вращение
                    p[3] = max(2, p[3] - p[4])  # стягивание к центру
                    p[0] = cx + int(math.cos(p[2]) * p[3])
                    p[1] = cy + int(math.sin(p[2]) * p[3])
                    pygame.draw.circle(s, (255, 250, 200, 170), (int(p[0]), int(p[1])), 3)
                    pygame.draw.circle(s, (255, 255, 255, 110), (int(p[0]), int(p[1])), 1)
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(18)
            
            # Этап 3: божественное свечение и восстановление
            for step in range(16):
                pygame.event.pump()
                game.draw()
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pulse_r = 8 + step * 2
                pulse_a = max(0, 180 - step * 10)
                pygame.draw.circle(s, (255, 255, 200, pulse_a), (cx, cy), pulse_r, 3)
                pygame.draw.circle(s, (255, 240, 120, max(0, pulse_a-40)), (cx, cy), max(2, pulse_r-5), 2)
                # Светлые огни
                for i in range(6):
                    ang = (step*0.4 + i) * 0.8
                    rr = 10 + step
                    fx = cx + int(math.cos(ang) * rr)
                    fy = cy + int(math.sin(ang) * rr)
                    pygame.draw.circle(s, (255, 255, 220, 90), (fx, fy), 4)
                game.screen.blit(s, (0,0))
                pygame.display.flip()
                pygame.time.delay(18)
        except Exception:
            pass
        
        # Воскрешаем юнита
        unit_class = corpse.get('unit_class')
        if unit_class:
            try:
                # Создаем нового юнита того же класса
                new_unit = unit_class(x, y, corpse['team'])
                # Восстанавливаем здоровье на heal_amount
                new_unit.health = min(new_unit.max_health, heal)
                new_unit.game_ref = game
                game.units.append(new_unit)
                # Добавляем в очередь хода
                if hasattr(game, 'turn_queue') and hasattr(game, '_round_delimiter'):
                    try:
                        delim_index = game.turn_queue.index(game._round_delimiter)
                        game.turn_queue.insert(delim_index, new_unit)
                    except (ValueError, AttributeError):
                        game.turn_queue.append(new_unit)
                game.corpses.remove(corpse)
                game.add_event(f"Воскрешен {new_unit.unit_type}!")
                return True  # Успешное применение
            except Exception:
                pass
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
        
        # Запоминаем здоровье до лечения
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
                for _ in range(30):
                    angle = random.random() * math.tau
                    distance = random.randint(30, 60)
                    px = cx + int(math.cos(angle) * distance)
                    py = cy + int(math.sin(angle) * distance)
                    particles.append([px, py, angle, distance])
                
                for step in range(20):
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
                    pygame.time.delay(20)
                
                # Этап 2: Ледяная корка покрывает юнита
                for step in range(15):
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
                    for i in range(6):
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
        
        # Наносим урон (магический)
        unit_died = target.take_damage(damage, attack_type='magical')
        actual_damage = health_before - target.health
        
        # Анимация молнии
        if hasattr(caster, 'game_ref'):
            game = caster.game_ref
            try:
                import pygame, random, math
                from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
                cx = target.x * CELL_SIZE + CELL_SIZE // 2
                cy = target.y * CELL_SIZE + CELL_SIZE // 2
                
                # Молния бьёт!
                for strike in range(3):  # 3 удара молнии
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
                    pygame.time.delay(50)
                    
                    # Пауза между ударами
                    if strike < 2:
                        pygame.event.pump()
                        game.draw()
                        pygame.display.flip()
                        pygame.time.delay(40)
                
                # Рассеивание
                for step in range(10):
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
                    pygame.time.delay(30)
                
                if unit_died:
                    game.kill_unit(target)
                    game.animation_manager.animate_queue_fade(target)
                    game.add_event(f"Молния убила {target.unit_type} (урон: {actual_damage})")
                    game.check_game_over()
                else:
                    game.add_event(f"Молния ударила {target.unit_type} (урон: {actual_damage}, осталось: {target.health}/{target.max_health})")
            except Exception:
                pass
        else:
            # Если нет анимации, всё равно нужно убрать юнита
            if unit_died and hasattr(caster, 'game_ref'):
                game = caster.game_ref
                game.kill_unit(target)
                game.animation_manager.animate_queue_fade(target)
                game.add_event(f"Молния убила {target.unit_type} (урон: {actual_damage})")
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
                pygame.time.delay(30)
            
            # Этап 2: Шипы поднимаются
            for step in range(15):
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
                pygame.time.delay(35)
            
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
                pygame.time.delay(30)
                
        except Exception:
            pass
        
        # Наносим урон всем юнитам в зоне
        for unit in affected_units:
            health_before = unit.health
            unit_died = unit.take_damage(damage, attack_type='physical')
            actual_damage = health_before - unit.health
            
            if unit_died:
                game.kill_unit(unit)
                game.animation_manager.animate_queue_fade(unit)
                game.add_event(f"Каменные шипы убили {unit.unit_type} (урон: {actual_damage})")
            else:
                game.add_event(f"Каменные шипы ранили {unit.unit_type} (урон: {actual_damage})")
        
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
                for step in range(25):
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
                    pygame.time.delay(30)
                
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
            for step in range(15):
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
                pygame.time.delay(30)
            
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
                    pygame.time.delay(30)
                
                # Этап 2: Темная аура окружает меч
                for step in range(10):
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
                    pygame.time.delay(35)
                
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