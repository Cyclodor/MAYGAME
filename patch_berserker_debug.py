"""
Автоматически добавляет логирование берсерка в код игры.
Запустите эту программу перед запуском игры для включения отладки.
"""

import os
import re

def patch_file(file_path, patches):
    """Применяет патчи к файлу"""
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for patch_name, (old_pattern, new_code) in patches.items():
        if old_pattern in content:
            content = content.replace(old_pattern, new_code)
            print(f"✓ Применен патч '{patch_name}' в {file_path}")
        else:
            print(f"✗ Не найден паттерн для '{patch_name}' в {file_path}")
    
    if content != original_content:
        # Создаем резервную копию
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"  Создана резервная копия: {backup_path}")
        
        # Сохраняем измененный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Файл обновлен: {file_path}")
        return True
    else:
        print(f"  Изменений не требуется в {file_path}")
        return False


def patch_spells_py():
    """Патчит game/spells.py"""
    file_path = 'game/spells.py'
    
    # Патч 1: Импорт отладчика в начале файла
    import_patch = (
        "from .config import GRID_WIDTH, GRID_HEIGHT",
        """from .config import GRID_WIDTH, GRID_HEIGHT
# Импорт отладчика берсерка
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None"""
    )
    
    # Патч 2: Логирование в RuneBerserkerSpell.apply()
    apply_patch_old = """        # Устанавливаем флаг враждебности и меняем команду на уникальную
        target.rune_berserker_active = True
        target.rune_berserker_turns = turns
        
        # КРИТИЧНО: Используем более надежный способ создания уникальной команды
        # Используем комбинацию id объекта и текущего времени для гарантии уникальности
        import time
        unique_id = f'berserker_{id(target)}_{int(time.time() * 1000000)}'
        target.team = unique_id
        
        # Анимация каста уже вызывается в core.py при применении заклинания"""
    
    apply_patch_new = """        # Устанавливаем флаг враждебности и меняем команду на уникальную
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
        
        # Анимация каста уже вызывается в core.py при применении заклинания"""
    
    patches = {
        'import_debugger': import_patch,
        'log_apply': (apply_patch_old, apply_patch_new)
    }
    
    return patch_file(file_path, patches)


def patch_units_py():
    """Патчит game/units.py"""
    file_path = 'game/units.py'
    
    # Патч: Логирование в end_turn_effects для берсерка
    end_turn_patch_old = """        # Руна берсерка: тикаем длительность
        if getattr(self, 'rune_berserker_turns', 0) > 0:
            self.rune_berserker_turns -= 1
            if self.rune_berserker_turns == 0:
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
                    self.team = self.rune_berserker_original_team
                self.rune_berserker_active = False
                print(f'Руна берсерка рассеялась у {self.unit_type} ({self.x},{self.y})')"""
    
    end_turn_patch_new = """        # Руна берсерка: тикаем длительность
        if getattr(self, 'rune_berserker_turns', 0) > 0:
            # ОТЛАДКА: Логируем окончание хода
            try:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
                print(f'Руна берсерка рассеялась у {self.unit_type} ({self.x},{self.y})')"""
    
    patches = {
        'log_end_turn': (end_turn_patch_old, end_turn_patch_new)
    }
    
    return patch_file(file_path, patches)


