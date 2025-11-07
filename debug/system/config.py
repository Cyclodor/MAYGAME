"""
Конфигурация системы логирования и отладки
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from .logger import LogLevel


@dataclass
class LoggingConfig:
    """Конфигурация логирования"""
    # Основные настройки
    log_dir: str = "debug/logs"
    max_file_size_mb: int = 10
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    min_level: str = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Категории логирования (включены/выключены)
    categories: Dict[str, bool] = None
    
    # Настройки метрик
    enable_metrics: bool = True
    metrics_update_interval: float = 1.0  # секунды
    
    # Настройки валидации
    enable_validation: bool = True
    validation_interval: float = 5.0  # секунды
    auto_validate: bool = True
    
    # Настройки диагностики
    enable_diagnostics: bool = True
    diagnostics_interval: float = 10.0  # секунды
    auto_diagnostics: bool = True
    
    # Настройки производительности
    performance_warning_fps: float = 80.0  # Увеличен порог до 80 FPS
    performance_warning_memory_percent: float = 90.0
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = {
                'GAME': True,
                'COMBAT': True,
                'UNITS': True,
                'SPELLS': True,
                'AI': True,
                'UI': True,
                'ANIMATION': True,
                'SOUND': True,
                'GRAPHICS': True,
                'BERSERKER': True,
                'RESURRECTION': True,
                'BATTLE_MANAGER': True,
                'TURN_SYSTEM': True,
                'VALIDATION': True,
                'DIAGNOSTICS': True,
                'METRICS': True,
                'SYSTEM': True,
                'ERROR': True,
                'PERFORMANCE': True,
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoggingConfig':
        """Создать из словаря"""
        return cls(**data)
    
    def save(self, filepath: str):
        """Сохранить конфигурацию в файл"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'LoggingConfig':
        """Загрузить конфигурацию из файла"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            return cls()  # Возвращаем конфигурацию по умолчанию
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)


# Путь к файлу конфигурации по умолчанию
DEFAULT_CONFIG_PATH = "debug/system/config.json"

# Глобальная конфигурация
_global_config: Optional[LoggingConfig] = None


def load_config(filepath: Optional[str] = None) -> LoggingConfig:
    """
    Загрузить конфигурацию
    
    Args:
        filepath: Путь к файлу конфигурации (опционально)
        
    Returns:
        Конфигурация логирования
    """
    global _global_config
    
    if filepath is None:
        filepath = DEFAULT_CONFIG_PATH
    
    _global_config = LoggingConfig.load(filepath)
    return _global_config


def save_config(config: LoggingConfig, filepath: Optional[str] = None):
    """
    Сохранить конфигурацию
    
    Args:
        config: Конфигурация логирования
        filepath: Путь к файлу конфигурации (опционально)
    """
    global _global_config
    
    if filepath is None:
        filepath = DEFAULT_CONFIG_PATH
    
    config.save(filepath)
    _global_config = config


def get_config() -> LoggingConfig:
    """
    Получить текущую конфигурацию
    
    Returns:
        Конфигурация логирования
    """
    global _global_config
    
    if _global_config is None:
        _global_config = load_config()
    
    return _global_config


