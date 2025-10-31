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
            cooldown=2,
            target_type='ally',
            description="Увеличивает атаку на 25% на 2 хода",
            icon='bless',
            duration=2,
            school='light'
        )
    def apply(self, target, caster=None):
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        target.apply_attack_buff(turns=turns)

class CurseSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Проклятие",
            damage=0,
            mana_cost=5,
            cooldown=2,
            target_type='enemy',
            description="Уменьшает атаку на 25% на 2 хода",
            icon='curse',
            duration=2,
            school='darkness'
        )
    def apply(self, target, caster=None):
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        target.apply_attack_debuff(turns=turns)

class FireballSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Огненный шар",
            damage=30,
            mana_cost=10,
            cooldown=2,
            target_type='enemy',
            description="Наносит 30 урона врагу. Дальность: 3 клетки.",
            icon='fireball',
            duration=0
        )
    def apply(self, target, caster=None):
        dmg = self.damage
        if caster and hasattr(caster, 'spell_power'):
            dmg += 5 * caster.spell_power
        died = target.take_damage(dmg)
        if died and hasattr(target, 'game_ref') and target.game_ref:
            game = target.game_ref
            if target in game.units:
                game.units.remove(target)
                if hasattr(game, 'turn_queue'):
                    game.turn_queue = [u for u in game.turn_queue if u != target]
                game.animate_queue_fade(target)
            if hasattr(game, 'add_event'):
                game.add_event(f"{caster.unit_type.capitalize()} убил {target.unit_type}")
            if hasattr(game, 'check_game_over'):
                game.check_game_over()

# Удалено: заклинание Исцеление выведено из игры

# Удалено: заклинание Щит выведено из игры

class SlowSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Замедление",
            damage=0,
            mana_cost=7,
            cooldown=2,
            target_type='enemy',
            description="Уменьшает инициативу цели на 5 и скорость на 1 на 2 хода.",
            icon='slow',
            duration=2,
            school='earth'
        )
    def apply(self, target, caster=None):
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        if not hasattr(target, 'slow_turns') or target.slow_turns == 0:
            target.base_initiative = getattr(target, 'base_initiative', target.initiative)
            target.initiative = max(1, target.initiative - 5)
            target.base_speed = getattr(target, 'base_speed', target.speed)
            target.speed = max(1, target.speed - 1)
            target.slow_turns = turns
        else:
            target.slow_turns = turns

class FireArrowSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Огненная стрела",
            damage=20,
            mana_cost=10,
            cooldown=2,
            target_type='enemy',
            description="Наносит 20 урона врагу.",
            icon='firearrow',
            duration=0,
            school='fire'
        )
    def apply(self, target, caster=None):
        dmg = self.damage
        if caster and hasattr(caster, 'spell_power'):
            dmg += 5 * caster.spell_power
        died = target.take_damage(dmg)
        if died and hasattr(target, 'game_ref') and target.game_ref:
            game = target.game_ref
            if target in game.units:
                game.units.remove(target)
                if hasattr(game, 'turn_queue'):
                    game.turn_queue = [u for u in game.turn_queue if u != target]
                game.animate_queue_fade(target)
            if hasattr(game, 'add_event'):
                game.add_event(f"{caster.unit_type.capitalize()} убил {target.unit_type}")
            if hasattr(game, 'check_game_over'):
                game.check_game_over()

class DispelSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Снятие чар",
            damage=0,
            mana_cost=4,
            cooldown=2,
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
        # Снимаем огненный щит
        if hasattr(target, 'fire_shield_turns'):
            target.fire_shield_turns = 0
        if hasattr(target, 'fire_shield_damage'):
            target.fire_shield_damage = 0
        if hasattr(target, 'fire_shield_pct'):
            target.fire_shield_pct = 0.0
        # Снимаем обычное ускорение (это не руна скорости)
        if hasattr(target, 'haste_turns'):
            target.haste_turns = 0
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

class HasteSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Ускорение",
            damage=0,
            mana_cost=7,
            cooldown=3,
            target_type='ally',
            description="Увеличивает скорость на 2 и инициативу на 5 на 2 хода.",
            icon='haste',
            duration=2,
            school='air'
        )
    def apply(self, target, caster=None):
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        # Используем общие поля, как у рунической спешки, чтобы логика снятия/окончания работала одинаково
        if not hasattr(target, 'haste_turns') or target.haste_turns == 0:
            target.base_speed = getattr(target, 'base_speed', target.speed)
            target.speed += 2
            target.base_initiative = getattr(target, 'base_initiative', target.initiative)
            target.initiative += 5
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

class RuneShieldSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Руна защиты",
            damage=0,
            mana_cost=7,
            cooldown=3,
            target_type='ally',
            description="Дает +15 к защите на 2 хода.",
            icon='rune_shield',
            duration=2,
            school='rune'
        )
    def apply(self, target, caster=None):
        if getattr(target, 'rune_shield_turns', 0) == 0:
            target.defense += 15
        target.rune_shield_turns = self.duration

class RuneHasteSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Руна скорости",
            damage=0,
            mana_cost=7,
            cooldown=3,
            target_type='ally',
            description="Увеличивает скорость на 2 и инициативу на 5 на 2 хода.",
            icon='rune_haste',
            duration=2,
            school='rune'
        )
    def apply(self, target, caster=None):
        turns = self.duration
        if caster and hasattr(caster, 'spell_power'):
            turns += caster.spell_power
        if not hasattr(target, 'rune_haste_turns') or target.rune_haste_turns == 0:
            target.base_speed = getattr(target, 'base_speed', target.speed)
            target.speed += 2
            target.base_initiative = getattr(target, 'base_initiative', target.initiative)
            target.initiative += 5
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

class ForgetSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Забвение",
            damage=0,
            mana_cost=8,
            cooldown=4,
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

class FrostRingSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Кольцо холода",
            damage=18,
            mana_cost=12,
            cooldown=4,
            target_type='area',
            description="Бьёт по кругу радиусом 1 клетка вокруг выбранной клетки (центр не бьёт).",
            icon='frost_ring',
            duration=0,
            school='water'
        )
    def apply(self, center, caster=None):
        # center — (x, y), game_ref должен быть у caster
        if not caster or not hasattr(caster, 'game_ref'):
            return
        game = caster.game_ref
        x0, y0 = center
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                tx, ty = x0 + dx, y0 + dy
                for unit in list(game.units):
                    if unit.x == tx and unit.y == ty and unit.team != caster.team:
                        dmg = self.damage
                        if caster and hasattr(caster, 'spell_power'):
                            dmg += 5 * caster.spell_power
                        if unit.take_damage(dmg):
                            # Удаляем убитого юнита из игры и очереди
                            if unit in game.units:
                                game.units.remove(unit)
                            if hasattr(game, 'turn_queue') and getattr(game, 'turn_queue'):
                                game.turn_queue = [u for u in game.turn_queue if u != unit]
                            if hasattr(game, 'add_event'):
                                game.add_event(f"{unit.unit_type.capitalize()} погиб от {self.name}")

class RaiseDeadSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Призыв скелета",
            damage=0,
            mana_cost=10,
            cooldown=4,
            target_type='area',
            description="Призывает скелета на выбранной пустой клетке.",
            # Используем идентификатор иконки, ожидаемый интерфейсом
            icon='raise_dead',
            duration=0,
            school='darkness'
        )
    
    def apply(self, center, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return
        game = caster.game_ref
        x, y = center
        # Проверка границ и занятости клетки
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return
        if any(u.x == x and u.y == y for u in game.units):
            return
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
        if hasattr(game, 'turn_queue') and getattr(game, 'turn_queue'):
            try:
                _ = game.turn_queue.index(game._round_delimiter)  # type: ignore[attr-defined]
                game.turn_queue.append(skel)
            except Exception:
                game.turn_queue.append(skel)

class UndeadHealSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Поднятие мёртвых",
            damage=0,
            mana_cost=8,
            cooldown=3,
            target_type='ally',
            description="Лечит только нежить, собирая кости в целебную гору.",
            icon='raise_undead',
            duration=0,
            school='darkness'
        )

    def apply(self, target, caster=None):
        # Лечит только нежить, если она ранена
        if not target or getattr(target, 'team', None) != 'undead':
            return
        # Проверяем, нужно ли лечение
        current_hp = getattr(target, 'health', 0)
        max_hp = getattr(target, 'max_health', 0)
        if current_hp >= max_hp:
            return  # Уже полное здоровье
        # Лечение
        heal = 25
        target.health = min(max_hp, current_hp + heal)

class FireballSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Огненный шар",
            damage=25,
            mana_cost=12,
            cooldown=3,
            target_type='area',
            description="Сбрасывает с неба пылающий шар, бьёт по зоне 3x3 клетки.",
            icon='fireball',
            duration=0,
            school='fire'
        )
    
    def apply(self, center, caster=None):
        if not caster or not hasattr(caster, 'game_ref'):
            return
        game = caster.game_ref
        x, y = center
        # Применение урона по зоне 3x3
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                tx, ty = x + dx, y + dy
                if not (0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT):
                    continue
                for unit in list(game.units):
                    if unit.x == tx and unit.y == ty and unit.team != caster.team:
                        # Пропускаем героев (через проверку типа класса)
                        if hasattr(unit, 'unit_type') and unit.unit_type == 'hero':
                            continue
                        dmg = self.damage
                        if caster and hasattr(caster, 'spell_power'):
                            dmg += 5 * caster.spell_power
                        if unit.take_damage(dmg):
                            if unit in game.units:
                                game.units.remove(unit)
                            if hasattr(game, 'turn_queue') and getattr(game, 'turn_queue'):
                                game.turn_queue = [u for u in game.turn_queue if u != unit]
                            game.add_event(f"{unit.unit_type.capitalize()} погиб от {self.name}")

class StoneSkinSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Каменная кожа",
            damage=0,
            mana_cost=8,
            cooldown=3,
            target_type='ally',
            description="Повышает защиту на 15% + знание героя%.",
            icon='stone_skin',
            duration=0,
            school='earth'
        )
    def apply(self, target, caster=None):
        if not target:
            return
        knowledge = getattr(caster, 'knowledge', 0) if caster else 0
        percent = 0.15 + knowledge / 100.0
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

class FireShieldSpell(Spell):
    def __init__(self):
        super().__init__(
            name="Огненный щит",
            damage=0,
            mana_cost=8,
            cooldown=3,
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