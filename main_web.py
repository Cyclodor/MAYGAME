import pygame
import sys
import asyncio
from pygame import mixer
from game.config import *
from game.core import Game

# Инициализация системы логирования и отладки
try:
    from debug.system import initialize_debug_system, get_debug_system, LogCategory
    DEBUG_SYSTEM_ENABLED = True
except ImportError as e:
    print(f"Предупреждение: Система отладки недоступна: {e}")
    DEBUG_SYSTEM_ENABLED = False
    def get_debug_system():
        return None

async def main():
    print("Инициализация игры для веб-версии...")
    pygame.init()
    mixer.init()
    # Включаем аппаратное ускорение для веб-версии
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    except:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Фэнтези Стратегия")
    
    # Инициализация системы логирования и отладки
    debug_system = None
    if DEBUG_SYSTEM_ENABLED:
        try:
            debug_system = initialize_debug_system()
            logger = debug_system.logger
            logger.info(LogCategory.SYSTEM, "Игра запущена (веб-версия)", {
                'screen_size': (SCREEN_WIDTH, SCREEN_HEIGHT),
                'grid_size': (GRID_WIDTH, GRID_HEIGHT)
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
            debug_system = None
    
    print("Создание объекта Game...")
    game = Game(screen)
    print("Игра создана, состояние:", game.state)
    clock = pygame.time.Clock()
    
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
                    game.handle_click(event.pos, button=1)
                elif event.button == 3:
                    # Обработка правой кнопки мыши
                    if game.state == 'creative':
                        # Удаление юнитов в креативе правой кнопкой
                        game.handle_click(event.pos, button=3)
                    else:
                        # Cancel prepared spell if any
                        if (hasattr(game, 'selected_unit') and game.selected_unit and 
                            hasattr(game.selected_unit, 'selected_spell') and 
                            game.selected_unit.selected_spell is not None):
                            game.selected_unit.selected_spell = None
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
        
        game.update()
        game.draw()
        pygame.display.flip()
        
        # Сохраняем время для следующей итерации
        # Для веб-версии ограничиваем до 120 FPS (браузеры могут не справиться с неограниченным)
        frame_time = clock.tick(120) / 1000.0  # В секундах, максимальный FPS для веба
        
        # Критически важно для pygbag!
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
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
                                            "Критическая ошибка при работе игры (веб)",
                                            exception=e)
                debug_system.save_all_reports()
            except:
                pass
        raise

