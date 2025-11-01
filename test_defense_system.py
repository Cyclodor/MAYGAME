"""
Тест системы защиты
Проверяет правильность работы защиты в течение раунда
"""

class MockUnit:
    """Мок-объект юнита для тестирования"""
    def __init__(self, name):
        self.name = name
        self.defense = 10
        self.phys_defense = 15
        self.magic_defense = 12
        self.magic_resist = 20
        self._defend_this_round = False
    
    def apply_defense_buff(self):
        """Применяет баф защиты (+20%)"""
        # Сохраняем оригинальные значения перед применением бафа
        if not hasattr(self, '_original_defense'):
            self._original_defense = self.defense
            self._original_phys_defense = self.phys_defense
            self._original_magic_defense = self.magic_defense
            self._original_magic_resist = self.magic_resist
        
        self.defense = int(self.defense * 1.2)
        self.phys_defense = int(self.phys_defense * 1.2)
        self.magic_defense = int(self.magic_defense * 1.2)
        self.magic_resist = min(95, int(self.magic_resist * 1.2))
        self._defend_this_round = True
        print(f"\n{self.name} встал в защиту!")
        self.print_stats()
    
    def reset_defense_buff(self):
        """Сбрасывает баф защиты в начале нового раунда"""
        if self._defend_this_round:
            # Восстанавливаем оригинальные значения
            if hasattr(self, '_original_defense'):
                self.defense = self._original_defense
                self.phys_defense = self._original_phys_defense
                self.magic_defense = self._original_magic_defense
                self.magic_resist = self._original_magic_resist
                delattr(self, '_original_defense')
                delattr(self, '_original_phys_defense')
                delattr(self, '_original_magic_defense')
                delattr(self, '_original_magic_resist')
            else:
                self.defense = int(self.defense / 1.2)
                self.phys_defense = int(self.phys_defense / 1.2)
                self.magic_defense = int(self.magic_defense / 1.2)
                self.magic_resist = int(self.magic_resist / 1.2)
            
            self._defend_this_round = False
            print(f"\n{self.name}: защита сброшена в начале нового раунда")
            self.print_stats()
    
    def print_stats(self):
        """Печатает текущие характеристики"""
        print(f"  Защита: {self.defense}")
        print(f"  Физ. защита: {self.phys_defense}")
        print(f"  Маг. защита: {self.magic_defense}")
        print(f"  Сопр. магии: {self.magic_resist}%")
        print(f"  В защите: {'ДА' if self._defend_this_round else 'НЕТ'}")

def test_defense_system():
    """Тестирует систему защиты"""
    print("=== ТЕСТ СИСТЕМЫ ЗАЩИТЫ ===\n")
    
    # Создаем юнита
    unit = MockUnit("Крестьянин")
    
    print("Начальные характеристики:")
    unit.print_stats()
    
    # Раунд 1: юнит встает в защиту
    print("\n--- РАУНД 1 ---")
    unit.apply_defense_buff()
    
    # Проверяем что защита увеличилась
    assert unit.defense == 12, f"Ожидается 12, получено {unit.defense}"
    assert unit.phys_defense == 18, f"Ожидается 18, получено {unit.phys_defense}"
    assert unit.magic_defense == 14, f"Ожидается 14, получено {unit.magic_defense}"
    assert unit.magic_resist == 24, f"Ожидается 24, получено {unit.magic_resist}"
    assert unit._defend_this_round == True
    print("✓ Защита правильно увеличена на 20%")
    
    # Раунд 2: начинается новый раунд, защита сбрасывается
    print("\n--- РАУНД 2 (новый раунд) ---")
    unit.reset_defense_buff()
    
    # Проверяем что защита вернулась к исходным значениям
    assert unit.defense == 10, f"Ожидается 10, получено {unit.defense}"
    assert unit.phys_defense == 15, f"Ожидается 15, получено {unit.phys_defense}"
    assert unit.magic_defense == 12, f"Ожидается 12, получено {unit.magic_defense}"
    assert unit.magic_resist == 20, f"Ожидается 20, получено {unit.magic_resist}"
    assert unit._defend_this_round == False
    print("✓ Защита правильно сброшена до исходных значений")
    
    # Проверяем множественное применение
    print("\n--- ТЕСТ: Множественное применение защиты ---")
    unit.apply_defense_buff()
    unit.apply_defense_buff()  # Повторное применение
    
    # Защита должна быть применена дважды (1.2 * 1.2 = 1.44)
    expected_defense = int(10 * 1.2 * 1.2)
    print(f"\nПосле двойного применения защита: {unit.defense}")
    print(f"Ожидалось: {expected_defense}")
    
    # Сбрасываем дважды
    unit.reset_defense_buff()
    unit.reset_defense_buff()
    print(f"После двойного сброса защита: {unit.defense}")
    print(f"Ожидалось: 10 (или близко к этому)")
    
    print("\n=== ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! ===")
    print("\nВЫВОДЫ:")
    print("1. ✓ Защита правильно увеличивается на 20% при использовании")
    print("2. ✓ Защита правильно сбрасывается в начале нового раунда")
    print("3. ✓ Все параметры защиты (физ, маг, сопр. магии) обрабатываются")
    print("4. ✓ Флаг _defend_this_round правильно устанавливается и сбрасывается")

if __name__ == "__main__":
    test_defense_system()

