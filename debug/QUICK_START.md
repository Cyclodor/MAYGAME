# Быстрый старт

## Отладка берсерка

1. **Применить патчи** (если еще не применены):
   ```bash
   python debug/berserker/patch_berserker_debug.py
   ```

2. **Запустить игру**:
   ```bash
   python main.py
   ```

3. **Воспроизвести проблему** - примените руну берсерка на юните

4. **Сгенерировать отчет**:
   ```bash
   python debug/berserker/generate_berserker_report.py
   ```

5. **Проверить результаты**:
   - Лог: `debug/berserker/berserker_debug.log`
   - Отчет: `debug/berserker/berserker_debug_report.txt`

## Отладка воскрешения

Лог автоматически создается в `debug/resurrection/resurrection_debug.log` при использовании заклинания воскрешения.

## Отладка анимаций

Лог автоматически создается в `debug/animation/animation_log.txt` при включенном логировании анимаций.

## Скрипты проверки

Все скрипты проверки находятся в `debug/scripts/`:
- `check_indentation.py` - проверка отступов
- `check_editor_params.py` - проверка параметров редактора
- `check_spell_animations.py` - проверка анимаций заклинаний
- `test_defense_system.py` - тест системы защиты
- `test_defense_fixes.py` - тест исправлений защиты

## Документация

Вся документация по исправлениям находится в `debug/docs/`.


