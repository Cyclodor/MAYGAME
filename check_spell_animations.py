"""
Временный файл для проверки анимаций заклинаний
Проверяет какие заклинания используют какие анимации
"""

# Словарь заклинаний и их анимаций
SPELL_ANIMATIONS = {
    # Заклинания БЕЗ анимации полета снаряда (мгновенные)
    'instant': [
        'lightning',      # Молния - анимация в самом заклинании
        'weakness',       # Слабость - мгновенное наложение эффекта
        'bless',          # Благословение - мгновенный баф
        'curse',          # Проклятие - мгновенный дебаф
        'slow',           # Замедление - мгновенный дебаф
        'haste',          # Ускорение - мгновенный баф
        'heal',           # Лечение - мгновенное восстановление
        'dispel',         # Снятие чар - мгновенное
        'stone_skin',     # Каменная кожа - мгновенный баф
        'ice_shield',     # Ледяной щит - мгновенный баф
        'fire_shield',    # Огненный щит - мгновенный баф
        'counterstrike',  # Контрудар - мгновенный баф
        'rune_shield',    # Руна защиты - мгновенный баф
        'rune_haste',     # Руна скорости - мгновенный баф
        'raise_dead',     # Призыв скелета - мгновенное призывание
        'resurrection',   # Воскрешение - мгновенное воскрешение
        'undead_heal',    # Лечение нежити - мгновенное восстановление
        'forget',         # Забвение - мгновенный дебаф
        'earth_spikes',   # Каменные шипы - анимация в заклинании
        'rune_wall',      # Рунная стена - мгновенное создание стены
    ],
    
    # Заклинания С анимацией полета снаряда
    'projectile': [
        'firearrow',      # Огненная стрела - специальная анимация
        'fireball',       # Огненный шар - специальная анимация фаербола
        'frost_ring',     # Кольцо холода - анимация полета снаряда
    ],
    
    # Заклинания со специальной анимацией
    'special': [
        'firearrow',      # Своя анимация стрелы
        'fireball',       # Своя анимация шара и взрыва
        'lightning',      # Своя анимация молнии
        'earth_spikes',   # Своя анимация шипов
    ]
}

def check_spell_animation(spell_icon, spell_name):
    """
    Проверяет какую анимацию должно использовать заклинание
    Возвращает тип анимации: 'instant', 'projectile', 'special'
    """
    # Проверяем мгновенные заклинания
    if spell_icon in SPELL_ANIMATIONS['instant']:
        return 'instant'
    
    # Проверяем специальные анимации
    if spell_icon in SPELL_ANIMATIONS['special']:
        return 'special'
    
    # Проверяем заклинания с полетом снаряда
    if spell_icon in SPELL_ANIMATIONS['projectile']:
        return 'projectile'
    
    # По умолчанию - мгновенное
    return 'instant'

def should_use_projectile_animation(spell_icon, spell_name):
    """
    Определяет, нужно ли использовать анимацию полета снаряда
    """
    animation_type = check_spell_animation(spell_icon, spell_name)
    
    # Только для projectile используем анимацию полета
    # Для special - своя анимация внутри заклинания
    # Для instant - никакой анимации полета
    return animation_type == 'projectile'

# Тесты
if __name__ == "__main__":
    print("=== ПРОВЕРКА АНИМАЦИЙ ЗАКЛИНАНИЙ ===\n")
    
    test_spells = [
        ('lightning', 'Молния'),
        ('weakness', 'Слабость'),
        ('firearrow', 'Огненная стрела'),
        ('fireball', 'Огненный шар'),
        ('frost_ring', 'Кольцо холода'),
        ('bless', 'Благословение'),
        ('heal', 'Лечение'),
    ]
    
    for icon, name in test_spells:
        anim_type = check_spell_animation(icon, name)
        use_projectile = should_use_projectile_animation(icon, name)
        print(f"{name} ({icon}):")
        print(f"  Тип анимации: {anim_type}")
        print(f"  Использовать полет снаряда: {'ДА' if use_projectile else 'НЕТ'}")
        print()
    
    print("\n=== РЕКОМЕНДАЦИИ ===")
    print("1. Молния и Слабость НЕ должны иметь анимацию полета снаряда")
    print("2. Огненная стрела и Огненный шар имеют свою специальную анимацию")
    print("3. Кольцо холода использует стандартную анимацию полета снаряда")
    print("4. Все баффы/дебаффы мгновенные")


