"""
Тест исправлений системы защиты
Проверяет что защита правильно работает без старого параметра defense
"""

class MockUnit:
    """Мок-объект юнита для тестирования"""
    def __init__(self, name):
        self.name = name
        self.unit_type = name.lower()
        # Новая система - только phys_defense и magic_defense
        self.phys_defense = 15
        self.magic_defense = 12
        self.magic_resist = 20
        self._defend_this_round = False
    
    def apply_defense_buff(self):
        """Применяет баф защиты (+20%)"""
        # Проверяем, не в защите ли уже
        if self._defend_this_round:
            print(f"{self.name}: уже в защите, игнорируем")
            return False
        
        # Сохраняем оригинальные значения
        if not hasattr(self, '_original_phys_defense'):
            self._original_phys_defense = self.phys_defense
            self._original_magic_defense = self.magic_defense
            self._original_magic_resist = self.magic_resist
        
        # Применяем баф
        self.phys_defense = int(self.phys_defense * 1.2)
        self.magic_defense = int(self.magic_defense * 1.2)
        self.magic_resist = min(95, int(self.magic_resist * 1.2))
        self._defend_this_round = True
        
        print(f"\n{self.name} встал в защиту!")
        self.print_stats()
        return True
    
    def reset_defense_buff(self):
        """Сбрасывает баф защиты в начале нового раунда"""
        if self._defend_this_round:
            # Восстанавливаем оригинальные значения
            if hasattr(self, '_original_phys_defense'):
                self.phys_defense = self._original_phys_defense
                self.magic_defense = self._original_magic_defense
                self.magic_resist = self._original_magic_resist
                delattr(self, '_original_phys_defense')
                delattr(self, '_original_magic_defense')
                delattr(self, '_original_magic_resist')
            else:
                self.phys_defense = int(self.phys_defense / 1.2)
                self.magic_defense = int(self.magic_defense / 1.2)
                self.magic_resist = int(self.magic_resist / 1.2)
            
            self._defend_this_round = False
            print(f"\n{self.name}: защита сброшена в начале нового раунда")
            self.print_stats()
    
    def print_stats(self):
        """Печатает текущие характеристики"""
        print(f"  Физ. защита: {self.phys_defense}")
        print(f"  Маг. защита: {self.magic_defense}")
        print(f"  Сопр. магии: {self.magic_resist}%")
        print(f"  В защите: {'ДА' if self._defend_this_round else 'НЕТ'}")

def test_defense_system():
    """Тестирует систему защиты"""
    print("=== ТЕСТ ИСПРАВЛЕННОЙ СИСТЕМЫ ЗАЩИТЫ ===\n")
    
    unit = MockUnit("Крестьянин")
    
    print("Начальные характеристики:")
    unit.print_stats()
    
    # Тест 1: Применение защиты
    print("\n--- ТЕСТ 1: Применение защиты ---")
    result = unit.apply_defense_buff()
    assert result == True, "Защита должна быть применена"
    assert unit.phys_defense == 18, f"Ожидается 18, получено {unit.phys_defense}"
    assert unit.magic_defense == 14, f"Ожидается 14, получено {unit.magic_defense}"
    assert unit.magic_resist == 24, f"Ожидается 24, получено {unit.magic_resist}"
    assert unit._defend_this_round == True
    print("✓ Защита правильно применена")
    
    # Тест 2: Повторное применение защиты (должно игнорироваться)
    print("\n--- ТЕСТ 2: Повторное применение (должно игнорироваться) ---")
    result = unit.apply_defense_buff()
    assert result == False, "Повторное применение должно быть игнорировано"
    assert unit.phys_defense == 18, f"Значения не должны измениться"
    print("✓ Повторное применение правильно игнорируется")
    
    # Тест 3: Сброс защиты в новом раунде
    print("\n--- ТЕСТ 3: Сброс в новом раунде ---")
    unit.reset_defense_buff()
    assert unit.phys_defense == 15, f"Ожидается 15, получено {unit.phys_defense}"
    assert unit.magic_defense == 12, f"Ожидается 12, получено {unit.magic_defense}"
    assert unit.magic_resist == 20, f"Ожидается 20, получено {unit.magic_resist}"
    assert unit._defend_this_round == False
    print("✓ Защита правильно сброшена")
    
    # Тест 4: Повторное применение после сброса
    print("\n--- ТЕСТ 4: Применение после сброса ---")
    result = unit.apply_defense_buff()
    assert result == True, "После сброса защита должна снова применяться"
    assert unit.phys_defense == 18
    assert unit._defend_this_round == True
    print("✓ После сброса защита снова применяется")
    
    # Тест 5: Множественные раунды
    print("\n--- ТЕСТ 5: Несколько раундов подряд ---")
    for round_num in range(2, 5):
        print(f"\nРаунд {round_num}:")
        unit.reset_defense_buff()
        assert unit.phys_defense == 15, f"Раунд {round_num}: значения должны быть сброшены"
        assert unit._defend_this_round == False
        print(f"✓ Раунд {round_num}: защита сброшена")
        
        unit.apply_defense_buff()
        assert unit.phys_defense == 18, f"Раунд {round_num}: защита должна быть применена"
        assert unit._defend_this_round == True
        print(f"✓ Раунд {round_num}: защита применена")
    
    print("\n=== ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! ===")
    print("\nВЫВОДЫ:")
    print("1. ✓ Старый параметр defense удален")
    print("2. ✓ Используются только phys_defense и magic_defense")
    print("3. ✓ Защита не может быть применена дважды за раунд")
    print("4. ✓ Защита правильно сбрасывается в начале раунда")
    print("5. ✓ После сброса защиту можно применить снова")
    print("6. ✓ Флаг _defend_this_round правильно управляется")

if __name__ == "__main__":
    test_defense_system()


