# Система логирования и отладки

Комплексная система для тотальной проверки ошибок, действий и контроля правильности работы игры.

## Компоненты системы

### 1. Централизованный логгер (`logger.py`)

Унифицированная система логирования с поддержкой:
- **Уровней логирования**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Категорий**: GAME, COMBAT, UNITS, SPELLS, AI, UI, ANIMATION, SOUND, GRAPHICS и др.
- **Ротации файлов**: автоматическое управление размером логов
- **Фильтрации**: по уровню и категории
- **Статистики**: подсчет логов по уровням и категориям

**Использование:**
```python
from debug.system import get_logger, LogCategory, LogLevel

logger = get_logger()
logger.info(LogCategory.COMBAT, "Атака выполнена", {'damage': 10})
logger.error(LogCategory.SPELLS, "Ошибка применения заклинания", exception=e)
```

### 2. Система метрик (`metrics.py`)

Отслеживание производительности и статистики:
- **FPS**: текущий и средний FPS
- **Память**: использование RAM
- **Время выполнения функций**: профилирование кода
- **События**: подсчет различных событий игры
- **Игровые метрики**: раунды, ходы, заклинания, атаки

**Использование:**
```python
from debug.system import get_metrics

metrics = get_metrics()
metrics.start_timer("combat_calculation")
# ... код ...
elapsed = metrics.stop_timer("combat_calculation")

fps = metrics.get_fps()
memory = metrics.get_memory_usage()
```

### 3. Система валидации (`validator.py`)

Проверка корректности состояния игры:
- **Валидация юнитов**: позиции, здоровье, команды, состояния
- **Валидация состояния игры**: очередь ходов, выбранные юниты
- **Валидация заклинаний**: проверка кастера и целей
- **Кастомные правила**: регистрация собственных правил валидации

**Использование:**
```python
from debug.system import get_validator

validator = get_validator()
issues = validator.validate_game_state(game)
for issue in issues:
    print(f"{issue.severity}: {issue.message}")
```

### 4. Система диагностики (`diagnostics.py`)

Автоматическое обнаружение проблем:
- **Проверка производительности**: FPS, память
- **Проверка состояния игры**: валидность состояний
- **Проверка целостности данных**: юниты, очередь ходов
- **Кастомные проверки**: регистрация собственных проверок

**Использование:**
```python
from debug.system import get_diagnostics

diagnostics = get_diagnostics()
results = diagnostics.run_all_checks(game)
summary = diagnostics.get_summary()
```

### 5. Конфигурация (`config.py`)

Централизованная конфигурация всех систем:
- Настройки логирования
- Включение/выключение категорий
- Интервалы проверок
- Пороги предупреждений

**Использование:**
```python
from debug.system import load_config, save_config, LoggingConfig

config = load_config()  # Загрузить из файла
config.min_level = "INFO"
config.enable_metrics = True
save_config(config)  # Сохранить
```

### 6. Интеграция (`integration.py`)

Главный класс, объединяющий все системы:
- Автоматическое обновление всех компонентов
- Периодические проверки валидации и диагностики
- Единая точка доступа ко всем системам

**Использование:**
```python
from debug.system import initialize_debug_system, get_debug_system

# Инициализация
debug_system = initialize_debug_system()

# В игровом цикле
debug_system.update(game, delta_time)

# Получение сводки
summary = debug_system.get_summary()
```

## Быстрый старт

### 1. Базовая инициализация

```python
from debug.system import initialize_debug_system

# Инициализация системы отладки
debug_system = initialize_debug_system()
```

### 2. Интеграция в игровой цикл

```python
# В главном цикле игры
clock = pygame.time.Clock()
while running:
    delta_time = clock.tick(60) / 1000.0  # В секундах
    
    # Обновление системы отладки
    debug_system.update(game, delta_time)
    
    # ... остальной код игры ...
```

### 3. Использование в коде

```python
from debug.system import get_logger, LogCategory

logger = get_logger()

# Логирование действий юнита
logger.log_unit_action(unit, "move", {'from': (x1, y1), 'to': (x2, y2)})

# Логирование заклинания
logger.log_spell_cast(spell, caster, target, success=True)

# Логирование боевого действия
logger.log_combat_action(attacker, defender, damage=15, is_ranged=False)

# Логирование решения AI
logger.log_ai_decision(unit, "attack", {'target': target.unit_type})
```

## Конфигурация

Создайте файл `debug/system/config.json`:

