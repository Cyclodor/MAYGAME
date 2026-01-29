import pygame
import sys
import os
import subprocess
import shutil
from pygame import mixer
from game.config import *
from game.core import Game
from game.config import CELL_SIZE

# Инициализация системы логирования и отладки
try:
    from debug.system import initialize_debug_system, get_debug_system, LogCategory
    DEBUG_SYSTEM_ENABLED = True
except ImportError as e:
    print(f"Предупреждение: Система отладки недоступна: {e}")
    DEBUG_SYSTEM_ENABLED = False
    def get_debug_system():
        return None

def _latest_source_mtime(paths):
    latest = 0.0
    for path in paths:
        if not os.path.exists(path):
            continue
        if os.path.isfile(path):
            latest = max(latest, os.path.getmtime(path))
            continue
        for root, _, files in os.walk(path):
            for fname in files:
                if fname.endswith(".py"):
                    try:
                        latest = max(latest, os.path.getmtime(os.path.join(root, fname)))
                    except OSError:
                        pass
    return latest


def auto_rebuild_exe():
    exe_name = 'main.exe'
    dist_path = os.path.join('dist', exe_name)
    exe_path = os.path.join(os.getcwd(), exe_name)
    need_rebuild = False
    if not os.path.exists('main.spec'):
        print("Создаю исполняемый файл...")
        subprocess.run(['py', '-m', 'PyInstaller', '--onefile', '--windowed', 'main.py'])
        need_rebuild = True
    else:
        main_py_time = os.path.getmtime('main.py')
        main_spec_time = os.path.getmtime('main.spec')
        project_sources_time = _latest_source_mtime(['main.py', 'game', 'tools'])
        exe_time = os.path.getmtime(exe_path) if os.path.exists(exe_path) else 0
        if main_py_time > main_spec_time or project_sources_time > exe_time:
            print("Обнаружены изменения в исходниках. Пересобираю исполняемый файл...")
            subprocess.run(['py', '-m', 'PyInstaller', '--onefile', '--windowed', 'main.py'])
            print("Исполняемый файл обновлен!")
            need_rebuild = True
    # Автоматическая замена main.exe
    if need_rebuild or not os.path.exists(exe_path):
        if os.path.exists(dist_path):
            try:
                shutil.move(dist_path, exe_path)
                print(f"main.exe успешно обновлён в {exe_path}")
            except Exception as e:
                print(f"Ошибка при замене main.exe: {e}")
        else:
            print(f"Не найден {dist_path} для замены main.exe")

