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
            return False
        
        unit = self.game.selected_unit
        if not unit:
            return False
        
        # Герой - проверяем заклинания
        if isinstance(unit, Hero) and not unit.used_spell_this_round:
            # Если заклинание уже выбрано, применяем его
            if unit.selected_spell is not None:
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
                        self.game.handle_click(target_pos)
                        return True
                elif spell.target_type == 'ally' and allies:
                    # Ищем лучшую цель для поддерживающего заклинания (исключая героев)
                    valid_targets = [a for a in allies if not isinstance(a, Hero)]
                    if valid_targets:
                        best_target = max(valid_targets, key=lambda e: self.evaluate_spell_target(spell, unit, e))
                        if best_target.health < best_target.max_health * 0.7:
                            target_pos = (best_target.x * CELL_SIZE + CELL_SIZE // 2,
                                        best_target.y * CELL_SIZE + CELL_SIZE // 2)
                            self.game.handle_click(target_pos)
                            return True
            
            # Если заклинание не выбрано, выбираем лучшее
            spell_idx, spell_target, spell_pos = self.find_best_spell_action(unit)
            
            if spell_idx is not None and spell_target is not None and spell_pos:
                # Устанавливаем заклинание напрямую без открытия книги
                unit.selected_spell = spell_idx
                # Закрываем книгу если она была открыта (не должно быть видно игроку)
                if self.game.spellbook_open:
                    self.game.spellbook_open = False
                
                return True
        
        # Проверяем защиту
        if not isinstance(unit, Hero) and not unit.has_attacked and self.should_defend(unit):
            # Используем защиту
            defend_pos = (self.game.defend_button_rect.x + self.game.defend_button_rect.width // 2,
                         self.game.defend_button_rect.y + self.game.defend_button_rect.height // 2)
            self.game.handle_click(defend_pos)
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
            
            # Для дальнобойных ищем цели в пределах досягаемости (предпочитаем дальние, но можем и в ближний бой)
            else:
                for enemy in enemies:
                    if unit.can_attack(enemy.x, enemy.y, self.game.units):
                        distance = self.get_distance(unit, enemy)
                        # Предпочитаем цели вне ближнего боя, но если только такая - берем ее
                        score = self.evaluate_target(unit, enemy)
                        # Даем небольшой штраф за ближний бой для дальнобойных
                        if distance == 1:
                            score -= 10
                        reachable_targets.append((enemy, score))
            
            # Если есть цели в пределах досягаемости - атакуем лучшую
            if reachable_targets:
                best_reachable = max(reachable_targets, key=lambda x: x[1])[0]
                attack_pos = (best_reachable.x * CELL_SIZE + CELL_SIZE // 2,
                            best_reachable.y * CELL_SIZE + CELL_SIZE // 2)
                self.game.handle_click(attack_pos)
                return True
            
            # Если нет целей в пределах досягаемости, ищем лучшую цель для приближения
            target, estimated_damage = self.find_best_attack_target(unit)
            
            if target:
                # Проверяем, нужен ли шаг для атаки
                can_attack_now = unit.can_attack(target.x, target.y, self.game.units)
                
                if not can_attack_now:
                    # Нужно подойти ближе
                    best_move = self.find_best_move_position(unit, target)
                    
                    if best_move:
                        # Перемещаемся
                        move_pos = (best_move[0] * CELL_SIZE + CELL_SIZE // 2,
                                  best_move[1] * CELL_SIZE + CELL_SIZE // 2)
                        self.game.handle_click(move_pos)
                        
                        # После перемещения атакуем (через следующий вызов)
                        return True
                    else:
                        # Не можем достичь цели, ищем другую
                        pass
                else:
                    # Можем атаковать сейчас
                    attack_pos = (target.x * CELL_SIZE + CELL_SIZE // 2,
                                target.y * CELL_SIZE + CELL_SIZE // 2)
                    self.game.handle_click(attack_pos)
                    return True
        
        # Если не атаковали, перемещаемся к ближайшей цели
        if not unit.has_attacked and hasattr(unit, 'move_points_left') and unit.move_points_left > 0:
            enemies = self.get_enemies()
            if enemies:
                nearest_enemy = min(enemies, key=lambda e: self.get_distance(unit, e))
                best_move = self.find_best_move_position(unit, nearest_enemy)
                
                if best_move:
                    move_pos = (best_move[0] * CELL_SIZE + CELL_SIZE // 2,
                              best_move[1] * CELL_SIZE + CELL_SIZE // 2)
                    self.game.handle_click(move_pos)
                    return True
        
        # Пропускаем ход
        skip_pos = (self.game.skip_button_rect.x + self.game.skip_button_rect.width // 2,
                   self.game.skip_button_rect.y + self.game.skip_button_rect.height // 2)
        self.game.handle_click(skip_pos)
        return True

