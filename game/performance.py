"""
Модуль для определения возможностей системы и оптимизации производительности
"""
import os
import sys

# Попытка импорта для определения доступности библиотек
NUMPY_AVAILABLE = False
PSUTIL_AVAILABLE = False
MULTIPROCESSING_AVAILABLE = False

try:
    import numpy
    NUMPY_AVAILABLE = True
except ImportError:
    pass

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    pass

try:
    import multiprocessing
    MULTIPROCESSING_AVAILABLE = True
except ImportError:
    pass

def get_system_info():
    """Получает информацию о системе для адаптивной оптимизации"""
    info = {
        'cpu_count': 1,
        'ram_total_gb': 4,
        'numpy_available': NUMPY_AVAILABLE,
        'psutil_available': PSUTIL_AVAILABLE,
        'multiprocessing_available': MULTIPROCESSING_AVAILABLE,
    }
    
    if MULTIPROCESSING_AVAILABLE:
        try:
            info['cpu_count'] = multiprocessing.cpu_count()
        except:
            pass
    
    if PSUTIL_AVAILABLE:
        try:
            ram = psutil.virtual_memory()
            info['ram_total_gb'] = ram.total / (1024 ** 3)
            info['ram_available_gb'] = ram.available / (1024 ** 3)
        except:
            pass
    
    return info

def get_performance_profile():
    """Определяет профиль производительности на основе возможностей системы"""
    info = get_system_info()
    
    # Максимальный профиль производительности: используем ВСЕ доступные ресурсы системы
    # Определяем доступную память и используем до 50% для кэширования
    max_cache_mb = min(2048, int(info['ram_total_gb'] * 512))  # До 512MB на GB RAM или 2GB максимум
    
    profile = {
        'use_numpy': NUMPY_AVAILABLE,
        'use_hardware_accel': True,
        'cache_aggressive': True,  # Максимальное кэширование
        'preload_resources': True,  # Предзагрузка всех ресурсов
        'max_cache_size_mb': max_cache_mb,  # Используем максимум памяти для кэша
        'animation_fps': 120,  # Максимальная частота анимации (неограниченная)
        'grass_quality': 'ultra',  # Максимальное качество травы
        'barrier_animation_fps': 120,  # Максимальная частота для барьеров
        'multithreading': MULTIPROCESSING_AVAILABLE and info['cpu_count'] > 1,  # Используем многопоточность
        'use_all_cores': True,  # Используем все доступные ядра CPU
        'max_fps': 0,  # 0 = неограниченный FPS для максимальной производительности
    }
    
    return profile

