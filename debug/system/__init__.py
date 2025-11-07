"""
Централизованная система логирования и отладки для игры
"""

from .logger import GameLogger, get_logger, LogCategory, LogLevel
from .metrics import MetricsCollector, get_metrics
from .validator import GameValidator, get_validator
from .diagnostics import DiagnosticsEngine, get_diagnostics
from .config import LoggingConfig, load_config, save_config
from .integration import DebugSystem, initialize_debug_system, get_debug_system

__all__ = [
    'GameLogger',
    'get_logger',
    'LogCategory',
    'LogLevel',
    'MetricsCollector',
    'get_metrics',
    'GameValidator',
    'get_validator',
    'DiagnosticsEngine',
    'get_diagnostics',
    'LoggingConfig',
    'load_config',
    'save_config',
    'DebugSystem',
    'initialize_debug_system',
    'get_debug_system',
]

