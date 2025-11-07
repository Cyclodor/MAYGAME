"""
Пример интеграции системы логирования и отладки в игру
"""

import pygame
from debug.system import (
    initialize_debug_system,
    get_debug_system,
    get_logger,
    get_metrics,
    get_validator,
    get_diagnostics,
    LogCategory,
    LogLevel
)


def example_game_integration():
    """Пример интеграции в игровой цикл"""
    
    # 1. Инициализация системы отладки
    debug_system = initialize_debug_system()
    logger = get_logger()
    metrics = get_metrics()
    
    logger.info(LogCategory.SYSTEM, "Игра запущена")
    
    # 2. В игровом цикле
    clock = pygame.time.Clock()
    running = True
    
    while running:
        delta_time = clock.tick(60) / 1000.0  # В секундах
        
        # Обновление системы отладки (важно вызывать каждый кадр)
        debug_system.update(game, delta_time)
        
        # Обновление метрик кадра
        metrics.update_frame(delta_time)
        
        # ... остальной код игры ...
        
        # Пример логирования событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info(LogCategory.SYSTEM, "Выход из игры")
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                logger.debug(LogCategory.UI, "Клик мыши", {
                    'position': event.pos,
                    'button': event.button
                })


def example_unit_actions():
    """Пример логирования действий юнита"""
    logger = get_logger()
    
    # Движение юнита
    def move_unit(unit, new_x, new_y):
        old_x, old_y = unit.x, unit.y
        unit.x, unit.y = new_x, new_y
        
        logger.log_unit_action(unit, "move", {
            'from': (old_x, old_y),
            'to': (new_x, new_y),
            'move_points_used': abs(new_x - old_x) + abs(new_y - old_y)
        })
    
    # Атака
    def attack_unit(attacker, defender):
        damage = calculate_damage(attacker, defender)
        defender.health -= damage
        
        logger.log_combat_action(attacker, defender, damage, is_ranged=False)
        
        if defender.health <= 0:
            logger.info(LogCategory.COMBAT, f"{defender.unit_type} убит", {
                'killer': attacker.unit_type,
                'final_damage': damage
            })


def example_spell_casting():
    """Пример логирования заклинаний"""
    logger = get_logger()
    validator = get_validator()
    
    def cast_spell(spell, caster, target):
        # Валидация перед применением
        issues = validator.validate_spell(spell, caster, target)
        if issues:
            for issue in issues:
                logger.error(LogCategory.VALIDATION, issue.message, issue.details)
            return False
        
        # Применение заклинания
        try:
            success = spell.apply(caster, target)
            logger.log_spell_cast(spell, caster, target, success)
            return success
        except Exception as e:
            logger.error(LogCategory.SPELLS, "Ошибка применения заклинания", 
                        exception=e, extra_data={'spell': spell.icon})
            return False


def example_ai_decision():
    """Пример логирования решений AI"""
    logger = get_logger()
    
    def ai_turn(unit, game):
        # AI принимает решение
        decision = ai_choose_action(unit, game)
        
        logger.log_ai_decision(unit, decision['action'], {
            'target': decision.get('target'),
            'reason': decision.get('reason'),
            'priority': decision.get('priority')
        })
        
        # Выполнение действия
        if decision['action'] == 'attack':
            attack_unit(unit, decision['target'])
        elif decision['action'] == 'move':
            move_unit(unit, decision['target_x'], decision['target_y'])


def example_performance_profiling():
    """Пример профилирования производительности"""
    metrics = get_metrics()
    logger = get_logger()
    
    def expensive_calculation():
        metrics.start_timer("expensive_calculation")
        
        # Тяжелые вычисления
        result = complex_algorithm()
        
        elapsed = metrics.stop_timer("expensive_calculation")
        
        # Предупреждение при медленном выполнении
        if elapsed > 0.1:  # Больше 100мс
            logger.warning(LogCategory.PERFORMANCE, 
                          f"Медленное вычисление: {elapsed:.3f}с",
                          {'function': 'expensive_calculation'})
        
        return result
    
    # Использование декоратора
    @metrics.time_function
    def another_expensive_function():
        # Код функции
        pass


def example_validation():
    """Пример использования валидации"""
    validator = get_validator()
    logger = get_logger()
    
    def validate_game_state_periodically(game):
        # Периодическая валидация
        issues = validator.validate_all(game)
        
        if issues:
            # Группируем по серьезности
            critical = [i for i in issues if i.severity.value == 'CRITICAL']
            errors = [i for i in issues if i.severity.value == 'ERROR']
            warnings = [i for i in issues if i.severity.value == 'WARNING']
            
            if critical:
                logger.critical(LogCategory.VALIDATION, 
                               f"Обнаружено {len(critical)} критических проблем")
            if errors:
                logger.error(LogCategory.VALIDATION, 
                           f"Обнаружено {len(errors)} ошибок")
            if warnings:
                logger.warning(LogCategory.VALIDATION, 
                              f"Обнаружено {len(warnings)} предупреждений")
    
    # Регистрация кастомного правила
    def check_custom_rule(game):
        from debug.system.validator import ValidationIssue, ValidationSeverity
        
        if some_custom_condition(game):
            return ValidationIssue(
                ValidationSeverity.ERROR,
                'custom_category',
                'Описание проблемы',
                {'extra': 'data'}
            )
        return None
    
    validator.register_rule('custom', check_custom_rule)


def example_diagnostics():
    """Пример использования диагностики"""
    diagnostics = get_diagnostics()
    logger = get_logger()
    
    def run_diagnostics_periodically(game):
        # Запуск всех проверок
        results = diagnostics.run_all_checks(game)
        
        # Получение сводки
        summary = diagnostics.get_summary()
        
        # Проверка неудачных проверок
        failed = diagnostics.get_failed_checks()
        if failed:
            logger.warning(LogCategory.DIAGNOSTICS, 
                          f"Неудачные проверки: {', '.join(failed)}")
    
    # Регистрация кастомной проверки
    def check_custom_condition(game):
        from debug.system.diagnostics import DiagnosticResult
        
        if some_condition(game):
            return DiagnosticResult.OK
        return DiagnosticResult.WARNING
    
    diagnostics.register_check(
        'custom_check',
        'Описание проверки',
        check_custom_condition,
        DiagnosticResult.WARNING
    )


def example_saving_reports():
    """Пример сохранения отчетов"""
    debug_system = get_debug_system()
    
    def save_all_reports():
        # Сохранение всех отчетов
        debug_system.save_all_reports("debug/reports")
        
        # Или отдельно
        logger = get_logger()
        metrics = get_metrics()
        
        logger.save_stats_report()
        metrics.save_metrics_report()


# Вспомогательные функции (заглушки)
def calculate_damage(attacker, defender):
    return 10

def ai_choose_action(unit, game):
    return {'action': 'wait', 'reason': 'no_target'}

def complex_algorithm():
    return None

def some_custom_condition(game):
    return False

def some_condition(game):
    return True


