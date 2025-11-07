"""
Прямые методы для выполнения действий AI без использования handle_click
Это предотвращает открытие окон и блокировку интерфейса
"""

import pygame
from .config import CELL_SIZE
from .units import Hero


class AIActions:
    """Методы для прямого выполнения действий AI без кликов"""
    
    def __init__(self, game):
        self.game = game
    
    def close_all_windows(self):
        """Закрывает все открытые окна перед действием AI"""
        self.game.unit_info_window_open = False
        self.game.unit_info_window_unit = None
        self.game.spellbook_open = False
        self.game.history_panel_open = False
        self.game.menu_open = False
    
    def move_unit_direct(self, unit, target_x, target_y):
        """
        Прямое перемещение юнита без использования handle_click
        
        Args:
            unit: Юнит для перемещения
            target_x, target_y: Целевые координаты
            
        Returns:
            True если перемещение успешно, False иначе
        """
        if not unit or unit.has_moved:
            return False
        
        # Проверяем достижимость
        if not hasattr(unit, 'move_points_left') or unit.move_points_left <= 0:
            return False
        
        # Проверяем, что клетка свободна
        for u in self.game.units:
            if u != unit and u.x == target_x and u.y == target_y:
                return False
        
        # Вычисляем длину пути (используем метод из Game или BattleManager)
        if hasattr(self.game, 'battle_manager') and hasattr(self.game.battle_manager, 'get_path_length'):
            path_len = self.game.battle_manager.get_path_length(unit.x, unit.y, target_x, target_y)
        elif hasattr(self.game, 'get_path_length'):
            path_len = self.game.get_path_length(unit.x, unit.y, target_x, target_y)
        else:
            # Fallback: манхэттенское расстояние
            path_len = abs(unit.x - target_x) + abs(unit.y - target_y)
        
        if path_len > unit.move_points_left:
            return False
        
        # Закрываем все окна
        self.close_all_windows()
        
        # Выполняем перемещение
        self.game.animate_unit_move(unit, target_x, target_y)
        unit.x = target_x
        unit.y = target_y
        unit.move_points_left -= path_len
        unit.has_moved = True
        
        self.game.add_event(f"{unit.unit_type.capitalize()} переместился на ({target_x},{target_y})")
        
        # Проверяем, нужно ли перейти к следующему ходу
        if unit.move_points_left <= 0:
            if hasattr(self.game, 'battle_manager') and hasattr(self.game.battle_manager, 'can_attack_any'):
                if not self.game.battle_manager.can_attack_any(unit):
                    self.game.battle_manager.next_turn()
            elif hasattr(self.game, 'can_attack_any'):
                if not self.game.can_attack_any(unit):
                    if hasattr(self.game, 'battle_manager'):
                        self.game.battle_manager.next_turn()
                    elif hasattr(self.game, 'next_turn'):
                        self.game.next_turn()
        
        return True
    
    def attack_unit_direct(self, attacker, target):
        """
        Прямая атака юнита без использования handle_click
        
        Args:
            attacker: Атакующий юнит
            target: Целевой юнит
            
        Returns:
            True если атака успешна, False иначе
        """
        if not attacker or not target:
            return False
        
        if attacker.has_attacked:
            return False
        
        if isinstance(target, Hero):
            return False  # Нельзя атаковать героев
        
        # Проверяем возможность атаки
        if not attacker.can_attack(target.x, target.y, self.game.units):
            return False
        
        # Закрываем все окна
        self.close_all_windows()
        
        # Вычисляем расстояние
        distance = abs(attacker.x - target.x) + abs(attacker.y - target.y)
        is_melee = (distance == 1)
        
        # Выполняем атаку
        attacker.has_attacked = True
        
        # Определяем тип атаки
        if hasattr(attacker, 'is_ranged') and attacker.is_ranged:
            if is_melee:
                # Ближний бой для лучников
                damage = max(1, attacker.get_current_attack() // 2)
                attack_type = getattr(attacker, 'attack_type', 'physical')
                if target.take_damage(damage, attack_type=attack_type):
                    self.game.kill_unit(target)
                    self.game.animation_manager.animate_queue_fade(target)
                    self.game.add_event(f"{attacker.unit_type.capitalize()} убил {target.unit_type.capitalize()} в ближнем бою")
                    self.game.battle_manager.check_game_over()
                else:
                    self.game.add_event(f"{attacker.unit_type.capitalize()} атаковал {target.unit_type.capitalize()} в ближнем бою (урон: {damage})")
                
                # Контратака
                self.game.battle_manager.perform_counterattack(attacker, target, True, True)
            else:
                # Дальнобойная атака
                damage = attacker.ranged_damage(target.x, target.y)
                attack_type = getattr(attacker, 'attack_type', 'physical')
                if target.take_damage(damage, attack_type=attack_type):
                    self.game.kill_unit(target)
                    self.game.animation_manager.animate_queue_fade(target)
                    self.game.add_event(f"{attacker.unit_type.capitalize()} убил {target.unit_type.capitalize()} (дальнобойная атака)")
                    self.game.battle_manager.check_game_over()
                else:
                    self.game.add_event(f"{attacker.unit_type.capitalize()} атаковал {target.unit_type.capitalize()} (дальнобойная атака, урон: {damage})")
                
                # Анимация стрелы - используем правильную функцию из graphics
                try:
                    from .graphics import animate_arrow_fly
                    start = (attacker.x * CELL_SIZE + CELL_SIZE // 2, attacker.y * CELL_SIZE + CELL_SIZE // 2)
                    end = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
                    # Определяем тип снаряда в зависимости от юнита
                    if attacker.unit_type in ['crossbowman', 'elf_archer']:
                        # Лучники стреляют стрелами
                        animate_arrow_fly(self.game.screen, start, end, redraw_callback=self.game.draw)
                        # Звук попадания
                        if hasattr(attacker, 'arrow_hit_sound') and attacker.arrow_hit_sound:
                            attacker.arrow_hit_sound.play()
                    elif isinstance(attacker, Hero) and hasattr(attacker, 'hero_class') and attacker.hero_class == 'archer':
                        # Герой-лучник стреляет стрелами
                        animate_arrow_fly(self.game.screen, start, end, redraw_callback=self.game.draw)
                        # Звук попадания
                        if hasattr(attacker, 'arrow_hit_sound') and attacker.arrow_hit_sound:
                            attacker.arrow_hit_sound.play()
                    else:
                        # Маги и герои-маги стреляют магическими снарядами
                        from .graphics import animate_magic_fly
                        if attacker.unit_type == 'succubus':
                            color = (255, 80, 120)  # красный
                        elif attacker.unit_type == 'gog':
                            color = (255, 120, 40)  # оранжевый
                        elif attacker.unit_type == 'lich':
                            color = (80, 255, 80)   # зеленый
                        elif isinstance(attacker, Hero):
                            # Герои-маги стреляют синими магическими снарядами
                            color = (120, 180, 255)  # синий
                        else:
                            color = (120, 180, 255)  # синий для остальных
                        animate_magic_fly(self.game.screen, start, end, color=color, redraw_callback=self.game.draw)
                    # Перерисовываем экран, чтобы убрать снаряд
                    self.game.draw()
                    pygame.display.flip()
                except Exception as e:
                    # Если анимация не работает, просто перерисовываем
                    self.game.draw()
                    pygame.display.flip()
        else:
            # Ближний бой
            damage = attacker.get_current_attack()
            attack_type = getattr(attacker, 'attack_type', 'physical')
            if target.take_damage(damage, attack_type=attack_type):
                self.game.kill_unit(target)
                self.game.animation_manager.animate_queue_fade(target)
                self.game.add_event(f"{attacker.unit_type.capitalize()} убил {target.unit_type.capitalize()}")
                self.game.battle_manager.check_game_over()
            else:
                self.game.add_event(f"{attacker.unit_type.capitalize()} атаковал {target.unit_type.capitalize()} (урон: {damage})")
            
            # Контратака
            target_is_melee = not (hasattr(target, 'is_ranged') and target.is_ranged)
            if hasattr(self.game, 'battle_manager') and hasattr(self.game.battle_manager, 'perform_counterattack'):
                self.game.battle_manager.perform_counterattack(attacker, target, True, target_is_melee)
        
        # Проверяем, нужно ли перейти к следующему ходу
        can_attack = False
        if hasattr(self.game, 'battle_manager') and hasattr(self.game.battle_manager, 'can_attack_any'):
            can_attack = self.game.battle_manager.can_attack_any(attacker)
        elif hasattr(self.game, 'can_attack_any'):
            can_attack = self.game.can_attack_any(attacker)
        
        if not can_attack and (not hasattr(attacker, 'move_points_left') or attacker.move_points_left <= 0):
            if hasattr(self.game, 'battle_manager'):
                self.game.battle_manager.next_turn()
            elif hasattr(self.game, 'next_turn'):
                self.game.next_turn()
        
        return True
    
    def use_spell_direct(self, caster, spell, target=None, target_pos=None):
        """
        Прямое применение заклинания без использования handle_click
        
        Args:
            caster: Кастер заклинания (герой)
            spell: Объект заклинания или индекс
            target: Целевой юнит (опционально)
            target_pos: Целевая позиция (x, y) для area заклинаний (опционально)
            
        Returns:
            True если заклинание применено, False иначе
        """
        if not isinstance(caster, Hero):
            return False
        
        if caster.used_spell_this_round:
            return False
        
        # Получаем объект заклинания
        if isinstance(spell, int):
            if spell >= len(caster.spells):
                return False
            spell = caster.spells[spell]
        
        if not spell:
            return False
        
        # Проверяем ману
        if caster.mana < spell.mana_cost:
            return False
        
        # Закрываем все окна
        self.close_all_windows()
        
        # Применяем заклинание
        if target_pos:
            # Area заклинание
            x, y = target_pos
            spell_success = spell.apply((x, y), caster=caster)
        elif target:
            # Заклинание на цель
            spell_success = spell.apply(target, caster=caster)
        else:
            return False
        
        if spell_success:
            caster.mana = max(0, caster.mana - spell.mana_cost)
            caster.used_spell_this_round = True
            caster.selected_spell = None
            # Перерисовываем экран для отображения анимации заклинания
            self.game.draw()
            pygame.display.flip()
        
        return spell_success
    
    def defend_direct(self, unit):
        """
        Прямая активация защиты без использования handle_click
        
        Args:
            unit: Юнит для защиты
            
        Returns:
            True если защита активирована, False иначе
        """
        if not unit or isinstance(unit, Hero):
            return False
        
        if unit.has_attacked:
            return False
        
        # Закрываем все окна
        self.close_all_windows()
        
        # Активируем защиту
        if not hasattr(unit, '_defend_this_round'):
            unit._defend_this_round = False
        
        unit._defend_this_round = True
        
        # Увеличиваем защиту на 20%
        if not hasattr(unit, '_original_phys_defense'):
            unit._original_phys_defense = getattr(unit, 'phys_defense', 0)
        if not hasattr(unit, '_original_magic_defense'):
            unit._original_magic_defense = getattr(unit, 'magic_defense', 0)
        if not hasattr(unit, '_original_magic_resist'):
            unit._original_magic_resist = getattr(unit, 'magic_resist', 0)
        
        unit.phys_defense = int(getattr(unit, 'phys_defense', 0) * 1.2)
        unit.magic_defense = int(getattr(unit, 'magic_defense', 0) * 1.2)
        unit.magic_resist = int(getattr(unit, 'magic_resist', 0) * 1.2)
        
        self.game.add_event(f"{unit.unit_type.capitalize()} активировал защиту")
        
        # Переходим к следующему ходу
        if hasattr(self.game, 'battle_manager'):
            self.game.battle_manager.next_turn()
        elif hasattr(self.game, 'next_turn'):
            self.game.next_turn()
        
        return True
    
    def skip_turn_direct(self, unit):
        """
        Прямой пропуск хода без использования handle_click
        
        Args:
            unit: Юнит для пропуска хода
            
        Returns:
            True если ход пропущен, False иначе
        """
        if not unit:
            return False
        
        # Закрываем все окна
        self.close_all_windows()
        
        # Пропускаем ход
        if hasattr(self.game, 'battle_manager'):
            self.game.battle_manager.next_turn()
        elif hasattr(self.game, 'next_turn'):
            self.game.next_turn()
        
        return True

