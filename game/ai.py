"""
ИИ для бота-противника
Знает механики игры и умело применяет их
"""
import random
import math
from .units import Hero
from .config import CELL_SIZE, GRID_WIDTH, GRID_HEIGHT


class AIController:
    """Контроллер ИИ для управления юнитами бота"""
    
    def __init__(self, game, ai_team):
        """
        Инициализация ИИ
        :param game: Ссылка на объект Game
        :param ai_team: Команда, которой управляет ИИ (например, 'undead', 'demon')
        """
        self.game = game
        self.ai_team = ai_team
        self.current_state = "Ожидание"
        self.current_action = "Нет"
        self.last_decision = "Не было"
        
    def is_ai_turn(self):
        """Проверяет, является ли текущий ход ходом ИИ"""
        if not self.game.selected_unit:
            return False
        return self.game.selected_unit.team == self.ai_team
    
    def get_allies(self):
        """Возвращает список союзных юнитов (исключая героев)"""
        return [u for u in self.game.units if u.team == self.ai_team and not isinstance(u, Hero)]
    
    def get_enemies(self):
        """Возвращает список вражеских юнитов (исключая героев)"""
        return [u for u in self.game.units if u.team != self.ai_team and not isinstance(u, Hero)]
    
    def get_distance(self, unit1, unit2):
        """Вычисляет расстояние между двумя юнитами (манхэттенское)"""
        return abs(unit1.x - unit2.x) + abs(unit1.y - unit2.y)
    
    def can_reach_cell(self, unit, target_x, target_y):
        """Проверяет, может ли юнит достичь указанной клетки"""
        if hasattr(self.game, 'get_reachable_cells'):
            reachable = self.game.get_reachable_cells(unit.x, unit.y, unit.move_points_left)
            return (target_x, target_y) in reachable
        return False
    
    def evaluate_target(self, attacker, target):
        """
        Оценивает приоритет цели для атаки
        Возвращает значение: чем выше, тем приоритетнее цель
        """
        if not target:
            return 0
        
        score = 0
        
        # Приоритет 1: Убить слабых врагов (низкое здоровье)
        health_ratio = target.health / target.max_health if target.max_health > 0 else 1
        score += (1 - health_ratio) * 50  # Чем ниже здоровье, тем выше приоритет
        
        # Приоритет 2: Убить важные цели (герои)
        if isinstance(target, Hero):
            score += 100
        
        # Приоритет 3: Атаковать магов (опасные, но хрупкие)
        if hasattr(target, 'is_ranged') and target.is_ranged and not isinstance(target, Hero):
            score += 30
        
        # Приоритет 4: Учитываем расстояние - предпочитаем ближние цели
        distance = self.get_distance(attacker, target)
        if distance == 1 and hasattr(attacker, 'is_ranged') and attacker.is_ranged:
            # Лучники в ближнем бою - меньше приоритет, но можем убить слабого
            if health_ratio < 0.3:
                score += 20  # Слабый враг - можно добить
            else:
                score -= 20  # Сильный враг в ближнем бою - не стоит
        else:
            score += max(0, 20 - distance * 5)  # Ближе = лучше
        
        # Приоритет 5: Избегаем атаковать защищающихся юнитов (если есть лучшая цель)
        if hasattr(target, '_defend_this_round') and target._defend_this_round:
            score -= 15
        
        return score
    
    def find_best_attack_target(self, attacker):
        """
        Находит лучшую цель для атаки текущего юнита
        :return: (target, damage_estimate) или (None, 0)
        """
        enemies = self.get_enemies()
        if not enemies:
            return None, 0
        
        best_target = None
        best_score = -float('inf')
        
        for enemy in enemies:
            # Проверяем, можем ли атаковать
            if not attacker.can_attack(enemy.x, enemy.y, self.game.units):
                continue
            
            score = self.evaluate_target(attacker, enemy)
            
            if score > best_score:
                best_score = score
                best_target = enemy
        
        # Оцениваем урон
        damage = 0
        if best_target:
            if hasattr(attacker, 'is_ranged') and attacker.is_ranged:
                distance = self.get_distance(attacker, best_target)
                if distance == 1:
                    damage = max(1, attacker.get_current_attack() // 2)
                else:
                    damage = attacker.ranged_damage(best_target.x, best_target.y)
            else:
                damage = attacker.get_current_attack()
        
        return best_target, damage
    
    def evaluate_spell_target(self, spell, caster, target):
        """Оценивает использование заклинания на цель"""
        if not target:
            return 0
        
        score = 0
        
        # Атакующие заклинания
        if spell.target_type == 'enemy':
            # Оценка как обычной атаки, но с учетом урона заклинания
            base_score = self.evaluate_target(caster, target)
            # Заклинания обычно наносят хороший урон
            if hasattr(spell, 'damage'):
                score = base_score + spell.damage * 2
            else:
                score = base_score + 30  # Бонус за заклинание
        
        # Восстанавливающие заклинания
        elif spell.target_type == 'ally':
            if target.health < target.max_health * 0.5:  # Низкое здоровье
                score = 50
                if isinstance(target, Hero):
                    score += 30  # Герой важен
            else:
                score = 10  # Не критично
        
        return score
    
    def find_best_spell_action(self, hero):
        """
        Находит лучшее действие с заклинанием для героя
        :return: (spell_index, target, target_pos) или (None, None, None)
        """
        if not isinstance(hero, Hero):
            return None, None, None
        
        if hero.used_spell_this_round or not hero.spells:
            return None, None, None
        
        best_score = 0
        best_spell_idx = None
        best_target = None
        best_pos = None
        
        for idx, spell in enumerate(hero.spells):
            if hero.mana < spell.mana_cost:
                continue
            
            # Атакующие заклинания
            if spell.target_type == 'enemy':
                enemies = self.get_enemies()
                # Фильтруем героев из списка целей
                valid_enemies = [e for e in enemies if not isinstance(e, Hero)]
                for enemy in valid_enemies:
                    score = self.evaluate_spell_target(spell, hero, enemy)
                    
                    # Для AOE заклинаний учитываем несколько целей
                    if hasattr(spell, 'area') and spell.area:
                        # Оцениваем область (например, fireball 3x3)
                        area_score = score
                        for other_enemy in valid_enemies:
                            if other_enemy != enemy and not isinstance(other_enemy, Hero):
                                distance = self.get_distance(enemy, other_enemy)
                                if distance <= 2:  # В зоне взрыва
                                    area_score += self.evaluate_spell_target(spell, hero, other_enemy) * 0.5
                        
                        if area_score > best_score:
                            best_score = area_score
                            best_spell_idx = idx
                            best_target = enemy
                            best_pos = (enemy.x, enemy.y)
                    else:
                        if score > best_score:
                            best_score = score
                            best_spell_idx = idx
                            best_target = enemy
                            best_pos = (enemy.x, enemy.y)
            
            # Поддерживающие заклинания
            elif spell.target_type == 'ally':
                allies = self.get_allies()
                # Фильтруем героев из списка целей
                valid_allies = [a for a in allies if not isinstance(a, Hero)]
                for ally in valid_allies:
                    score = self.evaluate_spell_target(spell, hero, ally)
                    if score > best_score and score > 40:  # Только если действительно нужно
                        best_score = score
                        best_spell_idx = idx
                        best_target = ally
                        best_pos = (ally.x, ally.y)
        
        return best_spell_idx, best_target, best_pos
    
    def find_best_move_position(self, unit, preferred_target=None):
        """
        Находит лучшую позицию для перемещения юнита
        :param unit: Юнит для перемещения
        :param preferred_target: Предпочтительная цель (для атаки или защиты)
        :return: (x, y) или None
        """
        if not hasattr(unit, 'move_points_left') or unit.move_points_left <= 0:
            return None
        
        if hasattr(self.game, 'get_reachable_cells'):
            reachable = self.game.get_reachable_cells(unit.x, unit.y, unit.move_points_left)
        else:
            return None
        
        if not reachable:
            return None
        
        best_pos = None
        best_score = -float('inf')
        
        enemies = self.get_enemies()
        
        for x, y in reachable:
            score = 0
            
            # Если есть предпочтительная цель, двигаемся к ней
            if preferred_target:
                distance = abs(x - preferred_target.x) + abs(y - preferred_target.y)
                score += 30 - distance * 3  # Ближе = лучше
            
            # Рассчитываем расстояние до всех врагов
            for enemy in enemies:
                dist = abs(x - enemy.x) + abs(y - enemy.y)
                
                # Для ближних бойцов - подходим ближе
                if not hasattr(unit, 'is_ranged') or not unit.is_ranged:
                    if dist == 1:
                        score += 40  # Можем атаковать
                    else:
                        score += max(0, 20 - dist * 2)
                
                # Для дальнобойных - держим дистанцию
                else:
                    if dist == 1:
                        score -= 30  # Избегаем ближнего боя
                    elif dist <= 3:
                        score += 20  # Хорошая дистанция
                    elif dist > 8:
                        score -= 10  # Слишком далеко
            
            # Избегаем клеток, рядом с которыми много врагов
            nearby_enemies = sum(1 for e in enemies 
                               if abs(e.x - x) + abs(e.y - y) == 1)
            if nearby_enemies > 2:
                score -= 20
            
            if score > best_score:
                best_score = score
                best_pos = (x, y)
        
        return best_pos
    
    def find_best_retreat_position(self, unit, nearby_enemy, all_enemies):
        """
        Находит лучшую позицию для отступления дальнобойного юнита от рядом стоящего врага
        Пытается отойти так, чтобы можно было стрелять и при этом быть подальше от врага
        :param unit: Дальнобойный юнит
        :param nearby_enemy: Враг, который стоит рядом
        :param all_enemies: Все враги
        :return: (x, y) позиция для отступления или None
        """
        if not hasattr(unit, 'move_points_left') or unit.move_points_left <= 0:
            return None
        
        if hasattr(self.game, 'get_reachable_cells'):
            reachable = self.game.get_reachable_cells(unit.x, unit.y, unit.move_points_left)
        else:
            return None
        
        if not reachable:
            return None
        
        best_pos = None
        best_score = -float('inf')
        
        for x, y in reachable:
            score = 0
            
            # Высокий приоритет - отойти от рядом стоящего врага
            distance_from_nearby = abs(x - nearby_enemy.x) + abs(y - nearby_enemy.y)
            score += distance_from_nearby * 10  # Чем дальше, тем лучше
            
            # Проверяем, нет ли врагов рядом с новой позицией
            adjacent_positions = [
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1)
            ]
            has_enemy_adjacent = False
            for adj_x, adj_y in adjacent_positions:
                for enemy in all_enemies:
                    if enemy.x == adj_x and enemy.y == adj_y:
                        has_enemy_adjacent = True
                        break
                if has_enemy_adjacent:
                    break
            
            if has_enemy_adjacent:
                score -= 100  # Штраф, если после отступления всё равно будет враг рядом
            
            # Бонус, если можем стрелять по врагам с новой позиции
            for enemy in all_enemies:
                distance_to_enemy = abs(x - enemy.x) + abs(y - enemy.y)
                if distance_to_enemy > 1:  # Не ближний бой
                    # Проверяем, можем ли стрелять (нет врагов рядом с новой позицией)
                    if not has_enemy_adjacent:
                        score += 20 - distance_to_enemy  # Предпочитаем оптимальную дистанцию
            
            if score > best_score:
                best_score = score
                best_pos = (x, y)
        
        # Возвращаем только если действительно можем отойти (не останемся рядом с врагом)
        if best_pos:
            final_distance = abs(best_pos[0] - nearby_enemy.x) + abs(best_pos[1] - nearby_enemy.y)
            if final_distance > 1:
                return best_pos
        
        return None
    
    def should_defend(self, unit):
        """
        Решает, должен ли юнит использовать защиту
        :return: True если стоит защищаться
        """
        if isinstance(unit, Hero):
            return False  # Герои не защищаются
        
        enemies = self.get_enemies()
        nearby_enemies = [e for e in enemies 
                         if self.get_distance(unit, e) <= 2]
        
        # Защищаемся, если:
        # 1. Низкое здоровье (< 40%)
        # 2. Рядом много врагов (>= 2)
        health_ratio = unit.health / unit.max_health if unit.max_health > 0 else 1
        
        if health_ratio < 0.4 and len(nearby_enemies) >= 2:
            return True
        
        return False
    
    def make_decision(self):
        """
        Принимает решение для текущего активного юнита
        Выполняет действие: атака, заклинание, перемещение или защита
        :return: True если действие выполнено, False если нужно пропустить ход
        """
        if not self.is_ai_turn():
            self.current_state = "Не ход ИИ"
            self.current_action = "Ожидание"
            return False
        
        unit = self.game.selected_unit
        if not unit:
            self.current_state = "Нет активного юнита"
            self.current_action = "Ожидание"
            return False
        
        self.current_state = f"Ход {unit.unit_type} ({unit.team})"
        
        # Герой - проверяем заклинания
        if isinstance(unit, Hero) and not unit.used_spell_this_round:
            self.current_action = "Проверка заклинаний героя"
            # Если заклинание уже выбрано, применяем его
            if unit.selected_spell is not None:
                self.current_action = f"Применение заклинания {unit.selected_spell}"
                # Ищем цель для применения заклинания
                spell = unit.spells[unit.selected_spell]
                enemies = self.get_enemies()
                allies = self.get_allies()
                
                if spell.target_type == 'enemy' and enemies:
                    # Ищем лучшую цель для атакующего заклинания (исключая героев)
                    valid_targets = [e for e in enemies if not isinstance(e, Hero)]
                    if valid_targets:
                        best_target = max(valid_targets, key=lambda e: self.evaluate_spell_target(spell, unit, e))
                        target_pos = (best_target.x * CELL_SIZE + CELL_SIZE // 2,
                                    best_target.y * CELL_SIZE + CELL_SIZE // 2)
                        self.current_action = f"Применение заклинания на {best_target.unit_type}"
                        self.game.handle_click(target_pos, True)
                        self.last_decision = f"Применено заклинание на {best_target.unit_type}"
                        return True
                elif spell.target_type == 'ally' and allies:
                    # Ищем лучшую цель для поддерживающего заклинания (исключая героев)
                    valid_targets = [a for a in allies if not isinstance(a, Hero)]
                    if valid_targets:
                        best_target = max(valid_targets, key=lambda e: self.evaluate_spell_target(spell, unit, e))
                        if best_target.health < best_target.max_health * 0.7:
                            target_pos = (best_target.x * CELL_SIZE + CELL_SIZE // 2,
                                        best_target.y * CELL_SIZE + CELL_SIZE // 2)
                            self.current_action = f"Применение поддерживающего заклинания на {best_target.unit_type}"
                            self.game.handle_click(target_pos, True)
                            self.last_decision = f"Применено поддерживающее заклинание на {best_target.unit_type}"
                            return True
            
            # Если заклинание не выбрано, выбираем лучшее
            spell_idx, spell_target, spell_pos = self.find_best_spell_action(unit)
            
            if spell_idx is not None and spell_pos is not None:
                # Устанавливаем заклинание напрямую без открытия книги
                unit.selected_spell = spell_idx
                # Получаем заклинание по индексу (spells - это список)
                if spell_idx < len(unit.spells):
                    spell = unit.spells[spell_idx]
                    spell_name = spell.name if hasattr(spell, 'name') else f"Заклинание {spell_idx}"
                else:
                    self.current_action = f"Неверный индекс заклинания: {spell_idx}"
                    return False
                
                # Закрываем книгу если она была открыта (не должно быть видно игроку)
                if self.game.spellbook_open:
                    self.game.spellbook_open = False
                
                # Применяем заклинание сразу на позицию
                target_x, target_y = spell_pos
                target_pos = (target_x * CELL_SIZE + CELL_SIZE // 2,
                             target_y * CELL_SIZE + CELL_SIZE // 2)
                
                # Проверяем тип заклинания
                if spell.target_type == 'area':
                    # Для area заклинаний применяем на позицию
                    self.current_action = f"Применение {spell_name} на позицию ({target_x}, {target_y})"
                    self.game.handle_click(target_pos, True)
                    self.last_decision = f"Применено {spell_name} на позицию"
                    return True
                elif spell_target:
                    # Для обычных заклинаний применяем на цель
                    target_pos = (spell_target.x * CELL_SIZE + CELL_SIZE // 2,
                                 spell_target.y * CELL_SIZE + CELL_SIZE // 2)
                    self.current_action = f"Применение {spell_name} на {spell_target.unit_type}"
                    self.game.handle_click(target_pos, True)
                    self.last_decision = f"Применено {spell_name} на {spell_target.unit_type}"
                    return True
                else:
                    self.current_action = f"Выбрано заклинание {spell_name}, но нет цели"
                    self.last_decision = f"Не удалось применить {spell_name}"
                    return False
            else:
                self.current_action = "Нет подходящих заклинаний"
        
        # Проверяем защиту
        if not isinstance(unit, Hero) and not unit.has_attacked and self.should_defend(unit):
            self.current_action = "Использование защиты"
            self.last_decision = "Активирована защита"
            # Используем защиту (skip_button_rect теперь кнопка защиты)
            defend_pos = (self.game.skip_button_rect.x + self.game.skip_button_rect.width // 2,
                         self.game.skip_button_rect.y + self.game.skip_button_rect.height // 2)
            self.game.handle_click(defend_pos, True)
            return True
        
        # Проверяем атаку
        if not unit.has_attacked:
            # Сначала проверяем, можем ли атаковать цели, которые уже в пределах досягаемости
            enemies = self.get_enemies()
            reachable_targets = []
            
            # Для ближних бойцов ищем цели на расстоянии 1
            if not (hasattr(unit, 'is_ranged') and unit.is_ranged):
                for enemy in enemies:
                    distance = self.get_distance(unit, enemy)
                    if distance == 1 and unit.can_attack(enemy.x, enemy.y, self.game.units):
                        reachable_targets.append((enemy, self.evaluate_target(unit, enemy)))
            
            # Для дальнобойных ищем цели в пределах досягаемости
            else:
                # Проверяем, есть ли враги рядом
                has_nearby_enemy = False
                adjacent_positions = [
                    (unit.x + 1, unit.y),
                    (unit.x - 1, unit.y),
                    (unit.x, unit.y + 1),
                    (unit.x, unit.y - 1)
                ]
                for adj_x, adj_y in adjacent_positions:
                    for enemy in enemies:
                        if enemy.x == adj_x and enemy.y == adj_y:
                            has_nearby_enemy = True
                            break
                    if has_nearby_enemy:
                        break
                
                for enemy in enemies:
                    distance = self.get_distance(unit, enemy)
                    if distance == 1:
                        # Ближний бой - можно атаковать
                        if unit.can_attack(enemy.x, enemy.y, self.game.units):
                            score = self.evaluate_target(unit, enemy)
                            reachable_targets.append((enemy, score))
                    elif not has_nearby_enemy:
                        # Дальнобойная атака - только если рядом нет врагов
                        if unit.can_attack(enemy.x, enemy.y, self.game.units):
                            score = self.evaluate_target(unit, enemy)
                            reachable_targets.append((enemy, score))
            
            # Если есть цели в пределах досягаемости - атакуем лучшую
            if reachable_targets:
                best_reachable = max(reachable_targets, key=lambda x: x[1])[0]
                self.current_action = f"Атака {best_reachable.unit_type} на расстоянии {self.get_distance(unit, best_reachable)}"
                attack_pos = (best_reachable.x * CELL_SIZE + CELL_SIZE // 2,
                            best_reachable.y * CELL_SIZE + CELL_SIZE // 2)
                self.game.handle_click(attack_pos, True)
                self.last_decision = f"Атака по {best_reachable.unit_type}"
                return True
            
            # Если нет целей в пределах досягаемости, ищем лучшую цель для приближения
            # Для дальнобойных сначала проверяем, нужно ли отойти от рядом стоящих врагов
            if hasattr(unit, 'is_ranged') and unit.is_ranged:
                # Проверяем, есть ли враги рядом
                adjacent_positions = [
                    (unit.x + 1, unit.y),
                    (unit.x - 1, unit.y),
                    (unit.x, unit.y + 1),
                    (unit.x, unit.y - 1)
                ]
                nearby_enemy = None
                for adj_x, adj_y in adjacent_positions:
                    for enemy in enemies:
                        if enemy.x == adj_x and enemy.y == adj_y:
                            nearby_enemy = enemy
                            break
                    if nearby_enemy:
                        break
                
                # Если рядом враг, пытаемся отойти, чтобы выстрелить
                if nearby_enemy and hasattr(unit, 'move_points_left') and unit.move_points_left > 0:
                    # Ищем лучшую позицию для отступления (подальше от врага, но с возможностью стрелять)
                    best_retreat = self.find_best_retreat_position(unit, nearby_enemy, enemies)
                    if best_retreat and (best_retreat[0] != unit.x or best_retreat[1] != unit.y):
                        self.current_action = f"Отход от {nearby_enemy.unit_type} для стрельбы"
                        move_pos = (best_retreat[0] * CELL_SIZE + CELL_SIZE // 2,
                                  best_retreat[1] * CELL_SIZE + CELL_SIZE // 2)
                        old_x, old_y = unit.x, unit.y
                        old_mp = getattr(unit, 'move_points_left', 0)
                        self.game.handle_click(move_pos, True)
                        moved = (unit.x != old_x) or (unit.y != old_y) or (getattr(unit, 'move_points_left', 0) < old_mp)
                        if moved:
                            self.last_decision = f"Отход для стрельбы"
                            return True
                        else:
                            self.current_action = "Отход не удался"
            
            # Ищем достижимую цель для атаки
            # Сначала проверяем, какие враги достижимы с учетом текущих очков движения
            target, estimated_damage = self.find_best_attack_target(unit)
            reachable_enemy_for_attack = None
            
            if target and hasattr(unit, 'move_points_left') and unit.move_points_left > 0:
                # Проверяем, можем ли достичь позиции для атаки с текущими ОД
                can_attack_now = unit.can_attack(target.x, target.y, self.game.units)
                
                if not can_attack_now:
                    # Нужно подойти ближе - проверяем достижимость
                    # Для ближних юнитов нужно достичь клетки рядом с целью
                    # Для дальнобойных - нужна линия видимости
                    if hasattr(self.game, 'get_reachable_cells'):
                        reachable = self.game.get_reachable_cells(unit.x, unit.y, unit.move_points_left)
                        
                        # Для ближних юнитов проверяем, есть ли доступные клетки рядом с целью
                        if not (hasattr(unit, 'is_ranged') and unit.is_ranged):
                            adjacent_to_target = [
                                (target.x + 1, target.y),
                                (target.x - 1, target.y),
                                (target.x, target.y + 1),
                                (target.x, target.y - 1)
                            ]
                            can_reach_attack_pos = any(pos in reachable for pos in adjacent_to_target)
                            if can_reach_attack_pos:
                                reachable_enemy_for_attack = target
                        else:
                            # Для дальнобойных - проверяем, есть ли достижимые позиции для стрельбы
                            # Упрощенная проверка: если расстояние <= move_points + текущее расстояние
                            current_distance = self.get_distance(unit, target)
                            if current_distance <= unit.move_points_left + 3:  # +3 для запаса дистанции стрельбы
                                reachable_enemy_for_attack = target
                    
                    # Если цель недостижима - ищем ближайшего достижимого врага
                    if not reachable_enemy_for_attack:
                        self.current_action = f"Цель {target.unit_type} недостижима (расстояние: {self.get_distance(unit, target)}, ОД: {unit.move_points_left})"
                        # Находим ближайших врагов, которых можем достичь
                        closest_reachable = None
                        min_distance = float('inf')
                        
                        for enemy in enemies:
                            distance = self.get_distance(unit, enemy)
                            # Для ближних - проверяем достижимость клеток рядом с врагом
                            if not (hasattr(unit, 'is_ranged') and unit.is_ranged):
                                if distance <= unit.move_points_left + 1:  # +1 так как атакуем с соседней клетки
                                    if distance < min_distance:
                                        min_distance = distance
                                        closest_reachable = enemy
                            else:
                                # Для дальнобойных - более гибкий подход
                                if distance <= unit.move_points_left + 3:
                                    if distance < min_distance:
                                        min_distance = distance
                                        closest_reachable = enemy
                        
                        if closest_reachable:
                            reachable_enemy_for_attack = closest_reachable
                            self.current_action = f"Переключение на достижимого врага {closest_reachable.unit_type}"
                else:
                    # Можем атаковать прямо сейчас
                    self.current_action = f"Атака {target.unit_type} на расстоянии {self.get_distance(unit, target)}"
                    attack_pos = (target.x * CELL_SIZE + CELL_SIZE // 2,
                                target.y * CELL_SIZE + CELL_SIZE // 2)
                    self.game.handle_click(attack_pos, True)
                    self.last_decision = f"Атака по {target.unit_type}"
                    return True
            
            # Если нашли достижимую цель - двигаемся к ней
            if reachable_enemy_for_attack:
                best_move = self.find_best_move_position(unit, reachable_enemy_for_attack)
                if best_move and (best_move[0] != unit.x or best_move[1] != unit.y):
                    # Перемещаемся
                    self.current_action = f"Перемещение к {reachable_enemy_for_attack.unit_type} ({reachable_enemy_for_attack.x}, {reachable_enemy_for_attack.y})"
                    move_pos = (best_move[0] * CELL_SIZE + CELL_SIZE // 2,
                              best_move[1] * CELL_SIZE + CELL_SIZE // 2)
                    old_x, old_y = unit.x, unit.y
                    old_mp = getattr(unit, 'move_points_left', 0)
                    self.game.handle_click(move_pos, True)
                    moved = (unit.x != old_x) or (unit.y != old_y) or (getattr(unit, 'move_points_left', 0) < old_mp)
                    if moved:
                        self.last_decision = f"Перемещение к достижимой цели {reachable_enemy_for_attack.unit_type}"
                        return True
                    else:
                        self.current_action = "Перемещение не удалось - пропуск хода"
                else:
                    self.current_action = "Нет доступной позиции для перемещения"
            else:
                self.current_action = "Нет достижимых целей для атаки"
        
        # Если не атаковали, перемещаемся к ближайшей цели
        if not unit.has_attacked and hasattr(unit, 'move_points_left') and unit.move_points_left > 0:
            enemies = self.get_enemies()
            if enemies:
                nearest_enemy = min(enemies, key=lambda e: self.get_distance(unit, e))
                best_move = self.find_best_move_position(unit, nearest_enemy)
                
                if best_move:
                    self.current_action = f"Перемещение к ближайшему врагу {nearest_enemy.unit_type}"
                    move_pos = (best_move[0] * CELL_SIZE + CELL_SIZE // 2,
                              best_move[1] * CELL_SIZE + CELL_SIZE // 2)
                    self.game.handle_click(move_pos, True)
                    self.last_decision = f"Перемещение к врагу {nearest_enemy.unit_type}"
                    return True
                else:
                    self.current_action = "Не могу достичь ближайшего врага"
        
        # Пропускаем ход
        self.current_action = "Пропуск хода"
        self.last_decision = "Ход пропущен"
        skip_pos = (self.game.skip_button_rect.x + self.game.skip_button_rect.width // 2,
                   self.game.skip_button_rect.y + self.game.skip_button_rect.height // 2)
        self.game.handle_click(skip_pos, True)
        return True

