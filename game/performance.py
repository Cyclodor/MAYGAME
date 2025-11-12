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
    # Определяем доступную память и используем максимум для кэширования (до 75% доступной RAM)
    ram_available_gb = info.get('ram_available_gb', info['ram_total_gb'])
    # Используем до 75% доступной RAM для кэширования или минимум 512MB на GB RAM
    max_cache_mb = min(int(ram_available_gb * 1024 * 0.75), int(info['ram_total_gb'] * 1024))  # До 75% RAM
    max_cache_mb = max(max_cache_mb, int(info['ram_total_gb'] * 512))  # Минимум 512MB на GB RAM
    max_cache_mb = min(max_cache_mb, 4096)  # Максимум 4GB для кэша
    
    profile = {
        'use_numpy': NUMPY_AVAILABLE,
        'use_hardware_accel': True,
        'cache_aggressive': True,  # Максимальное кэширование
        'preload_resources': True,  # Предзагрузка всех ресурсов
        'max_cache_size_mb': max_cache_mb,  # Используем максимум памяти для кэша (до 75% RAM)
        'animation_fps': 240,  # Максимальная частота анимации
        'grass_quality': 'ultra',  # Максимальное качество травы
        'barrier_animation_fps': 240,  # Максимальная частота для барьеров
        'multithreading': MULTIPROCESSING_AVAILABLE and info['cpu_count'] > 1,  # Используем многопоточность
        'use_all_cores': True,  # Используем все доступные ядра CPU
        'max_fps': 0,  # 0 = неограниченный FPS для максимальной производительности
        'thread_pool_size': info.get('cpu_count', 1) * 2,  # Пулы потоков для параллельной обработки
        'precompute_cache': True,  # Предвычисление кэшей при загрузке
    }
    
    return profile

