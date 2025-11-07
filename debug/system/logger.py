"""
Централизованная система логирования для игры
Поддерживает уровни логирования, категории, ротацию файлов и фильтрацию
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pathlib import Path
import json


class LogLevel(Enum):
    """Уровни логирования"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LogCategory(Enum):
    """Категории логирования для разных систем игры"""
    # Основные системы
    GAME = "GAME"
    COMBAT = "COMBAT"
    UNITS = "UNITS"
    SPELLS = "SPELLS"
    AI = "AI"
    UI = "UI"
    ANIMATION = "ANIMATION"
    SOUND = "SOUND"
    GRAPHICS = "GRAPHICS"
    
    # Специфичные системы
    BERSERKER = "BERSERKER"
    RESURRECTION = "RESURRECTION"
    BATTLE_MANAGER = "BATTLE_MANAGER"
    TURN_SYSTEM = "TURN_SYSTEM"
    
    # Системы проверки
    VALIDATION = "VALIDATION"
    DIAGNOSTICS = "DIAGNOSTICS"
    METRICS = "METRICS"
    
    # Общие
    SYSTEM = "SYSTEM"
    ERROR = "ERROR"
    PERFORMANCE = "PERFORMANCE"


class GameLogger:
    """
    Централизованный логгер для игры
    Поддерживает множественные обработчики, фильтрацию и категории
    """
    
    def __init__(self, 
                 log_dir: str = "debug/logs",
                 max_file_size_mb: int = 10,
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 min_level: LogLevel = LogLevel.DEBUG):
        """
        Инициализация логгера
        
        Args:
            log_dir: Директория для логов
            max_file_size_mb: Максимальный размер файла лога в МБ
            backup_count: Количество резервных копий
            enable_console: Включить вывод в консоль
            enable_file: Включить запись в файл
            min_level: Минимальный уровень логирования
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_file_size = max_file_size_mb * 1024 * 1024  # В байтах
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.min_level = min_level
        
        # Создаем основной логгер
        self.logger = logging.getLogger('GameLogger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()  # Очищаем существующие обработчики
        
        # Форматтер для логов
        self.formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(category)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S.%f'
        )
        
        # Обработчик для консоли
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)
        
        # Обработчик для файла
        if self.enable_file:
            self._setup_file_handlers()
        
        # Статистика логирования
        self.stats = {
            'total_logs': 0,
            'by_level': {level.name: 0 for level in LogLevel},
            'by_category': {cat.value: 0 for cat in LogCategory},
            'errors': [],
            'warnings': [],
        }
        
        # История последних критических ошибок
        self.critical_history: List[Dict[str, Any]] = []
        self.max_critical_history = 100
        
        # Сессия
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime('%Y%m%d_%H%M%S')
        
        # Логируем инициализацию (используем прямой вызов, чтобы избежать рекурсии)
        try:
            self._log(LogLevel.INFO, LogCategory.SYSTEM, f"Логгер инициализирован. Сессия: {self.session_id}")
        except Exception as e:
            # Если не удалось залогировать, выводим в консоль
            print(f"Ошибка инициализации логгера: {e}")
    
    def _setup_file_handlers(self):
        """Настройка обработчиков файлов"""
        try:
            # Убеждаемся, что директория существует
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Основной лог
            main_log_file = self.log_dir / f"game_{self.session_id}.log"
            file_handler = logging.FileHandler(str(main_log_file), encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
            self.main_log_file = main_log_file
            
            # Лог ошибок
            error_log_file = self.log_dir / f"errors_{self.session_id}.log"
            error_handler = logging.FileHandler(str(error_log_file), encoding='utf-8')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(self.formatter)
            self.logger.addHandler(error_handler)
            self.error_log_file = error_log_file
            
            # Лог по категориям (опционально)
            self.category_logs: Dict[str, logging.FileHandler] = {}
            
            # Проверяем, что файлы созданы
            if not main_log_file.exists():
                print(f"Предупреждение: Не удалось создать файл лога: {main_log_file}")
        except Exception as e:
            print(f"Ошибка настройки обработчиков файлов: {e}")
            import traceback
            traceback.print_exc()
            # Устанавливаем None, чтобы избежать ошибок при проверке ротации
            self.main_log_file = None
            self.error_log_file = None
    
    def _check_file_rotation(self):
        """Проверяет и выполняет ротацию файлов логов"""
        if not self.enable_file:
            return
        
        for log_file in [self.main_log_file, self.error_log_file]:
            if log_file is not None and log_file.exists():
                try:
                    if log_file.stat().st_size > self.max_file_size:
                        self._rotate_file(log_file)
                except Exception:
                    pass  # Игнорируем ошибки ротации
    
    def _rotate_file(self, log_file: Path):
        """Ротирует файл лога"""
        # Удаляем старые резервные копии
        for i in range(self.backup_count - 1, 0, -1):
            old_file = Path(f"{log_file}.{i}")
            if old_file.exists():
                if i == self.backup_count - 1:
                    old_file.unlink()  # Удаляем самый старый
                else:
                    old_file.rename(Path(f"{log_file}.{i + 1}"))
        
        # Переименовываем текущий файл
        if log_file.exists():
            log_file.rename(Path(f"{log_file}.1"))
    
    def _log(self, 
             level: LogLevel,
             category: LogCategory,
             message: str,
             extra_data: Optional[Dict[str, Any]] = None,
             exception: Optional[Exception] = None):
        """
        Внутренний метод логирования
        
        Args:
            level: Уровень логирования
            category: Категория
            message: Сообщение
            extra_data: Дополнительные данные
            exception: Исключение для логирования
        """
        # Проверяем уровень
        if level.value < self.min_level.value:
            return
        
        # Формируем полное сообщение
        full_message = message
        if extra_data:
            full_message += f" | {json.dumps(extra_data, ensure_ascii=False, default=str)}"
        
        if exception:
            full_message += f"\n{''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))}"
        
        # Логируем через стандартный logging
        extra = {'category': category.value}
        log_method = {
            LogLevel.DEBUG: self.logger.debug,
            LogLevel.INFO: self.logger.info,
            LogLevel.WARNING: self.logger.warning,
            LogLevel.ERROR: self.logger.error,
            LogLevel.CRITICAL: self.logger.critical,
        }[level]
        
        log_method(full_message, extra=extra)
        
        # Обновляем статистику
        self.stats['total_logs'] += 1
        self.stats['by_level'][level.name] += 1
        self.stats['by_category'][category.value] += 1
        
        # Сохраняем ошибки и предупреждения
        if level == LogLevel.ERROR:
            self.stats['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'category': category.value,
                'message': message,
                'extra_data': extra_data,
            })
            if len(self.stats['errors']) > 1000:
                self.stats['errors'] = self.stats['errors'][-1000:]
        
        if level == LogLevel.WARNING:
            self.stats['warnings'].append({
                'timestamp': datetime.now().isoformat(),
                'category': category.value,
                'message': message,
                'extra_data': extra_data,
            })
            if len(self.stats['warnings']) > 1000:
                self.stats['warnings'] = self.stats['warnings'][-1000:]
        
        # Сохраняем критические ошибки
        if level == LogLevel.CRITICAL:
            self.critical_history.append({
                'timestamp': datetime.now().isoformat(),
                'category': category.value,
                'message': message,
                'extra_data': extra_data,
                'exception': str(exception) if exception else None,
            })
            if len(self.critical_history) > self.max_critical_history:
                self.critical_history = self.critical_history[-self.max_critical_history:]
        
        # Проверяем ротацию файлов
        if self.stats['total_logs'] % 100 == 0:  # Проверяем каждые 100 логов
            self._check_file_rotation()
    
    def debug(self, category: LogCategory, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Логирование уровня DEBUG"""
        self._log(LogLevel.DEBUG, category, message, extra_data)
    
    def info(self, category: LogCategory, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Логирование уровня INFO"""
        self._log(LogLevel.INFO, category, message, extra_data)
    
    def warning(self, category: LogCategory, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Логирование уровня WARNING"""
        self._log(LogLevel.WARNING, category, message, extra_data)
    
    def error(self, category: LogCategory, message: str, 
              extra_data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        """Логирование уровня ERROR"""
        self._log(LogLevel.ERROR, category, message, extra_data, exception)
    
    def critical(self, category: LogCategory, message: str,
                extra_data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        """Логирование уровня CRITICAL"""
        self._log(LogLevel.CRITICAL, category, message, extra_data, exception)
    
    def log_unit_action(self, unit, action: str, details: Optional[Dict[str, Any]] = None):
        """Специализированное логирование действий юнита"""
        unit_data = {
            'unit_type': getattr(unit, 'unit_type', 'Unknown'),
            'unit_id': id(unit),
            'position': (getattr(unit, 'x', None), getattr(unit, 'y', None)),
            'team': getattr(unit, 'team', None),
            'health': getattr(unit, 'health', None),
            'max_health': getattr(unit, 'max_health', None),
        }
        if details:
            unit_data.update(details)
        
        self.info(LogCategory.UNITS, f"Действие юнита: {action}", unit_data)
    
    def log_spell_cast(self, spell, caster, target=None, success: bool = True):
        """Специализированное логирование применения заклинания"""
        spell_data = {
            'spell_name': getattr(spell, 'name', getattr(spell, 'icon', 'Unknown')),
            'spell_icon': getattr(spell, 'icon', None),
            'caster_type': getattr(caster, 'unit_type', 'Unknown'),
            'caster_id': id(caster),
            'success': success,
        }
        if target:
            spell_data['target_type'] = getattr(target, 'unit_type', 'Unknown')
            spell_data['target_id'] = id(target)
            spell_data['target_position'] = (getattr(target, 'x', None), getattr(target, 'y', None))
        
        level = LogLevel.INFO if success else LogLevel.WARNING
        self._log(level, LogCategory.SPELLS, f"Применение заклинания: {spell_data['spell_name']}", spell_data)
    
    def log_combat_action(self, attacker, defender, damage: int, is_ranged: bool = False):
        """Специализированное логирование боевого действия"""
        combat_data = {
            'attacker_type': getattr(attacker, 'unit_type', 'Unknown'),
            'attacker_id': id(attacker),
            'attacker_position': (getattr(attacker, 'x', None), getattr(attacker, 'y', None)),
            'defender_type': getattr(defender, 'unit_type', 'Unknown'),
            'defender_id': id(defender),
            'defender_position': (getattr(defender, 'x', None), getattr(defender, 'y', None)),
            'damage': damage,
            'is_ranged': is_ranged,
            'defender_health_after': getattr(defender, 'health', None),
        }
        self.info(LogCategory.COMBAT, f"Боевое действие: {damage} урона", combat_data)
    
    def log_ai_decision(self, unit, decision: str, details: Optional[Dict[str, Any]] = None):
        """Специализированное логирование решений AI"""
        ai_data = {
            'unit_type': getattr(unit, 'unit_type', 'Unknown'),
            'unit_id': id(unit),
            'decision': decision,
        }
        if details:
            ai_data.update(details)
        self.debug(LogCategory.AI, f"Решение AI: {decision}", ai_data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику логирования"""
        session_duration = (datetime.now() - self.session_start).total_seconds()
        return {
            'session_id': self.session_id,
            'session_duration_seconds': session_duration,
            'total_logs': self.stats['total_logs'],
            'by_level': self.stats['by_level'],
            'by_category': self.stats['by_category'],
            'error_count': len(self.stats['errors']),
            'warning_count': len(self.stats['warnings']),
            'critical_count': len(self.critical_history),
        }
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """Получить последние ошибки"""
        return self.stats['errors'][-count:]
    
    def get_recent_warnings(self, count: int = 10) -> List[Dict[str, Any]]:
        """Получить последние предупреждения"""
        return self.stats['warnings'][-count:]
    
    def get_critical_history(self) -> List[Dict[str, Any]]:
        """Получить историю критических ошибок"""
        return self.critical_history.copy()
    
    def save_stats_report(self, filepath: Optional[str] = None):
        """Сохранить отчет о статистике"""
        if filepath is None:
            filepath = self.log_dir / f"stats_{self.session_id}.json"
        else:
            filepath = Path(filepath)
        
        report = {
            'session_id': self.session_id,
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'recent_errors': self.get_recent_errors(50),
            'recent_warnings': self.get_recent_warnings(50),
            'critical_history': self.get_critical_history(),
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        self.info(LogCategory.SYSTEM, f"Отчет о статистике сохранен: {filepath}")


# Глобальный экземпляр логгера
_logger_instance: Optional[GameLogger] = None


def get_logger() -> GameLogger:
    """Получить глобальный экземпляр логгера"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = GameLogger()
    return _logger_instance


def initialize_logger(**kwargs) -> GameLogger:
    """Инициализировать логгер с параметрами"""
    global _logger_instance
    _logger_instance = GameLogger(**kwargs)
    return _logger_instance

