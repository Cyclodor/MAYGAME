"""
Анимации специфичные для героев разных классов
"""
import pygame
from .config import CELL_SIZE

def animate_warrior_teleport(screen, start_pos, end_pos, attacker_img, redraw_callback=None, attack_sound_callback=None, damage_callback=None, hide_attacker_pos=None):
    """
    Анимация телепортации воина: медленное исчезновение на старом месте, 
    появление рядом с целью, атака, и телепортация обратно.
    start_pos, end_pos: (x, y) в пикселях (координаты клетки, НЕ центр)
    hide_attacker_pos: (x, y) координаты юнита, которого не нужно рисовать во время анимации
    damage_callback: функция, вызываемая после звука атаки для применения урона
    """
    # Функция перерисовки, которая скрывает атакующего
    def redraw_without_attacker():
        if redraw_callback and hide_attacker_pos:
            redraw_callback(hide_unit_at=hide_attacker_pos)
        elif redraw_callback:
            redraw_callback()
    
    # Фаза 1: Исчезновение (fade out)
    fade_out_frames = 15
    for i in range(fade_out_frames):
        pygame.event.pump()
        redraw_without_attacker()
        
        # Рисуем героя с уменьшающейся прозрачностью
        alpha = int(255 * (1 - i / fade_out_frames))
        temp_surf = attacker_img.copy()
        temp_surf.set_alpha(alpha)
        screen.blit(temp_surf, (start_pos[0], start_pos[1]))
        
        pygame.display.flip()
        pygame.time.delay(30)
    
    # Фаза 2: Появление рядом с целью (fade in)
    fade_in_frames = 15
    for i in range(fade_in_frames):
        pygame.event.pump()
        redraw_without_attacker()
        
        # Рисуем героя с увеличивающейся прозрачностью
        alpha = int(255 * (i / fade_in_frames))
        temp_surf = attacker_img.copy()
        temp_surf.set_alpha(alpha)
        screen.blit(temp_surf, (end_pos[0], end_pos[1]))
        
        pygame.display.flip()
        pygame.time.delay(30)
    
    # Фаза 3: Замах и атака
    if attack_sound_callback:
        attack_sound_callback()
    
    # Применяем урон сразу после звука атаки!
    if damage_callback:
        damage_callback()
    
    attack_frames = 8
    for i in range(attack_frames):
        pygame.event.pump()
        redraw_without_attacker()
        
        # Небольшой "удар" - смещение влево-вправо
        offset_x = 5 if i % 2 == 0 else -5
        screen.blit(attacker_img, (end_pos[0] + offset_x, end_pos[1]))
        
        pygame.display.flip()
        pygame.time.delay(40)
    
    # Небольшая пауза
    pygame.time.delay(100)
    
    # Фаза 4: Исчезновение с позиции атаки
    for i in range(fade_out_frames):
        pygame.event.pump()
        redraw_without_attacker()
        
        alpha = int(255 * (1 - i / fade_out_frames))
        temp_surf = attacker_img.copy()
        temp_surf.set_alpha(alpha)
        screen.blit(temp_surf, (end_pos[0], end_pos[1]))
        
        pygame.display.flip()
        pygame.time.delay(30)
    
    # Фаза 5: Плавное появление обратно на начальной позиции
    fade_in_frames_return = 15
    for i in range(fade_in_frames_return):
        pygame.event.pump()
        redraw_without_attacker()
        
        # Рисуем героя с увеличивающейся прозрачностью на начальной позиции
        alpha = int(255 * (i / fade_in_frames_return))
        temp_surf = attacker_img.copy()
        temp_surf.set_alpha(alpha)
        screen.blit(temp_surf, (start_pos[0], start_pos[1]))
        
        pygame.display.flip()
        pygame.time.delay(30)