```json
{
  "log_dir": "debug/logs",
  "max_file_size_mb": 10,
  "backup_count": 5,
  "enable_console": true,
  "enable_file": true,
  "min_level": "DEBUG",
  "categories": {
    "GAME": true,
    "COMBAT": true,
    "UNITS": true,
    "SPELLS": true,
    "AI": true,
    "UI": true,
    "ANIMATION": true,
    "SOUND": false,
    "GRAPHICS": false
  },
  "enable_metrics": true,
  "metrics_update_interval": 1.0,
  "enable_validation": true,
  "validation_interval": 5.0,
  "auto_validate": true,
  "enable_diagnostics": true,
  "diagnostics_interval": 10.0,
  "auto_diagnostics": true,
  "performance_warning_fps": 30.0,
  "performance_warning_memory_percent": 90.0
}
```

## Интеграция с существующими системами

Система автоматически интегрируется с существующими системами отладки:
- `debug/berserker/berserker_debug.py` - логирование берсерка
- `debug/animation/animation_logger.py` - логирование анимаций
- `debug/resurrection/resurrection_debug.py` - логирование воскрешения

Все логи объединяются в единую систему.

## Отчеты

Система автоматически генерирует отчеты:
- `debug/logs/game_YYYYMMDD_HHMMSS.log` - основной лог
- `debug/logs/errors_YYYYMMDD_HHMMSS.log` - лог ошибок
- `debug/logs/stats_YYYYMMDD_HHMMSS.json` - статистика логирования
- `debug/logs/metrics_YYYYMMDD_HHMMSS.json` - метрики производительности

## Рекомендации

1. **Включите логирование** для всех критических операций
2. **Используйте категории** для удобной фильтрации
3. **Настройте уровни** в зависимости от окружения (DEBUG для разработки, INFO для продакшена)
4. **Проверяйте метрики** регулярно для выявления проблем производительности
5. **Используйте валидацию** для обнаружения проблем с данными
6. **Запускайте диагностику** периодически для автоматического обнаружения проблем

## Примеры использования

### Логирование боевой системы

```python
from debug.system import get_logger, LogCategory

logger = get_logger()

def attack(attacker, defender):
    damage = calculate_damage(attacker, defender)
    defender.health -= damage
    
    logger.log_combat_action(attacker, defender, damage, is_ranged=False)
    
    if defender.health <= 0:
        logger.info(LogCategory.COMBAT, f"{defender.unit_type} убит", {
            'killer': attacker.unit_type,
            'final_damage': damage
        })
```

### Профилирование производительности

```python
from debug.system import get_metrics

metrics = get_metrics()

def expensive_calculation():
    metrics.start_timer("expensive_calculation")
    # ... тяжелые вычисления ...
    elapsed = metrics.stop_timer("expensive_calculation")
    
    if elapsed > 0.1:  # Больше 100мс
        logger.warning(LogCategory.PERFORMANCE, 
                      f"Медленное вычисление: {elapsed:.3f}с")
```

### Валидация после изменений

```python
from debug.system import get_validator

validator = get_validator()

def apply_spell(spell, caster, target):
    # Применяем заклинание
    spell.apply(caster, target)
    
    # Проверяем результат
    issues = validator.validate_spell(spell, caster, target)
    if issues:
        for issue in issues:
            logger.error(LogCategory.VALIDATION, issue.message, issue.details)
```

## Расширение системы

### Добавление кастомного правила валидации

```python
from debug.system import get_validator, ValidationIssue, ValidationSeverity

validator = get_validator()

def check_custom_rule(game):
    # Ваша проверка
    if some_condition:
        return ValidationIssue(
            ValidationSeverity.ERROR,
            'custom_category',
            'Описание проблемы',
            {'extra': 'data'}
        )
    return None

validator.register_rule('custom', check_custom_rule)
```

### Добавление кастомной проверки диагностики

```python
from debug.system import get_diagnostics, DiagnosticResult

diagnostics = get_diagnostics()

def check_custom_condition(game):
    # Ваша проверка
    return some_condition  # True = OK, False = проблема

diagnostics.register_check(
    'custom_check',
    'Описание проверки',
    check_custom_condition,
    DiagnosticResult.WARNING
)
```

## Производительность

Система оптимизирована для минимального влияния на производительность:
- Логирование выполняется асинхронно где возможно
- Проверки валидации и диагностики выполняются с интервалами
- Метрики собираются эффективно
- Ротация файлов происходит автоматически

## Поддержка

При возникновении проблем:
1. Проверьте логи в `debug/logs/`
2. Запустите диагностику: `diagnostics.run_all_checks(game)`
3. Проверьте метрики производительности
4. Изучите отчеты валидации


