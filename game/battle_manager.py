"""
Менеджер боевой логики
Управляет инициативой, очередью ходов, атаками и проверкой победы
"""
import pygame
from .config import CELL_SIZE, GRID_WIDTH, GRID_HEIGHT
from .units import Hero


class BattleManager:
    """Управляет боевой системой"""
    
    def __init__(self, game):
        """
        game: ссылка на главный объект Game
        """
        self.game = game
    
    def prepare_initiative_queue(self):
        """Формирует очередь ходов на основе инициативы юнитов"""
        init_list = []
        for u in self.game.units:
            if not isinstance(u, Hero):
                init_list.append((u.initiative, u))
        init_list.sort(reverse=True, key=lambda x: x[0])
        self.game.turn_queue = [u for (_, u) in init_list]
        # Добавляем разделитель раунда в конец
        self.game.turn_queue.append(self.game._round_delimiter)
        # Сбрасываем флаги всех юнитов
        for u in self.game.turn_queue:
            if u is not self.game._round_delimiter:
                u.has_moved = False
                u.has_attacked = False
                u.has_counterattacked = False
                u.move_points_left = u.speed
                if hasattr(u, '_defend_this_round'):
                    u._defend_this_round = False
    
    def next_turn(self):
        """Переход к следующему юниту в очереди"""
        if not self.game.turn_queue:
            return
        # Убираем текущего юнита
        if self.game.turn_queue:
            self.game.turn_queue.pop(0)
        # Если дошли до разделителя — новый раунд
        while self.game.turn_queue and self.game.turn_queue[0] is self.game._round_delimiter:
            self.game.turn_queue.pop(0)
            self.game.round_number += 1
            self.game.add_event(f"--- Раунд {self.game.round_number} ---")
            # Логируем начало раунда
            if hasattr(self.game, 'anim_logger'):
                self.game.anim_logger.log_round_start(self.game.round_number)
            # Сброс эффектов на всех юнитах
            for unit in self.game.units:
                if isinstance(unit, Hero):
                    unit.used_spell_this_round = False
                    unit.mana = min(unit.max_mana, unit.mana + max(1, int(unit.knowledge * 0.5)))
                else:
                    unit.has_moved = False
                    unit.has_attacked = False
                    unit.has_counterattacked = False
                    unit.move_points_left = unit.speed
                    # Сброс флага защиты (бонус действует только 1 раунд)
                    if getattr(unit, '_defend_this_round', False):
                        # Логируем сброс защиты ДО изменений
                        if hasattr(self.game, 'anim_logger'):
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
                        if hasattr(self.game, 'anim_logger'):
                            details = f"{unit.unit_type}: Физ.защ {old_phys}->{getattr(unit, 'phys_defense', 0)}, Маг.защ {old_mag}->{getattr(unit, 'magic_defense', 0)}, Сопр.маг {old_res}->{getattr(unit, 'magic_resist', 0)}"
                            self.game.anim_logger.log("DEFENSE_RESET", details)
                    # Уменьшаем счётчики эффектов
                    if hasattr(unit, 'curse_turns') and unit.curse_turns > 0:
                        unit.curse_turns -= 1
                    if hasattr(unit, 'attack_buff_turns') and unit.attack_buff_turns > 0:
                        unit.attack_buff_turns -= 1
                    if hasattr(unit, 'attack_debuff_turns') and unit.attack_debuff_turns > 0:
                        unit.attack_debuff_turns -= 1
                    if hasattr(unit, 'stone_skin_turns') and unit.stone_skin_turns > 0:
                        unit.stone_skin_turns -= 1
                    if hasattr(unit, 'slow_turns') and unit.slow_turns > 0:
                        unit.slow_turns -= 1
                    if hasattr(unit, 'haste_turns') and unit.haste_turns > 0:
                        unit.haste_turns -= 1
                    if hasattr(unit, 'fire_shield_turns') and unit.fire_shield_turns > 0:
                        unit.fire_shield_turns -= 1
                    if hasattr(unit, 'forget_turns') and unit.forget_turns > 0:
                        unit.forget_turns -= 1
                        if unit.forget_turns == 0:
                            unit.skip_next_turn = False
                    if hasattr(unit, 'has_waited'):
                        unit.has_waited = False
            # Пересоздаём очередь для нового раунда
            self.prepare_initiative_queue()
            return
        if self.game.turn_queue:
            self.game.selected_unit = self.game.turn_queue[0]
    
    def can_attack_any(self, unit):
        """Проверяет, может ли юнит атаковать хотя бы одного врага"""
        for enemy in self.game.units:
            if enemy.team != unit.team:
                if unit.can_attack(enemy.x, enemy.y, self.game.units):
                    return True
        return False
    
    def get_reachable_cells(self, x, y, move_points):
        """Возвращает клетки, достижимые с данной позиции за move_points ходов"""
        reachable = set()
        for dx in range(-move_points, move_points + 1):
            remaining = move_points - abs(dx)
            for dy in range(-remaining, remaining + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    distance = abs(dx) + abs(dy)
                    if distance <= move_points:
                        # Не занимать клетки с юнитами другой команды
                        occupied = any(u.x == nx and u.y == ny for u in self.game.units)
                        if not occupied:
                            reachable.add((nx, ny))
        return reachable
    
    def get_path_length(self, x1, y1, x2, y2):
        """Возвращает манхэттенское расстояние между двумя точками"""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def perform_counterattack(self, attacker, defender, is_melee, target_is_melee_unit, skip_initial_redraw=False, hide_unit_at=None):
        """Обрабатывает контратаку и реактивные эффекты (огненный щит)"""
        # 1) Реактивный урон огненного щита (не считается контратакой) - ТОЛЬКО для ближних атак
        if is_melee and defender and attacker and getattr(defender, 'fire_shield_turns', 0) > 0 and defender.health > 0:
            try:
                self.game.animation_manager.animate_fire_shield_burst(defender, attacker, hide_unit_at=hide_unit_at)
            except Exception:
                pass
            # Новая формула: 15% от макс HP + сила магии кастера
            max_hp = getattr(defender, 'max_health', 100)
            spell_power = getattr(defender, 'fire_shield_spell_power', 0)
            shield_damage = max(1, int(max_hp * 0.15) + spell_power)
            if shield_damage > 0:
                if attacker.take_damage(shield_damage, attack_type='magical'):
                    self.game.kill_unit(attacker)
                    self.game.animation_manager.animate_queue_fade(attacker)
                    self.game.add_event(f"{defender.unit_type.capitalize()} обжёг {attacker.unit_type} огненным щитом")
                    self.check_game_over()
                    # Если атакующий погиб — контратаки не будет
                    return True
                else:
                    self.game.add_event(f"{defender.unit_type.capitalize()} обжёг {attacker.unit_type} огненным щитом")

        # 2) Стандартная логика контратаки - только для ближнего боя
        # Герои не получают и не наносят контратаки
        if isinstance(attacker, Hero) or isinstance(defender, Hero):
            return False
        
        # Проверка контратаки:
        # - Если у защитника есть контрудар (counterstrike_turns > 0), он всегда контратакует
        # - Иначе контратакует только если еще не контратаковал в этом раунде
        has_counterstrike = hasattr(defender, 'counterstrike_turns') and getattr(defender, 'counterstrike_turns', 0) > 0
        can_counter = has_counterstrike or not (hasattr(defender, 'has_counterattacked') and defender.has_counterattacked)
        
        if not (is_melee and defender.health > 0 and can_counter):
            return False
        
        # Ждем завершения первой атаки (урон и звук)
        # Обновляем экран, чтобы показать урон (пропускаем, если идет анимация воина)
        if not skip_initial_redraw:
            self.game.draw()
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
        attacker_died = attacker.take_damage(counter_damage, attack_type=defender_attack_type)
        actual_damage = health_before - attacker.health
        
        if attacker_died:
            self.game.kill_unit(attacker)
            self.game.animation_manager.animate_queue_fade(attacker)
            self.game.add_event(f"{defender.unit_type.capitalize()} контратаковал и убил {attacker.unit_type.capitalize()} (урон: {actual_damage})")
            self.check_game_over()
        else:
            self.game.add_event(f"{defender.unit_type.capitalize()} контратаковал {attacker.unit_type.capitalize()} (урон: {actual_damage}, осталось: {attacker.health}/{attacker.max_health})")
            
            # 3) Проверяем огненный щит АТАКУЮЩЕГО после получения урона от контратаки
            # Это ближний бой (контратака), поэтому щит срабатывает
            if attacker and attacker.health > 0 and getattr(attacker, 'fire_shield_turns', 0) > 0 and defender.health > 0:
                try:
                    self.game.animation_manager.animate_fire_shield_burst(attacker, defender)
                except Exception:
                    pass
                max_hp_att = getattr(attacker, 'max_health', 100)
                spell_power_att = getattr(attacker, 'fire_shield_spell_power', 0)
                shield_damage_att = max(1, int(max_hp_att * 0.15) + spell_power_att)
                if shield_damage_att > 0:
                    if defender.take_damage(shield_damage_att, attack_type='magical'):
                        self.game.kill_unit(defender)
                        self.game.animation_manager.animate_queue_fade(defender)
                        self.game.add_event(f"{attacker.unit_type.capitalize()} обжёг {defender.unit_type} огненным щитом")
                        self.check_game_over()
                    else:
                        self.game.add_event(f"{attacker.unit_type.capitalize()} обжёг {defender.unit_type} огненным щитом")
        
        # Отмечаем, что защитник контратаковал (только если нет контрудара)
        if not has_counterstrike:
            defender.has_counterattacked = True
        return False
    
    def check_game_over(self):
        """Проверяет условия победы/поражения"""
        # Находим команды с живыми юнитами (исключая героев)
        teams_alive = set()
        for unit in self.game.units:
            if not isinstance(unit, Hero) and unit.health > 0:
                teams_alive.add(unit.team)
        
        # Если осталась только одна команда
        if len(teams_alive) <= 1:
            self.game.game_over = True
            if len(teams_alive) == 1:
                winner_team = list(teams_alive)[0]
                self.game.winner_team = winner_team
                # Определяем победителя по расе
                if self.game.player1_race and winner_team == self.game.player1_race:
                    self.game.victory_state = 'victory' if self.game.player1_type == 'human' else 'defeat'
                elif self.game.player2_race and winner_team == self.game.player2_race:
                    self.game.victory_state = 'defeat' if self.game.player1_type == 'human' else 'victory'
            else:
                # Ничья (все погибли)
                self.game.victory_state = 'defeat'