def patch_core_py():
    """Патчит game/core.py"""
    file_path = 'game/core.py'
    
    # Патч 1: Импорт отладчика после других импортов
    import_patch = (
        "from .debugger import GameDebugger",
        """from .debugger import GameDebugger
# Импорт отладчика берсерка
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from berserker_debug import get_debugger
    BERSERKER_DEBUG = True
except:
    BERSERKER_DEBUG = False
    def get_debugger():
        return None"""
    )
    
    # Патч 2: Логирование в prepare_initiative_queue
    queue_patch_old = """        # Сортируем по инициативе (выше — раньше). При равенстве — стабильно.
        self.turn_queue = sorted(all_units, key=lambda u: getattr(u, 'initiative', 0), reverse=True)"""
    
    queue_patch_new = """        # Сортируем по инициативе (выше — раньше). При равенстве — стабильно.
        self.turn_queue = sorted(all_units, key=lambda u: getattr(u, 'initiative', 0), reverse=True)
        
        # ОТЛАДКА: Логируем подготовку очереди
        if BERSERKER_DEBUG:
            try:
                debugger = get_debugger()
                if debugger:
                    debugger.log_queue_preparation(self.turn_queue)
            except:
                pass"""
    
    # Патч 3: Логирование проверки берсерка в next_turn
    check_patch_old = """            # КРИТИЧНО: Если следующий юнит получил ЛЮБЫЕ флаги связанные с берсерком - удаляем их нахуй
            if (self.selected_unit and 
                not isinstance(self.selected_unit, Hero)):
                # Проверяем все возможные флаги берсерка
                berserker_flags_found = False"""
    
    check_patch_new = """            # КРИТИЧНО: Если следующий юнит получил ЛЮБЫЕ флаги связанные с берсерком - удаляем их нахуй
            if (self.selected_unit and 
                not isinstance(self.selected_unit, Hero)):
                # ОТЛАДКА: Логируем проверку берсерка
                if BERSERKER_DEBUG:
                    try:
                        debugger = get_debugger()
                        if debugger:
                            is_berserker = (hasattr(self.selected_unit, 'rune_berserker_active') and
                                          getattr(self.selected_unit, 'rune_berserker_active', False) and
                                          getattr(self.selected_unit, 'rune_berserker_turns', 0) > 0 and
                                          isinstance(self.selected_unit.team, str) and
                                          self.selected_unit.team.startswith('berserker_'))
                            debugger.log_berserker_check(self.selected_unit, is_berserker, "next_turn: проверка флагов")
                    except:
                        pass
                
                # Проверяем все возможные флаги берсерка
                berserker_flags_found = False"""
    
    # Патч 4: Логирование изменения команды при исправлении
    fix_patch_old = """                    # Восстанавливаем оригинальную команду
                    if hasattr(self.selected_unit, 'rune_berserker_original_team'):
                        self.selected_unit.team = self.selected_unit.rune_berserker_original_team"""
    
    fix_patch_new = """                    # Восстанавливаем оригинальную команду
                    if hasattr(self.selected_unit, 'rune_berserker_original_team'):
                        old_team = getattr(self.selected_unit, 'team', None)
                        new_team = self.selected_unit.rune_berserker_original_team
                        self.selected_unit.team = new_team
                        
                        # ОТЛАДКА: Логируем исправление команды
                        if BERSERKER_DEBUG:
                            try:
                                debugger = get_debugger()
                                if debugger:
                                    debugger.log_team_change(self.selected_unit, old_team, new_team, "Исправление неправильной команды берсерка")
                            except:
                                pass"""
    
    # Патч 5: Логирование начала хода и определения контроллера
    turn_start_patch_old = """            if is_berserker:
                # Берсерк обрабатывается в next_turn, здесь просто пропускаем AI
                # ДОПОЛНИТЕЛЬНО: Сбрасываем таймер AI чтобы не было проблем
                self.ai_think_timer = 0"""
    
    turn_start_patch_new = """            if is_berserker:
                # Берсерк обрабатывается в next_turn, здесь просто пропускаем AI
                # ДОПОЛНИТЕЛЬНО: Сбрасываем таймер AI чтобы не было проблем
                self.ai_think_timer = 0
                
                # ОТЛАДКА: Логируем начало хода берсерка
                if BERSERKER_DEBUG:
                    try:
                        debugger = get_debugger()
                        if debugger:
                            debugger.log_turn_start(self.selected_unit, 'berserker', {'reason': 'auto_berserker_logic'})
                    except:
                        pass"""
    
    # Патч 6: Логирование проверки AI контроллера
    ai_check_patch_old = """                if active_ai_controller and active_ai_controller.is_ai_turn():
                    # Увеличиваем таймер"""
    
    ai_check_patch_new = """                if active_ai_controller and active_ai_controller.is_ai_turn():
                    # ОТЛАДКА: Логируем проверку AI контроллера
                    if BERSERKER_DEBUG:
                        try:
                            debugger = get_debugger()
                            if debugger:
                                controller_name = getattr(active_ai_controller, 'ai_team', 'unknown')
                                debugger.log_controller_check(self.selected_unit, 'ai', controller_name, "AI контроллер найден")
                                debugger.log_turn_start(self.selected_unit, 'ai', {'controller': controller_name})
                        except:
                            pass
                    
                    # Увеличиваем таймер"""
    
    # Патч 7: Логирование начала хода игрока
    player_turn_patch_old = """            self.selected_unit = self.turn_queue[0]
            # КРИТИЧНО: Если следующий юнит получил ЛЮБЫЕ флаги связанные с берсерком - удаляем их нахуй"""
    
    player_turn_patch_new = """            self.selected_unit = self.turn_queue[0]
            
            # ОТЛАДКА: Логируем начало хода (игрок или другой контроллер)
            if BERSERKER_DEBUG and self.selected_unit:
                try:
                    debugger = get_debugger()
                    if debugger and not isinstance(self.selected_unit, Hero):
                        # Определяем тип контроллера
                        is_berserker = (hasattr(self.selected_unit, 'rune_berserker_active') and
                                      getattr(self.selected_unit, 'rune_berserker_active', False) and
                                      getattr(self.selected_unit, 'rune_berserker_turns', 0) > 0 and
                                      isinstance(self.selected_unit.team, str) and
                                      self.selected_unit.team.startswith('berserker_'))
                        
                        if not is_berserker:
                            # Проверяем, есть ли AI контроллер для этой команды
                            has_ai = False
                            if (self.ai_controller_p1 and self.selected_unit.team == self.ai_controller_p1.ai_team):
                                has_ai = True
                            elif (self.ai_controller_p2 and self.selected_unit.team == self.ai_controller_p2.ai_team):
                                has_ai = True
                            
                            controller_type = 'ai' if has_ai else 'player'
                            debugger.log_turn_start(self.selected_unit, controller_type, {'has_ai_controller': has_ai})
                except:
                    pass
            
            # КРИТИЧНО: Если следующий юнит получил ЛЮБЫЕ флаги связанные с берсерком - удаляем их нахуй"""
    
    # Патч 8: Логирование начала обработки берсерка в update()
    berserker_logic_start_old = """            if is_berserker:
                # Берсерк работает независимо - продолжаем атаковать/двигаться пока есть возможности
                max_actions = 50  # Защита от бесконечного цикла
                action_count = 0"""
    
    # Патч 8b: Проверка юнита, который обрабатывается как берсерк, но не имеет флага
    berserker_check_before_logic_old = """            # Автономный бот для берсерка - атакует ближайшего любого юнита (РАБОТАЕТ ДО AI)
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
                    is_berserker = True"""
    
    berserker_check_before_logic_new = """            # Автономный бот для берсерка - атакует ближайшего любого юнита (РАБОТАЕТ ДО AI)
            # ВАЖНО: Проверяем, что это действительно берсерк, а не просто следующий юнит в очереди
            # Также проверяем, что команда юнита соответствует берсерку (уникальная команда)
            # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: убеждаемся что это не герой и что юнит действительно под эффектом
            # КРИТИЧНО: Проверяем ВСЕ условия вместе, чтобы исключить ложные срабатывания
            
            # ОТЛАДКА: Проверяем состояние юнита перед проверкой берсерка
            if BERSERKER_DEBUG and self.selected_unit and not isinstance(self.selected_unit, Hero):
                try:
                    debugger = get_debugger()
                    if debugger:
                        unit_team = getattr(self.selected_unit, 'team', None)
                        has_berserker_team = isinstance(unit_team, str) and unit_team.startswith('berserker_')
                        has_berserker_flag = getattr(self.selected_unit, 'rune_berserker_active', False)
                        has_berserker_turns = getattr(self.selected_unit, 'rune_berserker_turns', 0) > 0
                        
                        # КРИТИЧНО: Если команда берсерка, но нет флага - это ошибка!
                        if has_berserker_team and not has_berserker_flag:
                            debugger.log_auto_action_without_berserker_flag(
                                self.selected_unit, 
                                'check_before_berserker_logic',
                                "Юнит имеет команду берсерка, но не имеет флага берсерка перед проверкой логики"
                            )
                except:
                    pass
            
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
                    is_berserker = True"""
    
    berserker_logic_start_new = """            if is_berserker:
                # ОТЛАДКА: Логируем начало обработки берсерка
                if BERSERKER_DEBUG:
                    try:
                        debugger = get_debugger()
                        if debugger:
                            debugger.log('BERSERKER_LOGIC_START',
                                        f"Начало обработки берсерка | Команда: {getattr(self.selected_unit, 'team', None)}",
                                        self.selected_unit,
                                        {
                                            'rune_berserker_active': getattr(self.selected_unit, 'rune_berserker_active', False),
                                            'rune_berserker_turns': getattr(self.selected_unit, 'rune_berserker_turns', 0),
                                            'team': getattr(self.selected_unit, 'team', None),
                                        })
                    except:
                        pass
                
                # Берсерк работает независимо - продолжаем атаковать/двигаться пока есть возможности
                max_actions = 50  # Защита от бесконечного цикла
                action_count = 0"""
    
    # Патч 9: Логирование действий берсерка (атака)
    berserker_attack_old = """                    # Проверяем, можем ли атаковать
                    if not self.selected_unit.has_attacked and self.selected_unit.can_attack(nearest_unit.x, nearest_unit.y, self.units):
                        # Атакуем ближайшего юнита
                        self.handle_click((nearest_unit.x * CELL_SIZE + CELL_SIZE//2, nearest_unit.y * CELL_SIZE + CELL_SIZE//2), is_ai_action=True)"""
    
    berserker_attack_new = """                    # Проверяем, можем ли атаковать
                    if not self.selected_unit.has_attacked and self.selected_unit.can_attack(nearest_unit.x, nearest_unit.y, self.units):
                        # ОТЛАДКА: Логируем атаку берсерка
                        if BERSERKER_DEBUG:
                            try:
                                debugger = get_debugger()
                                if debugger:
                                    debugger.log_unit_action(self.selected_unit, 'attack', {
                                        'target': getattr(nearest_unit, 'unit_type', None),
                                        'target_pos': (nearest_unit.x, nearest_unit.y),
                                        'target_id': id(nearest_unit),
                                        'target_team': getattr(nearest_unit, 'team', None)
                                    })
                            except:
                                pass
                        
                        # Атакуем ближайшего юнита
                        self.handle_click((nearest_unit.x * CELL_SIZE + CELL_SIZE//2, nearest_unit.y * CELL_SIZE + CELL_SIZE//2), is_ai_action=True)"""
    
    # Патч 10: Логирование действий берсерка (движение)
    berserker_move_old = """                        if moved:
                            path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, new_x, new_y)
                            if path_len <= self.selected_unit.move_points_left:
                                self.animate_unit_move(self.selected_unit, new_x, new_y)
                                self.selected_unit.move_points_left -= path_len
                                self.add_event(f"{self.selected_unit.unit_type.capitalize()} (берсерк) движется к цели")"""
    
    berserker_move_new = """                        if moved:
                            path_len = self.get_path_length(self.selected_unit.x, self.selected_unit.y, new_x, new_y)
                            if path_len <= self.selected_unit.move_points_left:
                                # ОТЛАДКА: Логируем движение берсерка
                                if BERSERKER_DEBUG:
                                    try:
                                        debugger = get_debugger()
                                        if debugger:
                                            debugger.log_unit_action(self.selected_unit, 'move', {
                                                'from': (self.selected_unit.x, self.selected_unit.y),
                                                'to': (new_x, new_y),
                                                'target': getattr(nearest_unit, 'unit_type', None),
                                                'target_pos': (nearest_unit.x, nearest_unit.y)
                                            })
                                    except:
                                        pass
                                
                                self.animate_unit_move(self.selected_unit, new_x, new_y)
                                self.selected_unit.move_points_left -= path_len
                                self.add_event(f"{self.selected_unit.unit_type.capitalize()} (берсерк) движется к цели")"""
    
    # Патч 11: Логирование проверки команды следующего юнита после берсерка
    berserker_next_check_old = """                # КРИТИЧНО: Сохраняем ссылку на следующий юнит ДО next_turn(), чтобы проверить что его команда не изменилась
                next_unit_index = 0
                if self.turn_queue and len(self.turn_queue) > 1:"""
    
    berserker_next_check_new = """                # КРИТИЧНО: Сохраняем ссылку на следующий юнит ДО next_turn(), чтобы проверить что его команда не изменилась
                # ОТЛАДКА: Логируем проверку следующего юнита
                if BERSERKER_DEBUG:
                    try:
                        debugger = get_debugger()
                        if debugger and self.turn_queue and len(self.turn_queue) > 1:
                            berserker_index = self.turn_queue.index(berserker_unit) if berserker_unit in self.turn_queue else -1
                            if berserker_index >= 0 and berserker_index < len(self.turn_queue) - 1:
                                next_unit = self.turn_queue[berserker_index + 1]
                                if next_unit != self._round_delimiter:
                                    debugger.log('BERSERKER_NEXT_UNIT_CHECK',
                                                f"Проверка следующего юнита после берсерка",
                                                next_unit,
                                                {
                                                    'next_unit_type': getattr(next_unit, 'unit_type', None),
                                                    'next_unit_team': getattr(next_unit, 'team', None),
                                                    'next_unit_has_berserker': getattr(next_unit, 'rune_berserker_active', False),
                                                    'berserker_unit_type': getattr(berserker_unit, 'unit_type', None),
                                                    'berserker_unit_team': getattr(berserker_unit, 'team', None),
                                                })
                    except:
                        pass
                
                next_unit_index = 0
                if self.turn_queue and len(self.turn_queue) > 1:"""
    
    patches = {
        'import_debugger': import_patch,
        'log_queue': (queue_patch_old, queue_patch_new),
        'log_check': (check_patch_old, check_patch_new),
        'log_fix': (fix_patch_old, fix_patch_new),
        'log_turn_start_berserker': (turn_start_patch_old, turn_start_patch_new),
        'log_ai_check': (ai_check_patch_old, ai_check_patch_new),
        'log_player_turn': (player_turn_patch_old, player_turn_patch_new),
        'log_berserker_check_before': (berserker_check_before_logic_old, berserker_check_before_logic_new),
        'log_berserker_logic_start': (berserker_logic_start_old, berserker_logic_start_new),
        'log_berserker_attack': (berserker_attack_old, berserker_attack_new),
        'log_berserker_move': (berserker_move_old, berserker_move_new),
        'log_berserker_next_check': (berserker_next_check_old, berserker_next_check_new)
    }
    
    return patch_file(file_path, patches)


def main():
    """Главная функция"""
    print("=" * 80)
    print("ПАТЧИРОВАНИЕ КОДА ДЛЯ ОТЛАДКИ РУНЫ БЕРСЕРКА")
    print("=" * 80)
    print()
    
    results = []
    results.append(("game/spells.py", patch_spells_py()))
    results.append(("game/units.py", patch_units_py()))
    results.append(("game/core.py", patch_core_py()))
    
    print()
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ:")
    print("=" * 80)
    for file_path, success in results:
        status = "✓ УСПЕШНО" if success else "✗ ОШИБКА"
        print(f"{status}: {file_path}")
    
    print()
    print("=" * 80)
    print("ИНСТРУКЦИИ:")
    print("=" * 80)
    print("1. Запустите игру: python main.py")
    print("2. Примените руну берсерка на юните")
    print("3. Проверьте файл berserker_debug.log для детального лога")
    print("4. После игры запустите: python -c 'from berserker_debug import generate_report; generate_report()'")
    print("   для генерации отчета")
    print()
    print("Для отката изменений используйте файлы .backup")
    print("=" * 80)


if __name__ == '__main__':
    main()