def main():
    pygame.init()
    mixer.init()
    auto_rebuild_exe()
    
    # Получаем разрешение экрана монитора
    try:
        # Получаем размеры всех доступных дисплеев
        desktop_sizes = pygame.display.get_desktop_sizes()
        if desktop_sizes:
            # Используем разрешение основного монитора (первого в списке)
            monitor_width, monitor_height = desktop_sizes[0]
            print(f"Разрешение монитора: {monitor_width}x{monitor_height}")
        else:
            # Fallback, если не удалось получить размеры
            monitor_width, monitor_height = 1920, 1080
            print(f"Не удалось определить разрешение монитора, используется {monitor_width}x{monitor_height}")
    except Exception as e:
        print(f"Ошибка получения разрешения монитора: {e}")
        monitor_width, monitor_height = 1920, 1080
    
    # Загружаем настройки разрешения
    settings_path = os.path.join('data', 'settings.json')
    screen_width = SCREEN_WIDTH
    screen_height = SCREEN_HEIGHT
    fullscreen = False
    
    try:
        if os.path.exists(settings_path):
            import json
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                screen_width = int(data.get('screen_width', SCREEN_WIDTH))
                screen_height = int(data.get('screen_height', SCREEN_HEIGHT))
                fullscreen = bool(data.get('fullscreen', False))
    except Exception as e:
        print(f"Ошибка загрузки настроек разрешения: {e}")
    
    # В полноэкранном режиме используем разрешение монитора
    if fullscreen:
        screen_width = monitor_width
        screen_height = monitor_height
        print(f"Полноэкранный режим: использование разрешения монитора {screen_width}x{screen_height}")
    
    # Базовое разрешение внутреннего полотна (фиксировано)
    BASE_WIDTH = 800
    BASE_HEIGHT = 600
    
    # Настройки базового разрешения в конфиге (логическая область)
    import game.config as config
    config.SCREEN_WIDTH = BASE_WIDTH
    config.SCREEN_HEIGHT = BASE_HEIGHT
    config.GRID_WIDTH = BASE_WIDTH // config.CELL_SIZE
    config.GRID_HEIGHT = BASE_HEIGHT // config.CELL_SIZE
    
    # Создаем экран с учетом полноэкранного режима и аппаратным ускорением
    flags = pygame.FULLSCREEN if fullscreen else 0
    # Включаем все доступные флаги для максимальной производительности
    # HWSURFACE - аппаратное ускорение, DOUBLEBUF - двойная буферизация
    flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
    # Пытаемся использовать максимальные возможности видеокарты
    try:
        display_screen = pygame.display.set_mode((screen_width, screen_height), flags)
    except:
        # Если аппаратное ускорение недоступно, используем программный рендеринг
        flags = pygame.FULLSCREEN if fullscreen else 0
        display_screen = pygame.display.set_mode((screen_width, screen_height), flags)
    pygame.display.set_caption("Фэнтези Стратегия")
    
    # Инициализация системы логирования и отладки
    debug_system = None
    if DEBUG_SYSTEM_ENABLED:
        try:
            debug_system = initialize_debug_system()
            logger = debug_system.logger
            logger.info(LogCategory.SYSTEM, "Игра запущена", {
                'screen_size': (screen_width, screen_height),
                'grid_size': (config.GRID_WIDTH, config.GRID_HEIGHT)
            })
            print("\n" + "="*50)
            print("СИСТЕМА ЛОГИРОВАНИЯ И ОТЛАДКИ АКТИВНА!")
            print("="*50)
            print("Логи сохраняются в: debug/logs/")
            print("Система автоматически отслеживает производительность,")
            print("валидацию состояния игры и диагностику проблем.")
            # Проверяем реальное состояние psutil после инициализации
            if debug_system and debug_system.metrics:
                if debug_system.metrics.psutil_available:
                    print("Метрики памяти: доступны")
                else:
                    print("Примечание: psutil не установлен, метрики памяти недоступны.")
            print("="*50)
        except Exception as e:
            print(f"Ошибка инициализации системы отладки: {e}")
            import traceback
            traceback.print_exc()
            debug_system = None
    
    # Внутренняя поверхность для рендеринга
    render_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    
    # Передаем внутреннюю поверхность в игру
    game = Game(render_surface)
    clock = pygame.time.Clock()
    
    # Начальный масштаб и смещения
    def update_render_params():
        # ВАЖНО: Используем pixel-perfect scaling (целочисленное масштабирование)
        # Каждый пиксель текстуры отображается как NxN пикселей на экране, где N - целое число
        # Это сохраняет четкость пикселей без размытия, идеально для pixel-art стиля
        # Вычисляем максимальный целочисленный масштаб, который помещается в экран
        scale_x = screen_width // BASE_WIDTH  # Целочисленное деление
        scale_y = screen_height // BASE_HEIGHT  # Целочисленное деление
        # Берем минимум, чтобы изображение помещалось полностью
        integer_scale = min(scale_x, scale_y)
        # Минимальный масштаб - 1 (не уменьшаем изображение)
        integer_scale = max(1, integer_scale)
        
        # Вычисляем размеры масштабированного изображения
        scaled_width = BASE_WIDTH * integer_scale
        scaled_height = BASE_HEIGHT * integer_scale
        
        # Центрируем изображение на экране (черные полосы будут минимальными)
        offset_x = (screen_width - scaled_width) // 2
        offset_y = (screen_height - scaled_height) // 2
        
        # Сохраняем в конфиг для использования в игре
        config.RENDER_SCALE = float(integer_scale)
        config.RENDER_SCALE_X = float(integer_scale)
        config.RENDER_SCALE_Y = float(integer_scale)
        config.RENDER_OFFSET_X = offset_x
        config.RENDER_OFFSET_Y = offset_y
        # Масштаб для координат мыши
        config.MOUSE_SCALE_X = float(integer_scale)
        config.MOUSE_SCALE_Y = float(integer_scale)
        return integer_scale, scaled_width, scaled_height, offset_x, offset_y
    
    scale, scaled_width, scaled_height, offset_x, offset_y = update_render_params()

    original_flip = pygame.display.flip

    def present_frame():
        nonlocal display_screen, render_surface
        display_screen.fill((0, 0, 0))  # Черный фон для черных полос
        # ВАЖНО: Используем целочисленное масштабирование (pixel-perfect scaling)
        # scale всегда целое число (1, 2, 3, 4...)
        # Это обеспечивает идеальное качество для pixel-art текстур:
        # - Каждый пиксель дублируется точно N раз (без интерполяции)
        # - Нет размытия или искажений
        # - Сохраняется четкость границ и деталей
        scale = int(max(config.RENDER_SCALE, 1))
        scaled_w = BASE_WIDTH * scale
        scaled_h = BASE_HEIGHT * scale
        
        if scaled_w > 0 and scaled_h > 0:
            if scale == 1:
                # Масштаб 1:1 - просто копируем поверхность без изменений
                surface_to_blit = render_surface
            else:
                # Целочисленное масштабирование: используем scale() вместо smoothscale()
                # pygame.transform.scale() использует nearest neighbor интерполяцию
                # Это идеально для pixel-art: каждый пиксель становится блоком NxN пикселей
                # НЕ используем smoothscale(), так как он размывает пиксели
                surface_to_blit = pygame.transform.scale(render_surface, (scaled_w, scaled_h))
            display_screen.blit(surface_to_blit, (config.RENDER_OFFSET_X, config.RENDER_OFFSET_Y))
        original_flip()

    pygame.display.flip = present_frame
    
    def screen_to_base(pos):
        # ВАЖНО: scale всегда целое число для целочисленного масштабирования
        scale = int(max(config.RENDER_SCALE, 1))
        x = int((pos[0] - config.RENDER_OFFSET_X) / scale)
        y = int((pos[1] - config.RENDER_OFFSET_Y) / scale)
        return x, y
    
    # Выводим информацию о дебаггере
    print("\n" + "="*50)
    print("ДЕБАГГЕР АКТИВЕН!")
    print("="*50)
    print("F1 - Включить/выключить режим отладки")
    print("F2 - Отладка дальности хода")
    print("F3 - Отладка дальности атаки")
    print("F4 - Отладка интерфейса")
    print("F5 - Отладка дальнобойных юнитов")
    print("F6 - Тест can_attack для выбранного юнита")
    print("="*50)
    
    # Переменная для отслеживания времени
    last_time = pygame.time.get_ticks()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Обычный клик левой кнопкой (координаты уже в правильном масштабе)
                    base_pos = screen_to_base(event.pos)
                    result = game.handle_click(base_pos, button=1)
                    # Проверяем, нужно ли применить изменения разрешения
                    if result == 'apply_resolution':
                        # Применяем изменения разрешения
                        new_display_screen = game.apply_resolution_change(display_screen)
                        if new_display_screen:
                            display_screen = new_display_screen
                        screen_width = game.screen_width
                        screen_height = game.screen_height
                        # Обновляем конфиг внутреннего полотна
                        config.SCREEN_WIDTH = BASE_WIDTH
                        config.SCREEN_HEIGHT = BASE_HEIGHT
                        config.GRID_WIDTH = BASE_WIDTH // config.CELL_SIZE
                        config.GRID_HEIGHT = BASE_HEIGHT // config.CELL_SIZE
                        scale, scaled_width, scaled_height, offset_x, offset_y = update_render_params()
                        game.screen = render_surface
                elif event.button == 3:
                    # Обработка правой кнопки мыши
                    base_pos = screen_to_base(event.pos)
                    if game.state == 'creative':
                        # Удаление юнитов в креативе правой кнопкой
                        game.handle_click(base_pos, button=3)
                    else:
                        # Cancel prepared spell if any
                        if (hasattr(game, 'selected_unit') and game.selected_unit and 
                            hasattr(game.selected_unit, 'selected_spell') and 
                            game.selected_unit.selected_spell is not None):
                            game.selected_unit.selected_spell = None
                        
                        # Проверяем, кликнули ли по юниту
                        clicked_unit = None
                        from game.config import CELL_SIZE
                        for unit in game.units:
                            if (unit.x * CELL_SIZE <= base_pos[0] < (unit.x+1)*CELL_SIZE and 
                                unit.y * CELL_SIZE <= base_pos[1] < (unit.y+1)*CELL_SIZE):
                                clicked_unit = unit
                                break
                        
                        # Обработка двойного клика правой кнопкой для открытия окна юнита
                        current_time = pygame.time.get_ticks()
                        if (clicked_unit and 
                            game.last_click_unit == clicked_unit and
                            game.last_click_pos and
                            abs(base_pos[0] - game.last_click_pos[0]) < 10 and
                            abs(base_pos[1] - game.last_click_pos[1]) < 10 and
                            current_time - game.last_click_time < 500 and
                            game.last_click_button == 3):
                            # Двойной клик правой кнопкой - открываем окно юнита
                            game.unit_info_window_open = True
                            game.unit_info_window_unit = clicked_unit
                            game.last_click_time = 0  # Сбрасываем для предотвращения тройного клика
                            game.last_click_unit = None
                            game.last_click_button = None
                        else:
                            # Сохраняем информацию о клике для проверки двойного клика
                            game.last_click_time = current_time
                            game.last_click_pos = base_pos
                            game.last_click_unit = clicked_unit
                            game.last_click_button = 3
                            
                            # Зажатие правой кнопки на юните для тултипа
                            if clicked_unit:
                                game.unit_tooltip_unit = clicked_unit
                                game.unit_tooltip_show = True
                            else:
                                game.unit_tooltip_show = False
                                game.unit_tooltip_unit = None
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    # Отпускание правой кнопки - скрываем тултип
                    game.unit_tooltip_show = False
                    game.unit_tooltip_unit = None
            elif event.type == pygame.MOUSEMOTION:
                # Обновляем позицию мыши для тултипов и других элементов
                if hasattr(game, 'handle_mouse_motion'):
                    try:
                        game.handle_mouse_motion(screen_to_base(event.pos))
                    except Exception:
                        pass
            elif event.type == pygame.MOUSEWHEEL:
                # Прокрутка UI (креатив/редактор книг) колесом мыши
                if hasattr(game, 'on_mouse_wheel'):
                    try:
                        game.on_mouse_wheel(event.y)
                    except Exception:
                        pass
            elif event.type == pygame.KEYDOWN:
                if game.state == 'menu':
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif game.state == 'multiplayer_mode_selection':
                    if event.key == pygame.K_ESCAPE:
                        game.clear_multiplayer_data()
                        game.state = 'menu'
                elif game.state == 'multiplayer_lobby':
                    # Обработка ввода кода лобби для клиента
                    if (hasattr(game, 'multiplayer_lobby_code_input_active') and 
                        game.multiplayer_lobby_code_input_active):
                        if event.key == pygame.K_BACKSPACE:
                            game.multiplayer_lobby_code_input = game.multiplayer_lobby_code_input[:-1]
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            if len(game.multiplayer_lobby_code_input) == 6:
                                game.start_multiplayer_client(game.multiplayer_lobby_code_input)
                        elif event.unicode and event.unicode.isdigit() and len(game.multiplayer_lobby_code_input) < 6:
                            game.multiplayer_lobby_code_input += event.unicode
                        elif event.key == pygame.K_ESCAPE:
                            game.multiplayer_lobby_code_input_active = False
                    elif event.key == pygame.K_ESCAPE:
                        # Выход из лобби - полная очистка данных
                        game.clear_multiplayer_data()
                        game.state = 'menu'
                else:
                    if event.key == pygame.K_ESCAPE:
                        game.handle_key(event.key)
                    elif pygame.K_1 <= event.key <= pygame.K_3:
                        game.handle_key(event.key)
                    else:
                        game.handle_key(event.key)
        
        # Вычисление delta_time для системы отладки
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0  # В секундах
        last_time = current_time
        
        # Обновление системы отладки
        if debug_system:
            try:
                debug_system.update(game, delta_time)
            except Exception as e:
                print(f"Ошибка обновления системы отладки: {e}")
        
        # Оптимизация FPS: используем двойную буферизацию (включена в flags)
        # tick() должен быть вызван ДО обновления для правильного контроля FPS
        # Убираем ограничение FPS для максимального использования ресурсов
        # Передаем 0 для неограниченного FPS (используем все ресурсы CPU/GPU)
        frame_time = clock.tick(0) / 1000.0  # 0 = неограниченный FPS для максимальной производительности
        
        # Проверяем, нужно ли обновить экран (например, после переключения полноэкранного режима)
        if hasattr(game, '_pending_screen_update') and game._pending_screen_update:
            new_display_screen = game._pending_screen_update
            game._pending_screen_update = None
            if new_display_screen:
                display_screen = new_display_screen
            screen_width = game.screen_width
            screen_height = game.screen_height
            # Обновляем конфиг внутреннего полотна
            config.SCREEN_WIDTH = BASE_WIDTH
            config.SCREEN_HEIGHT = BASE_HEIGHT
            config.GRID_WIDTH = BASE_WIDTH // config.CELL_SIZE
            config.GRID_HEIGHT = BASE_HEIGHT // config.CELL_SIZE
            scale, scaled_width, scaled_height, offset_x, offset_y = update_render_params()
            game.screen = render_surface
        
        # Обновляем игру
        game.update()
        
        # Рисуем на внутренней поверхности
        game.draw()
        
        # Масштабируем и выводим на экран
        pygame.display.flip()
        
        # Обновляем метрики FPS в системе отладки
        if debug_system and debug_system.metrics:
            try:
                fps = 1.0 / frame_time if frame_time > 0 else 0
                debug_system.metrics.update_frame(frame_time)
            except Exception:
                pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nИгра прервана пользователем")
        # Сохраняем отчеты при выходе
        debug_system = get_debug_system()
        if debug_system:
            try:
                debug_system.save_all_reports()
                print("Отчеты системы отладки сохранены")
            except Exception as e:
                print(f"Ошибка сохранения отчетов: {e}")
        sys.exit(0)
    except Exception as e:
        # Логируем критическую ошибку
        debug_system = get_debug_system()
        if debug_system:
            try:
                debug_system.logger.critical(LogCategory.ERROR, 
                                            "Критическая ошибка при работе игры",
                                            exception=e)
                debug_system.save_all_reports()
            except:
                pass
        raise 