#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки применения параметров из редактора
"""
import json
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_overrides():
    """Проверяет применение параметров из unit_overrides.json"""
    
    # Загружаем оверрайды
    overrides_path = os.path.join('data', 'unit_overrides.json')
    if not os.path.exists(overrides_path):
        print(f"❌ Файл {overrides_path} не найден!")
        return
    
    with open(overrides_path, 'r', encoding='utf-8') as f:
        overrides = json.load(f)
    
    print("=" * 60)
    print("ПРОВЕРКА ПАРАМЕТРОВ ИЗ РЕДАКТОРА")
    print("=" * 60)
    print(f"\n📁 Загружено оверрайдов: {len(overrides)}")
    
    # Проверяем, какие параметры есть в оверрайдах
    for key, data in overrides.items():
        print(f"\n🔹 {key}:")
        for param, value in data.items():
            print(f"   {param} = {value}")
    
    # Проверяем импорт и создание юнитов
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ПРИМЕНЕНИЯ ПАРАМЕТРОВ")
    print("=" * 60)
    
    try:
        from game.units import Hero, Peasant, Skeleton
        from game.core import Game
        
        # Создаем тестовый герой с классом mage
        print("\n🧙 Создание тестового героя (human mage)...")
        hero = Hero(0, 0, 'human', attack=0, defense=0, knowledge=0, spell_power=0, hero_class='mage')
        print(f"   До оверрайдов: attack={hero.attack}, defense={hero.defense}, knowledge={hero.knowledge}, luck={getattr(hero, 'luck', 'N/A')}, combat_spirit={getattr(hero, 'combat_spirit', 'N/A')}")
        
        # Симулируем применение оверрайдов (как в _apply_unit_overrides_to_instance)
        print("\n📝 Применение оверрайдов (логика из _apply_unit_overrides_to_instance)...")
        hero_data = None
        # Проверяем специфичный оверрайд для race+class
        if hero.team and hero.hero_class:
            key = f"Hero_{hero.team}_{hero.hero_class}"
            if key in overrides:
                hero_data = overrides[key]
                print(f"   ✓ Найден специфичный оверрайд: {key}")
        # Если не нашли, ищем по расе
        if not hero_data and hero.team:
            key = f"Hero_{hero.team}"
            if key in overrides:
                hero_data = overrides[key]
                print(f"   ✓ Найден оверрайд по расе: {key}")
        # Если и это не нашли, используем общий Hero
        if not hero_data:
            if 'Hero' in overrides:
                hero_data = overrides['Hero']
                print(f"   ✓ Использован общий оверрайд: Hero")
        
        if hero_data:
            for key in ['max_health','health','attack','defense','speed','initiative','attack_range','is_ranged',
                       'knowledge','spell_power','mana','max_mana','mana_regen',
                       'phys_attack','magic_attack','phys_defense','magic_defense','magic_resist','attack_type','hero_class',
                       'squad_count','base_squad_count','luck','combat_spirit']:
                if key in hero_data:
                    if hasattr(hero, key):
                        old_value = getattr(hero, key)
                        setattr(hero, key, hero_data[key])
                        new_value = getattr(hero, key)
                        print(f"   {key}: {old_value} → {new_value}")
                    else:
                        print(f"   ⚠️ {key} не существует у Hero")
        else:
            print("   ❌ Оверрайды не найдены!")
        
        print(f"\n   После оверрайдов: attack={hero.attack}, defense={hero.defense}, knowledge={hero.knowledge}, luck={getattr(hero, 'luck', 'N/A')}, combat_spirit={getattr(hero, 'combat_spirit', 'N/A')}")
        
        # Проверяем обычного юнита
        print("\n⚔️ Создание тестового юнита...")
        unit = Peasant(0, 0, 'human')
        print(f"   До оверрайдов: health={unit.health}, max_health={unit.max_health}, squad_count={getattr(unit, 'squad_count', 'N/A')}")
        
        if 'Peasant' in overrides:
            unit_data = overrides['Peasant']
            for key, value in unit_data.items():
                if hasattr(unit, key):
                    old_value = getattr(hero, key)
                    setattr(unit, key, value)
                    print(f"   {key}: {old_value} → {value}")
        
        print(f"   После оверрайдов: health={unit.health}, max_health={unit.max_health}, squad_count={getattr(unit, 'squad_count', 'N/A')}")
        
        # Проверяем метод _apply_unit_overrides_to_instance
        print("\n" + "=" * 60)
        print("ПРОВЕРКА МЕТОДА _apply_unit_overrides_to_instance")
        print("=" * 60)
        
        # Создаем игру для доступа к методу
        import pygame
        pygame.init()
        screen = pygame.Surface((800, 600))
        game = Game(screen)
        
        # Проверяем, какие ключи обрабатываются
        print("\n📋 Проверка списка обрабатываемых ключей...")
        test_unit = Hero(0, 0, 'human', hero_class='mage')
        test_data = {'attack': 10, 'defense': 5, 'knowledge': 7, 'luck': 3, 'combat_spirit': 4, 'spell_power': 6}
        
        handled_keys = ['max_health','health','attack','defense','speed','initiative','attack_range','is_ranged',
                       'knowledge','spell_power','mana','max_mana','mana_regen',
                       'phys_attack','magic_attack','phys_defense','magic_defense','magic_resist','attack_type','hero_class',
                       'squad_count','base_squad_count','luck','combat_spirit']
        
        print("   Обрабатываемые ключи:")
        for key in handled_keys:
            marker = "✓" if key in handled_keys else "✗"
            print(f"   {marker} {key}")
        
        print("\n   Применение тестовых данных...")
        for key, value in test_data.items():
            if hasattr(test_unit, key):
                old_value = getattr(test_unit, key)
                setattr(test_unit, key, value)
                new_value = getattr(test_unit, key)
                status = "✓" if new_value == value else "✗"
                print(f"   {status} {key}: {old_value} → {new_value} (ожидалось {value})")
            else:
                print(f"   ✗ {key}: атрибут не существует")
        
        # Проверяем реальное применение через метод игры
        print("\n🔧 Проверка реального применения через _apply_unit_overrides_to_instance...")
        test_hero = Hero(0, 0, 'human', hero_class='mage', attack=0, defense=0, knowledge=0, spell_power=0)
        print(f"   До применения: attack={test_hero.attack}, luck={getattr(test_hero, 'luck', 0)}, combat_spirit={getattr(test_hero, 'combat_spirit', 0)}")
        game._apply_unit_overrides_to_instance(test_hero)
        print(f"   После применения: attack={test_hero.attack}, luck={getattr(test_hero, 'luck', 0)}, combat_spirit={getattr(test_hero, 'combat_spirit', 0)}")
        
        pygame.quit()
        
    except Exception as e:
        print(f"\n❌ Ошибка при проверке: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ЗАВЕРШЕНА")
    print("=" * 60)

if __name__ == '__main__':
    check_overrides()

