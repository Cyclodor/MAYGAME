"""
Менеджер анимаций для игры
Содержит все визуальные эффекты и анимации
"""
import pygame
import math
from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from .graphics import (
    animate_fire_arrow_fly,
    animate_fire_explosion,
)


class AnimationManager:
    """Управляет всеми анимациями в игре"""
    
    def __init__(self, game):
        """
        game: ссылка на главный объект Game для доступа к screen и draw()
        """
        self.game = game
        self.screen = game.screen
    
    def animate_queue_move(self, old_queue, new_queue):
        """Анимация перемещения очереди (заглушка)"""
        pass

    def animate_queue_fade(self, unit):
        """Анимация исчезновения юнита из очереди (заглушка)"""
        pass

    def animate_spell_flash(self, target, color, redraw_callback=None):
        """Базовая анимация вспышки заклинания"""
        cx = target.x * CELL_SIZE + CELL_SIZE // 2
        cy = target.y * CELL_SIZE + CELL_SIZE // 2
        max_r = CELL_SIZE
        frames = 60  # Увеличено до 60 кадров для максимальной плавности
        for i in range(frames):
            pygame.event.pump()
            if redraw_callback:
                redraw_callback()
            r = int(max_r * (i + 1) / frames)
            alpha = max(40, 200 - int(200 * i / frames))
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (cx, cy), r, 4)
            self.screen.blit(s, (0, 0))
            pygame.display.flip()
            pygame.time.delay(10)  # Уменьшена задержка для плавности

    def animate_unit_move(self, unit, dest_x, dest_y):
        """Пошаговая анимация перемещения юнита по манхэттен-пути"""
        # Строим простой путь: сначала по X, затем по Y
        path = []
        cx, cy = unit.x, unit.y
        step_x = 1 if dest_x > cx else -1
        while cx != dest_x:
            cx += step_x
            path.append((cx, cy))
        step_y = 1 if dest_y > cy else -1
        while cy != dest_y:
            cy += step_y
            path.append((cx, cy))
        # Проигрываем шаги
        for px, py in path:
            unit.x, unit.y = px, py
            self.game.draw()
            pygame.display.flip()
            pygame.time.delay(60)

    def animate_firearrow(self, caster, target):
        """Анимация огненной стрелы"""
        start = (caster.x * CELL_SIZE + CELL_SIZE // 2, caster.y * CELL_SIZE + CELL_SIZE // 2)
        end = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
        # Полёт огненной стрелы с текстурами и пламенем
        animate_fire_arrow_fly(self.screen, start, end, redraw_callback=self.game.draw)
        # Эпичный взрыв в точке попадания
        animate_fire_explosion(self.screen, end[0], end[1])

    def animate_explosion(self, x, y, color):
        """Простая анимация взрыва"""
        pygame.draw.circle(self.screen, color, (x, y), 12)
        pygame.display.flip()

    def animate_roots(self, target):
        """Анимация корней (для заклинаний природы)"""
        self.animate_spell_flash(target, (80, 180, 60), redraw_callback=self.game.draw)

    def animate_water_bless(self, target):
        """Анимация водного благословения"""
        self.animate_spell_flash(target, (120, 180, 255), redraw_callback=self.game.draw)

    def animate_curse(self, caster, target):
        """Анимация проклятия"""
        self.animate_spell_flash(target, (200, 0, 0), redraw_callback=self.game.draw)

    def animate_undead_heal_cast(self, target):
        """Анимация исцеления нежити: призрачные кости и голубоватое свечение"""
        cx = target.x * CELL_SIZE + CELL_SIZE // 2
        cy = target.y * CELL_SIZE + CELL_SIZE // 2
        frames = 80  # Увеличено до 80 кадров для максимальной плавности
        for i in range(frames):
            pygame.event.pump()
            self.game.draw()
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            # Призрачные "кости" — светлые частицы, вращающиеся и стягивающиеся к центру
            for k in range(25):  # Увеличено количество частиц до 25
                ang = (i * 0.4 + k) * 0.8
                rad = 16 + max(0, 24 - i * 0.8)
                px = cx + int(math.cos(ang) * rad)
                py = cy + int(math.sin(ang) * rad)
                pygame.draw.circle(s, (200, 220, 240, 120), (px, py), 3)
                pygame.draw.circle(s, (230, 240, 255, 90), (px, py), 1)
            # Голубое лечебное свечение
            r = 8 + int(i * 0.5)
            a = max(0, 180 - int(i * 4.5))
            pygame.draw.circle(s, (120, 200, 255, a), (cx, cy), r, 3)
            self.screen.blit(s, (0, 0))
            pygame.display.flip()
            pygame.time.delay(8)  # Уменьшена задержка для плавности

    def animate_fire_shield_cast(self, target, hide_unit_at=None):
        """Анимация наложения огненного щита"""
        cx = target.x * CELL_SIZE + CELL_SIZE // 2
        cy = target.y * CELL_SIZE + CELL_SIZE // 2
        max_r = CELL_SIZE
        frames = 60  # Увеличено до 60 кадров для максимальной плавности
        for i in range(frames):
            pygame.event.pump()
            self.game.draw(hide_unit_at=hide_unit_at)
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            r = int(max_r * (i + 1) / frames)
            alpha = max(60, 220 - int(200 * i / frames))
            pygame.draw.circle(s, (255, 120, 40, alpha), (cx, cy), r, 4)
            pygame.draw.circle(s, (255, 200, 120, max(20, alpha - 40)), (cx, cy), max(2, r - 6), 2)
            self.screen.blit(s, (0, 0))
            pygame.display.flip()
            pygame.time.delay(8)  # Уменьшена задержка для плавности

    def animate_fire_shield_burst(self, defender, attacker, hide_unit_at=None):
        """Анимация срабатывания огненного щита"""
        self.animate_fire_shield_cast(defender, hide_unit_at=hide_unit_at)


