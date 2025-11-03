"""
Файл для отладки заклинания Воскрешение
Логирует все попытки каста и детали выполнения
"""

import os
import datetime

DEBUG_FILE = "resurrection_debug.log"

def log_resurrection(message, **kwargs):
    """Записывает сообщение в лог-файл с временной меткой"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_entry = f"[{timestamp}] {message}"
    
    # Добавляем дополнительные параметры если они есть
    if kwargs:
        for key, value in kwargs.items():
            log_entry += f" | {key}={value}"
    
    log_entry += "\n"
    
    with open(DEBUG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def clear_log():
    """Очищает лог-файл"""
    if os.path.exists(DEBUG_FILE):
        with open(DEBUG_FILE, "w", encoding="utf-8") as f:
            f.write("=== Лог отладки воскрешения ===\n\n")

def log_spell_cast(caster, spell, target_pos, has_target):
    """Логирует попытку каста заклинания"""
    caster_info = f"{caster.unit_type}"
    if hasattr(caster, 'hero_class'):
        caster_info += f" ({caster.hero_class})"
    log_resurrection(
        "ПОПЫТКА_КАСТА",
        кастер=caster_info,
        заклинание=spell.name if hasattr(spell, 'name') else 'unknown',
        иконка=spell.icon if hasattr(spell, 'icon') else 'unknown',
        позиция=f"({target_pos[0]}, {target_pos[1]})",
        есть_цель=has_target,
        мана_кастера=getattr(caster, 'mana', 'N/A'),
        стоимость_маны=getattr(spell, 'mana_cost', 'N/A')
    )

def log_spell_check(caster, spell, target_pos, living_unit, corpse):
    """Логирует проверку перед применением заклинания"""
    log_resurrection(
        "ПРОВЕРКА_ЗАКЛИНАНИЯ",
        позиция=f"({target_pos[0]}, {target_pos[1]})",
        живой_юнит=f"{living_unit.unit_type if living_unit else 'None'} ({living_unit.team if living_unit else 'None'})",
        труп=f"{'Да' if corpse else 'Нет'}"
    )

def log_resurrection_logic(unit, base_squad, dead_units, heal, unit_hp, units_to_resurrect):
    """Логирует логику воскрешения отряда"""
    log_resurrection(
        "ЛОГИКА_ВОСКРЕШЕНИЯ_ОТРЯДА",
        юнит=unit.unit_type,
        текущий_отряд=getattr(unit, 'squad_count', 'N/A'),
        базовый_отряд=base_squad,
        мертвые_юниты=dead_units,
        лечение=heal,
        HP_юнита=unit_hp,
        воскрешено_юнитов=units_to_resurrect
    )

def log_heal_logic(unit, health_before, heal, actual_heal):
    """Логирует логику лечения"""
    log_resurrection(
        "ЛОГИКА_ЛЕЧЕНИЯ",
        юнит=unit.unit_type,
        здоровье_до=health_before,
        лечение=heal,
        фактическое_лечение=actual_heal
    )

def log_result(success, message):
    """Логирует результат применения заклинания"""
    log_resurrection(
        "РЕЗУЛЬТАТ",
        успех=success,
        сообщение=message
    )

