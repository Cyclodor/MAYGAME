import pygame
from .config import *
from .units import Hero

class GameDebugger:
    def __init__(self, game):
        self.game = game
        self.debug_mode = False
        self.show_move_range = False
        self.show_attack_range = False
        self.show_ui_debug = False
        self.show_ranged_debug = False
        self.debug_info = []
        self.font = pygame.font.Font(None, 20)
        self.debug_font = pygame.font.Font(None, 16)
        
    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        print(f"DEBUG MODE: {self.debug_mode}")
        
    def toggle_move_range_debug(self):
        self.show_move_range = not self.show_move_range
        print(f"MOVE RANGE DEBUG: {self.show_move_range}")
        
    def toggle_attack_range_debug(self):
        self.show_attack_range = not self.show_attack_range
        print(f"ATTACK RANGE DEBUG: {self.show_attack_range}")
        
    def toggle_ui_debug(self):
        self.show_ui_debug = not self.show_ui_debug
        print(f"UI DEBUG: {self.show_ui_debug}")
        
    def toggle_ranged_debug(self):
        self.show_ranged_debug = not self.show_ranged_debug
        print(f"RANGED DEBUG: {self.show_ranged_debug}")
    
    def debug_move_range(self, surface):
        """Отлаживает отображение дальности хода"""
        if not self.show_move_range or not self.game.selected_unit:
            return
            
        unit = self.game.selected_unit
        if isinstance(unit, Hero):
            return
            
        # Показываем текущую позицию юнита
        pygame.draw.rect(surface, (255, 0, 0), 
                        (unit.x * CELL_SIZE, unit.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        
        # Показываем все достижимые клетки
        if hasattr(unit, 'move_points_left') and unit.move_points_left > 0:
            reachable = self.game.get_reachable_cells(unit.x, unit.y, unit.move_points_left)
            for x, y in reachable:
                pygame.draw.rect(surface, (0, 255, 0), 
                               (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
        
        # Показываем информацию о юните
        info = [
            f"Юнит: {unit.unit_type}",
            f"Позиция: ({unit.x}, {unit.y})",
            f"Скорость: {unit.speed}",
            f"Очки хода: {getattr(unit, 'move_points_left', 0)}",
            f"Походил: {getattr(unit, 'has_moved', False)}"
        ]
        
        y_offset = 10
        for line in info:
            text = self.debug_font.render(line, True, (255, 255, 255))
            surface.blit(text, (10, y_offset))
            y_offset += 20
    
    def debug_attack_range(self, surface):
        """Отлаживает дальность атаки дальнобойных юнитов"""
        if not self.show_attack_range or not self.game.selected_unit:
            return
            
        unit = self.game.selected_unit
        if not getattr(unit, 'is_ranged', False):
            return
            
        # Показываем текущую позицию юнита
        pygame.draw.rect(surface, (255, 0, 0), 
                        (unit.x * CELL_SIZE, unit.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        
        # Показываем все клетки, которые можно атаковать
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if unit.can_attack(x, y, self.game.units):
                    # Проверяем, есть ли враг на этой клетке
                    enemy = None
                    for u in self.game.units:
                        if u.x == x and u.y == y and u.team != unit.team:
                            enemy = u
                            break
                    
                    if enemy:
                        pygame.draw.rect(surface, (255, 0, 0), 
                                       (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
                    else:
                        pygame.draw.rect(surface, (255, 255, 0), 
                                       (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
        
        # Показываем информацию о дальнобойном юните
        info = [
            f"Дальнобойный юнит: {unit.unit_type}",
            f"Позиция: ({unit.x}, {unit.y})",
            f"is_ranged: {getattr(unit, 'is_ranged', False)}",
            f"Атаковал: {getattr(unit, 'has_attacked', False)}"
        ]
        
        y_offset = 150
        for line in info:
            text = self.debug_font.render(line, True, (255, 255, 255))
            surface.blit(text, (10, y_offset))
            y_offset += 20
    
    def debug_ui_elements(self, surface):
        """Отлаживает отображение элементов интерфейса"""
        if not self.show_ui_debug:
            return
            
        # Показываем границы всех кнопок
        buttons = [
            ("Skip", self.game.skip_button_rect, (180, 180, 80)),
            ("Defend", self.game.defend_button_rect, (120, 180, 220)),
            ("Book", self.game.book_button_rect, (180, 120, 60)),
            ("History", self.game.history_button_rect, (80, 120, 200))
        ]
        
        for name, rect, color in buttons:
            pygame.draw.rect(surface, color, rect, 3)
            text = self.debug_font.render(name, True, (255, 255, 255))
            surface.blit(text, (rect.x, rect.y - 20))
        
        # Показываем информацию о выбранном юните
        if self.game.selected_unit:
            info = [
                f"Выбран: {self.game.selected_unit.unit_type}",
                f"Команда: {self.game.selected_unit.team}",
                f"Позиция: ({self.game.selected_unit.x}, {self.game.selected_unit.y})",
                f"Герой: {isinstance(self.game.selected_unit, Hero)}"
            ]
            
            y_offset = 250
            for line in info:
                text = self.debug_font.render(line, True, (255, 255, 255))
                surface.blit(text, (10, y_offset))
                y_offset += 20
    
    def debug_ranged_attack_logic(self, surface):
        """Отлаживает логику стрельбы дальнобойных юнитов"""
        if not self.show_ranged_debug:
            return
            
        # Находим все дальнобойные юниты
        ranged_units = [u for u in self.game.units if getattr(u, 'is_ranged', False)]
        
        info = ["=== ДАЛЬНОБОЙНЫЕ ЮНИТЫ ==="]
        for unit in ranged_units:
            info.append(f"{unit.unit_type} ({unit.team}) на ({unit.x}, {unit.y})")
            
            # Проверяем, может ли атаковать в разных направлениях
            directions = [
                ("вверх", 0, -1),
                ("вниз", 0, 1),
                ("влево", -1, 0),
                ("вправо", 1, 0),
                ("по диагонали", 1, 1)
            ]
            
            for dir_name, dx, dy in directions:
                target_x = unit.x + dx * 3  # Проверяем на расстоянии 3
                target_y = unit.y + dy * 3
                
                if 0 <= target_x < GRID_WIDTH and 0 <= target_y < GRID_HEIGHT:
                    can_attack = unit.can_attack(target_x, target_y, self.game.units)
                    info.append(f"  {dir_name}: {'ДА' if can_attack else 'НЕТ'}")
        
        # Отображаем информацию
        y_offset = 350
        for line in info:
            text = self.debug_font.render(line, True, (255, 255, 255))
            surface.blit(text, (10, y_offset))
            y_offset += 20
    
    def debug_can_attack_method(self, unit, target_x, target_y):
        """Детально отлаживает метод can_attack для дальнобойных юнитов"""
        if not getattr(unit, 'is_ranged', False):
            return False
            
        print(f"\n=== DEBUG can_attack для {unit.unit_type} ===")
        print(f"Позиция юнита: ({unit.x}, {unit.y})")
        print(f"Цель: ({target_x}, {target_y})")
        
        dx = abs(unit.x - target_x)
        dy = abs(unit.y - target_y)
        print(f"Расстояние по X: {dx}, по Y: {dy}")
        
        # Проверяем, что цель не на той же клетке
        if unit.x == target_x and unit.y == target_y:
            print("❌ Цель на той же клетке")
            return False
        
        # Проверяем, что цель на одной линии (горизонталь, вертикаль или диагональ)
        is_horizontal = unit.y == target_y
        is_vertical = unit.x == target_x
        is_diagonal = dx == dy
        
        print(f"Горизонталь: {is_horizontal}")
        print(f"Вертикаль: {is_vertical}")
        print(f"Диагональ: {is_diagonal}")
        
        if not (is_horizontal or is_vertical or is_diagonal):
            print("❌ Цель не на одной линии")
            return False
        
        # Проверяем препятствия
        if self.game.units is not None:
            steps = max(dx, dy)
            step_x = (target_x - unit.x) // steps if steps else 0
            step_y = (target_y - unit.y) // steps if steps else 0
            
            print(f"Шагов: {steps}")
            print(f"Шаг по X: {step_x}, по Y: {step_y}")
            
            cx, cy = unit.x, unit.y
            for i in range(1, steps):
                cx += step_x
                cy += step_y
                print(f"Проверяем клетку ({cx}, {cy})")
                
                for u in self.game.units:
                    if u != unit and u.x == cx and u.y == cy:
                        print(f"❌ Препятствие: {u.unit_type} на ({cx}, {cy})")
                        return False
        
        print("✅ Атака возможна")
        return True
    
    def debug_unit_images(self, surface):
        """Отлаживает загрузку и отображение изображений юнитов"""
        if not self.debug_mode:
            return
            
        # Показываем информацию о всех юнитах и их изображениях
        info = ["=== ИЗОБРАЖЕНИЯ ЮНИТОВ ==="]
        
        for unit in self.game.units:
            img_info = f"{unit.unit_type} ({unit.team}): "
            if hasattr(unit, 'image') and unit.image:
                img_info += f"✅ {unit.image.get_size()}"
            else:
                img_info += "❌ НЕТ ИЗОБРАЖЕНИЯ"
            info.append(img_info)
        
        # Отображаем информацию
        y_offset = 450
        for line in info:
            text = self.debug_font.render(line, True, (255, 255, 255))
            surface.blit(text, (10, y_offset))
            y_offset += 20
    
    def debug_ui_visibility(self, surface):
        """Отлаживает видимость элементов интерфейса"""
        if not self.show_ui_debug:
            return
            
        # Показываем координаты и размеры всех элементов интерфейса
        ui_elements = [
            ("Нижняя панель", pygame.Rect(0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80)),
            ("Skip кнопка", self.game.skip_button_rect),
            ("Defend кнопка", self.game.defend_button_rect),
            ("Book кнопка", self.game.book_button_rect),
            ("History кнопка", self.game.history_button_rect),
            ("Wait кнопка", pygame.Rect(self.game.skip_button_rect.x - 70, self.game.skip_button_rect.y, 48, 48))
        ]
        
        info = ["=== ЭЛЕМЕНТЫ ИНТЕРФЕЙСА ==="]
        for name, rect in ui_elements:
            info.append(f"{name}: {rect}")
        
        # Отображаем информацию
        y_offset = 550
        for line in info:
            text = self.debug_font.render(line, True, (255, 255, 255))
            surface.blit(text, (10, y_offset))
            y_offset += 20
    
    def debug_move_range_issues(self, surface):
        """Специальная отладка проблем с дальностью хода"""
        if not self.show_move_range or not self.game.selected_unit:
            return
            
        unit = self.game.selected_unit
        if isinstance(unit, Hero):
            return
            
        # Проверяем, правильно ли работает get_reachable_cells
        if hasattr(unit, 'move_points_left') and unit.move_points_left > 0:
            reachable = self.game.get_reachable_cells(unit.x, unit.y, unit.move_points_left)
            
            info = [
                f"=== ОТЛАДКА ДАЛЬНОСТИ ХОДА ===",
                f"Юнит: {unit.unit_type}",
                f"Позиция: ({unit.x}, {unit.y})",
                f"Скорость: {unit.speed}",
                f"Очки хода: {unit.move_points_left}",
                f"Достижимых клеток: {len(reachable)}"
            ]
            
            # Показываем первые несколько достижимых клеток
            for i, (x, y) in enumerate(list(reachable)[:5]):
                info.append(f"  Клетка {i+1}: ({x}, {y})")
            
            if len(reachable) > 5:
                info.append(f"  ... и ещё {len(reachable) - 5} клеток")
            
            # Отображаем информацию
            y_offset = 650
            for line in info:
                text = self.debug_font.render(line, True, (255, 255, 255))
                surface.blit(text, (10, y_offset))
                y_offset += 20
    
    def debug_ranged_attack_directions(self, surface):
        """Специальная отладка направлений атаки дальнобойных юнитов"""
        if not self.show_ranged_debug:
            return
            
        # Находим все дальнобойные юниты
        ranged_units = [u for u in self.game.units if getattr(u, 'is_ranged', False)]
        
        if not ranged_units:
            return
            
        unit = ranged_units[0]  # Берём первого для примера
        
        info = [
            f"=== ОТЛАДКА ДАЛЬНОБОЙНОЙ АТАКИ ===",
            f"Юнит: {unit.unit_type} ({unit.team})",
            f"Позиция: ({unit.x}, {unit.y})",
            f"is_ranged: {getattr(unit, 'is_ranged', False)}"
        ]
        
        # Тестируем атаку в разных направлениях
        test_directions = [
            ("вверх", 0, -3),
            ("вниз", 0, 3),
            ("влево", -3, 0),
            ("вправо", 3, 0),
            ("по диагонали вправо-вверх", 3, -3),
            ("по диагонали влево-вниз", -3, 3)
        ]
        
        for dir_name, dx, dy in test_directions:
            target_x = unit.x + dx
            target_y = unit.y + dy
            
            if 0 <= target_x < GRID_WIDTH and 0 <= target_y < GRID_HEIGHT:
                can_attack = unit.can_attack(target_x, target_y, self.game.units)
                info.append(f"  {dir_name}: {'✅' if can_attack else '❌'}")
            else:
                info.append(f"  {dir_name}: за пределами поля")
        
        # Отображаем информацию
        y_offset = 750
        for line in info:
            text = self.debug_font.render(line, True, (255, 255, 255))
            surface.blit(text, (10, y_offset))
            y_offset += 20

    def draw_debug_overlay(self, surface):
        """Рисует все отладочные элементы"""
        if not self.debug_mode:
            return
            
        # Полупрозрачный фон для отладочной информации
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))
        
        # Заголовок отладки
        title = self.font.render("DEBUG MODE", True, (255, 255, 0))
        surface.blit(title, (SCREEN_WIDTH - 150, 10))
        
        # Кнопки переключения отладки
        debug_buttons = [
            ("MOVE", self.show_move_range, (SCREEN_WIDTH - 100, 40)),
            ("ATTACK", self.show_attack_range, (SCREEN_WIDTH - 100, 60)),
            ("UI", self.show_ui_debug, (SCREEN_WIDTH - 100, 80)),
            ("RANGED", self.show_ranged_debug, (SCREEN_WIDTH - 100, 100))
        ]
        
        for name, active, pos in debug_buttons:
            color = (0, 255, 0) if active else (255, 0, 0)
            text = self.debug_font.render(name, True, color)
            surface.blit(text, pos)
        
        # Вызываем все отладочные функции
        self.debug_move_range(surface)
        self.debug_attack_range(surface)
        self.debug_ui_elements(surface)
        self.debug_ranged_attack_logic(surface)
        self.debug_unit_images(surface)
        self.debug_ui_visibility(surface)
        self.debug_move_range_issues(surface)
        self.debug_ranged_attack_directions(surface)
    
    def handle_debug_key(self, key):
        """Обрабатывает клавиши отладки"""
        if key == pygame.K_F1:
            self.toggle_debug_mode()
        elif key == pygame.K_F2:
            self.toggle_move_range_debug()
        elif key == pygame.K_F3:
            self.toggle_attack_range_debug()
        elif key == pygame.K_F4:
            self.toggle_ui_debug()
        elif key == pygame.K_F5:
            self.toggle_ranged_debug()
        elif key == pygame.K_F6:
            # Тестируем can_attack для выбранного юнита
            if self.game.selected_unit and getattr(self.game.selected_unit, 'is_ranged', False):
                unit = self.game.selected_unit
                print(f"\n=== ТЕСТ can_attack для {unit.unit_type} ===")
                
                # Тестируем атаку в разных направлениях
                test_targets = [
                    (unit.x, unit.y - 3, "вверх"),
                    (unit.x, unit.y + 3, "вниз"),
                    (unit.x - 3, unit.y, "влево"),
                    (unit.x + 3, unit.y, "вправо"),
                    (unit.x + 2, unit.y + 2, "по диагонали")
                ]
                
                for tx, ty, direction in test_targets:
                    if 0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT:
                        result = unit.can_attack(tx, ty, self.game.units)
                        print(f"Атака {direction} ({tx}, {ty}): {'✅' if result else '❌'}")
    
    def print_unit_info(self, unit):
        """Выводит подробную информацию о юните"""
        print(f"\n=== ИНФОРМАЦИЯ О ЮНИТЕ ===")
        print(f"Тип: {unit.unit_type}")
        print(f"Команда: {unit.team}")
        print(f"Позиция: ({unit.x}, {unit.y})")
        print(f"Здоровье: {unit.health}/{unit.max_health}")
        print(f"Атака: {unit.attack}")
        print(f"Защита: {unit.defense}")
        print(f"Скорость: {unit.speed}")
        print(f"Инициатива: {unit.initiative}")
        print(f"Дальнобойный: {getattr(unit, 'is_ranged', False)}")
        print(f"Диапазон атаки: {getattr(unit, 'attack_range', 1)}")
        print(f"Очки хода: {getattr(unit, 'move_points_left', 0)}")
        print(f"Походил: {getattr(unit, 'has_moved', False)}")
        print(f"Атаковал: {getattr(unit, 'has_attacked', False)}")
        print(f"Герой: {isinstance(unit, Hero)}") 