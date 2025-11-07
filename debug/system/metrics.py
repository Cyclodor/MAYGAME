"""
Система сбора метрик и производительности
Отслеживает производительность, использование памяти, FPS и другие метрики
"""

import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict, deque
from pathlib import Path
import json

# Опциональный импорт psutil - проверяем при каждом использовании
# Не устанавливаем глобальную переменную, чтобы всегда проверять динамически
from .logger import get_logger, LogCategory, LogLevel

def _check_psutil():
    """Проверяет доступность psutil"""
    try:
        import psutil
        return True, psutil
    except ImportError:
        return False, None


class MetricsCollector:
    """Сборщик метрик производительности и статистики"""
    
    def __init__(self, max_history: int = 1000):
        """
        Инициализация сборщика метрик
        
        Args:
            max_history: Максимальное количество записей в истории
        """
        self.max_history = max_history
        self.logger = get_logger()
        
        # Метрики производительности
        self.frame_times: deque = deque(maxlen=max_history)
        self.fps_history: deque = deque(maxlen=max_history)
        self.current_fps = 0.0
        
        # Метрики памяти
        self.memory_history: deque = deque(maxlen=max_history)
        # Динамическая проверка доступности psutil
        self.psutil_available, psutil_module = _check_psutil()
        self.process = None
        if self.psutil_available and psutil_module:
            try:
                self.process = psutil_module.Process(os.getpid())
            except Exception as e:
                self.logger.warning(LogCategory.METRICS, f"Не удалось создать процесс psutil: {e}")
                self.psutil_available = False
                self.process = None
        
        # Метрики функций (таймеры)
        self.function_timings: Dict[str, List[float]] = defaultdict(list)
        self.active_timers: Dict[str, float] = {}
        
        # Метрики событий
        self.event_counts: Dict[str, int] = defaultdict(int)
        self.event_history: List[Dict[str, Any]] = []
        
        # Метрики игры
        self.game_metrics: Dict[str, Any] = {
            'rounds_played': 0,
            'turns_played': 0,
            'spells_cast': 0,
            'attacks_made': 0,
            'units_killed': 0,
            'units_created': 0,
        }
        
        # Статистика по категориям
        self.category_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'avg_time': 0.0,
        })
        
        # Сессия
        self.session_start = datetime.now()
        self.last_update = time.time()
        
        self.logger.info(LogCategory.METRICS, "Система метрик инициализирована")
    
    def update_frame(self, frame_time: float):
        """
        Обновление метрик кадра
        
        Args:
            frame_time: Время обработки кадра в секундах
        """
        self.frame_times.append(frame_time)
        
        if frame_time > 0:
            fps = 1.0 / frame_time
            self.fps_history.append(fps)
            self.current_fps = fps
        
        # Обновляем метрики памяти периодически
        current_time = time.time()
        if current_time - self.last_update >= 1.0:  # Раз в секунду
            self._update_memory_metrics()
            self.last_update = current_time
    
    def _update_memory_metrics(self):
        """Обновление метрик памяти"""
        if not self.psutil_available or self.process is None:
            return
        
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # В мегабайтах
            
            self.memory_history.append({
                'timestamp': datetime.now().isoformat(),
                'memory_mb': memory_mb,
                'memory_percent': self.process.memory_percent(),
            })
        except Exception as e:
            self.logger.warning(LogCategory.METRICS, f"Ошибка обновления метрик памяти: {e}")
    
    def start_timer(self, name: str):
        """
        Запуск таймера для измерения времени выполнения
        
        Args:
            name: Имя таймера
        """
        self.active_timers[name] = time.time()
    
    def stop_timer(self, name: str) -> Optional[float]:
        """
        Остановка таймера и возврат времени выполнения
        
        Args:
            name: Имя таймера
            
        Returns:
            Время выполнения в секундах или None если таймер не найден
        """
        if name not in self.active_timers:
            self.logger.warning(LogCategory.METRICS, f"Таймер {name} не найден")
            return None
        
        elapsed = time.time() - self.active_timers[name]
        del self.active_timers[name]
        
        # Сохраняем время выполнения
        self.function_timings[name].append(elapsed)
        if len(self.function_timings[name]) > self.max_history:
            self.function_timings[name] = self.function_timings[name][-self.max_history:]
        
        return elapsed
    
    def time_function(self, func: Callable, name: Optional[str] = None):
        """
        Декоратор для измерения времени выполнения функции
        
        Args:
            func: Функция для измерения
            name: Имя для метрики (по умолчанию имя функции)
        """
        if name is None:
            name = func.__name__
        
        def wrapper(*args, **kwargs):
            self.start_timer(name)
            try:
                result = func(*args, **kwargs)
                elapsed = self.stop_timer(name)
                return result
            except Exception as e:
                self.stop_timer(name)
                raise e
        
        return wrapper
    
    def record_event(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        """
        Запись события
        
        Args:
            event_type: Тип события
            data: Дополнительные данные события
        """
        self.event_counts[event_type] += 1
        
        event_record = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data or {},
        }
        
        self.event_history.append(event_record)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
    
    def increment_game_metric(self, metric_name: str, value: int = 1):
        """
        Увеличение игровой метрики
        
        Args:
            metric_name: Имя метрики
            value: Значение для увеличения
        """
        if metric_name in self.game_metrics:
            self.game_metrics[metric_name] += value
        else:
            self.game_metrics[metric_name] = value
    
    def get_fps(self) -> float:
        """Получить текущий FPS"""
        return self.current_fps
    
    def get_avg_fps(self, frames: int = 60) -> float:
        """
        Получить средний FPS за последние N кадров
        
        Args:
            frames: Количество кадров для усреднения
        """
        if not self.fps_history:
            return 0.0
        
        recent_fps = list(self.fps_history)[-frames:]
        return sum(recent_fps) / len(recent_fps) if recent_fps else 0.0
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Получить текущее использование памяти"""
        if not self.psutil_available or self.process is None:
            return {'memory_mb': 0.0, 'memory_percent': 0.0}
        
        try:
            memory_info = self.process.memory_info()
            return {
                'memory_mb': memory_info.rss / 1024 / 1024,
                'memory_percent': self.process.memory_percent(),
            }
        except Exception:
            return {'memory_mb': 0.0, 'memory_percent': 0.0}
    
    def get_function_stats(self, function_name: str) -> Optional[Dict[str, float]]:
        """
        Получить статистику по функции
        
        Args:
            function_name: Имя функции
            
        Returns:
            Словарь со статистикой или None
        """
        if function_name not in self.function_timings or not self.function_timings[function_name]:
            return None
        
        times = self.function_timings[function_name]
        return {
            'count': len(times),
            'total': sum(times),
            'avg': sum(times) / len(times),
            'min': min(times),
            'max': max(times),
        }
    
    def get_all_function_stats(self) -> Dict[str, Dict[str, float]]:
        """Получить статистику по всем функциям"""
        stats = {}
        for func_name in self.function_timings:
            stats[func_name] = self.get_function_stats(func_name)
        return stats
    
    def get_event_counts(self) -> Dict[str, int]:
        """Получить счетчики событий"""
        return dict(self.event_counts)
    
    def get_game_metrics(self) -> Dict[str, Any]:
        """Получить игровые метрики"""
        return self.game_metrics.copy()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Получить сводку производительности"""
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            'session_duration_seconds': session_duration,
            'fps': {
                'current': self.get_fps(),
                'average': self.get_avg_fps(60),
                'min': min(self.fps_history) if self.fps_history else 0.0,
                'max': max(self.fps_history) if self.fps_history else 0.0,
            },
            'memory': self.get_memory_usage(),
            'frame_times': {
                'avg': sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0.0,
                'min': min(self.frame_times) if self.frame_times else 0.0,
                'max': max(self.frame_times) if self.frame_times else 0.0,
            },
            'function_stats': self.get_all_function_stats(),
            'event_counts': self.get_event_counts(),
            'game_metrics': self.get_game_metrics(),
        }
    
    def log_performance_issue(self, threshold_fps: float = 30.0):
        """
        Логирование проблем с производительностью
        
        Args:
            threshold_fps: Порог FPS для предупреждения
        """
        avg_fps = self.get_avg_fps(60)
        if avg_fps < threshold_fps and avg_fps > 0:
            memory = self.get_memory_usage()
            self.logger.warning(
                LogCategory.PERFORMANCE,
                f"Низкий FPS: {avg_fps:.1f} (порог: {threshold_fps})",
                {
                    'fps': avg_fps,
                    'memory_mb': memory['memory_mb'],
                    'memory_percent': memory['memory_percent'],
                }
            )
    
    def save_metrics_report(self, filepath: Optional[str] = None):
        """
        Сохранить отчет о метриках
        
        Args:
            filepath: Путь к файлу (опционально)
        """
        if filepath is None:
            log_dir = Path("debug/logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            session_id = self.session_start.strftime('%Y%m%d_%H%M%S')
            filepath = log_dir / f"metrics_{session_id}.json"
        else:
            filepath = Path(filepath)
        
        report = {
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat(),
            'performance_summary': self.get_performance_summary(),
            'recent_memory_history': list(self.memory_history)[-100:],
            'recent_fps_history': list(self.fps_history)[-100:],
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(LogCategory.METRICS, f"Отчет о метриках сохранен: {filepath}")


# Глобальный экземпляр сборщика метрик
_metrics_instance: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Получить глобальный экземпляр сборщика метрик"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance


def initialize_metrics(**kwargs) -> MetricsCollector:
    """Инициализировать сборщик метрик с параметрами"""
    global _metrics_instance
    _metrics_instance = MetricsCollector(**kwargs)
    return _metrics_instance

