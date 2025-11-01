"""
Логгер анимаций для отладки
Записывает все анимации, которые проигрываются во время игры
"""
import time
from datetime import datetime

class AnimationLogger:
    """Класс для логирования анимаций"""
    
    def __init__(self, log_file='animation_log.txt'):
        self.log_file = log_file
        self.enabled = True
        self.session_start = datetime.now()
        
        # Очищаем файл при создании логгера
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== ЛОГ АНИМАЦИЙ ===\n")
            f.write(f"Начало сессии: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def log(self, animation_name, details=None):
        """Записывает анимацию в лог"""
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        elapsed = (datetime.now() - self.session_start).total_seconds()
        
        log_entry = f"[{timestamp}] (+{elapsed:.2f}s) {animation_name}"
        
        if details:
            log_entry += f" | {details}"
        
        log_entry += "\n"
        
        # Записываем в файл
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Также выводим в консоль для отладки
        print(f"[ANIM] {log_entry.strip()}")
    
    def log_spell_animation(self, spell_name, spell_icon, caster, target=None, is_instant=False):
        """Логирует анимацию заклинания"""
        details = f"Заклинание: {spell_name} ({spell_icon})"
        details += f" | Кастер: {caster.unit_type}"
        
        if target:
            details += f" | Цель: {target.unit_type}"
        
        if is_instant:
            details += " | ТИП: Мгновенное (без снаряда)"
        else:
            details += " | ТИП: С полетом снаряда"
        
        self.log("SPELL_ANIMATION", details)
    
    def log_attack_animation(self, attacker, defender, is_ranged=False):
        """Логирует анимацию атаки"""
        attack_type = "Дальнобойная" if is_ranged else "Ближняя"
        details = f"{attack_type} атака | Атакующий: {attacker.unit_type} | Защитник: {defender.unit_type}"
        self.log("ATTACK_ANIMATION", details)
    
    def log_movement_animation(self, unit, from_pos, to_pos):
        """Логирует анимацию перемещения"""
        details = f"Юнит: {unit.unit_type} | От ({from_pos[0]}, {from_pos[1]}) к ({to_pos[0]}, {to_pos[1]})"
        self.log("MOVEMENT_ANIMATION", details)
    
    def log_effect_animation(self, effect_name, target, duration=None):
        """Логирует анимацию эффекта"""
        details = f"Эффект: {effect_name} | Цель: {target.unit_type}"
        if duration:
            details += f" | Длительность: {duration}"
        self.log("EFFECT_ANIMATION", details)
    
    def log_projectile_animation(self, projectile_type, start, end, color=None):
        """Логирует анимацию снаряда"""
        details = f"Снаряд: {projectile_type} | От {start} к {end}"
        if color:
            details += f" | Цвет: {color}"
        self.log("PROJECTILE_ANIMATION", details)
    
    def log_round_start(self, round_number):
        """Логирует начало раунда"""
        self.log("ROUND_START", f"Раунд {round_number}")
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n")
    
    def enable(self):
        """Включает логирование"""
        self.enabled = True
        self.log("LOGGER_ENABLED", "Логирование включено")
    
    def disable(self):
        """Выключает логирование"""
        self.log("LOGGER_DISABLED", "Логирование выключено")
        self.enabled = False

# Глобальный экземпляр логгера
_logger = None

def get_logger():
    """Получить глобальный логгер"""
    global _logger
    if _logger is None:
        _logger = AnimationLogger()
    return _logger

def log_animation(animation_name, details=None):
    """Быстрый доступ к логированию"""
    get_logger().log(animation_name, details)

# Тестирование
if __name__ == "__main__":
    logger = AnimationLogger('test_animation_log.txt')
    
    print("Тестирование логгера анимаций...")
    
    class MockUnit:
        def __init__(self, unit_type):
            self.unit_type = unit_type
    
    # Тест 1: Логирование заклинания
    caster = MockUnit("hero")
    target = MockUnit("skeleton")
    logger.log_spell_animation("Молния", "lightning", caster, target, is_instant=True)
    
    # Тест 2: Логирование атаки
    attacker = MockUnit("knight")
    defender = MockUnit("zombie")
    logger.log_attack_animation(attacker, defender, is_ranged=False)
    
    # Тест 3: Логирование снаряда
    logger.log_projectile_animation("magic_bolt", (100, 100), (200, 200), (255, 0, 0))
    
    # Тест 4: Логирование эффекта
    logger.log_effect_animation("Благословение", target, duration=3)
    
    # Тест 5: Начало раунда
    logger.log_round_start(2)
    
    print("\n✓ Тест завершен. Проверьте файл test_animation_log.txt")


