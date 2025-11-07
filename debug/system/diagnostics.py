"""
Система автоматической диагностики
Автоматически обнаруживает и анализирует проблемы в игре
"""

import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from .logger import get_logger, LogCategory, LogLevel
from .validator import get_validator, ValidationIssue, ValidationSeverity
from .metrics import get_metrics


class DiagnosticResult(Enum):
    """Результат диагностики"""
    OK = "OK"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DiagnosticCheck:
    """Проверка диагностики"""
    
    def __init__(self,
                 name: str,
                 description: str,
                 check_func,
                 severity: DiagnosticResult = DiagnosticResult.WARNING):
        self.name = name
        self.description = description
        self.check_func = check_func
        self.severity = severity
        self.last_run = None
        self.last_result = None
        self.history: List[Dict[str, Any]] = []
    
    def run(self, game) -> DiagnosticResult:
        """Выполнить проверку"""
        try:
            result = self.check_func(game)
            if isinstance(result, bool):
                result = DiagnosticResult.OK if result else self.severity
            elif not isinstance(result, DiagnosticResult):
                result = DiagnosticResult.OK
            
            self.last_run = datetime.now()
            self.last_result = result
            
            self.history.append({
                'timestamp': self.last_run.isoformat(),
                'result': result.value,
            })
            if len(self.history) > 100:
                self.history = self.history[-100:]
            
            return result
        except Exception as e:
            self.last_run = datetime.now()
            self.last_result = DiagnosticResult.ERROR
            
            get_logger().error(
                LogCategory.DIAGNOSTICS,
                f"Ошибка выполнения проверки {self.name}: {e}",
                exception=e
            )
            
            return DiagnosticResult.ERROR


