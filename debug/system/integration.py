"""
Интеграция с существующими системами отладки
Объединяет все системы логирования в единую точку доступа
"""

from typing import Optional
from .logger import get_logger, initialize_logger, LogCategory, LogLevel
from .metrics import get_metrics, initialize_metrics
from .validator import get_validator, initialize_validator
from .diagnostics import get_diagnostics, initialize_diagnostics
from .config import load_config, get_config, LoggingConfig


class DebugSystem:
    """Главный класс системы отладки, объединяющий все компоненты"""
    
    def __init__(self, config: Optional[LoggingConfig] = None):
        """
        Инициализация системы отладки
        
        Args:
            config: Конфигурация (опционально, загружается автоматически)
        """
        if config is None:
            config = get_config()
        
        self.config = config
        
        # Инициализируем компоненты
        log_level = LogLevel[config.min_level] if hasattr(LogLevel, config.min_level) else LogLevel.DEBUG
        
        self.logger = initialize_logger(
            log_dir=config.log_dir,
            max_file_size_mb=config.max_file_size_mb,
            backup_count=config.backup_count,
            enable_console=config.enable_console,
            enable_file=config.enable_file,
            min_level=log_level
        )
        
        if config.enable_metrics:
            self.metrics = initialize_metrics()
        else:
            self.metrics = None
        
        if config.enable_validation:
            self.validator = initialize_validator()
        else:
            self.validator = None
        
        if config.enable_diagnostics:
            self.diagnostics = initialize_diagnostics()
        else:
            self.diagnostics = None
        
        # Таймеры для периодических проверок
        self._last_validation = 0.0
        self._last_diagnostics = 0.0
        self._last_metrics_update = 0.0
        
        self.logger.info(LogCategory.SYSTEM, "Система отладки полностью инициализирована")
    
    def update(self, game, delta_time: float):
        """
        Обновление системы отладки (вызывать каждый кадр)
        
        Args:
            game: Объект игры
            delta_time: Время с последнего кадра
        """
        import time
        current_time = time.time()
        
        # Обновление метрик
        if self.metrics:
            self.metrics.update_frame(delta_time)
            
            # Проверка производительности
            if current_time - self._last_metrics_update >= self.config.metrics_update_interval:
                self.metrics.log_performance_issue(self.config.performance_warning_fps)
                self._last_metrics_update = current_time
        
        # Автоматическая валидация
        if self.validator and self.config.auto_validate:
            if current_time - self._last_validation >= self.config.validation_interval:
                try:
                    issues = self.validator.validate_all(game)
                    if issues:
                        error_count = len([i for i in issues if i.severity.value == 'ERROR'])
                        critical_count = len([i for i in issues if i.severity.value == 'CRITICAL'])
                        
                        if critical_count > 0:
                            self.logger.critical(
                                LogCategory.VALIDATION,
                                f"Обнаружено {critical_count} критических проблем валидации"
                            )
                        elif error_count > 0:
                            self.logger.error(
                                LogCategory.VALIDATION,
                                f"Обнаружено {error_count} ошибок валидации"
                            )
                except Exception as e:
                    self.logger.error(
                        LogCategory.VALIDATION,
                        f"Ошибка валидации: {e}",
                        exception=e
                    )
                
                self._last_validation = current_time
        
        # Автоматическая диагностика
        if self.diagnostics and self.config.auto_diagnostics:
            if current_time - self._last_diagnostics >= self.config.diagnostics_interval:
                try:
                    results = self.diagnostics.run_all_checks(game)
                    failed = self.diagnostics.get_failed_checks()
                    if failed:
                        self.logger.warning(
                            LogCategory.DIAGNOSTICS,
                            f"Неудачные проверки диагностики: {', '.join(failed)}"
                        )
                except Exception as e:
                    self.logger.error(
                        LogCategory.DIAGNOSTICS,
                        f"Ошибка диагностики: {e}",
                        exception=e
                    )
                
                self._last_diagnostics = current_time
    
    def get_summary(self) -> dict:
        """Получить сводку всех систем"""
        summary = {
            'logger': self.logger.get_stats() if self.logger else None,
            'metrics': self.metrics.get_performance_summary() if self.metrics else None,
            'validator': self.validator.get_issues_summary() if self.validator else None,
            'diagnostics': self.diagnostics.get_summary() if self.diagnostics else None,
        }
        return summary
    
    def save_all_reports(self, directory: Optional[str] = None):
        """
        Сохранить все отчеты
        
        Args:
            directory: Директория для сохранения (опционально)
        """
        if directory:
            from pathlib import Path
            directory = Path(directory)
            directory.mkdir(parents=True, exist_ok=True)
        
        if self.logger:
            self.logger.save_stats_report(
                str(directory / "logger_stats.json") if directory else None
            )
        
        if self.metrics:
            self.metrics.save_metrics_report(
                str(directory / "metrics_report.json") if directory else None
            )


# Глобальный экземпляр системы отладки
_debug_system_instance: Optional[DebugSystem] = None


def initialize_debug_system(config: Optional[LoggingConfig] = None) -> DebugSystem:
    """
    Инициализировать систему отладки
    
    Args:
        config: Конфигурация (опционально)
        
    Returns:
        Экземпляр системы отладки
    """
    global _debug_system_instance
    _debug_system_instance = DebugSystem(config)
    return _debug_system_instance


def get_debug_system() -> Optional[DebugSystem]:
    """
    Получить глобальный экземпляр системы отладки
    
    Returns:
        Экземпляр системы отладки или None если не инициализирован
    """
    return _debug_system_instance


# Удобные функции для быстрого доступа
def log(level: LogLevel, category: LogCategory, message: str, **kwargs):
    """Быстрое логирование"""
    logger = get_logger()
    if level == LogLevel.DEBUG:
        logger.debug(category, message, kwargs if kwargs else None)
    elif level == LogLevel.INFO:
        logger.info(category, message, kwargs if kwargs else None)
    elif level == LogLevel.WARNING:
        logger.warning(category, message, kwargs if kwargs else None)
    elif level == LogLevel.ERROR:
        logger.error(category, message, kwargs if kwargs else None, exception=kwargs.get('exception'))
    elif level == LogLevel.CRITICAL:
        logger.critical(category, message, kwargs if kwargs else None, exception=kwargs.get('exception'))


def validate_game(game):
    """Быстрая валидация игры"""
    validator = get_validator()
    if validator:
        return validator.validate_all(game)
    return []


def run_diagnostics(game):
    """Быстрый запуск диагностики"""
    diagnostics = get_diagnostics()
    if diagnostics:
        return diagnostics.run_all_checks(game)
    return {}


