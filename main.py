import pygame
import sys
import os
import subprocess
import shutil
from pygame import mixer
from game.config import *
from game.core import Game

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
        if main_py_time > main_spec_time:
            print("Обнаружены изменения в main.py. Пересобираю исполняемый файл...")
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
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Фэнтези Стратегия")
    game = Game(screen)
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
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main() 