class DiagnosticsEngine:
    """Движок автоматической диагностики"""
    
    def __init__(self):
        """Инициализация движка диагностики"""
        self.logger = get_logger()
        self.validator = get_validator()
        self.metrics = get_metrics()
        
        self.checks: List[DiagnosticCheck] = []
        self.results: Dict[str, DiagnosticResult] = {}
        
        # Регистрируем стандартные проверки
        self._register_standard_checks()
        
        self.logger.info(LogCategory.DIAGNOSTICS, "Движок диагностики инициализирован")
    
    def _register_standard_checks(self):
        """Регистрация стандартных проверок"""
        
        # Проверка производительности
        self.register_check(
            "performance_fps",
            "Проверка FPS",
            self._check_fps,
            DiagnosticResult.WARNING
        )
        
        # Проверка памяти
        self.register_check(
            "performance_memory",
            "Проверка использования памяти",
            self._check_memory,
            DiagnosticResult.WARNING
        )
        
        # Проверка состояния игры
        self.register_check(
            "game_state",
            "Проверка состояния игры",
            self._check_game_state,
            DiagnosticResult.ERROR
        )
        
        # Проверка юнитов
        self.register_check(
            "units_integrity",
            "Проверка целостности юнитов",
            self._check_units_integrity,
            DiagnosticResult.ERROR
        )
        
        # Проверка очереди ходов
        self.register_check(
            "turn_queue",
            "Проверка очереди ходов",
            self._check_turn_queue,
            DiagnosticResult.ERROR
        )
    
    def register_check(self,
                      name: str,
                      description: str,
                      check_func,
                      severity: DiagnosticResult = DiagnosticResult.WARNING):
        """
        Регистрация проверки
        
        Args:
            name: Имя проверки
            description: Описание проверки
            check_func: Функция проверки (должна принимать game и возвращать bool или DiagnosticResult)
            severity: Уровень серьезности при неудаче
        """
        check = DiagnosticCheck(name, description, check_func, severity)
        self.checks.append(check)
        self.logger.debug(LogCategory.DIAGNOSTICS, f"Зарегистрирована проверка: {name}")
    
    def _check_fps(self, game) -> bool:
        """Проверка FPS"""
        avg_fps = self.metrics.get_avg_fps(60)
        return avg_fps >= 80.0  # Минимум 80 FPS
    
    def _check_memory(self, game) -> bool:
        """Проверка использования памяти"""
        memory = self.metrics.get_memory_usage()
        return memory['memory_percent'] < 90.0  # Меньше 90% памяти
    
    def _check_game_state(self, game) -> bool:
        """Проверка состояния игры"""
        if not hasattr(game, 'state'):
            return False
        
        valid_states = ['menu', 'game', 'creative', 'spell_editor', 'unit_editor']
        return game.state in valid_states
    
    def _check_units_integrity(self, game) -> bool:
        """Проверка целостности юнитов"""
        if not hasattr(game, 'units'):
            return False
        
        # Проверяем, что все юниты валидны
        issues = self.validator.validate_game_state(game)
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        return len(critical_issues) == 0
    
    def _check_turn_queue(self, game) -> bool:
        """Проверка очереди ходов"""
        if not hasattr(game, 'turn_queue'):
            return True  # Очередь может отсутствовать в некоторых состояниях
        
        # Проверяем, что очередь не пуста в игровом состоянии
        if hasattr(game, 'state') and game.state == 'game':
            if not game.turn_queue:
                return False
        
        return True
    
    def run_all_checks(self, game) -> Dict[str, DiagnosticResult]:
        """
        Выполнить все проверки
        
        Args:
            game: Объект игры
            
        Returns:
            Словарь результатов проверок
        """
        results = {}
        
        for check in self.checks:
            result = check.run(game)
            results[check.name] = result
            
            # Логируем результаты
            if result != DiagnosticResult.OK:
                log_level = {
                    DiagnosticResult.WARNING: LogLevel.WARNING,
                    DiagnosticResult.ERROR: LogLevel.ERROR,
                    DiagnosticResult.CRITICAL: LogLevel.CRITICAL,
                }.get(result, LogLevel.WARNING)
                
                if result == DiagnosticResult.WARNING:
                    self.logger.warning(LogCategory.DIAGNOSTICS, 
                                       f"Диагностика: {check.name} - {result.value}",
                                       {'description': check.description})
                elif result == DiagnosticResult.ERROR:
                    self.logger.error(LogCategory.DIAGNOSTICS, 
                                     f"Диагностика: {check.name} - {result.value}",
                                     {'description': check.description})
                elif result == DiagnosticResult.CRITICAL:
                    self.logger.critical(LogCategory.DIAGNOSTICS, 
                                        f"Диагностика: {check.name} - {result.value}",
                                        {'description': check.description})
        
        self.results = results
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Получить сводку диагностики"""
        summary = {
            'total_checks': len(self.checks),
            'results': {},
            'status': DiagnosticResult.OK.value,
        }
        
        for check in self.checks:
            summary['results'][check.name] = {
                'result': check.last_result.value if check.last_result else 'NOT_RUN',
                'last_run': check.last_run.isoformat() if check.last_run else None,
                'description': check.description,
            }
            
            # Определяем общий статус
            if check.last_result:
                if check.last_result == DiagnosticResult.CRITICAL:
                    summary['status'] = DiagnosticResult.CRITICAL.value
                elif check.last_result == DiagnosticResult.ERROR and summary['status'] != DiagnosticResult.CRITICAL.value:
                    summary['status'] = DiagnosticResult.ERROR.value
                elif check.last_result == DiagnosticResult.WARNING and summary['status'] == DiagnosticResult.OK.value:
                    summary['status'] = DiagnosticResult.WARNING.value
        
        return summary
    
    def get_failed_checks(self) -> List[str]:
        """Получить список неудачных проверок"""
        failed = []
        for check in self.checks:
            if check.last_result and check.last_result != DiagnosticResult.OK:
                failed.append(check.name)
        return failed
    
    def auto_fix_issues(self, game) -> Dict[str, bool]:
        """
        Попытка автоматического исправления проблем
        
        Args:
            game: Объект игры
            
        Returns:
            Словарь результатов исправлений
        """
        fixes = {}
        
        # Исправление проблем с валидацией
        issues = self.validator.get_issues(severity=ValidationSeverity.ERROR)
        for issue in issues:
            if issue.category == 'unit_position':
                # Попытка исправить некорректные координаты
                # (требует доступа к юниту, что сложно без дополнительной информации)
                pass
        
        return fixes


# Глобальный экземпляр движка диагностики
_diagnostics_instance: Optional[DiagnosticsEngine] = None


def get_diagnostics() -> DiagnosticsEngine:
    """Получить глобальный экземпляр движка диагностики"""
    global _diagnostics_instance
    if _diagnostics_instance is None:
        _diagnostics_instance = DiagnosticsEngine()
    return _diagnostics_instance


def initialize_diagnostics() -> DiagnosticsEngine:
    """Инициализировать движок диагностики"""
    global _diagnostics_instance
    _diagnostics_instance = DiagnosticsEngine()
    return _diagnostics_instance

