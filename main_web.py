import pygame
import sys
import asyncio
from pygame import mixer
from game.config import *
from game.core import Game

async def main():
    pygame.init()
    mixer.init()
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
                    game.handle_click(event.pos)
                elif event.button == 3:
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
        
        # Критически важно для pygbag!
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())

