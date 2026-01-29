import pygame
import random
import math
import os
from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_WIDTH, GRID_HEIGHT, GOLD

# Кэш для загруженных текстур
_texture_cache = {}

def _legacy_crossbowman_texture(animation_state='Idle'):
    """Генерируем профильную текстуру арбалетчика с вариациями поз."""
    cache_key = f'crossbowman_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def outlined_rect(target, rect, fill, outline=(30, 25, 20), width=1):
        pygame.draw.rect(target, fill, rect)
        pygame.draw.rect(target, outline, rect, width)

    def gradient_band(target, rect, top_color, bottom_color):
        x, y, w, h = rect
        for i in range(h):
            t = i / max(1, h - 1)
            color = (
                int(top_color[0] + (bottom_color[0] - top_color[0]) * t),
                int(top_color[1] + (bottom_color[1] - top_color[1]) * t),
                int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
            )
            pygame.draw.line(target, color, (x, y + i), (x + w - 1, y + i))

    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, crossbow_angle=0,
                  crossbow_raise=0, head_tilt=0, crouch=0, show_dagger=False,
                  dagger_phase=0, lighten=False):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        crossbow = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        quiver = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (45, 40, 36, 160)
        armor_dark = (110, 108, 104)
        armor_mid = (162, 156, 142)
        armor_light = (206, 198, 184)
        cloth = (88, 108, 158)
        leather_dark = (92, 66, 46)
        leather_mid = (132, 96, 66)
        leather_light = (174, 138, 94)
        boots_dark = (64, 50, 36)
        boots_light = (92, 70, 52)
        skin = (240, 214, 182)
        metal = (210, 210, 218)
        steel = (168, 174, 184)
        visor = (86, 95, 112)
        string = (72, 58, 48)

        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        back_leg_rect = pygame.Rect(12 + leg_back_shift, 24 + base_y, 6, 11)
        front_leg_rect = pygame.Rect(22 + leg_front_shift, 24 + base_y - 1, 7, 12)
        outlined_rect(body, back_leg_rect, boots_dark, outline=(40, 32, 24))
        outlined_rect(body, front_leg_rect, boots_light, outline=(40, 32, 24))

        gradient_band(body, (12, 19 + base_y, 17, 5), leather_mid, leather_dark)
        pygame.draw.rect(body, (40, 32, 24), (12, 19 + base_y, 17, 5), 1)

        torso_rect = pygame.Rect(13 + torso_shift, 10 + base_y, 18, 12)
        gradient_band(body, torso_rect, armor_light, armor_dark)
        pygame.draw.rect(body, (40, 35, 30), torso_rect, 1)
        pygame.draw.rect(body, armor_mid, (13 + torso_shift, 14 + base_y, 18, 3))

        pygame.draw.ellipse(body, armor_mid, (10 + torso_shift, 10 + base_y, 10, 6))
        pygame.draw.ellipse(body, armor_light, (11 + torso_shift, 11 + base_y, 8, 3))
        pygame.draw.rect(body, cloth, (11 + torso_shift, 12 + base_y, 5, 12))
        pygame.draw.rect(body, (40, 35, 30), (11 + torso_shift, 12 + base_y, 5, 12), 1)

        front_arm = pygame.Rect(19 + torso_shift, 14 + base_y, 10, 4)
        back_arm = pygame.Rect(13 + torso_shift, 15 + base_y, 8, 4)
        outlined_rect(body, back_arm, leather_mid, outline=(40, 32, 24))
        outlined_rect(body, front_arm, leather_light, outline=(40, 32, 24))
        pygame.draw.rect(body, metal, (27 + torso_shift, 14 + base_y, 4, 4))

        helmet = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 22 + torso_shift
        head_y = 5 + base_y + head_tilt
        pygame.draw.ellipse(helmet, armor_mid, (head_x - 7, head_y, 14, 10))
        pygame.draw.rect(helmet, armor_dark, (head_x - 7, head_y - 2, 14, 4))
        pygame.draw.rect(helmet, visor, (head_x - 3, head_y + 3, 9, 4))
        pygame.draw.rect(helmet, steel, (head_x - 3, head_y + 2, 7, 2))
        pygame.draw.polygon(helmet, GOLD, [(head_x - 1, head_y - 2), (head_x + 1, head_y - 6), (head_x + 4, head_y - 2)])
        pygame.draw.polygon(helmet, (60, 52, 40), [(head_x - 1, head_y - 2), (head_x + 1, head_y - 6), (head_x + 4, head_y - 2)], 1)
        pygame.draw.polygon(helmet, skin, [(head_x + 4, head_y + 4), (head_x + 6, head_y + 5), (head_x + 4, head_y + 6)])
        pygame.draw.rect(helmet, skin, (head_x - 1, head_y + 6, 4, 3))
        pygame.draw.line(helmet, (40, 32, 24), (head_x - 1, head_y + 7), (head_x + 2, head_y + 7))
        body.blit(helmet, (0, 0))

        outlined_rect(quiver, pygame.Rect(8, 12 + base_y, 5, 13), leather_dark, outline=(32, 26, 18))
        pygame.draw.rect(quiver, leather_mid, (8, 20 + base_y, 5, 4))
        for i in range(3):
            pygame.draw.line(quiver, metal, (9 + i, 11 + base_y), (9 + i, 16 + base_y), 1)
            pygame.draw.circle(quiver, metal, (9 + i, 11 + base_y), 1)

        if show_dagger:
            dagger = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            if dagger_phase == 0:
                pygame.draw.rect(dagger, leather_dark, (20 + torso_shift, 15 + base_y, 2, 6))
                pygame.draw.polygon(dagger, metal, [(21 + torso_shift, 15 + base_y),
                                                    (24 + torso_shift, 16 + base_y),
                                                    (21 + torso_shift, 19 + base_y)])
            elif dagger_phase == 1:
                pygame.draw.rect(dagger, leather_dark, (26 + torso_shift, 14 + base_y, 3, 8))
                pygame.draw.polygon(dagger, metal, [(29 + torso_shift, 15 + base_y),
                                                    (34 + torso_shift, 13 + base_y),
                                                    (30 + torso_shift, 18 + base_y)])
            else:
                pygame.draw.rect(dagger, leather_dark, (22 + torso_shift, 14 + base_y, 2, 7))
                pygame.draw.polygon(dagger, metal, [(23 + torso_shift, 14 + base_y),
                                                    (26 + torso_shift, 15 + base_y),
                                                    (23 + torso_shift, 18 + base_y)])
            body.blit(dagger, (0, 0))

        pygame.draw.rect(crossbow, leather_dark, (18, 18 + crossbow_raise + base_y, 16, 4))
        pygame.draw.rect(crossbow, (40, 30, 20), (18, 18 + crossbow_raise + base_y, 16, 4), 1)
        pygame.draw.rect(crossbow, metal, (24, 14 + crossbow_raise + base_y, 4, 8))
        pygame.draw.rect(crossbow, (50, 40, 30), (24, 14 + crossbow_raise + base_y, 4, 8), 1)
        pygame.draw.rect(crossbow, GOLD, (22, 20 + crossbow_raise + base_y, 8, 2))
        pygame.draw.line(crossbow, string, (19, 18 + crossbow_raise + base_y), (33, 18 + crossbow_raise + base_y), 1)
        pygame.draw.polygon(crossbow, metal, [(24, 15 + crossbow_raise + base_y), (28, 15 + crossbow_raise + base_y), (30, 18 + crossbow_raise + base_y), (22, 18 + crossbow_raise + base_y)])
        pygame.draw.rect(crossbow, metal, (25, 17 + crossbow_raise + base_y, 2, 4))
        pygame.draw.rect(crossbow, (80, 65, 45), (24, 17 + crossbow_raise + base_y, 4, 1))
        pygame.draw.rect(crossbow, metal, (28, 17 + crossbow_raise + base_y, 2, 6))

        body.blit(quiver, (0, 0))
        final_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        final_surface.blit(body, (0, 0))

        if crossbow_angle != 0:
            cb_rotated = pygame.transform.rotate(crossbow, crossbow_angle)
            cb_rect = cb_rotated.get_rect(center=(CELL_SIZE // 2 + 6, CELL_SIZE // 2 - 4 + crossbow_raise))
            final_surface.blit(cb_rotated, cb_rect.topleft)
        else:
            final_surface.blit(crossbow, (0, 0))

        if lighten:
            wash = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            wash.fill((255, 245, 220, 90))
            final_surface.blit(wash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return final_surface

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=-1, torso_shift=0, crossbow_angle=-6, crossbow_raise=-1, head_tilt=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-3, torso_shift=-1, crossbow_angle=-4, crossbow_raise=-1, head_tilt=-1),
        'WalkAlt': dict(leg_front_shift=-1, leg_back_shift=2, torso_shift=1, crossbow_angle=-2, crossbow_raise=0, head_tilt=1),
        'Attack': dict(torso_shift=-1, crossbow_angle=-18, crossbow_raise=-3, head_tilt=-1),
        'Attack02': dict(torso_shift=-1, crossbow_angle=6, crossbow_raise=-1, head_tilt=0),
        'Attack03': dict(torso_shift=-1, crossbow_angle=14, crossbow_raise=2, head_tilt=1),
        'MeleePrep': dict(torso_shift=-2, crossbow_angle=-10, crossbow_raise=4, head_tilt=-1, show_dagger=True, dagger_phase=0),
        'MeleeStrike': dict(torso_shift=-1, crossbow_angle=12, crossbow_raise=5, head_tilt=0, show_dagger=True, dagger_phase=1),
        'MeleeRecover': dict(torso_shift=-1, crossbow_angle=-4, crossbow_raise=2, head_tilt=0, show_dagger=True, dagger_phase=2),
        'Hurt': dict(torso_shift=-2, crouch=2, crossbow_raise=2, head_tilt=-3, lighten=True),
        'Death': dict(torso_shift=-3, crouch=5, crossbow_angle=20, crossbow_raise=6, head_tilt=6, lighten=True),
        'Corpse': dict(torso_shift=-3, crouch=6, crossbow_angle=22, crossbow_raise=6, head_tilt=6, lighten=True),
    }

    params = params_map.get(animation_state, params_map['Idle'])
    surface = build_pose(**params)

    if animation_state == 'Hurt':
        overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((255, 80, 80, 110))
        surface.blit(overlay, (0, 0))
    elif animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 70)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-6, 10))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 88)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 6))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_greendragon_texture(animation_state='Idle'):
    """Процедурная анимация зелёного дракона: парение, шаги и плевок огнём/ядовитыми облаками."""
    cache_key = f'greendragon_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        wing_phase=0,
        tail_phase=0,
        breath_size=0,
    ):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (18, 40, 22, 180)
        body_main = (60, 150, 80)
        body_dark = (40, 120, 60)
        wing = (70, 180, 100)
        horn = (120, 210, 130)
        eye = (255, 230, 120)

        base_y = crouch
        pygame.draw.ellipse(surf, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        # Тело
        pygame.draw.ellipse(surf, body_main, (8 + torso_shift, 20 + base_y, 24, 14))
        pygame.draw.ellipse(surf, body_dark, (10 + torso_shift, 22 + base_y, 20, 10))

        # Хвост
        tail = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        for i in range(3):
            pygame.draw.circle(
                tail,
                body_dark,
                (8 - i * 3, 24 + base_y + tail_phase + i * 3),
                2,
            )
        pygame.draw.polygon(tail, body_main, [(0, 30 + base_y), (4, 32 + base_y), (2, 28 + base_y)])
        surf.blit(tail, (0, 0))

        # Крылья
        wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        for side, sign in (('left', -1), ('right', 1)):
            dx = 2 if side == 'left' else 28
            flap = wing_phase * sign
            pygame.draw.ellipse(wings, wing, (dx, 12 + base_y + flap, 10, 14))
            pygame.draw.ellipse(wings, body_dark, (dx, 12 + base_y + flap, 10, 14), 2)
        surf.blit(wings, (0, 0))

        # Голова
        head = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 26 + torso_shift
        head_y = 10 + base_y + head_tilt
        pygame.draw.ellipse(head, body_main, (head_x, head_y, 12, 10))
        # Глаза
        pygame.draw.circle(head, eye, (head_x + 3, head_y + 4), 2)
        pygame.draw.circle(head, eye, (head_x + 9, head_y + 4), 2)
        # Рога
        pygame.draw.polygon(head, horn, [(head_x + 2, head_y + 2), (head_x, head_y - 2), (head_x + 4, head_y + 2)])
        pygame.draw.polygon(head, horn, [(head_x + 10, head_y + 2), (head_x + 12, head_y - 2), (head_x + 8, head_y + 2)])
        surf.blit(head, (0, 0))

        # Дыхание (огонь/яд)
        if breath_size > 0:
            breath = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            for i in range(breath_size):
                pygame.draw.circle(
                    breath,
                    (120, 230, 120, 140),
                    (38 + i * 2, head_y + 4),
                    max(1, 3 - i),
                )
            surf.blit(breath, (0, 0))

        return surf

    params_map = {
        'Idle': dict(torso_shift=0, head_tilt=0, crouch=0, wing_phase=0, tail_phase=0, breath_size=0),
        'IdleBreath': dict(torso_shift=-1, head_tilt=-1, crouch=0, wing_phase=1, tail_phase=1, breath_size=0),
        'Walk': dict(torso_shift=-1, head_tilt=0, crouch=0, wing_phase=2, tail_phase=2, breath_size=0),
        'WalkAlt': dict(torso_shift=1, head_tilt=0, crouch=0, wing_phase=-2, tail_phase=-2, breath_size=0),
        'AttackPrep': dict(torso_shift=-2, head_tilt=-2, crouch=1, wing_phase=-1, tail_phase=3, breath_size=1),
        'AttackStrike': dict(torso_shift=1, head_tilt=1, crouch=-1, wing_phase=3, tail_phase=4, breath_size=3),
        'AttackRecover': dict(torso_shift=0, head_tilt=0, crouch=0, wing_phase=1, tail_phase=2, breath_size=0),
        'Hurt': dict(torso_shift=-1, head_tilt=-4, crouch=2, wing_phase=-2, tail_phase=-2, breath_size=0),
        'Death': dict(torso_shift=-2, head_tilt=5, crouch=5, wing_phase=0, tail_phase=0, breath_size=0),
        'Corpse': dict(torso_shift=-2, head_tilt=5, crouch=6, wing_phase=0, tail_phase=0, breath_size=0),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_zombie_texture(animation_state='Idle'):
    """Процедурная анимация зомби: тяжёлые шаги и замах руками."""
    cache_key = f'zombie_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        arm_swing=0,
        shamble_phase=0,
    ):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (24, 32, 24, 190)
        body = (90, 125, 95)
        body_dark = (70, 105, 80)
        skin = (155, 195, 160)
        skin_dark = (135, 175, 140)

        base_y = crouch
        pygame.draw.ellipse(surf, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        # Тело
        torso = pygame.Rect(14 + torso_shift, 18 + base_y, 14, 14)
        pygame.draw.rect(surf, body, torso)
        pygame.draw.rect(surf, body_dark, torso, 2)

        # Голова
        head = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 21 + torso_shift
        head_y = 8 + base_y + head_tilt
        pygame.draw.ellipse(head, skin, (head_x - 5, head_y, 10, 10))
        pygame.draw.ellipse(head, skin_dark, (head_x - 3, head_y + 2, 6, 6))
        pygame.draw.circle(head, (20, 55, 30), (head_x - 1, head_y + 4), 2)
        pygame.draw.circle(head, (20, 55, 30), (head_x + 2, head_y + 4), 2)
        surf.blit(head, (0, 0))

        # Руки
        arms = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.line(
            arms,
            skin,
            (14 + torso_shift, 22 + base_y),
            (10 + torso_shift - arm_swing, 30 + base_y + shamble_phase),
            3,
        )
        pygame.draw.line(
            arms,
            skin,
            (26 + torso_shift, 22 + base_y),
            (30 + torso_shift + arm_swing, 30 + base_y - shamble_phase),
            3,
        )
        surf.blit(arms, (0, 0))

        # Ноги
        for i, x in enumerate((16, 22)):
            dy = shamble_phase if i == 0 else -shamble_phase
            pygame.draw.rect(surf, body_dark, (x, 30 + base_y + dy, 4, 10))

        return surf

    params_map = {
        'Idle': dict(torso_shift=0, head_tilt=0, crouch=0, arm_swing=0, shamble_phase=0),
        'IdleBreath': dict(torso_shift=-1, head_tilt=-1, crouch=0, arm_swing=1, shamble_phase=1),
        'Walk': dict(torso_shift=-1, head_tilt=0, crouch=0, arm_swing=2, shamble_phase=2),
        'WalkAlt': dict(torso_shift=1, head_tilt=0, crouch=0, arm_swing=-2, shamble_phase=-2),
        'AttackPrep': dict(torso_shift=-2, head_tilt=-2, crouch=1, arm_swing=-3, shamble_phase=2),
        'AttackStrike': dict(torso_shift=1, head_tilt=1, crouch=-1, arm_swing=4, shamble_phase=3),
        'AttackRecover': dict(torso_shift=0, head_tilt=0, crouch=0, arm_swing=1, shamble_phase=1),
        'Hurt': dict(torso_shift=-1, head_tilt=-4, crouch=2, arm_swing=-2, shamble_phase=-2),
        'Death': dict(torso_shift=-2, head_tilt=5, crouch=5, arm_swing=0, shamble_phase=0),
        'Corpse': dict(torso_shift=-2, head_tilt=5, crouch=6, arm_swing=0, shamble_phase=0),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_ghost_texture(animation_state='Idle'):
    """Процедурная анимация призрака: парение, дрожащий силуэт и вспышки ауры."""
    cache_key = f'ghost_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        float_phase=0,
        aura_pulse=0,
        head_tilt=0,
    ):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        base_y = -2 + float_phase
        body_main = (220, 220, 255, 180)
        body_inner = (200, 200, 235, 160)
        face = (240, 240, 255, 200)

        ghost = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(ghost, body_main, (10, 8 + base_y, 20, 18))
        pygame.draw.ellipse(ghost, body_inner, (12, 10 + base_y, 16, 14))
        pygame.draw.ellipse(ghost, face, (14, 10 + base_y, 12, 8))
        pygame.draw.circle(ghost, (100, 100, 200, 180), (18, 14 + base_y), 2)
        pygame.draw.circle(ghost, (100, 100, 200, 180), (22, 14 + base_y), 2)
        pygame.draw.arc(ghost, (120, 120, 200, 160), (18, 16 + base_y, 4, 3), 0, 3.14, 2)
        # нижняя волнистая часть
        pygame.draw.arc(ghost, (120, 120, 180, 120), (6, 18 + base_y, 28, 18), 3.14, 0, 3)

        # Аура
        for i in range(3):
            pygame.draw.circle(
                ghost,
                (200, 200, 255, 60 - i * 15 + aura_pulse),
                (20, 20 + base_y),
                8 + i * 3,
                1,
            )

        surf.blit(ghost, (0, 0))
        return surf

    params_map = {
        'Idle': dict(float_phase=0, aura_pulse=0, head_tilt=0),
        'IdleBreath': dict(float_phase=1, aura_pulse=10, head_tilt=-1),
        'Walk': dict(float_phase=2, aura_pulse=15, head_tilt=0),
        'WalkAlt': dict(float_phase=-2, aura_pulse=15, head_tilt=0),
        'AttackPrep': dict(float_phase=1, aura_pulse=20, head_tilt=-2),
        'AttackStrike': dict(float_phase=-1, aura_pulse=30, head_tilt=1),
        'AttackRecover': dict(float_phase=0, aura_pulse=10, head_tilt=0),
        'Hurt': dict(float_phase=3, aura_pulse=0, head_tilt=-4),
        'Death': dict(float_phase=4, aura_pulse=0, head_tilt=5),
        'Corpse': dict(float_phase=5, aura_pulse=0, head_tilt=5),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        fade = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        fade.fill((0, 0, 0, 80))
        surface.blit(fade, (0, 0))
    elif animation_state == 'Corpse':
        # лёгкое прозрачное пятно вместо тела
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(corpse_surface, (180, 180, 220, 120), (8, 20, 24, 10))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_vampire_texture(animation_state='Idle'):
    """Процедурная анимация вампира: плащ, шаги и выпад с клыками."""
    cache_key = f'vampire_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        cloak_sway=0,
        arm_reach=0,
    ):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (30, 18, 26, 180)
        body = (120, 40, 80)
        body_inner = (100, 20, 60)
        skin = (220, 220, 220)
        skin_dark = (200, 200, 200)
        cloak_outer = (180, 0, 0)
        cloak_inner = (160, 0, 0)

        base_y = crouch
        pygame.draw.ellipse(surf, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        # Плащ
        cloak = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(
            cloak,
            cloak_outer,
            [(20 + torso_shift, 16 + base_y),
             (26 + cloak_sway, 24 + base_y),
             (14 + cloak_sway, 24 + base_y)],
        )
        pygame.draw.polygon(
            cloak,
            cloak_inner,
            [(20 + torso_shift, 16 + base_y),
             (24 + cloak_sway, 22 + base_y),
             (16 + cloak_sway, 22 + base_y)],
        )
        surf.blit(cloak, (0, 0))

        # Тело
        torso = pygame.Rect(14 + torso_shift, 18 + base_y, 12, 14)
        pygame.draw.ellipse(surf, body, torso)
        pygame.draw.ellipse(surf, body_inner, torso.inflate(-4, -4))

        # Голова
        head = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 20 + torso_shift
        head_y = 8 + base_y + head_tilt
        pygame.draw.ellipse(head, skin, (head_x - 4, head_y, 8, 8))
        pygame.draw.ellipse(head, skin_dark, (head_x - 3, head_y + 1, 6, 5))
        pygame.draw.circle(head, (200, 0, 0), (head_x - 1, head_y + 3), 2)
        pygame.draw.circle(head, (200, 0, 0), (head_x + 1, head_y + 3), 2)
        pygame.draw.circle(head, (255, 100, 100), (head_x - 1, head_y + 3), 1)
        pygame.draw.circle(head, (255, 100, 100), (head_x + 1, head_y + 3), 1)
        # клыки
        pygame.draw.rect(head, (255, 255, 255), (head_x - 2, head_y + 5, 1, 2))
        pygame.draw.rect(head, (255, 255, 255), (head_x + 1, head_y + 5, 1, 2))
        surf.blit(head, (0, 0))

        # Руки
        arms = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.line(
            arms,
            body_inner,
            (20 + torso_shift, 24 + base_y),
            (12 + torso_shift - arm_reach, 34 + base_y),
            3,
        )
        pygame.draw.line(
            arms,
            body_inner,
            (20 + torso_shift, 24 + base_y),
            (28 + torso_shift + arm_reach, 34 + base_y),
            3,
        )
        surf.blit(arms, (0, 0))

        # Ноги
        pygame.draw.rect(surf, body_inner, (16 + leg_back_shift, 30 + base_y, 3, 10))
        pygame.draw.rect(surf, body_inner, (21 + leg_front_shift, 30 + base_y, 3, 10))

        return surf

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, cloak_sway=0, arm_reach=0),
        'IdleBreath': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-1, head_tilt=-1, crouch=0, cloak_sway=1, arm_reach=0),
        'Walk': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=0, crouch=0, cloak_sway=2, arm_reach=1),
        'WalkAlt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=1, head_tilt=0, crouch=0, cloak_sway=-2, arm_reach=-1),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, cloak_sway=-1, arm_reach=-2),
        'AttackStrike': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=2, head_tilt=1, crouch=-1, cloak_sway=3, arm_reach=3),
        'AttackRecover': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, cloak_sway=1, arm_reach=1),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-4, crouch=2, cloak_sway=-2, arm_reach=-1),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-3, head_tilt=5, crouch=5, cloak_sway=0, arm_reach=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-3, head_tilt=5, crouch=6, cloak_sway=0, arm_reach=0),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_lich_texture(animation_state='Idle'):
    """Процедурная анимация лича: парящий маг в мантии с поднятым посохом."""
    cache_key = f'lich_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        float_phase=0,
        staff_angle=0,
        staff_raise=0,
        aura_pulse=0,
    ):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        base_y = -1 + float_phase
        robe = (120, 80, 180)
        robe_dark = (100, 60, 160)
        bone = (235, 240, 245)
        bone_dark = (185, 190, 200)
        glow = (150, 110, 210)

        # Тело
        pygame.draw.ellipse(surf, bone, (10, 8 + base_y, 20, 18))
        pygame.draw.ellipse(surf, bone_dark, (12, 10 + base_y, 16, 14))
        # Лицо
        pygame.draw.ellipse(surf, bone, (14, 10 + base_y, 12, 8))
        pygame.draw.circle(surf, (80, 40, 120), (18, 14 + base_y), 3)
        pygame.draw.circle(surf, (80, 40, 120), (22, 14 + base_y), 3)
        pygame.draw.circle(surf, glow, (18, 14 + base_y), 1)
        pygame.draw.circle(surf, glow, (22, 14 + base_y), 1)

        # Мантия
        pygame.draw.rect(surf, robe, (14, 24 + base_y, 12, 10))
        pygame.draw.rect(surf, robe_dark, (16, 26 + base_y, 8, 6))

        # Посох
        staff = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.line(
            staff,
            (100, 80, 60),
            (26, 12 + base_y + staff_raise),
            (26, 36 + base_y + staff_raise),
            3,
        )
        pygame.draw.circle(staff, glow, (26, 10 + base_y + staff_raise), 4)
        if staff_angle:
            rot = pygame.transform.rotate(staff, staff_angle)
            rect = rot.get_rect(center=(CELL_SIZE // 2 + 4, CELL_SIZE // 2))
            surf.blit(rot, rect.topleft)
        else:
            surf.blit(staff, (0, 0))

        # Аура
        for i in range(2):
            pygame.draw.circle(
                surf,
                (200, 160, 255, 80 - i * 20 + aura_pulse),
                (20, 22 + base_y),
                10 + i * 3,
                1,
            )

        return surf

    params_map = {
        'Idle': dict(float_phase=0, staff_angle=0, staff_raise=0, aura_pulse=0),
        'IdleBreath': dict(float_phase=1, staff_angle=2, staff_raise=-1, aura_pulse=10),
        'Walk': dict(float_phase=2, staff_angle=4, staff_raise=-1, aura_pulse=15),
        'WalkAlt': dict(float_phase=-2, staff_angle=-4, staff_raise=-1, aura_pulse=15),
        'AttackPrep': dict(float_phase=1, staff_angle=-15, staff_raise=-3, aura_pulse=20),
        'AttackStrike': dict(float_phase=-1, staff_angle=10, staff_raise=-4, aura_pulse=30),
        'AttackRecover': dict(float_phase=0, staff_angle=4, staff_raise=-1, aura_pulse=10),
        'Hurt': dict(float_phase=3, staff_angle=8, staff_raise=1, aura_pulse=0),
        'Death': dict(float_phase=4, staff_angle=20, staff_raise=3, aura_pulse=0),
        'Corpse': dict(float_phase=5, staff_angle=20, staff_raise=3, aura_pulse=0),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        fade = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        fade.fill((0, 0, 0, 80))
        surface.blit(fade, (0, 0))
    elif animation_state == 'Corpse':
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(corpse_surface, (180, 160, 210, 150), (8, 22, 24, 10))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface

def load_crossbowman_texture(animation_state='Idle'):
    """Новая генерация профильной текстуры арбалетчика с расширенными кадрами."""
    cache_key = f'crossbowman_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def outlined_rect(target, rect, fill, outline=(35, 28, 20), width=1):
        pygame.draw.rect(target, fill, rect)
        pygame.draw.rect(target, outline, rect, width)

    def gradient_band(target, rect, top_color, bottom_color):
        x, y, w, h = rect
        for i in range(h):
            t = i / max(1, h - 1)
            color = (
                int(top_color[0] + (bottom_color[0] - top_color[0]) * t),
                int(top_color[1] + (bottom_color[1] - top_color[1]) * t),
                int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
            )
            pygame.draw.line(target, color, (x, y + i), (x + w - 1, y + i))

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        crossbow_angle=0,
        crossbow_raise=0,
        head_tilt=0,
        crouch=0,
        show_dagger=False,
        dagger_phase=0,
        lighten=False,
        muzzle_flash=False,
        string_pull=0,
        bolt_visible=True,
        motion_blur=False,
        head_offset_x=0,
        head_offset_y=0,
        crossbow_offset_x=0,
        crossbow_offset_y=0,
        quiver_sway=0,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        crossbow = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        quiver = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (45, 40, 36, 170)
        armor_dark = (110, 108, 104)
        armor_mid = (166, 158, 142)
        armor_light = (208, 200, 184)
        cloth = (90, 112, 162)
        leather_dark = (95, 70, 48)
        leather_mid = (132, 98, 64)
        leather_light = (178, 144, 96)
        boots_dark = (60, 48, 36)
        boots_light = (96, 74, 54)
        skin = (240, 214, 182)
        metal = (210, 210, 218)
        steel = (170, 176, 188)
        visor = (86, 98, 116)
        string = (70, 56, 46)

        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        back_leg_rect = pygame.Rect(12 + leg_back_shift, 24 + base_y, 6, 11)
        front_leg_rect = pygame.Rect(22 + leg_front_shift, 24 + base_y - 1, 7, 12)
        outlined_rect(body, back_leg_rect, boots_dark)
        outlined_rect(body, front_leg_rect, boots_light)

        gradient_band(body, (12, 19 + base_y, 17, 5), leather_mid, leather_dark)
        pygame.draw.rect(body, (42, 34, 26), (12, 19 + base_y, 17, 5), 1)

        torso_rect = pygame.Rect(13 + torso_shift, 10 + base_y, 18, 12)
        gradient_band(body, torso_rect, armor_light, armor_dark)
        pygame.draw.rect(body, (40, 35, 30), torso_rect, 1)
        pygame.draw.rect(body, armor_mid, (13 + torso_shift, 14 + base_y, 18, 3))

        pygame.draw.ellipse(body, armor_mid, (10 + torso_shift, 10 + base_y, 10, 6))
        pygame.draw.ellipse(body, armor_light, (11 + torso_shift, 11 + base_y, 8, 3))
        pygame.draw.rect(body, cloth, (11 + torso_shift, 12 + base_y, 5, 12))
        pygame.draw.rect(body, (40, 35, 30), (11 + torso_shift, 12 + base_y, 5, 12), 1)

        front_arm = pygame.Rect(19 + torso_shift, 14 + base_y, 10, 4)
        back_arm = pygame.Rect(13 + torso_shift, 15 + base_y, 8, 4)
        outlined_rect(body, back_arm, leather_mid)
        outlined_rect(body, front_arm, leather_light)
        pygame.draw.rect(body, metal, (27 + torso_shift, 14 + base_y, 4, 4))

        helmet = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 21 + torso_shift + head_offset_x
        head_y = 6 + base_y + head_tilt + head_offset_y
        crown_rect = (head_x - 9, head_y - 6, 18, 13)
        pygame.draw.ellipse(helmet, armor_mid, crown_rect)
        pygame.draw.ellipse(helmet, armor_dark, crown_rect, 1)
        brow_plate = pygame.Rect(head_x - 8, head_y - 1, 16, 6)
        pygame.draw.rect(helmet, armor_dark, brow_plate)
        pygame.draw.rect(helmet, armor_mid, brow_plate.inflate(-3, -1))
        visor_rect = pygame.Rect(head_x - 7, head_y + 1, 14, 6)
        pygame.draw.rect(helmet, visor, visor_rect)
        slit_rect = visor_rect.inflate(-6, -4)
        slit_rect.height = max(1, slit_rect.height)
        pygame.draw.rect(helmet, steel, slit_rect)
        pygame.draw.rect(helmet, (28, 24, 20), visor_rect, 1)
        nasal = [
            (head_x - 1, head_y + 1),
            (head_x + 1, head_y + 1),
            (head_x + 2, head_y + 8),
            (head_x - 2, head_y + 8),
        ]
        pygame.draw.polygon(helmet, armor_dark, nasal)
        pygame.draw.line(helmet, steel, (head_x, head_y - 3), (head_x, head_y + 7), 1)
        cheek_guard_left = pygame.Rect(head_x - 8, head_y + 2, 3, 8)
        cheek_guard_right = pygame.Rect(head_x + 5, head_y + 2, 3, 8)
        pygame.draw.rect(helmet, armor_mid, cheek_guard_left)
        pygame.draw.rect(helmet, armor_mid, cheek_guard_right)
        pygame.draw.rect(helmet, armor_dark, cheek_guard_left, 1)
        pygame.draw.rect(helmet, armor_dark, cheek_guard_right, 1)
        crest = [
            (head_x, head_y - 6),
            (head_x + 3, head_y - 11),
            (head_x + 5, head_y - 12),
            (head_x + 2, head_y - 7),
        ]
        pygame.draw.polygon(helmet, GOLD, crest)
        pygame.draw.polygon(helmet, (62, 54, 42), crest, 1)
        body.blit(helmet, (0, 0))

        quiver_x = 8 + quiver_sway
        outlined_rect(quiver, pygame.Rect(quiver_x, 12 + base_y, 5, 13), leather_dark)
        pygame.draw.rect(quiver, leather_mid, (quiver_x, 20 + base_y, 5, 4))
        for i in range(3):
            pygame.draw.line(quiver, metal, (quiver_x + 1 + i, 11 + base_y), (quiver_x + 1 + i, 16 + base_y), 1)
            pygame.draw.circle(quiver, metal, (quiver_x + 1 + i, 11 + base_y), 1)

        if show_dagger:
            dagger = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            if dagger_phase == 0:
                pygame.draw.rect(dagger, leather_dark, (20 + torso_shift, 15 + base_y, 2, 6))
                pygame.draw.polygon(dagger, metal, [(21 + torso_shift, 15 + base_y),
                                                    (24 + torso_shift, 16 + base_y),
                                                    (21 + torso_shift, 19 + base_y)])
            elif dagger_phase == 1:
                pygame.draw.rect(dagger, leather_dark, (26 + torso_shift, 14 + base_y, 3, 8))
                pygame.draw.polygon(dagger, metal, [(29 + torso_shift, 15 + base_y),
                                                    (35 + torso_shift, 13 + base_y),
                                                    (30 + torso_shift, 19 + base_y)])
            else:
                pygame.draw.rect(dagger, leather_dark, (23 + torso_shift, 14 + base_y, 2, 7))
                pygame.draw.polygon(dagger, metal, [(24 + torso_shift, 14 + base_y),
                                                    (27 + torso_shift, 15 + base_y),
                                                    (24 + torso_shift, 18 + base_y)])
            body.blit(dagger, (0, 0))

        stock_rect = pygame.Rect(18, 18 + crossbow_raise + base_y, 16, 4)
        pygame.draw.rect(crossbow, leather_dark, stock_rect)
        pygame.draw.rect(crossbow, (40, 30, 20), stock_rect, 1)
        pygame.draw.rect(crossbow, metal, (24, 14 + crossbow_raise + base_y, 4, 8))
        pygame.draw.rect(crossbow, (50, 40, 30), (24, 14 + crossbow_raise + base_y, 4, 8), 1)
        pygame.draw.rect(crossbow, GOLD, (22, 20 + crossbow_raise + base_y, 8, 2))
        pygame.draw.polygon(
            crossbow,
            metal,
            [
                (24, 15 + crossbow_raise + base_y),
                (28, 15 + crossbow_raise + base_y),
                (30, 18 + crossbow_raise + base_y),
                (22, 18 + crossbow_raise + base_y),
            ],
        )
        pygame.draw.rect(crossbow, metal, (25, 17 + crossbow_raise + base_y, 2, 4))
        pygame.draw.rect(crossbow, (80, 65, 45), (24, 17 + crossbow_raise + base_y, 4, 1))
        pygame.draw.rect(crossbow, metal, (28, 17 + crossbow_raise + base_y, 2, 6))

        string_base_y = 19 + crossbow_raise + base_y
        pull = max(-4, min(6, string_pull))
        mid_y = string_base_y - int(pull * 1.3)
        left_anchor = (19, string_base_y)
        right_anchor = (33, string_base_y)
        pygame.draw.line(crossbow, string, left_anchor, (26, mid_y), 2)
        pygame.draw.line(crossbow, string, (26, mid_y), right_anchor, 2)

        if bolt_visible:
            bolt_rect = pygame.Rect(23, string_base_y - 2, 7, 3)
            pygame.draw.rect(crossbow, (142, 108, 70), bolt_rect)
            pygame.draw.rect(crossbow, (64, 48, 32), bolt_rect, 1)

        body.blit(quiver, (0, 0))
        final_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        final_surface.blit(body, (0, 0))

        if crossbow_angle != 0:
            cb_rotated = pygame.transform.rotate(crossbow, crossbow_angle)
            cb_rect = cb_rotated.get_rect(
                center=(
                    CELL_SIZE // 2 + 6 + crossbow_offset_x,
                    CELL_SIZE // 2 - 4 + crossbow_raise + crossbow_offset_y,
                )
            )
            final_surface.blit(cb_rotated, cb_rect.topleft)
        else:
            final_surface.blit(crossbow, (crossbow_offset_x, crossbow_offset_y))

        if lighten:
            wash = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            wash.fill((255, 240, 200, 70))
            final_surface.blit(wash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        if motion_blur:
            blur = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.ellipse(
                blur,
                (255, 220, 160, 70),
                (16 + crossbow_offset_x, 14 + crossbow_raise + base_y + crossbow_offset_y, 24, 10),
            )
            final_surface.blit(blur, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        if muzzle_flash:
            flash = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            tip_x = 34 + crossbow_offset_x
            tip_y = 17 + crossbow_raise + base_y + crossbow_offset_y
            pygame.draw.circle(flash, (255, 240, 200, 210), (tip_x, tip_y), 5)
            pygame.draw.circle(flash, (255, 170, 60, 170), (tip_x + 3, tip_y - 1), 8, 2)
            final_surface.blit(flash, (0, 0))

        return final_surface

    attack_draw = dict(
        torso_shift=-3,
        crossbow_angle=-24,
        crossbow_raise=-5,
        head_tilt=-3,
        string_pull=6,
        crossbow_offset_x=-1,
        crossbow_offset_y=-1,
    )
    attack_aim = dict(
        torso_shift=-2,
        crossbow_angle=-8,
        crossbow_raise=-3,
        head_tilt=-1,
        string_pull=6,
        head_offset_x=-1,
        head_offset_y=-1,
    )
    attack_release = dict(
        torso_shift=-1,
        crossbow_angle=10,
        crossbow_raise=2,
        head_tilt=0,
        string_pull=-3,
        bolt_visible=False,
        motion_blur=False,
        muzzle_flash=False,
    )
    attack_follow = dict(
        torso_shift=0,
        crossbow_angle=18,
        crossbow_raise=4,
        head_tilt=1,
        string_pull=-3,
        bolt_visible=False,
        motion_blur=False,
        crossbow_offset_x=2,
        crossbow_offset_y=1,
    )
    attack_recover = dict(
        torso_shift=-1,
        crossbow_angle=-6,
        crossbow_raise=-1,
        head_tilt=0,
        string_pull=2,
        bolt_visible=False,
    )

    melee_guard = dict(
        torso_shift=-3,
        crossbow_angle=-14,
        crossbow_raise=6,
        head_tilt=-2,
        show_dagger=True,
        dagger_phase=0,
        string_pull=2,
        bolt_visible=False,
        quiver_sway=-1,
    )
    melee_windup = dict(
        torso_shift=-2,
        crossbow_angle=4,
        crossbow_raise=7,
        head_tilt=0,
        show_dagger=True,
        dagger_phase=1,
        string_pull=2,
        bolt_visible=False,
        motion_blur=True,
    )
    melee_strike = dict(
        torso_shift=-1,
        crossbow_angle=18,
        crossbow_raise=6,
        head_tilt=1,
        show_dagger=True,
        dagger_phase=1,
        string_pull=-3,
        bolt_visible=False,
        motion_blur=True,
        crossbow_offset_x=2,
    )
    melee_follow = dict(
        torso_shift=-1,
        crossbow_angle=10,
        crossbow_raise=4,
        head_tilt=0,
        show_dagger=True,
        dagger_phase=2,
        string_pull=-2,
        bolt_visible=False,
    )
    melee_recover = dict(
        torso_shift=-2,
        crossbow_angle=-6,
        crossbow_raise=2,
        head_tilt=-1,
        show_dagger=True,
        dagger_phase=2,
        string_pull=1,
        bolt_visible=False,
    )

    hurt_start = dict(
        torso_shift=-3,
        crouch=3,
        crossbow_angle=-6,
        crossbow_raise=3,
        head_tilt=-4,
        string_pull=1,
        bolt_visible=True,
        head_offset_x=-1,
    )
    hurt_hold = dict(
        torso_shift=-2,
        crouch=4,
        crossbow_angle=0,
        crossbow_raise=4,
        head_tilt=-3,
        string_pull=0,
        bolt_visible=False,
    )
    hurt_recover = dict(
        torso_shift=-1,
        crouch=2,
        crossbow_angle=-4,
        crossbow_raise=1,
        head_tilt=-1,
        string_pull=1,
        bolt_visible=False,
    )

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=-1, torso_shift=0, crossbow_angle=-6, crossbow_raise=-1, head_tilt=0, string_pull=1),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-2, torso_shift=-1, crossbow_angle=-4, crossbow_raise=-2, head_tilt=-1, string_pull=2, head_offset_y=-1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-3, torso_shift=-1, crossbow_angle=-4, crossbow_raise=-1, head_tilt=-1, string_pull=0),
        'WalkAlt': dict(leg_front_shift=-1, leg_back_shift=2, torso_shift=1, crossbow_angle=-2, crossbow_raise=0, head_tilt=1, string_pull=0),
        'Attack': attack_draw,
        'AttackDraw': attack_draw,
        'Attack02': attack_aim,
        'AttackAim': attack_aim,
        'Attack03': attack_release,
        'AttackRelease': attack_release,
        'AttackFollow': attack_follow,
        'AttackRecover': attack_recover,
        'MeleePrep': melee_guard,
        'MeleeGuard': melee_guard,
        'MeleeWindup': melee_windup,
        'MeleeStrike': melee_strike,
        'MeleeFollow': melee_follow,
        'MeleeRecover': melee_recover,
        'Hurt': hurt_start,
        'HurtStart': hurt_start,
        'HurtHold': hurt_hold,
        'HurtRecover': hurt_recover,
        'Death': dict(torso_shift=-3, crouch=5, crossbow_angle=20, crossbow_raise=6, head_tilt=6, string_pull=-2, bolt_visible=False, motion_blur=False, lighten=True),
        'Corpse': dict(torso_shift=-3, crouch=6, crossbow_angle=22, crossbow_raise=6, head_tilt=6, string_pull=-2, bolt_visible=False),
    }

    params = params_map.get(animation_state, params_map['Idle'])
    surface = build_pose(**params)

    if animation_state == 'Hurt':
        overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((255, 90, 90, 130))
        surface.blit(overlay, (0, 0))
    elif animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 70)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-6, 10))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 88)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 6))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_peasant_texture(animation_state='Idle'):
    cache_key = f'peasant_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        arm_raise=0,
        tool_angle=90,
        tool_raise=0,
        tool_reach=0,
        bag_sway=0,
        idle_sash=False,
        motion_blur=False,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pitchfork = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        sack = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (42, 38, 32, 165)
        shirt_light = (216, 204, 180)
        shirt_shadow = (184, 170, 150)
        pants = (96, 92, 84)
        sash = (162, 98, 54)
        sash_dark = (130, 74, 44)
        skin = (235, 210, 190)
        hair = (102, 68, 42)
        boots = (70, 52, 40)
        boots_light = (92, 70, 54)
        wood = (160, 120, 72)
        iron = (170, 176, 186)

        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        back_leg = pygame.Rect(12 + leg_back_shift, 25 + base_y, 6, 11)
        front_leg = pygame.Rect(23 + leg_front_shift, 24 + base_y, 7, 12)
        pygame.draw.rect(body, boots, back_leg)
        pygame.draw.rect(body, (48, 38, 28), back_leg, 1)
        pygame.draw.rect(body, boots_light, front_leg)
        pygame.draw.rect(body, (48, 38, 28), front_leg, 1)

        pants_rect = pygame.Rect(12 + torso_shift, 21 + base_y, 19, 6)
        pygame.draw.rect(body, pants, pants_rect)
        pygame.draw.rect(body, (48, 40, 34), pants_rect, 1)

        torso_rect = pygame.Rect(13 + torso_shift, 11 + base_y, 17, 11)
        pygame.draw.rect(body, shirt_light, torso_rect)
        pygame.draw.rect(body, (98, 88, 74), torso_rect, 1)
        pygame.draw.rect(body, shirt_shadow, torso_rect.inflate(-2, -2))

        if idle_sash:
            sash_rect = pygame.Rect(12 + torso_shift, 17 + base_y, 19, 4)
            pygame.draw.rect(body, sash, sash_rect)
            pygame.draw.rect(body, sash_dark, sash_rect, 1)

        back_arm = pygame.Rect(12 + torso_shift, 14 + base_y, 5, 4)
        front_arm = pygame.Rect(23 + torso_shift, 13 + base_y - arm_raise, 5, 5)
        pygame.draw.rect(body, shirt_shadow, back_arm)
        pygame.draw.rect(body, (96, 84, 70), back_arm, 1)
        pygame.draw.rect(body, shirt_light, front_arm)
        pygame.draw.rect(body, (96, 84, 70), front_arm, 1)

        head = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(head, skin, (head_x - 6, head_y, 12, 12))
        pygame.draw.ellipse(head, hair, (head_x - 7, head_y - 1, 14, 6))
        pygame.draw.rect(head, hair, (head_x - 7, head_y + 3, 14, 4), 1)
        pygame.draw.rect(head, (60, 46, 36), (head_x - 2, head_y + 5, 5, 1))
        pygame.draw.rect(head, (60, 46, 36), (head_x - 2, head_y + 7, 4, 1))
        pygame.draw.polygon(head, hair, [(head_x - 6, head_y + 10), (head_x - 3, head_y + 12), (head_x - 6, head_y + 12)])
        body.blit(head, (0, 0))

        sack_rect = pygame.Rect(9 + bag_sway, 14 + base_y, 7, 9)
        pygame.draw.ellipse(sack, (186, 162, 126), sack_rect)
        pygame.draw.ellipse(sack, (150, 130, 102), sack_rect, 1)
        pygame.draw.rect(sack, (150, 130, 102), (sack_rect.x + 2, sack_rect.y + 1, sack_rect.width - 4, 2))
        body.blit(sack, (0, 0))

        shaft_start = (26 + tool_reach // 2, 16 + base_y + tool_raise)
        angle_rad = math.radians(tool_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        for offset in range(-1, 2):
            start = (shaft_start[0] + offset, shaft_start[1])
            end = (start[0] + int(20 * cos_a), start[1] + int(-20 * sin_a))
            pygame.draw.line(pitchfork, wood, start, end, 2 if offset == 0 else 1)
        tine_origin = (shaft_start[0] + int(20 * cos_a), shaft_start[1] + int(-20 * sin_a))
        for i in range(-2, 3):
            tine = (tine_origin[0] + int(i * 2.5), tine_origin[1] - 6)
            pygame.draw.line(pitchfork, iron, tine_origin, tine, 2)
        pygame.draw.circle(pitchfork, iron, tine_origin, 3)
        body.blit(pitchfork, (0, 0))

        if motion_blur:
            blur = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.ellipse(
                blur,
                (220, 210, 180, 70),
                (shaft_start[0] - 14, shaft_start[1] - 8, 24, 10),
            )
            body.blit(blur, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return body

    params_map = {
        'Idle': dict(),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, bag_sway=-1, idle_sash=True),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=-1, bag_sway=-1, tool_angle=96, tool_reach=2),
        'WalkAlt': dict(leg_front_shift=-1, leg_back_shift=2, torso_shift=1, head_tilt=1, bag_sway=1, tool_angle=84, tool_reach=2),
        'AttackWindup': dict(torso_shift=-2, head_tilt=-3, arm_raise=2, tool_angle=60, tool_raise=4, tool_reach=4),
        'AttackStrike': dict(torso_shift=-1, head_tilt=0, arm_raise=4, tool_angle=12, tool_raise=-4, tool_reach=12, motion_blur=True),
        'AttackRecover': dict(torso_shift=-2, head_tilt=-1, arm_raise=1, tool_angle=78, tool_raise=2, tool_reach=6),
        'HurtStart': dict(crouch=3, head_tilt=-4, torso_shift=-3, tool_angle=-40, tool_raise=4),
        'HurtHold': dict(crouch=4, head_tilt=-2, torso_shift=-2, tool_angle=-12, tool_raise=8),
        'HurtRecover': dict(crouch=2, head_tilt=-1, torso_shift=-2, tool_angle=-20, tool_raise=2),
        'Death': dict(crouch=6, torso_shift=-4, head_tilt=6, tool_angle=70, tool_raise=10, motion_blur=False),
        'Corpse': dict(crouch=6, torso_shift=-4, head_tilt=6, tool_angle=90, tool_raise=10, motion_blur=False),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 82)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 4))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 92)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 8))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_spearman_texture(animation_state='Idle'):
    cache_key = f'spearman_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        shield_angle=0,
        shield_raise=0,
        spear_angle=-6,
        spear_raise=0,
        spear_reach=0,
        motion_blur=False,
        brace=False,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        spear = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shield = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (40, 38, 32, 170)
        armor_dark = (118, 116, 108)
        armor_mid = (164, 158, 144)
        armor_light = (206, 198, 182)
        cloth = (84, 104, 156)
        leather = (108, 82, 56)
        leather_dark = (86, 62, 44)
        skin = (232, 208, 184)
        metal = (182, 186, 198)
        bronze = (184, 140, 72)

        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        back_leg = pygame.Rect(12 + leg_back_shift, 24 + base_y, 6, 12)
        front_leg = pygame.Rect(22 + leg_front_shift, 23 + base_y, 8, 13)
        pygame.draw.rect(body, leather_dark, back_leg)
        pygame.draw.rect(body, (40, 32, 26), back_leg, 1)
        pygame.draw.rect(body, leather, front_leg)
        pygame.draw.rect(body, (40, 32, 26), front_leg, 1)

        waist_rect = pygame.Rect(12 + torso_shift, 19 + base_y, 19, 6)
        pygame.draw.rect(body, cloth, waist_rect)
        pygame.draw.rect(body, (40, 32, 28), waist_rect, 1)
        pygame.draw.rect(body, armor_mid, waist_rect.inflate(-6, -2))

        torso_rect = pygame.Rect(13 + torso_shift, 11 + base_y, 18, 10)
        pygame.draw.rect(body, armor_light, torso_rect)
        pygame.draw.rect(body, (54, 44, 36), torso_rect, 1)
        pygame.draw.rect(body, armor_mid, torso_rect.inflate(-2, -2))

        pauldrons = pygame.Rect(11 + torso_shift, 10 + base_y, 10, 5)
        pygame.draw.ellipse(body, armor_dark, pauldrons)
        pygame.draw.ellipse(body, armor_light, (pauldrons[0] + 1, pauldrons[1] + 1, pauldrons[2] - 2, pauldrons[3] - 2))

        head = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 23 + torso_shift
        head_y = 5 + base_y + head_tilt
        pygame.draw.ellipse(head, armor_mid, (head_x - 7, head_y, 14, 12))
        pygame.draw.rect(head, armor_dark, (head_x - 7, head_y + 4, 14, 6), 1)
        pygame.draw.rect(head, metal, (head_x - 4, head_y + 5, 8, 2))
        pygame.draw.rect(head, (48, 40, 32), (head_x - 2, head_y + 7, 4, 1))
        pygame.draw.rect(head, skin, (head_x - 2, head_y + 8, 5, 3))
        pygame.draw.polygon(head, bronze, [(head_x, head_y - 2), (head_x + 3, head_y - 5), (head_x + 4, head_y - 2)])
        body.blit(head, (0, 0))

        front_arm = pygame.Rect(22 + torso_shift, 14 + base_y, 9, 4)
        back_arm = pygame.Rect(13 + torso_shift, 15 + base_y, 7, 4)
        pygame.draw.rect(body, armor_mid, back_arm)
        pygame.draw.rect(body, (50, 42, 34), back_arm, 1)
        pygame.draw.rect(body, armor_light, front_arm)
        pygame.draw.rect(body, (50, 42, 34), front_arm, 1)

        shield_center = (15 + torso_shift, 20 + base_y - shield_raise)
        pygame.draw.circle(shield, armor_dark, shield_center, 10)
        pygame.draw.circle(shield, armor_light, shield_center, 8)
        pygame.draw.circle(shield, bronze, shield_center, 3)
        if shield_angle:
            shield = pygame.transform.rotate(shield, shield_angle)
        body.blit(shield, shield.get_rect(center=shield_center))

        spear_start = (26, 16 + base_y + spear_raise)
        angle_rad = math.radians(spear_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        spear_length = 22 + spear_reach
        spear_end = (spear_start[0] + int(spear_length * cos_a), spear_start[1] - int(spear_length * sin_a))
        pygame.draw.line(spear, (142, 110, 60), spear_start, spear_end, 3)
        pygame.draw.line(spear, (96, 72, 44), spear_start, spear_end, 1)
        spear_tip = [
            (spear_end[0], spear_end[1]),
            (spear_end[0] + int(6 * math.cos(angle_rad + math.pi / 2)), spear_end[1] - int(6 * math.sin(angle_rad + math.pi / 2))),
            (spear_end[0] + int(12 * cos_a), spear_end[1] - int(12 * sin_a)),
        ]
        pygame.draw.polygon(spear, metal, spear_tip)
        pygame.draw.polygon(spear, (90, 96, 110), spear_tip, 1)
        body.blit(spear, (0, 0))

        if brace:
            brace_block = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(
                brace_block,
                (200, 200, 210, 60),
                (spear_start[0] - 8, spear_start[1] - 6, 18, 8),
            )
            body.blit(brace_block, (0, 0))

        if motion_blur:
            blur = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.ellipse(
                blur,
                (210, 210, 220, 70),
                (spear_start[0] - 10, spear_start[1] - 6, 26, 10),
            )
            body.blit(blur, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return body

    params_map = {
        'Idle': dict(spear_angle=92, spear_raise=0, spear_reach=2),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-2, torso_shift=-1, head_tilt=-1, spear_angle=96, spear_raise=1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-3, torso_shift=-1, head_tilt=-1, spear_angle=100, spear_raise=2, spear_reach=3),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=1, spear_angle=88, spear_raise=1, spear_reach=2),
        'AttackPrep': dict(torso_shift=-2, head_tilt=-2, spear_angle=46, spear_raise=6, spear_reach=6, shield_angle=12, brace=True),
        'AttackThrust': dict(torso_shift=0, head_tilt=0, spear_angle=12, spear_raise=-2, spear_reach=12, motion_blur=True, shield_angle=-6),
        'AttackRecover': dict(torso_shift=-1, head_tilt=-1, spear_angle=82, spear_raise=4, spear_reach=4, shield_angle=8),
        'HurtStart': dict(crouch=3, torso_shift=-3, head_tilt=-4, spear_angle=70, spear_raise=8, shield_raise=2),
        'HurtHold': dict(crouch=4, torso_shift=-2, head_tilt=-2, spear_angle=96, spear_raise=6, shield_raise=4),
        'HurtRecover': dict(crouch=2, torso_shift=-1, head_tilt=-1, spear_angle=86, spear_raise=4, shield_raise=2),
        'Death': dict(crouch=6, torso_shift=-4, head_tilt=5, spear_angle=62, spear_raise=10, shield_angle=-24),
        'Corpse': dict(crouch=6, torso_shift=-4, head_tilt=5, spear_angle=94, spear_raise=8, shield_angle=-32),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 76)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-9, 6))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 94)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-13, 10))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_swordsman_texture(animation_state='Idle'):
    cache_key = f'swordsman_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        sword_angle=0,
        sword_raise=0,
        sword_reach=0,
        shield_tilt=0,
        shield_raise=0,
        cloak_sway=0,
        motion_blur=False,
        guard=False,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        sword = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shield = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        cloak = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (38, 34, 30, 170)
        armor_dark = (120, 118, 110)
        armor_mid = (170, 164, 150)
        armor_light = (210, 202, 190)
        cloth = (68, 88, 138)
        leather = (96, 74, 52)
        leather_dark = (80, 60, 44)
        skin = (232, 208, 184)
        metal = (190, 194, 206)
        steel = (220, 224, 234)
        trim = (112, 172, 200)

        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        back_leg = pygame.Rect(11 + leg_back_shift, 24 + base_y, 7, 12)
        front_leg = pygame.Rect(22 + leg_front_shift, 23 + base_y, 8, 13)
        pygame.draw.rect(body, leather_dark, back_leg)
        pygame.draw.rect(body, (40, 32, 24), back_leg, 1)
        pygame.draw.rect(body, leather, front_leg)
        pygame.draw.rect(body, (40, 32, 24), front_leg, 1)

        skirt_rect = pygame.Rect(12 + torso_shift, 19 + base_y, 19, 7)
        pygame.draw.rect(body, cloth, skirt_rect)
        pygame.draw.rect(body, (36, 30, 26), skirt_rect, 1)
        pygame.draw.rect(body, armor_mid, skirt_rect.inflate(-6, -2))

        torso_rect = pygame.Rect(13 + torso_shift, 11 + base_y, 18, 10)
        pygame.draw.rect(body, armor_light, torso_rect)
        pygame.draw.rect(body, (50, 42, 34), torso_rect, 1)
        pygame.draw.rect(body, armor_mid, torso_rect.inflate(-3, -2))
        pygame.draw.rect(body, trim, (torso_rect[0] + 7, torso_rect[1] + 1, 4, torso_rect[3] - 2))

        pygame.draw.ellipse(body, armor_dark, (11 + torso_shift, 10 + base_y, 10, 5))
        pygame.draw.ellipse(body, armor_light, (12 + torso_shift, 11 + base_y, 8, 3))

        cloak_rect = pygame.Rect(9 + cloak_sway, 12 + base_y, 22, 18)
        pygame.draw.ellipse(cloak, (46, 60, 90, 150), cloak_rect)
        body.blit(cloak, (0, 0))

        head = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 23 + torso_shift
        head_y = 5 + base_y + head_tilt
        pygame.draw.ellipse(head, armor_mid, (head_x - 7, head_y, 14, 12))
        pygame.draw.rect(head, armor_dark, (head_x - 7, head_y + 4, 14, 6), 1)
        pygame.draw.rect(head, steel, (head_x - 3, head_y + 5, 6, 2))
        pygame.draw.rect(head, skin, (head_x - 2, head_y + 8, 4, 3))
        pygame.draw.rect(head, (42, 34, 28), (head_x - 2, head_y + 6, 4, 1))
        pygame.draw.polygon(head, trim, [(head_x, head_y - 3), (head_x + 2, head_y - 6), (head_x + 4, head_y - 3)])
        body.blit(head, (0, 0))

        front_arm = pygame.Rect(22 + torso_shift, 14 + base_y, 8, 4)
        back_arm = pygame.Rect(13 + torso_shift, 15 + base_y, 7, 4)
        pygame.draw.rect(body, armor_mid, back_arm)
        pygame.draw.rect(body, (44, 36, 30), back_arm, 1)
        pygame.draw.rect(body, armor_light, front_arm)
        pygame.draw.rect(body, (44, 36, 30), front_arm, 1)

        shield_center = (15 + torso_shift, 20 + base_y - shield_raise)
        pygame.draw.polygon(
            shield,
            armor_dark,
            [
                (shield_center[0] - 9, shield_center[1]),
                (shield_center[0], shield_center[1] - 12),
                (shield_center[0] + 9, shield_center[1]),
                (shield_center[0], shield_center[1] + 10),
            ],
        )
        pygame.draw.polygon(
            shield,
            armor_light,
            [
                (shield_center[0] - 7, shield_center[1]),
                (shield_center[0], shield_center[1] - 10),
                (shield_center[0] + 7, shield_center[1]),
                (shield_center[0], shield_center[1] + 8),
            ],
        )
        pygame.draw.polygon(
            shield,
            trim,
            [
                (shield_center[0] - 2, shield_center[1] - 2),
                (shield_center[0], shield_center[1] - 6),
                (shield_center[0] + 2, shield_center[1] - 2),
                (shield_center[0], shield_center[1] + 1),
            ],
        )
        if shield_tilt:
            shield = pygame.transform.rotate(shield, shield_tilt)
        body.blit(shield, shield.get_rect(center=shield_center))

        sword_start = (27, 16 + base_y + sword_raise)
        angle_rad = math.radians(sword_angle)
        sword_length = 18 + sword_reach
        sword_end = (
            sword_start[0] + int(sword_length * math.cos(angle_rad)),
            sword_start[1] - int(sword_length * math.sin(angle_rad)),
        )
        pygame.draw.line(sword, (88, 70, 52), sword_start, sword_end, 4)
        pygame.draw.line(sword, (58, 44, 36), sword_start, sword_end, 1)
        guard_rect = pygame.Rect(sword_start[0] - 2, sword_start[1] - 1, 6, 3)
        pygame.draw.rect(sword, metal, guard_rect)
        pygame.draw.rect(sword, (96, 96, 104), guard_rect, 1)
        blade_end = (
            sword_end[0] + int(8 * math.cos(angle_rad)),
            sword_end[1] - int(8 * math.sin(angle_rad)),
        )
        pygame.draw.line(sword, steel, sword_end, blade_end, 3)
        pygame.draw.line(sword, (120, 130, 150), sword_end, blade_end, 1)
        body.blit(sword, (0, 0))

        if motion_blur:
            blur = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.ellipse(
                blur,
                (220, 225, 240, 80),
                (sword_start[0] - 12, sword_start[1] - 8, 26, 12),
            )
            body.blit(blur, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return body

    params_map = {
        'Idle': dict(sword_angle=94, sword_raise=0, sword_reach=2, shield_tilt=4),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-2, torso_shift=-1, head_tilt=-1, shield_tilt=8, cloak_sway=-2, sword_angle=98, sword_raise=1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-3, torso_shift=-1, head_tilt=-1, sword_angle=104, sword_raise=2, sword_reach=3, cloak_sway=-4),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=1, torso_shift=1, head_tilt=1, sword_angle=86, sword_raise=1, sword_reach=3, cloak_sway=6),
        'AttackPrep': dict(torso_shift=-3, head_tilt=-2, sword_angle=48, sword_raise=6, sword_reach=6, shield_tilt=14),
        'AttackSlash': dict(torso_shift=-1, head_tilt=0, sword_angle=32, sword_raise=-3, sword_reach=10, motion_blur=True, shield_tilt=-6),
        'AttackRecover': dict(torso_shift=-2, head_tilt=-1, sword_angle=88, sword_raise=3, sword_reach=4, shield_tilt=6),
        'Block': dict(torso_shift=-2, head_tilt=-1, sword_angle=84, sword_raise=4, shield_tilt=18),
        'HurtStart': dict(crouch=3, torso_shift=-3, head_tilt=-4, sword_angle=70, sword_raise=5, shield_raise=2),
        'HurtHold': dict(crouch=4, torso_shift=-2, head_tilt=-3, sword_angle=94, sword_raise=6, shield_raise=4),
        'HurtRecover': dict(crouch=2, torso_shift=-1, head_tilt=-1, sword_angle=86, sword_raise=3),
        'Death': dict(crouch=6, torso_shift=-4, head_tilt=6, sword_angle=74, sword_raise=8, shield_tilt=-20),
        'Corpse': dict(crouch=6, torso_shift=-4, head_tilt=6, sword_angle=98, sword_raise=8, shield_tilt=-30),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 78)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 4))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 96)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-14, 8))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_gryphon_texture(animation_state='Idle'):
    cache_key = f'gryphon_v3_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        body_shift=0,
        head_tilt=0,
        wing_angle=0,
        wing_raise=0,
        claw_reach=0,
        tail_sway=0,
        crouch=0,
        beak_open=False,
        motion_blur=False,
    ):
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (32, 30, 28, 170)
        feather_dark = (88, 78, 64)
        feather_mid = (152, 138, 118)
        feather_light = (204, 192, 170)
        fur_dark = (96, 68, 44)
        fur_light = (158, 118, 70)
        beak_color = (210, 160, 70)
        eye_color = (220, 228, 240)
        claw_color = (230, 220, 210)
        tail_color = (98, 80, 58)

        base_y = crouch
        ground = CELL_SIZE - 8 + base_y
        center_x = CELL_SIZE // 2 + body_shift

        pygame.draw.ellipse(surface, shadow, (center_x - 22, ground - 2, 44, 6))

        body_rect = pygame.Rect(center_x - 10, ground - 22, 20, 14)
        pygame.draw.ellipse(surface, feather_mid, body_rect)
        pygame.draw.ellipse(surface, feather_dark, body_rect, 1)
        pygame.draw.ellipse(surface, feather_light, (body_rect.x + 4, body_rect.y + 3, body_rect.width - 8, body_rect.height - 8))

        tail_points = [
            (center_x - 10, ground - 16),
            (center_x - 20 + tail_sway, ground - 6),
            (center_x - 6, ground - 4),
        ]
        pygame.draw.polygon(surface, tail_color, tail_points)
        pygame.draw.polygon(surface, (60, 50, 42), tail_points, 1)

        back_leg = pygame.Rect(center_x - 14 + leg_back_shift, ground - 6, 6, 10)
        front_leg = pygame.Rect(center_x + 6 + leg_front_shift, ground - 8 - claw_reach, 6, 12 + claw_reach)
        pygame.draw.rect(surface, fur_dark, back_leg)
        pygame.draw.rect(surface, (44, 32, 24), back_leg, 1)
        pygame.draw.rect(surface, fur_light, front_leg)
        pygame.draw.rect(surface, (44, 32, 24), front_leg, 1)

        upper_leg = pygame.Rect(center_x + 2 + leg_front_shift, ground - 14 - claw_reach, 8, 6)
        pygame.draw.rect(surface, fur_dark, upper_leg)
        pygame.draw.rect(surface, (44, 34, 26), upper_leg, 1)

        claw = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        claw_x = center_x + 10 + leg_front_shift
        claw_y = ground - 2 - claw_reach
        claw_shape = [
            (claw_x, claw_y),
            (claw_x + 8, claw_y - 6),
            (claw_x + 12, claw_y),
            (claw_x + 8, claw_y + 6),
            (claw_x - 2, claw_y + 4),
        ]
        pygame.draw.polygon(claw, claw_color, claw_shape)
        pygame.draw.polygon(claw, (182, 172, 170), claw_shape, 1)
        talons = [
            [(claw_x + 6, claw_y - 4), (claw_x + 14, claw_y - 10), (claw_x + 12, claw_y)],
            [(claw_x + 4, claw_y + 2), (claw_x + 12, claw_y + 4), (claw_x + 6, claw_y + 9)],
        ]
        for talon in talons:
            pygame.draw.polygon(claw, (210, 200, 190), talon)
            pygame.draw.polygon(claw, (150, 140, 140), talon, 1)
        surface.blit(claw, (0, 0))

        wing = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shoulder_y = body_rect.top + 4 - wing_raise
        left_wing_points = [
            (center_x - 6, shoulder_y),
            (center_x - 18, shoulder_y - 10),
            (center_x - 22, shoulder_y + 2),
            (center_x - 18, shoulder_y + 8),
            (center_x - 8, shoulder_y + 4),
        ]
        pygame.draw.polygon(wing, feather_light, left_wing_points)
        pygame.draw.polygon(wing, feather_dark, left_wing_points, 1)
        for i in range(4):
            t = i / 3.0
            fx = int(center_x - 6 - 12 * t)
            pygame.draw.line(wing, feather_dark, (fx, shoulder_y - int(10 * t)), (fx - 2, shoulder_y + 6), 1)
        if wing_angle:
            wing = pygame.transform.rotate(wing, wing_angle)
        surface.blit(wing, (0, 0))
        right_wing = pygame.transform.flip(wing, True, False)
        surface.blit(right_wing, (0, 0))

        neck_rect = pygame.Rect(center_x - 4, body_rect.top - 6 - head_tilt, 10, 14)
        pygame.draw.ellipse(surface, feather_light, neck_rect)
        pygame.draw.ellipse(surface, feather_dark, neck_rect, 1)

        head = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = center_x + 6
        head_y = body_rect.top - 4 - head_tilt
        pygame.draw.ellipse(head, feather_light, (head_x - 6, head_y, 12, 9))
        pygame.draw.ellipse(head, feather_dark, (head_x - 6, head_y, 12, 9), 1)
        eye_center = (head_x + 1, head_y + 4)
        pygame.draw.circle(head, eye_color, eye_center, 2)
        pygame.draw.circle(head, (30, 40, 60), eye_center, 1)
        beak = [
            (head_x + 3, head_y + 3),
            (head_x + 10, head_y + (0 if beak_open else 3)),
            (head_x + 3, head_y + 5),
        ]
        pygame.draw.polygon(head, beak_color, beak)
        pygame.draw.line(head, (160, 120, 50), (head_x + 3, head_y + 3), (head_x + 10, head_y + (0 if beak_open else 3)), 2)
        surface.blit(head, (0, 0))

        if motion_blur:
            blur = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.ellipse(blur, (220, 210, 200, 70), (claw_x - 14, claw_y - 10, 26, 14))
            surface.blit(blur, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return surface

    params_map = {
        'Idle': dict(wing_angle=-2, tail_sway=-1),
        'IdleBreath': dict(wing_angle=-6, head_tilt=-2, tail_sway=-2),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, claw_reach=3, body_shift=-1, tail_sway=-3),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, claw_reach=2, body_shift=1, tail_sway=3),
        'AttackClaw': dict(claw_reach=7, head_tilt=-2, motion_blur=True, body_shift=2, wing_angle=8),
        'AttackBeak': dict(head_tilt=-6, beak_open=True, claw_reach=4, wing_angle=-4),
        'AttackWing': dict(wing_angle=26, wing_raise=6, motion_blur=True),
        'HurtStart': dict(crouch=4, body_shift=-3, head_tilt=-6, wing_angle=-18),
        'HurtHold': dict(crouch=6, body_shift=-2, head_tilt=-4, wing_angle=-12),
        'HurtRecover': dict(crouch=3, body_shift=-1, head_tilt=-2, wing_angle=-8),
        'Death': dict(crouch=8, body_shift=-4, head_tilt=8, wing_angle=36, claw_reach=4),
        'Corpse': dict(crouch=8, body_shift=-4, head_tilt=8, wing_angle=48, claw_reach=4),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 84)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-16, 4))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 102)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-20, 8))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def _render_human_hero(hero_class):
    """Детализированная текстура героя людей с понятной структурой тела."""
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    armor_base = (196, 188, 172)
    armor_mid = (160, 152, 136)
    armor_shadow = (112, 102, 90)
    cloth_primary = (88, 112, 168)
    cloth_dark = (68, 88, 132)
    gold = (218, 192, 96)
    skin = (238, 216, 192)
    skin_shadow = (210, 190, 168)
    leather = (110, 84, 52)
    leather_dark = (90, 68, 42)

    # Тень
    pygame.draw.ellipse(surf, (38, 34, 28, 160), (6, CELL_SIZE - 8, CELL_SIZE - 12, 6))

    # Ноги - отдельно видимые
    left_leg = pygame.Rect(14, 24, 7, 12)
    right_leg = pygame.Rect(28, 24, 7, 12)
    pygame.draw.rect(surf, leather_dark, left_leg)
    pygame.draw.rect(surf, (48, 38, 28), left_leg, 1)
    pygame.draw.rect(surf, leather, right_leg)
    pygame.draw.rect(surf, (48, 38, 28), right_leg, 1)
    # Сапоги
    pygame.draw.rect(surf, (70, 54, 40), (14, 34, 7, 4))
    pygame.draw.rect(surf, (90, 70, 50), (28, 34, 7, 4))

    # Торс - детализированный
    torso = pygame.Rect(16, 14, 18, 14)
    pygame.draw.rect(surf, armor_base, torso)
    pygame.draw.rect(surf, armor_shadow, torso, 2)
    # Центральная часть с тканью
    pygame.draw.rect(surf, cloth_primary, (18, 16, 14, 10))
    pygame.draw.rect(surf, cloth_dark, (18, 16, 14, 10), 1)
    # Детали брони
    pygame.draw.line(surf, armor_mid, (17, 16), (17, 26), 2)
    pygame.draw.line(surf, armor_mid, (33, 16), (33, 26), 2)
    pygame.draw.rect(surf, gold, (20, 18, 10, 2), 1)

    # Плечи/руки - отдельно видимые
    left_shoulder = pygame.Rect(12, 14, 6, 8)
    right_shoulder = pygame.Rect(32, 14, 6, 8)
    pygame.draw.rect(surf, armor_base, left_shoulder)
    pygame.draw.rect(surf, armor_shadow, left_shoulder, 1)
    pygame.draw.rect(surf, armor_base, right_shoulder)
    pygame.draw.rect(surf, armor_shadow, right_shoulder, 1)
    # Руки
    left_arm = pygame.Rect(12, 22, 5, 10)
    right_arm = pygame.Rect(33, 22, 5, 10)
    pygame.draw.rect(surf, leather, left_arm)
    pygame.draw.rect(surf, (48, 38, 28), left_arm, 1)
    pygame.draw.rect(surf, leather, right_arm)
    pygame.draw.rect(surf, (48, 38, 28), right_arm, 1)

    # Голова - детализированная
    head = pygame.Rect(18, 4, 14, 12)
    pygame.draw.ellipse(surf, skin, head)
    pygame.draw.ellipse(surf, skin_shadow, (head.x + 2, head.y + 2, 10, 8))
    # Шлем/капюшон
    pygame.draw.ellipse(surf, armor_base, (head.x - 2, head.y - 2, head.width + 4, head.height + 2), 2)
    pygame.draw.arc(surf, armor_base, (head.x - 1, head.y - 3, head.width + 2, 8), 0, 3.14, 2)
    # Лицо
    pygame.draw.circle(surf, (40, 32, 24), (head.centerx - 3, head.y + 6), 1)
    pygame.draw.circle(surf, (40, 32, 24), (head.centerx + 3, head.y + 6), 1)
    pygame.draw.arc(surf, (180, 140, 120), (head.centerx - 3, head.y + 8, 6, 4), 0, 3.14, 2)

    if hero_class == 'warrior':
        pygame.draw.rect(surf, armor_base, (12, 18, 24, 4))
        pygame.draw.rect(surf, gold, (16, 18, 16, 4), 1)
        pygame.draw.rect(surf, armor_base, (32, 14, 4, 22))
        pygame.draw.rect(surf, gold, (30, 14, 8, 4))
        pygame.draw.rect(surf, (220, 220, 232), (32, 8, 3, 10), 2)
        pygame.draw.line(surf, (200, 200, 220), (33, 8), (33, 2), 2)
        pygame.draw.polygon(surf, armor_shadow, [(12, 24), (6, 30), (12, 34), (22, 34), (22, 24)])
        pygame.draw.polygon(surf, gold, [(12, 24), (6, 30), (12, 34), (22, 34), (22, 24)], 1)
    elif hero_class == 'archer':
        pygame.draw.rect(surf, (84, 112, 68), (14, 14, 4, 20))
        pygame.draw.rect(surf, (84, 112, 68), (32, 14, 4, 20))
        pygame.draw.rect(surf, (64, 88, 52), (32, 16, 4, 12))
        pygame.draw.line(surf, (210, 210, 220), (34, 16), (34, 32), 2)
        bow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.arc(bow_surface, (120, 80, 40), (4, 8, 32, 32), 0.3, 2.84, 3)
        surf.blit(bow_surface, (0, 0))
        pygame.draw.line(surf, (220, 220, 220), (10, 22), (34, 16), 2)
        pygame.draw.rect(surf, (76, 56, 34), (10, 20, 6, 18))
    else:  # mage
        pygame.draw.rect(surf, (96, 122, 194), (12, 18, 24, 20))
        pygame.draw.rect(surf, (60, 80, 132), (12, 18, 24, 20), 2)
        pygame.draw.polygon(surf, (72, 92, 152), [(16, 18), (20, 8), (24, 18)])
        pygame.draw.line(surf, (160, 140, 100), (32, 10), (32, 32), 4)
        pygame.draw.circle(surf, (120, 200, 240), (32, 10), 5)
        pygame.draw.circle(surf, (180, 240, 255), (32, 10), 3)

    return surf


def _render_elf_hero(hero_class):
    """Детализированная текстура героя эльфов с понятной структурой тела."""
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    cloak_light = (104, 190, 140)
    cloak_mid = (82, 160, 116)
    cloak_shadow = (62, 132, 92)
    silver = (198, 214, 226)
    gold = (220, 204, 140)
    skin = (228, 238, 206)
    skin_shadow = (208, 218, 186)
    hair = (92, 180, 140)
    leather = (100, 84, 60)

    # Тень
    pygame.draw.ellipse(surf, (26, 40, 32, 150), (6, CELL_SIZE - 10, CELL_SIZE - 12, 8))

    # Ноги - отдельно видимые
    left_leg = pygame.Rect(16, 26, 6, 12)
    right_leg = pygame.Rect(28, 26, 6, 12)
    pygame.draw.rect(surf, cloak_light, left_leg)
    pygame.draw.rect(surf, cloak_shadow, left_leg, 1)
    pygame.draw.rect(surf, cloak_light, right_leg)
    pygame.draw.rect(surf, cloak_shadow, right_leg, 1)
    # Сапоги
    pygame.draw.rect(surf, leather, (16, 36, 6, 4))
    pygame.draw.rect(surf, (80, 68, 50), (28, 36, 6, 4))

    # Торс - детализированный
    torso = pygame.Rect(18, 14, 14, 12)
    pygame.draw.rect(surf, cloak_light, torso)
    pygame.draw.rect(surf, cloak_shadow, torso, 2)
    # Центральная часть
    pygame.draw.rect(surf, cloak_mid, (20, 16, 10, 8))
    pygame.draw.line(surf, cloak_shadow, (19, 16), (19, 24), 1)
    pygame.draw.line(surf, cloak_shadow, (31, 16), (31, 24), 1)

    # Плечи/руки - отдельно видимые
    left_shoulder = pygame.Rect(14, 14, 5, 8)
    right_shoulder = pygame.Rect(31, 14, 5, 8)
    pygame.draw.rect(surf, cloak_light, left_shoulder)
    pygame.draw.rect(surf, cloak_shadow, left_shoulder, 1)
    pygame.draw.rect(surf, cloak_light, right_shoulder)
    pygame.draw.rect(surf, cloak_shadow, right_shoulder, 1)
    # Руки
    left_arm = pygame.Rect(14, 22, 4, 10)
    right_arm = pygame.Rect(32, 22, 4, 10)
    pygame.draw.rect(surf, skin, left_arm)
    pygame.draw.rect(surf, skin_shadow, left_arm, 1)
    pygame.draw.rect(surf, skin, right_arm)
    pygame.draw.rect(surf, skin_shadow, right_arm, 1)

    # Голова - детализированная
    head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    head_x = 25
    head_y = 6
    pygame.draw.ellipse(head_surface, skin, (head_x - 6, head_y - 6, 12, 12))
    pygame.draw.ellipse(head_surface, skin_shadow, (head_x - 4, head_y - 4, 8, 8))
    # Уши-остроконечные
    pygame.draw.polygon(head_surface, skin, [(head_x - 7, head_y), (head_x - 10, head_y - 6), (head_x - 4, head_y - 4)])
    pygame.draw.polygon(head_surface, skin, [(head_x + 7, head_y), (head_x + 10, head_y - 6), (head_x + 4, head_y - 4)])
    # Волосы
    pygame.draw.ellipse(head_surface, hair, (head_x - 7, head_y - 8, 14, 6))
    # Глаза
    pygame.draw.circle(head_surface, (36, 70, 40), (head_x - 2, head_y - 1), 1)
    pygame.draw.circle(head_surface, (36, 70, 40), (head_x + 2, head_y - 1), 1)
    surf.blit(head_surface, (0, 0))

    if hero_class == 'warrior':
        sword = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(sword, silver, (30, 10, 4, 24))
        pygame.draw.rect(sword, gold, (28, 20, 8, 3))
        pygame.draw.rect(sword, (220, 230, 240), (30, 6, 3, 8))
        surf.blit(sword, (0, 0))
        shield = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(shield, silver, [(12, 18), (6, 26), (12, 34), (20, 30)])
        pygame.draw.polygon(shield, gold, [(12, 18), (6, 26), (12, 34), (20, 30)], 2)
        surf.blit(shield, (0, 0))
    elif hero_class == 'archer':
        bow = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.arc(bow, (118, 156, 112), (6, 4, 28, 36), 0.1, 3.04, 3)
        pygame.draw.line(bow, silver, (12, 22), (30, 14), 2)
        pygame.draw.rect(bow, (108, 86, 58), (10, 20, 4, 18))
        quiver = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(quiver, (110, 84, 60), (28, 12, 5, 18))
        pygame.draw.polygon(quiver, silver, [(30, 12), (34, 8), (32, 16)])
        surf.blit(bow, (0, 0))
        surf.blit(quiver, (0, 0))
    else:  # mage
        robe = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(robe, (84, 152, 146), (16, 14, 16, 20))
        pygame.draw.rect(robe, (58, 118, 108), (16, 14, 16, 20), 2)
        staff = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(staff, (120, 86, 52), (30, 6, 4, 26))
        pygame.draw.circle(staff, (160, 220, 200), (32, 6), 5)
        pygame.draw.circle(staff, (220, 255, 240), (32, 6), 3)
        surf.blit(robe, (0, 0))
        surf.blit(staff, (0, 0))

    return surf


def _render_undead_hero(hero_class):
    """Детализированная текстура героя нежити в более холодном, контрастном стиле костей и тёмной брони."""
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    armor_base = (90, 90, 110)
    armor_mid = (120, 120, 150)
    armor_shadow = (50, 50, 70)
    cloth_primary = (70, 50, 110)
    cloth_dark = (50, 35, 90)
    gold = (200, 150, 255)
    bone = (215, 220, 230)
    bone_dark = (170, 175, 185)
    dark_metal = (90, 95, 120)
    glow = (140, 80, 210)

    # Тень
    pygame.draw.ellipse(surf, (22, 24, 40, 185), (6, CELL_SIZE - 8, CELL_SIZE - 12, 6))

    # Ноги - отдельно видимые
    left_leg = pygame.Rect(14, 24, 7, 12)
    right_leg = pygame.Rect(28, 24, 7, 12)
    pygame.draw.rect(surf, dark_metal, left_leg)
    pygame.draw.rect(surf, armor_shadow, left_leg, 1)
    pygame.draw.rect(surf, dark_metal, right_leg)
    pygame.draw.rect(surf, armor_shadow, right_leg, 1)
    # Сапоги
    pygame.draw.rect(surf, (70, 70, 90), (14, 34, 7, 4))
    pygame.draw.rect(surf, (90, 90, 110), (28, 34, 7, 4))

    # Торс - детализированный
    torso = pygame.Rect(16, 14, 18, 14)
    pygame.draw.rect(surf, armor_base, torso)
    pygame.draw.rect(surf, armor_shadow, torso, 2)
    # Центральная часть с тканью
    pygame.draw.rect(surf, cloth_primary, (18, 16, 14, 10))
    pygame.draw.rect(surf, cloth_dark, (18, 16, 14, 10), 1)
    # Детали брони
    pygame.draw.line(surf, armor_mid, (17, 16), (17, 26), 2)
    pygame.draw.line(surf, armor_mid, (33, 16), (33, 26), 2)
    pygame.draw.rect(surf, gold, (20, 18, 10, 2), 1)

    # Плечи/руки - отдельно видимые
    left_shoulder = pygame.Rect(12, 14, 6, 8)
    right_shoulder = pygame.Rect(32, 14, 6, 8)
    pygame.draw.rect(surf, armor_base, left_shoulder)
    pygame.draw.rect(surf, armor_shadow, left_shoulder, 1)
    pygame.draw.rect(surf, armor_base, right_shoulder)
    pygame.draw.rect(surf, armor_shadow, right_shoulder, 1)
    # Руки (кости)
    left_arm = pygame.Rect(12, 22, 5, 10)
    right_arm = pygame.Rect(33, 22, 5, 10)
    pygame.draw.rect(surf, bone, left_arm)
    pygame.draw.rect(surf, bone_dark, left_arm, 1)
    pygame.draw.rect(surf, bone, right_arm)
    pygame.draw.rect(surf, bone_dark, right_arm, 1)

    # Голова (череп) - детализированная
    head = pygame.Rect(18, 4, 14, 12)
    pygame.draw.ellipse(surf, bone, head)
    pygame.draw.ellipse(surf, bone_dark, (head.x + 2, head.y + 2, 10, 8))
    # Шлем
    pygame.draw.ellipse(surf, armor_base, (head.x - 2, head.y - 2, head.width + 4, head.height + 2), 2)
    pygame.draw.arc(surf, armor_base, (head.x - 1, head.y - 3, head.width + 2, 8), 0, 3.14, 2)
    # Глаза (магическое свечение)
    pygame.draw.circle(surf, glow, (head.centerx - 3, head.y + 6), 2)
    pygame.draw.circle(surf, (220, 80, 255), (head.centerx - 3, head.y + 6), 1)
    pygame.draw.circle(surf, glow, (head.centerx + 3, head.y + 6), 2)
    pygame.draw.circle(surf, (220, 80, 255), (head.centerx + 3, head.y + 6), 1)
    # Рот (щель)
    pygame.draw.rect(surf, (60, 60, 80), (head.centerx - 2, head.y + 8, 4, 2))

    if hero_class == 'warrior':
        pygame.draw.rect(surf, armor_base, (12, 18, 24, 4))
        pygame.draw.rect(surf, gold, (16, 18, 16, 4), 1)
        pygame.draw.rect(surf, armor_base, (32, 14, 4, 22))
        pygame.draw.rect(surf, gold, (30, 14, 8, 4))
        pygame.draw.rect(surf, (180, 180, 200), (32, 8, 3, 10), 2)
        pygame.draw.line(surf, (160, 160, 180), (33, 8), (33, 2), 2)
        pygame.draw.polygon(surf, armor_shadow, [(12, 24), (6, 30), (12, 34), (22, 34), (22, 24)])
        pygame.draw.polygon(surf, gold, [(12, 24), (6, 30), (12, 34), (22, 34), (22, 24)], 1)
    elif hero_class == 'archer':
        pygame.draw.rect(surf, (100, 80, 120), (14, 14, 4, 20))
        pygame.draw.rect(surf, (100, 80, 120), (32, 14, 4, 20))
        pygame.draw.rect(surf, (80, 60, 100), (32, 16, 4, 12))
        pygame.draw.line(surf, (180, 180, 200), (34, 16), (34, 32), 2)
        bow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.arc(bow_surface, (80, 60, 100), (4, 8, 32, 32), 0.3, 2.84, 3)
        surf.blit(bow_surface, (0, 0))
        pygame.draw.line(surf, (200, 200, 220), (10, 22), (34, 16), 2)
        pygame.draw.rect(surf, (100, 80, 100), (10, 20, 6, 18))
        quiver_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(quiver_surface, (90, 70, 110), (28, 12, 5, 18))
        pygame.draw.polygon(quiver_surface, dark_metal, [(30, 12), (34, 8), (32, 16)])
        surf.blit(quiver_surface, (0, 0))
    else:  # mage
        pygame.draw.rect(surf, (90, 70, 130), (12, 18, 24, 20))
        pygame.draw.rect(surf, (60, 40, 90), (12, 18, 24, 20), 2)
        pygame.draw.polygon(surf, (80, 60, 120), [(16, 18), (20, 8), (24, 18)])
        pygame.draw.line(surf, (100, 80, 120), (32, 10), (32, 32), 4)
        pygame.draw.circle(surf, (140, 40, 180), (32, 10), 5)
        pygame.draw.circle(surf, (180, 60, 220), (32, 10), 3)

    return surf


def _render_demon_hero(hero_class):
    """Детализированная текстура героя демонов с понятной структурой тела."""
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    armor_base = (200, 60, 40)
    armor_mid = (170, 50, 30)
    armor_shadow = (140, 40, 20)
    cloth_primary = (180, 60, 80)
    cloth_dark = (160, 50, 60)
    gold = (255, 140, 60)
    skin = (240, 120, 80)
    skin_shadow = (220, 100, 60)
    dark_metal = (140, 40, 20)
    glow = (255, 40, 0)

    # Тень
    pygame.draw.ellipse(surf, (48, 20, 14, 160), (6, CELL_SIZE - 8, CELL_SIZE - 12, 6))

    # Ноги - отдельно видимые
    left_leg = pygame.Rect(14, 24, 7, 12)
    right_leg = pygame.Rect(28, 24, 7, 12)
    pygame.draw.rect(surf, dark_metal, left_leg)
    pygame.draw.rect(surf, armor_shadow, left_leg, 1)
    pygame.draw.rect(surf, dark_metal, right_leg)
    pygame.draw.rect(surf, armor_shadow, right_leg, 1)
    # Сапоги
    pygame.draw.rect(surf, (100, 30, 15), (14, 34, 7, 4))
    pygame.draw.rect(surf, (120, 40, 20), (28, 34, 7, 4))

    # Торс - детализированный
    torso = pygame.Rect(16, 14, 18, 14)
    pygame.draw.rect(surf, armor_base, torso)
    pygame.draw.rect(surf, armor_shadow, torso, 2)
    # Центральная часть с тканью
    pygame.draw.rect(surf, cloth_primary, (18, 16, 14, 10))
    pygame.draw.rect(surf, cloth_dark, (18, 16, 14, 10), 1)
    # Детали брони
    pygame.draw.line(surf, armor_mid, (17, 16), (17, 26), 2)
    pygame.draw.line(surf, armor_mid, (33, 16), (33, 26), 2)
    pygame.draw.rect(surf, gold, (20, 18, 10, 2), 1)

    # Плечи/руки - отдельно видимые
    left_shoulder = pygame.Rect(12, 14, 6, 8)
    right_shoulder = pygame.Rect(32, 14, 6, 8)
    pygame.draw.rect(surf, armor_base, left_shoulder)
    pygame.draw.rect(surf, armor_shadow, left_shoulder, 1)
    pygame.draw.rect(surf, armor_base, right_shoulder)
    pygame.draw.rect(surf, armor_shadow, right_shoulder, 1)
    # Руки
    left_arm = pygame.Rect(12, 22, 5, 10)
    right_arm = pygame.Rect(33, 22, 5, 10)
    pygame.draw.rect(surf, skin, left_arm)
    pygame.draw.rect(surf, skin_shadow, left_arm, 1)
    pygame.draw.rect(surf, skin, right_arm)
    pygame.draw.rect(surf, skin_shadow, right_arm, 1)

    # Голова - детализированная
    head = pygame.Rect(18, 4, 14, 12)
    pygame.draw.ellipse(surf, skin, head)
    pygame.draw.ellipse(surf, skin_shadow, (head.x + 2, head.y + 2, 10, 8))
    # Рога
    pygame.draw.polygon(surf, dark_metal, [(head.centerx - 6, head.y + 2), (head.centerx - 8, head.y - 2), (head.centerx - 2, head.y)])
    pygame.draw.polygon(surf, dark_metal, [(head.centerx + 6, head.y + 2), (head.centerx + 8, head.y - 2), (head.centerx + 2, head.y)])
    # Шлем/капюшон
    pygame.draw.ellipse(surf, armor_base, (head.x - 2, head.y - 2, head.width + 4, head.height + 2), 2)
    # Глаза (огненные)
    pygame.draw.circle(surf, glow, (head.centerx - 3, head.y + 6), 2)
    pygame.draw.circle(surf, (255, 120, 40), (head.centerx - 3, head.y + 6), 1)
    pygame.draw.circle(surf, glow, (head.centerx + 3, head.y + 6), 2)
    pygame.draw.circle(surf, (255, 120, 40), (head.centerx + 3, head.y + 6), 1)
    # Рот
    pygame.draw.arc(surf, (200, 40, 20), (head.centerx - 3, head.y + 8, 6, 4), 0, 3.14, 2)

    if hero_class == 'warrior':
        pygame.draw.rect(surf, armor_base, (12, 18, 24, 4))
        pygame.draw.rect(surf, gold, (16, 18, 16, 4), 1)
        pygame.draw.rect(surf, armor_base, (32, 14, 4, 22))
        pygame.draw.rect(surf, gold, (30, 14, 8, 4))
        pygame.draw.rect(surf, (255, 100, 60), (32, 8, 3, 10), 2)
        pygame.draw.line(surf, (255, 120, 80), (33, 8), (33, 2), 2)
        pygame.draw.polygon(surf, armor_shadow, [(12, 24), (6, 30), (12, 34), (22, 34), (22, 24)])
        pygame.draw.polygon(surf, gold, [(12, 24), (6, 30), (12, 34), (22, 34), (22, 24)], 1)
    elif hero_class == 'archer':
        pygame.draw.rect(surf, (180, 60, 60), (14, 14, 4, 20))
        pygame.draw.rect(surf, (180, 60, 60), (32, 14, 4, 20))
        pygame.draw.rect(surf, (140, 40, 40), (32, 16, 4, 12))
        pygame.draw.line(surf, (255, 140, 100), (34, 16), (34, 32), 2)
        bow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.arc(bow_surface, (140, 40, 40), (4, 8, 32, 32), 0.3, 2.84, 3)
        surf.blit(bow_surface, (0, 0))
        pygame.draw.line(surf, (255, 120, 60), (10, 22), (34, 16), 2)
        pygame.draw.rect(surf, (160, 60, 60), (10, 20, 6, 18))
        quiver_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(quiver_surface, (160, 50, 50), (28, 12, 5, 18))
        pygame.draw.polygon(quiver_surface, dark_metal, [(30, 12), (34, 8), (32, 16)])
        surf.blit(quiver_surface, (0, 0))
    else:  # mage
        pygame.draw.rect(surf, (160, 40, 80), (12, 18, 24, 20))
        pygame.draw.rect(surf, (120, 30, 60), (12, 18, 24, 20), 2)
        pygame.draw.polygon(surf, (140, 40, 70), [(16, 18), (20, 8), (24, 18)])
        pygame.draw.line(surf, (120, 60, 40), (32, 10), (32, 32), 4)
        pygame.draw.circle(surf, (255, 80, 20), (32, 10), 5)
        pygame.draw.circle(surf, (255, 140, 60), (32, 10), 3)

    return surf


def _render_dwarf_hero(hero_class):
    """Детализированная текстура героя гномов в более контрастном, «тяжёлом» стиле брони."""
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    armor_base = (150, 150, 170)
    armor_mid = (120, 120, 140)
    armor_shadow = (80, 80, 100)
    cloth_primary = (110, 130, 150)
    cloth_dark = (80, 100, 130)
    gold = (220, 190, 90)
    skin = (210, 170, 120)
    skin_shadow = (185, 140, 95)
    beard = (130, 90, 55)
    beard_dark = (100, 70, 45)
    metal = (170, 170, 190)

    # Тень
    pygame.draw.ellipse(surf, (28, 30, 38, 180), (6, CELL_SIZE - 8, CELL_SIZE - 12, 6))

    # Ноги - отдельно видимые (короткие у гнома)
    left_leg = pygame.Rect(14, 26, 7, 10)
    right_leg = pygame.Rect(28, 26, 7, 10)
    pygame.draw.rect(surf, armor_base, left_leg)
    pygame.draw.rect(surf, armor_shadow, left_leg, 1)
    pygame.draw.rect(surf, armor_base, right_leg)
    pygame.draw.rect(surf, armor_shadow, right_leg, 1)
    # Сапоги
    pygame.draw.rect(surf, (100, 100, 120), (14, 34, 7, 4))
    pygame.draw.rect(surf, (120, 120, 140), (28, 34, 7, 4))

    # Торс - детализированный (широкий у гнома)
    torso = pygame.Rect(16, 14, 18, 12)
    pygame.draw.rect(surf, armor_base, torso)
    pygame.draw.rect(surf, armor_shadow, torso, 2)
    # Центральная часть с тканью
    pygame.draw.rect(surf, cloth_primary, (18, 16, 14, 8))
    pygame.draw.rect(surf, cloth_dark, (18, 16, 14, 8), 1)
    # Детали брони
    pygame.draw.line(surf, armor_mid, (17, 16), (17, 24), 2)
    pygame.draw.line(surf, armor_mid, (33, 16), (33, 24), 2)
    pygame.draw.rect(surf, gold, (20, 18, 10, 2), 1)

    # Плечи/руки - отдельно видимые (широкие)
    left_shoulder = pygame.Rect(12, 14, 6, 8)
    right_shoulder = pygame.Rect(32, 14, 6, 8)
    pygame.draw.rect(surf, armor_base, left_shoulder)
    pygame.draw.rect(surf, armor_shadow, left_shoulder, 1)
    pygame.draw.rect(surf, armor_base, right_shoulder)
    pygame.draw.rect(surf, armor_shadow, right_shoulder, 1)
    # Руки
    left_arm = pygame.Rect(12, 22, 5, 10)
    right_arm = pygame.Rect(33, 22, 5, 10)
    pygame.draw.rect(surf, skin, left_arm)
    pygame.draw.rect(surf, skin_shadow, left_arm, 1)
    pygame.draw.rect(surf, skin, right_arm)
    pygame.draw.rect(surf, skin_shadow, right_arm, 1)

    # Голова - детализированная (большая у гнома)
    head = pygame.Rect(18, 6, 14, 10)
    pygame.draw.ellipse(surf, skin, head)
    pygame.draw.ellipse(surf, skin_shadow, (head.x + 2, head.y + 2, 10, 6))
    # Борода
    pygame.draw.rect(surf, beard, (16, 20, 18, 8))
    pygame.draw.line(surf, beard_dark, (17, 20), (17, 26), 1)
    pygame.draw.line(surf, beard_dark, (21, 20), (21, 26), 1)
    pygame.draw.line(surf, beard_dark, (25, 20), (25, 26), 1)
    pygame.draw.line(surf, beard_dark, (29, 20), (29, 26), 1)
    pygame.draw.line(surf, beard_dark, (33, 20), (33, 26), 1)
    # Шлем/капюшон
    pygame.draw.ellipse(surf, armor_base, (head.x - 2, head.y - 2, head.width + 4, head.height + 2), 2)
    # Глаза
    pygame.draw.circle(surf, (60, 40, 20), (head.centerx - 2, head.y + 5), 1)
    pygame.draw.circle(surf, (60, 40, 20), (head.centerx + 2, head.y + 5), 1)
    # Нос
    pygame.draw.circle(surf, skin_shadow, (head.centerx, head.y + 6), 1)

    if hero_class == 'warrior':
        pygame.draw.rect(surf, armor_base, (12, 18, 24, 4))
        pygame.draw.rect(surf, gold, (16, 18, 16, 4), 1)
        pygame.draw.rect(surf, armor_base, (32, 14, 4, 22))
        pygame.draw.rect(surf, gold, (30, 14, 8, 4))
        pygame.draw.rect(surf, metal, (32, 8, 3, 10), 2)
        pygame.draw.line(surf, (200, 200, 220), (33, 8), (33, 2), 2)
        pygame.draw.polygon(surf, armor_shadow, [(12, 24), (6, 30), (12, 34), (22, 34), (22, 24)])
        pygame.draw.polygon(surf, gold, [(12, 24), (6, 30), (12, 34), (22, 34), (22, 24)], 1)
    elif hero_class == 'archer':
        pygame.draw.rect(surf, (160, 160, 180), (14, 14, 4, 20))
        pygame.draw.rect(surf, (160, 160, 180), (32, 14, 4, 20))
        pygame.draw.rect(surf, (120, 120, 140), (32, 16, 4, 12))
        pygame.draw.line(surf, (200, 200, 220), (34, 16), (34, 32), 2)
        bow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.arc(bow_surface, (120, 80, 40), (4, 8, 32, 32), 0.3, 2.84, 3)
        surf.blit(bow_surface, (0, 0))
        pygame.draw.line(surf, (220, 220, 240), (10, 22), (34, 16), 2)
        pygame.draw.rect(surf, (140, 100, 60), (10, 20, 6, 18))
        quiver_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(quiver_surface, (130, 90, 50), (28, 12, 5, 18))
        pygame.draw.polygon(quiver_surface, metal, [(30, 12), (34, 8), (32, 16)])
        surf.blit(quiver_surface, (0, 0))
    else:  # mage
        pygame.draw.rect(surf, (120, 140, 180), (12, 18, 24, 20))
        pygame.draw.rect(surf, (80, 100, 140), (12, 18, 24, 20), 2)
        pygame.draw.polygon(surf, (100, 120, 160), [(16, 18), (20, 8), (24, 18)])
        pygame.draw.line(surf, (180, 140, 80), (32, 10), (32, 32), 4)
        pygame.draw.circle(surf, (200, 180, 80), (32, 10), 5)
        pygame.draw.circle(surf, gold, (32, 10), 3)

    return surf


def _render_shadow_hero(hero_class):
    """Детализированная текстура героя теней с понятной структурой тела."""
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    armor_base = (60, 0, 90)
    armor_mid = (50, 0, 75)
    armor_shadow = (40, 0, 60)
    cloth_primary = (80, 0, 120)
    cloth_dark = (60, 0, 100)
    gold = (180, 120, 255)
    skin = (200, 180, 120)
    skin_shadow = (180, 160, 100)
    dark_metal = (100, 80, 120)
    glow = (120, 0, 180)

    # Тень
    pygame.draw.ellipse(surf, (20, 0, 30, 160), (6, CELL_SIZE - 8, CELL_SIZE - 12, 6))

    # Ноги - отдельно видимые
    left_leg = pygame.Rect(14, 24, 7, 12)
    right_leg = pygame.Rect(28, 24, 7, 12)
    pygame.draw.rect(surf, dark_metal, left_leg)
    pygame.draw.rect(surf, armor_shadow, left_leg, 1)
    pygame.draw.rect(surf, dark_metal, right_leg)
    pygame.draw.rect(surf, armor_shadow, right_leg, 1)
    # Сапоги
    pygame.draw.rect(surf, (50, 0, 70), (14, 34, 7, 4))
    pygame.draw.rect(surf, (70, 0, 90), (28, 34, 7, 4))

    # Торс - детализированный
    torso = pygame.Rect(16, 14, 18, 14)
    pygame.draw.rect(surf, armor_base, torso)
    pygame.draw.rect(surf, armor_shadow, torso, 2)
    # Центральная часть с тканью
    pygame.draw.rect(surf, cloth_primary, (18, 16, 14, 10))
    pygame.draw.rect(surf, cloth_dark, (18, 16, 14, 10), 1)
    # Детали брони
    pygame.draw.line(surf, armor_mid, (17, 16), (17, 26), 2)
    pygame.draw.line(surf, armor_mid, (33, 16), (33, 26), 2)
    pygame.draw.rect(surf, gold, (20, 18, 10, 2), 1)

    # Плечи/руки - отдельно видимые
    left_shoulder = pygame.Rect(12, 14, 6, 8)
    right_shoulder = pygame.Rect(32, 14, 6, 8)
    pygame.draw.rect(surf, armor_base, left_shoulder)
    pygame.draw.rect(surf, armor_shadow, left_shoulder, 1)
    pygame.draw.rect(surf, armor_base, right_shoulder)
    pygame.draw.rect(surf, armor_shadow, right_shoulder, 1)
    # Руки
    left_arm = pygame.Rect(12, 22, 5, 10)
    right_arm = pygame.Rect(33, 22, 5, 10)
    pygame.draw.rect(surf, skin, left_arm)
    pygame.draw.rect(surf, skin_shadow, left_arm, 1)
    pygame.draw.rect(surf, skin, right_arm)
    pygame.draw.rect(surf, skin_shadow, right_arm, 1)

    # Голова - детализированная
    head = pygame.Rect(18, 4, 14, 12)
    pygame.draw.ellipse(surf, skin, head)
    pygame.draw.ellipse(surf, skin_shadow, (head.x + 2, head.y + 2, 10, 8))
    # Капюшон
    pygame.draw.polygon(surf, armor_shadow, [(head.x - 2, head.y), (head.centerx, head.y - 4), (head.x + 16, head.y)])
    pygame.draw.arc(surf, armor_base, (head.x - 1, head.y - 3, head.width + 2, 8), 0, 3.14, 2)
    # Глаза (магическое свечение)
    pygame.draw.circle(surf, glow, (head.centerx - 3, head.y + 6), 2)
    pygame.draw.circle(surf, (160, 40, 220), (head.centerx - 3, head.y + 6), 1)
    pygame.draw.circle(surf, glow, (head.centerx + 3, head.y + 6), 2)
    pygame.draw.circle(surf, (160, 40, 220), (head.centerx + 3, head.y + 6), 1)
    # Рот
    pygame.draw.arc(surf, (80, 0, 100), (head.centerx - 3, head.y + 8, 6, 4), 0, 3.14, 2)

    if hero_class == 'warrior':
        pygame.draw.rect(surf, armor_base, (12, 18, 24, 4))
        pygame.draw.rect(surf, gold, (16, 18, 16, 4), 1)
        pygame.draw.rect(surf, armor_base, (32, 14, 4, 22))
        pygame.draw.rect(surf, gold, (30, 14, 8, 4))
        pygame.draw.rect(surf, (80, 0, 120), (32, 8, 3, 10), 2)
        pygame.draw.line(surf, (100, 0, 150), (33, 8), (33, 2), 2)
        pygame.draw.polygon(surf, armor_shadow, [(12, 24), (6, 30), (12, 34), (22, 34), (22, 24)])
        pygame.draw.polygon(surf, gold, [(12, 24), (6, 30), (12, 34), (22, 34), (22, 24)], 1)
    elif hero_class == 'archer':
        pygame.draw.rect(surf, (80, 0, 100), (14, 14, 4, 20))
        pygame.draw.rect(surf, (80, 0, 100), (32, 14, 4, 20))
        pygame.draw.rect(surf, (60, 0, 80), (32, 16, 4, 12))
        pygame.draw.line(surf, (200, 120, 240), (34, 16), (34, 32), 2)
        bow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.arc(bow_surface, (120, 0, 160), (4, 8, 32, 32), 0.3, 2.84, 3)
        surf.blit(bow_surface, (0, 0))
        pygame.draw.line(surf, (200, 120, 240), (10, 22), (34, 16), 2)
        pygame.draw.rect(surf, (70, 0, 90), (10, 20, 6, 18))
        quiver_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(quiver_surface, (70, 0, 90), (28, 12, 5, 18))
        pygame.draw.polygon(quiver_surface, dark_metal, [(30, 12), (34, 8), (32, 16)])
        surf.blit(quiver_surface, (0, 0))
    else:  # mage
        pygame.draw.rect(surf, (80, 0, 120), (12, 18, 24, 20))
        pygame.draw.rect(surf, (60, 0, 90), (12, 18, 24, 20), 2)
        pygame.draw.polygon(surf, (70, 0, 110), [(16, 18), (20, 8), (24, 18)])
        pygame.draw.line(surf, (60, 40, 80), (32, 10), (32, 32), 4)
        pygame.draw.circle(surf, (140, 0, 200), (32, 10), 5)
        pygame.draw.circle(surf, (180, 40, 240), (32, 10), 3)

    return surf


def _render_elf_unit(unit):
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

    leaf_light = (130, 200, 150)
    leaf_mid = (82, 150, 102)
    leaf_dark = (56, 96, 68)
    bark = (120, 88, 58)
    silver = (198, 214, 226)
    gold = (220, 204, 140)
    skin = (228, 238, 206)
    hair = (86, 168, 120)
    shadow_color = (32, 40, 36, 140)

    pygame.draw.ellipse(surf, shadow_color, (6, CELL_SIZE - 9, CELL_SIZE - 12, 6))

    def draw_head(target, cx, cy, hair_color):
        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(head_surface, skin, (cx - 6, cy - 6, 12, 12))
        pygame.draw.polygon(head_surface, skin, [(cx - 8, cy), (cx - 12, cy - 6), (cx - 2, cy - 4)])
        pygame.draw.polygon(head_surface, skin, [(cx + 8, cy), (cx + 12, cy - 6), (cx + 2, cy - 4)])
        pygame.draw.ellipse(head_surface, hair_color, (cx - 7, cy - 8, 14, 6))
        pygame.draw.circle(head_surface, (40, 80, 50), (cx - 2, cy - 1), 1)
        pygame.draw.circle(head_surface, (40, 80, 50), (cx + 2, cy - 1), 1)
        target.blit(head_surface, (0, 0))

    def draw_humanoid_body(target, tunic_top, tunic_bottom, belt_color):
        torso = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(torso, tunic_top, (18, 16, 14, 12))
        pygame.draw.rect(torso, tunic_bottom, (18, 26, 14, 10))
        pygame.draw.rect(torso, belt_color, (18, 24, 14, 3))
        pygame.draw.rect(torso, leaf_dark, (18, 16, 14, 20), 2)
        pygame.draw.rect(torso, tunic_bottom, (14, 28, 6, 12))
        pygame.draw.rect(torso, tunic_bottom, (26, 28, 6, 12))
        target.blit(torso, (0, 0))

    if unit == 'elf_archer':
        draw_humanoid_body(surf, leaf_mid, leaf_light, leaf_dark)
        draw_head(surf, 24, 16, hair)
        bow = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.arc(bow, (116, 150, 96), (4, 4, 28, 36), 0.12, 3.02, 3)
        pygame.draw.line(bow, silver, (10, 22), (30, 14), 2)
        pygame.draw.rect(bow, (120, 88, 52), (12, 20, 4, 18))
        surf.blit(bow, (0, 0))
        quiver = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(quiver, (100, 72, 40), (30, 12, 4, 18))
        pygame.draw.polygon(quiver, silver, [(32, 12), (36, 8), (34, 16)])
        surf.blit(quiver, (0, 0))
    elif unit == 'elf_scout':
        draw_humanoid_body(surf, (100, 160, 116), leaf_mid, leaf_dark)
        draw_head(surf, 24, 16, (92, 156, 120))
        daggers = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(daggers, silver, [(30, 14), (36, 12), (32, 18)])
        pygame.draw.rect(daggers, (120, 88, 52), (28, 18, 5, 10))
        pygame.draw.polygon(daggers, silver, [(18, 30), (12, 34), (18, 36)])
        pygame.draw.rect(daggers, (120, 88, 52), (16, 28, 4, 8))
        surf.blit(daggers, (0, 0))
    elif unit == 'dryad':
        # Дриада - гуманоидная фея постарше (не дерево)
        fairy_skin = (200, 230, 180)  # Более зелёный оттенок кожи
        fairy_hair = (100, 180, 120)  # Зелёные волосы
        dress_light = (120, 200, 140)
        dress_dark = (80, 160, 100)
        
        draw_humanoid_body(surf, dress_light, dress_dark, leaf_dark)
        draw_head(surf, 24, 16, fairy_hair)
        
        # Крылья феи
        wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Левое крыло
        pygame.draw.ellipse(wings, (180, 240, 200, 150), (8, 14, 12, 16))
        pygame.draw.ellipse(wings, (140, 220, 160, 180), (8, 14, 12, 16), 2)
        # Правое крыло
        pygame.draw.ellipse(wings, (180, 240, 200, 150), (28, 14, 12, 16))
        pygame.draw.ellipse(wings, (140, 220, 160, 180), (28, 14, 12, 16), 2)
        surf.blit(wings, (0, 0))
        
        # Магический посох/жезл
        staff = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(staff, (100, 140, 80), (30, 8, 3, 26))
        pygame.draw.circle(staff, (160, 240, 180), (31, 8), 4)
        pygame.draw.circle(staff, (200, 255, 220), (31, 8), 2)
        surf.blit(staff, (0, 0))
    elif unit == 'druid':
        robe = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(robe, (90, 152, 140), (16, 16, 16, 20))
        pygame.draw.rect(robe, (60, 118, 108), (16, 16, 16, 20), 2)
        draw_head(robe, 24, 14, (120, 200, 160))
        staff = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(staff, (110, 70, 40), (30, 8, 4, 26))
        pygame.draw.circle(staff, (160, 220, 200), (32, 6), 5)
        pygame.draw.circle(staff, (220, 255, 240), (32, 6), 3)
        surf.blit(robe, (0, 0))
        surf.blit(staff, (0, 0))
    elif unit == 'pixie' or unit == 'fairy':
        # Фея - молодая дриада (меньше размер, светлее)
        fairy_skin = (220, 245, 200)  # Светлая кожа
        fairy_hair = (120, 200, 140)  # Светло-зелёные волосы
        dress_light = (140, 220, 160)
        dress_dark = (100, 180, 120)
        
        # Меньше тело для молодой феи
        torso_small = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(torso_small, dress_light, (18, 18, 12, 10))
        pygame.draw.rect(torso_small, dress_dark, (18, 26, 12, 8))
        pygame.draw.rect(torso_small, leaf_dark, (18, 18, 12, 16), 2)
        pygame.draw.rect(torso_small, dress_dark, (16, 28, 6, 10))
        pygame.draw.rect(torso_small, dress_dark, (26, 28, 6, 10))
        surf.blit(torso_small, (0, 0))
        
        # Маленькая голова
        head_small = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(head_small, fairy_skin, (22, 6, 10, 10))
        pygame.draw.polygon(head_small, fairy_skin, [(22, 10), (18, 6), (20, 4)])
        pygame.draw.polygon(head_small, fairy_skin, [(32, 10), (36, 6), (34, 4)])
        pygame.draw.ellipse(head_small, fairy_hair, (21, 5, 12, 5))
        pygame.draw.circle(head_small, (60, 120, 80), (25, 9), 1)
        pygame.draw.circle(head_small, (60, 120, 80), (29, 9), 1)
        surf.blit(head_small, (0, 0))
        
        # Большие крылья для феи
        wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Левое крыло
        pygame.draw.ellipse(wings, (200, 250, 220, 140), (6, 16, 14, 18))
        pygame.draw.ellipse(wings, (160, 230, 180, 160), (6, 16, 14, 18), 2)
        # Правое крыло
        pygame.draw.ellipse(wings, (200, 250, 220, 140), (28, 16, 14, 18))
        pygame.draw.ellipse(wings, (160, 230, 180, 160), (28, 16, 14, 18), 2)
        surf.blit(wings, (0, 0))
    elif unit == 'ent':
        # Энт - ходячее древоподобное существо (не дуб, а человекоподобное дерево)
        bark_dark = (80, 60, 40)
        bark_mid = (100, 75, 50)
        bark_light = (120, 90, 60)
        
        # Тело-ствол (гуманоидная форма)
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Торс
        pygame.draw.rect(body, bark_mid, (16, 14, 16, 16))
        pygame.draw.rect(body, bark_dark, (16, 14, 16, 16), 2)
        # Детали коры
        for i in range(4):
            pygame.draw.line(body, bark_dark, (18, 16 + i*4), (30, 16 + i*4), 1)
        
        # Руки-ветви
        pygame.draw.rect(body, bark_mid, (10, 20, 5, 12))
        pygame.draw.rect(body, bark_mid, (33, 20, 5, 12))
        pygame.draw.rect(body, bark_dark, (10, 20, 5, 12), 1)
        pygame.draw.rect(body, bark_dark, (33, 20, 5, 12), 1)
        
        # Ноги-корни
        pygame.draw.rect(body, bark_mid, (14, 28, 6, 10))
        pygame.draw.rect(body, bark_mid, (28, 28, 6, 10))
        pygame.draw.rect(body, bark_dark, (14, 28, 6, 10), 1)
        pygame.draw.rect(body, bark_dark, (28, 28, 6, 10), 1)
        # Корни на ногах
        pygame.draw.line(body, bark_dark, (17, 38), (10, 42), 2)
        pygame.draw.line(body, bark_dark, (31, 38), (38, 42), 2)
        
        # Голова-крона (формы как у дерева, но на месте головы)
        head = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Основание головы (широкое)
        pygame.draw.ellipse(head, bark_mid, (14, 4, 20, 12))
        pygame.draw.ellipse(head, bark_dark, (14, 4, 20, 12), 2)
        # Листва вместо волос
        pygame.draw.ellipse(head, leaf_mid, (14, 2, 20, 10))
        pygame.draw.ellipse(head, leaf_light, (16, 3, 16, 8))
        # "Глаза" - сучки
        pygame.draw.circle(head, (60, 40, 20), (20, 9), 2)
        pygame.draw.circle(head, (60, 40, 20), (28, 9), 2)
        # "Рот" - щель в коре
        pygame.draw.rect(head, (50, 30, 15), (22, 11, 4, 2))
        
        body.blit(head, (0, 0))
        surf.blit(body, (0, 0))
    elif unit == 'unicorn':
        uni = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(uni, (236, 236, 246), (10, 20, 28, 14))
        pygame.draw.ellipse(uni, (210, 210, 220), (10, 20, 28, 14), 2)
        pygame.draw.rect(uni, (236, 236, 246), (14, 24, 6, 12))
        pygame.draw.rect(uni, (236, 236, 246), (28, 24, 6, 12))
        pygame.draw.ellipse(uni, (236, 236, 246), (22, 10, 12, 10))
        pygame.draw.polygon(uni, gold, [(28, 10), (32, 2), (30, 12)])
        pygame.draw.circle(uni, (80, 100, 140), (28, 14), 2)
        surf.blit(uni, (0, 0))
    else:
        draw_humanoid_body(surf, leaf_mid, leaf_light, leaf_dark)
        draw_head(surf, 24, 16, hair)

    return surf


_ELF_ANIMATION_BLUEPRINTS = {
    'elf_archer': {
        'Idle': {},
        'IdleBreath': {'offset': (0, -2)},
        'Walk': {'offset': (2, 0)},
        'WalkAlt': {'offset': (-2, 0)},
        'AttackDraw': {'offset': (-1, -3), 'tint': (10, 40, 10, 60)},
        'AttackRelease': {'offset': (2, -4), 'tint': (160, 160, 60, 70)},
        'AttackRecover': {'offset': (1, -1)},
        'MeleePrep': {'offset': (-2, 0), 'rotate': -6},
        'MeleeStrike': {'offset': (3, -2), 'rotate': 7},
        'MeleeRecover': {'offset': (1, -1)},
        'TurnLeft': {'offset': (-2, 1), 'rotate': -8},
        'TurnRight': {'offset': (2, -1), 'rotate': 8},
        'Hurt': {'offset': (-1, 2), 'rotate': 8},
        'Death': {'offset': (-10, 12), 'rotate': 86, 'dim': 110},
        'Corpse': {'offset': (-14, 16), 'rotate': 104, 'dim': 150, 'alpha': 220},
    },
    'elf_scout': {
        'Idle': {},
        'IdleBreath': {'offset': (0, -1)},
        'Walk': {'offset': (2, 0)},
        'WalkAlt': {'offset': (-2, 0)},
        'AttackPrep': {'offset': (-1, -1), 'rotate': -6},
        'AttackStrike': {'offset': (3, -2), 'rotate': 8},
        'AttackRecover': {'offset': (1, -1)},
        'TurnLeft': {'offset': (-2, 1), 'rotate': -10},
        'TurnRight': {'offset': (2, -1), 'rotate': 10},
        'Hurt': {'offset': (-2, 2), 'rotate': 10},
        'Death': {'offset': (-8, 10), 'rotate': 82, 'dim': 110},
        'Corpse': {'offset': (-12, 14), 'rotate': 102, 'dim': 160, 'alpha': 220},
    },
    'dryad': {
        'Idle': {},
        'IdleSway': {'offset': (1, -1)},
        'Walk': {'offset': (1, 0)},
        'WalkAlt': {'offset': (-1, 0)},
        'CastStart': {'offset': (0, -2)},
        'CastRelease': {'offset': (0, -3)},
        'CastRecover': {'offset': (0, -1)},
        'TurnLeft': {'offset': (-1, 0), 'rotate': -6},
        'TurnRight': {'offset': (1, -1), 'rotate': 6},
        'Hurt': {'offset': (-1, 2), 'rotate': 6},
        'Death': {'offset': (-10, 12), 'rotate': 92, 'dim': 120},
        'Corpse': {'offset': (-14, 16), 'rotate': 110, 'dim': 170, 'alpha': 210},
    },
    'druid': {
        'Idle': {},
        'IdleBreath': {'offset': (0, -2)},
        'Walk': {'offset': (1, 0)},
        'WalkAlt': {'offset': (-1, 0)},
        'CastStart': {'offset': (0, -3), 'glow': {'color': (140, 210, 200), 'alpha': 90}},
        'CastRelease': {'offset': (0, -4), 'glow': {'color': (200, 255, 240), 'alpha': 130}},
        'CastRecover': {'offset': (0, -2)},
        'TurnLeft': {'offset': (-1, 0), 'rotate': -6},
        'TurnRight': {'offset': (1, -1), 'rotate': 6},
        'Hurt': {'offset': (-1, 2), 'rotate': 8},
        'Death': {'offset': (-10, 12), 'rotate': 88, 'dim': 120},
        'Corpse': {'offset': (-14, 16), 'rotate': 106, 'dim': 170, 'alpha': 220},
    },
    'pixie': {
        'Idle': {},
        'IdlePulse': {'scale': 1.04},
        'IdleHover': {'offset': (0, -3)},
        'CastStart': {'scale': 1.08, 'glow': {'color': (200, 250, 220), 'alpha': 120}},
        'CastRelease': {'scale': 1.12, 'glow': {'color': (220, 255, 240), 'alpha': 160}},
        'CastRecover': {'scale': 1.02},
        'TurnLeft': {'offset': (-1, -2), 'rotate': -4},
        'TurnRight': {'offset': (1, -2), 'rotate': 4},
        'Hurt': {'offset': (-1, 2), 'dim': 80},
        'Death': {'offset': (0, 6), 'scale': 0.9, 'dim': 140},
        'Corpse': {'offset': (0, 10), 'scale': 0.82, 'dim': 180, 'alpha': 170},
    },
    'fairy': {
        'Idle': {},
        'IdlePulse': {'scale': 1.04},
        'IdleHover': {'offset': (0, -3)},
        'CastStart': {'scale': 1.08},
        'CastRelease': {'scale': 1.12},
        'CastRecover': {'scale': 1.02},
        'TurnLeft': {'offset': (-1, -2), 'rotate': -4},
        'TurnRight': {'offset': (1, -2), 'rotate': 4},
        'Hurt': {'offset': (-1, 2), 'dim': 80},
        'Death': {'offset': (0, 6), 'scale': 0.9, 'dim': 140},
        'Corpse': {'offset': (0, 10), 'scale': 0.82, 'dim': 180, 'alpha': 170},
    },
    'ent': {
        'Idle': {},
        'IdleBreath': {'offset': (0, -1)},
        'StepLeft': {'offset': (-1, 0)},
        'StepRight': {'offset': (1, 0)},
        'Walk': {'offset': (1, 0)},
        'WalkAlt': {'offset': (-1, 0)},
        'SlamPrep': {'offset': (-2, -1), 'rotate': -4},
        'SlamHit': {'offset': (3, -2), 'rotate': 5},
        'SlamRecover': {'offset': (1, -1)},
        'TurnLeft': {'offset': (-2, 0), 'rotate': -6},
        'TurnRight': {'offset': (2, -1), 'rotate': 6},
        'Hurt': {'offset': (-1, 2), 'rotate': 6},
        'Death': {'offset': (-8, 10), 'rotate': 78, 'dim': 130},
        'Corpse': {'offset': (-12, 14), 'rotate': 96, 'dim': 170, 'alpha': 220},
    },
    'unicorn': {
        'Idle': {},
        'IdleBreath': {'offset': (0, -1)},
        'Walk': {'offset': (2, 0)},
        'WalkAlt': {'offset': (-2, 0)},
        'ChargePrep': {'offset': (-2, -1), 'rotate': -3},
        'ChargeImpact': {'offset': (3, -2), 'rotate': 5},
        'ChargeRecover': {'offset': (1, -1)},
        'TurnLeft': {'offset': (-2, -1), 'rotate': -5},
        'TurnRight': {'offset': (2, -1), 'rotate': 5},
        'Hurt': {'offset': (-1, 2), 'rotate': 6},
        'Death': {'offset': (-10, 12), 'rotate': 86, 'dim': 130},
        'Corpse': {'offset': (-12, 16), 'rotate': 108, 'dim': 170, 'alpha': 210},
    },
}


def _apply_tint(surface, color):
    tint = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    if len(color) == 3:
        tint.fill((*color, 90))
    else:
        tint.fill(color)
    surface.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _apply_dim(surface, value):
    dim = max(0, min(255, value))
    overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    overlay.fill((dim, dim, dim, 0))
    surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


def _apply_glow(surface, glow_spec):
    color = glow_spec.get('color', (200, 255, 220))
    alpha = glow_spec.get('alpha', 120)
    overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    overlay.fill((*color, alpha))
    surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _render_elf_animation_frame(unit_key, state):
    cache_key = f'elf_anim_{unit_key}_{state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    blueprint = _ELF_ANIMATION_BLUEPRINTS.get(unit_key, {})
    ops = blueprint.get(state) or blueprint.get('Idle', {})

    base = _render_elf_unit(unit_key)
    image = base

    if 'scale' in ops:
        factor = ops['scale']
        width = max(1, int(image.get_width() * factor))
        height = max(1, int(image.get_height() * factor))
        image = pygame.transform.smoothscale(image, (width, height))

    if 'rotate' in ops:
        image = pygame.transform.rotate(image, ops['rotate'])

    if 'flip' in ops:
        fx, fy = ops['flip']
        image = pygame.transform.flip(image, fx, fy)

    target = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    offset_x, offset_y = ops.get('offset', (0, 0))
    rect = image.get_rect(center=(CELL_SIZE // 2 + offset_x, CELL_SIZE // 2 + offset_y))
    target.blit(image, rect)

    if 'tint' in ops:
        _apply_tint(target, ops['tint'])

    if 'dim' in ops:
        _apply_dim(target, ops['dim'])

    if 'glow' in ops:
        _apply_glow(target, ops['glow'])

    if ops.get('alpha') is not None:
        target.set_alpha(ops['alpha'])

    _texture_cache[cache_key] = target
    return target


def load_elf_archer_texture(animation_state='Idle'):
    """Полноценная система анимаций для эльфийского лучника по образцу людей."""
    cache_key = f'elf_archer_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def outlined_rect(target, rect, fill, outline=(36, 48, 38), width=1):
        pygame.draw.rect(target, fill, rect)
        pygame.draw.rect(target, outline, rect, width)

    def gradient_band(target, rect, top_color, bottom_color):
        x, y, w, h = rect
        for i in range(h):
            t = i / max(1, h - 1)
            color = (
                int(top_color[0] + (bottom_color[0] - top_color[0]) * t),
                int(top_color[1] + (bottom_color[1] - top_color[1]) * t),
                int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
            )
            pygame.draw.line(target, color, (x, y + i), (x + w - 1, y + i))

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        bow_angle=-6,
        bow_raise=0,
        head_tilt=0,
        crouch=0,
        show_dagger=False,
        dagger_phase=0,
        lighten=False,
        string_pull=0,
        arrow_visible=True,
        motion_blur=False,
        head_offset_x=0,
        head_offset_y=0,
        bow_offset_x=0,
        bow_offset_y=0,
        quiver_sway=0,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        bow = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        quiver = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (32, 40, 36, 170)
        tunic_dark = (56, 96, 68)
        tunic_mid = (82, 150, 102)
        tunic_light = (130, 200, 150)
        leather_dark = (88, 72, 52)
        leather_mid = (120, 96, 68)
        leather_light = (152, 124, 84)
        boots_dark = (68, 56, 44)
        boots_light = (96, 80, 64)
        skin = (228, 238, 206)
        silver = (198, 214, 226)
        gold = (220, 204, 140)
        hair = (86, 168, 120)
        wood = (116, 88, 64)

        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        back_leg_rect = pygame.Rect(12 + leg_back_shift, 24 + base_y, 6, 11)
        front_leg_rect = pygame.Rect(22 + leg_front_shift, 24 + base_y - 1, 7, 12)
        outlined_rect(body, back_leg_rect, boots_dark, outline=(48, 40, 32))
        outlined_rect(body, front_leg_rect, boots_light, outline=(48, 40, 32))

        gradient_band(body, (12, 19 + base_y, 17, 5), leather_mid, leather_dark)
        pygame.draw.rect(body, (48, 40, 32), (12, 19 + base_y, 17, 5), 1)

        torso_rect = pygame.Rect(13 + torso_shift, 10 + base_y, 18, 12)
        gradient_band(body, torso_rect, tunic_light, tunic_dark)
        pygame.draw.rect(body, (40, 52, 42), torso_rect, 1)
        pygame.draw.rect(body, tunic_mid, (13 + torso_shift, 14 + base_y, 18, 3))

        pygame.draw.ellipse(body, tunic_mid, (10 + torso_shift, 10 + base_y, 10, 6))
        pygame.draw.ellipse(body, tunic_light, (11 + torso_shift, 11 + base_y, 8, 3))
        pygame.draw.rect(body, leather_mid, (11 + torso_shift, 12 + base_y, 5, 12))
        pygame.draw.rect(body, (40, 52, 42), (11 + torso_shift, 12 + base_y, 5, 12), 1)

        front_arm = pygame.Rect(19 + torso_shift, 14 + base_y, 10, 4)
        back_arm = pygame.Rect(13 + torso_shift, 15 + base_y, 8, 4)
        outlined_rect(body, back_arm, leather_mid)
        outlined_rect(body, front_arm, leather_light)

        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 21 + torso_shift + head_offset_x
        head_y = 6 + base_y + head_tilt + head_offset_y
        pygame.draw.ellipse(head_surface, skin, (head_x - 6, head_y - 6, 12, 12))
        pygame.draw.polygon(head_surface, skin, [(head_x - 8, head_y), (head_x - 12, head_y - 6), (head_x - 2, head_y - 4)])
        pygame.draw.polygon(head_surface, skin, [(head_x + 8, head_y), (head_x + 12, head_y - 6), (head_x + 2, head_y - 4)])
        pygame.draw.ellipse(head_surface, hair, (head_x - 7, head_y - 8, 14, 6))
        pygame.draw.circle(head_surface, (40, 80, 50), (head_x - 2, head_y - 1), 1)
        pygame.draw.circle(head_surface, (40, 80, 50), (head_x + 2, head_y - 1), 1)
        body.blit(head_surface, (0, 0))

        quiver_x = 8 + quiver_sway
        outlined_rect(quiver, pygame.Rect(quiver_x, 12 + base_y, 5, 13), leather_dark)
        pygame.draw.rect(quiver, leather_mid, (quiver_x, 20 + base_y, 5, 4))
        for i in range(3):
            pygame.draw.line(quiver, silver, (quiver_x + 1 + i, 11 + base_y), (quiver_x + 1 + i, 16 + base_y), 1)

        if show_dagger:
            dagger = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            if dagger_phase == 0:
                pygame.draw.rect(dagger, leather_dark, (20 + torso_shift, 15 + base_y, 2, 6))
                pygame.draw.polygon(dagger, silver, [(21 + torso_shift, 15 + base_y),
                                                    (24 + torso_shift, 16 + base_y),
                                                    (21 + torso_shift, 19 + base_y)])
            elif dagger_phase == 1:
                pygame.draw.rect(dagger, leather_dark, (26 + torso_shift, 14 + base_y, 3, 8))
                pygame.draw.polygon(dagger, silver, [(29 + torso_shift, 15 + base_y),
                                                    (35 + torso_shift, 13 + base_y),
                                                    (30 + torso_shift, 19 + base_y)])
            else:
                pygame.draw.rect(dagger, leather_dark, (23 + torso_shift, 14 + base_y, 2, 7))
                pygame.draw.polygon(dagger, silver, [(24 + torso_shift, 14 + base_y),
                                                    (27 + torso_shift, 15 + base_y),
                                                    (24 + torso_shift, 18 + base_y)])
            body.blit(dagger, (0, 0))

        bow_center_x = 24
        bow_center_y = 18 + bow_raise + base_y
        bow_arc_rect = (4, 4, 28, 36)
        pygame.draw.arc(bow, wood, bow_arc_rect, 0.12, 3.02, 3)
        pygame.draw.line(bow, wood, (10, 22), (30, 14), 2)
        string_base_y = bow_center_y
        pull = max(-4, min(6, string_pull))
        mid_y = string_base_y - int(pull * 1.5)
        left_anchor = (12, string_base_y)
        right_anchor = (30, string_base_y - 8)
        pygame.draw.line(bow, (70, 56, 42), left_anchor, (24, mid_y), 2)
        pygame.draw.line(bow, (70, 56, 42), (24, mid_y), right_anchor, 2)

        if arrow_visible:
            arrow_rect = pygame.Rect(22, string_base_y - 3, 6, 2)
            pygame.draw.rect(bow, wood, arrow_rect)
            pygame.draw.rect(bow, (64, 48, 32), arrow_rect, 1)
            pygame.draw.polygon(bow, silver, [(28, string_base_y - 2), (32, string_base_y - 2), (30, string_base_y)])

        body.blit(quiver, (0, 0))
        final_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        final_surface.blit(body, (0, 0))

        if bow_angle != 0:
            bow_rotated = pygame.transform.rotate(bow, bow_angle)
            bow_rect = bow_rotated.get_rect(
                center=(
                    CELL_SIZE // 2 + bow_offset_x,
                    CELL_SIZE // 2 - 4 + bow_raise + bow_offset_y,
                )
            )
            final_surface.blit(bow_rotated, bow_rect.topleft)
        else:
            final_surface.blit(bow, (bow_offset_x, bow_offset_y))

        if lighten:
            wash = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            wash.fill((255, 250, 240, 70))
            final_surface.blit(wash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        if motion_blur:
            blur = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.ellipse(
                blur,
                (240, 250, 220, 70),
                (16 + bow_offset_x, 14 + bow_raise + base_y + bow_offset_y, 24, 10),
            )
            final_surface.blit(blur, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return final_surface

    attack_draw = dict(
        torso_shift=-3,
        bow_angle=-24,
        bow_raise=-5,
        head_tilt=-3,
        string_pull=6,
        bow_offset_x=-1,
        bow_offset_y=-1,
    )
    attack_aim = dict(
        torso_shift=-2,
        bow_angle=-8,
        bow_raise=-3,
        head_tilt=-1,
        string_pull=6,
        head_offset_x=-1,
        head_offset_y=-1,
    )
    attack_release = dict(
        torso_shift=-1,
        bow_angle=10,
        bow_raise=2,
        head_tilt=0,
        string_pull=-3,
        arrow_visible=False,
        motion_blur=False,
    )
    attack_follow = dict(
        torso_shift=0,
        bow_angle=18,
        bow_raise=4,
        head_tilt=1,
        string_pull=-3,
        arrow_visible=False,
        motion_blur=False,
        bow_offset_x=2,
        bow_offset_y=1,
    )
    attack_recover = dict(
        torso_shift=-1,
        bow_angle=-6,
        bow_raise=-1,
        head_tilt=0,
        string_pull=2,
        arrow_visible=False,
    )

    melee_guard = dict(
        torso_shift=-3,
        bow_angle=-14,
        bow_raise=6,
        head_tilt=-2,
        show_dagger=True,
        dagger_phase=0,
        string_pull=2,
        arrow_visible=False,
        quiver_sway=-1,
    )
    melee_windup = dict(
        torso_shift=-2,
        bow_angle=4,
        bow_raise=7,
        head_tilt=0,
        show_dagger=True,
        dagger_phase=1,
        string_pull=2,
        arrow_visible=False,
        motion_blur=True,
    )
    melee_strike = dict(
        torso_shift=-1,
        bow_angle=18,
        bow_raise=6,
        head_tilt=1,
        show_dagger=True,
        dagger_phase=1,
        string_pull=-3,
        arrow_visible=False,
        motion_blur=True,
        bow_offset_x=2,
    )
    melee_follow = dict(
        torso_shift=-1,
        bow_angle=10,
        bow_raise=4,
        head_tilt=0,
        show_dagger=True,
        dagger_phase=2,
        string_pull=-2,
        arrow_visible=False,
    )
    melee_recover = dict(
        torso_shift=-2,
        bow_angle=-6,
        bow_raise=2,
        head_tilt=-1,
        show_dagger=True,
        dagger_phase=2,
        string_pull=1,
        arrow_visible=False,
    )

    hurt_start = dict(
        torso_shift=-3,
        crouch=3,
        bow_angle=-6,
        bow_raise=3,
        head_tilt=-4,
        string_pull=1,
        arrow_visible=True,
        head_offset_x=-1,
    )
    hurt_hold = dict(
        torso_shift=-2,
        crouch=4,
        bow_angle=0,
        bow_raise=4,
        head_tilt=-3,
        string_pull=0,
        arrow_visible=False,
    )
    hurt_recover = dict(
        torso_shift=-1,
        crouch=2,
        bow_angle=-4,
        bow_raise=1,
        head_tilt=-1,
        string_pull=1,
        arrow_visible=False,
    )

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=-1, torso_shift=0, bow_angle=-6, bow_raise=-1, head_tilt=0, string_pull=1),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-2, torso_shift=-1, bow_angle=-4, bow_raise=-2, head_tilt=-1, string_pull=2, head_offset_y=-1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-3, torso_shift=-1, bow_angle=-4, bow_raise=-1, head_tilt=-1, string_pull=0),
        'WalkAlt': dict(leg_front_shift=-1, leg_back_shift=2, torso_shift=1, bow_angle=-2, bow_raise=0, head_tilt=1, string_pull=0),
        'Attack': attack_draw,
        'AttackDraw': attack_draw,
        'Attack02': attack_aim,
        'AttackAim': attack_aim,
        'Attack03': attack_release,
        'AttackRelease': attack_release,
        'AttackFollow': attack_follow,
        'AttackRecover': attack_recover,
        'MeleePrep': melee_guard,
        'MeleeGuard': melee_guard,
        'MeleeWindup': melee_windup,
        'MeleeStrike': melee_strike,
        'MeleeFollow': melee_follow,
        'MeleeRecover': melee_recover,
        'Hurt': hurt_start,
        'HurtStart': hurt_start,
        'HurtHold': hurt_hold,
        'HurtRecover': hurt_recover,
        'Death': dict(torso_shift=-3, crouch=5, bow_angle=20, bow_raise=6, head_tilt=6, string_pull=-2, arrow_visible=False, motion_blur=False, lighten=True),
        'Corpse': dict(torso_shift=-3, crouch=6, bow_angle=22, bow_raise=6, head_tilt=6, string_pull=-2, arrow_visible=False),
    }

    params = params_map.get(animation_state, params_map['Idle'])
    surface = build_pose(**params)

    # Убрано красное перепание для эльфов
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 70)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-6, 10))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 88)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 6))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_elf_scout_texture(animation_state='Idle'):
    """Полноценная система анимаций для эльфийского разведчика по образцу людей."""
    cache_key = f'elf_scout_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def outlined_rect(target, rect, fill, outline=(36, 48, 38), width=1):
        pygame.draw.rect(target, fill, rect)
        pygame.draw.rect(target, outline, rect, width)

    def gradient_band(target, rect, top_color, bottom_color):
        x, y, w, h = rect
        for i in range(h):
            t = i / max(1, h - 1)
            color = (
                int(top_color[0] + (bottom_color[0] - top_color[0]) * t),
                int(top_color[1] + (bottom_color[1] - top_color[1]) * t),
                int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
            )
            pygame.draw.line(target, color, (x, y + i), (x + w - 1, y + i))

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        dagger1_angle=0,
        dagger1_raise=0,
        dagger1_reach=0,
        dagger2_angle=0,
        dagger2_raise=0,
        dagger2_reach=0,
        motion_blur=False,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        daggers = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (32, 40, 36, 170)
        tunic_dark = (72, 118, 88)
        tunic_mid = (100, 160, 116)
        tunic_light = (130, 200, 150)
        leather_dark = (88, 72, 52)
        leather_mid = (120, 96, 68)
        leather_light = (152, 124, 84)
        boots_dark = (68, 56, 44)
        boots_light = (96, 80, 64)
        skin = (228, 238, 206)
        silver = (198, 214, 226)
        hair = (92, 156, 120)

        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        back_leg_rect = pygame.Rect(12 + leg_back_shift, 24 + base_y, 6, 11)
        front_leg_rect = pygame.Rect(22 + leg_front_shift, 24 + base_y - 1, 7, 12)
        outlined_rect(body, back_leg_rect, boots_dark, outline=(48, 40, 32))
        outlined_rect(body, front_leg_rect, boots_light, outline=(48, 40, 32))

        gradient_band(body, (12, 19 + base_y, 17, 5), leather_mid, leather_dark)
        pygame.draw.rect(body, (48, 40, 32), (12, 19 + base_y, 17, 5), 1)

        torso_rect = pygame.Rect(13 + torso_shift, 10 + base_y, 18, 12)
        gradient_band(body, torso_rect, tunic_light, tunic_dark)
        pygame.draw.rect(body, (40, 52, 42), torso_rect, 1)
        pygame.draw.rect(body, tunic_mid, (13 + torso_shift, 14 + base_y, 18, 3))

        pygame.draw.ellipse(body, tunic_mid, (10 + torso_shift, 10 + base_y, 10, 6))
        pygame.draw.ellipse(body, tunic_light, (11 + torso_shift, 11 + base_y, 8, 3))
        pygame.draw.rect(body, leather_mid, (11 + torso_shift, 12 + base_y, 5, 12))
        pygame.draw.rect(body, (40, 52, 42), (11 + torso_shift, 12 + base_y, 5, 12), 1)

        front_arm = pygame.Rect(19 + torso_shift, 14 + base_y, 10, 4)
        back_arm = pygame.Rect(13 + torso_shift, 15 + base_y, 8, 4)
        outlined_rect(body, back_arm, leather_mid)
        outlined_rect(body, front_arm, leather_light)

        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 21 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(head_surface, skin, (head_x - 6, head_y - 6, 12, 12))
        pygame.draw.polygon(head_surface, skin, [(head_x - 8, head_y), (head_x - 12, head_y - 6), (head_x - 2, head_y - 4)])
        pygame.draw.polygon(head_surface, skin, [(head_x + 8, head_y), (head_x + 12, head_y - 6), (head_x + 2, head_y - 4)])
        pygame.draw.ellipse(head_surface, hair, (head_x - 7, head_y - 8, 14, 6))
        pygame.draw.circle(head_surface, (40, 80, 50), (head_x - 2, head_y - 1), 1)
        pygame.draw.circle(head_surface, (40, 80, 50), (head_x + 2, head_y - 1), 1)
        body.blit(head_surface, (0, 0))

        dagger1_start = (28, 14 + base_y + dagger1_raise)
        angle1_rad = math.radians(dagger1_angle)
        dagger1_length = 10 + dagger1_reach
        dagger1_end = (
            dagger1_start[0] + int(dagger1_length * math.cos(angle1_rad)),
            dagger1_start[1] - int(dagger1_length * math.sin(angle1_rad)),
        )
        pygame.draw.line(daggers, leather_dark, dagger1_start, dagger1_end, 3)
        pygame.draw.polygon(daggers, silver, [
            dagger1_end,
            (dagger1_end[0] + int(3 * math.cos(angle1_rad)), dagger1_end[1] - int(3 * math.sin(angle1_rad))),
            (dagger1_end[0] + int(2 * math.cos(angle1_rad + math.pi/2)), dagger1_end[1] - int(2 * math.sin(angle1_rad + math.pi/2))),
        ])

        dagger2_start = (16, 28 + base_y + dagger2_raise)
        angle2_rad = math.radians(dagger2_angle)
        dagger2_length = 10 + dagger2_reach
        dagger2_end = (
            dagger2_start[0] + int(dagger2_length * math.cos(angle2_rad)),
            dagger2_start[1] - int(dagger2_length * math.sin(angle2_rad)),
        )
        pygame.draw.line(daggers, leather_dark, dagger2_start, dagger2_end, 3)
        pygame.draw.polygon(daggers, silver, [
            dagger2_end,
            (dagger2_end[0] + int(3 * math.cos(angle2_rad)), dagger2_end[1] - int(3 * math.sin(angle2_rad))),
            (dagger2_end[0] + int(2 * math.cos(angle2_rad + math.pi/2)), dagger2_end[1] - int(2 * math.sin(angle2_rad + math.pi/2))),
        ])

        body.blit(daggers, (0, 0))

        if motion_blur:
            blur = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.ellipse(
                blur,
                (240, 250, 220, 80),
                (14, 12, 24, 18),
            )
            body.blit(blur, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return body

    params_map = {
        'Idle': dict(dagger1_angle=94, dagger1_raise=0, dagger1_reach=2, dagger2_angle=94, dagger2_raise=0, dagger2_reach=2),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-2, torso_shift=-1, head_tilt=-1, dagger1_angle=98, dagger1_raise=1, dagger2_angle=98, dagger2_raise=1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-3, torso_shift=-1, head_tilt=-1, dagger1_angle=104, dagger1_raise=2, dagger1_reach=3, dagger2_angle=86, dagger2_raise=2, dagger2_reach=3),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=1, torso_shift=1, head_tilt=1, dagger1_angle=86, dagger1_raise=1, dagger1_reach=3, dagger2_angle=104, dagger2_raise=1, dagger2_reach=3),
        'AttackPrep': dict(torso_shift=-3, head_tilt=-2, dagger1_angle=48, dagger1_raise=6, dagger1_reach=6, dagger2_angle=94, dagger2_raise=0),
        'AttackStrike': dict(torso_shift=-1, head_tilt=0, dagger1_angle=32, dagger1_raise=-3, dagger1_reach=10, motion_blur=True, dagger2_angle=70, dagger2_raise=2, dagger2_reach=4),
        'AttackRecover': dict(torso_shift=-2, head_tilt=-1, dagger1_angle=88, dagger1_raise=3, dagger1_reach=4, dagger2_angle=94, dagger2_raise=0),
        'Hurt': dict(crouch=3, torso_shift=-3, head_tilt=-4, dagger1_angle=70, dagger1_raise=5, dagger2_angle=94, dagger2_raise=2),
        'HurtStart': dict(crouch=3, torso_shift=-3, head_tilt=-4, dagger1_angle=70, dagger1_raise=5, dagger2_angle=94, dagger2_raise=2),
        'HurtHold': dict(crouch=4, torso_shift=-2, head_tilt=-3, dagger1_angle=94, dagger1_raise=6, dagger2_angle=94, dagger2_raise=4),
        'HurtRecover': dict(crouch=2, torso_shift=-1, head_tilt=-1, dagger1_angle=86, dagger1_raise=3, dagger2_angle=94, dagger2_raise=0),
        'TurnLeft': dict(torso_shift=-1, head_tilt=-1, dagger1_angle=98, dagger1_raise=1, dagger2_angle=90, dagger2_raise=1),
        'TurnRight': dict(torso_shift=1, head_tilt=1, dagger1_angle=90, dagger1_raise=1, dagger2_angle=98, dagger2_raise=1),
        'Death': dict(crouch=6, torso_shift=-4, head_tilt=6, dagger1_angle=74, dagger1_raise=8, dagger2_angle=110, dagger2_raise=8),
        'Corpse': dict(crouch=6, torso_shift=-4, head_tilt=6, dagger1_angle=98, dagger1_raise=8, dagger2_angle=98, dagger2_raise=8),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    # Убрано красное перепание для эльфов
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 78)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 4))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 96)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-14, 8))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_skeleton_texture(animation_state='Idle'):
    """Процедурная анимация скелета в стиле новой нежити: несколько поз (idle, walk, attack, hurt, death)."""
    cache_key = f'skeleton_v3_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        sword_angle=0,
        sword_raise=0,
        sword_reach=0,
        arm_swing=0,
    ):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        bone = (215, 220, 230)
        bone_dark = (170, 175, 185)
        shadow = (26, 26, 38, 185)

        base_y = crouch

        # Тень
        pygame.draw.ellipse(surf, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        # Тело
        body = pygame.Rect(16 + torso_shift, 16 + base_y, 18, 14)
        pygame.draw.rect(surf, bone, body)
        pygame.draw.rect(surf, bone_dark, body, 2)
        # Рёбра
        for i in range(3):
            pygame.draw.line(surf, bone_dark, (18 + torso_shift, 18 + base_y + i * 3), (32 + torso_shift, 18 + base_y + i * 3), 1)

        # Череп
        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 23 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(head_surface, bone, (head_x - 7, head_y - 4, 14, 10))
        pygame.draw.ellipse(head_surface, bone_dark, (head_x - 5, head_y - 2, 10, 6))
        # Глазницы
        pygame.draw.circle(head_surface, (10, 10, 30), (head_x - 3, head_y), 2)
        pygame.draw.circle(head_surface, (10, 10, 30), (head_x + 3, head_y), 2)
        pygame.draw.circle(head_surface, (120, 80, 200), (head_x - 3, head_y), 1)
        pygame.draw.circle(head_surface, (120, 80, 200), (head_x + 3, head_y), 1)
        # Челюсть
        pygame.draw.arc(head_surface, (40, 40, 60), (head_x - 4, head_y + 2, 8, 4), 0, 3.14, 2)
        surf.blit(head_surface, (0, 0))

        # Ноги
        left_leg = pygame.Rect(16 + torso_shift, 28 + base_y, 5, 10)
        right_leg = pygame.Rect(27 + torso_shift, 28 + base_y, 5, 10)
        pygame.draw.rect(surf, bone, left_leg)
        pygame.draw.rect(surf, bone_dark, left_leg, 1)
        pygame.draw.rect(surf, bone, right_leg)
        pygame.draw.rect(surf, bone_dark, right_leg, 1)
        # Ступни
        pygame.draw.rect(surf, bone, (left_leg.x, left_leg.bottom - 2, left_leg.width, 2))
        pygame.draw.rect(surf, bone, (right_leg.x, right_leg.bottom - 2, right_leg.width, 2))

        # Руки + меч
        arms = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Левая рука (щит/свободная)
        left_arm_y = 20 + base_y + arm_swing
        pygame.draw.line(arms, bone, (16 + torso_shift, 20 + base_y), (12 + torso_shift, left_arm_y + 6), 2)
        # Правая рука с мечом
        right_arm_y = 20 + base_y - arm_swing
        pygame.draw.line(arms, bone, (30 + torso_shift, 20 + base_y), (34 + torso_shift, right_arm_y + 4), 2)
        # Меч
        sword_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(sword_surface, bone_dark, (30, 14 + base_y + sword_raise, 6, 18))
        pygame.draw.polygon(sword_surface, (200, 200, 220), [(30, 14 + base_y + sword_raise),
                                                             (33, 10 + base_y + sword_raise),
                                                             (36, 14 + base_y + sword_raise)])
        if sword_angle or sword_reach:
            sword_rot = pygame.transform.rotate(sword_surface, sword_angle)
            rect = sword_rot.get_rect(center=(CELL_SIZE // 2 + 4 + sword_reach, CELL_SIZE // 2))
            arms.blit(sword_rot, rect.topleft)
        else:
            arms.blit(sword_surface, (0, 0))

        surf.blit(arms, (0, 0))
        return surf

    params_map = {
        'Idle': dict(torso_shift=0, head_tilt=0, crouch=0, sword_angle=0, sword_raise=0, sword_reach=0, arm_swing=0),
        'IdleBreath': dict(torso_shift=-1, head_tilt=-1, crouch=0, sword_angle=2, sword_raise=-1, sword_reach=0, arm_swing=1),
        'Walk': dict(torso_shift=-1, head_tilt=0, crouch=0, sword_angle=5, sword_raise=-1, sword_reach=0, arm_swing=2),
        'WalkAlt': dict(torso_shift=1, head_tilt=0, crouch=0, sword_angle=-5, sword_raise=-1, sword_reach=0, arm_swing=-2),
        'AttackPrep': dict(torso_shift=-2, head_tilt=-2, crouch=1, sword_angle=-25, sword_raise=-3, sword_reach=-2, arm_swing=-1),
        'AttackStrike': dict(torso_shift=1, head_tilt=1, crouch=-1, sword_angle=20, sword_raise=-4, sword_reach=4, arm_swing=2),
        'AttackRecover': dict(torso_shift=0, head_tilt=0, crouch=1, sword_angle=5, sword_raise=-1, sword_reach=0, arm_swing=0),
        'Hurt': dict(torso_shift=-1, head_tilt=-4, crouch=3, sword_angle=12, sword_raise=1, sword_reach=-1, arm_swing=-3),
        'Death': dict(torso_shift=-2, head_tilt=5, crouch=5, sword_angle=40, sword_raise=3, sword_reach=-3, arm_swing=-4),
        'Corpse': dict(torso_shift=-2, head_tilt=5, crouch=6, sword_angle=45, sword_raise=3, sword_reach=-3, arm_swing=-4),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_monk_texture(animation_state='Idle'):
    """Процедурная анимация монаха: спокойные позы, лёгкие шаги и удар посохом."""
    cache_key = f'monk_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        staff_angle=0,
        staff_raise=0,
        prayer_hands=False,
    ):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (38, 34, 30, 170)
        robe = (135, 110, 80)
        robe_dark = (100, 80, 60)
        skin = (230, 210, 180)
        skin_dark = (200, 180, 150)
        cord = (200, 190, 150)

        base_y = crouch
        pygame.draw.ellipse(surf, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        # Ноги под робой
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(surf, robe_dark, left_leg)
        pygame.draw.rect(surf, robe_dark, right_leg)

        # Роба
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 14)
        pygame.draw.rect(surf, robe, torso)
        pygame.draw.rect(surf, robe_dark, torso, 2)
        # Пояс
        pygame.draw.rect(surf, cord, (torso.x, torso.y + 9, torso.w, 2))

        # Голова
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        head_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(head_surf, skin, (head_x - 6, head_y, 12, 10))
        pygame.draw.ellipse(head_surf, skin_dark, (head_x - 4, head_y + 2, 8, 6))
        # Глаза
        pygame.draw.circle(head_surf, (40, 30, 20), (head_x - 2, head_y + 4), 1)
        pygame.draw.circle(head_surf, (40, 30, 20), (head_x + 2, head_y + 4), 1)
        # Капюшон
        pygame.draw.ellipse(head_surf, robe_dark, (head_x - 7, head_y - 2, 14, 8), 2)
        surf.blit(head_surf, (0, 0))

        # Руки
        arms = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        if prayer_hands:
            # Руки сложены у груди
            pygame.draw.ellipse(arms, skin, (18 + torso_shift, 18 + base_y, 8, 6))
            pygame.draw.ellipse(arms, skin_dark, (19 + torso_shift, 19 + base_y, 6, 4))
        else:
            left_arm = pygame.Rect(12 + torso_shift, 18 + base_y, 4, 8)
            right_arm = pygame.Rect(26 + torso_shift, 18 + base_y, 4, 8)
            pygame.draw.rect(arms, skin, left_arm)
            pygame.draw.rect(arms, skin_dark, left_arm, 1)
            pygame.draw.rect(arms, skin, right_arm)
            pygame.draw.rect(arms, skin_dark, right_arm, 1)

        # Посох
        staff_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.line(
            staff_surf,
            (120, 90, 60),
            (26, 12 + base_y + staff_raise),
            (30, 40 + base_y),
            3,
        )
        pygame.draw.circle(staff_surf, (220, 210, 150), (26, 12 + base_y + staff_raise), 3)
        if staff_angle:
            staff_rot = pygame.transform.rotate(staff_surf, staff_angle)
            rect = staff_rot.get_rect(center=(CELL_SIZE // 2 + 6, CELL_SIZE // 2))
            arms.blit(staff_rot, rect.topleft)
        else:
            arms.blit(staff_surf, (0, 0))

        surf.blit(arms, (0, 0))
        return surf

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, staff_angle=0, staff_raise=0, prayer_hands=True),
        'IdleBreath': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-1, head_tilt=-1, crouch=0, staff_angle=2, staff_raise=-1, prayer_hands=True),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, staff_angle=4, staff_raise=-1, prayer_hands=False),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, staff_angle=-4, staff_raise=-1, prayer_hands=False),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, staff_angle=-20, staff_raise=-4, prayer_hands=False),
        'AttackStrike': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=1, head_tilt=1, crouch=-1, staff_angle=10, staff_raise=-6, prayer_hands=False),
        'AttackRecover': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, staff_angle=0, staff_raise=-1, prayer_hands=True),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, staff_angle=8, staff_raise=1, prayer_hands=False),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-3, head_tilt=5, crouch=5, staff_angle=20, staff_raise=3, prayer_hands=False),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-3, head_tilt=5, crouch=6, staff_angle=22, staff_raise=3, prayer_hands=False),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 88)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_angel_texture(animation_state='Idle'):
    """Процедурная анимация ангела: парение, шаги и рубящий удар мечом."""
    cache_key = f'angel_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        wing_flap=0,
        sword_angle=0,
        sword_raise=0,
        sword_reach=0,
    ):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (200, 210, 230, 120)
        armor = (205, 210, 235)
        armor_shadow = (160, 170, 200)
        cloth = (230, 235, 250)
        skin = (235, 220, 200)
        hair = (245, 215, 155)
        gold = (230, 200, 120)

        base_y = crouch
        pygame.draw.ellipse(surf, shadow, (6, CELL_SIZE - 10 - base_y, CELL_SIZE - 12, 5))

        # Ноги
        left_leg = pygame.Rect(16 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 25 + base_y, 6, 11)
        pygame.draw.rect(surf, armor, left_leg)
        pygame.draw.rect(surf, armor_shadow, left_leg, 1)
        pygame.draw.rect(surf, armor, right_leg)
        pygame.draw.rect(surf, armor_shadow, right_leg, 1)

        # Тело / доспех
        torso = pygame.Rect(15 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(surf, armor, torso)
        pygame.draw.rect(surf, armor_shadow, torso, 2)
        pygame.draw.rect(surf, cloth, (torso.x + 3, torso.y + 2, torso.w - 6, torso.h - 4))

        # Голова
        head_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 23 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(head_surf, skin, (head_x - 6, head_y, 12, 10))
        pygame.draw.ellipse(head_surf, (220, 205, 190), (head_x - 4, head_y + 2, 8, 6))
        pygame.draw.circle(head_surf, (40, 30, 20), (head_x - 2, head_y + 4), 1)
        pygame.draw.circle(head_surf, (40, 30, 20), (head_x + 2, head_y + 4), 1)
        # Волосы
        pygame.draw.ellipse(head_surf, hair, (head_x - 7, head_y - 2, 14, 6))
        # Нимб
        pygame.draw.ellipse(head_surf, (255, 245, 200), (head_x - 8, head_y - 6, 16, 4), 1)
        surf.blit(head_surf, (0, 0))

        # Крылья
        wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        flap_y = int(wing_flap * 1.5)
        pygame.draw.ellipse(wings, (250, 250, 255), (4, 14 + flap_y, 12, 18))
        pygame.draw.ellipse(wings, (230, 235, 250), (4, 14 + flap_y, 12, 18), 2)
        pygame.draw.ellipse(wings, (250, 250, 255), (28, 14 - flap_y, 12, 18))
        pygame.draw.ellipse(wings, (230, 235, 250), (28, 14 - flap_y, 12, 18), 2)
        surf.blit(wings, (0, 0))

        # Руки и меч
        arms = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        left_arm = pygame.Rect(14 + torso_shift, 18 + base_y, 4, 8)
        right_arm = pygame.Rect(26 + torso_shift, 18 + base_y, 4, 8)
        pygame.draw.rect(arms, skin, left_arm)
        pygame.draw.rect(arms, (210, 195, 180), left_arm, 1)
        pygame.draw.rect(arms, skin, right_arm)
        pygame.draw.rect(arms, (210, 195, 180), right_arm, 1)

        sword = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(sword, (230, 230, 245), (28, 16 + base_y + sword_raise, 4, 14))
        pygame.draw.rect(sword, gold, (26, 14 + base_y + sword_raise, 8, 3))
        pygame.draw.polygon(sword, (250, 250, 255), [(30, 14 + base_y + sword_raise),
                                                     (28, 10 + base_y + sword_raise),
                                                     (32, 10 + base_y + sword_raise)])
        if sword_angle or sword_reach:
            rot = pygame.transform.rotate(sword, sword_angle)
            rect = rot.get_rect(center=(CELL_SIZE // 2 + 6 + sword_reach, CELL_SIZE // 2))
            arms.blit(rot, rect.topleft)
        else:
            arms.blit(sword, (0, 0))

        surf.blit(arms, (0, 0))
        return surf

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, wing_flap=0, sword_angle=0, sword_raise=0, sword_reach=0),
        'IdleBreath': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-1, head_tilt=-1, crouch=0, wing_flap=1, sword_angle=2, sword_raise=-1, sword_reach=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, wing_flap=2, sword_angle=4, sword_raise=-1, sword_reach=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, wing_flap=-2, sword_angle=-4, sword_raise=-1, sword_reach=0),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, wing_flap=-1, sword_angle=-25, sword_raise=-3, sword_reach=-2),
        'AttackStrike': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=2, head_tilt=1, crouch=-1, wing_flap=3, sword_angle=15, sword_raise=-5, sword_reach=4),
        'AttackRecover': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, wing_flap=1, sword_angle=4, sword_raise=-1, sword_reach=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-4, crouch=2, wing_flap=-2, sword_angle=8, sword_raise=1, sword_reach=-1),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-3, head_tilt=5, crouch=5, wing_flap=-3, sword_angle=25, sword_raise=3, sword_reach=-3),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-3, head_tilt=5, crouch=6, wing_flap=-3, sword_angle=28, sword_raise=3, sword_reach=-3),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 88)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_cavalryman_texture(animation_state='Idle'):
    """Процедурная анимация кавалериста: скачка и атакующий наскок копьём."""
    cache_key = f'cavalryman_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        horse_phase=0,
        spear_angle=0,
        spear_raise=0,
        spear_reach=0,
    ):
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

        shadow = (40, 32, 24, 170)
        horse_body = (140, 100, 60)
        horse_shadow = (110, 80, 50)
        armor = (180, 170, 160)
        armor_dark = (120, 110, 100)
        metal = (190, 190, 200)
        skin = (230, 210, 185)

        base_y = crouch
        pygame.draw.ellipse(surf, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))

        # Тело коня
        pygame.draw.ellipse(surf, horse_body, (6, 22 + base_y, 28, 14))
        pygame.draw.ellipse(surf, horse_shadow, (8, 24 + base_y, 24, 10))
        # Голова коня
        pygame.draw.ellipse(surf, horse_body, (24, 12 + base_y, 10, 10))
        pygame.draw.circle(surf, (0, 0, 0), (28, 16 + base_y), 2)

        # Ноги коня (простая фаза шага)
        phase = horse_phase
        for i, x in enumerate((10, 16, 22, 28)):
            dy = (phase if i % 2 == 0 else -phase)
            pygame.draw.rect(surf, horse_body, (x, 30 + base_y + dy, 3, 10))

        # Всадник - торс
        torso = pygame.Rect(14 + torso_shift, 12 + base_y, 12, 12)
        pygame.draw.rect(surf, armor, torso)
        pygame.draw.rect(surf, armor_dark, torso, 2)
        # Всадник - голова
        pygame.draw.ellipse(surf, skin, (16 + torso_shift, 6 + base_y + head_tilt, 8, 8))
        pygame.draw.circle(surf, (0, 0, 0), (18 + torso_shift, 10 + base_y + head_tilt), 1)
        pygame.draw.circle(surf, (0, 0, 0), (22 + torso_shift, 10 + base_y + head_tilt), 1)
        # Шлем
        pygame.draw.ellipse(surf, metal, (16 + torso_shift, 4 + base_y + head_tilt, 8, 6))

        # Копьё
        spear = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.line(
            spear,
            (160, 140, 120),
            (26, 10 + base_y + spear_raise),
            (36, 4 + base_y + spear_raise),
            3,
        )
        pygame.draw.polygon(spear, metal, [(36, 2 + base_y + spear_raise),
                                           (38, 4 + base_y + spear_raise),
                                           (36, 6 + base_y + spear_raise)])
        if spear_angle or spear_reach:
            rot = pygame.transform.rotate(spear, spear_angle)
            rect = rot.get_rect(center=(CELL_SIZE // 2 + 4 + spear_reach, CELL_SIZE // 2))
            surf.blit(rot, rect.topleft)
        else:
            surf.blit(spear, (0, 0))

        return surf

    params_map = {
        'Idle': dict(torso_shift=0, head_tilt=0, crouch=0, horse_phase=0, spear_angle=0, spear_raise=0, spear_reach=0),
        'IdleBreath': dict(torso_shift=-1, head_tilt=-1, crouch=0, horse_phase=1, spear_angle=2, spear_raise=-1, spear_reach=0),
        'Walk': dict(torso_shift=-1, head_tilt=0, crouch=0, horse_phase=2, spear_angle=4, spear_raise=-1, spear_reach=0),
        'WalkAlt': dict(torso_shift=1, head_tilt=0, crouch=0, horse_phase=-2, spear_angle=-4, spear_raise=-1, spear_reach=0),
        'AttackPrep': dict(torso_shift=-2, head_tilt=-2, crouch=1, horse_phase=3, spear_angle=-20, spear_raise=-3, spear_reach=-2),
        'AttackStrike': dict(torso_shift=2, head_tilt=1, crouch=-1, horse_phase=4, spear_angle=10, spear_raise=-5, spear_reach=4),
        'AttackRecover': dict(torso_shift=0, head_tilt=0, crouch=0, horse_phase=1, spear_angle=4, spear_raise=-1, spear_reach=0),
        'Hurt': dict(torso_shift=-1, head_tilt=-4, crouch=2, horse_phase=-2, spear_angle=8, spear_raise=1, spear_reach=-1),
        'Death': dict(torso_shift=-2, head_tilt=5, crouch=5, horse_phase=0, spear_angle=25, spear_raise=3, spear_reach=-3),
        'Corpse': dict(torso_shift=-2, head_tilt=5, crouch=6, horse_phase=0, spear_angle=28, spear_raise=3, spear_reach=-3),
    }

    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))

    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 70)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-8, 14))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 12))
        surface = corpse_surface

    _texture_cache[cache_key] = surface
    return surface


def load_dryad_texture(animation_state='Idle'):
    """Полноценная система анимаций для дриады (старшая фея) с перемещением и атакой."""
    cache_key = f'dryad_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        wing_flap=0,
        staff_angle=0,
        staff_raise=0,
        motion_blur=False,
        glow_intensity=0,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        
        shadow = (32, 40, 36, 170)
        fairy_skin = (200, 230, 180)
        fairy_skin_dark = (180, 210, 160)
        dress_light = (120, 200, 140)
        dress_dark = (80, 160, 100)
        hair = (100, 180, 120)
        wood = (100, 140, 80)
        
        base_y = 0
        
        # Тень
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Ноги
        left_leg = pygame.Rect(14 + leg_back_shift, 24 + base_y, 6, 12)
        right_leg = pygame.Rect(26 + leg_front_shift, 24 + base_y, 6, 12)
        pygame.draw.rect(body, dress_light, left_leg)
        pygame.draw.rect(body, dress_dark, left_leg, 1)
        pygame.draw.rect(body, dress_light, right_leg)
        pygame.draw.rect(body, dress_dark, right_leg, 1)
        
        # Тело
        torso = pygame.Rect(15 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, dress_light, torso)
        pygame.draw.rect(body, dress_dark, torso, 1)
        pygame.draw.line(body, dress_dark, (17 + torso_shift, 16 + base_y), (17 + torso_shift, 24 + base_y), 1)
        pygame.draw.line(body, dress_dark, (29 + torso_shift, 16 + base_y), (29 + torso_shift, 24 + base_y), 1)
        
        # Руки
        left_arm = pygame.Rect(13 + torso_shift, 16 + base_y, 4, 10)
        right_arm = pygame.Rect(29 + torso_shift, 16 + base_y, 4, 10)
        pygame.draw.rect(body, fairy_skin, left_arm)
        pygame.draw.rect(body, fairy_skin_dark, left_arm, 1)
        pygame.draw.rect(body, fairy_skin, right_arm)
        pygame.draw.rect(body, fairy_skin_dark, right_arm, 1)
        
        # Голова
        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 23 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(head_surface, fairy_skin, (head_x - 6, head_y - 6, 12, 12))
        pygame.draw.ellipse(head_surface, fairy_skin_dark, (head_x - 4, head_y - 4, 8, 8))
        # Уши-остроконечные
        pygame.draw.polygon(head_surface, fairy_skin, [(head_x - 7, head_y), (head_x - 10, head_y - 6), (head_x - 4, head_y - 3)])
        pygame.draw.polygon(head_surface, fairy_skin, [(head_x + 7, head_y), (head_x + 10, head_y - 6), (head_x + 4, head_y - 3)])
        # Волосы
        pygame.draw.ellipse(head_surface, hair, (head_x - 7, head_y - 8, 14, 6))
        # Глаза
        pygame.draw.circle(head_surface, (50, 100, 70), (head_x - 2, head_y - 1), 1)
        pygame.draw.circle(head_surface, (50, 100, 70), (head_x + 2, head_y - 1), 1)
        body.blit(head_surface, (0, 0))
        
        # Крылья
        wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        wing_offset_y = int(wing_flap * 1.5)
        # Левое крыло
        pygame.draw.ellipse(wings, (180, 240, 200, 150), (8, 14 + wing_offset_y, 12, 16))
        pygame.draw.ellipse(wings, (140, 220, 160, 180), (8, 14 + wing_offset_y, 12, 16), 2)
        # Правое крыло
        pygame.draw.ellipse(wings, (180, 240, 200, 150), (28, 14 - wing_offset_y, 12, 16))
        pygame.draw.ellipse(wings, (140, 220, 160, 180), (28, 14 - wing_offset_y, 12, 16), 2)
        body.blit(wings, (0, 0))
        
        # Посох/жезл
        staff = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        staff_base_x = 30 + torso_shift
        staff_base_y = 20 + base_y + staff_raise
        angle_rad = math.radians(staff_angle)
        staff_length = 20
        staff_end_x = staff_base_x + int(staff_length * math.cos(angle_rad))
        staff_end_y = staff_base_y - int(staff_length * math.sin(angle_rad))
        pygame.draw.line(staff, wood, (staff_base_x, staff_base_y), (staff_end_x, staff_end_y), 3)
        pygame.draw.circle(staff, (160, 240, 180), (int(staff_base_x - 2), int(staff_base_y - 10)), 5)
        pygame.draw.circle(staff, (200, 255, 220), (int(staff_base_x - 2), int(staff_base_y - 10)), 3)
        body.blit(staff, (0, 0))
        
        # Магическое свечение убрано
        
        # Размытие движения убрано (создавало свечение)
        
        return body

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, wing_flap=0, staff_angle=90, staff_raise=0),
        'IdleSway': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, wing_flap=1, staff_angle=92, staff_raise=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, wing_flap=2, staff_angle=92, staff_raise=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, wing_flap=-2, staff_angle=88, staff_raise=0),
        'CastStart': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-1, head_tilt=-2, wing_flap=2, staff_angle=75, staff_raise=-4),
        'CastRelease': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, wing_flap=3, staff_angle=60, staff_raise=-6),
        'CastRecover': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-1, head_tilt=-1, wing_flap=0, staff_angle=90, staff_raise=-2),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, wing_flap=-1, staff_angle=100, staff_raise=2),
        'TurnLeft': dict(leg_front_shift=-1, leg_back_shift=0, torso_shift=-1, head_tilt=-1, wing_flap=-1, staff_angle=95, staff_raise=0),
        'TurnRight': dict(leg_front_shift=0, leg_back_shift=1, torso_shift=1, head_tilt=1, wing_flap=1, staff_angle=85, staff_raise=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, wing_flap=-2, staff_angle=120, staff_raise=4),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, wing_flap=-2, staff_angle=125, staff_raise=4),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 92)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 110)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-14, 16))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_druid_texture(animation_state='Idle'):
    return _render_elf_animation_frame('druid', animation_state)


def load_pixie_texture(animation_state='Idle'):
    """Пикси переименована в Фею - молодая дриада."""
    return _render_elf_animation_frame('fairy', animation_state)

def load_fairy_texture(animation_state='Idle'):
    """Полноценная система анимаций для феи (молодая дриада) с перемещением и атакой."""
    cache_key = f'fairy_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def outlined_rect(target, rect, fill, outline=(36, 48, 38), width=1):
        pygame.draw.rect(target, fill, rect)
        pygame.draw.rect(target, outline, rect, width)

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        hover_offset=0,
        wing_flap=0,
        staff_angle=0,
        staff_raise=0,
        motion_blur=False,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        
        shadow = (32, 40, 36, 170)
        fairy_skin = (220, 245, 200)
        fairy_skin_dark = (200, 225, 180)
        dress_light = (140, 220, 160)
        dress_dark = (100, 180, 120)
        hair = (120, 200, 140)
        wood = (100, 140, 80)
        
        base_y = hover_offset
        
        # Тень
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Ноги - маленькие для молодой феи
        left_leg = pygame.Rect(16 + leg_back_shift, 28 + base_y, 4, 8)
        right_leg = pygame.Rect(26 + leg_front_shift, 28 + base_y, 4, 8)
        pygame.draw.rect(body, dress_light, left_leg)
        pygame.draw.rect(body, dress_dark, left_leg, 1)
        pygame.draw.rect(body, dress_light, right_leg)
        pygame.draw.rect(body, dress_dark, right_leg, 1)
        
        # Тело - меньше для молодой феи
        torso = pygame.Rect(16 + torso_shift, 18 + base_y, 12, 10)
        pygame.draw.rect(body, dress_light, torso)
        pygame.draw.rect(body, dress_dark, torso, 1)
        pygame.draw.line(body, dress_dark, (18 + torso_shift, 20 + base_y), (18 + torso_shift, 26 + base_y), 1)
        pygame.draw.line(body, dress_dark, (26 + torso_shift, 20 + base_y), (26 + torso_shift, 26 + base_y), 1)
        
        # Руки
        left_arm = pygame.Rect(14 + torso_shift, 20 + base_y, 3, 8)
        right_arm = pygame.Rect(29 + torso_shift, 20 + base_y, 3, 8)
        pygame.draw.rect(body, fairy_skin, left_arm)
        pygame.draw.rect(body, fairy_skin_dark, left_arm, 1)
        pygame.draw.rect(body, fairy_skin, right_arm)
        pygame.draw.rect(body, fairy_skin_dark, right_arm, 1)
        
        # Голова - маленькая
        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 22 + torso_shift
        head_y = 8 + base_y + head_tilt
        pygame.draw.ellipse(head_surface, fairy_skin, (head_x - 5, head_y - 5, 10, 10))
        pygame.draw.ellipse(head_surface, fairy_skin_dark, (head_x - 3, head_y - 3, 6, 6))
        # Уши-остроконечные
        pygame.draw.polygon(head_surface, fairy_skin, [(head_x - 6, head_y - 2), (head_x - 8, head_y - 6), (head_x - 4, head_y - 4)])
        pygame.draw.polygon(head_surface, fairy_skin, [(head_x + 6, head_y - 2), (head_x + 8, head_y - 6), (head_x + 4, head_y - 4)])
        # Волосы
        pygame.draw.ellipse(head_surface, hair, (head_x - 6, head_y - 7, 12, 5))
        # Глаза
        pygame.draw.circle(head_surface, (60, 120, 80), (head_x - 2, head_y - 1), 1)
        pygame.draw.circle(head_surface, (60, 120, 80), (head_x + 2, head_y - 1), 1)
        body.blit(head_surface, (0, 0))
        
        # Крылья - большие, с анимацией взмаха
        wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        wing_offset_y = int(wing_flap * 2)
        # Левое крыло
        pygame.draw.ellipse(wings, (200, 250, 220, 140), (4, 14 + wing_offset_y, 14, 18))
        pygame.draw.ellipse(wings, (160, 230, 180, 160), (4, 14 + wing_offset_y, 14, 18), 2)
        # Правое крыло
        pygame.draw.ellipse(wings, (200, 250, 220, 140), (30, 14 - wing_offset_y, 14, 18))
        pygame.draw.ellipse(wings, (160, 230, 180, 160), (30, 14 - wing_offset_y, 14, 18), 2)
        body.blit(wings, (0, 0))
        
        # Посох/жезл
        staff = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        staff_base_x = 32 + torso_shift
        staff_base_y = 22 + base_y + staff_raise
        angle_rad = math.radians(staff_angle)
        staff_length = 16
        staff_end_x = staff_base_x + int(staff_length * math.cos(angle_rad))
        staff_end_y = staff_base_y - int(staff_length * math.sin(angle_rad))
        pygame.draw.line(staff, wood, (staff_base_x, staff_base_y), (staff_end_x, staff_end_y), 2)
        pygame.draw.circle(staff, (160, 240, 180), (int(staff_base_x - 2), int(staff_base_y - 8)), 4)
        pygame.draw.circle(staff, (200, 255, 220), (int(staff_base_x - 2), int(staff_base_y - 8)), 2)
        body.blit(staff, (0, 0))
        
        # Магическое свечение убрано
        
        # Размытие движения убрано (создавало свечение)
        
        return body

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, hover_offset=0, wing_flap=0, staff_angle=90, staff_raise=0),
        'IdlePulse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, hover_offset=-1, wing_flap=1, staff_angle=90, staff_raise=0),
        'IdleHover': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, hover_offset=-2, wing_flap=-1, staff_angle=90, staff_raise=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, hover_offset=-1, wing_flap=2, staff_angle=92, staff_raise=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, hover_offset=-1, wing_flap=-2, staff_angle=88, staff_raise=0),
        'CastStart': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-1, head_tilt=-2, hover_offset=-2, wing_flap=2, staff_angle=75, staff_raise=-4),
        'CastRelease': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, hover_offset=-3, wing_flap=3, staff_angle=60, staff_raise=-6),
        'CastRecover': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-1, head_tilt=-1, hover_offset=-1, wing_flap=0, staff_angle=90, staff_raise=-2),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, hover_offset=1, wing_flap=-1, staff_angle=100, staff_raise=2),
        'TurnLeft': dict(leg_front_shift=-1, leg_back_shift=0, torso_shift=-1, head_tilt=-1, hover_offset=0, wing_flap=-1, staff_angle=95, staff_raise=0),
        'TurnRight': dict(leg_front_shift=0, leg_back_shift=1, torso_shift=1, head_tilt=1, hover_offset=0, wing_flap=1, staff_angle=85, staff_raise=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, hover_offset=3, wing_flap=-2, staff_angle=120, staff_raise=4),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, hover_offset=4, wing_flap=-2, staff_angle=125, staff_raise=4),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 75)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-8, 8))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-10, 12))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_ent_texture(animation_state='Idle'):
    """Полноценная система анимаций для энта (ходячее древоподобное существо) с перемещением и атакой."""
    cache_key = f'ent_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        left_arm_angle=0,
        right_arm_angle=0,
        arm_raise=0,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        
        shadow = (32, 40, 28, 170)
        bark_dark = (80, 60, 40)
        bark_mid = (100, 75, 50)
        bark_light = (120, 90, 60)
        leaf_mid = (80, 140, 70)
        leaf_light = (120, 180, 100)
        leaf_dark = (60, 100, 50)
        
        base_y = 0
        
        # Тень
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Ноги-корни
        left_leg = pygame.Rect(14 + leg_back_shift, 28 + base_y, 6, 10)
        right_leg = pygame.Rect(28 + leg_front_shift, 28 + base_y, 6, 10)
        pygame.draw.rect(body, bark_mid, left_leg)
        pygame.draw.rect(body, bark_dark, left_leg, 1)
        pygame.draw.rect(body, bark_mid, right_leg)
        pygame.draw.rect(body, bark_dark, right_leg, 1)
        # Детали коры на ногах
        pygame.draw.line(body, bark_dark, (17 + leg_back_shift, 30 + base_y), (17 + leg_back_shift, 36 + base_y), 1)
        pygame.draw.line(body, bark_dark, (31 + leg_front_shift, 30 + base_y), (31 + leg_front_shift, 36 + base_y), 1)
        # Корни
        pygame.draw.line(body, bark_dark, (17 + leg_back_shift, 38 + base_y), (10, 42), 2)
        pygame.draw.line(body, bark_dark, (31 + leg_front_shift, 38 + base_y), (38, 42), 2)
        
        # Тело-ствол
        torso = pygame.Rect(16 + torso_shift, 14 + base_y, 16, 14)
        pygame.draw.rect(body, bark_mid, torso)
        pygame.draw.rect(body, bark_dark, torso, 2)
        # Детали коры
        for i in range(3):
            pygame.draw.line(body, bark_dark, (18 + torso_shift, 16 + base_y + i*4), (30 + torso_shift, 16 + base_y + i*4), 1)
        
        # Руки-ветви
        left_arm_start = (12 + torso_shift, 20 + base_y + arm_raise)
        left_angle_rad = math.radians(left_arm_angle)
        left_arm_length = 14
        left_arm_end = (
            left_arm_start[0] + int(left_arm_length * math.cos(left_angle_rad)),
            left_arm_start[1] - int(left_arm_length * math.sin(left_angle_rad))
        )
        pygame.draw.line(body, bark_mid, left_arm_start, left_arm_end, 5)
        pygame.draw.line(body, bark_dark, left_arm_start, left_arm_end, 1)
        # Веточки на руке
        pygame.draw.line(body, bark_dark, (left_arm_end[0] - 2, left_arm_end[1]), (left_arm_end[0] - 4, left_arm_end[1] - 3), 2)
        pygame.draw.line(body, bark_dark, (left_arm_end[0] + 2, left_arm_end[1]), (left_arm_end[0] + 4, left_arm_end[1] - 3), 2)
        
        right_arm_start = (32 + torso_shift, 20 + base_y + arm_raise)
        right_angle_rad = math.radians(right_arm_angle)
        right_arm_length = 14
        right_arm_end = (
            right_arm_start[0] + int(right_arm_length * math.cos(right_angle_rad)),
            right_arm_start[1] - int(right_arm_length * math.sin(right_angle_rad))
        )
        pygame.draw.line(body, bark_mid, right_arm_start, right_arm_end, 5)
        pygame.draw.line(body, bark_dark, right_arm_start, right_arm_end, 1)
        # Веточки на руке
        pygame.draw.line(body, bark_dark, (right_arm_end[0] - 2, right_arm_end[1]), (right_arm_end[0] - 4, right_arm_end[1] - 3), 2)
        pygame.draw.line(body, bark_dark, (right_arm_end[0] + 2, right_arm_end[1]), (right_arm_end[0] + 4, right_arm_end[1] - 3), 2)
        
        # Голова-крона
        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 24 + torso_shift
        head_y = 6 + base_y + head_tilt
        # Основание головы (широкое)
        pygame.draw.ellipse(head_surface, bark_mid, (head_x - 10, head_y - 6, 20, 12))
        pygame.draw.ellipse(head_surface, bark_dark, (head_x - 10, head_y - 6, 20, 12), 2)
        # Детали коры на голове
        pygame.draw.line(head_surface, bark_dark, (head_x - 6, head_y - 2), (head_x + 6, head_y - 2), 1)
        pygame.draw.line(head_surface, bark_dark, (head_x - 6, head_y + 2), (head_x + 6, head_y + 2), 1)
        # Листва вместо волос
        pygame.draw.ellipse(head_surface, leaf_mid, (head_x - 10, head_y - 8, 20, 10))
        pygame.draw.ellipse(head_surface, leaf_light, (head_x - 8, head_y - 7, 16, 8))
        # "Глаза" - сучки
        pygame.draw.circle(head_surface, (60, 40, 20), (head_x - 4, head_y - 1), 2)
        pygame.draw.circle(head_surface, (60, 40, 20), (head_x + 4, head_y - 1), 2)
        # "Рот" - щель в коре
        pygame.draw.rect(head_surface, (50, 30, 15), (head_x - 2, head_y + 2, 4, 2))
        body.blit(head_surface, (0, 0))
        
        # Размытие движения убрано (создавало свечение)
        
        return body

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, left_arm_angle=120, right_arm_angle=60, arm_raise=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, left_arm_angle=122, right_arm_angle=58, arm_raise=-1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, left_arm_angle=130, right_arm_angle=50, arm_raise=-1),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, left_arm_angle=110, right_arm_angle=70, arm_raise=-1),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, left_arm_angle=90, right_arm_angle=150, arm_raise=-2),
        'AttackStrike': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=1, head_tilt=1, left_arm_angle=40, right_arm_angle=180, arm_raise=-3),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, left_arm_angle=100, right_arm_angle=140, arm_raise=-1),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, left_arm_angle=135, right_arm_angle=45, arm_raise=2),
        'TurnLeft': dict(leg_front_shift=-1, leg_back_shift=0, torso_shift=-1, head_tilt=-1, left_arm_angle=125, right_arm_angle=55, arm_raise=0),
        'TurnRight': dict(leg_front_shift=0, leg_back_shift=1, torso_shift=1, head_tilt=1, left_arm_angle=115, right_arm_angle=65, arm_raise=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, left_arm_angle=140, right_arm_angle=40, arm_raise=4),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, left_arm_angle=145, right_arm_angle=35, arm_raise=4),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 78)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-8, 10))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 96)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 14))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_unicorn_texture(animation_state='Idle'):
    return _render_elf_animation_frame('unicorn', animation_state)


def load_imp_texture(animation_state='Idle'):
    """Полноценная система анимаций для беса (imp) в более мрачном демоническом стиле."""
    cache_key = f'imp_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def outlined_rect(target, rect, fill, outline=(60, 20, 10), width=1):
        pygame.draw.rect(target, fill, rect)
        pygame.draw.rect(target, outline, rect, width)

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        tail_angle=0,
        wing_flap=0,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        
        shadow = (15, 5, 4, 190)
        # Палитра — более адская: насыщенная красная кожа и почти чёрные рога/крылья
        skin = (150, 60, 50)       # Бордовая кожа
        skin_dark = (100, 30, 25)
        skin_light = (190, 90, 70)
        horn = (40, 20, 20)        # Почти чёрные рога
        horn_dark = (25, 10, 10)
        eye_glow = (240, 40, 40)   # Более насыщенное свечение
        eye_bright = (255, 120, 120)
        wing = (60, 20, 20)        # Тёмно-кровавые крылья
        wing_dark = (30, 10, 10)
        
        base_y = crouch
        
        # Тень
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Ноги (более детализированные)
        left_leg = pygame.Rect(14 + leg_back_shift, 24 + base_y, 5, 10)
        right_leg = pygame.Rect(25 + leg_front_shift, 24 + base_y, 5, 10)
        pygame.draw.rect(body, skin_dark, left_leg)
        pygame.draw.rect(body, (50, 30, 20), left_leg, 1)
        pygame.draw.rect(body, skin_dark, right_leg)
        pygame.draw.rect(body, (50, 30, 20), right_leg, 1)
        # Детали мышц
        pygame.draw.line(body, (90, 45, 30), (16 + leg_back_shift, 26 + base_y), (16 + leg_back_shift, 32 + base_y), 1)
        pygame.draw.line(body, (90, 45, 30), (28 + leg_front_shift, 26 + base_y), (28 + leg_front_shift, 32 + base_y), 1)
        # Лапы с когтями
        pygame.draw.circle(body, (80, 50, 35), (17 + leg_back_shift, 34 + base_y), 2)
        pygame.draw.circle(body, (40, 25, 15), (17 + leg_back_shift, 34 + base_y), 1)
        pygame.draw.circle(body, (80, 50, 35), (27 + leg_front_shift, 34 + base_y), 2)
        pygame.draw.circle(body, (40, 25, 15), (27 + leg_front_shift, 34 + base_y), 1)
        # Когти
        pygame.draw.line(body, (40, 25, 15), (17 + leg_back_shift, 36 + base_y), (16 + leg_back_shift, 38 + base_y), 1)
        pygame.draw.line(body, (40, 25, 15), (27 + leg_front_shift, 36 + base_y), (26 + leg_front_shift, 38 + base_y), 1)
        
        # Тело (более детализированное)
        torso = pygame.Rect(13 + torso_shift, 14 + base_y, 14, 12)
        pygame.draw.ellipse(body, skin, torso)
        pygame.draw.ellipse(body, skin_dark, (15 + torso_shift, 16 + base_y, 10, 8))
        pygame.draw.ellipse(body, skin_light, (16 + torso_shift, 17 + base_y, 8, 6))
        # Детали груди
        pygame.draw.line(body, skin_dark, (18 + torso_shift, 16 + base_y), (18 + torso_shift, 22 + base_y), 1)
        pygame.draw.line(body, skin_dark, (22 + torso_shift, 16 + base_y), (22 + torso_shift, 22 + base_y), 1)
        
        # Руки
        left_arm = pygame.Rect(11 + torso_shift, 16 + base_y, 4, 8)
        right_arm = pygame.Rect(25 + torso_shift, 16 + base_y, 4, 8)
        pygame.draw.rect(body, skin, left_arm)
        pygame.draw.rect(body, skin_dark, left_arm, 1)
        pygame.draw.rect(body, skin, right_arm)
        pygame.draw.rect(body, skin_dark, right_arm, 1)
        
        # Голова (более детализированная)
        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 20 + torso_shift
        head_y = 8 + base_y + head_tilt
        # Основная форма головы
        pygame.draw.ellipse(head_surface, skin_light, (head_x - 4, head_y - 4, 8, 8))
        pygame.draw.ellipse(head_surface, skin_dark, (head_x - 3, head_y - 3, 6, 6))
        pygame.draw.ellipse(head_surface, skin, (head_x - 2, head_y - 2, 4, 4))
        # Рога (более загнутые)
        horn_left_points = [(head_x - 2, head_y - 3), (head_x - 5, head_y - 6), (head_x - 4, head_y - 4)]
        horn_right_points = [(head_x + 2, head_y - 3), (head_x + 5, head_y - 6), (head_x + 4, head_y - 4)]
        pygame.draw.polygon(head_surface, horn, horn_left_points)
        pygame.draw.polygon(head_surface, horn, horn_right_points)
        pygame.draw.polygon(head_surface, horn_dark, horn_left_points, 1)
        pygame.draw.polygon(head_surface, horn_dark, horn_right_points, 1)
        # Глаза (яркие красные)
        pygame.draw.circle(head_surface, eye_glow, (head_x - 2, head_y), 2)
        pygame.draw.circle(head_surface, eye_bright, (head_x - 2, head_y), 1)
        pygame.draw.circle(head_surface, eye_glow, (head_x + 2, head_y), 2)
        pygame.draw.circle(head_surface, eye_bright, (head_x + 2, head_y), 1)
        # Рот (более детализированный)
        pygame.draw.arc(head_surface, (120, 20, 20), (head_x - 1, head_y + 1, 2, 2), 0, 3.14, 2)
        # Клыки (тёмные)
        pygame.draw.polygon(head_surface, (180, 180, 180), [(head_x - 1, head_y + 2), (head_x - 2, head_y + 4), (head_x, head_y + 3)])
        pygame.draw.polygon(head_surface, (180, 180, 180), [(head_x + 1, head_y + 2), (head_x + 2, head_y + 4), (head_x, head_y + 3)])
        body.blit(head_surface, (0, 0))
        
        # Хвост (тёмный с шипами)
        tail = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        tail_base = (20 + torso_shift, 20 + base_y)
        tail_angle_rad = math.radians(tail_angle)
        tail_length = 8
        tail_end = (
            tail_base[0] + int(tail_length * math.cos(tail_angle_rad)),
            tail_base[1] + int(tail_length * math.sin(tail_angle_rad))
        )
        # Основной хвост
        pygame.draw.line(tail, (80, 50, 40), tail_base, tail_end, 3)
        pygame.draw.line(tail, (60, 35, 25), tail_base, tail_end, 1)
        # Остроконечный кончик
        pygame.draw.polygon(tail, (60, 35, 25), [
            tail_end,
            (tail_end[0] + 3, tail_end[1] - 2),
            (tail_end[0] - 3, tail_end[1] - 2)
        ])
        body.blit(tail, (0, 0))
        
        # Крылья (перепончатые, тёмные)
        wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        wing_offset = int(wing_flap * 1.5)
        # Левое крыло (более детализированное)
        wing_points_left = [
            (12 + torso_shift, 16 + base_y),
            (8 + torso_shift, 24 + base_y + wing_offset),
            (20 + torso_shift, 20 + base_y),
            (14 + torso_shift, 18 + base_y)
        ]
        pygame.draw.polygon(wings, wing, wing_points_left)
        pygame.draw.polygon(wings, wing_dark, wing_points_left, 1)
        # Прожилки на крыле
        pygame.draw.line(wings, wing_dark, (12 + torso_shift, 16 + base_y), (8 + torso_shift, 24 + base_y + wing_offset), 1)
        pygame.draw.line(wings, wing_dark, (14 + torso_shift, 18 + base_y), (10 + torso_shift, 22 + base_y + wing_offset), 1)
        # Правое крыло
        wing_points_right = [
            (28 + torso_shift, 16 + base_y),
            (32 + torso_shift, 24 + base_y - wing_offset),
            (20 + torso_shift, 20 + base_y),
            (26 + torso_shift, 18 + base_y)
        ]
        pygame.draw.polygon(wings, wing, wing_points_right)
        pygame.draw.polygon(wings, wing_dark, wing_points_right, 1)
        # Прожилки
        pygame.draw.line(wings, wing_dark, (28 + torso_shift, 16 + base_y), (32 + torso_shift, 24 + base_y - wing_offset), 1)
        pygame.draw.line(wings, wing_dark, (26 + torso_shift, 18 + base_y), (30 + torso_shift, 22 + base_y - wing_offset), 1)
        body.blit(wings, (0, 0))
        
        # Размытие движения убрано (создавало свечение)
        
        return body

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, tail_angle=90, wing_flap=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, tail_angle=95, wing_flap=1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, tail_angle=100, wing_flap=2),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, tail_angle=80, wing_flap=-2),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, tail_angle=70, wing_flap=-1),
        'AttackStrike': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=1, head_tilt=1, tail_angle=110, wing_flap=3),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, tail_angle=90, wing_flap=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, tail_angle=120, wing_flap=-1),
        'TurnLeft': dict(leg_front_shift=-1, leg_back_shift=0, torso_shift=-1, head_tilt=-1, tail_angle=100, wing_flap=-1),
        'TurnRight': dict(leg_front_shift=0, leg_back_shift=1, torso_shift=1, head_tilt=1, tail_angle=80, wing_flap=1),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, tail_angle=130, wing_flap=-2),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, tail_angle=135, wing_flap=-2),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 75)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-8, 8))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-10, 12))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_gog_texture(animation_state='Idle'):
    """Полноценная система анимаций для гога (дальнобойный демон) с более «адской» палитрой."""
    cache_key = f'gog_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        fireball_angle=0,
        fireball_raise=0,
        fireball_size=0,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        
        shadow = (12, 4, 3, 195)
        # Более контрастная красно-чёрная палитра
        skin = (160, 70, 55)
        skin_dark = (110, 35, 30)
        skin_light = (195, 105, 80)
        horn = (50, 25, 25)
        horn_dark = (30, 12, 12)
        eye_glow = (255, 60, 60)
        eye_bright = (255, 130, 130)
        fire = (255, 120, 40)
        fire_bright = (255, 210, 90)
        
        base_y = crouch
        
        # Тень
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Ноги (детализированные)
        left_leg = pygame.Rect(14 + leg_back_shift, 28 + base_y, 6, 10)
        right_leg = pygame.Rect(26 + leg_front_shift, 28 + base_y, 6, 10)
        pygame.draw.rect(body, skin_dark, left_leg)
        pygame.draw.rect(body, (60, 35, 25), left_leg, 1)
        pygame.draw.rect(body, skin_dark, right_leg)
        pygame.draw.rect(body, (60, 35, 25), right_leg, 1)
        # Детали мышц
        pygame.draw.line(body, (90, 55, 40), (17 + leg_back_shift, 30 + base_y), (17 + leg_back_shift, 36 + base_y), 1)
        pygame.draw.line(body, (90, 55, 40), (29 + leg_front_shift, 30 + base_y), (29 + leg_front_shift, 36 + base_y), 1)
        # Лапы с когтями
        pygame.draw.circle(body, (90, 60, 45), (17 + leg_back_shift, 38 + base_y), 2)
        pygame.draw.circle(body, (50, 30, 20), (17 + leg_back_shift, 38 + base_y), 1)
        pygame.draw.circle(body, (90, 60, 45), (29 + leg_front_shift, 38 + base_y), 2)
        pygame.draw.circle(body, (50, 30, 20), (29 + leg_front_shift, 38 + base_y), 1)
        # Когти
        pygame.draw.line(body, (50, 30, 20), (17 + leg_back_shift, 40 + base_y), (16 + leg_back_shift, 42 + base_y), 1)
        pygame.draw.line(body, (50, 30, 20), (29 + leg_front_shift, 40 + base_y), (28 + leg_front_shift, 42 + base_y), 1)
        
        # Тело (более детализированное)
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 14)
        pygame.draw.ellipse(body, skin, torso)
        pygame.draw.ellipse(body, skin_dark, (16 + torso_shift, 16 + base_y, 12, 10))
        pygame.draw.ellipse(body, skin_light, (17 + torso_shift, 17 + base_y, 10, 8))
        # Детали груди
        pygame.draw.line(body, skin_dark, (18 + torso_shift, 16 + base_y), (18 + torso_shift, 24 + base_y), 1)
        pygame.draw.line(body, skin_dark, (24 + torso_shift, 16 + base_y), (24 + torso_shift, 24 + base_y), 1)
        
        # Руки
        left_arm = pygame.Rect(12 + torso_shift, 16 + base_y, 4, 10)
        right_arm = pygame.Rect(28 + torso_shift, 16 + base_y, 4, 10)
        pygame.draw.rect(body, skin, left_arm)
        pygame.draw.rect(body, skin_dark, left_arm, 1)
        pygame.draw.rect(body, skin, right_arm)
        pygame.draw.rect(body, skin_dark, right_arm, 1)
        # Детали мышц на руках
        pygame.draw.line(body, skin_dark, (14 + torso_shift, 18 + base_y), (14 + torso_shift, 24 + base_y), 1)
        pygame.draw.line(body, skin_dark, (30 + torso_shift, 18 + base_y), (30 + torso_shift, 24 + base_y), 1)
        
        # Голова (детализированная)
        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 22 + torso_shift
        head_y = 8 + base_y + head_tilt
        # Основная форма
        pygame.draw.ellipse(head_surface, skin_light, (head_x - 4, head_y - 4, 8, 8))
        pygame.draw.ellipse(head_surface, skin_dark, (head_x - 3, head_y - 3, 6, 6))
        pygame.draw.ellipse(head_surface, skin, (head_x - 2, head_y - 2, 4, 4))
        # Рога (загнутые)
        horn_left_points = [(head_x - 2, head_y - 3), (head_x - 5, head_y - 6), (head_x - 4, head_y - 4)]
        horn_right_points = [(head_x + 2, head_y - 3), (head_x + 5, head_y - 6), (head_x + 4, head_y - 4)]
        pygame.draw.polygon(head_surface, horn, horn_left_points)
        pygame.draw.polygon(head_surface, horn, horn_right_points)
        pygame.draw.polygon(head_surface, horn_dark, horn_left_points, 1)
        pygame.draw.polygon(head_surface, horn_dark, horn_right_points, 1)
        # Глаза (яркие)
        pygame.draw.circle(head_surface, eye_glow, (head_x - 2, head_y), 2)
        pygame.draw.circle(head_surface, eye_bright, (head_x - 2, head_y), 1)
        pygame.draw.circle(head_surface, eye_glow, (head_x + 2, head_y), 2)
        pygame.draw.circle(head_surface, eye_bright, (head_x + 2, head_y), 1)
        # Рот
        pygame.draw.arc(head_surface, (120, 20, 20), (head_x - 1, head_y + 2, 2, 2), 0, 3.14, 2)
        body.blit(head_surface, (0, 0))
        
        # Пламя (более реалистичное)
        flame = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        flame_base = (22 + torso_shift, 28 + base_y)
        # Основное пламя
        flame_points = [
            flame_base,
            (flame_base[0] + 5, flame_base[1] + 8),
            (flame_base[0], flame_base[1] + 6),
            (flame_base[0] - 5, flame_base[1] + 8)
        ]
        pygame.draw.polygon(flame, fire, flame_points)
        pygame.draw.polygon(flame, fire_bright, [
            flame_base,
            (flame_base[0] + 3, flame_base[1] + 4),
            (flame_base[0] - 3, flame_base[1] + 4)
        ])
        # Язычки пламени
        pygame.draw.polygon(flame, (255, 220, 120), [
            (flame_base[0] - 2, flame_base[1] + 2),
            (flame_base[0] - 4, flame_base[1] + 5),
            (flame_base[0] - 1, flame_base[1] + 4)
        ])
        pygame.draw.polygon(flame, (255, 220, 120), [
            (flame_base[0] + 2, flame_base[1] + 2),
            (flame_base[0] + 4, flame_base[1] + 5),
            (flame_base[0] + 1, flame_base[1] + 4)
        ])
        body.blit(flame, (0, 0))
        
        # Огненный шар (для атаки)
        if fireball_size > 0:
            fireball = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            fireball_base_x = 28 + torso_shift
            fireball_base_y = 20 + base_y + fireball_raise
            angle_rad = math.radians(fireball_angle)
            fireball_x = fireball_base_x + int(12 * math.cos(angle_rad))
            fireball_y = fireball_base_y - int(12 * math.sin(angle_rad))
            size = 4 + fireball_size
            pygame.draw.circle(fireball, fire_bright, (fireball_x, fireball_y), size)
            pygame.draw.circle(fireball, fire, (fireball_x, fireball_y), size - 1)
            pygame.draw.circle(fireball, (255, 200, 100), (fireball_x, fireball_y), size - 2)
            body.blit(fireball, (0, 0))
        
        # Размытие движения убрано (создавало свечение)
        
        return body

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, fireball_angle=0, fireball_raise=0, fireball_size=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, fireball_angle=0, fireball_raise=0, fireball_size=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, fireball_angle=0, fireball_raise=0, fireball_size=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, fireball_angle=0, fireball_raise=0, fireball_size=0),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, fireball_angle=45, fireball_raise=-2, fireball_size=1),
        'AttackAim': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-1, fireball_angle=30, fireball_raise=-4, fireball_size=2),
        'AttackRelease': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, fireball_angle=0, fireball_raise=-6, fireball_size=3),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, fireball_angle=0, fireball_raise=0, fireball_size=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, fireball_angle=0, fireball_raise=0, fireball_size=0),
        'TurnLeft': dict(leg_front_shift=-1, leg_back_shift=0, torso_shift=-1, head_tilt=-1, fireball_angle=0, fireball_raise=0, fireball_size=0),
        'TurnRight': dict(leg_front_shift=0, leg_back_shift=1, torso_shift=1, head_tilt=1, fireball_angle=0, fireball_raise=0, fireball_size=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, fireball_angle=0, fireball_raise=0, fireball_size=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, fireball_angle=0, fireball_raise=0, fireball_size=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 75)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-8, 8))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-10, 12))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_demon_texture(animation_state='Idle'):
    """Полноценная система анимаций для демона-воина в более тяжёлом, мрачном стиле."""
    cache_key = f'demon_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        sword_angle=0,
        sword_raise=0,
        sword_reach=0,
        shield_tilt=0,
        shield_raise=0,
        tail_angle=0,
        wing_flap=0,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        sword = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shield = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        
        shadow = (10, 4, 3, 200)
        # Палитра демона: более тёмная броня и насыщенно-красная кожа
        skin = (150, 60, 50)
        skin_dark = (110, 35, 30)
        skin_light = (190, 90, 75)
        armor = (40, 25, 30)        # Почти чёрная броня
        armor_dark = (20, 10, 15)
        armor_metal = (130, 120, 120)  # Холодный металл
        horn = (50, 25, 25)
        horn_dark = (30, 12, 12)
        eye_glow = (255, 60, 60)
        eye_bright = (255, 140, 140)
        metal = (150, 150, 170)
        wing = (45, 15, 20)         # Тёмно-кровавые крылья
        wing_dark = (25, 8, 10)
        
        base_y = crouch
        
        # Тень
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Ноги (в броне)
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 12)
        right_leg = pygame.Rect(26 + leg_front_shift, 26 + base_y, 6, 12)
        pygame.draw.rect(body, armor, left_leg)
        pygame.draw.rect(body, armor_dark, left_leg, 1)
        pygame.draw.rect(body, armor, right_leg)
        pygame.draw.rect(body, armor_dark, right_leg, 1)
        # Детали брони на ногах
        pygame.draw.line(body, armor_metal, (16 + leg_back_shift, 28 + base_y), (16 + leg_back_shift, 34 + base_y), 1)
        pygame.draw.line(body, armor_metal, (28 + leg_front_shift, 28 + base_y), (28 + leg_front_shift, 34 + base_y), 1)
        # Наголенники
        pygame.draw.rect(body, armor_metal, (14 + leg_back_shift, 30 + base_y, 6, 4))
        pygame.draw.rect(body, armor_metal, (26 + leg_front_shift, 30 + base_y, 6, 4))
        # Лапы с когтями
        pygame.draw.circle(body, (90, 60, 45), (17 + leg_back_shift, 38 + base_y), 3)
        pygame.draw.circle(body, (50, 30, 20), (17 + leg_back_shift, 38 + base_y), 1)
        pygame.draw.circle(body, (90, 60, 45), (29 + leg_front_shift, 38 + base_y), 3)
        pygame.draw.circle(body, (50, 30, 20), (29 + leg_front_shift, 38 + base_y), 1)
        # Когти
        pygame.draw.line(body, (40, 25, 15), (17 + leg_back_shift, 40 + base_y), (16 + leg_back_shift, 42 + base_y), 1)
        pygame.draw.line(body, (40, 25, 15), (29 + leg_front_shift, 40 + base_y), (28 + leg_front_shift, 42 + base_y), 1)
        
        # Тело (более детализированное)
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 20, 14)
        pygame.draw.ellipse(body, skin, torso)
        pygame.draw.ellipse(body, skin_dark, (16 + torso_shift, 16 + base_y, 16, 10))
        pygame.draw.ellipse(body, skin_light, (17 + torso_shift, 17 + base_y, 14, 8))
        # Броня (детализированная)
        armor_rect = pygame.Rect(16 + torso_shift, 18 + base_y, 16, 6)
        pygame.draw.rect(body, armor, armor_rect)
        pygame.draw.rect(body, armor_dark, armor_rect, 1)
        # Детали брони
        pygame.draw.line(body, armor_metal, (18 + torso_shift, 18 + base_y), (18 + torso_shift, 24 + base_y), 1)
        pygame.draw.line(body, armor_metal, (26 + torso_shift, 18 + base_y), (26 + torso_shift, 24 + base_y), 1)
        pygame.draw.rect(body, armor_metal, (20 + torso_shift, 19 + base_y, 8, 2))
        
        # Руки
        left_arm = pygame.Rect(12 + torso_shift, 16 + base_y, 5, 12)
        right_arm = pygame.Rect(31 + torso_shift, 16 + base_y, 5, 12)
        pygame.draw.rect(body, skin, left_arm)
        pygame.draw.rect(body, skin_dark, left_arm, 1)
        pygame.draw.rect(body, skin, right_arm)
        pygame.draw.rect(body, skin_dark, right_arm, 1)
        
        # Голова (детализированная с шлемом)
        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 24 + torso_shift
        head_y = 8 + base_y + head_tilt
        # Основная форма
        pygame.draw.ellipse(head_surface, skin_light, (head_x - 5, head_y - 5, 10, 10))
        pygame.draw.ellipse(head_surface, skin_dark, (head_x - 3, head_y - 3, 6, 6))
        pygame.draw.ellipse(head_surface, skin, (head_x - 2, head_y - 2, 4, 4))
        # Шлем/наголовник
        pygame.draw.arc(head_surface, armor, (head_x - 5, head_y - 6, 10, 8), 0, 3.14, 2)
        pygame.draw.line(head_surface, armor_metal, (head_x - 4, head_y - 3), (head_x + 4, head_y - 3), 1)
        # Рога (большие, загнутые)
        horn_left_points = [(head_x - 3, head_y - 4), (head_x - 7, head_y - 8), (head_x - 5, head_y - 5)]
        horn_right_points = [(head_x + 3, head_y - 4), (head_x + 7, head_y - 8), (head_x + 5, head_y - 5)]
        pygame.draw.polygon(head_surface, horn, horn_left_points)
        pygame.draw.polygon(head_surface, horn, horn_right_points)
        pygame.draw.polygon(head_surface, horn_dark, horn_left_points, 1)
        pygame.draw.polygon(head_surface, horn_dark, horn_right_points, 1)
        # Глаза (яркие)
        pygame.draw.circle(head_surface, eye_glow, (head_x - 2, head_y), 2)
        pygame.draw.circle(head_surface, eye_bright, (head_x - 2, head_y), 1)
        pygame.draw.circle(head_surface, eye_glow, (head_x + 2, head_y), 2)
        pygame.draw.circle(head_surface, eye_bright, (head_x + 2, head_y), 1)
        # Рот
        pygame.draw.arc(head_surface, (120, 20, 20), (head_x - 1, head_y + 2, 2, 2), 0, 3.14, 2)
        # Клыки (тёмные)
        pygame.draw.polygon(head_surface, (200, 200, 200), [(head_x - 1, head_y + 2), (head_x - 2, head_y + 5), (head_x, head_y + 4)])
        pygame.draw.polygon(head_surface, (200, 200, 200), [(head_x + 1, head_y + 2), (head_x + 2, head_y + 5), (head_x, head_y + 4)])
        body.blit(head_surface, (0, 0))
        
        # Хвост (тёмный с шипами)
        tail = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        tail_base = (24 + torso_shift, 26 + base_y)
        tail_angle_rad = math.radians(tail_angle)
        tail_length = 10
        tail_end = (
            tail_base[0] + int(tail_length * math.cos(tail_angle_rad)),
            tail_base[1] + int(tail_length * math.sin(tail_angle_rad))
        )
        # Основной хвост
        pygame.draw.line(tail, (90, 60, 50), tail_base, tail_end, 4)
        pygame.draw.line(tail, (70, 45, 35), tail_base, tail_end, 1)
        # Остроконечный кончик
        pygame.draw.polygon(tail, (70, 45, 35), [
            tail_end,
            (tail_end[0] + 4, tail_end[1] - 2),
            (tail_end[0] - 4, tail_end[1] - 2)
        ])
        # Шипы на хвосте
        mid_tail = (
            tail_base[0] + int(tail_length * 0.5 * math.cos(tail_angle_rad)),
            tail_base[1] + int(tail_length * 0.5 * math.sin(tail_angle_rad))
        )
        pygame.draw.polygon(tail, (60, 40, 30), [
            mid_tail,
            (mid_tail[0] + 2, mid_tail[1] - 3),
            (mid_tail[0] - 2, mid_tail[1] - 3)
        ])
        body.blit(tail, (0, 0))
        
        # Крылья (перепончатые, тёмные с прожилками)
        wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        wing_offset = int(wing_flap * 1.5)
        # Левое крыло (детализированное)
        wing_points_left = [
            (10 + torso_shift, 18 + base_y),
            (2 + torso_shift, 8 + base_y + wing_offset),
            (24 + torso_shift, 20 + base_y),
            (14 + torso_shift, 18 + base_y)
        ]
        pygame.draw.polygon(wings, wing, wing_points_left)
        pygame.draw.polygon(wings, wing_dark, wing_points_left, 1)
        # Прожилки на крыле
        pygame.draw.line(wings, wing_dark, (10 + torso_shift, 18 + base_y), (2 + torso_shift, 8 + base_y + wing_offset), 1)
        pygame.draw.line(wings, wing_dark, (14 + torso_shift, 18 + base_y), (6 + torso_shift, 12 + base_y + wing_offset), 1)
        pygame.draw.line(wings, wing_dark, (18 + torso_shift, 19 + base_y), (10 + torso_shift, 14 + base_y + wing_offset), 1)
        # Правое крыло
        wing_points_right = [
            (38 + torso_shift, 18 + base_y),
            (46 + torso_shift, 8 + base_y - wing_offset),
            (24 + torso_shift, 20 + base_y),
            (30 + torso_shift, 18 + base_y)
        ]
        pygame.draw.polygon(wings, wing, wing_points_right)
        pygame.draw.polygon(wings, wing_dark, wing_points_right, 1)
        # Прожилки
        pygame.draw.line(wings, wing_dark, (38 + torso_shift, 18 + base_y), (46 + torso_shift, 8 + base_y - wing_offset), 1)
        pygame.draw.line(wings, wing_dark, (30 + torso_shift, 18 + base_y), (38 + torso_shift, 12 + base_y - wing_offset), 1)
        pygame.draw.line(wings, wing_dark, (26 + torso_shift, 19 + base_y), (34 + torso_shift, 14 + base_y - wing_offset), 1)
        body.blit(wings, (0, 0))
        
        # Щит (тёмная броня)
        shield_center = (14 + torso_shift, 20 + base_y + shield_raise)
        shield_rect = pygame.Rect(shield_center[0] - 5, shield_center[1] - 7, 10, 12)
        pygame.draw.ellipse(shield, armor, shield_rect)
        pygame.draw.ellipse(shield, armor_dark, shield_rect, 2)
        pygame.draw.line(shield, armor_metal, (shield_center[0], shield_center[1] - 7), (shield_center[0], shield_center[1] + 5), 2)
        pygame.draw.line(shield, armor_metal, (shield_center[0] - 4, shield_center[1] - 2), (shield_center[0] + 4, shield_center[1] - 2), 1)
        # Эмблема на щите
        pygame.draw.circle(shield, eye_glow, (shield_center[0], shield_center[1] - 1), 2)
        if shield_tilt:
            shield = pygame.transform.rotate(shield, shield_tilt)
        body.blit(shield, shield.get_rect(center=shield_center))
        
        # Меч (тёмный, детализированный)
        sword_start = (31 + torso_shift, 18 + base_y + sword_raise)
        angle_rad = math.radians(sword_angle)
        sword_length = 18 + sword_reach
        sword_end = (
            sword_start[0] + int(sword_length * math.cos(angle_rad)),
            sword_start[1] - int(sword_length * math.sin(angle_rad))
        )
        # Рукоять
        pygame.draw.line(sword, (60, 50, 40), sword_start, sword_end, 4)
        pygame.draw.line(sword, (40, 30, 25), sword_start, sword_end, 1)
        # Гарда
        guard_rect = pygame.Rect(sword_start[0] - 2, sword_start[1] - 2, 6, 4)
        pygame.draw.rect(sword, metal, guard_rect)
        pygame.draw.rect(sword, armor_dark, guard_rect, 1)
        pygame.draw.line(sword, armor_metal, (sword_start[0] - 3, sword_start[1]), (sword_start[0] + 3, sword_start[1]), 1)
        # Клинок
        blade_end = (
            sword_end[0] + int(8 * math.cos(angle_rad)),
            sword_end[1] - int(8 * math.sin(angle_rad))
        )
        pygame.draw.line(sword, metal, sword_end, blade_end, 3)
        pygame.draw.line(sword, (180, 180, 200), sword_end, blade_end, 1)
        body.blit(sword, (0, 0))
        
        # Размытие движения убрано (создавало свечение)
        
        return body

    params_map = {
        # Базовая стойка — более пригнутая, с акцентом на тяжёлую броню и крылья
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-1, sword_angle=88, sword_raise=-1, shield_tilt=-4, tail_angle=95, wing_flap=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-2, head_tilt=-2, sword_angle=90, sword_raise=-1, shield_tilt=-6, tail_angle=105, wing_flap=2),
        # Ходьба — более тяжёлый шаг с активной работой хвоста и крыльев
        'Walk': dict(leg_front_shift=3, leg_back_shift=-3, torso_shift=-2, sword_angle=92, sword_raise=-1, shield_tilt=-4, tail_angle=115, wing_flap=3),
        'WalkAlt': dict(leg_front_shift=-3, leg_back_shift=3, torso_shift=0, sword_angle=86, sword_raise=-1, shield_tilt=-2, tail_angle=80, wing_flap=-3),
        # Атака — широкий замах и мощный удар
        'AttackPrep': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=-3, head_tilt=-3, sword_angle=45, sword_raise=-4, shield_tilt=-14, tail_angle=65, wing_flap=-2),
        'AttackStrike': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=2, head_tilt=1, sword_angle=20, sword_raise=-6, sword_reach=6, shield_tilt=14, tail_angle=125, wing_flap=4),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, sword_angle=92, sword_raise=-1, shield_tilt=-2, tail_angle=100, wing_flap=1),
        # Получение урона — сильное проседание корпуса
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-3, head_tilt=-4, crouch=3, sword_angle=110, sword_raise=1, shield_tilt=-4, tail_angle=135, wing_flap=-2),
        # Повороты — лёгкие смещения с работой крыльев
        'TurnLeft': dict(leg_front_shift=-1, leg_back_shift=0, torso_shift=-2, head_tilt=-2, sword_angle=96, sword_raise=-1, shield_tilt=-4, tail_angle=105, wing_flap=-2),
        'TurnRight': dict(leg_front_shift=0, leg_back_shift=1, torso_shift=0, head_tilt=2, sword_angle=84, sword_raise=-1, shield_tilt=-2, tail_angle=85, wing_flap=2),
        # Смерть / труп — более «развалившаяся» поза
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-3, head_tilt=5, crouch=5, sword_angle=125, sword_raise=5, shield_tilt=-6, tail_angle=145, wing_flap=-3),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-3, head_tilt=5, crouch=6, sword_angle=130, sword_raise=5, shield_tilt=-6, tail_angle=150, wing_flap=-3),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 75)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-8, 8))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-10, 12))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_cerberus_texture(animation_state='Idle'):
    """Полноценная система анимаций для цербера (трёхголовая адская гончая) с более тёмной палитрой."""
    cache_key = f'cerberus_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head1_tilt=0,
        head2_tilt=0,
        head3_tilt=0,
        crouch=0,
        tail_angle=0,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        
        shadow = (10, 4, 3, 200)
        skin = (90, 35, 30)        # Более тёмная кожа
        skin_dark = (60, 20, 18)
        skin_light = (130, 60, 50)
        eye_glow = (255, 60, 60)
        eye_bright = (255, 130, 130)
        
        base_y = crouch
        
        # Тень
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Тело (большое, тёмное)
        torso = pygame.Rect(8 + torso_shift, 20 + base_y, 24, 16)
        pygame.draw.ellipse(body, skin, torso)
        pygame.draw.ellipse(body, skin_dark, (10 + torso_shift, 22 + base_y, 20, 12))
        pygame.draw.ellipse(body, skin_light, (11 + torso_shift, 23 + base_y, 18, 10))
        # Детали шерсти/мышц
        pygame.draw.line(body, skin_dark, (14 + torso_shift, 22 + base_y), (14 + torso_shift, 32 + base_y), 1)
        pygame.draw.line(body, skin_dark, (20 + torso_shift, 22 + base_y), (20 + torso_shift, 32 + base_y), 1)
        pygame.draw.line(body, skin_dark, (26 + torso_shift, 22 + base_y), (26 + torso_shift, 32 + base_y), 1)
        
        # Ноги (детализированные)
        left_leg = pygame.Rect(12 + leg_back_shift, 36 + base_y, 5, 6)
        right_leg = pygame.Rect(27 + leg_front_shift, 36 + base_y, 5, 6)
        pygame.draw.rect(body, skin, left_leg)
        pygame.draw.rect(body, skin_dark, left_leg, 1)
        pygame.draw.rect(body, skin, right_leg)
        pygame.draw.rect(body, skin_dark, right_leg, 1)
        # Детали мышц
        pygame.draw.line(body, skin_dark, (14 + leg_back_shift, 36 + base_y), (14 + leg_back_shift, 40 + base_y), 1)
        pygame.draw.line(body, skin_dark, (29 + leg_front_shift, 36 + base_y), (29 + leg_front_shift, 40 + base_y), 1)
        # Лапы с когтями
        pygame.draw.circle(body, (90, 60, 45), (14 + leg_back_shift, 42 + base_y), 3)
        pygame.draw.circle(body, (50, 30, 20), (14 + leg_back_shift, 42 + base_y), 1)
        pygame.draw.circle(body, (90, 60, 45), (29 + leg_front_shift, 42 + base_y), 3)
        pygame.draw.circle(body, (50, 30, 20), (29 + leg_front_shift, 42 + base_y), 1)
        # Когти
        pygame.draw.line(body, (40, 25, 15), (14 + leg_back_shift, 44 + base_y), (13 + leg_back_shift, 46 + base_y), 1)
        pygame.draw.line(body, (40, 25, 15), (29 + leg_front_shift, 44 + base_y), (28 + leg_front_shift, 46 + base_y), 1)
        
        # Три головы (тёмные, детализированные)
        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Голова 1 (левая)
        head1_x = 14 + torso_shift
        head1_y = 8 + base_y + head1_tilt
        pygame.draw.ellipse(head_surface, skin_light, (head1_x - 5, head1_y - 5, 10, 10))
        pygame.draw.ellipse(head_surface, skin_dark, (head1_x - 3, head1_y - 3, 6, 6))
        pygame.draw.ellipse(head_surface, skin, (head1_x - 2, head1_y - 2, 4, 4))
        pygame.draw.circle(head_surface, eye_glow, (head1_x - 2, head1_y - 1), 2)
        pygame.draw.circle(head_surface, eye_bright, (head1_x - 2, head1_y - 1), 1)
        pygame.draw.arc(head_surface, (100, 20, 20), (head1_x - 1, head1_y + 2, 2, 2), 0, 3.14, 2)
        pygame.draw.polygon(head_surface, (200, 200, 200), [(head1_x - 1, head1_y + 2), (head1_x - 2, head1_y + 4), (head1_x, head1_y + 3)])
        # Шерсть на голове
        pygame.draw.ellipse(head_surface, skin_dark, (head1_x - 6, head1_y - 6, 12, 4))
        
        # Голова 2 (центральная)
        head2_x = 20 + torso_shift
        head2_y = 4 + base_y + head2_tilt
        pygame.draw.ellipse(head_surface, skin_light, (head2_x - 4, head2_y - 4, 8, 8))
        pygame.draw.ellipse(head_surface, skin_dark, (head2_x - 2, head2_y - 2, 4, 4))
        pygame.draw.ellipse(head_surface, skin, (head2_x - 1, head2_y - 1, 2, 2))
        pygame.draw.circle(head_surface, eye_glow, (head2_x, head2_y), 2)
        pygame.draw.circle(head_surface, eye_bright, (head2_x, head2_y), 1)
        pygame.draw.arc(head_surface, (100, 20, 20), (head2_x - 1, head2_y + 2, 2, 2), 0, 3.14, 2)
        pygame.draw.polygon(head_surface, (200, 200, 200), [(head2_x - 1, head2_y + 2), (head2_x - 2, head2_y + 4), (head2_x, head2_y + 3)])
        # Шерсть на голове
        pygame.draw.ellipse(head_surface, skin_dark, (head2_x - 5, head2_y - 5, 10, 3))
        
        # Голова 3 (правая)
        head3_x = 26 + torso_shift
        head3_y = 8 + base_y + head3_tilt
        pygame.draw.ellipse(head_surface, skin_light, (head3_x - 5, head3_y - 5, 10, 10))
        pygame.draw.ellipse(head_surface, skin_dark, (head3_x - 3, head3_y - 3, 6, 6))
        pygame.draw.ellipse(head_surface, skin, (head3_x - 2, head3_y - 2, 4, 4))
        pygame.draw.circle(head_surface, eye_glow, (head3_x + 2, head3_y - 1), 2)
        pygame.draw.circle(head_surface, eye_bright, (head3_x + 2, head3_y - 1), 1)
        pygame.draw.arc(head_surface, (100, 20, 20), (head3_x - 1, head3_y + 2, 2, 2), 0, 3.14, 2)
        pygame.draw.polygon(head_surface, (200, 200, 200), [(head3_x + 1, head3_y + 2), (head3_x + 2, head3_y + 4), (head3_x, head3_y + 3)])
        # Шерсть на голове
        pygame.draw.ellipse(head_surface, skin_dark, (head3_x - 6, head3_y - 6, 12, 4))
        
        body.blit(head_surface, (0, 0))
        
        # Хвост (тёмный)
        tail = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        tail_base = (20 + torso_shift, 36 + base_y)
        tail_angle_rad = math.radians(tail_angle)
        tail_length = 8
        tail_end = (
            tail_base[0] + int(tail_length * math.cos(tail_angle_rad)),
            tail_base[1] + int(tail_length * math.sin(tail_angle_rad))
        )
        # Основной хвост
        pygame.draw.line(tail, (90, 60, 50), tail_base, tail_end, 4)
        pygame.draw.line(tail, (70, 45, 35), tail_base, tail_end, 1)
        # Остроконечный кончик
        pygame.draw.polygon(tail, (70, 45, 35), [
            tail_end,
            (tail_end[0] + 4, tail_end[1] - 2),
            (tail_end[0] - 4, tail_end[1] - 2)
        ])
        body.blit(tail, (0, 0))
        
        # Размытие движения убрано (создавало свечение)
        
        return body

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head1_tilt=0, head2_tilt=0, head3_tilt=0, tail_angle=90),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head1_tilt=-1, head2_tilt=-1, head3_tilt=-1, tail_angle=95),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head1_tilt=-1, head2_tilt=0, head3_tilt=1, tail_angle=100),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head1_tilt=1, head2_tilt=0, head3_tilt=-1, tail_angle=80),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head1_tilt=-2, head2_tilt=-2, head3_tilt=-2, tail_angle=70),
        'AttackStrike': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=1, head1_tilt=1, head2_tilt=1, head3_tilt=1, tail_angle=110),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head1_tilt=-1, head2_tilt=-1, head3_tilt=-1, tail_angle=90),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head1_tilt=-3, head2_tilt=-3, head3_tilt=-3, crouch=2, tail_angle=120),
        'TurnLeft': dict(leg_front_shift=-1, leg_back_shift=0, torso_shift=-1, head1_tilt=-1, head2_tilt=-1, head3_tilt=0, tail_angle=100),
        'TurnRight': dict(leg_front_shift=0, leg_back_shift=1, torso_shift=1, head1_tilt=0, head2_tilt=1, head3_tilt=1, tail_angle=80),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head1_tilt=4, head2_tilt=4, head3_tilt=4, crouch=4, tail_angle=130),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head1_tilt=4, head2_tilt=4, head3_tilt=4, crouch=5, tail_angle=135),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 75)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-8, 8))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-10, 12))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_succubus_texture(animation_state='Idle'):
    """Полноценная система анимаций для суккуба (дальнобойный демон-маг) с более контрастной демонической палитрой."""
    cache_key = f'succubus_v2_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]

    def build_pose(
        leg_front_shift=0,
        leg_back_shift=0,
        torso_shift=0,
        head_tilt=0,
        crouch=0,
        wing_flap=0,
        magic_orb_angle=0,
        magic_orb_raise=0,
        magic_orb_size=0,
    ):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        
        shadow = (10, 4, 5, 200)
        # Более «адская» суккуба: бледная кожа, почти чёрные крылья и яркие акценты
        skin = (220, 170, 160)
        skin_dark = (185, 120, 115)
        skin_light = (240, 195, 185)
        dress = (150, 30, 80)
        dress_dark = (90, 20, 55)
        dress_detail = (190, 60, 110)
        horn = (160, 120, 120)
        horn_dark = (120, 80, 80)
        eye_glow = (255, 90, 170)
        eye_bright = (255, 160, 215)
        wing = (45, 15, 35)
        wing_dark = (25, 8, 20)
        magic = (255, 110, 210)
        magic_bright = (255, 170, 235)
        
        base_y = crouch
        
        # Тень
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Ноги (в платье)
        left_leg = pygame.Rect(14 + leg_back_shift, 24 + base_y, 6, 12)
        right_leg = pygame.Rect(26 + leg_front_shift, 24 + base_y, 6, 12)
        pygame.draw.rect(body, dress, left_leg)
        pygame.draw.rect(body, dress_dark, left_leg, 1)
        pygame.draw.rect(body, dress, right_leg)
        pygame.draw.rect(body, dress_dark, right_leg, 1)
        # Детали платья на ногах
        pygame.draw.line(body, dress_detail, (17 + leg_back_shift, 26 + base_y), (17 + leg_back_shift, 34 + base_y), 1)
        pygame.draw.line(body, dress_detail, (29 + leg_front_shift, 26 + base_y), (29 + leg_front_shift, 34 + base_y), 1)
        # Сапоги
        pygame.draw.rect(body, (70, 30, 45), (14 + leg_back_shift, 34 + base_y, 6, 4))
        pygame.draw.rect(body, (90, 40, 55), (26 + leg_front_shift, 34 + base_y, 6, 4))
        
        # Тело (детализированное)
        torso = pygame.Rect(15 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, dress, torso)
        pygame.draw.rect(body, dress_dark, torso, 2)
        pygame.draw.rect(body, dress_dark, (17 + torso_shift, 16 + base_y, 12, 8))
        pygame.draw.line(body, dress_detail, (17 + torso_shift, 16 + base_y), (17 + torso_shift, 24 + base_y), 1)
        pygame.draw.line(body, dress_detail, (29 + torso_shift, 16 + base_y), (29 + torso_shift, 24 + base_y), 1)
        # Детали платья
        pygame.draw.line(body, dress_detail, (19 + torso_shift, 18 + base_y), (19 + torso_shift, 22 + base_y), 1)
        pygame.draw.line(body, dress_detail, (23 + torso_shift, 18 + base_y), (23 + torso_shift, 22 + base_y), 1)
        pygame.draw.line(body, dress_detail, (27 + torso_shift, 18 + base_y), (27 + torso_shift, 22 + base_y), 1)
        
        # Руки (детализированные)
        left_arm = pygame.Rect(13 + torso_shift, 16 + base_y, 4, 10)
        right_arm = pygame.Rect(29 + torso_shift, 16 + base_y, 4, 10)
        pygame.draw.rect(body, skin, left_arm)
        pygame.draw.rect(body, skin_dark, left_arm, 1)
        pygame.draw.rect(body, skin, right_arm)
        pygame.draw.rect(body, skin_dark, right_arm, 1)
        # Детали мышц на руках
        pygame.draw.line(body, skin_dark, (15 + torso_shift, 18 + base_y), (15 + torso_shift, 24 + base_y), 1)
        pygame.draw.line(body, skin_dark, (31 + torso_shift, 18 + base_y), (31 + torso_shift, 24 + base_y), 1)
        
        # Голова (детализированная)
        head_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        head_x = 23 + torso_shift
        head_y = 6 + base_y + head_tilt
        # Основная форма
        pygame.draw.ellipse(head_surface, skin_light, (head_x - 4, head_y - 4, 8, 8))
        pygame.draw.ellipse(head_surface, skin_dark, (head_x - 3, head_y - 3, 6, 6))
        pygame.draw.ellipse(head_surface, skin, (head_x - 2, head_y - 2, 4, 4))
        # Рога (загнутые)
        horn_left_points = [(head_x - 2, head_y - 3), (head_x - 5, head_y - 6), (head_x - 4, head_y - 4)]
        horn_right_points = [(head_x + 2, head_y - 3), (head_x + 5, head_y - 6), (head_x + 4, head_y - 4)]
        pygame.draw.polygon(head_surface, horn, horn_left_points)
        pygame.draw.polygon(head_surface, horn, horn_right_points)
        pygame.draw.polygon(head_surface, horn_dark, horn_left_points, 1)
        pygame.draw.polygon(head_surface, horn_dark, horn_right_points, 1)
        # Глаза (яркие)
        pygame.draw.circle(head_surface, eye_glow, (head_x - 2, head_y), 2)
        pygame.draw.circle(head_surface, eye_bright, (head_x - 2, head_y), 1)
        pygame.draw.circle(head_surface, eye_glow, (head_x + 2, head_y), 2)
        pygame.draw.circle(head_surface, eye_bright, (head_x + 2, head_y), 1)
        # Рот
        pygame.draw.arc(head_surface, (140, 30, 70), (head_x - 1, head_y + 2, 2, 2), 0, 3.14, 2)
        body.blit(head_surface, (0, 0))
        
        # Крылья (перепончатые, тёмные с прожилками)
        wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        wing_offset = int(wing_flap * 1.5)
        # Левое крыло (детализированное)
        wing_points_left = [
            (12 + torso_shift, 16 + base_y),
            (8 + torso_shift, 24 + base_y + wing_offset),
            (23 + torso_shift, 20 + base_y),
            (16 + torso_shift, 18 + base_y)
        ]
        pygame.draw.polygon(wings, wing, wing_points_left)
        pygame.draw.polygon(wings, wing_dark, wing_points_left, 1)
        # Прожилки на крыле
        pygame.draw.line(wings, wing_dark, (12 + torso_shift, 16 + base_y), (8 + torso_shift, 24 + base_y + wing_offset), 1)
        pygame.draw.line(wings, wing_dark, (16 + torso_shift, 18 + base_y), (12 + torso_shift, 22 + base_y + wing_offset), 1)
        # Правое крыло
        wing_points_right = [
            (34 + torso_shift, 16 + base_y),
            (38 + torso_shift, 24 + base_y - wing_offset),
            (23 + torso_shift, 20 + base_y),
            (30 + torso_shift, 18 + base_y)
        ]
        pygame.draw.polygon(wings, wing, wing_points_right)
        pygame.draw.polygon(wings, wing_dark, wing_points_right, 1)
        # Прожилки
        pygame.draw.line(wings, wing_dark, (34 + torso_shift, 16 + base_y), (38 + torso_shift, 24 + base_y - wing_offset), 1)
        pygame.draw.line(wings, wing_dark, (30 + torso_shift, 18 + base_y), (34 + torso_shift, 22 + base_y - wing_offset), 1)
        body.blit(wings, (0, 0))
        
        # Магический шар (для атаки)
        if magic_orb_size > 0:
            orb = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            orb_base_x = 30 + torso_shift
            orb_base_y = 20 + base_y + magic_orb_raise
            angle_rad = math.radians(magic_orb_angle)
            orb_x = orb_base_x + int(14 * math.cos(angle_rad))
            orb_y = orb_base_y - int(14 * math.sin(angle_rad))
            size = 5 + magic_orb_size
            pygame.draw.circle(orb, magic_bright, (orb_x, orb_y), size)
            pygame.draw.circle(orb, magic, (orb_x, orb_y), size - 1)
            pygame.draw.circle(orb, (255, 180, 240), (orb_x, orb_y), size - 2)
            body.blit(orb, (0, 0))
        
        # Размытие движения убрано (создавало свечение)
        
        return body

    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, wing_flap=0, magic_orb_angle=0, magic_orb_raise=0, magic_orb_size=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, wing_flap=1, magic_orb_angle=0, magic_orb_raise=0, magic_orb_size=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, wing_flap=2, magic_orb_angle=0, magic_orb_raise=0, magic_orb_size=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, wing_flap=-2, magic_orb_angle=0, magic_orb_raise=0, magic_orb_size=0),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, wing_flap=-1, magic_orb_angle=45, magic_orb_raise=-2, magic_orb_size=1),
        'AttackAim': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-1, wing_flap=-1, magic_orb_angle=30, magic_orb_raise=-4, magic_orb_size=2),
        'AttackRelease': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, wing_flap=3, magic_orb_angle=0, magic_orb_raise=-6, magic_orb_size=3),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, wing_flap=0, magic_orb_angle=0, magic_orb_raise=0, magic_orb_size=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, wing_flap=-1, magic_orb_angle=0, magic_orb_raise=0, magic_orb_size=0),
        'TurnLeft': dict(leg_front_shift=-1, leg_back_shift=0, torso_shift=-1, head_tilt=-1, wing_flap=-1, magic_orb_angle=0, magic_orb_raise=0, magic_orb_size=0),
        'TurnRight': dict(leg_front_shift=0, leg_back_shift=1, torso_shift=1, head_tilt=1, wing_flap=1, magic_orb_angle=0, magic_orb_raise=0, magic_orb_size=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, wing_flap=-2, magic_orb_angle=0, magic_orb_raise=0, magic_orb_size=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, wing_flap=-2, magic_orb_angle=0, magic_orb_raise=0, magic_orb_size=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 75)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-8, 8))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-10, 12))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


# Texture loaders for creatures that need migration
def load_miner_texture(animation_state='Idle'):
    """Процедурная анимация шахтёра."""
    cache_key = f'miner_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, 
                  pickaxe_angle=0, pickaxe_raise=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (40, 35, 30, 170)
        clothes = (80, 70, 60)
        clothes_dark = (60, 50, 40)
        skin = (220, 190, 160)
        helmet = (100, 100, 100)
        pickaxe_wood = (120, 80, 50)
        pickaxe_metal = (150, 150, 150)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Ноги
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, clothes, left_leg)
        pygame.draw.rect(body, clothes_dark, left_leg, 1)
        pygame.draw.rect(body, clothes, right_leg)
        pygame.draw.rect(body, clothes_dark, right_leg, 1)
        
        # Тело
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, clothes, torso)
        pygame.draw.rect(body, clothes_dark, torso, 2)
        
        # Голова
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 5, head_y, 10, 8))
        pygame.draw.ellipse(body, helmet, (head_x - 6, head_y - 2, 12, 6))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 2, head_y + 3), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 2, head_y + 3), 1)
        
        # Кирка
        if pickaxe_raise != 0 or pickaxe_angle != 0:
            pickaxe = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(pickaxe_angle)
            base_x = 28 + torso_shift
            base_y_pick = 18 + base_y + pickaxe_raise
            end_x = base_x + int(12 * math.cos(angle_rad))
            end_y = base_y_pick - int(12 * math.sin(angle_rad))
            pygame.draw.line(pickaxe, pickaxe_wood, (base_x, base_y_pick), (end_x, end_y), 2)
            pygame.draw.circle(pickaxe, pickaxe_metal, (end_x, end_y), 3)
            body.blit(pickaxe, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, pickaxe_angle=0, pickaxe_raise=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, pickaxe_angle=0, pickaxe_raise=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, pickaxe_angle=0, pickaxe_raise=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, pickaxe_angle=0, pickaxe_raise=0),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, pickaxe_angle=-45, pickaxe_raise=-2),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, pickaxe_angle=45, pickaxe_raise=-4),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, pickaxe_angle=0, pickaxe_raise=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, pickaxe_angle=0, pickaxe_raise=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, pickaxe_angle=0, pickaxe_raise=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, pickaxe_angle=0, pickaxe_raise=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_spearthrower_texture(animation_state='Idle'):
    """Процедурная анимация метателя копий."""
    cache_key = f'spearthrower_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  spear_angle=0, spear_raise=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (40, 35, 30, 170)
        clothes = (100, 80, 60)
        clothes_dark = (70, 55, 40)
        skin = (220, 190, 160)
        spear_wood = (120, 80, 50)
        spear_metal = (180, 180, 200)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, clothes, left_leg)
        pygame.draw.rect(body, clothes_dark, left_leg, 1)
        pygame.draw.rect(body, clothes, right_leg)
        pygame.draw.rect(body, clothes_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, clothes, torso)
        pygame.draw.rect(body, clothes_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 5, head_y, 10, 8))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 2, head_y + 3), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 2, head_y + 3), 1)
        
        if spear_raise != 0 or spear_angle != 0:
            spear = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(spear_angle)
            base_x = 28 + torso_shift
            base_y_spear = 18 + base_y + spear_raise
            end_x = base_x + int(15 * math.cos(angle_rad))
            end_y = base_y_spear - int(15 * math.sin(angle_rad))
            pygame.draw.line(spear, spear_wood, (base_x, base_y_spear), (end_x, end_y), 2)
            pygame.draw.circle(spear, spear_metal, (end_x, end_y), 2)
            body.blit(spear, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, spear_angle=0, spear_raise=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, spear_angle=0, spear_raise=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, spear_angle=0, spear_raise=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, spear_angle=0, spear_raise=0),
        'CastStart': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, spear_angle=-30, spear_raise=-2),
        'CastRelease': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, spear_angle=30, spear_raise=-4),
        'CastRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, spear_angle=0, spear_raise=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, spear_angle=0, spear_raise=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, spear_angle=0, spear_raise=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, spear_angle=0, spear_raise=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_bearrider_texture(animation_state='Idle'):
    """Процедурная анимация медвежьего всадника."""
    cache_key = f'bearrider_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  bear_head_tilt=0, weapon_angle=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (40, 35, 30, 170)
        bear_fur = (100, 60, 40)
        bear_fur_dark = (70, 40, 25)
        rider_clothes = (80, 70, 60)
        rider_clothes_dark = (60, 50, 40)
        skin = (220, 190, 160)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Медведь тело
        bear_body = pygame.Rect(10 + torso_shift, 20 + base_y, 24, 16)
        pygame.draw.ellipse(body, bear_fur, bear_body)
        pygame.draw.ellipse(body, bear_fur_dark, bear_body, 2)
        
        # Медведь ноги
        bear_legs = [
            pygame.Rect(12 + leg_back_shift, 34 + base_y, 5, 6),
            pygame.Rect(27 + leg_front_shift, 34 + base_y, 5, 6),
        ]
        for leg in bear_legs:
            pygame.draw.rect(body, bear_fur, leg)
            pygame.draw.rect(body, bear_fur_dark, leg, 1)
        
        # Всадник
        rider_torso = pygame.Rect(16 + torso_shift, 12 + base_y, 12, 10)
        pygame.draw.rect(body, rider_clothes, rider_torso)
        pygame.draw.rect(body, rider_clothes_dark, rider_torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 4 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 4, head_y, 8, 6))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 1, head_y + 2), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 1, head_y + 2), 1)
        
        # Голова медведя
        bear_head_x = 18 + torso_shift
        bear_head_y = 18 + base_y + bear_head_tilt
        pygame.draw.ellipse(body, bear_fur, (bear_head_x - 6, bear_head_y, 12, 10))
        pygame.draw.ellipse(body, bear_fur_dark, (bear_head_x - 4, bear_head_y + 2, 8, 6))
        pygame.draw.circle(body, (40, 20, 20), (bear_head_x - 2, bear_head_y + 4), 2)
        pygame.draw.circle(body, (40, 20, 20), (bear_head_x + 2, bear_head_y + 4), 2)
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, bear_head_tilt=0, weapon_angle=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, bear_head_tilt=1, weapon_angle=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, bear_head_tilt=0, weapon_angle=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, bear_head_tilt=0, weapon_angle=0),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, bear_head_tilt=-2, weapon_angle=-30),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, bear_head_tilt=2, weapon_angle=30),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, bear_head_tilt=0, weapon_angle=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, bear_head_tilt=-2, weapon_angle=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, bear_head_tilt=3, weapon_angle=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, bear_head_tilt=3, weapon_angle=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_runemage_texture(animation_state='Idle'):
    """Процедурная анимация рунного мага."""
    cache_key = f'runemage_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  staff_angle=0, staff_raise=0, rune_glow=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (40, 35, 30, 170)
        robe = (60, 50, 80)
        robe_dark = (40, 30, 50)
        skin = (220, 190, 160)
        staff_wood = (100, 70, 50)
        rune_color = (150 + rune_glow, 150 + rune_glow, 200 + rune_glow)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, robe, left_leg)
        pygame.draw.rect(body, robe_dark, left_leg, 1)
        pygame.draw.rect(body, robe, right_leg)
        pygame.draw.rect(body, robe_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, robe, torso)
        pygame.draw.rect(body, robe_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 5, head_y, 10, 8))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 2, head_y + 3), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 2, head_y + 3), 1)
        
        if staff_raise != 0 or staff_angle != 0:
            staff = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(staff_angle)
            base_x = 28 + torso_shift
            base_y_staff = 18 + base_y + staff_raise
            end_x = base_x + int(14 * math.cos(angle_rad))
            end_y = base_y_staff - int(14 * math.sin(angle_rad))
            pygame.draw.line(staff, staff_wood, (base_x, base_y_staff), (end_x, end_y), 2)
            if rune_glow > 0:
                pygame.draw.circle(staff, rune_color, (end_x, end_y), 4)
            body.blit(staff, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, staff_angle=0, staff_raise=0, rune_glow=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, staff_angle=2, staff_raise=-1, rune_glow=10),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, staff_angle=4, staff_raise=-1, rune_glow=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, staff_angle=-4, staff_raise=-1, rune_glow=0),
        'CastStart': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, staff_angle=-15, staff_raise=-3, rune_glow=20),
        'CastRelease': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, staff_angle=10, staff_raise=-4, rune_glow=40),
        'CastRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, staff_angle=4, staff_raise=-1, rune_glow=10),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, staff_angle=8, staff_raise=1, rune_glow=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, staff_angle=20, staff_raise=3, rune_glow=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, staff_angle=20, staff_raise=3, rune_glow=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_jarl_texture(animation_state='Idle'):
    """Процедурная анимация ярла."""
    cache_key = f'jarl_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  weapon_angle=0, weapon_raise=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (40, 35, 30, 170)
        armor = (120, 100, 80)
        armor_dark = (80, 60, 50)
        skin = (220, 190, 160)
        weapon_metal = (180, 180, 200)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, armor, left_leg)
        pygame.draw.rect(body, armor_dark, left_leg, 1)
        pygame.draw.rect(body, armor, right_leg)
        pygame.draw.rect(body, armor_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, armor, torso)
        pygame.draw.rect(body, armor_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 5, head_y, 10, 8))
        pygame.draw.ellipse(body, armor, (head_x - 6, head_y - 2, 12, 6))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 2, head_y + 3), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 2, head_y + 3), 1)
        
        if weapon_raise != 0 or weapon_angle != 0:
            weapon = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(weapon_angle)
            base_x = 28 + torso_shift
            base_y_weapon = 18 + base_y + weapon_raise
            end_x = base_x + int(12 * math.cos(angle_rad))
            end_y = base_y_weapon - int(12 * math.sin(angle_rad))
            pygame.draw.line(weapon, weapon_metal, (base_x, base_y_weapon), (end_x, end_y), 3)
            body.blit(weapon, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, weapon_angle=0, weapon_raise=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, weapon_angle=2, weapon_raise=-1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, weapon_angle=5, weapon_raise=-1),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, weapon_angle=-5, weapon_raise=-1),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, weapon_angle=-25, weapon_raise=-3),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, weapon_angle=20, weapon_raise=-4),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, weapon_angle=5, weapon_raise=-1),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, weapon_angle=12, weapon_raise=1),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, weapon_angle=40, weapon_raise=3),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, weapon_angle=45, weapon_raise=3),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


# Additional texture loaders for remaining creatures
def load_scout_texture(animation_state='Idle'):
    """Процедурная анимация разведчика."""
    cache_key = f'scout_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  dagger_angle=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (30, 25, 20, 170)
        clothes = (50, 50, 50)
        clothes_dark = (30, 30, 30)
        skin = (200, 180, 150)
        dagger_metal = (150, 150, 170)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, clothes, left_leg)
        pygame.draw.rect(body, clothes_dark, left_leg, 1)
        pygame.draw.rect(body, clothes, right_leg)
        pygame.draw.rect(body, clothes_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, clothes, torso)
        pygame.draw.rect(body, clothes_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 5, head_y, 10, 8))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 2, head_y + 3), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 2, head_y + 3), 1)
        
        if dagger_angle != 0:
            dagger = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(dagger_angle)
            base_x = 28 + torso_shift
            base_y_dagger = 18 + base_y
            end_x = base_x + int(8 * math.cos(angle_rad))
            end_y = base_y_dagger - int(8 * math.sin(angle_rad))
            pygame.draw.line(dagger, dagger_metal, (base_x, base_y_dagger), (end_x, end_y), 2)
            body.blit(dagger, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, dagger_angle=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, dagger_angle=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, dagger_angle=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, dagger_angle=0),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, dagger_angle=-25),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, dagger_angle=20),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, dagger_angle=5),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, dagger_angle=12),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, dagger_angle=40),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, dagger_angle=45),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_beast_texture(animation_state='Idle'):
    """Процедурная анимация зверя."""
    cache_key = f'beast_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  tail_angle=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (30, 25, 20, 170)
        fur = (80, 60, 40)
        fur_dark = (50, 35, 25)
        eye_glow = (200, 100, 50)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        torso = pygame.Rect(12 + torso_shift, 18 + base_y, 20, 14)
        pygame.draw.ellipse(body, fur, torso)
        pygame.draw.ellipse(body, fur_dark, torso, 2)
        
        left_leg = pygame.Rect(14 + leg_back_shift, 32 + base_y, 5, 6)
        right_leg = pygame.Rect(25 + leg_front_shift, 32 + base_y, 5, 6)
        pygame.draw.rect(body, fur, left_leg)
        pygame.draw.rect(body, fur_dark, left_leg, 1)
        pygame.draw.rect(body, fur, right_leg)
        pygame.draw.rect(body, fur_dark, right_leg, 1)
        
        head_x = 20 + torso_shift
        head_y = 14 + base_y + head_tilt
        pygame.draw.ellipse(body, fur, (head_x - 6, head_y, 12, 10))
        pygame.draw.ellipse(body, fur_dark, (head_x - 4, head_y + 2, 8, 6))
        pygame.draw.circle(body, eye_glow, (head_x - 2, head_y + 4), 2)
        pygame.draw.circle(body, eye_glow, (head_x + 2, head_y + 4), 2)
        
        if tail_angle != 0:
            tail = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(tail_angle)
            base_x = 30 + torso_shift
            base_y_tail = 24 + base_y
            end_x = base_x + int(8 * math.cos(angle_rad))
            end_y = base_y_tail - int(8 * math.sin(angle_rad))
            pygame.draw.line(tail, fur, (base_x, base_y_tail), (end_x, end_y), 3)
            body.blit(tail, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, tail_angle=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, tail_angle=5),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, tail_angle=10),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, tail_angle=-10),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, tail_angle=-15),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, tail_angle=15),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, tail_angle=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, tail_angle=-10),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, tail_angle=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, tail_angle=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_minotaur_texture(animation_state='Idle'):
    """Процедурная анимация минотавра."""
    cache_key = f'minotaur_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  weapon_angle=0, horn_tilt=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (40, 35, 30, 170)
        fur = (120, 80, 60)
        fur_dark = (80, 50, 35)
        skin = (200, 180, 150)
        weapon_metal = (180, 180, 200)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 28 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 28 + base_y, 6, 10)
        pygame.draw.rect(body, fur, left_leg)
        pygame.draw.rect(body, fur_dark, left_leg, 1)
        pygame.draw.rect(body, fur, right_leg)
        pygame.draw.rect(body, fur_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 16 + base_y, 16, 14)
        pygame.draw.rect(body, fur, torso)
        pygame.draw.rect(body, fur_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 8 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 6, head_y, 12, 10))
        pygame.draw.ellipse(body, fur_dark, (head_x - 4, head_y + 2, 8, 6))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 2, head_y + 4), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 2, head_y + 4), 1)
        
        # Рога
        horn_angle = math.radians(horn_tilt)
        horn1_x = head_x - 3 + int(4 * math.cos(horn_angle))
        horn1_y = head_y - 2 - int(4 * math.sin(horn_angle))
        horn2_x = head_x + 3 + int(4 * math.cos(horn_angle))
        horn2_y = head_y - 2 - int(4 * math.sin(horn_angle))
        pygame.draw.line(body, fur_dark, (head_x - 3, head_y), (horn1_x, horn1_y), 2)
        pygame.draw.line(body, fur_dark, (head_x + 3, head_y), (horn2_x, horn2_y), 2)
        
        if weapon_angle != 0:
            weapon = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(weapon_angle)
            base_x = 28 + torso_shift
            base_y_weapon = 20 + base_y
            end_x = base_x + int(12 * math.cos(angle_rad))
            end_y = base_y_weapon - int(12 * math.sin(angle_rad))
            pygame.draw.line(weapon, weapon_metal, (base_x, base_y_weapon), (end_x, end_y), 3)
            body.blit(weapon, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, weapon_angle=0, horn_tilt=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, weapon_angle=2, horn_tilt=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, weapon_angle=5, horn_tilt=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, weapon_angle=-5, horn_tilt=0),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, weapon_angle=-25, horn_tilt=-5),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, weapon_angle=20, horn_tilt=5),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, weapon_angle=5, horn_tilt=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, weapon_angle=12, horn_tilt=-3),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, weapon_angle=40, horn_tilt=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, weapon_angle=45, horn_tilt=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_witch_texture(animation_state='Idle'):
    """Процедурная анимация ведьмы."""
    cache_key = f'witch_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  staff_angle=0, staff_raise=0, magic_glow=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (30, 25, 20, 170)
        robe = (40, 30, 50)
        robe_dark = (25, 20, 30)
        skin = (200, 180, 150)
        staff_wood = (80, 60, 40)
        magic_color = (150 + magic_glow, 100 + magic_glow, 200 + magic_glow)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, robe, left_leg)
        pygame.draw.rect(body, robe_dark, left_leg, 1)
        pygame.draw.rect(body, robe, right_leg)
        pygame.draw.rect(body, robe_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, robe, torso)
        pygame.draw.rect(body, robe_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 5, head_y, 10, 8))
        pygame.draw.ellipse(body, robe, (head_x - 6, head_y - 2, 12, 6))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 2, head_y + 3), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 2, head_y + 3), 1)
        
        if staff_raise != 0 or staff_angle != 0:
            staff = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(staff_angle)
            base_x = 28 + torso_shift
            base_y_staff = 18 + base_y + staff_raise
            end_x = base_x + int(14 * math.cos(angle_rad))
            end_y = base_y_staff - int(14 * math.sin(angle_rad))
            pygame.draw.line(staff, staff_wood, (base_x, base_y_staff), (end_x, end_y), 2)
            if magic_glow > 0:
                pygame.draw.circle(staff, magic_color, (end_x, end_y), 4)
            body.blit(staff, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, staff_angle=0, staff_raise=0, magic_glow=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, staff_angle=2, staff_raise=-1, magic_glow=10),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, staff_angle=4, staff_raise=-1, magic_glow=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, staff_angle=-4, staff_raise=-1, magic_glow=0),
        'CastStart': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, staff_angle=-15, staff_raise=-3, magic_glow=20),
        'CastRelease': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, staff_angle=10, staff_raise=-4, magic_glow=40),
        'CastRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, staff_angle=4, staff_raise=-1, magic_glow=10),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, staff_angle=8, staff_raise=1, magic_glow=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, staff_angle=20, staff_raise=3, magic_glow=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, staff_angle=20, staff_raise=3, magic_glow=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_lizardrider_texture(animation_state='Idle'):
    """Процедурная анимация всадника на ящерице."""
    cache_key = f'lizardrider_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  lizard_head_tilt=0, weapon_angle=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (40, 35, 30, 170)
        lizard_scale = (80, 120, 80)
        lizard_scale_dark = (50, 80, 50)
        rider_clothes = (100, 80, 60)
        rider_clothes_dark = (70, 55, 40)
        skin = (220, 190, 160)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Ящерица тело
        lizard_body = pygame.Rect(10 + torso_shift, 20 + base_y, 24, 16)
        pygame.draw.ellipse(body, lizard_scale, lizard_body)
        pygame.draw.ellipse(body, lizard_scale_dark, lizard_body, 2)
        
        # Ящерица ноги
        lizard_legs = [
            pygame.Rect(12 + leg_back_shift, 34 + base_y, 5, 6),
            pygame.Rect(27 + leg_front_shift, 34 + base_y, 5, 6),
        ]
        for leg in lizard_legs:
            pygame.draw.rect(body, lizard_scale, leg)
            pygame.draw.rect(body, lizard_scale_dark, leg, 1)
        
        # Всадник
        rider_torso = pygame.Rect(16 + torso_shift, 12 + base_y, 12, 10)
        pygame.draw.rect(body, rider_clothes, rider_torso)
        pygame.draw.rect(body, rider_clothes_dark, rider_torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 4 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 4, head_y, 8, 6))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 1, head_y + 2), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 1, head_y + 2), 1)
        
        # Голова ящерицы
        lizard_head_x = 18 + torso_shift
        lizard_head_y = 18 + base_y + lizard_head_tilt
        pygame.draw.ellipse(body, lizard_scale, (lizard_head_x - 6, lizard_head_y, 12, 10))
        pygame.draw.ellipse(body, lizard_scale_dark, (lizard_head_x - 4, lizard_head_y + 2, 8, 6))
        pygame.draw.circle(body, (100, 150, 100), (lizard_head_x - 2, lizard_head_y + 4), 2)
        pygame.draw.circle(body, (100, 150, 100), (lizard_head_x + 2, lizard_head_y + 4), 2)
        
        if weapon_angle != 0:
            weapon = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(weapon_angle)
            base_x = 28 + torso_shift
            base_y_weapon = 18 + base_y
            end_x = base_x + int(12 * math.cos(angle_rad))
            end_y = base_y_weapon - int(12 * math.sin(angle_rad))
            pygame.draw.line(weapon, (180, 180, 200), (base_x, base_y_weapon), (end_x, end_y), 3)
            body.blit(weapon, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, lizard_head_tilt=0, weapon_angle=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, lizard_head_tilt=1, weapon_angle=0),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, lizard_head_tilt=0, weapon_angle=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, lizard_head_tilt=0, weapon_angle=0),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, lizard_head_tilt=-2, weapon_angle=-30),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, lizard_head_tilt=2, weapon_angle=30),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, lizard_head_tilt=0, weapon_angle=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, lizard_head_tilt=-2, weapon_angle=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, lizard_head_tilt=3, weapon_angle=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, lizard_head_tilt=3, weapon_angle=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


# Texture loaders for undead, demon, dwarf, and shadow creatures
def load_deathknight_texture(animation_state='Idle'):
    """Процедурная анимация рыцаря смерти."""
    cache_key = f'deathknight_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  weapon_angle=0, weapon_raise=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (20, 20, 20, 200)
        armor = (60, 60, 70)
        armor_dark = (40, 40, 50)
        weapon_metal = (150, 150, 170)
        eye_glow = (150, 200, 255)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, armor, left_leg)
        pygame.draw.rect(body, armor_dark, left_leg, 1)
        pygame.draw.rect(body, armor, right_leg)
        pygame.draw.rect(body, armor_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, armor, torso)
        pygame.draw.rect(body, armor_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, armor, (head_x - 6, head_y, 12, 8))
        pygame.draw.rect(body, armor_dark, (head_x - 4, head_y + 2, 8, 4))
        pygame.draw.circle(body, eye_glow, (head_x - 2, head_y + 4), 2)
        pygame.draw.circle(body, eye_glow, (head_x + 2, head_y + 4), 2)
        
        if weapon_raise != 0 or weapon_angle != 0:
            weapon = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(weapon_angle)
            base_x = 28 + torso_shift
            base_y_weapon = 18 + base_y + weapon_raise
            end_x = base_x + int(12 * math.cos(angle_rad))
            end_y = base_y_weapon - int(12 * math.sin(angle_rad))
            pygame.draw.line(weapon, weapon_metal, (base_x, base_y_weapon), (end_x, end_y), 3)
            body.blit(weapon, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, weapon_angle=0, weapon_raise=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, weapon_angle=2, weapon_raise=-1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, weapon_angle=5, weapon_raise=-1),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, weapon_angle=-5, weapon_raise=-1),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, weapon_angle=-25, weapon_raise=-3),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, weapon_angle=20, weapon_raise=-4),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, weapon_angle=5, weapon_raise=-1),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, weapon_angle=12, weapon_raise=1),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, weapon_angle=40, weapon_raise=3),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, weapon_angle=45, weapon_raise=3),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_bonedragon_texture(animation_state='Idle'):
    """Процедурная анимация костяного дракона."""
    cache_key = f'bonedragon_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  wing_flap=0, tail_angle=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (20, 20, 20, 200)
        bone = (200, 200, 190)
        bone_dark = (150, 150, 140)
        eye_glow = (150, 200, 255)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        torso = pygame.Rect(10 + torso_shift, 18 + base_y, 24, 18)
        pygame.draw.ellipse(body, bone, torso)
        pygame.draw.ellipse(body, bone_dark, torso, 2)
        
        left_leg = pygame.Rect(12 + leg_back_shift, 34 + base_y, 6, 6)
        right_leg = pygame.Rect(28 + leg_front_shift, 34 + base_y, 6, 6)
        pygame.draw.rect(body, bone, left_leg)
        pygame.draw.rect(body, bone_dark, left_leg, 1)
        pygame.draw.rect(body, bone, right_leg)
        pygame.draw.rect(body, bone_dark, right_leg, 1)
        
        head_x = 18 + torso_shift
        head_y = 16 + base_y + head_tilt
        pygame.draw.ellipse(body, bone, (head_x - 8, head_y, 16, 12))
        pygame.draw.ellipse(body, bone_dark, (head_x - 6, head_y + 2, 12, 8))
        pygame.draw.circle(body, eye_glow, (head_x - 2, head_y + 5), 3)
        pygame.draw.circle(body, eye_glow, (head_x + 2, head_y + 5), 3)
        
        if wing_flap != 0:
            wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            wing_offset = int(wing_flap * 1.5)
            wing_points = [
                (14 + torso_shift, 20 + base_y),
                (8 + torso_shift, 28 + base_y + wing_offset),
                (22 + torso_shift, 22 + base_y),
            ]
            pygame.draw.polygon(wings, bone, wing_points)
            pygame.draw.polygon(wings, bone_dark, wing_points, 1)
            body.blit(wings, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, wing_flap=0, tail_angle=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, wing_flap=1, tail_angle=5),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, wing_flap=2, tail_angle=10),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, wing_flap=-2, tail_angle=-10),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, wing_flap=-1, tail_angle=-15),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, wing_flap=3, tail_angle=15),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, wing_flap=0, tail_angle=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, wing_flap=-1, tail_angle=-10),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, wing_flap=-2, tail_angle=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, wing_flap=-2, tail_angle=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_reaper_texture(animation_state='Idle'):
    """Процедурная анимация жнеца."""
    cache_key = f'reaper_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  scythe_angle=0, scythe_raise=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (20, 20, 20, 200)
        robe = (30, 30, 40)
        robe_dark = (20, 20, 25)
        scythe_wood = (80, 60, 40)
        scythe_metal = (150, 150, 170)
        eye_glow = (200, 100, 100)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, robe, left_leg)
        pygame.draw.rect(body, robe_dark, left_leg, 1)
        pygame.draw.rect(body, robe, right_leg)
        pygame.draw.rect(body, robe_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, robe, torso)
        pygame.draw.rect(body, robe_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, (60, 60, 70), (head_x - 5, head_y, 10, 8))
        pygame.draw.circle(body, eye_glow, (head_x - 2, head_y + 3), 2)
        pygame.draw.circle(body, eye_glow, (head_x + 2, head_y + 3), 2)
        
        if scythe_raise != 0 or scythe_angle != 0:
            scythe = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(scythe_angle)
            base_x = 28 + torso_shift
            base_y_scythe = 18 + base_y + scythe_raise
            end_x = base_x + int(14 * math.cos(angle_rad))
            end_y = base_y_scythe - int(14 * math.sin(angle_rad))
            pygame.draw.line(scythe, scythe_wood, (base_x, base_y_scythe), (end_x, end_y), 2)
            pygame.draw.circle(scythe, scythe_metal, (end_x, end_y), 3)
            body.blit(scythe, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, scythe_angle=0, scythe_raise=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, scythe_angle=2, scythe_raise=-1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, scythe_angle=4, scythe_raise=-1),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, scythe_angle=-4, scythe_raise=-1),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, scythe_angle=-30, scythe_raise=-3),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, scythe_angle=30, scythe_raise=-4),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, scythe_angle=4, scythe_raise=-1),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, scythe_angle=12, scythe_raise=1),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, scythe_angle=40, scythe_raise=3),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, scythe_angle=45, scythe_raise=3),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_bloodpriestess_texture(animation_state='Idle'):
    """Процедурная анимация жрицы крови."""
    cache_key = f'bloodpriestess_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  staff_angle=0, staff_raise=0, blood_glow=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (30, 20, 20, 200)
        robe = (120, 30, 40)
        robe_dark = (80, 20, 25)
        skin = (200, 150, 150)
        staff_wood = (100, 70, 50)
        blood_color = (200 + blood_glow, 50 + blood_glow, 50 + blood_glow)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, robe, left_leg)
        pygame.draw.rect(body, robe_dark, left_leg, 1)
        pygame.draw.rect(body, robe, right_leg)
        pygame.draw.rect(body, robe_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, robe, torso)
        pygame.draw.rect(body, robe_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 5, head_y, 10, 8))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 2, head_y + 3), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 2, head_y + 3), 1)
        
        if staff_raise != 0 or staff_angle != 0:
            staff = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(staff_angle)
            base_x = 28 + torso_shift
            base_y_staff = 18 + base_y + staff_raise
            end_x = base_x + int(14 * math.cos(angle_rad))
            end_y = base_y_staff - int(14 * math.sin(angle_rad))
            pygame.draw.line(staff, staff_wood, (base_x, base_y_staff), (end_x, end_y), 2)
            if blood_glow > 0:
                pygame.draw.circle(staff, blood_color, (end_x, end_y), 4)
            body.blit(staff, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, staff_angle=0, staff_raise=0, blood_glow=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, staff_angle=2, staff_raise=-1, blood_glow=10),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, staff_angle=4, staff_raise=-1, blood_glow=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, staff_angle=-4, staff_raise=-1, blood_glow=0),
        'CastStart': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, staff_angle=-15, staff_raise=-3, blood_glow=20),
        'CastRelease': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, staff_angle=10, staff_raise=-4, blood_glow=40),
        'CastRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, staff_angle=4, staff_raise=-1, blood_glow=10),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, staff_angle=8, staff_raise=1, blood_glow=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, staff_angle=20, staff_raise=3, blood_glow=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, staff_angle=20, staff_raise=3, blood_glow=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_devil_texture(animation_state='Idle'):
    """Процедурная анимация дьявола."""
    cache_key = f'devil_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  weapon_angle=0, weapon_raise=0, wing_flap=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (20, 10, 10, 200)
        skin = (150, 50, 50)
        skin_dark = (100, 30, 30)
        weapon_metal = (180, 180, 200)
        eye_glow = (255, 100, 100)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 28 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 28 + base_y, 6, 10)
        pygame.draw.rect(body, skin, left_leg)
        pygame.draw.rect(body, skin_dark, left_leg, 1)
        pygame.draw.rect(body, skin, right_leg)
        pygame.draw.rect(body, skin_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 16 + base_y, 16, 14)
        pygame.draw.rect(body, skin, torso)
        pygame.draw.rect(body, skin_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 8 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 6, head_y, 12, 10))
        pygame.draw.ellipse(body, skin_dark, (head_x - 4, head_y + 2, 8, 6))
        pygame.draw.circle(body, eye_glow, (head_x - 2, head_y + 4), 2)
        pygame.draw.circle(body, eye_glow, (head_x + 2, head_y + 4), 2)
        
        if wing_flap != 0:
            wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            wing_offset = int(wing_flap * 1.5)
            wing_points = [
                (14 + torso_shift, 20 + base_y),
                (8 + torso_shift, 28 + base_y + wing_offset),
                (22 + torso_shift, 22 + base_y),
            ]
            pygame.draw.polygon(wings, skin_dark, wing_points)
            pygame.draw.polygon(wings, (80, 20, 20), wing_points, 1)
            body.blit(wings, (0, 0))
        
        if weapon_raise != 0 or weapon_angle != 0:
            weapon = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(weapon_angle)
            base_x = 28 + torso_shift
            base_y_weapon = 20 + base_y + weapon_raise
            end_x = base_x + int(12 * math.cos(angle_rad))
            end_y = base_y_weapon - int(12 * math.sin(angle_rad))
            pygame.draw.line(weapon, weapon_metal, (base_x, base_y_weapon), (end_x, end_y), 3)
            body.blit(weapon, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, weapon_angle=0, weapon_raise=0, wing_flap=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, weapon_angle=2, weapon_raise=-1, wing_flap=1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, weapon_angle=5, weapon_raise=-1, wing_flap=2),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, weapon_angle=-5, weapon_raise=-1, wing_flap=-2),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, weapon_angle=-25, weapon_raise=-3, wing_flap=-1),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, weapon_angle=20, weapon_raise=-4, wing_flap=3),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, weapon_angle=5, weapon_raise=-1, wing_flap=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, weapon_angle=12, weapon_raise=1, wing_flap=-1),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, weapon_angle=40, weapon_raise=3, wing_flap=-2),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, weapon_angle=45, weapon_raise=3, wing_flap=-2),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_hellhorse_texture(animation_state='Idle'):
    """Процедурная анимация адского коня."""
    cache_key = f'hellhorse_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  mane_flame=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (20, 10, 10, 200)
        fur = (80, 30, 30)
        fur_dark = (50, 15, 15)
        eye_glow = (255, 100, 100)
        flame_color = (255, 150 + mane_flame, 50 + mane_flame)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        torso = pygame.Rect(12 + torso_shift, 20 + base_y, 20, 16)
        pygame.draw.ellipse(body, fur, torso)
        pygame.draw.ellipse(body, fur_dark, torso, 2)
        
        left_leg = pygame.Rect(14 + leg_back_shift, 34 + base_y, 5, 6)
        right_leg = pygame.Rect(25 + leg_front_shift, 34 + base_y, 5, 6)
        pygame.draw.rect(body, fur, left_leg)
        pygame.draw.rect(body, fur_dark, left_leg, 1)
        pygame.draw.rect(body, fur, right_leg)
        pygame.draw.rect(body, fur_dark, right_leg, 1)
        
        head_x = 20 + torso_shift
        head_y = 16 + base_y + head_tilt
        pygame.draw.ellipse(body, fur, (head_x - 6, head_y, 12, 10))
        pygame.draw.ellipse(body, fur_dark, (head_x - 4, head_y + 2, 8, 6))
        pygame.draw.circle(body, eye_glow, (head_x - 2, head_y + 4), 2)
        pygame.draw.circle(body, eye_glow, (head_x + 2, head_y + 4), 2)
        
        if mane_flame > 0:
            flame = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            flame_points = [
                (head_x - 4, head_y - 2),
                (head_x - 2, head_y - 4 - mane_flame),
                (head_x, head_y - 2),
                (head_x + 2, head_y - 4 - mane_flame),
                (head_x + 4, head_y - 2),
            ]
            pygame.draw.polygon(flame, flame_color, flame_points)
            body.blit(flame, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, mane_flame=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, mane_flame=2),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, mane_flame=3),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, mane_flame=3),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, mane_flame=5),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, mane_flame=8),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, mane_flame=2),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, mane_flame=1),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, mane_flame=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, mane_flame=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_forgedragon_texture(animation_state='Idle'):
    """Процедурная анимация кузнечного дракона."""
    cache_key = f'forgedragon_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  wing_flap=0, fire_glow=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (40, 30, 20, 200)
        metal = (120, 100, 80)
        metal_dark = (80, 60, 50)
        fire_color = (255, 150 + fire_glow, 50 + fire_glow)
        eye_glow = (255, 200, 100)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        torso = pygame.Rect(10 + torso_shift, 18 + base_y, 24, 18)
        pygame.draw.ellipse(body, metal, torso)
        pygame.draw.ellipse(body, metal_dark, torso, 2)
        
        left_leg = pygame.Rect(12 + leg_back_shift, 34 + base_y, 6, 6)
        right_leg = pygame.Rect(28 + leg_front_shift, 34 + base_y, 6, 6)
        pygame.draw.rect(body, metal, left_leg)
        pygame.draw.rect(body, metal_dark, left_leg, 1)
        pygame.draw.rect(body, metal, right_leg)
        pygame.draw.rect(body, metal_dark, right_leg, 1)
        
        head_x = 18 + torso_shift
        head_y = 16 + base_y + head_tilt
        pygame.draw.ellipse(body, metal, (head_x - 8, head_y, 16, 12))
        pygame.draw.ellipse(body, metal_dark, (head_x - 6, head_y + 2, 12, 8))
        pygame.draw.circle(body, eye_glow, (head_x - 2, head_y + 5), 3)
        pygame.draw.circle(body, eye_glow, (head_x + 2, head_y + 5), 3)
        
        if fire_glow > 0:
            fire = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            fire_points = [
                (head_x, head_y + 8),
                (head_x - 2, head_y + 12 + fire_glow),
                (head_x, head_y + 10),
                (head_x + 2, head_y + 12 + fire_glow),
            ]
            pygame.draw.polygon(fire, fire_color, fire_points)
            body.blit(fire, (0, 0))
        
        if wing_flap != 0:
            wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            wing_offset = int(wing_flap * 1.5)
            wing_points = [
                (14 + torso_shift, 20 + base_y),
                (8 + torso_shift, 28 + base_y + wing_offset),
                (22 + torso_shift, 22 + base_y),
            ]
            pygame.draw.polygon(wings, metal, wing_points)
            pygame.draw.polygon(wings, metal_dark, wing_points, 1)
            body.blit(wings, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, wing_flap=0, fire_glow=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, wing_flap=1, fire_glow=5),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, wing_flap=2, fire_glow=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, wing_flap=-2, fire_glow=0),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, wing_flap=-1, fire_glow=10),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, wing_flap=3, fire_glow=20),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, wing_flap=0, fire_glow=5),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, wing_flap=-1, fire_glow=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, wing_flap=-2, fire_glow=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, wing_flap=-2, fire_glow=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_mountainruler_texture(animation_state='Idle'):
    """Процедурная анимация правителя гор."""
    cache_key = f'mountainruler_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  weapon_angle=0, weapon_raise=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (40, 35, 30, 170)
        armor = (140, 120, 100)
        armor_dark = (100, 80, 70)
        skin = (220, 190, 160)
        weapon_metal = (180, 180, 200)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, armor, left_leg)
        pygame.draw.rect(body, armor_dark, left_leg, 1)
        pygame.draw.rect(body, armor, right_leg)
        pygame.draw.rect(body, armor_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, armor, torso)
        pygame.draw.rect(body, armor_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 5, head_y, 10, 8))
        pygame.draw.ellipse(body, armor, (head_x - 6, head_y - 2, 12, 6))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 2, head_y + 3), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 2, head_y + 3), 1)
        
        if weapon_raise != 0 or weapon_angle != 0:
            weapon = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(weapon_angle)
            base_x = 28 + torso_shift
            base_y_weapon = 18 + base_y + weapon_raise
            end_x = base_x + int(12 * math.cos(angle_rad))
            end_y = base_y_weapon - int(12 * math.sin(angle_rad))
            pygame.draw.line(weapon, weapon_metal, (base_x, base_y_weapon), (end_x, end_y), 3)
            body.blit(weapon, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, weapon_angle=0, weapon_raise=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, weapon_angle=2, weapon_raise=-1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, weapon_angle=5, weapon_raise=-1),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, weapon_angle=-5, weapon_raise=-1),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, weapon_angle=-25, weapon_raise=-3),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, weapon_angle=20, weapon_raise=-4),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, weapon_angle=5, weapon_raise=-1),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, weapon_angle=12, weapon_raise=1),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, weapon_angle=40, weapon_raise=3),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, weapon_angle=45, weapon_raise=3),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_volkhv_texture(animation_state='Idle'):
    """Процедурная анимация волхва."""
    cache_key = f'volkhv_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  staff_angle=0, staff_raise=0, magic_glow=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (40, 35, 30, 170)
        robe = (100, 80, 60)
        robe_dark = (70, 55, 40)
        skin = (220, 190, 160)
        staff_wood = (100, 70, 50)
        magic_color = (150 + magic_glow, 150 + magic_glow, 200 + magic_glow)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        left_leg = pygame.Rect(14 + leg_back_shift, 26 + base_y, 6, 10)
        right_leg = pygame.Rect(24 + leg_front_shift, 26 + base_y, 6, 10)
        pygame.draw.rect(body, robe, left_leg)
        pygame.draw.rect(body, robe_dark, left_leg, 1)
        pygame.draw.rect(body, robe, right_leg)
        pygame.draw.rect(body, robe_dark, right_leg, 1)
        
        torso = pygame.Rect(14 + torso_shift, 14 + base_y, 16, 12)
        pygame.draw.rect(body, robe, torso)
        pygame.draw.rect(body, robe_dark, torso, 2)
        
        head_x = 22 + torso_shift
        head_y = 6 + base_y + head_tilt
        pygame.draw.ellipse(body, skin, (head_x - 5, head_y, 10, 8))
        pygame.draw.circle(body, (40, 30, 20), (head_x - 2, head_y + 3), 1)
        pygame.draw.circle(body, (40, 30, 20), (head_x + 2, head_y + 3), 1)
        
        if staff_raise != 0 or staff_angle != 0:
            staff = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(staff_angle)
            base_x = 28 + torso_shift
            base_y_staff = 18 + base_y + staff_raise
            end_x = base_x + int(14 * math.cos(angle_rad))
            end_y = base_y_staff - int(14 * math.sin(angle_rad))
            pygame.draw.line(staff, staff_wood, (base_x, base_y_staff), (end_x, end_y), 2)
            if magic_glow > 0:
                pygame.draw.circle(staff, magic_color, (end_x, end_y), 4)
            body.blit(staff, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, staff_angle=0, staff_raise=0, magic_glow=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, staff_angle=2, staff_raise=-1, magic_glow=10),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, staff_angle=4, staff_raise=-1, magic_glow=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, staff_angle=-4, staff_raise=-1, magic_glow=0),
        'CastStart': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, staff_angle=-15, staff_raise=-3, magic_glow=20),
        'CastRelease': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, staff_angle=10, staff_raise=-4, magic_glow=40),
        'CastRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, staff_angle=4, staff_raise=-1, magic_glow=10),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, staff_angle=8, staff_raise=1, magic_glow=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, staff_angle=20, staff_raise=3, magic_glow=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, staff_angle=20, staff_raise=3, magic_glow=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_manticore_texture(animation_state='Idle'):
    """Процедурная анимация мантикоры."""
    cache_key = f'manticore_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  tail_angle=0, wing_flap=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (30, 25, 20, 170)
        fur = (120, 100, 80)
        fur_dark = (80, 60, 50)
        eye_glow = (200, 150, 100)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        torso = pygame.Rect(12 + torso_shift, 20 + base_y, 20, 16)
        pygame.draw.ellipse(body, fur, torso)
        pygame.draw.ellipse(body, fur_dark, torso, 2)
        
        left_leg = pygame.Rect(14 + leg_back_shift, 34 + base_y, 5, 6)
        right_leg = pygame.Rect(25 + leg_front_shift, 34 + base_y, 5, 6)
        pygame.draw.rect(body, fur, left_leg)
        pygame.draw.rect(body, fur_dark, left_leg, 1)
        pygame.draw.rect(body, fur, right_leg)
        pygame.draw.rect(body, fur_dark, right_leg, 1)
        
        head_x = 20 + torso_shift
        head_y = 16 + base_y + head_tilt
        pygame.draw.ellipse(body, fur, (head_x - 6, head_y, 12, 10))
        pygame.draw.ellipse(body, fur_dark, (head_x - 4, head_y + 2, 8, 6))
        pygame.draw.circle(body, eye_glow, (head_x - 2, head_y + 4), 2)
        pygame.draw.circle(body, eye_glow, (head_x + 2, head_y + 4), 2)
        
        if wing_flap != 0:
            wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            wing_offset = int(wing_flap * 1.5)
            wing_points = [
                (14 + torso_shift, 22 + base_y),
                (8 + torso_shift, 30 + base_y + wing_offset),
                (20 + torso_shift, 24 + base_y),
            ]
            pygame.draw.polygon(wings, fur, wing_points)
            pygame.draw.polygon(wings, fur_dark, wing_points, 1)
            body.blit(wings, (0, 0))
        
        if tail_angle != 0:
            tail = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(tail_angle)
            base_x = 30 + torso_shift
            base_y_tail = 26 + base_y
            end_x = base_x + int(10 * math.cos(angle_rad))
            end_y = base_y_tail - int(10 * math.sin(angle_rad))
            pygame.draw.line(tail, fur, (base_x, base_y_tail), (end_x, end_y), 3)
            pygame.draw.circle(tail, (200, 50, 50), (end_x, end_y), 2)
            body.blit(tail, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, tail_angle=0, wing_flap=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, tail_angle=5, wing_flap=1),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, tail_angle=10, wing_flap=2),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, tail_angle=-10, wing_flap=-2),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, tail_angle=-15, wing_flap=-1),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, tail_angle=15, wing_flap=3),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, tail_angle=0, wing_flap=0),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, tail_angle=-10, wing_flap=-1),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, tail_angle=0, wing_flap=-2),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, tail_angle=0, wing_flap=-2),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_reddragon_texture(animation_state='Idle'):
    """Процедурная анимация красного дракона."""
    cache_key = f'reddragon_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0,
                  wing_flap=0, fire_glow=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (30, 20, 10, 200)
        scale = (180, 60, 40)
        scale_dark = (120, 40, 25)
        fire_color = (255, 150 + fire_glow, 50 + fire_glow)
        eye_glow = (255, 200, 100)
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        torso = pygame.Rect(10 + torso_shift, 18 + base_y, 24, 18)
        pygame.draw.ellipse(body, scale, torso)
        pygame.draw.ellipse(body, scale_dark, torso, 2)
        
        left_leg = pygame.Rect(12 + leg_back_shift, 34 + base_y, 6, 6)
        right_leg = pygame.Rect(28 + leg_front_shift, 34 + base_y, 6, 6)
        pygame.draw.rect(body, scale, left_leg)
        pygame.draw.rect(body, scale_dark, left_leg, 1)
        pygame.draw.rect(body, scale, right_leg)
        pygame.draw.rect(body, scale_dark, right_leg, 1)
        
        head_x = 18 + torso_shift
        head_y = 16 + base_y + head_tilt
        pygame.draw.ellipse(body, scale, (head_x - 8, head_y, 16, 12))
        pygame.draw.ellipse(body, scale_dark, (head_x - 6, head_y + 2, 12, 8))
        pygame.draw.circle(body, eye_glow, (head_x - 2, head_y + 5), 3)
        pygame.draw.circle(body, eye_glow, (head_x + 2, head_y + 5), 3)
        
        if fire_glow > 0:
            fire = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            fire_points = [
                (head_x, head_y + 8),
                (head_x - 2, head_y + 12 + fire_glow),
                (head_x, head_y + 10),
                (head_x + 2, head_y + 12 + fire_glow),
            ]
            pygame.draw.polygon(fire, fire_color, fire_points)
            body.blit(fire, (0, 0))
        
        if wing_flap != 0:
            wings = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            wing_offset = int(wing_flap * 1.5)
            wing_points = [
                (14 + torso_shift, 20 + base_y),
                (8 + torso_shift, 28 + base_y + wing_offset),
                (22 + torso_shift, 22 + base_y),
            ]
            pygame.draw.polygon(wings, scale, wing_points)
            pygame.draw.polygon(wings, scale_dark, wing_points, 1)
            body.blit(wings, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=0, head_tilt=0, crouch=0, wing_flap=0, fire_glow=0),
        'IdleBreath': dict(leg_front_shift=1, leg_back_shift=-1, torso_shift=-1, head_tilt=-1, crouch=0, wing_flap=1, fire_glow=5),
        'Walk': dict(leg_front_shift=2, leg_back_shift=-2, torso_shift=-1, head_tilt=0, crouch=0, wing_flap=2, fire_glow=0),
        'WalkAlt': dict(leg_front_shift=-2, leg_back_shift=2, torso_shift=1, head_tilt=0, crouch=0, wing_flap=-2, fire_glow=0),
        'AttackPrep': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-2, crouch=1, wing_flap=-1, fire_glow=10),
        'AttackStrike': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=1, head_tilt=1, crouch=-1, wing_flap=3, fire_glow=20),
        'AttackRecover': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-1, head_tilt=-1, crouch=0, wing_flap=0, fire_glow=5),
        'Hurt': dict(leg_front_shift=-1, leg_back_shift=1, torso_shift=-2, head_tilt=-3, crouch=2, wing_flap=-1, fire_glow=0),
        'Death': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=4, wing_flap=-2, fire_glow=0),
        'Corpse': dict(leg_front_shift=0, leg_back_shift=0, torso_shift=-2, head_tilt=4, crouch=5, wing_flap=-2, fire_glow=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_beholder_texture(animation_state='Idle'):
    """Процедурная анимация наблюдателя."""
    cache_key = f'beholder_v1_{animation_state}'
    if cache_key in _texture_cache:
        return _texture_cache[cache_key]
    
    def build_pose(torso_shift=0, head_tilt=0, crouch=0, eye_glow=0, tentacle_angle=0):
        body = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        shadow = (20, 20, 30, 200)
        skin = (100, 80, 120)
        skin_dark = (70, 50, 90)
        eye_color = (min(255, 200 + eye_glow), min(255, 150 + eye_glow), min(255, 255 + eye_glow))
        
        base_y = crouch
        pygame.draw.ellipse(body, shadow, (6, CELL_SIZE - 8 - base_y, CELL_SIZE - 12, 6))
        
        # Тело (большой глаз)
        torso = pygame.Rect(12 + torso_shift, 18 + base_y, 20, 18)
        pygame.draw.ellipse(body, skin, torso)
        pygame.draw.ellipse(body, skin_dark, torso, 2)
        
        # Главный глаз
        eye_x = 22 + torso_shift
        eye_y = 26 + base_y + head_tilt
        pygame.draw.circle(body, eye_color, (eye_x, eye_y), 8)
        pygame.draw.circle(body, (40, 30, 50), (eye_x, eye_y), 4)
        pygame.draw.circle(body, (255, 255, 255), (eye_x - 1, eye_y - 1), 2)
        
        # Щупальца
        if tentacle_angle != 0:
            tentacles = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            angle_rad = math.radians(tentacle_angle)
            for i in range(4):
                base_angle = i * 90 + tentacle_angle
                base_rad = math.radians(base_angle)
                start_x = eye_x + int(10 * math.cos(base_rad))
                start_y = eye_y + int(10 * math.sin(base_rad))
                end_x = start_x + int(8 * math.cos(base_rad))
                end_y = start_y + int(8 * math.sin(base_rad))
                pygame.draw.line(tentacles, skin, (start_x, start_y), (end_x, end_y), 2)
            body.blit(tentacles, (0, 0))
        
        return body
    
    params_map = {
        'Idle': dict(torso_shift=0, head_tilt=0, crouch=0, eye_glow=0, tentacle_angle=0),
        'IdleBreath': dict(torso_shift=-1, head_tilt=-1, crouch=0, eye_glow=20, tentacle_angle=5),
        'Walk': dict(torso_shift=-1, head_tilt=0, crouch=0, eye_glow=0, tentacle_angle=10),
        'WalkAlt': dict(torso_shift=1, head_tilt=0, crouch=0, eye_glow=0, tentacle_angle=-10),
        'AttackPrep': dict(torso_shift=-2, head_tilt=-2, crouch=1, eye_glow=40, tentacle_angle=-15),
        'AttackStrike': dict(torso_shift=1, head_tilt=1, crouch=-1, eye_glow=60, tentacle_angle=15),
        'AttackRecover': dict(torso_shift=-1, head_tilt=-1, crouch=0, eye_glow=20, tentacle_angle=0),
        'Hurt': dict(torso_shift=-2, head_tilt=-3, crouch=2, eye_glow=0, tentacle_angle=-10),
        'Death': dict(torso_shift=-2, head_tilt=4, crouch=4, eye_glow=0, tentacle_angle=0),
        'Corpse': dict(torso_shift=-2, head_tilt=4, crouch=5, eye_glow=0, tentacle_angle=0),
    }
    
    surface = build_pose(**params_map.get(animation_state, params_map['Idle']))
    if animation_state == 'Death':
        topple = pygame.transform.rotate(surface, 80)
        result = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        result.blit(topple, (-10, 12))
        surface = result
    elif animation_state == 'Corpse':
        fallen = pygame.transform.rotate(surface, 90)
        corpse_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        corpse_surface.blit(fallen, (-12, 10))
        surface = corpse_surface
    
    _texture_cache[cache_key] = surface
    return surface


def load_image(name, scale=1):
    # Используем процедурную генерацию (как было раньше)
    image = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    # Разделяем имя на части
    parts = name.split('_')
    if len(parts) >= 3 and parts[0] == 'hero':
        # Формат: hero_team_class
        unit = 'hero'
        team = parts[1]
        hero_class = parts[2]
    elif len(parts) >= 2:
        # Обычный формат: unit_team
        unit = '_'.join(parts[:-1])
        team = parts[-1]
        hero_class = None
    else:
        unit = name
        team = 'human'
        hero_class = None
    target_size = None
    if scale != 1:
        target_size = (int(CELL_SIZE * scale), int(CELL_SIZE * scale))

    def _apply_scale(surface):
        if target_size:
            return pygame.transform.smoothscale(surface, target_size)
        return surface
    # Цветовые схемы
    if team == 'human':
        main_color = (180, 160, 100)
        accent = (60, 60, 200)
        metal = (180, 180, 200)
        gold = (255, 215, 0)
        skin = (255, 224, 189)
        cloth = (100, 120, 200)
    elif team == 'dwarf':
        main_color = (100, 120, 160)
        accent = (80, 100, 140)
        metal = (200, 200, 220)
        gold = (255, 215, 0)
        skin = (220, 180, 120)
        cloth = (140, 160, 180)
    elif team == 'shadow':
        main_color = (40, 0, 60)
        accent = (80, 0, 120)
        metal = (100, 80, 120)
        gold = (180, 120, 255)
        skin = (200, 180, 120)
        cloth = (60, 0, 90)
    else:
        main_color = (120, 100, 180)
        accent = (80, 40, 120)
        metal = (180, 180, 200)
        gold = (180, 120, 255)
        skin = (200, 200, 220)
        cloth = (80, 60, 120)
    # Герой
    if unit == 'hero':
        if team == 'human':
            return _apply_scale(_render_human_hero(hero_class))
        elif team == 'elf':
            return _apply_scale(_render_elf_hero(hero_class))
        elif team == 'undead':
            return _apply_scale(_render_undead_hero(hero_class))
        elif team == 'demon':
            return _apply_scale(_render_demon_hero(hero_class))
        elif team == 'dwarf':
            return _apply_scale(_render_dwarf_hero(hero_class))
        elif team == 'shadow':
            return _apply_scale(_render_shadow_hero(hero_class))
        else:
            image.fill(main_color)
            return _apply_scale(image)

    if team == 'human':
        human_unit_textures = {
            'peasant': load_peasant_texture('Idle'),
            'spearman': load_spearman_texture('Idle'),
            'swordsman': load_swordsman_texture('Idle'),
            'gryphon': load_gryphon_texture('Idle'),
            'crossbowman': load_crossbowman_texture('Idle'),
        }
        if unit in human_unit_textures:
            return _apply_scale(human_unit_textures[unit])

    if team == 'elf':
        return _apply_scale(_render_elf_unit(unit))
    
    if team == 'undead':
        undead_unit_textures = {
            'skeleton': load_skeleton_texture('Idle'),
        }
        if unit in undead_unit_textures:
            return _apply_scale(undead_unit_textures[unit])
    
    if team == 'demon':
        demon_unit_textures = {
            'imp': load_imp_texture('Idle'),
            'gog': load_gog_texture('Idle'),
            'demon': load_demon_texture('Idle'),
            'cerberus': load_cerberus_texture('Idle'),
            'succubus': load_succubus_texture('Idle'),
        }
        if unit in demon_unit_textures:
            return _apply_scale(demon_unit_textures[unit])
    # Воин
    elif unit == 'warrior':
        image.fill(main_color)
        # Тело
        pygame.draw.rect(image, metal, (12, 16, 16, 18))
        # Шлем
        pygame.draw.ellipse(image, metal, (12, 6, 16, 14))
        pygame.draw.rect(image, accent, (12, 12, 16, 6))
        # Меч
        pygame.draw.rect(image, (180,180,180), (26, 24, 6, 16))
        pygame.draw.rect(image, (120,120,120), (28, 36, 2, 6))
        # Щит
        pygame.draw.ellipse(image, accent, (2, 22, 10, 16))
    # Лучник
    elif unit == 'archer':
        image.fill(main_color)
        # Капюшон
        pygame.draw.ellipse(image, cloth, (10, 4, 20, 16))
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 10, 12, 10))
        # Тело
        pygame.draw.rect(image, cloth, (14, 20, 12, 16))
        # Лук
        pygame.draw.arc(image, (120, 80, 40), (4, 10, 28, 28), 3.14/2, 3*3.14/2, 3)
        # Стрела
        pygame.draw.line(image, (180,180,180), (18, 24), (28, 8), 2)
    # Рыцарь
    elif unit == 'knight':
        image.fill(main_color)
        # Латы
        pygame.draw.rect(image, metal, (10, 16, 20, 20))
        pygame.draw.ellipse(image, metal, (10, 6, 20, 14))
        # Щит
        pygame.draw.ellipse(image, accent, (2, 22, 12, 18))
        # Меч
        pygame.draw.rect(image, (180,180,180), (28, 24, 6, 16))
        pygame.draw.rect(image, (120,120,120), (30, 36, 2, 6))
        # Перо на шлеме
        pygame.draw.line(image, gold, (20, 8), (20, 2), 2)
    # --- Люди ---
    elif unit == 'peasant':
        # Основа
        image.fill((140, 120, 100))
        # Детализированная одежда крестьянина
        pygame.draw.rect(image, (180,140,80), (14, 20, 12, 18))  # рубаха
        pygame.draw.rect(image, (160,120,60), (16, 22, 8, 14))  # внутренняя рубаха
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 8, 12, 12))
        pygame.draw.circle(image, (0,0,0), (18, 14), 1)  # глаз
        pygame.draw.circle(image, (0,0,0), (22, 14), 1)  # глаз
        pygame.draw.circle(image, (180,160,120), (20, 18), 1)  # нос
        # Волосы
        pygame.draw.ellipse(image, (100,80,40), (14, 6, 12, 8))
        # Мотыга
        pygame.draw.line(image, (120,80,40), (20, 38), (8, 44), 4)  # рукоять
        pygame.draw.line(image, (120,80,40), (20, 38), (32, 44), 4)  # рукоять
        pygame.draw.polygon(image, (160,160,180), [(8,44),(4,48),(12,48)])  # наконечник
        pygame.draw.polygon(image, (160,160,180), [(32,44),(28,48),(36,48)])  # наконечник
        # Пояс
        pygame.draw.rect(image, (100,80,60), (14, 32, 12, 4))
    elif unit == 'spearman':
        # Основа
        image.fill((120, 100, 80))
        # Детализированная броня копейщика
        pygame.draw.rect(image, metal, (14, 18, 12, 18))  # кольчуга
        pygame.draw.rect(image, (140,140,160), (16, 20, 8, 14))  # внутренняя кольчуга
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 8, 12, 12))
        pygame.draw.circle(image, (0,0,0), (18, 14), 1)
        pygame.draw.circle(image, (0,0,0), (22, 14), 1)
        # Шлем
        pygame.draw.ellipse(image, metal, (12, 6, 16, 10))
        pygame.draw.rect(image, accent, (14, 8, 12, 6))
        # Копье
        pygame.draw.line(image, (200,180,160), (20, 20), (20, 44), 3)
        pygame.draw.polygon(image, (160,160,180), [(20,20),(18,16),(22,16)])  # наконечник
        pygame.draw.polygon(image, (120,80,60), [(20,44),(18,48),(22,48)])  # оперение
        # Щит
        pygame.draw.ellipse(image, accent, (2, 22, 10, 16))
        pygame.draw.circle(image, gold, (7, 30), 2)  # украшение щита
    elif unit == 'crossbowman':
        # ВСЕГДА используем текстуру из файла (старые текстуры)
        texture = load_crossbowman_texture('Idle')
        if texture is not None:
            # Если текстура загружена, используем её
            image.blit(texture, (0, 0))
        else:
            # Если текстура не найдена, создаём простую заглушку (не процедурную генерацию)
            image.fill((100, 120, 140))
            # Простой квадрат как заглушка
            pygame.draw.rect(image, (80, 100, 120), (10, 10, 20, 20))
    elif unit == 'swordsman':
        # Основа
        image.fill((100, 100, 120))
        # Детализированная броня мечника
        pygame.draw.rect(image, metal, (12, 16, 16, 18))  # латы
        pygame.draw.rect(image, (160,160,180), (14, 18, 12, 14))  # внутренние латы
        # Детали брони
        pygame.draw.line(image, (120,120,140), (14, 16), (26, 16), 2)
        pygame.draw.line(image, (120,120,140), (14, 20), (26, 20), 2)
        pygame.draw.line(image, (120,120,140), (14, 24), (26, 24), 2)
        pygame.draw.line(image, (120,120,140), (14, 28), (26, 28), 2)
        # Шлем
        pygame.draw.ellipse(image, metal, (12, 6, 16, 14))
        pygame.draw.rect(image, accent, (12, 12, 16, 6))
        # Лицо
        pygame.draw.ellipse(image, skin, (16, 8, 8, 8))
        pygame.draw.circle(image, (0,0,0), (18, 12), 1)
        pygame.draw.circle(image, (0,0,0), (22, 12), 1)
        # Меч
        pygame.draw.rect(image, (180,180,180), (28, 24, 6, 16))
        pygame.draw.rect(image, (120,120,120), (30, 36, 2, 6))
        pygame.draw.polygon(image, (160,160,180), [(28,24),(26,20),(30,20)])  # гарда
        # Щит
        pygame.draw.ellipse(image, accent, (2, 22, 12, 18))
        pygame.draw.circle(image, gold, (8, 31), 2)
    elif unit == 'gryphon':
        # Основа
        image.fill((200,180,120))
        # Детализированное тело грифона
        pygame.draw.ellipse(image, (200,180,120), (8, 20, 24, 16))  # тело
        pygame.draw.ellipse(image, (180,160,100), (10, 22, 20, 12))  # тень тела
        # Голова
        pygame.draw.ellipse(image, (255,224,189), (20, 8, 12, 12))
        pygame.draw.ellipse(image, (240,200,160), (22, 10, 8, 8))  # тень головы
        # Глаза
        pygame.draw.circle(image, (60,40,20), (24, 14), 2)
        pygame.draw.circle(image, (60,40,20), (28, 14), 2)
        pygame.draw.circle(image, (255,255,255), (25, 13), 1)  # блик
        pygame.draw.circle(image, (255,255,255), (29, 13), 1)  # блик
        # Клюв
        pygame.draw.polygon(image, (255,215,0), [(30,14),(36,12),(32,18)])
        pygame.draw.polygon(image, (200,180,0), [(30,14),(34,13),(31,16)])
        # Крылья
        pygame.draw.polygon(image, (180,180,220), [(8,24),(0,8),(16,16)])
        pygame.draw.polygon(image, (180,180,220), [(32,24),(40,8),(24,16)])
        # Перья на крыльях
        for i in range(3):
            pygame.draw.line(image, (160,160,200), (4+i*2, 12), (8+i*2, 20), 2)
            pygame.draw.line(image, (160,160,200), (36-i*2, 12), (32-i*2, 20), 2)
        # Лапы
        pygame.draw.circle(image, (160,140,100), (16, 36), 3)
        pygame.draw.circle(image, (160,140,100), (24, 36), 3)
    # --- Нежить ---
    elif unit == 'skeleton':
        # Основа в холодных фиолетово-серых тонах
        image.fill((40, 40, 70))
        # Череп
        pygame.draw.circle(image, (225, 230, 235), (20, 14), 9)
        pygame.draw.circle(image, (190, 195, 205), (20, 14), 7)
        # Глазницы с холодным свечением
        pygame.draw.circle(image, (10, 10, 30), (17, 12), 2)
        pygame.draw.circle(image, (10, 10, 30), (23, 12), 2)
        pygame.draw.circle(image, (130, 90, 210), (17, 12), 1)
        pygame.draw.circle(image, (130, 90, 210), (23, 12), 1)
        # Челюсть
        pygame.draw.arc(image, (60, 60, 90), (16, 16, 8, 4), 0, 3.14, 2)
        # Позвоночник
        pygame.draw.rect(image, (215, 220, 230), (18, 22, 4, 12))
        # Рёбра
        for i in range(3):
            pygame.draw.line(image, (215, 220, 230), (14 + i * 2, 24 + i * 2), (26 - i * 2, 24 + i * 2), 2)
        # Руки
        pygame.draw.line(image, (215, 220, 230), (14, 26), (8, 34), 2)
        pygame.draw.line(image, (215, 220, 230), (26, 26), (32, 34), 2)
        # Ноги
        pygame.draw.line(image, (215, 220, 230), (18, 34), (16, 44), 2)
        pygame.draw.line(image, (215, 220, 230), (22, 34), (24, 44), 2)
    elif unit == 'zombie':
        # Зомби в более тусклой, гнилой палитре
        image.fill((30, 45, 35))
        # Тело
        pygame.draw.rect(image, (90,125,95), (12, 18, 16, 18))
        pygame.draw.rect(image, (70,105,80), (14, 20, 12, 14))
        # Лицо
        pygame.draw.ellipse(image, (155,195,160), (14, 8, 12, 12))
        pygame.draw.ellipse(image, (135,175,140), (16, 10, 8, 8))  # тень лица
        # Глаза с бледным свечением
        pygame.draw.circle(image, (20,55,30), (18, 14), 2)
        pygame.draw.circle(image, (20,55,30), (22, 14), 2)
        pygame.draw.circle(image, (140,190,140), (18, 14), 1)
        pygame.draw.circle(image, (140,190,140), (22, 14), 1)
        # Рот
        pygame.draw.arc(image, (80,115,85), (18, 18, 4, 3), 0, 3.14, 2)
        # Раны
        pygame.draw.line(image, (110,70,70), (16, 24), (20, 28), 2)
        pygame.draw.line(image, (110,70,70), (24, 26), (28, 30), 2)
        # Руки
        pygame.draw.line(image, (90,130,95), (20, 36), (10, 44), 4)
        pygame.draw.line(image, (90,130,95), (20, 36), (30, 44), 4)
        # Когти
        pygame.draw.polygon(image, (95,145,100), [(10,44),(8,48),(12,48)])
        pygame.draw.polygon(image, (95,145,100), [(30,44),(28,48),(32,48)])
    elif unit == 'ghost':
        # Основа
        image.fill((40, 40, 80))
        # Детализированный призрак
        ghost_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Тело призрака
        pygame.draw.ellipse(ghost_surface, (220,220,255,180), (10, 8, 20, 18))
        pygame.draw.ellipse(ghost_surface, (200,200,235,160), (12, 10, 16, 14))
        # Лицо
        pygame.draw.ellipse(ghost_surface, (240,240,255,200), (14, 10, 12, 8))
        # Глаза
        pygame.draw.circle(ghost_surface, (100,100,200,180), (18, 14), 2)
        pygame.draw.circle(ghost_surface, (100,100,200,180), (22, 14), 2)
        # Рот
        pygame.draw.arc(ghost_surface, (120,120,200,160), (18, 16, 4, 3), 0, 3.14, 2)
        # Плащ
        pygame.draw.arc(ghost_surface, (120,120,180,120), (6, 18, 28, 18), 3.14, 0, 3)
        # Мистические частицы
        for i in range(5):
            pygame.draw.circle(ghost_surface, (200,200,255,100), 
                             (10+i*5, 20+i*2), 1)
        # Применяем к основному изображению
        image.blit(ghost_surface, (0, 0))
    elif unit == 'vampire':
        # Вампир в холодно-кровавой палитре
        image.fill((40, 20, 40))
        # Тело
        pygame.draw.ellipse(image, (110,30,80), (12, 16, 16, 18))
        pygame.draw.ellipse(image, (90,20,60), (14, 18, 12, 14))
        # Лицо
        pygame.draw.ellipse(image, (225,225,235), (16, 8, 8, 8))
        pygame.draw.ellipse(image, (195,195,205), (17, 9, 6, 6))
        # Глаза
        pygame.draw.circle(image, (200,20,40), (18, 12), 2)
        pygame.draw.circle(image, (200,20,40), (22, 12), 2)
        pygame.draw.circle(image, (255,110,130), (18, 12), 1)
        pygame.draw.circle(image, (255,110,130), (22, 12), 1)
        # Плащ
        pygame.draw.polygon(image, (150,0,20), [(20,16),(24,20),(16,20)])
        pygame.draw.polygon(image, (120,0,15), [(20,16),(22,18),(18,18)])
        # Клыки
        pygame.draw.rect(image, (255,255,255), (18, 16, 2, 4))
        pygame.draw.rect(image, (255,255,255), (20, 16, 2, 4))
        # Руки
        pygame.draw.line(image, (90,20,55), (20, 34), (12, 44), 3)
        pygame.draw.line(image, (90,20,55), (20, 34), (28, 44), 3)
        # Когти
        pygame.draw.polygon(image, (70,0,15), [(12,44),(10,48),(14,48)])
        pygame.draw.polygon(image, (70,0,15), [(28,44),(26,48),(30,48)])
    elif unit == 'lich':
        # Лич — более холодная палитра костей и тёмной мантии
        image.fill((26, 22, 40))
        # Тело
        pygame.draw.ellipse(image, (215,220,230), (10, 8, 20, 18))
        pygame.draw.ellipse(image, (185,190,200), (12, 10, 16, 14))
        # Лицо
        pygame.draw.ellipse(image, (235,240,245), (14, 10, 12, 8))
        # Глаза
        pygame.draw.circle(image, (70,40,130), (18, 14), 3)
        pygame.draw.circle(image, (70,40,130), (22, 14), 3)
        pygame.draw.circle(image, (150,110,210), (18, 14), 1)
        pygame.draw.circle(image, (150,110,210), (22, 14), 1)
        # Рот
        pygame.draw.arc(image, (150,155,180), (18, 16, 4, 3), 0, 3.14, 2)
        # Мантия
        pygame.draw.rect(image, (105,80,165), (14, 26, 12, 10))
        pygame.draw.rect(image, (80,55,140), (16, 28, 8, 6))
        # Корона
        pygame.draw.polygon(image, (180,135,255), [(20, 8), (18, 2), (22, 2)])
        pygame.draw.polygon(image, (150,100,225), [(20, 8), (19, 4), (21, 4)])
        # Мистические руны
        pygame.draw.circle(image, (195,160,250), (16, 30), 1)
        pygame.draw.circle(image, (195,160,250), (24, 30), 1)
        pygame.draw.circle(image, (195,160,250), (20, 34), 1)
        # Плащ
        pygame.draw.arc(image, (60,35,110), (6, 18, 28, 18), 3.14, 0, 3)
    # --- Эльфы ---
    elif unit == 'pixie':
        # Основа
        image.fill((80, 180, 80))
        # Детализированная фея
        pygame.draw.ellipse(image, (220,255,220), (12, 8, 16, 16))  # тело
        pygame.draw.ellipse(image, (200,235,200), (14, 10, 12, 12))  # внутреннее тело
        # Лицо
        pygame.draw.circle(image, (255,255,255), (20, 12), 4)  # голова
        pygame.draw.circle(image, (240,240,240), (20, 12), 3)  # внутренняя голова
        # Глаза
        pygame.draw.circle(image, (0,120,0), (18, 12), 1)
        pygame.draw.circle(image, (0,120,0), (22, 12), 1)
        pygame.draw.circle(image, (0,180,0), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (0,180,0), (22, 12), 1)  # свечение
        # Рот
        pygame.draw.arc(image, (0,100,0), (19, 14, 2, 2), 0, 3.14, 1)
        # Крылья
        pygame.draw.ellipse(image, (180,255,180), (8, 16, 24, 12))  # крылья
        pygame.draw.ellipse(image, (160,235,160), (10, 18, 20, 8))  # внутренние крылья
        # Корона
        pygame.draw.polygon(image, (255,255,180), [(20,12),(24,4),(16,4)])
        pygame.draw.polygon(image, (255,255,200), [(20,12),(22,6),(18,6)])
        # Блёстки
        for i in range(3):
            pygame.draw.circle(image, (255,255,180,120), (20+(-1)**i*4, 18), 2)
        # Магические частицы
        for i in range(4):
            angle = i * 1.57  # 90 градусов
            x = 20 + int(8 * math.cos(angle))
            y = 20 + int(8 * math.sin(angle))
            pygame.draw.circle(image, (200,255,200,150), (x, y), 1)
    elif unit == 'elf_scout':
        # Основа
        image.fill((60, 160, 60))
        # Детализированный эльфийский разведчик
        pygame.draw.rect(image, (120,220,120), (14, 18, 12, 18))  # туника
        pygame.draw.rect(image, (100,200,100), (16, 20, 8, 14))  # внутренняя туника
        # Лицо
        pygame.draw.ellipse(image, (220,255,200), (14, 8, 12, 12))
        pygame.draw.ellipse(image, (200,235,180), (16, 10, 8, 8))  # тень лица
        # Глаза
        pygame.draw.circle(image, (0,120,0), (18, 14), 1)
        pygame.draw.circle(image, (0,120,0), (22, 14), 1)
        pygame.draw.circle(image, (0,180,0), (18, 14), 1)  # свечение
        pygame.draw.circle(image, (0,180,0), (22, 14), 1)  # свечение
        # Уши
        pygame.draw.polygon(image, (220,255,200), [(14,12),(10,6),(18,10)])
        pygame.draw.polygon(image, (220,255,200), [(26,12),(30,6),(22,10)])
        # Копье
        pygame.draw.line(image, (60,180,60), (20, 20), (20, 44), 3)
        pygame.draw.polygon(image, (255,255,180), [(18,8),(22,8),(20,2)])
        pygame.draw.polygon(image, (160,160,180), [(20,20),(18,16),(22,16)])  # наконечник
        # Плащ
        pygame.draw.polygon(image, (80,180,120), [(14,36),(26,36),(20,44)])
        pygame.draw.polygon(image, (60,160,100), [(16,36),(24,36),(20,40)])
        # Пояс
        pygame.draw.rect(image, (100,180,80), (14, 30, 12, 4))
    elif unit == 'elf_archer':
        # Основа
        image.fill((80, 180, 80))
        # Детализированный эльфийский лучник
        pygame.draw.rect(image, (120,220,120), (14, 20, 12, 16))  # туника
        pygame.draw.rect(image, (100,200,100), (16, 22, 8, 12))  # внутренняя туника
        # Лицо
        pygame.draw.ellipse(image, (220,255,200), (14, 8, 12, 12))
        pygame.draw.ellipse(image, (200,235,180), (16, 10, 8, 8))  # тень лица
        # Глаза
        pygame.draw.circle(image, (0,120,0), (18, 14), 1)
        pygame.draw.circle(image, (0,120,0), (22, 14), 1)
        pygame.draw.circle(image, (0,180,0), (18, 14), 1)  # свечение
        pygame.draw.circle(image, (0,180,0), (22, 14), 1)  # свечение
        # Уши
        pygame.draw.polygon(image, (220,255,200), [(14,12),(10,6),(18,10)])
        pygame.draw.polygon(image, (220,255,200), [(26,12),(30,6),(22,10)])
        # Лук
        pygame.draw.line(image, (60,180,60), (8, 36), (32, 36), 3)
        pygame.draw.line(image, (255,215,0), (20, 36), (20, 28), 2)
        pygame.draw.polygon(image, (160,160,180), [(20,28),(18,24),(22,24)])  # наконечник
        # Капюшон
        pygame.draw.ellipse(image, (60,120,60), (12, 4, 16, 10))
        pygame.draw.rect(image, (40,100,40), (14, 6, 12, 6))
        # Колчан
        pygame.draw.rect(image, (180,140,80), (26, 18, 4, 10))
        pygame.draw.rect(image, (160,120,60), (27, 20, 2, 6))
        # Стрелы в колчане
        for i in range(3):
            pygame.draw.line(image, (200,180,160), (26, 20+i*2), (30, 20+i*2), 1)
    elif unit == 'dryad':
        # Основа
        image.fill((60, 140, 60))
        # Детализированная дриада
        pygame.draw.ellipse(image, (120,220,120), (10, 8, 20, 18))  # тело
        pygame.draw.ellipse(image, (100,200,100), (12, 10, 16, 14))  # внутреннее тело
        # Лицо
        pygame.draw.ellipse(image, (200,240,180), (14, 10, 12, 8))
        # Глаза
        pygame.draw.circle(image, (0,120,0), (18, 14), 1)
        pygame.draw.circle(image, (0,120,0), (22, 14), 1)
        pygame.draw.circle(image, (0,180,0), (18, 14), 1)  # свечение
        pygame.draw.circle(image, (0,180,0), (22, 14), 1)  # свечение
        # Уши
        pygame.draw.polygon(image, (200,240,180), [(14,12),(10,6),(18,10)])
        pygame.draw.polygon(image, (200,240,180), [(26,12),(30,6),(22,10)])
        # Корона из листьев
        pygame.draw.polygon(image, (255,255,180), [(20,8),(24,2),(16,2)])
        pygame.draw.polygon(image, (200,255,100), [(20,8),(22,4),(18,4)])
        # Ноги (ствол дерева)
        pygame.draw.rect(image, (80,140,60), (16, 26, 8, 12))
        pygame.draw.rect(image, (60,120,40), (17, 27, 6, 10))
        # Корни
        pygame.draw.line(image, (60,120,40), (16, 38), (10, 44), 2)
        pygame.draw.line(image, (60,120,40), (24, 38), (30, 44), 2)
        # Цветы
        for i in range(3):
            pygame.draw.circle(image, (255,200,220), (20+(-1)**i*6, 18), 2)
            pygame.draw.circle(image, (255,180,200), (20+(-1)**i*6, 18), 1)
        # Листья
        for i in range(4):
            angle = i * 1.57
            x = 20 + int(6 * math.cos(angle))
            y = 20 + int(6 * math.sin(angle))
            pygame.draw.circle(image, (100,200,100,150), (x, y), 2)
    elif unit == 'ent':
        # Основа
        image.fill((40, 100, 40))
        # Детализированный энт
        pygame.draw.rect(image, (100,80,40), (14, 20, 12, 18))  # тело
        pygame.draw.rect(image, (80,60,20), (16, 22, 8, 14))  # внутреннее тело
        # Лицо
        pygame.draw.ellipse(image, (120,220,120), (10, 8, 20, 18))
        pygame.draw.ellipse(image, (100,200,100), (12, 10, 16, 14))  # тень лица
        # Глаза
        pygame.draw.ellipse(image, (40,80,40), (16, 16, 4, 2))
        pygame.draw.ellipse(image, (40,80,40), (20, 16, 4, 2))
        pygame.draw.circle(image, (60,120,60), (18, 17), 1)  # свечение
        pygame.draw.circle(image, (60,120,60), (22, 17), 1)  # свечение
        # Рот
        pygame.draw.arc(image, (60,120,60), (18, 20, 4, 3), 0, 3.14, 2)
        # Ветви-руки
        pygame.draw.line(image, (80,140,60), (20, 38), (10, 44), 4)
        pygame.draw.line(image, (80,140,60), (20, 38), (30, 44), 4)
        # Листья на руках
        pygame.draw.circle(image, (100,180,100), (10, 44), 3)
        pygame.draw.circle(image, (100,180,100), (30, 44), 3)
        # Ветви на голове
        pygame.draw.line(image, (100,80,40), (20, 8), (10, 2), 2)
        pygame.draw.line(image, (100,80,40), (20, 8), (30, 2), 2)
        # Листья на голове
        pygame.draw.circle(image, (120,200,120), (10, 2), 2)
        pygame.draw.circle(image, (120,200,120), (30, 2), 2)
        # Корни-ноги
        pygame.draw.line(image, (60,120,40), (16, 38), (12, 44), 3)
        pygame.draw.line(image, (60,120,40), (24, 38), (28, 44), 3)
        # Мох на теле
        pygame.draw.circle(image, (80,160,80), (18, 28), 2)
        pygame.draw.circle(image, (80,160,80), (22, 30), 2)
    # --- Демоны ---
    elif unit == 'imp':
        # Основа
        image.fill((120, 40, 20))
        # Детализированный бес
        pygame.draw.ellipse(image, (255,180,120), (12, 8, 16, 16))  # тело
        pygame.draw.ellipse(image, (235,160,100), (14, 10, 12, 12))  # внутреннее тело
        # Лицо
        pygame.draw.circle(image, (255,220,180), (20, 12), 4)  # голова
        pygame.draw.circle(image, (235,200,160), (20, 12), 3)  # внутренняя голова
        # Глаза
        pygame.draw.circle(image, (200,0,0), (18, 12), 2)
        pygame.draw.circle(image, (200,0,0), (22, 12), 2)
        pygame.draw.circle(image, (255,100,100), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (255,100,100), (22, 12), 1)  # свечение
        # Рога
        pygame.draw.polygon(image, (120,40,20), [(20,8),(24,2),(16,2)])
        pygame.draw.polygon(image, (100,20,0), [(20,8),(22,4),(18,4)])
        # Рот
        pygame.draw.arc(image, (180,0,0), (19, 14, 2, 2), 0, 3.14, 1)
        # Клыки
        pygame.draw.rect(image, (255,255,255), (19, 14, 1, 2))
        pygame.draw.rect(image, (255,255,255), (20, 14, 1, 2))
        # Хвост
        pygame.draw.polygon(image, (255,80,20), [(20,12),(24,20),(16,20)])
        pygame.draw.polygon(image, (235,60,0), [(20,12),(22,16),(18,16)])
        # Крылья
        pygame.draw.polygon(image, (200,80,80), [(12,16),(8,24),(20,20)])
        pygame.draw.polygon(image, (200,80,80), [(28,16),(32,24),(20,20)])
        # Лапы
        pygame.draw.circle(image, (200,120,80), (16, 24), 2)
        pygame.draw.circle(image, (200,120,80), (24, 24), 2)
    elif unit == 'gog':
        # Основа
        image.fill((160, 60, 40))
        # Детализированный гог
        pygame.draw.ellipse(image, (255,180,120), (12, 8, 16, 16))  # тело
        pygame.draw.ellipse(image, (235,160,100), (14, 10, 12, 12))  # внутреннее тело
        # Лицо
        pygame.draw.circle(image, (255,220,180), (20, 12), 4)  # голова
        pygame.draw.circle(image, (235,200,160), (20, 12), 3)  # внутренняя голова
        # Глаза
        pygame.draw.circle(image, (200,0,0), (18, 12), 2)
        pygame.draw.circle(image, (200,0,0), (22, 12), 2)
        pygame.draw.circle(image, (255,100,100), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (255,100,100), (22, 12), 1)  # свечение
        # Рога
        pygame.draw.polygon(image, (255,80,20), [(20,8),(24,2),(16,2)])
        pygame.draw.polygon(image, (235,60,0), [(20,8),(22,4),(18,4)])
        # Рот
        pygame.draw.arc(image, (180,0,0), (19, 14, 2, 2), 0, 3.14, 1)
        # Тело
        pygame.draw.rect(image, (180,60,40), (16, 24, 8, 12))
        pygame.draw.rect(image, (160,40,20), (17, 25, 6, 10))
        # Пламя
        pygame.draw.polygon(image, (255,120,40), [(20,24),(24,32),(16,32)])
        pygame.draw.polygon(image, (255,100,20), [(20,24),(22,28),(18,28)])
        # Лапы
        pygame.draw.circle(image, (200,120,80), (16, 36), 2)
        pygame.draw.circle(image, (200,120,80), (24, 36), 2)
    elif unit == 'demon':
        # Основа
        image.fill((100, 20, 10))
        # Детализированный демон
        pygame.draw.ellipse(image, (255,180,120), (10, 8, 20, 18))  # тело
        pygame.draw.ellipse(image, (235,160,100), (12, 10, 16, 14))  # внутреннее тело
        # Лицо
        pygame.draw.circle(image, (255,220,180), (20, 12), 4)  # голова
        pygame.draw.circle(image, (235,200,160), (20, 12), 3)  # внутренняя голова
        # Глаза
        pygame.draw.circle(image, (200,0,0), (18, 12), 2)
        pygame.draw.circle(image, (200,0,0), (22, 12), 2)
        pygame.draw.circle(image, (255,100,100), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (255,100,100), (22, 12), 1)  # свечение
        # Рога
        pygame.draw.polygon(image, (255,80,20), [(20,8),(24,2),(16,2)])
        pygame.draw.polygon(image, (235,60,0), [(20,8),(22,4),(18,4)])
        # Рот
        pygame.draw.arc(image, (180,0,0), (19, 14, 2, 2), 0, 3.14, 1)
        # Клыки
        pygame.draw.rect(image, (255,255,255), (19, 14, 1, 3))
        pygame.draw.rect(image, (255,255,255), (20, 14, 1, 3))
        # Тело
        pygame.draw.rect(image, (180,60,40), (14, 26, 12, 10))
        pygame.draw.rect(image, (160,40,20), (15, 27, 10, 8))
        # Хвост
        pygame.draw.polygon(image, (255,80,20), [(20,26),(24,36),(16,36)])
        pygame.draw.polygon(image, (235,60,0), [(20,26),(22,31),(18,31)])
        # Крылья
        pygame.draw.polygon(image, (180,60,40), [(10,18),(2,8),(20,20)])
        pygame.draw.polygon(image, (180,60,40), [(30,18),(38,8),(20,20)])
        # Лапы
        pygame.draw.circle(image, (200,120,80), (16, 36), 3)
        pygame.draw.circle(image, (200,120,80), (24, 36), 3)
    elif unit == 'cerberus':
        # Основа
        image.fill((80, 20, 10))
        # Детализированный цербер
        pygame.draw.ellipse(image, (180,60,40), (8, 20, 24, 16))  # тело
        pygame.draw.ellipse(image, (160,40,20), (10, 22, 20, 12))  # тень тела
        # Голова 1
        pygame.draw.ellipse(image, (255,180,120), (10, 8, 10, 10))
        pygame.draw.ellipse(image, (235,160,100), (12, 10, 6, 6))  # тень головы
        # Голова 2
        pygame.draw.ellipse(image, (255,180,120), (20, 8, 10, 10))
        pygame.draw.ellipse(image, (235,160,100), (22, 10, 6, 6))  # тень головы
        # Голова 3
        pygame.draw.ellipse(image, (255,180,120), (16, 4, 8, 8))
        pygame.draw.ellipse(image, (235,160,100), (17, 5, 6, 6))  # тень головы
        # Глаза головы 1
        pygame.draw.circle(image, (255,80,20), (14, 12), 2)
        pygame.draw.circle(image, (255,100,40), (14, 12), 1)  # свечение
        # Глаза головы 2
        pygame.draw.circle(image, (255,80,20), (22, 12), 2)
        pygame.draw.circle(image, (255,100,40), (22, 12), 1)  # свечение
        # Глаза головы 3
        pygame.draw.circle(image, (255,80,20), (18, 8), 2)
        pygame.draw.circle(image, (255,100,40), (18, 8), 1)  # свечение
        # Рты
        pygame.draw.arc(image, (180,0,0), (13, 14, 4, 3), 0, 3.14, 1)
        pygame.draw.arc(image, (180,0,0), (21, 14, 4, 3), 0, 3.14, 1)
        pygame.draw.arc(image, (180,0,0), (17, 10, 2, 2), 0, 3.14, 1)
        # Клыки
        pygame.draw.rect(image, (255,255,255), (14, 16, 1, 2))
        pygame.draw.rect(image, (255,255,255), (22, 16, 1, 2))
        pygame.draw.rect(image, (255,255,255), (18, 12, 1, 2))
        # Хвост
        pygame.draw.polygon(image, (255,80,20), [(20,36),(24,44),(16,44)])
        pygame.draw.polygon(image, (235,60,0), [(20,36),(22,40),(18,40)])
        # Лапы
        pygame.draw.circle(image, (200,120,80), (12, 36), 3)
        pygame.draw.circle(image, (200,120,80), (28, 36), 3)
    elif unit == 'succubus':
        # Основа
        image.fill((140, 40, 60))
        # Детализированная суккуб
        pygame.draw.ellipse(image, (255,180,200), (12, 8, 16, 16))  # тело
        pygame.draw.ellipse(image, (235,160,180), (14, 10, 12, 12))  # внутреннее тело
        # Лицо
        pygame.draw.circle(image, (255,220,220), (20, 12), 4)  # голова
        pygame.draw.circle(image, (235,200,200), (20, 12), 3)  # внутренняя голова
        # Глаза
        pygame.draw.circle(image, (200,0,100), (18, 12), 2)
        pygame.draw.circle(image, (200,0,100), (22, 12), 2)
        pygame.draw.circle(image, (255,100,150), (18, 12), 1)  # свечение
        pygame.draw.circle(image, (255,100,150), (22, 12), 1)  # свечение
        # Рога
        pygame.draw.polygon(image, (180,60,80), [(20,8),(24,2),(16,2)])
        pygame.draw.polygon(image, (160,40,60), [(20,8),(22,4),(18,4)])
        # Рот
        pygame.draw.arc(image, (180,0,100), (19, 14, 2, 2), 0, 3.14, 1)
        # Хвост
        pygame.draw.polygon(image, (255,80,120), [(20,12),(24,20),(16,20)])
        pygame.draw.polygon(image, (235,60,100), [(20,12),(22,16),(18,16)])
        # Крылья
        pygame.draw.polygon(image, (200,80,120), [(12,16),(8,24),(20,20)])
        pygame.draw.polygon(image, (200,80,120), [(28,16),(32,24),(20,20)])
        # Лапы
        pygame.draw.circle(image, (220,140,160), (16, 24), 2)
        pygame.draw.circle(image, (220,140,160), (24, 24), 2)
    # --- Гномы ---
    elif team == 'dwarf':
        if unit == 'hero':
            # Основа - каменный фон
            image.fill((90, 110, 140))
            # Детализированная броня с металлическими пластинами
            pygame.draw.rect(image, (200,200,220), (8, 20, 24, 18))
            pygame.draw.rect(image, (160,160,180), (10, 22, 20, 14))  # внутренняя броня
            pygame.draw.line(image, (120,120,140), (12, 20), (28, 20), 2)  # верхняя пластина
            pygame.draw.line(image, (120,120,140), (12, 24), (28, 24), 2)  # средняя пластина
            pygame.draw.line(image, (120,120,140), (12, 28), (28, 28), 2)  # нижняя пластина
            pygame.draw.line(image, (120,120,140), (12, 32), (28, 32), 2)  # нижняя пластина
            # Лицо с детализацией
            pygame.draw.ellipse(image, (240,220,160), (10, 8, 20, 18))
            pygame.draw.ellipse(image, (200,180,140), (12, 10, 16, 14))  # тень лица
            # Глаза
            pygame.draw.circle(image, (60,40,20), (16, 16), 2)
            pygame.draw.circle(image, (60,40,20), (24, 16), 2)
            pygame.draw.circle(image, (255,255,255), (17, 15), 1)  # блик
            pygame.draw.circle(image, (255,255,255), (25, 15), 1)  # блик
            # Нос
            pygame.draw.circle(image, (180,160,120), (20, 20), 2)
            # Рот
            pygame.draw.arc(image, (160,140,100), (18, 22, 4, 3), 0, 3.14, 2)
            # Детализированный шлем с рогами
            pygame.draw.polygon(image, (180,160,100), [(12,12),(16,4),(20,12),(24,4),(28,12)])
            pygame.draw.polygon(image, (140,120,80), [(14,10),(18,6),(22,10)])  # внутренний шлем
            # Рога
            pygame.draw.polygon(image, (120,100,60), [(14,10),(12,2),(16,6)])
            pygame.draw.polygon(image, (120,100,60), [(26,10),(28,2),(24,6)])
            # Детализированная борода
            pygame.draw.circle(image, (100,80,60), (20, 30), 8)
            pygame.draw.circle(image, (80,60,40), (20, 32), 6)  # тень бороды
            # Украшения на броне
            pygame.draw.circle(image, (255,215,0), (16, 26), 2)  # золотая пуговица
            pygame.draw.circle(image, (255,215,0), (24, 26), 2)  # золотая пуговица
            # Пояс с пряжкой
            pygame.draw.rect(image, (100,80,60), (8, 28, 24, 10))
            pygame.draw.rect(image, (255,215,0), (18, 30, 4, 6))  # золотая пряжка
        elif unit == 'miner':
            # Гном-шахтёр в более «каменной» и тёмной палитре
            image.fill((60, 70, 90))
            # Детализированная одежда
            pygame.draw.rect(image, (150,130,110), (14, 20, 12, 18))  # рубаха
            pygame.draw.rect(image, (110,90,75), (16, 22, 8, 14))    # внутренняя рубаха
            # Лицо
            pygame.draw.ellipse(image, (225,200,150), (14, 8, 12, 12))
            pygame.draw.circle(image, (50,35,18), (18, 14), 1)  # глаз
            pygame.draw.circle(image, (50,35,18), (22, 14), 1)  # глаз
            # Шахтерская каска
            pygame.draw.ellipse(image, (110,95,80), (12, 6, 16, 10))
            pygame.draw.rect(image, (85,70,55), (14, 8, 12, 6))  # внутренняя каска
            # Фонарь на каске
            pygame.draw.circle(image, (255,210,130), (20, 10), 3)
            pygame.draw.circle(image, (255,255,255), (20, 9), 1)  # свет
            # Кирка
            pygame.draw.line(image, (90,70,55), (20, 38), (8, 44), 4)   # рукоять
            pygame.draw.line(image, (90,70,55), (20, 38), (32, 44), 4)  # рукоять
            pygame.draw.polygon(image, metal, [(8,44),(4,48),(12,48)])   # наконечник
            pygame.draw.polygon(image, metal, [(32,44),(28,48),(36,48)]) # наконечник
            # Борода
            pygame.draw.circle(image, (95,75,55), (20, 26), 4)
        elif unit == 'spearthrower':
            # Гном-копьemetатель — более тёмная стальная броня
            image.fill((55, 75, 100))
            # Детализированная броня
            pygame.draw.rect(image, (150,140,130), (14, 18, 12, 18))
            pygame.draw.rect(image, (115,100,85), (16, 20, 8, 14))
            # Лицо
            pygame.draw.ellipse(image, (225,200,150), (14, 8, 12, 12))
            pygame.draw.circle(image, (50,35,18), (18, 14), 1)
            pygame.draw.circle(image, (50,35,18), (22, 14), 1)
            # Шлем с пером
            pygame.draw.ellipse(image, (115,100,85), (12, 6, 16, 10))
            pygame.draw.polygon(image, (200,120,80), [(18,8),(20,2),(22,8)])  # перо
            # Копье
            pygame.draw.line(image, (180,170,160), (20, 20), (20, 44), 3)
            pygame.draw.polygon(image, (210,210,220), [(20,20),(18,16),(22,16)])  # наконечник
            pygame.draw.polygon(image, (90,70,55), [(20,44),(18,48),(22,48)])    # оперение
            # Борода
            pygame.draw.circle(image, (95,75,55), (20, 24), 4)
        elif unit == 'bearrider':
            # Гном-наездник на медведе — более мрачный лесной фон
            image.fill((45,60,90))
            # Медведь - тело
            pygame.draw.ellipse(image, (140,100,60), (8, 20, 24, 16))
            pygame.draw.ellipse(image, (120,80,40), (10, 22, 20, 12))  # тень тела
            # Медведь - голова
            pygame.draw.ellipse(image, (160,120,80), (20, 8, 12, 12))
            pygame.draw.ellipse(image, (140,100,60), (22, 10, 8, 8))  # тень головы
            # Уши медведя
            pygame.draw.circle(image, (120,80,40), (22, 10), 3)
            pygame.draw.circle(image, (120,80,40), (30, 10), 3)
            # Глаза медведя
            pygame.draw.circle(image, (60,40,20), (24, 14), 1)
            pygame.draw.circle(image, (60,40,20), (28, 14), 1)
            # Нос медведя
            pygame.draw.circle(image, (80,60,40), (26, 16), 1)
            # Гном-всадник
            pygame.draw.ellipse(image, (225,200,150), (20, 6, 8, 8))  # лицо гнома
            pygame.draw.circle(image, (50,35,18), (22, 8), 1)  # глаз
            pygame.draw.circle(image, (50,35,18), (26, 8), 1)  # глаз
            # Шлем гнома
            pygame.draw.ellipse(image, (120,100,80), (18, 4, 12, 8))
            # Борода гнома
            pygame.draw.circle(image, (95,75,55), (24, 12), 3)
            # Седельные сумки
            pygame.draw.rect(image, (100,80,60), (14, 28, 12, 10))
            pygame.draw.rect(image, (80,60,40), (16, 30, 8, 6))
        elif unit == 'runemage':
            # Рунический маг — более глубокие сине-стальные оттенки
            image.fill((40,80,140))
            # Магическая мантия
            pygame.draw.rect(image, (150,140,190), (14, 20, 12, 18))
            pygame.draw.rect(image, (115,105,165), (16, 22, 8, 14))
            # Лицо
            pygame.draw.ellipse(image, (225,200,150), (14, 8, 12, 12))
            pygame.draw.circle(image, (50,35,18), (18, 14), 1)
            pygame.draw.circle(image, (50,35,18), (22, 14), 1)
            # Магический колпак
            pygame.draw.polygon(image, (100,80,160), [(14,8),(20,2),(26,8)])
            pygame.draw.polygon(image, (80,60,140), [(16,8),(20,4),(24,8)])
            # Рунический посох
            pygame.draw.line(image, (130,115,95), (20, 32), (20, 44), 3)
            pygame.draw.circle(image, (190,175,245), (20, 32), 6)  # рунический кристалл
            pygame.draw.circle(image, (255,255,255), (20, 30), 2)  # свет кристалла
            # Руны на мантии
            pygame.draw.circle(image, (255,255,255), (16, 26), 1)
            pygame.draw.circle(image, (255,255,255), (24, 26), 1)
            pygame.draw.circle(image, (255,255,255), (20, 30), 1)
            # Борода
            pygame.draw.circle(image, (95,75,55), (20, 24), 4)
        elif unit == 'jarl':
            # Ярл — более тяжёлая, затемнённая королевская броня
            image.fill((50,80,120))
            # Королевская броня
            pygame.draw.rect(image, (170,155,135), (12, 16, 16, 18))
            pygame.draw.rect(image, (135,120,100), (14, 18, 12, 14))
            # Детали брони
            pygame.draw.line(image, (120,100,80), (14, 16), (26, 16), 2)
            pygame.draw.line(image, (120,100,80), (14, 20), (26, 20), 2)
            pygame.draw.line(image, (120,100,80), (14, 24), (26, 24), 2)
            pygame.draw.line(image, (120,100,80), (14, 28), (26, 28), 2)
            # Лицо
            pygame.draw.ellipse(image, (225,200,150), (12, 6, 16, 14))
            pygame.draw.ellipse(image, (195,170,135), (14, 8, 12, 10))
            # Глаза
            pygame.draw.circle(image, (60,40,20), (16, 12), 2)
            pygame.draw.circle(image, (60,40,20), (24, 12), 2)
            pygame.draw.circle(image, (255,255,255), (17, 11), 1)
            pygame.draw.circle(image, (255,255,255), (25, 11), 1)
            # Королевский шлем
            pygame.draw.polygon(image, (180,160,100), [(12,12),(16,4),(20,12),(24,4),(28,12)])
            pygame.draw.polygon(image, (140,120,80), [(14,10),(18,6),(22,10)])
            # Корона
            pygame.draw.polygon(image, (255,215,0), [(16,6),(18,2),(20,6),(22,2),(24,6)])
            # Детализированная борода
            pygame.draw.circle(image, (100,80,60), (20, 30), 8)
            pygame.draw.circle(image, (80,60,40), (20, 32), 6)
            # Королевские украшения
            pygame.draw.circle(image, (255,215,0), (16, 24), 2)
            pygame.draw.circle(image, (255,215,0), (24, 24), 2)
            pygame.draw.circle(image, (255,215,0), (20, 28), 2)
        # --- Новые юниты гномов ---
        elif unit == 'forgedragon':
            # Кузнечный дракон гномов — более глубокая каменно-металлическая палитра
            image.fill((70, 45, 35))
            # Каменное тело
            pygame.draw.ellipse(image, (110, 75, 55), (8, 20, 24, 14))
            # Металлические пластины/доспех
            for i in range(3):
                pygame.draw.rect(image, metal, (10 + i * 6, 22, 5, 10))
            # Голова
            pygame.draw.ellipse(image, (110, 75, 55), (22, 8, 14, 12))
            pygame.draw.circle(image, (255, 140, 60), (26, 12), 2)  # раскалённые глаза
            pygame.draw.circle(image, (255, 140, 60), (32, 12), 2)
            # Металлические рога
            pygame.draw.polygon(image, metal, [(24, 8), (22, 2), (26, 8)])
            pygame.draw.polygon(image, metal, [(34, 8), (36, 2), (32, 8)])
            # Хвост с молотом
            pygame.draw.line(image, (90, 55, 40), (10, 28), (4, 34), 3)
            pygame.draw.rect(image, metal, (2, 32, 4, 6))
        elif unit == 'mountainruler':
            image.fill((120, 100, 80))
            # Мощное тело
            pygame.draw.rect(image, metal, (10, 18, 20, 20))
            # Борода и лицо
            pygame.draw.ellipse(image, skin, (14, 12, 12, 10))
            pygame.draw.circle(image, (0,0,0), (18, 16), 1)
            pygame.draw.circle(image, (0,0,0), (22, 16), 1)
            # Длинная борода
            pygame.draw.ellipse(image, (140, 100, 60), (12, 20, 16, 14))
            # Корона
            pygame.draw.rect(image, gold, (14, 10, 12, 4))
            for i in range(3):
                pygame.draw.polygon(image, gold, [(16+i*3, 10), (17+i*3, 6), (18+i*3, 10)])
            # Королевский молот
            pygame.draw.line(image, (100, 80, 60), (28, 20), (28, 36), 4)
            pygame.draw.rect(image, metal, (24, 16, 8, 8))
            pygame.draw.circle(image, gold, (28, 20), 2)
        elif unit == 'volkhv':
            image.fill((100, 120, 140))
            # Роба с рунами
            pygame.draw.rect(image, (140, 160, 180), (10, 18, 20, 22))
            pygame.draw.ellipse(image, (140, 160, 180), (10, 10, 20, 12))  # Капюшон
            # Лицо с бородой
            pygame.draw.ellipse(image, skin, (14, 14, 12, 10))
            pygame.draw.circle(image, (0,0,0), (18, 18), 1)
            pygame.draw.circle(image, (0,0,0), (22, 18), 1)
            # Борода
            pygame.draw.ellipse(image, (180, 160, 140), (14, 22, 12, 10))
            # Руны на робе
            for i in range(3):
                pygame.draw.line(image, (100, 200, 255), (14, 26+i*4), (18, 26+i*4), 2)
                pygame.draw.line(image, (100, 200, 255), (22, 26+i*4), (26, 26+i*4), 2)
            # Рунический посох
            pygame.draw.line(image, (100, 80, 60), (28, 12), (28, 38), 3)
            for i in range(4):
                pygame.draw.circle(image, (100, 200, 255), (28, 14+i*6), 2)
    # --- Лига теней ---
    elif team == 'shadow':
        if unit == 'hero':
            # Основа - глубокие тени
            image.fill((20,0,40))
            # Мистический плащ с тенями
            pygame.draw.rect(image, (60,0,100), (8, 20, 24, 18))
            pygame.draw.rect(image, (40,0,80), (10, 22, 20, 14))  # внутренний плащ
            # Теневые складки
            pygame.draw.line(image, (30,0,60), (12, 20), (28, 20), 2)
            pygame.draw.line(image, (30,0,60), (12, 24), (28, 24), 2)
            pygame.draw.line(image, (30,0,60), (12, 28), (28, 28), 2)
            pygame.draw.line(image, (30,0,60), (12, 32), (28, 32), 2)
            # Лицо с мистическим свечением
            pygame.draw.ellipse(image, (180,160,200), (10, 8, 20, 18))
            pygame.draw.ellipse(image, (140,120,180), (12, 10, 16, 14))  # тень лица
            # Мистические глаза
            pygame.draw.circle(image, (200,0,200), (16, 16), 3)
            pygame.draw.circle(image, (200,0,200), (24, 16), 3)
            pygame.draw.circle(image, (255,255,255), (17, 15), 1)  # блик
            pygame.draw.circle(image, (255,255,255), (25, 15), 1)  # блик
            # Теневая маска/корона
            pygame.draw.polygon(image, (100,0,150), [(12,12),(16,4),(20,12),(24,4),(28,12)])
            pygame.draw.polygon(image, (80,0,120), [(14,10),(18,6),(22,10)])
            # Мистические рога
            pygame.draw.polygon(image, (60,0,100), [(14,10),(12,2),(16,6)])
            pygame.draw.polygon(image, (60,0,100), [(26,10),(28,2),(24,6)])
            # Теневая аура
            pygame.draw.circle(image, (40,0,80), (20, 30), 8)
            pygame.draw.circle(image, (20,0,60), (20, 32), 6)
            # Мистические украшения
            pygame.draw.circle(image, (200,0,200), (16, 26), 2)
            pygame.draw.circle(image, (200,0,200), (24, 26), 2)
            # Теневой пояс
            pygame.draw.rect(image, (40,0,80), (8, 28, 24, 10))
            pygame.draw.rect(image, (100,0,150), (18, 30, 4, 6))  # мистическая пряжка
        elif unit == 'scout':
            # Основа
            image.fill((40,0,60))
            # Теневой камуфляж
            pygame.draw.rect(image, (80,0,120), (14, 20, 12, 18))
            pygame.draw.rect(image, (60,0,100), (16, 22, 8, 14))
            # Лицо
            pygame.draw.ellipse(image, (180,160,200), (14, 8, 12, 12))
            pygame.draw.circle(image, (200,0,200), (18, 14), 1)  # мистический глаз
            pygame.draw.circle(image, (200,0,200), (22, 14), 1)  # мистический глаз
            # Теневой капюшон
            pygame.draw.ellipse(image, (60,0,100), (12, 6, 16, 10))
            pygame.draw.rect(image, (40,0,80), (14, 8, 12, 6))
            # Теневые перья
            pygame.draw.polygon(image, (100,0,150), [(18,8),(20,2),(22,8)])
            # Теневой кинжал
            pygame.draw.line(image, (120,0,180), (20, 20), (20, 44), 2)
            pygame.draw.polygon(image, (160,0,200), [(20,20),(18,16),(22,16)])  # лезвие
            pygame.draw.polygon(image, (80,0,120), [(20,44),(18,48),(22,48)])  # рукоять
            # Теневые следы
            pygame.draw.circle(image, (40,0,80), (20, 24), 3)
        elif unit == 'beast':
            # Основа
            image.fill((20,0,40))
            # Теневой зверь - тело
            pygame.draw.ellipse(image, (60,0,100), (8, 20, 24, 16))
            pygame.draw.ellipse(image, (40,0,80), (10, 22, 20, 12))  # тень тела
            # Теневой зверь - голова
            pygame.draw.ellipse(image, (80,0,120), (20, 8, 12, 12))
            pygame.draw.ellipse(image, (60,0,100), (22, 10, 8, 8))  # тень головы
            # Уши теневого зверя
            pygame.draw.circle(image, (40,0,80), (22, 10), 3)
            pygame.draw.circle(image, (40,0,80), (30, 10), 3)
            # Мистические глаза
            pygame.draw.circle(image, (200,0,200), (24, 14), 2)
            pygame.draw.circle(image, (200,0,200), (28, 14), 2)
            pygame.draw.circle(image, (255,255,255), (25, 13), 1)  # блик
            pygame.draw.circle(image, (255,255,255), (29, 13), 1)  # блик
            # Теневой нос
            pygame.draw.circle(image, (100,0,150), (26, 16), 1)
            # Теневые клыки
            pygame.draw.polygon(image, (160,0,200), [(24,18),(22,22),(26,22)])
            pygame.draw.polygon(image, (160,0,200), [(28,18),(26,22),(30,22)])
            # Теневые когти
            pygame.draw.polygon(image, (120,0,180), [(10,36),(8,40),(12,40)])
            pygame.draw.polygon(image, (120,0,180), [(28,36),(26,40),(30,40)])
        elif unit == 'minotaur':
            # Основа
            image.fill((40,0,80))
            # Теневой минотавр - тело
            pygame.draw.rect(image, (80,0,120), (12, 16, 16, 18))
            pygame.draw.rect(image, (60,0,100), (14, 18, 12, 14))
            # Детали теневой брони
            pygame.draw.line(image, (40,0,80), (14, 16), (26, 16), 2)
            pygame.draw.line(image, (40,0,80), (14, 20), (26, 20), 2)
            pygame.draw.line(image, (40,0,80), (14, 24), (26, 24), 2)
            pygame.draw.line(image, (40,0,80), (14, 28), (26, 28), 2)
            # Лицо минотавра
            pygame.draw.ellipse(image, (180,160,200), (12, 6, 16, 14))
            pygame.draw.ellipse(image, (140,120,180), (14, 8, 12, 10))
            # Мистические глаза
            pygame.draw.circle(image, (200,0,200), (16, 12), 2)
            pygame.draw.circle(image, (200,0,200), (24, 12), 2)
            pygame.draw.circle(image, (255,255,255), (17, 11), 1)
            pygame.draw.circle(image, (255,255,255), (25, 11), 1)
            # Теневые рога
            pygame.draw.polygon(image, (100,0,150), [(12,12),(16,4),(20,12),(24,4),(28,12)])
            pygame.draw.polygon(image, (80,0,120), [(14,10),(18,6),(22,10)])
            # Теневые рога минотавра
            pygame.draw.polygon(image, (60,0,100), [(14,10),(12,2),(16,6)])
            pygame.draw.polygon(image, (60,0,100), [(26,10),(28,2),(24,6)])
            # Теневая борода
            pygame.draw.circle(image, (60,0,100), (20, 30), 8)
            pygame.draw.circle(image, (40,0,80), (20, 32), 6)
            # Мистические украшения
            pygame.draw.circle(image, (200,0,200), (16, 24), 2)
            pygame.draw.circle(image, (200,0,200), (24, 24), 2)
        elif unit == 'witch':
            # Основа
            image.fill((60,0,80))
            # Теневая мантия ведьмы
            pygame.draw.rect(image, (100,0,150), (14, 20, 12, 18))
            pygame.draw.rect(image, (80,0,120), (16, 22, 8, 14))
            # Лицо ведьмы
            pygame.draw.ellipse(image, (180,160,200), (14, 8, 12, 12))
            pygame.draw.circle(image, (200,0,200), (18, 14), 1)  # мистический глаз
            pygame.draw.circle(image, (200,0,200), (22, 14), 1)  # мистический глаз
            # Теневой колпак ведьмы
            pygame.draw.polygon(image, (80,0,120), [(14,8),(20,2),(26,8)])
            pygame.draw.polygon(image, (60,0,100), [(16,8),(20,4),(24,8)])
            # Мистический посох
            pygame.draw.line(image, (120,0,180), (20, 32), (20, 44), 3)
            pygame.draw.circle(image, (200,0,200), (20, 32), 6)  # мистический кристалл
            pygame.draw.circle(image, (255,255,255), (20, 30), 2)  # свет кристалла
            # Теневые руны на мантии
            pygame.draw.circle(image, (200,0,200), (16, 26), 1)
            pygame.draw.circle(image, (200,0,200), (24, 26), 1)
            pygame.draw.circle(image, (200,0,200), (20, 30), 1)
            # Теневые волосы
            pygame.draw.circle(image, (60,0,100), (20, 24), 4)
        elif unit == 'lizardrider':
            # Основа
            image.fill((40,0,60))
            # Теневой ящер - тело
            pygame.draw.ellipse(image, (60,0,100), (8, 20, 24, 16))
            pygame.draw.ellipse(image, (40,0,80), (10, 22, 20, 12))  # тень тела
            # Теневой ящер - голова
            pygame.draw.ellipse(image, (80,0,120), (20, 8, 12, 12))
            pygame.draw.ellipse(image, (60,0,100), (22, 10, 8, 8))  # тень головы
            # Глаза ящера
            pygame.draw.circle(image, (200,0,200), (24, 14), 2)
            pygame.draw.circle(image, (200,0,200), (28, 14), 2)
            pygame.draw.circle(image, (255,255,255), (25, 13), 1)  # блик
            pygame.draw.circle(image, (255,255,255), (29, 13), 1)  # блик
            # Теневой всадник
            pygame.draw.ellipse(image, (180,160,200), (20, 6, 8, 8))  # лицо всадника
            pygame.draw.circle(image, (200,0,200), (22, 8), 1)  # мистический глаз
            pygame.draw.circle(image, (200,0,200), (26, 8), 1)  # мистический глаз
            # Теневой шлем всадника
            pygame.draw.ellipse(image, (60,0,100), (18, 4, 12, 8))
            # Теневые волосы всадника
            pygame.draw.circle(image, (60,0,100), (24, 12), 3)
            # Теневые седельные сумки
            pygame.draw.rect(image, (60,0,100), (14, 28, 12, 10))
            pygame.draw.rect(image, (40,0,80), (16, 30, 8, 6))
            # Теневые чешуи ящера
            for i in range(3):
                pygame.draw.circle(image, (80,0,120), (16 + i*4, 26), 1)
                pygame.draw.circle(image, (80,0,120), (16 + i*4, 30), 1)
        # --- Новые юниты теней ---
        elif unit == 'manticore':
            # Мантакора Лиги теней — более глубокий фиолетово-каменный тон
            image.fill((32, 20, 46))
            # Тело льва
            pygame.draw.ellipse(image, (105, 80, 65), (8, 20, 24, 14))
            # Лапы
            for i in range(4):
                pygame.draw.rect(image, (105, 80, 65), (10+i*6, 32, 4, 8))
            # Голова со злым лицом
            pygame.draw.ellipse(image, (105, 80, 65), (24, 10, 12, 10))
            pygame.draw.circle(image, (220, 40, 80), (28, 14), 2)
            pygame.draw.circle(image, (220, 40, 80), (32, 14), 2)
            # Крылья летучей мыши
            pygame.draw.polygon(image, (70, 50, 100), [(16, 18), (4, 12), (10, 22)])
            pygame.draw.polygon(image, (70, 50, 100), [(24, 18), (36, 12), (30, 22)])
            # Хвост скорпиона
            for i in range(3):
                pygame.draw.circle(image, (90, 70, 115), (6-i, 28+i*2), 2)
            pygame.draw.polygon(image, (150, 40, 150), [(4, 34), (2, 36), (6, 36)])  # Жало
        elif unit == 'reddragon':
            # Красный дракон Лиги теней — более тёмный, с магическим свечением глаз
            image.fill((60, 0, 0))
            # Тело дракона
            pygame.draw.ellipse(image, (170, 40, 40), (8, 20, 24, 14))
            # Чешуя
            for i in range(3):
                for j in range(2):
                    pygame.draw.circle(image, (135, 20, 25), (12+i*6, 24+j*4), 2)
            # Голова
            pygame.draw.ellipse(image, (170, 40, 40), (22, 8, 14, 12))
            pygame.draw.circle(image, (255, 220, 120), (26, 12), 2)
            pygame.draw.circle(image, (255, 220, 120), (32, 12), 2)
            # Рога
            pygame.draw.polygon(image, (220, 120, 40), [(24, 8), (22, 4), (26, 8)])
            pygame.draw.polygon(image, (220, 120, 40), [(34, 8), (36, 4), (32, 8)])
            # Крылья
            for i in range(3):
                pygame.draw.ellipse(image, (150, 50, 50), (2+i, 10+i*4, 12, 16))
                pygame.draw.ellipse(image, (150, 50, 50), (26+i, 10+i*4, 12, 16))
        elif unit == 'beholder':
            image.fill((60, 20, 80))
            # Центральный большой глаз
            pygame.draw.circle(image, (100, 60, 120), (20, 20), 12)
            pygame.draw.circle(image, (255, 255, 255), (20, 20), 10)
            pygame.draw.circle(image, (200, 0, 200), (20, 20), 6)
            pygame.draw.circle(image, (0, 0, 0), (20, 20), 3)
            pygame.draw.circle(image, (255, 255, 255), (18, 18), 1)  # Блик
            # Маленькие глаза на щупальцах вокруг
            positions = [(20, 8), (30, 12), (32, 22), (28, 32), (20, 34), (12, 32), (8, 22), (10, 12)]
            for i, (x, y) in enumerate(positions):
                # Щупальце
                pygame.draw.line(image, (80, 40, 100), (20, 20), (x, y), 2)
                # Глаз
                pygame.draw.circle(image, (150, 100, 180), (x, y), 3)
                pygame.draw.circle(image, (0, 0, 0), (x, y), 1)
    
    # ==================== НОВЫЕ ЮНИТЫ ====================
    # --- Новые юниты людей ---
    elif unit == 'monk':
        # Монах — более спокойная, приглушённая палитра, чтобы не выбиваться из новых людей
        image.fill((170, 150, 120))
        # Роба
        pygame.draw.rect(image, (135, 110, 80), (10, 18, 20, 22))
        pygame.draw.ellipse(image, (135, 110, 80), (10, 10, 20, 12))  # Капюшон
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 14, 12, 10))
        pygame.draw.circle(image, (40,30,20), (18, 18), 1)
        pygame.draw.circle(image, (40,30,20), (22, 18), 1)
        # Крест
        pygame.draw.rect(image, gold, (19, 24, 2, 8))
        pygame.draw.rect(image, gold, (16, 26, 8, 2))
        # Руки сложены в молитве
        pygame.draw.ellipse(image, skin, (16, 28, 8, 6))
    
    elif unit == 'angel':
        # Ангел — более мягкая холодная палитра, чтобы не выбиваться на фоне новых людей и нежити
        # Упрощённый спрайт ангела для иконок (боевые кадры берутся из load_angel_texture)
        image.fill((220, 230, 250))
        pygame.draw.rect(image, (205, 210, 235), (12, 18, 16, 18))
        pygame.draw.ellipse(image, skin, (14, 10, 12, 10))
        pygame.draw.ellipse(image, (245, 215, 155), (12, 8, 16, 8))
        for i in range(2):
            pygame.draw.ellipse(image, (250, 250, 255), (4+i*2, 18+i*4, 8, 12))
            pygame.draw.ellipse(image, (250, 250, 255), (28-i*2, 18+i*4, 8, 12))
    
    elif unit == 'cavalryman':
        # Упрощённый спрайт кавалериста для иконок (боевые кадры берутся из load_cavalryman_texture)
        image.fill((150, 125, 95))
        pygame.draw.ellipse(image, (140, 100, 60), (6, 22, 28, 14))
        pygame.draw.ellipse(image, (140, 100, 60), (26, 12, 10, 10))
        pygame.draw.rect(image, metal, (14, 12, 12, 12))
    
    # --- Новые юниты нежити ---
    elif unit == 'deathknight':
        image.fill((40, 40, 60))
        # Чёрные доспехи
        pygame.draw.rect(image, (60, 60, 80), (10, 16, 20, 22))
        # Шлем
        pygame.draw.ellipse(image, (60, 60, 80), (10, 8, 20, 14))
        # Глаза - светящиеся красные
        pygame.draw.circle(image, (255, 0, 0), (16, 14), 2)
        pygame.draw.circle(image, (255, 0, 0), (24, 14), 2)
        # Тёмный меч
        pygame.draw.rect(image, (40, 40, 60), (28, 22, 6, 16))
        pygame.draw.rect(image, (80, 0, 0), (26, 20, 10, 4))
        # Щит с черепом
        pygame.draw.ellipse(image, (60, 60, 80), (2, 22, 12, 18))
        pygame.draw.circle(image, (200, 200, 200), (8, 28), 3)
    
    elif unit == 'bonedragon':
        # Костяной дракон — более мрачный, с холодной палитрой костей
        image.fill((30, 30, 50))
        # Тело
        pygame.draw.ellipse(image, (210, 215, 225), (8, 20, 24, 14))
        # Рёбра
        for i in range(4):
            pygame.draw.arc(image, (175, 180, 190), (10 + i * 4, 22, 8, 8), 0, 3.14, 2)
        # Голова
        pygame.draw.ellipse(image, (210, 215, 225), (22, 8, 14, 12))
        pygame.draw.circle(image, (255, 60, 80), (26, 12), 2)  # красно-розовое свечение глаз
        pygame.draw.circle(image, (255, 60, 80), (32, 12), 2)
        # Зубы
        for i in range(3):
            pygame.draw.polygon(image, (235, 235, 240), [(24 + i * 3, 18), (25 + i * 3, 20), (26 + i * 3, 18)])
        # Костяные крылья
        for i in range(2):
            pygame.draw.line(image, (180, 185, 195), (16, 16), (4 + i * 4, 8 + i * 6), 2)
            pygame.draw.line(image, (180, 185, 195), (24, 16), (32 + i * 4, 8 + i * 6), 2)
    
    elif unit == 'reaper':
        image.fill((20, 20, 40))
        # Чёрная роба
        pygame.draw.ellipse(image, (40, 40, 60), (8, 12, 24, 26))
        # Капюшон
        pygame.draw.ellipse(image, (40, 40, 60), (12, 6, 16, 14))
        # Темнота под капюшоном
        pygame.draw.ellipse(image, (0, 0, 0), (14, 10, 12, 8))
        # Красные глаза
        pygame.draw.circle(image, (255, 0, 0), (18, 14), 2)
        pygame.draw.circle(image, (255, 0, 0), (22, 14), 2)
        # Коса
        pygame.draw.line(image, (160, 160, 160), (28, 14), (28, 36), 3)
        pygame.draw.arc(image, (160, 160, 160), (20, 8, 16, 12), 0, 3.14, 3)
    
    # --- Новые юниты эльфов ---
    elif unit == 'greendragon':
        # Упрощённый спрайт зелёного дракона (боевые кадры берутся из load_greendragon_texture)
        image.fill((24, 80, 40))
        pygame.draw.ellipse(image, (60, 150, 80), (8, 20, 24, 14))
        pygame.draw.ellipse(image, (60, 150, 80), (22, 8, 14, 12))
    
    elif unit == 'druid':
        image.fill((80, 120, 60))
        # Зелёная роба
        pygame.draw.rect(image, (100, 160, 80), (10, 18, 20, 22))
        pygame.draw.ellipse(image, (100, 160, 80), (10, 10, 20, 12))  # Капюшон
        # Лицо
        pygame.draw.ellipse(image, skin, (14, 14, 12, 10))
        pygame.draw.circle(image, (0,0,0), (18, 18), 1)
        pygame.draw.circle(image, (0,0,0), (22, 18), 1)
        # Длинные уши эльфа
        pygame.draw.polygon(image, skin, [(13, 16), (10, 14), (14, 14)])
        pygame.draw.polygon(image, skin, [(27, 16), (30, 14), (26, 14)])
        # Посох с листьями
        pygame.draw.line(image, (120, 80, 40), (28, 12), (28, 38), 3)
        pygame.draw.circle(image, (100, 200, 100), (28, 10), 3)
        for i in range(3):
            pygame.draw.ellipse(image, (120, 220, 120), (26+i*2, 8+i, 4, 6))
    
    elif unit == 'unicorn':
        image.fill((200, 200, 240))
        # Белое тело
        pygame.draw.ellipse(image, (240, 240, 255), (8, 20, 24, 16))
        # Ноги
        pygame.draw.rect(image, (240, 240, 255), (10, 34, 4, 8))
        pygame.draw.rect(image, (240, 240, 255), (18, 34, 4, 8))
        pygame.draw.rect(image, (240, 240, 255), (26, 34, 4, 8))
        # Голова
        pygame.draw.ellipse(image, (240, 240, 255), (24, 10, 12, 12))
        pygame.draw.circle(image, (0, 100, 200), (28, 14), 2)  # Голубой глаз
        # Рог
        pygame.draw.polygon(image, gold, [(28, 8), (30, 2), (32, 8)])
        # Грива
        for i in range(3):
            pygame.draw.ellipse(image, (255, 200, 255), (20-i*2, 10+i*2, 8, 10))
    
    # --- Новые юниты демонов ---
    elif unit == 'bloodpriestess':
        image.fill((80, 0, 40))
        # Красная роба
        pygame.draw.rect(image, (140, 0, 60), (10, 18, 20, 22))
        # Плечи
        pygame.draw.ellipse(image, (140, 0, 60), (8, 16, 10, 8))
        pygame.draw.ellipse(image, (140, 0, 60), (22, 16, 10, 8))
        # Голова
        pygame.draw.ellipse(image, (200, 150, 150), (14, 10, 12, 10))
        pygame.draw.circle(image, (255, 0, 0), (18, 14), 1)  # Красные глаза
        pygame.draw.circle(image, (255, 0, 0), (22, 14), 1)
        # Рога
        pygame.draw.arc(image, (80, 0, 0), (12, 8, 6, 8), 0, 3.14, 2)
        pygame.draw.arc(image, (80, 0, 0), (22, 8, 6, 8), 0, 3.14, 2)
        # Посох с кровавым кристаллом
        pygame.draw.line(image, (80, 40, 40), (28, 14), (28, 38), 3)
        pygame.draw.circle(image, (200, 0, 0), (28, 12), 3)
    
    elif unit == 'devil':
        image.fill((100, 0, 0))
        # Мощное тело
        pygame.draw.rect(image, (160, 0, 0), (10, 16, 20, 24))
        # Мускулы
        pygame.draw.ellipse(image, (180, 20, 20), (8, 18, 10, 12))
        pygame.draw.ellipse(image, (180, 20, 20), (22, 18, 10, 12))
        # Голова
        pygame.draw.ellipse(image, (160, 0, 0), (12, 8, 16, 12))
        pygame.draw.circle(image, (255, 100, 0), (17, 12), 2)  # Огненные глаза
        pygame.draw.circle(image, (255, 100, 0), (23, 12), 2)
        # Большие рога
        pygame.draw.arc(image, (80, 0, 0), (10, 6, 8, 10), 0, 3.14, 3)
        pygame.draw.arc(image, (80, 0, 0), (22, 6, 8, 10), 0, 3.14, 3)
        # Крылья кожистые
        for i in range(2):
            pygame.draw.polygon(image, (80, 0, 0), [(16, 20), (4+i*4, 16+i*8), (10+i*2, 24+i*4)])
            pygame.draw.polygon(image, (80, 0, 0), [(24, 20), (32+i*4, 16+i*8), (28+i*2, 24+i*4)])
        # Трезубец
        pygame.draw.line(image, (120, 120, 120), (30, 12), (30, 36), 3)
        pygame.draw.line(image, (120, 120, 120), (26, 10), (30, 14), 2)
        pygame.draw.line(image, (120, 120, 120), (30, 10), (30, 14), 2)
        pygame.draw.line(image, (120, 120, 120), (34, 10), (30, 14), 2)
    
    elif unit == 'hellhorse':
        image.fill((80, 20, 0))
        # Огненное тело коня
        pygame.draw.ellipse(image, (160, 40, 0), (6, 22, 28, 14))
        # Ноги в огне
        for i in range(4):
            pygame.draw.rect(image, (200, 60, 0), (8+i*6, 34, 4, 8))
            # Пламя от копыт
            pygame.draw.circle(image, (255, 100, 0), (10+i*6, 40), 2)
        # Голова в огне
        pygame.draw.ellipse(image, (160, 40, 0), (26, 12, 10, 10))
        pygame.draw.circle(image, (255, 0, 0), (30, 16), 2)  # Красный глаз
        # Огненная грива
        for i in range(4):
            pygame.draw.circle(image, (255, 100, 0), (20+i*2, 14+i), 3)
        # Огненный хвост
        for i in range(3):
            pygame.draw.circle(image, (255, 80, 0), (8-i, 28+i*2), 2)
    
    
    # ==================== КОНЕЦ НОВЫХ ЮНИТОВ ====================
    return pygame.transform.scale(image, (int(CELL_SIZE * scale), int(CELL_SIZE * scale)))

def draw_cell_texture(surface, x, y, size):
    # Градиентный фон с небольшим шумом по клеткам
    for i in range(size):
        rel_x = (x + i) / SCREEN_WIDTH
        color1 = (44, 140, 60)
        color2 = (52, 155, 70)
        r = int(color1[0] * (1-rel_x) + color2[0] * rel_x)
        g = int(color1[1] * (1-rel_x) + color2[1] * rel_x)
        b = int(color1[2] * (1-rel_x) + color2[2] * rel_x)
        # Добавляем небольшой шум для каждой клетки
        noise = random.randint(-8, 8)
        r = max(0, min(255, r + noise))
        g = max(0, min(255, g + noise))
        b = max(0, min(255, b + noise))
        pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + size - 1))
    # Мягкие полутона
    if random.random() < 0.1:
        gx = x + random.randint(0, size-10)
        gy = y + random.randint(0, size-10)
        gr = random.randint(10, 18)
        color = (60, 170, 80)
        alpha = random.randint(30, 50)
        ellipse = pygame.Surface((gr, gr//2), pygame.SRCALPHA)
        ellipse.fill((0,0,0,0))
        pygame.draw.ellipse(ellipse, color + (alpha,), (0, 0, gr, gr//2))
        surface.blit(ellipse, (gx, gy))

# Кэш для анимированной травы
_grass_cache = {}
_grass_cache_time = 0
_grass_update_interval = 0.0125  # Обновляем каждые 0.0125 секунды для максимальной плавности (80 FPS анимация)
_grass_base_cache = {}  # Базовый кэш без анимации (создается один раз)
_grass_initialized = False

def _init_grass_base_cache():
    """Инициализирует базовый кэш травы (выполняется один раз)"""
    global _grass_base_cache, _grass_initialized
    if _grass_initialized:
        return
    
    # Используем numpy для быстрой генерации базовых травинок если доступен
    try:
        import numpy as np
        use_numpy = True
    except ImportError:
        use_numpy = False
    
    random.seed(42)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            cell_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            # Качественная анимация: 16 травинок на клетку для максимального качества
            grass_data = []
            for i in range(16):  # Увеличено до 16 травинок для максимальной детализации
                base_x = random.randint(4, CELL_SIZE-4)
                base_y = random.randint(CELL_SIZE//2, CELL_SIZE-4)
                length = random.randint(10, 18)
                base_color = (60, 170, 80)
                color = tuple(max(0, min(255, c + random.randint(-10, 10))) for c in base_color)
                phase = (x + y + i) * 0.2
                grass_data.append({
                    'base_x': base_x,
                    'base_y': base_y,
                    'length': length,
                    'color': color,
                    'phase': phase
                })
            _grass_base_cache[(x, y)] = grass_data
            # Рисуем начальное состояние
            for grass in grass_data:
                pygame.draw.line(cell_surface, grass['color'], 
                               (grass['base_x'], grass['base_y']), 
                               (grass['base_x'], grass['base_y'] - grass['length']), 1)
    random.seed()
    _grass_initialized = True

def draw_animated_grass(surface, t):
    global _grass_cache, _grass_cache_time
    
    # Инициализируем базовый кэш один раз
    _init_grass_base_cache()
    
    # Оптимизация: используем более частое обновление кэша для плавной анимации
    current_time = int(t / _grass_update_interval)
    
    # Обновляем кэш анимации только если нужно
    if current_time != _grass_cache_time or not _grass_cache:
        _grass_cache_time = current_time
        _grass_cache.clear()
        
        # Создаем анимированные поверхности из базового кэша
        for (x, y), grass_data in _grass_base_cache.items():
            cell_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            # Рисуем каждую травинку с анимацией
            for grass in grass_data:
                phase = grass['phase']
                sway = math.sin(t * 2.0 + phase) * 5
                tip_x = grass['base_x'] + int(sway)
                tip_y = grass['base_y'] - grass['length']
                pygame.draw.line(cell_surface, grass['color'], 
                               (grass['base_x'], grass['base_y']), 
                               (tip_x, tip_y), 1)
            _grass_cache[(x, y)] = cell_surface
    
    # Быстрое blit всех кэшированных поверхностей
    for (x, y), cached_surface in _grass_cache.items():
        surface.blit(cached_surface, (x * CELL_SIZE, y * CELL_SIZE))

def _draw_rotated_arrow(screen, x, y, angle, style='normal'):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    # Геометрия стрелы
    shaft_len = 16
    head_len = 8
    half_thick = 2
    # Точка основания древка
    bx = x - shaft_len * cos_a
    by = y - shaft_len * sin_a
    # Оси
    px = -sin_a
    py = cos_a
    # Цвета
    shaft_color = (160, 120, 60) if style == 'normal' else (200, 120, 40)
    head_outer = (200,200,200) if style == 'normal' else (255, 180, 60)
    fletch_color = (80,80,200) if style == 'normal' else (255, 120, 40)
    # Древко (как толстая линия двумя параллелями)
    pygame.draw.line(screen, shaft_color,
                     (bx + half_thick*px, by + half_thick*py),
                     (x + half_thick*px,  y + half_thick*py), 2)
    pygame.draw.line(screen, shaft_color,
                     (bx - half_thick*px, by - half_thick*py),
                     (x - half_thick*px,  y - half_thick*py), 2)
    # Наконечник (треугольник)
    tip = (x, y)
    left = (x - head_len*cos_a + 4*px, y - head_len*sin_a + 4*py)
    right = (x - head_len*cos_a - 4*px, y - head_len*sin_a - 4*py)
    pygame.draw.polygon(screen, head_outer, [tip, left, right])
    # Оперение
    tail = (bx, by)
    f1 = (bx - 6*cos_a + 3*px, by - 6*sin_a + 3*py)
    f2 = (bx - 6*cos_a - 3*px, by - 6*sin_a - 3*py)
    pygame.draw.polygon(screen, fletch_color, [tail, f1, f2])
    # Пламя для огненной стрелы
    if style == 'fire':
        flame1 = (x + 4*cos_a, y + 4*sin_a)
        flame2 = (x + 10*cos_a + 2*px, y + 10*sin_a + 2*py)
        flame3 = (x + 10*cos_a - 2*px, y + 10*sin_a - 2*py)
        pygame.draw.polygon(screen, (255, 80, 20), [flame1, flame2, flame3])
        inner2 = (x + 8*cos_a + 1*px, y + 8*sin_a + 1*py)
        inner3 = (x + 8*cos_a - 1*px, y + 8*sin_a - 1*py)
        pygame.draw.polygon(screen, (255, 200, 80), [flame1, inner2, inner3])

def animate_arrow(screen, start, end, redraw_callback=None, style='normal'):
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 40  # Пикселей за кадр - повышенная скорость
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    angle = math.atan2(dy, dx)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    x, y = float(start[0]), float(start[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Двигаем снаряд с фиксированной скоростью
        x += step_x
        y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == frames - 1 or (abs(x - end[0]) < abs(step_x) and abs(y - end[1]) < abs(step_y)):
            x, y = end[0], end[1]
        
        _draw_rotated_arrow(screen, int(x), int(y), angle, style=style)
        pygame.display.flip()
        pygame.time.delay(5)  # Минимальная задержка для максимальной скорости

def animate_arrow_fly(screen, start, end, redraw_callback=None):
    return animate_arrow(screen, start, end, redraw_callback=redraw_callback, style='normal')

def animate_fire_arrow_fly(screen, start, end, redraw_callback=None):
    """Улучшенная анимация полета огненной стрелы с детальными эффектами"""
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 48  # Повышенная скорость для огненной стрелы
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    angle = math.atan2(dy, dx)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    x, y = float(start[0]), float(start[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Двигаем снаряд с фиксированной скоростью
        x += step_x
        y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == frames - 1 or (abs(x - end[0]) < abs(step_x) and abs(y - end[1]) < abs(step_y)):
            x, y = end[0], end[1]
        
        # Создаем слой эффектов
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Длинный огненный шлейф за стрелой
        trail_length = 50
        for j in range(40):  # Увеличено с 20 до 40 для более плавного шлейфа
            trail_t = j / 40.0  # Исправлено деление для правильного расчета
            trail_x = x - int(trail_length * trail_t * math.cos(angle))
            trail_y = y - int(trail_length * trail_t * math.sin(angle))
            trail_r = max(2, int(8 * (1 - trail_t * 0.85)))
            
            # Градиент от яркого оранжевого к темному красному
            if trail_t < 0.3:
                color = (255, 200, 80, int(220 * (1 - trail_t)))
            elif trail_t < 0.6:
                color = (255, 140, 40, int(200 * (1 - trail_t)))
            else:
                color = (220, 80, 30, int(160 * (1 - trail_t)))
            
            pygame.draw.circle(overlay, color, (trail_x, trail_y), trail_r)
            
            # Огненные искры по бокам шлейфа
            if j % 3 == 0:
                for side in [-1, 1]:
                    spark_x = trail_x + int(8 * math.cos(angle + math.pi/2 * side))
                    spark_y = trail_y + int(8 * math.sin(angle + math.pi/2 * side))
                    pygame.draw.circle(overlay, (255, 220, 100, int(180 * (1 - trail_t))), 
                                     (spark_x, spark_y), max(1, 3 - int(trail_t * 2)))
        
        # Сама стрела (древко и наконечник)
        arrow_len = 20
        tail_x = x - int(arrow_len * math.cos(angle))
        tail_y = y - int(arrow_len * math.sin(angle))
        
        # Древко (деревянное с огнём)
        pygame.draw.line(overlay, (140, 100, 60), (tail_x, tail_y), (x, y), 4)
        pygame.draw.line(overlay, (200, 150, 80), (tail_x, tail_y), (x, y), 2)
        
        # Огненный наконечник
        tip_len = 8
        tip_x = x + int(tip_len * math.cos(angle))
        tip_y = y + int(tip_len * math.sin(angle))
        
        # Металлический наконечник с огненным свечением
        pygame.draw.line(overlay, (255, 180, 60), (x, y), (tip_x, tip_y), 5)
        pygame.draw.line(overlay, (255, 220, 120), (x, y), (tip_x, tip_y), 3)
        
        # Пульсирующее огненное свечение вокруг стрелы
        glow_r = int(12 + 4 * math.sin(i * 0.8))
        pygame.draw.circle(overlay, (255, 120, 40, 80), (x, y), glow_r)
        pygame.draw.circle(overlay, (255, 200, 100, 60), (x, y), int(glow_r * 1.3))
        
        # Летящие искры впереди стрелы
        for k in range(12):  # Увеличено с 5 до 12 искр
            spark_angle = angle + (random.random() - 0.5) * 0.5
            spark_dist = 10 + random.randint(0, 15)
            spark_x = x + int(spark_dist * math.cos(spark_angle))
            spark_y = y + int(spark_dist * math.sin(spark_angle))
            pygame.draw.circle(overlay, (255, 200, 80, 200), (spark_x, spark_y), 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)  # Минимальная задержка для максимальной скорости

def animate_ice_arrow(screen, start, end, redraw_callback=None):
    """Анимация полета ледяной стрелы с ледяными эффектами"""
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 44  # Повышенная скорость для ледяной стрелы
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    angle = math.atan2(dy, dx)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    x, y = float(start[0]), float(start[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Двигаем снаряд с фиксированной скоростью
        x += step_x
        y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == frames - 1 or (abs(x - end[0]) < abs(step_x) and abs(y - end[1]) < abs(step_y)):
            x, y = end[0], end[1]
        
        t = i / max(1, frames - 1)  # Для анимации эффектов
        
        # Создаем слой эффектов
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Ледяной шлейф за стрелой
        trail_length = 40
        for j in range(30):  # Увеличено с 15 до 30 для более плавного шлейфа
            trail_t = j / 30.0  # Исправлено деление для правильного расчета
            trail_x = x - int(trail_length * trail_t * math.cos(angle))
            trail_y = y - int(trail_length * trail_t * math.sin(angle))
            trail_r = max(2, int(6 * (1 - trail_t * 0.8)))
            
            # Градиент от яркого голубого к белому
            if trail_t < 0.4:
                color = (200, 240, 255, int(200 * (1 - trail_t)))
            elif trail_t < 0.7:
                color = (180, 220, 255, int(180 * (1 - trail_t)))
            else:
                color = (150, 200, 255, int(140 * (1 - trail_t)))
            
            pygame.draw.circle(overlay, color, (trail_x, trail_y), trail_r)
        
        # Ледяные кристаллы вокруг стрелы
        for k in range(12):  # Увеличено с 6 до 12 кристаллов
            crystal_angle = angle + (k * math.pi / 3) + (i * 0.1)
            crystal_dist = 8 + random.randint(-2, 2)
            crystal_x = x + int(crystal_dist * math.cos(crystal_angle))
            crystal_y = y + int(crystal_dist * math.sin(crystal_angle))
            crystal_size = 2 + random.randint(0, 1)
            pygame.draw.circle(overlay, (220, 240, 255, 180), (crystal_x, crystal_y), crystal_size)
        
        # Сама стрела
        arrow_len = 18
        tail_x = x - int(arrow_len * math.cos(angle))
        tail_y = y - int(arrow_len * math.sin(angle))
        
        # Древко (деревянное)
        pygame.draw.line(overlay, (120, 80, 50), (tail_x, tail_y), (x, y), 3)
        pygame.draw.line(overlay, (160, 120, 70), (tail_x, tail_y), (x, y), 2)
        
        # Ледяной наконечник
        tip_len = 7
        tip_x = x + int(tip_len * math.cos(angle))
        tip_y = y + int(tip_len * math.sin(angle))
        
        # Ледяной наконечник с градиентом
        pygame.draw.line(overlay, (180, 220, 255), (x, y), (tip_x, tip_y), 4)
        pygame.draw.line(overlay, (220, 240, 255), (x, y), (tip_x, tip_y), 2)
        
        # Ледяное свечение вокруг наконечника
        glow_r = int(8 + 2 * math.sin(i * 0.7))
        pygame.draw.circle(overlay, (180, 220, 255, 100), (x, y), glow_r)
        pygame.draw.circle(overlay, (220, 240, 255, 60), (x, y), int(glow_r * 1.2))
        
        # Ледяные частицы перед стрелой
        for m in range(3):
            particle_angle = angle + (random.random() - 0.5) * 0.4
            particle_dist = 12 + random.randint(0, 10)
            particle_x = x + int(particle_dist * math.cos(particle_angle))
            particle_y = y + int(particle_dist * math.sin(particle_angle))
            pygame.draw.circle(overlay, (240, 250, 255, 180), (particle_x, particle_y), 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний

def animate_magic_projectile(screen, start, end, color=(120,40,180)):
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 40  # Повышенная скорость
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    x, y = float(start[0]), float(start[1])
    
    for i in range(frames):
        pygame.event.pump()
        
        # Двигаем снаряд с фиксированной скоростью
        x += step_x
        y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == frames - 1 or (abs(x - end[0]) < abs(step_x) and abs(y - end[1]) < abs(step_y)):
            x, y = end[0], end[1]
        
        # Перерисовываем поле перед каждым кадром
        # Рисуем только магический шар (без следа)
        pygame.draw.circle(screen, color, (int(x), int(y)), 12)
        pygame.draw.circle(screen, (200,200,255), (int(x), int(y)), 6)
        pygame.display.flip()
        pygame.time.delay(5)  # Минимальная задержка для максимальной скорости

def animate_magic_fly(screen, start, end, color=(120,40,180), redraw_callback=None):
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 40  # Повышенная скорость
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    x, y = float(start[0]), float(start[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Двигаем снаряд с фиксированной скоростью
        x += step_x
        y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == frames - 1 or (abs(x - end[0]) < abs(step_x) and abs(y - end[1]) < abs(step_y)):
            x, y = end[0], end[1]
        
        pygame.draw.circle(screen, color, (int(x), int(y)), 12)
        pygame.draw.circle(screen, (220,220,255), (int(x), int(y)), 6)
        pygame.display.flip()
        pygame.time.delay(5)  # Минимальная задержка для максимальной скорости

def animate_stone_skin(screen, target_px, redraw_callback=None):
    # Анимация каменной корки: наложение серых колец и трещин, затем осыпание
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = target_px
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        r = int(CELL_SIZE * (0.6 + 0.4 * i / frames))
        alpha = 180 if i < frames - 4 else max(0, 180 - (i - (frames - 4)) * 45)
        pygame.draw.circle(overlay, (120, 120, 120, alpha), (cx, cy), r, 0)
        # Трещины
        for k in range(6):
            ang = (k * math.pi / 3.0) + (i * 0.1)
            x2 = cx + int(r * math.cos(ang))
            y2 = cy + int(r * math.sin(ang))
            pygame.draw.aaline(overlay, (80, 80, 80, alpha), (cx, cy), (x2, y2))
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний

def animate_curse_voodoo(screen, target_px, redraw_callback=None):
    """Улучшенная анимация проклятия с темной магией и вороньими перьями"""
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = target_px
    
    # Массив перьев, которые падают на юнит
    feathers = []
    for _ in range(60):  # Увеличено до 60 перьев для максимальной насыщенности
        # Позиция начала падения (над юнитом)
        start_x = cx + (random.random() - 0.5) * 80
        start_y = cy - CELL_SIZE - random.random() * 60
        # Скорость падения
        vel_x = (random.random() - 0.5) * 2.5
        vel_y = random.random() * 2.0 + 1.0
        # Размер и угол поворота
        size = random.random() * 5 + 3
        angle = random.random() * 2 * math.pi
        rotation_speed = (random.random() - 0.5) * 0.3
        feathers.append({
            'x': start_x,
            'y': start_y,
            'vel_x': vel_x,
            'vel_y': vel_y,
            'size': size,
            'angle': angle,
            'rotation_speed': rotation_speed,
            'alpha': 230
        })
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1)
        
        # Темная магическая аура вокруг цели
        aura_alpha = int(140 * math.sin(t * math.pi))
        for aura_ring in range(3):
            aura_r = int(25 + aura_ring * 12 + 10 * math.sin(i * 0.3 + aura_ring))
            pygame.draw.circle(overlay, (80, 0, 80, aura_alpha // (aura_ring + 1)), 
                             (cx, cy), aura_r, 3)
        
        # Темные энергетические спирали
        for spiral in range(8):
            spiral_angle = (spiral * 2 * math.pi / 8) + t * 3
            spiral_r = int(30 + 15 * t)
            spiral_x = cx + int(spiral_r * math.cos(spiral_angle))
            spiral_y = cy + int(spiral_r * math.sin(spiral_angle))
            spiral_alpha = int(180 * (1 - t * 0.7))
            
            # Темная частица
            pygame.draw.circle(overlay, (120, 0, 120, spiral_alpha), (spiral_x, spiral_y), 3)
            pygame.draw.circle(overlay, (180, 0, 180, spiral_alpha), (spiral_x, spiral_y), 2)
            
            # След за спиралью
            trail_r = spiral_r - 8
            trail_x = cx + int(trail_r * math.cos(spiral_angle))
            trail_y = cy + int(trail_r * math.sin(spiral_angle))
            pygame.draw.line(overlay, (100, 0, 100, spiral_alpha // 2), 
                           (trail_x, trail_y), (spiral_x, spiral_y), 2)
        
        # Обновляем позиции перьев
        for feather in feathers:
            feather['x'] += feather['vel_x']
            feather['y'] += feather['vel_y']
            feather['angle'] += feather['rotation_speed']  # Вращение
            # Замедление по мере падения
            if feather['y'] > cy - CELL_SIZE//2:
                feather['vel_y'] *= 0.93
                feather['alpha'] = max(60, feather['alpha'] - 8)
            else:
                feather['alpha'] = min(230, feather['alpha'] + 8)
        
        # Рисуем перья
        for feather in feathers:
            if feather['y'] < cy + CELL_SIZE//2 and feather['alpha'] > 0:
                # Воронье перо (тёмное, с контуром)
                px, py = int(feather['x']), int(feather['y'])
                alpha = int(feather['alpha'])
                size = feather['size']
                angle = feather['angle']
                
                # Основное тело пера (овальное)
                cos_a = math.cos(angle)
                sin_a = math.sin(angle)
                # Центральная часть
                for offset in range(-int(size), int(size) + 1):
                    ox = offset * cos_a
                    oy = offset * sin_a * 0.3
                    pygame.draw.circle(overlay, (20, 20, 20, alpha), 
                                     (px + int(ox), py + int(oy)), max(1, int(size * 0.5)))
                
                # Ость пера (центральная линия)
                pygame.draw.line(overlay, (40, 40, 40, alpha),
                               (px - int(size * cos_a), py - int(size * sin_a)),
                               (px + int(size * cos_a), py + int(size * sin_a)), 2)
                
                # Барбики (ветвистые части)
                for side in [-1, 1]:
                    for barb in range(3):
                        barb_offset = (barb + 0.5) * size / 2
                        barb_x = px + int(barb_offset * cos_a * side)
                        barb_y = py + int(barb_offset * sin_a * side)
                        barb_length = size * 0.4
                        barb_angle = angle + side * math.pi / 3
                        pygame.draw.line(overlay, (30, 30, 30, alpha),
                                       (barb_x, barb_y),
                                       (barb_x + int(barb_length * math.cos(barb_angle)),
                                        barb_y + int(barb_length * math.sin(barb_angle))), 1)
        
        # Темное свечение от центра проклятия
        glow_alpha = int(100 * math.sin(t * math.pi))
        for glow_layer in range(4):
            glow_r = int(20 + glow_layer * 8)
            pygame.draw.circle(overlay, (60, 0, 60, glow_alpha // (glow_layer + 1)), 
                             (cx, cy), glow_r)
        
        # Искры проклятия разлетаются
        if t > 0.3:
            spark_t = (t - 0.3) / 0.7
            for k in range(12):
                spark_angle = k * (2 * math.pi / 12) + spark_t * 0.5
                spark_dist = int(10 + 30 * spark_t)
                spark_x = cx + int(spark_dist * math.cos(spark_angle))
                spark_y = cy + int(spark_dist * math.sin(spark_angle))
                spark_alpha = int(200 * (1 - spark_t))
                
                pygame.draw.circle(overlay, (150, 0, 150, spark_alpha), (spark_x, spark_y), 3)
                pygame.draw.circle(overlay, (200, 50, 200, spark_alpha), (spark_x, spark_y), 2)
        
        # Дополнительные перья, которые появляются сверху
        if i < 15 and i % 2 == 0:
            new_x = cx + (random.random() - 0.5) * 60
            new_y = cy - CELL_SIZE - 25 - random.random() * 40
            # Рисуем одно новое перо
            alpha = 200
            size = random.random() * 4 + 3
            angle = random.random() * 2 * math.pi
            px, py = int(new_x), int(new_y)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            for offset in range(-int(size), int(size) + 1):
                ox = offset * cos_a
                oy = offset * sin_a * 0.3
                pygame.draw.circle(overlay, (20, 20, 20, alpha),
                                 (px + int(ox), py + int(oy)), max(1, int(size * 0.5)))
            pygame.draw.line(overlay, (40, 40, 40, alpha),
                           (px - int(size * cos_a), py - int(size * sin_a)),
                           (px + int(size * cos_a), py + int(size * sin_a)), 2)
        
        # Темные дымные частицы поднимаются вверх
        for k in range(10):
            smoke_x = cx + random.randint(-20, 20)
            smoke_y = cy - int(10 * t) + random.randint(-10, 10)
            smoke_alpha = int(120 * (1 - t) * random.random())
            smoke_r = random.randint(2, 4)
            pygame.draw.circle(overlay, (40, 0, 40, smoke_alpha), (smoke_x, smoke_y), smoke_r)
        
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(5)  # Минимальная задержка для максимальной скорости

def animate_rune_shield_spell(screen, target_px, redraw_callback=None):
    # Руна щита: камень с зелёным руническим знаком (щит) и белыми частицами
    frames = 70  # Увеличено до 70 кадров для максимальной плавности
    cx, cy = target_px
    base_y = cy - CELL_SIZE//2 - 15
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Мерцание
        flicker = 0.7 + 0.3 * math.sin(i * 0.9)
        alpha = int(220 * flicker)
        
        # Камень (эллипс) - как в книге
        stone_w, stone_h = 32, 24
        stone_rect = pygame.Rect(cx - stone_w//2, base_y - stone_h//2, stone_w, stone_h)
        pygame.draw.ellipse(overlay, (80, 200, 80, alpha), stone_rect)
        pygame.draw.ellipse(overlay, (40, 100, 40, alpha), stone_rect.inflate(-8, -8), 2)
        
        # Рунический знак (щит) - зелёный полигон, как в книге
        shield_points = [
            (cx - 10, base_y - 8),
            (cx + 10, base_y - 8),
            (cx + 12, base_y + 6),
            (cx, base_y + 14),
            (cx - 12, base_y + 6)
        ]
        pygame.draw.polygon(overlay, (60, 255, 120, alpha), shield_points)
        pygame.draw.polygon(overlay, (40, 200, 100, alpha), shield_points, 2)
        
        # Белые частицы вокруг - как в книге
        for k in range(7):
            angle = math.radians(k * (360 / 7))
            radius = 18 + 3 * math.sin(i * 0.6 + k)
            px = cx + int(radius * math.cos(angle))
            py = base_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.8)
            pygame.draw.circle(overlay, (255, 255, 255, particle_alpha), (px, py), 2)
            # Мерцающие точки
            if k % 2 == 0:
                pygame.draw.circle(overlay, (255, 255, 255, particle_alpha), (px, py), 1)
        
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний

def animate_meteor_rain(screen, meteors, redraw_callback=None, explosion_sound_callback=None, flight_sound_callback=None):
    """Анимация метеоритного дождя - все метеориты падают одновременно с маленьким промежутком"""
    import pygame
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    # Подготовка данных для всех метеоритов
    meteor_data = []
    for idx, (start_px, end_px, delay_frames) in enumerate(meteors):
        meteor_data.append({
            'start': start_px,
            'end': end_px,
            'delay': delay_frames,
            'current_frame': -delay_frames,  # Отрицательное значение означает задержку
            'exploded': False
        })
    
    # Фиксированная скорость полета метеоритов независимо от расстояния
    PROJECTILE_SPEED = 52  # Повышенная скорость для метеоритов
    explode_frames = 80  # Увеличено до 80 кадров для максимальной плавности
    if not meteor_data:
        return  # Нет метеоритов для анимации
    
    # Рассчитываем количество кадров полета для каждого метеорита на основе расстояния
    for meteor in meteor_data:
        dx = meteor['end'][0] - meteor['start'][0]
        dy = meteor['end'][1] - meteor['start'][1]
        distance = math.sqrt(dx*dx + dy*dy)
        meteor['flight_frames'] = max(1, int(distance / PROJECTILE_SPEED))
        meteor['step_x'] = (dx / distance * PROJECTILE_SPEED) if distance > 0 else 0
        meteor['step_y'] = (dy / distance * PROJECTILE_SPEED) if distance > 0 else 0
        meteor['x'] = float(meteor['start'][0])
        meteor['y'] = float(meteor['start'][1])
        meteor['angle'] = math.atan2(dy, dx)
    
    max_flight_frames = max(meteor['flight_frames'] for meteor in meteor_data)
    max_delay = max(meteor['delay'] for meteor in meteor_data)
    max_total_frames = max_flight_frames + explode_frames + max_delay
    
    # Флаги для звуков (чтобы каждый звук проигрался один раз)
    flight_sounds_played = [False] * len(meteor_data)
    explosion_sounds_played = [False] * len(meteor_data)
    
    # Проигрываем все кадры анимации
    for global_frame in range(max_total_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Обрабатываем каждый метеорит
        for meteor_idx, meteor in enumerate(meteor_data):
            # Если метеорит еще в задержке
            if meteor['current_frame'] < 0:
                meteor['current_frame'] += 1
                continue
            
            frame = meteor['current_frame']
            
            # Этап полета
            if frame < meteor['flight_frames'] and not meteor['exploded']:
                # Проигрываем звук полета один раз
                if not flight_sounds_played[meteor_idx] and flight_sound_callback:
                    try:
                        flight_sound_callback()
                    except:
                        pass
                    flight_sounds_played[meteor_idx] = True
                
                # Двигаем метеорит с фиксированной скоростью
                meteor['x'] += meteor['step_x']
                meteor['y'] += meteor['step_y']
                
                # Проверяем, достигли ли мы цели
                if frame == meteor['flight_frames'] - 1 or (abs(meteor['x'] - meteor['end'][0]) < abs(meteor['step_x']) and abs(meteor['y'] - meteor['end'][1]) < abs(meteor['step_y'])):
                    meteor['x'], meteor['y'] = meteor['end'][0], meteor['end'][1]
                
                ball_x = int(meteor['x'])
                ball_y = int(meteor['y'])
                angle = meteor['angle']
                t = frame / max(1, meteor['flight_frames'] - 1)  # Для анимации эффектов
                
                base_r = 12
                stone_r = base_r + int(3 * math.sin(t * 3))
                
                # Камень
                pygame.draw.circle(overlay, (60, 50, 45, 255), (ball_x, ball_y), stone_r)
                pygame.draw.circle(overlay, (90, 70, 60, 240), (ball_x, ball_y), int(stone_r*0.9))
                
                # Трещины
                for crack in range(4):
                    crack_angle = angle + crack * math.pi / 2
                    crack_x = ball_x + int(stone_r * 0.6 * math.cos(crack_angle))
                    crack_y = ball_y + int(stone_r * 0.6 * math.sin(crack_angle))
                    pygame.draw.line(overlay, (255, 180, 60, 220), (ball_x, ball_y), (crack_x, crack_y), 2)
                
                # Раскалённые края
                for edge in range(8):
                    edge_angle = edge * (2*math.pi / 8.0) + t
                    edge_x = ball_x + int(stone_r * 0.85 * math.cos(edge_angle))
                    edge_y = ball_y + int(stone_r * 0.85 * math.sin(edge_angle))
                    pygame.draw.circle(overlay, (255, 140, 40, 200), (edge_x, edge_y), 3)
                    pygame.draw.circle(overlay, (255, 220, 100, 150), (edge_x, edge_y), 2)
                
                # Огненный хвост
                tail_length = 35
                for j in range(15):
                    trail_t = j / 15.0
                    trail_x = ball_x - int(tail_length * trail_t * math.cos(angle))
                    trail_y = ball_y - int(tail_length * trail_t * math.sin(angle))
                    trail_r = max(2, int(base_r * (1 - trail_t * 0.9)))
                    tail_alpha = int(220 * (1 - trail_t * 0.7))
                    
                    if trail_t < 0.3:
                        color = (255, 150, 50, tail_alpha)
                    elif trail_t < 0.6:
                        color = (255, 120, 40, tail_alpha)
                    else:
                        color = (200, 80, 30, tail_alpha)
                    pygame.draw.circle(overlay, color, (trail_x, trail_y), trail_r)
                    
                    if j % 2 == 0:
                        for side in [-1, 1]:
                            spark_x = trail_x + int(5 * math.cos(angle + math.pi/2 + side * 0.3))
                            spark_y = trail_y + int(5 * math.sin(angle + math.pi/2 + side * 0.3))
                            pygame.draw.circle(overlay, (255, 220, 120, int(tail_alpha*0.6)), (spark_x, spark_y), 2)
                
                meteor['current_frame'] += 1
                
                # Переход к взрыву
                if frame >= meteor['flight_frames'] - 1:
                    meteor['exploded'] = True
                    meteor['explode_start_frame'] = global_frame
            
            # Этап взрыва
            elif meteor['exploded']:
                if not explosion_sounds_played[meteor_idx] and explosion_sound_callback:
                    try:
                        explosion_sound_callback()
                    except:
                        pass
                    explosion_sounds_played[meteor_idx] = True
                
                # Проверяем что explode_start_frame был установлен
                if 'explode_start_frame' not in meteor:
                    meteor['explode_start_frame'] = global_frame
                
                explode_frame = global_frame - meteor['explode_start_frame']
                if explode_frame < explode_frames:
                    ex_t = explode_frame / (explode_frames - 1) if explode_frames > 1 else 1.0
                    ex_x, ex_y = meteor['end']
                    
                    # Кольца взрыва
                    for k, radius in enumerate([20, 35, 55, 80, 110]):
                        alpha = int(max(0, 240 - int(280 * ex_t * (k+1) / 5)))
                        pygame.draw.circle(overlay, (255, 150, 50, alpha), (ex_x, ex_y), radius, 4)
                    
                    # Ядро взрыва
                    core_size = int(15 + 30 * (1 - ex_t))
                    pygame.draw.circle(overlay, (255, 220, 100, int(255 * (1 - ex_t * 0.5))), (ex_x, ex_y), core_size)
                    
                    # Искры
                    for k in range(24):
                        spark_angle = (k * (2*math.pi / 24.0)) + ex_t * 3
                        spark_dist = 20 + int(100 * ex_t)
                        spark_x = ex_x + int(spark_dist * math.cos(spark_angle))
                        spark_y = ex_y + int(spark_dist * math.sin(spark_angle))
                        spark_alpha = int(200 * (1 - ex_t))
                        pygame.draw.circle(overlay, (255, 140, 40, spark_alpha), (spark_x, spark_y), 4)
                        
                        if k % 3 == 0:
                            small_spark_x = spark_x + int(8 * math.cos(spark_angle + math.pi/4))
                            small_spark_y = spark_y + int(8 * math.sin(spark_angle + math.pi/4))
                            pygame.draw.circle(overlay, (255, 200, 100, int(spark_alpha*0.7)), (small_spark_x, small_spark_y), 2)
                    
                    # Дым
                    for k in range(12):
                        smoke_angle = (k * (2*math.pi / 12.0))
                        smoke_dist = int(50 * ex_t)
                        smoke_x = ex_x + int(smoke_dist * math.cos(smoke_angle))
                        smoke_y = ex_y + int(smoke_dist * math.sin(smoke_angle))
                        smoke_size = int(8 + 15 * ex_t)
                        pygame.draw.circle(overlay, (70, 55, 55, int(150*(1-ex_t*0.8))), (smoke_x, smoke_y), smoke_size)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(9)  # Ускорено для быстрых заклинаний

def animate_chain_lightning(screen, caster, targets, redraw_callback=None):
    """Анимация цепной молнии - молния бьёт первую цель, затем отскакивает к остальным"""
    import random
    import math
    from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
    
    # Анимация для каждой цели по очереди
    for target_idx, target in enumerate(targets):
        if target.health <= 0:
            continue
        
        target_px = (target.x * CELL_SIZE + CELL_SIZE // 2, target.y * CELL_SIZE + CELL_SIZE // 2)
        
        # Определяем начальную позицию молнии
        if target_idx == 0:
            # Первая молния сверху экрана к цели
            start_px = (target_px[0], 0)
        else:
            # Последующие молнии начинаются от предыдущей цели (отскок)
            prev_target = targets[target_idx - 1]
            start_px = (prev_target.x * CELL_SIZE + CELL_SIZE // 2, 
                       prev_target.y * CELL_SIZE + CELL_SIZE // 2)
        
        # Рисуем молнию от начальной позиции к цели
        for strike in range(2):  # 2 удара молнии на каждую цель
            pygame.event.pump()
            if redraw_callback:
                redraw_callback()
            
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            cx, cy = target_px
            start_x, start_y = start_px
            
            # Рисуем зигзагообразную молнию
            points = [(start_x, start_y)]
            current_y = start_y
            current_x = start_x
            
            # Для отскоков - рисуем молнию горизонтально или по направлению к цели
            if target_idx > 0:
                # Отскок - молния идёт от предыдущей цели к следующей
                steps = 10
                for step in range(steps + 1):
                    t = step / steps
                    x = int(start_x * (1 - t) + cx * t)
                    y = int(start_y * (1 - t) + cy * t)
                    # Добавляем случайные отклонения для зигзага
                    if step > 0 and step < steps:
                        x += random.randint(-8, 8)
                        y += random.randint(-5, 5)
                    points.append((x, y))
            else:
                # Первая молния - вертикально сверху вниз
                while current_y < cy:
                    offset = random.randint(-15, 15)
                    current_x += offset
                    current_y += random.randint(15, 30)
                    points.append((current_x, min(current_y, cy)))
            
            # Яркая молния
            if len(points) > 1:
                pygame.draw.lines(s, (255, 255, 255, 255), False, points, 4)
                pygame.draw.lines(s, (200, 200, 255, 200), False, points, 8)
                pygame.draw.lines(s, (150, 150, 255, 100), False, points, 12)
            
            # Вспышка в точке удара
            if target_idx == 0:
                # Первый удар - светящийся шар
                for i in range(3):
                    radius = 30 - i * 8
                    alpha = 255 - i * 60
                    pygame.draw.circle(s, (255, 255, 255, alpha), (cx, cy), radius)
            else:
                # Последующие удары - красивые искры вместо шара
                # Основные искры - больше и ярче
                for spark_idx in range(16):
                    spark_angle = (spark_idx * (2*math.pi / 16.0)) + random.uniform(-0.4, 0.4)
                    spark_dist = random.randint(12, 35)
                    spark_x = cx + int(spark_dist * math.cos(spark_angle))
                    spark_y = cy + int(spark_dist * math.sin(spark_angle))
                    spark_alpha = random.randint(200, 255)
                    
                    # Яркая центральная часть искры
                    spark_size = random.randint(3, 6)
                    pygame.draw.circle(s, (255, 255, 255, spark_alpha), (spark_x, spark_y), spark_size)
                    # Голубая оболочка
                    pygame.draw.circle(s, (180, 220, 255, int(spark_alpha*0.8)), (spark_x, spark_y), spark_size + 2)
                    # Внешнее свечение
                    pygame.draw.circle(s, (150, 200, 255, int(spark_alpha*0.5)), (spark_x, spark_y), spark_size + 4)
                    
                    # Дополнительные маленькие искры-хвосты
                    if spark_idx % 2 == 0:
                        tail_x = spark_x + int(8 * math.cos(spark_angle + math.pi))
                        tail_y = spark_y + int(8 * math.sin(spark_angle + math.pi))
                        pygame.draw.circle(s, (255, 255, 255, int(spark_alpha*0.9)), (tail_x, tail_y), 2)
                    # Боковые искры
                    if spark_idx % 4 == 0:
                        for side in [-1, 1]:
                            side_angle = spark_angle + side * 0.5
                            side_x = spark_x + int(6 * math.cos(side_angle))
                            side_y = spark_y + int(6 * math.sin(side_angle))
                            pygame.draw.circle(s, (220, 240, 255, int(spark_alpha*0.7)), (side_x, side_y), 2)
            
            screen.blit(s, (0, 0))
            pygame.display.flip()
            pygame.time.delay(6)  # Ускорено для быстрых заклинаний
            
            if strike < 1:
                pygame.event.pump()
                if redraw_callback:
                    redraw_callback()
                pygame.display.flip()
                pygame.time.delay(7)  # Ускорено для быстрых заклинаний
        
        # Небольшая задержка перед следующим отскоком
        if target_idx < len(targets) - 1:
            pygame.event.pump()
            if redraw_callback:
                redraw_callback()
            pygame.display.flip()
            pygame.time.delay(10)  # Ускорено для быстрых заклинаний

def animate_accuracy(screen, target_px, redraw_callback=None):
    """Анимация точности - появляется линза и монетка крутится два раза по вертикальной оси"""
    import random
    import math
    from .config import CELL_SIZE
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = target_px
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1)
        
        # Линза появляется (эллипс с градиентом)
        lens_alpha = int(200 * min(1.0, t * 2))  # Быстро появляется
        lens_w = int(40 + 20 * min(1.0, t * 2))
        lens_h = int(50 + 30 * min(1.0, t * 2))
        
        # Рисуем линзу (эллипс с эффектом стекла)
        lens_rect = pygame.Rect(cx - lens_w // 2, cy - lens_h // 2, lens_w, lens_h)
        
        # Внешний ободок
        pygame.draw.ellipse(overlay, (180, 220, 255, lens_alpha), lens_rect, 2)
        # Внутреннее стекло с градиентом
        for j in range(3):
            inner_rect = lens_rect.inflate(-j*4, -j*4)
            inner_alpha = int(lens_alpha * (1 - j * 0.3))
            pygame.draw.ellipse(overlay, (220, 240, 255, inner_alpha), inner_rect)
        
        # Монетка крутится два раза по вертикальной оси
        coin_rotations = 2  # Два оборота
        rotation_angle = (t * coin_rotations * 2 * math.pi) % (2 * math.pi)
        
        # Размер монетки меняется при вращении (эффект перспективы)
        coin_base_size = 8
        coin_size = int(coin_base_size * abs(math.cos(rotation_angle)))
        
        # Позиция монетки в центре линзы
        coin_y = cy
        
        # Рисуем монетку (круг, который становится линией при повороте на 90/270 градусов)
        if coin_size > 1:
            pygame.draw.circle(overlay, (255, 215, 0, 200), (cx, coin_y), coin_size)  # Золотая монетка
            pygame.draw.circle(overlay, (200, 150, 0, 200), (cx, coin_y), coin_size - 2)
        
        # Дополнительные блики на линзе
        if t > 0.3:
            for k in range(3):
                spark_x = cx + random.randint(-15, 15)
                spark_y = cy + random.randint(-15, 15)
                spark_alpha = int(150 * (1 - t) * random.random())
                pygame.draw.circle(overlay, (255, 255, 255, spark_alpha), (spark_x, spark_y), 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний

def animate_rune_haste_spell(screen, target_px, redraw_callback=None):
    # Руна скорости: камень с белым руническим знаком (молния) и жёлтыми частицами
    frames = 70  # Увеличено до 70 кадров для максимальной плавности
    cx, cy = target_px
    base_y = cy - CELL_SIZE//2 - 15
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Мерцание
        flicker = 0.7 + 0.3 * math.sin(i * 0.9)
        alpha = int(220 * flicker)
        
        # Камень (эллипс) - серый, как в книге
        stone_w, stone_h = 32, 24
        stone_rect = pygame.Rect(cx - stone_w//2, base_y - stone_h//2, stone_w, stone_h)
        pygame.draw.ellipse(overlay, (200, 200, 200, alpha), stone_rect)
        pygame.draw.ellipse(overlay, (120, 120, 120, alpha), stone_rect.inflate(-8, -8), 2)
        
        # Рунический знак (молния) - белый, как в книге
        lightning_points = [
            (cx - 8, base_y - 6),
            (cx, base_y + 2),
            (cx - 3, base_y + 2),
            (cx + 8, base_y + 14)
        ]
        pygame.draw.lines(overlay, (255, 255, 255, alpha), False, lightning_points, 3)
        # Дополнительная линия для красоты
        pygame.draw.line(overlay, (255, 255, 255, alpha), (cx - 3, base_y + 2), (cx + 5, base_y + 10), 2)
        
        # Жёлтые частицы вокруг - как в книге
        for k in range(7):
            angle = math.radians(k * (360 / 7))
            radius = 18 + 3 * math.sin(i * 0.6 + k)
            px = cx + int(radius * math.cos(angle))
            py = base_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.8)
            pygame.draw.circle(overlay, (255, 255, 120, particle_alpha), (px, py), 2)
            # Мерцающие точки
            if k % 2 == 0:
                pygame.draw.circle(overlay, (255, 255, 150, particle_alpha), (px, py), 1)
        
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(5)  # Минимальная задержка для максимальной скорости

def animate_fireball(screen, start_px, end_px, redraw_callback=None, explosion_sound_callback=None, flight_sound_callback=None):
    # Горящий камень летит к цели, затем взрыв после приземления
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 48  # Повышенная скорость для огненного шара
    dx = end_px[0] - start_px[0]
    dy = end_px[1] - start_px[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    flight_frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    # Воспроизводим звук полёта в начале анимации
    if flight_sound_callback:
        flight_sound_callback()
    
    ball_x, ball_y = float(start_px[0]), float(start_px[1])
    angle = math.atan2(dy, dx)
    
    # Этап 1: полет горящего камня
    for i in range(flight_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Двигаем снаряд с фиксированной скоростью
        ball_x += step_x
        ball_y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == flight_frames - 1 or (abs(ball_x - end_px[0]) < abs(step_x) and abs(ball_y - end_px[1]) < abs(step_y)):
            ball_x, ball_y = end_px[0], end_px[1]
        
        # Позиция камня
        ball_x_int = int(ball_x)
        ball_y_int = int(ball_y)
        # Размер горящего камня (неравномерный, как настоящий камень)
        base_r = 12
        t = i / max(1, flight_frames - 1)  # Для анимации эффектов
        # Камень с неровной формой
        stone_r = base_r + int(3 * math.sin(t * 3))
        # Тёмное ядро камня
        pygame.draw.circle(overlay, (60, 50, 45, 255), (ball_x_int, ball_y_int), stone_r)
        pygame.draw.circle(overlay, (90, 70, 60, 240), (ball_x_int, ball_y_int), int(stone_r*0.9))
        # Раскалённые трещины на камне
        for crack in range(4):
            crack_angle = angle + crack * math.pi / 2
            crack_x = ball_x_int + int(stone_r * 0.6 * math.cos(crack_angle))
            crack_y = ball_y_int + int(stone_r * 0.6 * math.sin(crack_angle))
            pygame.draw.line(overlay, (255, 180, 60, 220), (ball_x_int, ball_y_int), (crack_x, crack_y), 2)
        # Раскалённые края (огненные точки по краю)
        for edge in range(8):
            edge_angle = edge * (2*math.pi / 8.0) + t
            edge_x = ball_x_int + int(stone_r * 0.85 * math.cos(edge_angle))
            edge_y = ball_y_int + int(stone_r * 0.85 * math.sin(edge_angle))
            pygame.draw.circle(overlay, (255, 140, 40, 200), (edge_x, edge_y), 3)
            pygame.draw.circle(overlay, (255, 220, 100, 150), (edge_x, edge_y), 2)
        # Длинный огненный хвост
        tail_length = 35
        for j in range(15):
            trail_t = j / 15.0
            trail_x = ball_x_int - int(tail_length * trail_t * math.cos(angle))
            trail_y = ball_y_int - int(tail_length * trail_t * math.sin(angle))
            trail_r = max(2, int(base_r * (1 - trail_t * 0.9)))
            tail_alpha = int(220 * (1 - trail_t * 0.7))
            # Градиент хвоста от яркого к тусклому
            if trail_t < 0.3:
                color = (255, 150, 50, tail_alpha)
            elif trail_t < 0.6:
                color = (255, 120, 40, tail_alpha)
            else:
                color = (200, 80, 30, tail_alpha)
            pygame.draw.circle(overlay, color, (trail_x, trail_y), trail_r)
            # Искры по бокам хвоста
            if j % 2 == 0:
                for side in [-1, 1]:
                    spark_x = trail_x + int(5 * math.cos(angle + math.pi/2 + side * 0.3))
                    spark_y = trail_y + int(5 * math.sin(angle + math.pi/2 + side * 0.3))
                    pygame.draw.circle(overlay, (255, 220, 120, int(tail_alpha*0.6)), (spark_x, spark_y), 2)
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний
    
    # Этап 2: взрыв после приземления
    explode_frames = 80  # Увеличено до 80 кадров для максимальной плавности
    # Воспроизводим звук взрыва в начале этапа взрыва
    if explosion_sound_callback and callable(explosion_sound_callback):
        explosion_sound_callback()
    for i in range(explode_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ex_t = i / (explode_frames - 1)
        # Кольца взрыва (расходящиеся волны)
        for k, radius in enumerate([20, 35, 55, 80, 110]):
            alpha = int(max(0, 240 - int(280 * ex_t * (k+1) / 5)))
            pygame.draw.circle(overlay, (255, 150, 50, alpha), (end_px[0], end_px[1]), radius, 4)
        # Яркое ядро взрыва
        core_size = int(15 + 30 * (1 - ex_t))
        pygame.draw.circle(overlay, (255, 220, 100, int(255 * (1 - ex_t * 0.5))), (end_px[0], end_px[1]), core_size)
        # Искры вокруг взрыва
        for k in range(24):
            spark_angle = (k * (2*math.pi / 24.0)) + ex_t * 3
            spark_dist = 20 + int(100 * ex_t)
            spark_x = end_px[0] + int(spark_dist * math.cos(spark_angle))
            spark_y = end_px[1] + int(spark_dist * math.sin(spark_angle))
            spark_alpha = int(200 * (1 - ex_t))
            pygame.draw.circle(overlay, (255, 140, 40, spark_alpha), (spark_x, spark_y), 4)
            # Дополнительные мелкие искры
            if k % 3 == 0:
                small_spark_x = spark_x + int(8 * math.cos(spark_angle + math.pi/4))
                small_spark_y = spark_y + int(8 * math.sin(spark_angle + math.pi/4))
                pygame.draw.circle(overlay, (255, 200, 100, int(spark_alpha*0.7)), (small_spark_x, small_spark_y), 2)
        # Дым
        for k in range(12):
            smoke_angle = (k * (2*math.pi / 12.0))
            smoke_dist = int(50 * ex_t)
            smoke_x = end_px[0] + int(smoke_dist * math.cos(smoke_angle))
            smoke_y = end_px[1] + int(smoke_dist * math.sin(smoke_angle))
            smoke_size = int(8 + 15 * ex_t)
            pygame.draw.circle(overlay, (70, 55, 55, int(150*(1-ex_t*0.8))), (smoke_x, smoke_y), smoke_size)
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(6)  # Ускорено для быстрых заклинаний

def animate_raise_dead(screen, center_px, redraw_callback=None):
    # Рука вылазит из земли в центре клетки
    frames = 70  # Увеличено до 70 кадров для максимальной плавности
    cx, cy = center_px
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames-1)
        # Земляной круг
        pygame.draw.circle(overlay, (90, 60, 30, 180), (cx, cy+10), int(6 + 10*t))
        # Рука (пальцы появляются снизу вверх)
        height = int(4 + 18 * t)
        pygame.draw.rect(overlay, (200, 200, 200, 240), (cx-3, cy+8-height, 6, height))  # ладонь/предплечье
        for dx in [-6, -2, 2, 6]:
            finger_h = max(4, height - 6)
            pygame.draw.rect(overlay, (200,200,200,240), (cx+dx-1, cy+8-finger_h, 2, finger_h))
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний

def animate_fire_explosion(screen, x, y):
    """Улучшенный взрыв с детальными огненными эффектами"""
    frames = 80  # Увеличено до 80 кадров для максимальной плавности  # Увеличено с 14 до 40 кадров
    for i in range(frames):
        pygame.event.pump()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1)
        
        # Множественные расходящиеся огненные кольца
        for ring in range(4):
            r = int(8 + (18 + ring * 8) * t)
            alpha = max(0, int((200 - ring * 30) * (1 - t)))
            # Внешнее кольцо - оранжевое
            pygame.draw.circle(overlay, (255, 140, 50, alpha), (x, y), r, 4)
            # Внутреннее кольцо - желтое
            if ring < 2:
                pygame.draw.circle(overlay, (255, 200, 80, min(255, alpha + 40)), (x, y), max(1, r - 3), 2)
        
        # Яркое белое ядро взрыва
        core_r = max(2, int(12 * (1 - t)))
        pygame.draw.circle(overlay, (255, 255, 255, int(255 * (1 - t * 0.7))), (x, y), core_r)
        pygame.draw.circle(overlay, (255, 240, 180, int(220 * (1 - t))), (x, y), core_r + 3)
        pygame.draw.circle(overlay, (255, 180, 100, int(180 * (1 - t))), (x, y), core_r + 6)
        
        # Множество разлетающихся искр
        for k in range(16):
            ang = (k * (2*math.pi / 16.0)) + t * 0.8 + k * 0.3
            # Искры разлетаются с разной скоростью
            base_dist = 8 + (k % 3) * 5
            dist = base_dist + int(30 * t)
            sx = x + int(dist * math.cos(ang))
            sy = y + int(dist * math.sin(ang))
            
            spark_alpha = int(220 * (1 - t * 0.9))
            spark_size = max(1, 4 - int(3 * t))
            
            # Градиент цвета искр
            if k % 3 == 0:
                color = (255, 220, 100, spark_alpha)  # Желтые
            elif k % 3 == 1:
                color = (255, 160, 60, spark_alpha)   # Оранжевые
            else:
                color = (255, 100, 40, spark_alpha)   # Красные
            
            pygame.draw.circle(overlay, color, (sx, sy), spark_size)
            
            # След за искрой
            if t < 0.6:
                trail_x = x + int((dist - 8) * math.cos(ang))
                trail_y = y + int((dist - 8) * math.sin(ang))
                pygame.draw.line(overlay, (*color[:3], spark_alpha // 2), 
                               (trail_x, trail_y), (sx, sy), 2)
        
        # Дополнительные мелкие искры между основными
        for k in range(24):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.randint(5, int(15 + 35 * t))
            sx = x + int(dist * math.cos(ang))
            sy = y + int(dist * math.sin(ang))
            alpha = int(random.randint(150, 220) * (1 - t))
            pygame.draw.circle(overlay, (255, 200, 120, alpha), (sx, sy), 1)
        
        # Огненное свечение вокруг взрыва
        glow_r = int(20 + 35 * t)
        pygame.draw.circle(overlay, (255, 140, 40, int(60 * (1 - t))), (x, y), glow_r)
        
        # Дым начинает появляться в конце
        if t > 0.5:
            smoke_t = (t - 0.5) / 0.5
            for k in range(8):
                smoke_ang = k * (2*math.pi / 8.0) + smoke_t * 0.5
                smoke_dist = int(15 + 25 * smoke_t)
                smoke_x = x + int(smoke_dist * math.cos(smoke_ang))
                smoke_y = y + int(smoke_dist * math.sin(smoke_ang)) - int(10 * smoke_t)
                smoke_r = int(5 + 8 * smoke_t)
                smoke_alpha = int(120 * (1 - smoke_t * 0.7))
                pygame.draw.circle(overlay, (60, 50, 45, smoke_alpha), (smoke_x, smoke_y), smoke_r)
        
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        pygame.time.delay(11)  # Ускорено для быстрых заклинаний

def animate_forget_spell(screen, start, end, redraw_callback=None):
    """Максимально насыщенная анимация заклинания Забвение с темно-фиолетовыми эффектами"""
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        
        # Создаем максимально детализированный эффект забвения
        forget_surface = pygame.Surface((CELL_SIZE*4, CELL_SIZE*4), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*2, CELL_SIZE*2
        
        # Основной темно-фиолетовый туман забвения с максимальной насыщенностью
        alpha = int(180 * (1 - abs(t - 0.5) * 2))  # максимальная непрозрачность в середине
        pygame.draw.circle(forget_surface, (40, 10, 60, alpha), (center_x, center_y), 35)
        
        # Множественные слои тумана с разной интенсивностью
        for j in range(6):
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            cloud_alpha = int(alpha * 0.8)
            pygame.draw.circle(forget_surface, (60, 20, 80, cloud_alpha), 
                             (center_x + offset_x, center_y + offset_y), 25)
        
        # Третичные облака забвения
        for j in range(8):
            offset_x = random.randint(-25, 25)
            offset_y = random.randint(-25, 25)
            cloud_alpha = int(alpha * 0.6)
            pygame.draw.circle(forget_surface, (80, 40, 100, cloud_alpha), 
                             (center_x + offset_x, center_y + offset_y), 18)
        
        # Четвертичные облака
        for j in range(10):
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            cloud_alpha = int(alpha * 0.4)
            pygame.draw.circle(forget_surface, (100, 60, 120, cloud_alpha), 
                             (center_x + offset_x, center_y + offset_y), 12)
        
        # Интенсивные мистические частицы забвения
        for j in range(12):
            angle = (j * 0.524 + i * 0.4) % (2 * math.pi)  # вращение
            radius = 20 + random.randint(-8, 8)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 1.0)
            pygame.draw.circle(forget_surface, (160, 80, 180, particle_alpha), 
                             (particle_x, particle_y), 6)
        
        # Дополнительные светящиеся частицы
        for j in range(8):
            particle_x = center_x + random.randint(-25, 25)
            particle_y = center_y + random.randint(-25, 25)
            particle_alpha = int(alpha * 0.9)
            pygame.draw.circle(forget_surface, (200, 120, 220, particle_alpha), 
                             (particle_x, particle_y), 4)
        
        # Мелкие блестящие частицы
        for j in range(15):
            particle_x = center_x + random.randint(-30, 30)
            particle_y = center_y + random.randint(-30, 30)
            particle_alpha = int(alpha * 0.7)
            pygame.draw.circle(forget_surface, (240, 180, 255, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Центральный кристалл забвения с максимальной детализацией
        crystal_alpha = min(255, int(alpha * 1.5))
        # Внешний слой кристалла
        pygame.draw.circle(forget_surface, (80, 30, 100, crystal_alpha), 
                         (center_x, center_y), 18)
        # Средний слой
        pygame.draw.circle(forget_surface, (120, 60, 140, crystal_alpha), 
                         (center_x, center_y), 14)
        # Внутренний слой
        pygame.draw.circle(forget_surface, (160, 100, 180, crystal_alpha), 
                         (center_x, center_y), 10)
        # Ядро кристалла
        pygame.draw.circle(forget_surface, (200, 140, 220, crystal_alpha), 
                         (center_x, center_y), 6)
        # Центральное ядро
        pygame.draw.circle(forget_surface, (255, 200, 255, crystal_alpha), 
                         (center_x, center_y), 3)
        
        # Интенсивный эффект пульсации с множественными слоями
        pulse1 = int(12 * math.sin(i * 0.3))
        pulse2 = int(10 * math.sin(i * 0.5 + 1))
        pulse3 = int(8 * math.sin(i * 0.7 + 2))
        pulse4 = int(6 * math.sin(i * 0.9 + 3))
        
        pygame.draw.circle(forget_surface, (60, 20, 80, alpha//4), 
                         (center_x, center_y), 40 + pulse1)
        pygame.draw.circle(forget_surface, (80, 40, 100, alpha//5), 
                         (center_x, center_y), 45 + pulse2)
        pygame.draw.circle(forget_surface, (100, 60, 120, alpha//6), 
                         (center_x, center_y), 50 + pulse3)
        pygame.draw.circle(forget_surface, (120, 80, 140, alpha//7), 
                         (center_x, center_y), 55 + pulse4)
        
        # Интенсивные мистические руны забвения
        for j in range(8):
            angle = j * math.pi / 4 + i * 0.3
            rune_x = center_x + int(25 * math.cos(angle))
            rune_y = center_y + int(25 * math.sin(angle))
            rune_alpha = int(alpha * 0.8)
            pygame.draw.circle(forget_surface, (180, 120, 200, rune_alpha), 
                             (rune_x, rune_y), 3)
        
        # Дополнительные руны
        for j in range(6):
            angle = j * math.pi / 3 + i * 0.2
            rune_x = center_x + int(15 * math.cos(angle))
            rune_y = center_y + int(15 * math.sin(angle))
            rune_alpha = int(alpha * 0.9)
            pygame.draw.circle(forget_surface, (200, 160, 220, rune_alpha), 
                             (rune_x, rune_y), 2)
        
        # Эффект искажения пространства с множественными слоями
        for j in range(5):
            distortion_x = center_x + random.randint(-35, 35)
            distortion_y = center_y + random.randint(-35, 35)
            distortion_alpha = int(alpha * 0.5)
            pygame.draw.circle(forget_surface, (120, 60, 140, distortion_alpha), 
                             (distortion_x, distortion_y), 12)
        
        # Дополнительные искажения
        for j in range(3):
            distortion_x = center_x + random.randint(-40, 40)
            distortion_y = center_y + random.randint(-40, 40)
            distortion_alpha = int(alpha * 0.3)
            pygame.draw.circle(forget_surface, (140, 80, 160, distortion_alpha), 
                             (distortion_x, distortion_y), 8)
        
        # Эффект вихря забвения
        for j in range(20):
            angle = j * 0.314 + i * 0.6  # вращение
            radius = 15 + j * 0.5
            vortex_x = center_x + int(radius * math.cos(angle))
            vortex_y = center_y + int(radius * math.sin(angle))
            vortex_alpha = int(alpha * 0.4)
            pygame.draw.circle(forget_surface, (100, 50, 120, vortex_alpha), 
                             (vortex_x, vortex_y), 1)
        
        # Применяем эффект забвения к экрану
        screen.blit(forget_surface, (x - CELL_SIZE*2, y - CELL_SIZE*2))
        
        pygame.display.flip()
        pygame.time.delay(17)  # Ускорено для быстрых заклинаний

def animate_frost_ring(screen, center, radius_cells=1, redraw_callback=None):
    """Улучшенное Кольцо холода: детальная заморозка с ледяными кристаллами и туманом"""
    cx, cy = center
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames - 1)
        ring_px = pygame.Surface((CELL_SIZE*4, CELL_SIZE*4), pygame.SRCALPHA)
        ring_center = (CELL_SIZE*2, CELL_SIZE*2)
        
        # Морозное расширяющееся кольцо
        expand_r = int(CELL_SIZE * 1.5 * t)
        
        # Ледяной туман расползается от центра
        for fog_ring in range(5):
            fog_r = int((10 + fog_ring * 15) * t)
            fog_alpha = int(80 * (1 - fog_ring * 0.15) * (1 - t * 0.5))
            pygame.draw.circle(ring_px, (200, 230, 255, fog_alpha), ring_center, fog_r)
        
        # Множественные ледяные кольца
        for ring in range(4):
            ring_r = int(expand_r - ring * 8)
            if ring_r > 5:
                ring_alpha = int(180 - ring * 30)
                # Основное голубое кольцо
                pygame.draw.circle(ring_px, (180, 220, 255, ring_alpha), ring_center, ring_r, 3)
                # Белое свечение по краю
                pygame.draw.circle(ring_px, (230, 245, 255, min(255, ring_alpha + 40)), ring_center, ring_r, 1)
        
        # Ледяные трещины растут от центра
        num_cracks = 12
        for k in range(num_cracks):
            ang = k * (2*math.pi/num_cracks) + i*0.05
            crack_len = int(expand_r * 0.9)
            
            # Рисуем разветвляющуюся трещину
            for seg in range(4):
                seg_t = seg / 4.0
                if seg_t > t:
                    break
                    
                r1 = int(crack_len * seg_t)
                r2 = int(crack_len * min(1.0, seg_t + 0.25))
                
                x1 = int(ring_center[0] + r1 * math.cos(ang))
                y1 = int(ring_center[1] + r1 * math.sin(ang))
                x2 = int(ring_center[0] + r2 * math.cos(ang + random.uniform(-0.2, 0.2)))
                y2 = int(ring_center[1] + r2 * math.sin(ang + random.uniform(-0.2, 0.2)))
                
                crack_alpha = int(220 * (1 - seg_t * 0.5))
                pygame.draw.line(ring_px, (200, 230, 255, crack_alpha), (x1, y1), (x2, y2), 2)
                pygame.draw.line(ring_px, (240, 250, 255, crack_alpha), (x1, y1), (x2, y2), 1)
                
                # Боковые ответвления трещин
                if seg % 2 == 0:
                    for side in [-1, 1]:
                        branch_ang = ang + side * 0.5
                        branch_len = int((r2 - r1) * 0.6)
                        bx = int(x2 + branch_len * math.cos(branch_ang))
                        by = int(y2 + branch_len * math.sin(branch_ang))
                        pygame.draw.line(ring_px, (210, 235, 255, crack_alpha // 2), (x2, y2), (bx, by), 1)
        
        # Ледяные кристаллы появляются вдоль трещин
        if t > 0.3:
            crystal_t = (t - 0.3) / 0.7
            for k in range(num_cracks * 2):
                ang = k * (math.pi/num_cracks) + crystal_t * 0.3
                r = int(expand_r * random.uniform(0.4, 0.9))
                x = int(ring_center[0] + r * math.cos(ang))
                y = int(ring_center[1] + r * math.sin(ang))
                
                # Рисуем кристалл (ромб)
                size = random.randint(3, 6)
                crystal_alpha = int(230 * (1 - crystal_t * 0.5))
                
                crystal_points = [
                    (x, y - size),
                    (x + size//2, y),
                    (x, y + size),
                    (x - size//2, y)
                ]
                pygame.draw.polygon(ring_px, (220, 240, 255, crystal_alpha), crystal_points)
                pygame.draw.polygon(ring_px, (240, 250, 255, crystal_alpha), crystal_points, 1)
        
        # Ледяные искры разлетаются от центра
        for k in range(20):
            spark_ang = k * (2*math.pi/20) + t * 2
            spark_r = int(15 + 40 * t + random.randint(-5, 5))
            spark_x = int(ring_center[0] + spark_r * math.cos(spark_ang))
            spark_y = int(ring_center[1] + spark_r * math.sin(spark_ang))
            spark_alpha = int(200 * (1 - t * 0.8))
            
            pygame.draw.circle(ring_px, (220, 240, 255, spark_alpha), (spark_x, spark_y), 2)
            pygame.draw.circle(ring_px, (240, 250, 255, spark_alpha), (spark_x, spark_y), 1)
        
        # Центральная ледяная вспышка
        core_alpha = int(220 * (1 - t))
        pygame.draw.circle(ring_px, (240, 250, 255, core_alpha), ring_center, int(12 * (1 - t * 0.7)))
        pygame.draw.circle(ring_px, (200, 230, 255, core_alpha), ring_center, int(18 * (1 - t * 0.5)))
        
        # Применяем поверх
        screen.blit(ring_px, (cx - CELL_SIZE*2, cy - CELL_SIZE*2))
        pygame.display.flip()
        pygame.time.delay(13)  # Ускорено для быстрых заклинаний

def animate_frost_impact(screen, center, redraw_callback=None):
    """Анимация морозного удара: ледяные шипы растут из земли и разбиваются"""
    cx, cy = center
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        t = i / (frames-1)
        splash = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        ox, oy = CELL_SIZE*1.5, CELL_SIZE*1.5
        # Фаза роста шипов (первые 60%)
        if i < int(frames * 0.6):
            grow = i / (frames * 0.6)
            for a in [k * (math.pi/4) for k in range(8)]:
                length = int(20 + 22 * grow)
                ex = int(ox + (CELL_SIZE-6) * math.cos(a))
                ey = int(oy + (CELL_SIZE-6) * math.sin(a))
                bx = int(ex - length * math.cos(a))
                by = int(ey - length * math.sin(a))
                left = (int(bx + 6 * math.cos(a + math.pi/2)), int(by + 6 * math.sin(a + math.pi/2)))
                right = (int(bx + 6 * math.cos(a - math.pi/2)), int(by + 6 * math.sin(a - math.pi/2)))
                tip = (ex, ey)
                color_body = (170, 220, 255, 230)
                color_edge = (210, 245, 255, 240)
                pygame.draw.polygon(splash, color_body, [left, right, tip])
                pygame.draw.polygon(splash, color_edge, [left, right, tip], 2)
        else:
            # Фаза разбивания (осколки разлетаются)
            break_t = (i - frames * 0.6) / (frames * 0.4)
            alpha = int(220 * (1 - break_t))
            for a in [k * (math.pi/4) for k in range(8)]:
                ex = int(ox + (CELL_SIZE-6) * math.cos(a))
                ey = int(oy + (CELL_SIZE-6) * math.sin(a))
                # 3 осколка от каждого шипа
                for k in range(3):
                    da = a + (k-1) * 0.25
                    r = int(6 + 10 * break_t)
                    px = int(ex + r * math.cos(da))
                    py = int(ey + r * math.sin(da))
                    pygame.draw.circle(splash, (200, 240, 255, alpha), (px, py), max(1, 3 - int(2*break_t)))
        screen.blit(splash, (cx - CELL_SIZE*1.5, cy - CELL_SIZE*1.5))
        pygame.display.flip()
        pygame.time.delay(10)  # Ускорено для быстрых заклинаний

def animate_forget_spell_fly(screen, start, end, redraw_callback=None):
    """Детализированная анимация полета заклинания Забвение"""
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 44  # Повышенная скорость
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    x, y = float(start[0]), float(start[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Двигаем снаряд с фиксированной скоростью
        x += step_x
        y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == frames - 1 or (abs(x - end[0]) < abs(step_x) and abs(y - end[1]) < abs(step_y)):
            x, y = end[0], end[1]
        
        t = i / max(1, frames - 1)  # Для анимации эффектов
        
        # Создаем летящий кристалл забвения с детализацией
        crystal_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        center_x, center_y = 15, 15
        
        # Внешний ореол
        pygame.draw.circle(crystal_surface, (80, 40, 100, 120), (center_x, center_y), 14)
        
        # Основной кристалл
        pygame.draw.circle(crystal_surface, (120, 60, 140), (center_x, center_y), 10)
        pygame.draw.circle(crystal_surface, (160, 100, 180), (center_x, center_y), 7)
        pygame.draw.circle(crystal_surface, (200, 140, 220), (center_x, center_y), 4)
        pygame.draw.circle(crystal_surface, (255, 200, 255), (center_x, center_y), 2)
        
        # Светящийся ореол
        pygame.draw.circle(crystal_surface, (140, 80, 160, 100), (center_x, center_y), 12)
        
        # Мистические частицы вокруг кристалла
        for j in range(6):
            angle = (i * 0.4 + j * 1.047) % (2 * math.pi)  # 60 градусов между частицами
            particle_x = center_x + int(10 * math.cos(angle))
            particle_y = center_y + int(10 * math.sin(angle))
            pygame.draw.circle(crystal_surface, (200, 160, 220, 150), 
                             (particle_x, particle_y), 2)
        
        # Дополнительные вращающиеся частицы
        for j in range(4):
            angle = (i * 0.6 + j * 1.57) % (2 * math.pi)  # 90 градусов между частицами
            particle_x = center_x + int(8 * math.cos(angle))
            particle_y = center_y + int(8 * math.sin(angle))
            pygame.draw.circle(crystal_surface, (220, 180, 255, 180), 
                             (particle_x, particle_y), 1)
        
        # Эффект пульсации
        pulse = int(3 * math.sin(i * 0.8))
        pygame.draw.circle(crystal_surface, (100, 60, 120, 80), 
                         (center_x, center_y), 16 + pulse)
        
        # Мистические руны
        for j in range(3):
            angle = j * 2.094 + i * 0.3  # 120 градусов между рунами
            rune_x = center_x + int(6 * math.cos(angle))
            rune_y = center_y + int(6 * math.sin(angle))
            pygame.draw.circle(crystal_surface, (180, 120, 200, 200), 
                             (rune_x, rune_y), 1)
        
        # Применяем кристалл к экрану
        screen.blit(crystal_surface, (int(x) - 15, int(y) - 15))
        
        pygame.display.flip()
        pygame.time.delay(5)  # Минимальная задержка для максимальной скорости

def animate_slow_spell(screen, start, end, redraw_callback=None):
    """Замедление: густые шипастые лозы с тенями оплетают цель"""
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 42  # Повышенная скорость
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    x, y = float(start[0]), float(start[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Двигаем снаряд с фиксированной скоростью
        x += step_x
        y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == frames - 1 or (abs(x - end[0]) < abs(step_x) and abs(y - end[1]) < abs(step_y)):
            x, y = end[0], end[1]
        
        t = i / max(1, frames - 1)  # Для анимации эффектов
        
        # Эффект замедления с корнями
        slow_surface = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*1.5, CELL_SIZE*1.5
        
        # Основной эффект замедления
        alpha = int(150 * (1 - abs(t - 0.5) * 2))
        
        # Земляной фон и падающая тень от лоз
        pygame.draw.circle(slow_surface, (70, 50, 30, alpha//2), (center_x+2, center_y+2), 32)
        pygame.draw.circle(slow_surface, (80, 60, 40, alpha//2), (center_x, center_y), 30)
        
        # Оплетающие шипастые корни
        for j in range(10):
            angle = j * math.pi / 4 + i * 0.2
            # Основной корень
            root_length = 22 + int(12 * math.sin(i * 0.3 + j))
            root_x = center_x + int(root_length * math.cos(angle))
            root_y = center_y + int(root_length * math.sin(angle))
            # Тень
            pygame.draw.line(slow_surface, (50, 35, 20, alpha//2), (center_x+2, center_y+2), (root_x+2, root_y+2), 5)
            # Рисуем корень с ветвлением
            pygame.draw.line(slow_surface, (60, 40, 20, alpha), (center_x, center_y), (root_x, root_y), 5)
            # Шипы на корне
            for s in range(2):
                spike_angle = angle + (s*2-1)*0.3
                spike_len = 6
                sx = root_x - int(8 * math.cos(angle))
                sy = root_y - int(8 * math.sin(angle))
                ex = sx + int(spike_len * math.cos(spike_angle))
                ey = sy + int(spike_len * math.sin(spike_angle))
                pygame.draw.line(slow_surface, (60, 40, 20, alpha), (sx, sy), (ex, ey), 3)
            # Ветви корня
            for k in range(2):
                branch_angle = angle + (k * 2 - 1) * 0.5
                branch_length = 8 + int(5 * math.sin(i * 0.4 + j + k))
                branch_x = root_x + int(branch_length * math.cos(branch_angle))
                branch_y = root_y + int(branch_length * math.sin(branch_angle))
                pygame.draw.line(slow_surface, (50, 30, 10, alpha), (root_x, root_y), (branch_x, branch_y), 3)
                
                # Мелкие отростки
                for l in range(2):
                    twig_angle = branch_angle + (l * 2 - 1) * 0.3
                    twig_length = 4 + int(3 * math.sin(i * 0.5 + j + k + l))
                    twig_x = branch_x + int(twig_length * math.cos(twig_angle))
                    twig_y = branch_y + int(twig_length * math.sin(twig_angle))
                    pygame.draw.line(slow_surface, (40, 20, 0, alpha), (branch_x, branch_y), (twig_x, twig_y), 2)
        
        # Дополнительные корни, появляющиеся постепенно
        for j in range(5):
            if i > j * 3:  # Появляются постепенно
                angle = j * math.pi / 2 + i * 0.15
                root_length = 15 + int(8 * math.sin(i * 0.25 + j))
                root_x = center_x + int(root_length * math.cos(angle))
                root_y = center_y + int(root_length * math.sin(angle))
                
                pygame.draw.line(slow_surface, (70, 50, 30, alpha), (center_x, center_y), (root_x, root_y), 4)
        
        # Эффект оцепенения (густой круг)
        pygame.draw.circle(slow_surface, (90, 70, 50, alpha//3), (center_x, center_y), 26)
        
        # Частицы земли
        for j in range(16):
            particle_x = center_x + random.randint(-20, 20)
            particle_y = center_y + random.randint(-20, 20)
            particle_alpha = int(alpha * 0.6)
            pygame.draw.circle(slow_surface, (90, 70, 50, particle_alpha), (particle_x, particle_y), 2)
        
        # Эффект пульсации корней
        pulse = int(5 * math.sin(i * 0.4))
        pygame.draw.circle(slow_surface, (60, 40, 20, alpha//4), (center_x, center_y), 30 + pulse)
        
        # Применяем эффект к экрану
        screen.blit(slow_surface, (x - CELL_SIZE*1.5, y - CELL_SIZE*1.5))
        
        pygame.display.flip()
        pygame.time.delay(6)  # Ускорено для быстрых заклинаний

def animate_slow_spell_fly(screen, start, end, redraw_callback=None):
    """Анимация полета заклинания Замедление"""
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 42  # Повышенная скорость
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    x, y = float(start[0]), float(start[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Двигаем снаряд с фиксированной скоростью
        x += step_x
        y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == frames - 1 or (abs(x - end[0]) < abs(step_x) and abs(y - end[1]) < abs(step_y)):
            x, y = end[0], end[1]
        
        t = i / max(1, frames - 1)  # Для анимации эффектов
        
        # Создаем летящий корень
        root_surface = pygame.Surface((25, 25), pygame.SRCALPHA)
        center_x, center_y = 12, 12
        
        # Основной корень
        pygame.draw.line(root_surface, (80, 60, 40), (center_x-8, center_y), (center_x+8, center_y), 4)
        
        # Ветви корня
        pygame.draw.line(root_surface, (70, 50, 30), (center_x-6, center_y-3), (center_x-2, center_y-6), 2)
        pygame.draw.line(root_surface, (70, 50, 30), (center_x+6, center_y-3), (center_x+2, center_y-6), 2)
        pygame.draw.line(root_surface, (70, 50, 30), (center_x-6, center_y+3), (center_x-2, center_y+6), 2)
        pygame.draw.line(root_surface, (70, 50, 30), (center_x+6, center_y+3), (center_x+2, center_y+6), 2)
        
        # Частицы земли
        for j in range(3):
            particle_x = center_x + random.randint(-8, 8)
            particle_y = center_y + random.randint(-8, 8)
            pygame.draw.circle(root_surface, (90, 70, 50, 150), 
                             (particle_x, particle_y), 1)
        
        # Применяем к экрану
        screen.blit(root_surface, (int(x) - 12, int(y) - 12))
        
        pygame.display.flip()
        pygame.time.delay(5)  # Минимальная задержка для максимальной скорости

def animate_bless_spell(screen, start, end, redraw_callback=None):
    """Новая анимация Благословения: святой символ, золотой столп света,
    материализация кубка на краткий миг, поток святой воды и финальная вспышка."""
    frames = 60  # Увеличено для плавности
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Фиксируем позицию на цели
        x = int(end[0])
        y = int(end[1])

        surf = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        cx, cy = CELL_SIZE*1.5, CELL_SIZE*1.5

        # 1) Святой символ на земле (круг, крест, орнамент), появляется и ярчеет
        sym_t = min(1.0, i / 8.0)
        sym_alpha = int(220 * sym_t)
        pygame.draw.circle(surf, (255, 230, 160, sym_alpha//3), (cx, cy), 32, 2)
        pygame.draw.circle(surf, (255, 240, 180, sym_alpha//2), (cx, cy), 22, 2)
        # крест
        pygame.draw.line(surf, (255, 255, 200, sym_alpha), (cx-10, cy), (cx+10, cy), 3)
        pygame.draw.line(surf, (255, 255, 200, sym_alpha), (cx, cy-10), (cx, cy+10), 3)
        # мелкие рунки по кругу
        for k in range(6):
            a = k * (2*math.pi/6) + i*0.1
            rx = int(cx + 16 * math.cos(a))
            ry = int(cy + 16 * math.sin(a))
            pygame.draw.circle(surf, (255, 240, 190, sym_alpha), (rx, ry), 2)

        # 2) Золотой столп света сверху, слегка пульсирует
        beam_t = min(1.0, max(0.0, (i-4)/6.0))
        beam_alpha = int(180 * beam_t)
        pygame.draw.rect(surf, (255, 240, 180, beam_alpha), (cx-10, cy-40, 20, 80))
        # мягкие края столпа
        pygame.draw.rect(surf, (255, 240, 180, max(0, beam_alpha//2)), (cx-14, cy-40, 4, 80))
        pygame.draw.rect(surf, (255, 240, 180, max(0, beam_alpha//2)), (cx+10, cy-40, 4, 80))

        # 3) Усиление столпа и символа в средней фазе (без кубка и воды)
        if 8 <= i <= 16:
            boost_t = (i-8) / 8.0
            boost_alpha = int(140 * (1.0 - abs(0.5 - boost_t) * 2))
            # дополнительное свечение столпа
            pygame.draw.rect(surf, (255, 245, 200, boost_alpha), (cx-12, cy-42, 24, 84), 0)
            # расширяющееся кольцо на символе
            ring_r = 16 + int(10 * boost_t)
            pygame.draw.circle(surf, (255, 245, 200, boost_alpha), (cx, cy), ring_r, 2)

        # 4) Золотые лучи и искры вокруг цели
        ray_alpha = int(180 * min(1.0, max(0.0, (i-6)/10.0)))
        for r in range(10):
            ang = r * (2*math.pi/10) + i*0.12
            rlen = 22 + int(6*math.sin(i*0.2 + r))
            rx = cx + int(rlen * math.cos(ang))
            ry = cy + int(rlen * math.sin(ang))
            pygame.draw.line(surf, (255, 235, 180, ray_alpha), (cx, cy), (rx, ry), 2)
        for s in range(14):
            ang = s * 0.45 + i*0.18
            rr = 16 + random.randint(-3, 5)
            sx = cx + int(rr * math.cos(ang))
            sy = cy + int(rr * math.sin(ang))
            pygame.draw.circle(surf, (255, 245, 200, ray_alpha), (sx, sy), 2)

        # 5) Финальная мягкая вспышка благодати (последние кадры)
        if i > frames-8:
            ft = (i-(frames-8))/8.0
            burst_alpha = int(220 * (1.0 - ft))
            pygame.draw.circle(surf, (255, 250, 210, burst_alpha), (cx, cy), 26 + int(10*ft))

        # Рендер на экран
        screen.blit(surf, (x - CELL_SIZE*1.5, y - CELL_SIZE*1.5))
        pygame.display.flip()
        pygame.time.delay(13)  # Ускорено для быстрых заклинаний

def animate_bless_spell_fly(screen, start, end, redraw_callback=None):
    """Анимация полета заклинания Благословение"""
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 45  # Повышенная скорость
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    x, y = float(start[0]), float(start[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Двигаем снаряд с фиксированной скоростью
        x += step_x
        y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == frames - 1 or (abs(x - end[0]) < abs(step_x) and abs(y - end[1]) < abs(step_y)):
            x, y = end[0], end[1]
        
        t = i / max(1, frames - 1)  # Для анимации эффектов
        
        # Создаем летящий кубок
        cup_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        center_x, center_y = 10, 10
        
        # Кубок
        pygame.draw.ellipse(cup_surface, (200, 200, 255), (center_x-6, center_y+2, 12, 8))
        pygame.draw.rect(cup_surface, (220, 220, 255), (center_x-4, center_y-6, 8, 8))
        pygame.draw.rect(cup_surface, (180, 180, 255), (center_x-4, center_y-6, 8, 2))
        
        # Светящиеся частицы вокруг кубка
        for j in range(4):
            angle = j * 1.57 + i * 0.5
            particle_x = center_x + int(8 * math.cos(angle))
            particle_y = center_y + int(8 * math.sin(angle))
            pygame.draw.circle(cup_surface, (255, 255, 200, 180), 
                             (particle_x, particle_y), 2)
        
        # Применяем к экрану
        screen.blit(cup_surface, (int(x) - 10, int(y) - 10))
        
        pygame.display.flip()
        pygame.time.delay(5)  # Минимальная задержка для максимальной скорости

def animate_dispel_spell(screen, start, end, redraw_callback=None):
    """Детальная анимация заклинания Снятие чар с расходящимися волнами"""
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames-1)
        x = int(start[0] * (1-t) + end[0] * t)
        y = int(start[1] * (1-t) + end[1] * t)
        
        # Создаем эффект снятия чар
        dispel_surface = pygame.Surface((CELL_SIZE*4, CELL_SIZE*4), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*2, CELL_SIZE*2
        
        # Основной эффект снятия чар
        alpha = int(220 * (1 - abs(t - 0.5) * 2))
        
        # Расходящиеся волны
        for wave in range(5):
            wave_radius = 10 + wave * 8 + int(5 * math.sin(i * 0.3 + wave))
            wave_alpha = int(alpha * (1 - wave * 0.2))
            pygame.draw.circle(dispel_surface, (80, 140, 255, min(255, wave_alpha+40)), 
                             (center_x, center_y), wave_radius, 3)
        
        # Дополнительные волны
        for wave in range(3):
            wave_radius = 15 + wave * 12 + int(8 * math.sin(i * 0.4 + wave))
            wave_alpha = int(alpha * 0.6 * (1 - wave * 0.3))
            pygame.draw.circle(dispel_surface, (140, 200, 255, min(255, int(wave_alpha*0.9)+30)), 
                             (center_x, center_y), wave_radius, 2)
        
        # Центральная вспышка
        flash_alpha = min(255, int(alpha * 1.5))
        pygame.draw.circle(dispel_surface, (230, 240, 255, flash_alpha), 
                         (center_x, center_y), 8)
        pygame.draw.circle(dispel_surface, (255, 255, 255, flash_alpha), 
                         (center_x, center_y), 4)
        
        # Частицы очищения
        for j in range(15):
            angle = j * 0.419 + i * 0.4  # вращение
            radius = 20 + random.randint(-8, 8)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = min(255, int(alpha * 0.95))
            pygame.draw.circle(dispel_surface, (180, 220, 255, particle_alpha), 
                             (particle_x, particle_y), 3)
        
        # Дополнительные светящиеся частицы
        for j in range(10):
            particle_x = center_x + random.randint(-25, 25)
            particle_y = center_y + random.randint(-25, 25)
            particle_alpha = min(255, int(alpha * 0.8))
            pygame.draw.circle(dispel_surface, (220, 240, 255, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Эффект пульсации волн
        pulse1 = int(6 * math.sin(i * 0.5))
        pulse2 = int(4 * math.sin(i * 0.7 + 1))
        pulse3 = int(3 * math.sin(i * 0.9 + 2))
        
        pygame.draw.circle(dispel_surface, (90, 150, 255, min(255, alpha//3 + 30)), 
                         (center_x, center_y), 30 + pulse1)
        pygame.draw.circle(dispel_surface, (120, 180, 255, min(255, alpha//4 + 20)), 
                         (center_x, center_y), 40 + pulse2)
        pygame.draw.circle(dispel_surface, (150, 200, 255, min(255, alpha//5 + 10)), 
                         (center_x, center_y), 50 + pulse3)
        
        # Световые лучи очищения
        for j in range(8):
            angle = j * math.pi / 4 + i * 0.3
            ray_length = 30 + int(8 * math.sin(i * 0.4 + j))
            ray_x = center_x + int(ray_length * math.cos(angle))
            ray_y = center_y + int(ray_length * math.sin(angle))
            pygame.draw.line(dispel_surface, (200, 230, 255, min(255, alpha//2 + 40)), 
                           (center_x, center_y), (ray_x, ray_y), 3)
        
        # Эффект искр очищения
        for j in range(12):
            spark_x = center_x + random.randint(-30, 30)
            spark_y = center_y + random.randint(-30, 30)
            spark_alpha = min(255, int(alpha * 0.9))
            pygame.draw.circle(dispel_surface, (255, 255, 255, spark_alpha), 
                             (spark_x, spark_y), 1)
        
        # Применяем эффект к экрану
        screen.blit(dispel_surface, (x - CELL_SIZE*2, y - CELL_SIZE*2))
        
        pygame.display.flip()
        pygame.time.delay(6)  # Ускорено для быстрых заклинаний

def animate_stone_skin(screen, target_pos, redraw_callback=None):
    """Плитки-кирпичики поднимаются снизу, собираются вокруг юнита и потом рассыпаются."""
    x, y = target_pos
    cx, cy = x, y
    frames = 60  # Увеличено для плавности
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        t = i / (frames - 1)
        layer = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        ox, oy = CELL_SIZE//2, CELL_SIZE//2
        # Фаза 1 (0..0.35): кирпичики поднимаются снизу
        if t <= 0.35:
            rise = t / 0.35
            tile_w, tile_h = 12, 8
            base_y = CELL_SIZE + int(20 * (1 - rise))
            for tx in range(0, CELL_SIZE+tile_w, tile_w):
                for ty in range(0, CELL_SIZE+tile_h, tile_h):
                    px = tx
                    py = ty + (CELL_SIZE - ty) * (1 - rise)
                    color = (122+random.randint(-4,4), 114+random.randint(-4,4), 106+random.randint(-4,4), int(160 + 80*rise))
                    pygame.draw.rect(layer, color, (px, py, tile_w-2, tile_h-2))
                    # шов
                    pygame.draw.rect(layer, (90,80,70, int(140*rise)), (px, py, tile_w-2, 1))
        # Фаза 2 (0.35..0.7): кирпичики стягиваются и обволакивают
        elif t <= 0.7:
            wrap = (t - 0.35) / 0.35
            tile_w, tile_h = 12, 8
            for tx in range(0, CELL_SIZE+tile_w, tile_w):
                for ty in range(0, CELL_SIZE+tile_h, tile_h):
                    # Смещение к центру
                    dirx = (ox - tx)
                    diry = (oy - ty)
                    px = int(tx + dirx * 0.4 * wrap)
                    py = int(ty + diry * 0.4 * wrap)
                    shade = 120 + int(20*wrap)
                    pygame.draw.rect(layer, (shade, shade-10, shade-20, 220), (px, py, tile_w-2, tile_h-2))
                    # Лёгкие трещины по мере стягивания
                    if random.random() < 0.2:
                        pygame.draw.line(layer, (80,70,60,200), (px, py), (px+tile_w-2, py+tile_h//2), 2)
        # Фаза 3 (0.7..1.0): растрескивание и осыпание
        else:
            crack_t = (t - 0.7) / 0.3
            alpha = int(220 * (1 - crack_t))
            # Кирпичные осколки разлетаются
            for k in range(40):
                ang = random.uniform(0, 2*math.pi)
                r = int(8 + 26 * crack_t)
                px = ox + int(r * math.cos(ang))
                py = oy + int(r * math.sin(ang))
                w = max(1, 3 - int(2*crack_t))
                pygame.draw.rect(layer, (140, 130, 120, alpha), (px, py, w, w))
        screen.blit(layer, (cx - CELL_SIZE//2, cy - CELL_SIZE//2))
        pygame.display.flip()
        pygame.time.delay(11)  # Ускорено для быстрых заклинаний

def animate_dispel_spell_fly(screen, start, end, redraw_callback=None):
    """Анимация полета заклинания Снятие чар"""
    # Фиксированная скорость полета независимо от расстояния (пикселей за кадр)
    PROJECTILE_SPEED = 44  # Повышенная скорость
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Рассчитываем количество кадров на основе расстояния и фиксированной скорости
    frames = max(1, int(distance / PROJECTILE_SPEED))
    
    # Нормализуем вектор направления
    if distance > 0:
        step_x = dx / distance * PROJECTILE_SPEED
        step_y = dy / distance * PROJECTILE_SPEED
    else:
        step_x = step_y = 0
    
    x, y = float(start[0]), float(start[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Двигаем снаряд с фиксированной скоростью
        x += step_x
        y += step_y
        
        # Проверяем, достигли ли мы цели
        if i == frames - 1 or (abs(x - end[0]) < abs(step_x) and abs(y - end[1]) < abs(step_y)):
            x, y = end[0], end[1]
        
        t = i / max(1, frames - 1)  # Для анимации эффектов
        
        # Создаем летящую волну очищения
        wave_surface = pygame.Surface((25, 25), pygame.SRCALPHA)
        center_x, center_y = 12, 12
        
        # Центральная вспышка
        pygame.draw.circle(wave_surface, (230, 240, 255), (center_x, center_y), 6)
        pygame.draw.circle(wave_surface, (255, 255, 255), (center_x, center_y), 3)
        
        # Волны вокруг центра
        for j in range(3):
            wave_radius = 4 + j * 2
            pygame.draw.circle(wave_surface, (180, 220, 255, 200), 
                             (center_x, center_y), wave_radius, 2)
        
        # Частицы очищения
        for j in range(6):
            angle = j * 1.047 + i * 0.5
            particle_x = center_x + int(8 * math.cos(angle))
            particle_y = center_y + int(8 * math.sin(angle))
            pygame.draw.circle(wave_surface, (220, 240, 255, 220), 
                             (particle_x, particle_y), 2)
        
        # Применяем к экрану
        screen.blit(wave_surface, (int(x) - 12, int(y) - 12))
        
        pygame.display.flip()
        pygame.time.delay(5)  # Минимальная задержка для максимальной скорости

# Улучшенная анимация: ускорение воздуха с детальными эффектами ветра
def animate_air_haste_spell(screen, start, end, redraw_callback=None):
    """Улучшенное ускорение с мощными потоками ветра и воздушными эффектами"""
    frames = 110  # Увеличено до 110 кадров для максимальной плавности
    tx, ty = end
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        t = i / (frames - 1)
        layer = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        cx, cy = CELL_SIZE*1.5, CELL_SIZE*1.5
        
        # Мощные вихри ветра, закручивающиеся вокруг цели
        for vortex in range(3):
            vortex_phase = t * 4 + vortex * (2 * math.pi / 3)
            vortex_r = int(30 + vortex * 8 + 8 * math.sin(vortex_phase))
            vortex_alpha = int(180 - vortex * 40)
            
            # Основной вихрь
            for arc_seg in range(6):
                arc_start = vortex_phase + arc_seg * (math.pi / 3)
                arc_end = arc_start + (math.pi / 4)
                pygame.draw.arc(layer, (180, 230, 255, vortex_alpha), 
                              (cx - vortex_r, cy - vortex_r, vortex_r * 2, vortex_r * 2),
                              arc_start, arc_end, 4)
                pygame.draw.arc(layer, (220, 245, 255, vortex_alpha), 
                              (cx - vortex_r + 2, cy - vortex_r + 2, vortex_r * 2 - 4, vortex_r * 2 - 4),
                              arc_start, arc_end, 2)
        
        # Быстрые линии потока ветра (более детализированные)
        for k in range(20):
            ang = 2 * math.pi * (k / 20.0) + t * 3.5
            r1 = int(CELL_SIZE * 0.7)
            r2 = r1 + 15 + int(10 * math.sin(t * 4 + k * 0.3))
            x1 = cx + int(r1 * math.cos(ang))
            y1 = cy + int(r1 * math.sin(ang))
            x2 = cx + int(r2 * math.cos(ang + 0.35))
            y2 = cy + int(r2 * math.sin(ang + 0.35))
            
            # Градиент линий
            stream_alpha = int(160 - abs(k % 10 - 5) * 15)
            pygame.draw.line(layer, (160, 215, 255, stream_alpha), (x1, y1), (x2, y2), 3)
            pygame.draw.line(layer, (200, 235, 255, stream_alpha), (x1, y1), (x2, y2), 1)
            
            # Искры ветра на концах линий
            pygame.draw.circle(layer, (220, 240, 255, stream_alpha), (x2, y2), 2)
        
        # Воздушные частицы, кружащиеся вокруг
        for particle in range(30):
            particle_ang = (particle * 2 * math.pi / 30) + t * 5
            particle_r = int(20 + 25 * math.sin(t * 2 + particle * 0.2))
            particle_x = cx + int(particle_r * math.cos(particle_ang))
            particle_y = cy + int(particle_r * math.sin(particle_ang))
            particle_alpha = int(200 * (0.7 + 0.3 * math.sin(t * 3 + particle)))
            
            pygame.draw.circle(layer, (200, 230, 255, particle_alpha), (particle_x, particle_y), 3)
            pygame.draw.circle(layer, (240, 250, 255, particle_alpha), (particle_x, particle_y), 2)
        
        # Пульсирующие кольца ускорения
        for ring in range(4):
            pulse_r = int(12 + ring * 6 + 8 * math.sin(t * 6 + ring * 0.5))
            ring_alpha = int(120 - ring * 25)
            pygame.draw.circle(layer, (180, 220, 255, ring_alpha), (cx, cy), pulse_r, 2)
        
        # Центральное яркое свечение
        core_alpha = int(180 * (0.6 + 0.4 * math.sin(t * 8)))
        pygame.draw.circle(layer, (220, 240, 255, core_alpha), (cx, cy), 8)
        pygame.draw.circle(layer, (240, 250, 255, core_alpha), (cx, cy), 5)
        
        # Спиральные потоки воздуха
        for spiral in range(2):
            spiral_dir = 1 if spiral == 0 else -1
            for j in range(15):
                spiral_t = j / 15.0
                spiral_ang = (spiral_t * 4 * math.pi + t * 6) * spiral_dir
                spiral_r = int(10 + spiral_t * 40)
                spiral_x = cx + int(spiral_r * math.cos(spiral_ang))
                spiral_y = cy + int(spiral_r * math.sin(spiral_ang))
                spiral_alpha = int(150 * (1 - spiral_t * 0.7))
                
                pygame.draw.circle(layer, (190, 225, 255, spiral_alpha), (spiral_x, spiral_y), 2)
        
        screen.blit(layer, (tx - CELL_SIZE*1.5, ty - CELL_SIZE*1.5))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний

def animate_rune_shield_spell(screen, start, end, redraw_callback=None):
    """Анимация руны защиты: насыщенный глиф над целью с мерцанием и исчезновением"""
    frames = 110  # Увеличено до 110 кадров для максимальной плавности
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Позиция над целью (чуть выше центра клетки цели), с ограничениями по экрану
        x = int(end[0])
        y = int(end[1] - CELL_SIZE * 0.7)
        top_margin = int(CELL_SIZE * 0.5)
        bottom_margin = int(CELL_SIZE * 0.5)
        ui_panel = 80  # высота нижней панели интерфейса
        y = max(top_margin, min(SCREEN_HEIGHT - ui_panel - bottom_margin, y))
        
        # Создаем эффект руны защиты
        rune_surface = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*1.5, CELL_SIZE*1.5
        
        # Основной эффект руны (фазы появления/мерцания/исчезновения)
        t = i / (frames-1)
        base_alpha = int(220 * (1 - abs(t - 0.5) * 2))
        base_alpha = max(0, min(255, base_alpha))
        flicker = 0.75 + 0.25 * (math.sin(i * 0.8) + 1) / 2  # мягкое мерцание 0.75..1.0
        alpha = int(base_alpha * flicker)
        
        # Фаза появления (первые 8 кадров)
        if i < 8:
            appear_alpha = int(alpha * (i / 8))
            
            # Многоуровневая аура (насыщенный сине-голубой щит)
            pygame.draw.circle(rune_surface, (60, 140, 255, appear_alpha//3), (center_x, center_y), 36)
            pygame.draw.circle(rune_surface, (80, 180, 255, appear_alpha//2), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (120, 210, 255, appear_alpha//1), (center_x, center_y), 24)

            # Внешнее свечение
            pygame.draw.circle(rune_surface, (140, 240, 255, appear_alpha//2), (center_x, center_y), 18)

            # Центральный камень (как в книге заклинаний для rune_shield)
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (80, 200, 80, appear_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (40, 100, 40, appear_alpha), stone_rect.inflate(-6, -6), 2)

            # Глиф: круг и крестообразные полосы с диагоналями
            pygame.draw.circle(rune_surface, (200, 255, 255, appear_alpha), (center_x, center_y), 16, 3)
            pygame.draw.line(rune_surface, (255, 255, 255, appear_alpha), (center_x-10, center_y), (center_x+10, center_y), 3)
            pygame.draw.line(rune_surface, (255, 255, 255, appear_alpha), (center_x, center_y-10), (center_x, center_y+10), 3)
            pygame.draw.line(rune_surface, (180, 255, 255, appear_alpha), (center_x-8, center_y-8), (center_x+8, center_y+8), 2)
            pygame.draw.line(rune_surface, (180, 255, 255, appear_alpha), (center_x-8, center_y+8), (center_x+8, center_y-8), 2)

            # Рунический знак щита как в книге (поверх камня)
            shield_points = [
                (center_x-6, center_y-6), (center_x+6, center_y-6), (center_x+8, center_y+4),
                (center_x, center_y+10), (center_x-8, center_y+4)
            ]
            pygame.draw.polygon(rune_surface, (60, 255, 120, appear_alpha), shield_points)
        
        # Фаза мерцания (кадры 8-17)
        elif i < 17:
            flicker_alpha = alpha

            # Многоуровневая аура (усиленная насыщенность)
            pygame.draw.circle(rune_surface, (60, 140, 255, flicker_alpha//4), (center_x, center_y), 38)
            pygame.draw.circle(rune_surface, (80, 180, 255, flicker_alpha//3), (center_x, center_y), 32)
            pygame.draw.circle(rune_surface, (120, 210, 255, flicker_alpha//2), (center_x, center_y), 26)

            # Пульсирующее свечение
            pulse = int(3 * math.sin(i * 0.9))
            pygame.draw.circle(rune_surface, (160, 255, 255, flicker_alpha//2), (center_x, center_y), 18 + pulse)

            # Центральный камень
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (80, 200, 80, flicker_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (40, 100, 40, flicker_alpha), stone_rect.inflate(-6, -6), 2)

            # Глиф: круг и крест с диагоналями (ярче)
            pygame.draw.circle(rune_surface, (220, 255, 255, flicker_alpha), (center_x, center_y), 16, 3)
            pygame.draw.line(rune_surface, (255, 255, 255, flicker_alpha), (center_x-10, center_y), (center_x+10, center_y), 3)
            pygame.draw.line(rune_surface, (255, 255, 255, flicker_alpha), (center_x, center_y-10), (center_x, center_y+10), 3)
            pygame.draw.line(rune_surface, (190, 255, 255, flicker_alpha), (center_x-8, center_y-8), (center_x+8, center_y+8), 2)
            pygame.draw.line(rune_surface, (190, 255, 255, flicker_alpha), (center_x-8, center_y+8), (center_x+8, center_y-8), 2)

            # Рунический знак щита
            shield_points = [
                (center_x-6, center_y-6), (center_x+6, center_y-6), (center_x+8, center_y+4),
                (center_x, center_y+10), (center_x-8, center_y+4)
            ]
            pygame.draw.polygon(rune_surface, (60, 255, 120, flicker_alpha), shield_points)

            # Вращающееся кольцо рун (малые точки-глифы)
            for j in range(6):
                a = j * (math.pi/3) + i * 0.15
                rx = center_x + int(12 * math.cos(a))
                ry = center_y + int(12 * math.sin(a))
                pygame.draw.circle(rune_surface, (200, 255, 255, flicker_alpha), (rx, ry), 2)
        
        # Фаза исчезновения (последние 8 кадров)
        else:
            # Безопасная затухающая прозрачность на последних кадрах
            tail = 8
            disappear_ratio = max(0.0, min(1.0, (frames - 1 - i) / tail))
            disappear_alpha = int(alpha * disappear_ratio)

            # Исчезающая аура и глиф
            pygame.draw.circle(rune_surface, (80, 180, 255, disappear_alpha//3), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (140, 240, 255, disappear_alpha//2), (center_x, center_y), 22)
            pygame.draw.circle(rune_surface, (220, 255, 255, disappear_alpha), (center_x, center_y), 16, 2)
            pygame.draw.line(rune_surface, (255, 255, 255, disappear_alpha), (center_x-10, center_y), (center_x+10, center_y), 2)
            pygame.draw.line(rune_surface, (255, 255, 255, disappear_alpha), (center_x, center_y-10), (center_x, center_y+10), 2)

            # Камень и знак при исчезновении
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (80, 200, 80, disappear_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (40, 100, 40, disappear_alpha), stone_rect.inflate(-6, -6), 2)
            shield_points = [
                (center_x-6, center_y-6), (center_x+6, center_y-6), (center_x+8, center_y+4),
                (center_x, center_y+10), (center_x-8, center_y+4)
            ]
            pygame.draw.polygon(rune_surface, (60, 255, 120, disappear_alpha), shield_points)
        
        # Эффект пульсации
        pulse = int(5 * math.sin(i * 0.5))
        pygame.draw.circle(rune_surface, (60, 150, 255, alpha//4), 
                         (center_x, center_y), 25 + pulse)
        
        # Частицы магии
        for j in range(8):
            angle = j * 0.785 + i * 0.3
            radius = 15 + random.randint(-5, 5)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.6)
            pygame.draw.circle(rune_surface, (160, 220, 255, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Применяем эффект к экрану
        screen.blit(rune_surface, (x - CELL_SIZE*1.5, y - CELL_SIZE*1.5))
        
        pygame.display.flip()
        pygame.time.delay(6)  # Ускорено для быстрых заклинаний

def animate_rune_haste_spell(screen, start, end, redraw_callback=None):
    """Анимация руны скорости: насыщенный глиф над целью с мерцанием и исчезновением"""
    frames = 110  # Увеличено до 110 кадров для максимальной плавности
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Позиция над целью (чуть выше центра клетки цели), с ограничениями по экрану
        x = int(end[0])
        y = int(end[1] - CELL_SIZE * 0.7)
        top_margin = int(CELL_SIZE * 0.5)
        bottom_margin = int(CELL_SIZE * 0.5)
        ui_panel = 80  # высота нижней панели интерфейса
        y = max(top_margin, min(SCREEN_HEIGHT - ui_panel - bottom_margin, y))
        
        # Создаем эффект руны скорости
        rune_surface = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*1.5, CELL_SIZE*1.5
        
        # Основной эффект руны (фазы появления/мерцания/исчезновения)
        t = i / (frames-1)
        base_alpha = int(220 * (1 - abs(t - 0.5) * 2))
        base_alpha = max(0, min(255, base_alpha))
        flicker = 0.75 + 0.25 * (math.sin(i * 0.9) + 1) / 2
        alpha = int(base_alpha * flicker)
        
        # Фаза появления (первые 8 кадров)
        if i < 8:
            appear_alpha = int(alpha * (i / 8))
            
            # Многоуровневая аура (насыщённый янтарно-золотой)
            pygame.draw.circle(rune_surface, (255, 150, 60, appear_alpha//3), (center_x, center_y), 36)
            pygame.draw.circle(rune_surface, (255, 180, 80, appear_alpha//2), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (255, 210, 110, appear_alpha//1), (center_x, center_y), 24)

            # Внешнее свечение
            pygame.draw.circle(rune_surface, (255, 240, 160, appear_alpha//2), (center_x, center_y), 18)

            # Центральный камень (как в книге заклинаний для rune_haste)
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (200, 200, 200, appear_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (120, 120, 120, appear_alpha), stone_rect.inflate(-6, -6), 2)

            # Глиф скорости: круг + стрелы/усики ускорения
            pygame.draw.circle(rune_surface, (255, 255, 220, appear_alpha), (center_x, center_y), 16, 3)
            pygame.draw.line(rune_surface, (255, 255, 255, appear_alpha), (center_x-10, center_y-5), (center_x+10, center_y-5), 3)
            pygame.draw.line(rune_surface, (255, 255, 255, appear_alpha), (center_x-8, center_y), (center_x+8, center_y), 2)
            pygame.draw.line(rune_surface, (255, 255, 255, appear_alpha), (center_x-6, center_y+5), (center_x+6, center_y+5), 2)
            # косые штрихи-ускорители
            pygame.draw.line(rune_surface, (255, 255, 220, appear_alpha), (center_x-7, center_y-9), (center_x-1, center_y-13), 2)
            pygame.draw.line(rune_surface, (255, 255, 220, appear_alpha), (center_x+7, center_y+9), (center_x+1, center_y+13), 2)

            # Молния как в книге (поверх камня)
            bolt_points = [
                (center_x-5, center_y-4), (center_x, center_y+2), (center_x-2, center_y+2), (center_x+5, center_y+10)
            ]
            pygame.draw.lines(rune_surface, (255, 255, 255, appear_alpha), False, bolt_points, 3)
        
        # Фаза мерцания (кадры 8-17)
        elif i < 17:
            flicker_alpha = alpha

            # Многоуровневая аура (усиленная насыщенность)
            pygame.draw.circle(rune_surface, (255, 150, 60, flicker_alpha//4), (center_x, center_y), 38)
            pygame.draw.circle(rune_surface, (255, 180, 80, flicker_alpha//3), (center_x, center_y), 32)
            pygame.draw.circle(rune_surface, (255, 210, 110, flicker_alpha//2), (center_x, center_y), 26)

            # Пульсирующее свечение
            pulse = int(3 * math.sin(i * 1.0))
            pygame.draw.circle(rune_surface, (255, 240, 160, flicker_alpha//2), (center_x, center_y), 18 + pulse)

            # Центральный камень
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (200, 200, 200, flicker_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (120, 120, 120, flicker_alpha), stone_rect.inflate(-6, -6), 2)

            # Глиф скорости (ярче) + ускорители
            pygame.draw.circle(rune_surface, (255, 255, 220, flicker_alpha), (center_x, center_y), 16, 3)
            pygame.draw.line(rune_surface, (255, 255, 255, flicker_alpha), (center_x-10, center_y-5), (center_x+10, center_y-5), 3)
            pygame.draw.line(rune_surface, (255, 255, 255, flicker_alpha), (center_x-8, center_y), (center_x+8, center_y), 2)
            pygame.draw.line(rune_surface, (255, 255, 255, flicker_alpha), (center_x-6, center_y+5), (center_x+6, center_y+5), 2)
            pygame.draw.line(rune_surface, (255, 255, 220, flicker_alpha), (center_x-7, center_y-9), (center_x-1, center_y-13), 2)
            pygame.draw.line(rune_surface, (255, 255, 220, flicker_alpha), (center_x+7, center_y+9), (center_x+1, center_y+13), 2)

            # Вращающееся кольцо точечных глифов
            for j in range(6):
                a = j * (math.pi/3) + i * 0.18
                rx = center_x + int(12 * math.cos(a))
                ry = center_y + int(12 * math.sin(a))
                pygame.draw.circle(rune_surface, (255, 230, 160, flicker_alpha), (rx, ry), 2)

            # Молния как в книге
            bolt_points = [
                (center_x-5, center_y-4), (center_x, center_y+2), (center_x-2, center_y+2), (center_x+5, center_y+10)
            ]
            pygame.draw.lines(rune_surface, (255, 255, 255, flicker_alpha), False, bolt_points, 3)
        
        # Фаза исчезновения (последние 8 кадров)
        else:
            # Безопасная затухающая прозрачность на последних кадрах
            tail = 8
            disappear_ratio = max(0.0, min(1.0, (frames - 1 - i) / tail))
            disappear_alpha = int(alpha * disappear_ratio)

            # Исчезающая аура и глиф
            pygame.draw.circle(rune_surface, (255, 180, 80, disappear_alpha//3), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (255, 210, 110, disappear_alpha//2), (center_x, center_y), 22)
            pygame.draw.circle(rune_surface, (255, 255, 220, disappear_alpha), (center_x, center_y), 16, 2)
            pygame.draw.line(rune_surface, (255, 255, 255, disappear_alpha), (center_x-10, center_y-5), (center_x+10, center_y-5), 2)
            pygame.draw.line(rune_surface, (255, 255, 255, disappear_alpha), (center_x-8, center_y), (center_x+8, center_y), 2)

            # Камень и молния при исчезновении
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (200, 200, 200, disappear_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (120, 120, 120, disappear_alpha), stone_rect.inflate(-6, -6), 2)
            bolt_points = [
                (center_x-5, center_y-4), (center_x, center_y+2), (center_x-2, center_y+2), (center_x+5, center_y+10)
            ]
            pygame.draw.lines(rune_surface, (255, 255, 255, disappear_alpha), False, bolt_points, 3)
        
        # Эффект пульсации
        pulse = int(5 * math.sin(i * 0.5))
        pygame.draw.circle(rune_surface, (255, 170, 70, alpha//4), 
                         (center_x, center_y), 25 + pulse)
        
        # Частицы скорости
        for j in range(8):
            angle = j * 0.785 + i * 0.4
            radius = 15 + random.randint(-5, 5)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.6)
            pygame.draw.circle(rune_surface, (255, 230, 160, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Применяем эффект к экрану
        screen.blit(rune_surface, (x - CELL_SIZE*1.5, y - CELL_SIZE*1.5))
        
        pygame.display.flip()
        pygame.time.delay(6)  # Ускорено для быстрых заклинаний

def animate_rune_magic_spell(screen, start, end, redraw_callback=None):
    """Анимация руны магии: фиолетовый магический глиф над целью"""
    import random
    import math
    from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 110  # Увеличено до 110 кадров для максимальной плавности
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Позиция над целью
        x = int(end[0])
        y = int(end[1] - CELL_SIZE * 0.7)
        top_margin = int(CELL_SIZE * 0.5)
        bottom_margin = int(CELL_SIZE * 0.5)
        ui_panel = 80
        y = max(top_margin, min(SCREEN_HEIGHT - ui_panel - bottom_margin, y))
        
        # Создаем эффект руны магии
        rune_surface = pygame.Surface((CELL_SIZE*3, CELL_SIZE*3), pygame.SRCALPHA)
        center_x, center_y = CELL_SIZE*1.5, CELL_SIZE*1.5
        
        # Основной эффект руны
        t = i / (frames-1)
        base_alpha = int(220 * (1 - abs(t - 0.5) * 2))
        base_alpha = max(0, min(255, base_alpha))
        flicker = 0.75 + 0.25 * (math.sin(i * 0.8) + 1) / 2
        alpha = int(base_alpha * flicker)
        
        # Фаза появления (первые 8 кадров)
        if i < 8:
            appear_alpha = int(alpha * (i / 8))
            
            # Многоуровневая аура (фиолетово-магическая)
            pygame.draw.circle(rune_surface, (180, 100, 255, appear_alpha//3), (center_x, center_y), 36)
            pygame.draw.circle(rune_surface, (200, 120, 255, appear_alpha//2), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (220, 140, 255, appear_alpha//1), (center_x, center_y), 24)
            
            # Внешнее свечение
            pygame.draw.circle(rune_surface, (240, 160, 255, appear_alpha//2), (center_x, center_y), 18)
            
            # Центральный камень
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (160, 100, 200, appear_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (120, 60, 150, appear_alpha), stone_rect.inflate(-6, -6), 2)
            
            # Глиф магии: круг с магическими символами
            pygame.draw.circle(rune_surface, (255, 200, 255, appear_alpha), (center_x, center_y), 16, 3)
            # Звездочка магии
            for j in range(8):
                angle = j * (math.pi / 4)
                px = center_x + int(10 * math.cos(angle))
                py = center_y + int(10 * math.sin(angle))
                pygame.draw.circle(rune_surface, (255, 255, 255, appear_alpha), (px, py), 2)
        
        # Фаза мерцания (кадры 8-17)
        elif i < 17:
            flicker_alpha = alpha
            
            # Многоуровневая аура
            pygame.draw.circle(rune_surface, (180, 100, 255, flicker_alpha//4), (center_x, center_y), 38)
            pygame.draw.circle(rune_surface, (200, 120, 255, flicker_alpha//3), (center_x, center_y), 32)
            pygame.draw.circle(rune_surface, (220, 140, 255, flicker_alpha//2), (center_x, center_y), 26)
            
            # Пульсирующее свечение
            pulse = int(3 * math.sin(i * 0.9))
            pygame.draw.circle(rune_surface, (240, 160, 255, flicker_alpha//2), (center_x, center_y), 18 + pulse)
            
            # Центральный камень
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (160, 100, 200, flicker_alpha), stone_rect)
            pygame.draw.ellipse(rune_surface, (120, 60, 150, flicker_alpha), stone_rect.inflate(-6, -6), 2)
            
            # Глиф магии (ярче)
            pygame.draw.circle(rune_surface, (255, 220, 255, flicker_alpha), (center_x, center_y), 16, 3)
            # Вращающаяся звездочка магии
            for j in range(8):
                angle = j * (math.pi / 4) + i * 0.15
                px = center_x + int(10 * math.cos(angle))
                py = center_y + int(10 * math.sin(angle))
                pygame.draw.circle(rune_surface, (255, 255, 255, flicker_alpha), (px, py), 2)
            
            # Вращающееся кольцо рун
            for j in range(6):
                a = j * (math.pi/3) + i * 0.15
                rx = center_x + int(12 * math.cos(a))
                ry = center_y + int(12 * math.sin(a))
                pygame.draw.circle(rune_surface, (255, 200, 255, flicker_alpha), (rx, ry), 2)
        
        # Фаза исчезновения (последние 8 кадров)
        else:
            tail = 8
            disappear_ratio = max(0.0, min(1.0, (frames - 1 - i) / tail))
            disappear_alpha = int(alpha * disappear_ratio)
            
            # Исчезающая аура и глиф
            pygame.draw.circle(rune_surface, (200, 120, 255, disappear_alpha//3), (center_x, center_y), 30)
            pygame.draw.circle(rune_surface, (220, 140, 255, disappear_alpha//2), (center_x, center_y), 22)
            pygame.draw.circle(rune_surface, (255, 200, 255, disappear_alpha), (center_x, center_y), 16, 2)
            
            # Камень и звездочка при исчезновении
            stone_rect = pygame.Rect(0, 0, 22, 16)
            stone_rect.center = (center_x, center_y)
            pygame.draw.ellipse(rune_surface, (160, 100, 200, disappear_alpha), stone_rect)
            for j in range(8):
                angle = j * (math.pi / 4)
                px = center_x + int(10 * math.cos(angle))
                py = center_y + int(10 * math.sin(angle))
                pygame.draw.circle(rune_surface, (255, 255, 255, disappear_alpha), (px, py), 2)
        
        # Эффект пульсации
        pulse = int(5 * math.sin(i * 0.5))
        pygame.draw.circle(rune_surface, (200, 120, 255, alpha//4), 
                         (center_x, center_y), 25 + pulse)
        
        # Частицы магии
        for j in range(8):
            angle = j * 0.785 + i * 0.3
            radius = 15 + random.randint(-5, 5)
            particle_x = center_x + int(radius * math.cos(angle))
            particle_y = center_y + int(radius * math.sin(angle))
            particle_alpha = int(alpha * 0.6)
            pygame.draw.circle(rune_surface, (240, 160, 255, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Применяем эффект к экрану
        screen.blit(rune_surface, (x - CELL_SIZE*1.5, y - CELL_SIZE*1.5))
        
        pygame.display.flip()
        pygame.time.delay(6)  # Ускорено для быстрых заклинаний

def animate_rune_berserker_spell(screen, start, end, redraw_callback=None):
    """Простая анимация руны берсерка: красное свечение прямо на юните (без полета снаряда)"""
    import random
    import math
    from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
    
    # Игнорируем start - анимация проигрывается сразу на цели (end)
    frames = 90  # Увеличено до 90 кадров для максимальной плавности
    cx, cy = int(end[0]), int(end[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Создаем поверхность для эффекта
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Плавное появление и исчезновение
        t = i / (frames - 1)
        if t < 0.3:
            alpha = int(255 * (t / 0.3))
        elif t > 0.7:
            alpha = int(255 * ((1 - t) / 0.3))
        else:
            alpha = 255
        
        # Пульсирующее красное свечение вокруг юнита
        pulse = int(5 * math.sin(i * 0.8))
        radius = 20 + pulse
        
        # Внешнее свечение
        pygame.draw.circle(overlay, (255, 60, 60, alpha // 3), (cx, cy), radius + 8)
        # Среднее свечение
        pygame.draw.circle(overlay, (255, 80, 40, alpha // 2), (cx, cy), radius + 4)
        # Внутреннее яркое свечение
        pygame.draw.circle(overlay, (255, 100, 20, alpha), (cx, cy), radius)
        
        # Вращающиеся частицы ярости
        for j in range(6):
            angle = j * (math.pi / 3) + i * 0.5
            px = cx + int(radius * 0.6 * math.cos(angle))
            py = cy + int(radius * 0.6 * math.sin(angle))
            pygame.draw.circle(overlay, (255, 150, 50, alpha), (px, py), 3)
        
        # Применяем эффект к экрану
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний

def animate_luck_horseshoe(screen, unit_pos, redraw_callback=None):
    """Анимация подковы при срабатывании удачи - подкова крутится по вертикальной оси над юнитом"""
    import math
    from .config import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 30
    cx, cy = int(unit_pos[0]), int(unit_pos[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Создаем поверхность для эффекта
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Плавное появление и исчезновение
        t = i / (frames - 1)
        if t < 0.2:
            alpha = int(255 * (t / 0.2))
        elif t > 0.7:
            alpha = int(255 * ((1 - t) / 0.3))
        else:
            alpha = 255
        
        # Позиция подковы над юнитом (выше на 30-50 пикселей)
        horseshoe_y = cy - 40 - int(10 * math.sin(i * 0.3))  # Небольшое покачивание вверх-вниз
        horseshoe_x = cx
        
        # Вращение подковы по вертикальной оси (от 0 до 360 градусов)
        rotation_angle = (i * 360 / frames) * (math.pi / 180)  # В радианах
        
        # Размер подковы
        horseshoe_size = 40
        horseshoe_thickness = 4
        
        # Рисуем подкову (форма подковы с вращением)
        # Подкова состоит из дуги и двух "ножек"
        # При вращении по вертикальной оси она выглядит как эллипс, который меняет ширину
        
        # Вычисляем ширину эллипса в зависимости от угла вращения
        # Когда подкова повернута на 90 градусов - она видна сбоку (узкая)
        # Когда на 0/180 градусов - видна спереди (широкая)
        ellipse_width = int(horseshoe_size * abs(math.cos(rotation_angle)))
        ellipse_height = horseshoe_size
        
        # Цвет подковы (золотой/бронзовый)
        horseshoe_color = (255, 215, 0, alpha)  # Золотой
        glow_color = (255, 255, 200, alpha // 2)  # Свечение
        
        # Внешнее свечение
        pygame.draw.ellipse(overlay, glow_color, 
                          (horseshoe_x - ellipse_width//2 - 5, horseshoe_y - ellipse_height//2 - 5,
                           ellipse_width + 10, ellipse_height + 10), 2)
        
        # Основная подкова (дуга сверху)
        if ellipse_width > 5:  # Рисуем только если подкова видна
            # Верхняя дуга подковы
            pygame.draw.arc(overlay, horseshoe_color,
                          (horseshoe_x - ellipse_width//2, horseshoe_y - ellipse_height//2,
                           ellipse_width, ellipse_height),
                          math.pi * 0.2, math.pi * 0.8, horseshoe_thickness)
            
            # Левая "ножка" подковы
            left_leg_x = horseshoe_x - ellipse_width//2
            left_leg_y1 = horseshoe_y + int(ellipse_height * 0.3)
            left_leg_y2 = horseshoe_y + int(ellipse_height * 0.6)
            pygame.draw.line(overlay, horseshoe_color,
                           (left_leg_x, left_leg_y1), (left_leg_x, left_leg_y2), horseshoe_thickness)
            
            # Правая "ножка" подковы
            right_leg_x = horseshoe_x + ellipse_width//2
            right_leg_y1 = horseshoe_y + int(ellipse_height * 0.3)
            right_leg_y2 = horseshoe_y + int(ellipse_height * 0.6)
            pygame.draw.line(overlay, horseshoe_color,
                           (right_leg_x, right_leg_y1), (right_leg_x, right_leg_y2), horseshoe_thickness)
        
        # Звездочки удачи вокруг подковы
        for star_idx in range(6):
            star_angle = (star_idx * 2 * math.pi / 6) + i * 0.3
            star_radius = 25
            star_x = cx + int(star_radius * math.cos(star_angle))
            star_y = cy - 40 + int(star_radius * 0.5 * math.sin(star_angle))
            star_alpha = int(alpha * (0.6 + 0.4 * math.sin(i * 0.5 + star_idx)))
            pygame.draw.circle(overlay, (255, 255, 200, star_alpha), (star_x, star_y), 3)
        
        # Применяем эффект к экрану
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Ускорено для быстрых заклинаний

def animate_combat_spirit_bird(screen, unit_pos, redraw_callback=None):
    """Анимация золотой птицы при срабатывании боевого духа - птица поднимает крылья"""
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = int(unit_pos[0]), int(unit_pos[1])
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        # Создаем поверхность для эффекта
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Плавное появление и исчезновение
        t = i / (frames - 1)
        if t < 0.15:
            alpha = int(255 * (t / 0.15))
        elif t > 0.75:
            alpha = int(255 * ((1 - t) / 0.25))
        else:
            alpha = 255
        
        # Позиция птицы над юнитом (выше на 50-60 пикселей)
        bird_y = cy - 55 - int(8 * math.sin(i * 0.2))  # Покачивание вверх-вниз
        bird_x = cx
        
        # Анимация крыльев: от поднятых (0) до опущенных (1) и обратно
        wing_cycle = (i % 20) / 20.0  # Цикл каждые 20 кадров
        if wing_cycle < 0.5:
            # Крылья поднимаются (0 -> 0.5)
            wing_angle = math.pi * (1 - wing_cycle * 2)  # От π до 0
        else:
            # Крылья опускаются (0.5 -> 1.0)
            wing_angle = math.pi * ((wing_cycle - 0.5) * 2)  # От 0 до π
        
        # Размер птицы
        bird_size = 35
        body_size = 12
        
        # Цвета (золотой)
        bird_color = (255, 215, 0, alpha)  # Золотой
        glow_color = (255, 255, 180, alpha // 3)  # Свечение
        body_color = (255, 200, 50, alpha)  # Более темное золото для тела
        
        # Внешнее свечение
        glow_radius = bird_size + 8
        pygame.draw.circle(overlay, glow_color, (bird_x, bird_y), glow_radius)
        
        # Тело птицы (эллипс)
        body_rect = pygame.Rect(bird_x - body_size//2, bird_y - body_size//2, 
                               body_size, body_size)
        pygame.draw.ellipse(overlay, body_color, body_rect)
        
        # Голова птицы (маленький круг)
        head_radius = 5
        head_x = bird_x + body_size // 3
        head_y = bird_y - body_size // 3
        pygame.draw.circle(overlay, body_color, (head_x, head_y), head_radius)
        
        # Клюв (маленький треугольник)
        beak_points = [
            (head_x + head_radius, head_y),
            (head_x + head_radius + 4, head_y - 2),
            (head_x + head_radius + 4, head_y + 2)
        ]
        pygame.draw.polygon(overlay, (255, 180, 0, alpha), beak_points)
        
        # Крылья (поднимаются и опускаются)
        wing_length = 18
        wing_width = 8
        
        # Левое крыло
        left_wing_base_x = bird_x - body_size // 2
        left_wing_base_y = bird_y
        left_wing_end_x = left_wing_base_x + int(wing_length * math.cos(wing_angle))
        left_wing_end_y = left_wing_base_y - int(wing_length * math.sin(wing_angle))
        # Рисуем крыло как эллипс
        left_wing_center_x = (left_wing_base_x + left_wing_end_x) // 2
        left_wing_center_y = (left_wing_base_y + left_wing_end_y) // 2
        wing_rect = pygame.Rect(left_wing_center_x - wing_width//2, 
                               left_wing_center_y - wing_length//2,
                               wing_width, wing_length)
        # Поворачиваем крыло (упрощенная версия - просто рисуем линию с расширением)
        pygame.draw.line(overlay, bird_color, 
                        (left_wing_base_x, left_wing_base_y),
                        (left_wing_end_x, left_wing_end_y), 6)
        
        # Правое крыло
        right_wing_base_x = bird_x + body_size // 2
        right_wing_base_y = bird_y
        right_wing_end_x = right_wing_base_x - int(wing_length * math.cos(wing_angle))
        right_wing_end_y = right_wing_base_y - int(wing_length * math.sin(wing_angle))
        pygame.draw.line(overlay, bird_color,
                        (right_wing_base_x, right_wing_base_y),
                        (right_wing_end_x, right_wing_end_y), 6)
        
        # Хвост (небольшой веер)
        tail_base_x = bird_x - body_size // 2
        tail_base_y = bird_y + body_size // 2
        for tail_idx in range(3):
            tail_angle = math.pi * 0.3 + tail_idx * 0.2
            tail_length = 10
            tail_end_x = tail_base_x - int(tail_length * math.cos(tail_angle))
            tail_end_y = tail_base_y + int(tail_length * math.sin(tail_angle))
            pygame.draw.line(overlay, bird_color,
                           (tail_base_x, tail_base_y),
                           (tail_end_x, tail_end_y), 3)
        
        # Золотые частицы вокруг птицы
        for particle_idx in range(8):
            particle_angle = (particle_idx * 2 * math.pi / 8) + i * 0.4
            particle_radius = 30 + int(10 * math.sin(i * 0.3 + particle_idx))
            particle_x = cx + int(particle_radius * math.cos(particle_angle))
            particle_y = cy - 55 + int(particle_radius * 0.6 * math.sin(particle_angle))
            particle_alpha = int(alpha * (0.5 + 0.5 * math.sin(i * 0.4 + particle_idx)))
            pygame.draw.circle(overlay, (255, 255, 150, particle_alpha), 
                             (particle_x, particle_y), 2)
        
        # Применяем эффект к экрану
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний

def animate_spell_reflection(screen, target_px, caster_px, redraw_callback=None):
    """Анимация предотвращения заклинания - поток маны прилетает к щиту рядом с юнитом и отталкивается"""
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = target_px
    
    # Определяем позицию щита рядом с юнитом (не в центр юнита)
    # Если есть кастер, щит будет на стороне от кастера
    if caster_px:
        # Вычисляем направление от кастера к цели
        dx = cx - caster_px[0]
        dy = cy - caster_px[1]
        dist = math.sqrt(dx*dx + dy*dy) if (dx*dx + dy*dy) > 0 else 1
        # Позиция щита рядом с юнитом, на пути от кастера
        shield_offset = 25  # Смещение от центра юнита
        shield_x = cx - int((dx / dist) * shield_offset)
        shield_y = cy - int((dy / dist) * shield_offset)
    else:
        # Если кастера нет, щит справа от юнита
        shield_x = cx + 20
        shield_y = cy
    
    # Позиция, откуда прилетает поток маны (дальше от кастера, если есть)
    if caster_px:
        # Поток маны прилетает с направления кастера, но к позиции рядом с юнитом
        start_offset = 60
        start_x = shield_x - int((dx / dist) * start_offset) if dist > 0 else shield_x - start_offset
        start_y = shield_y - int((dy / dist) * start_offset) if dist > 0 else shield_y
    else:
        start_x = shield_x - 50
        start_y = shield_y
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        
        # Щит появляется и растёт (рядом с юнитом)
        if t < 0.3:
            shield_alpha = int(220 * (t / 0.3))
            shield_size = int(25 * (t / 0.3))
        else:
            shield_alpha = 220
            shield_size = 25
        
        # Рисуем щит рядом с юнитом (круг с магическим свечением)
        pygame.draw.circle(overlay, (150, 200, 255, shield_alpha), (shield_x, shield_y), shield_size)
        pygame.draw.circle(overlay, (200, 230, 255, int(shield_alpha*0.8)), (shield_x, shield_y), shield_size + 4, 2)
        pygame.draw.circle(overlay, (100, 150, 255, int(shield_alpha*0.6)), (shield_x, shield_y), shield_size + 8, 2)
        
        # Поток маны летит к щиту
        if t < 0.5:
            mana_t = t / 0.5
            mana_x = int(start_x * (1 - mana_t) + shield_x * mana_t)
            mana_y = int(start_y * (1 - mana_t) + shield_y * mana_t)
            
            # Магический поток (не шар, а поток энергии)
            for j in range(4):
                mana_size = 10 - j * 2
                mana_alpha = int(200 * (1 - j * 0.2) * (1 - mana_t * 0.3))
                pygame.draw.circle(overlay, (100, 150, 255, mana_alpha), (mana_x, mana_y), mana_size)
            
            # След потока маны
            for k in range(6):
                trail_t = mana_t - k * 0.08
                if trail_t > 0:
                    trail_x = int(start_x * (1 - trail_t) + shield_x * trail_t)
                    trail_y = int(start_y * (1 - trail_t) + shield_y * trail_t)
                    trail_alpha = int(120 * (1 - trail_t))
                    trail_size = 6 - k
                    if trail_size > 0:
                        pygame.draw.circle(overlay, (150, 200, 255, trail_alpha), (trail_x, trail_y), trail_size)
        
        # Поток отталкивается от щита (рассеивается в стороны)
        if t > 0.5:
            bounce_t = (t - 0.5) / 0.5
            # Вычисляем направление от кастера для определения угла отскока
            if caster_px:
                angle_to_caster = math.atan2(dy, dx) if dist > 0 else 0
            else:
                angle_to_caster = 0
            
            # Поток рассеивается в стороны от щита
            for particle_idx in range(8):
                # Частицы разлетаются в разные стороны
                particle_angle = (particle_idx * (2*math.pi / 8.0)) + angle_to_caster + math.pi/2
                particle_dist = int(30 * bounce_t)
                particle_x = shield_x + int(particle_dist * math.cos(particle_angle))
                particle_y = shield_y + int(particle_dist * math.sin(particle_angle))
                
                particle_size = int(6 * (1 - bounce_t))
                particle_alpha = int(180 * (1 - bounce_t))
                if particle_size > 0:
                    pygame.draw.circle(overlay, (150, 200, 255, particle_alpha), (particle_x, particle_y), particle_size)
                    pygame.draw.circle(overlay, (200, 230, 255, int(particle_alpha*0.7)), (particle_x, particle_y), particle_size + 2, 1)
        
        # Искры при столкновении со щитом
        if 0.45 < t < 0.7:
            spark_t = (t - 0.45) / 0.25
            for spark_idx in range(16):
                spark_angle = (spark_idx * (2*math.pi / 16.0)) + random.uniform(-0.3, 0.3)
                spark_dist = int(25 * spark_t)
                spark_x = shield_x + int(spark_dist * math.cos(spark_angle))
                spark_y = shield_y + int(spark_dist * math.sin(spark_angle))
                spark_alpha = int(220 * (1 - spark_t))
                spark_size = random.randint(2, 4)
                pygame.draw.circle(overlay, (255, 255, 255, spark_alpha), (spark_x, spark_y), spark_size)
                pygame.draw.circle(overlay, (200, 230, 255, int(spark_alpha*0.8)), (spark_x, spark_y), spark_size + 1, 1)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Ускорено для быстрых заклинаний

def animate_quicksand_cast(screen, center_px, redraw_callback=None):
    """Анимация каста зыбучих песков - земля трясётся, появляются трещины"""
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 90  # Увеличено до 90 кадров для максимальной плавности
    cx, cy = center_px
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        
        # Земля трясётся
        shake_intensity = int(3 * (1 - t))
        shake_x = random.randint(-shake_intensity, shake_intensity) if shake_intensity > 0 else 0
        shake_y = random.randint(-shake_intensity, shake_intensity) if shake_intensity > 0 else 0
        
        # Трещины появляются
        for crack_idx in range(8):
            crack_angle = (crack_idx * (2*math.pi / 8.0))
            crack_length = int(30 * t)
            crack_start_x = cx + shake_x
            crack_start_y = cy + shake_y
            crack_end_x = crack_start_x + int(crack_length * math.cos(crack_angle))
            crack_end_y = crack_start_y + int(crack_length * math.sin(crack_angle))
            crack_alpha = int(150 * t)
            pygame.draw.line(overlay, (60, 45, 30, crack_alpha), (crack_start_x, crack_start_y), (crack_end_x, crack_end_y), 2)
        
        # Частицы грязи поднимаются
        for particle_idx in range(12):
            particle_angle = (particle_idx * (2*math.pi / 12.0))
            particle_dist = int(20 * t)
            particle_height = int(15 * t * (1 - t))
            particle_x = cx + shake_x + int(particle_dist * math.cos(particle_angle))
            particle_y = cy + shake_y - particle_height
            particle_size = random.randint(2, 4)
            particle_alpha = int(180 * t * (1 - t * 0.5))
            pygame.draw.circle(overlay, (80, 60, 40, particle_alpha), (particle_x, particle_y), particle_size)
        
        # Коричневое свечение
        if t > 0.3:
            glow_alpha = int(100 * (t - 0.3) / 0.7)
            pygame.draw.circle(overlay, (100, 75, 50, glow_alpha), (cx + shake_x, cy + shake_y), int(40 * t))
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний

def animate_quicksand_creation(screen, quicksand_positions, redraw_callback=None):
    """Анимация создания зыбучих песков - появляются бурлящие лужи грязи"""
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        
        for qx, qy in quicksand_positions:
            # Лужа появляется и растёт
            if t < 0.5:
                pool_alpha = int(180 * (t / 0.5))
                pool_size = int(25 * (t / 0.5))
            else:
                pool_alpha = 180
                pool_size = 25
            
            # Основная лужа (коричневая/грязь)
            pygame.draw.circle(overlay, (80, 60, 40, pool_alpha), (qx, qy), pool_size)
            pygame.draw.circle(overlay, (100, 75, 50, int(pool_alpha*0.8)), (qx, qy), int(pool_size*0.9))
            
            # Бурлящие пузыри
            for bubble_idx in range(8):
                bubble_angle = (bubble_idx * (2*math.pi / 8.0)) + t * 2
                max_dist = max(5, int(pool_size * 0.7))  # Исправление: гарантируем минимум 5
                bubble_dist = random.randint(3, max_dist)  # Исправление: минимум 3 вместо 5
                bubble_x = qx + int(bubble_dist * math.cos(bubble_angle))
                bubble_y = qy + int(bubble_dist * math.sin(bubble_angle))
                bubble_size = random.randint(2, 5)
                bubble_alpha = int(pool_alpha * 0.6)
                pygame.draw.circle(overlay, (120, 90, 60, bubble_alpha), (bubble_x, bubble_y), bubble_size)
            
            # Частицы грязи
            for particle_idx in range(12):
                particle_angle = (particle_idx * (2*math.pi / 12.0)) + t * 3 + random.uniform(-0.3, 0.3)
                particle_dist = random.randint(int(pool_size * 0.8), int(pool_size * 1.2))
                particle_x = qx + int(particle_dist * math.cos(particle_angle))
                particle_y = qy + int(particle_dist * math.sin(particle_angle))
                particle_size = random.randint(1, 3)
                particle_alpha = int(pool_alpha * 0.4 * random.random())
                pygame.draw.circle(overlay, (90, 70, 45, particle_alpha), (particle_x, particle_y), particle_size)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(6)  # Ускорено для быстрых заклинаний

def animate_quicksand_trigger(screen, target_px, redraw_callback=None):
    """Анимация срабатывания зыбучих песков - улучшенная бурлящая лужа грязи"""
    import random
    import math
    import time
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 60  # Увеличено для плавности
    cx, cy = target_px
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        anim_time = time.time() * 3
        
        # Основная лужа (коричневая/грязь) - появляется и растёт
        pool_size = int(20 + 15 * min(1.0, t * 2))
        pool_alpha = int(220 * min(1.0, t * 1.5))
        
        # Основная лужа с градиентом
        pygame.draw.circle(overlay, (80, 60, 40, pool_alpha), (cx, cy), pool_size)
        pygame.draw.circle(overlay, (100, 75, 50, int(pool_alpha*0.9)), (cx, cy), int(pool_size*0.9))
        pygame.draw.circle(overlay, (120, 90, 60, int(pool_alpha*0.7)), (cx, cy), int(pool_size*0.7))
        
        # Бурлящие пузыри (больше и активнее)
        for bubble_idx in range(12):
            bubble_angle = (bubble_idx * (2*math.pi / 12.0)) + anim_time
            bubble_dist = random.randint(3, int(pool_size * 0.7))
            bubble_x = cx + int(bubble_dist * math.cos(bubble_angle))
            bubble_y = cy + int(bubble_dist * math.sin(bubble_angle))
            bubble_size = random.randint(3, 6)
            bubble_alpha = int(pool_alpha * 0.8)
            bubble_rise = int(5 * math.sin(anim_time + bubble_idx))
            pygame.draw.circle(overlay, (140, 110, 70, bubble_alpha), (bubble_x, bubble_y - bubble_rise), bubble_size)
            pygame.draw.circle(overlay, (160, 130, 90, int(bubble_alpha*0.6)), (bubble_x, bubble_y - bubble_rise), bubble_size - 1)
        
        # Частицы грязи (больше и активнее)
        for particle_idx in range(16):
            particle_angle = (particle_idx * (2*math.pi / 16.0)) + anim_time * 2 + random.uniform(-0.3, 0.3)
            particle_dist = random.randint(int(pool_size * 0.6), int(pool_size * 1.1))
            particle_x = cx + int(particle_dist * math.cos(particle_angle))
            particle_y = cy + int(particle_dist * math.sin(particle_angle))
            particle_size = random.randint(2, 4)
            particle_alpha = int(pool_alpha * 0.5 * random.random())
            particle_bounce = int(3 * math.sin(anim_time * 2 + particle_idx))
            pygame.draw.circle(overlay, (90, 70, 45, particle_alpha), (particle_x, particle_y + particle_bounce), particle_size)
        
        # Брызги грязи (вверх)
        if t > 0.2:
            splash_t = (t - 0.2) / 0.8
            for splash_idx in range(8):
                splash_angle = (splash_idx * (2*math.pi / 8.0)) + random.uniform(-0.2, 0.2)
                splash_dist = int(25 * splash_t)
                splash_height = int(20 * splash_t * (1 - splash_t))
                splash_x = cx + int(splash_dist * math.cos(splash_angle))
                splash_y = cy - splash_height
                splash_size = random.randint(2, 4)
                splash_alpha = int(150 * (1 - splash_t))
                pygame.draw.circle(overlay, (100, 75, 50, splash_alpha), (splash_x, splash_y), splash_size)
        
        # Волны на поверхности (улучшенные)
        for wave_idx in range(3):
            wave_radius = pool_size + wave_idx * 3
            wave_alpha = int(pool_alpha * 0.4 * (1 - wave_idx * 0.3) * (1 - t * 0.5))
            wave_offset = int(2 * math.sin(anim_time + wave_idx))
            pygame.draw.circle(overlay, (110, 85, 55, wave_alpha), (cx, cy), wave_radius + wave_offset, 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)  # Ускорено для быстрых заклинаний

def animate_earth_shock(screen, target_px, redraw_callback=None):
    """Анимация шока земли - фиолетовый гравитационный купол, собираются частицы, купол крутится, схлопывается в чёрную дыру и взрывается"""
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    # Этап 1: Появление купола и сбор частиц (20 кадров)
    phase1_frames = 20
    for i in range(phase1_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (phase1_frames - 1) if phase1_frames > 1 else 1.0
        cx, cy = target_px
        
        # Купол появляется и растёт (уменьшен размер)
        dome_size = int(25 + 20 * t)  # Уменьшено с 40+30 до 25+20
        dome_alpha = int(200 * min(1.0, t * 1.5))
        
        # Фиолетовый гравитационный купол
        for layer in range(3):
            layer_size = dome_size - layer * 5  # Уменьшено с 8 до 5
            layer_alpha = int(dome_alpha * (1 - layer * 0.3))
            pygame.draw.circle(overlay, (180, 100, 255, layer_alpha), (cx, cy), layer_size, 2)
        
        # Частицы собираются к центру (уменьшен размер)
        for particle_idx in range(20):
            particle_angle = (particle_idx * (2*math.pi / 20.0))
            particle_start_dist = 40  # Уменьшено с 60 до 40
            particle_dist = particle_start_dist * (1 - t)
            particle_x = cx + int(particle_dist * math.cos(particle_angle))
            particle_y = cy + int(particle_dist * math.sin(particle_angle))
            particle_size = random.randint(1, 3)  # Уменьшено с 2-4 до 1-3
            particle_alpha = int(200 * (1 - t * 0.5))
            pygame.draw.circle(overlay, (200, 120, 255, particle_alpha), (particle_x, particle_y), particle_size)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Ускорено для быстрых заклинаний
    
    # Этап 2: Купол крутится (12 кадров) - ускорено
    phase2_frames = 12
    for i in range(phase2_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (phase2_frames - 1) if phase2_frames > 1 else 1.0
        cx, cy = target_px
        
        dome_size = 45  # Уменьшено с 70 до 45
        rotation_angle = t * 4 * math.pi
        
        # Вращающийся купол
        for layer in range(4):
            layer_size = dome_size - layer * 4  # Уменьшено с 6 до 4
            layer_alpha = int(220 * (1 - layer * 0.2))
            rotated_angle = rotation_angle + layer * 0.5
            
            # Спирали на куполе
            for spiral_idx in range(8):
                spiral_angle = (spiral_idx * (2*math.pi / 8.0)) + rotated_angle
                spiral_x = cx + int(layer_size * 0.8 * math.cos(spiral_angle))
                spiral_y = cy + int(layer_size * 0.8 * math.sin(spiral_angle))
                pygame.draw.circle(overlay, (180, 100, 255, layer_alpha), (spiral_x, spiral_y), 2)  # Уменьшено с 3 до 2
        
        # Внешний купол
        pygame.draw.circle(overlay, (180, 100, 255, 200), (cx, cy), dome_size, 3)
        pygame.draw.circle(overlay, (200, 120, 255, 150), (cx, cy), dome_size + 3, 2)  # Уменьшено с 5 до 3
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Ускорено для быстрых заклинаний
    
    # Этап 3: Схлопывание в чёрную дыру (15 кадров) - ускорено
    phase3_frames = 15
    for i in range(phase3_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (phase3_frames - 1) if phase3_frames > 1 else 1.0
        cx, cy = target_px
        
        # Купол схлопывается (уменьшен размер)
        collapse_size = int(45 * (1 - t))  # Уменьшено с 70 до 45
        
        # Чёрная дыра в центре (уменьшен размер)
        black_hole_size = int(3 + 10 * t)  # Уменьшено с 5+15 до 3+10
        pygame.draw.circle(overlay, (0, 0, 0, 255), (cx, cy), black_hole_size)
        pygame.draw.circle(overlay, (50, 0, 80, 200), (cx, cy), black_hole_size + 2)  # Уменьшено с 3 до 2
        
        # Внешний купол схлопывается
        if collapse_size > black_hole_size:
            pygame.draw.circle(overlay, (180, 100, 255, int(200 * (1 - t))), (cx, cy), collapse_size, 2)
        
        # Частицы втягиваются в дыру (уменьшен размер)
        for particle_idx in range(30):
            particle_angle = (particle_idx * (2*math.pi / 30.0))
            particle_dist = int((collapse_size - black_hole_size) * (1 - t) + black_hole_size)
            particle_x = cx + int(particle_dist * math.cos(particle_angle))
            particle_y = cy + int(particle_dist * math.sin(particle_angle))
            particle_size = random.randint(1, 2)  # Уменьшено с 1-3 до 1-2
            particle_alpha = int(150 * (1 - t))
            pygame.draw.circle(overlay, (200, 120, 255, particle_alpha), (particle_x, particle_y), particle_size)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Ускорено для быстрых заклинаний
    
    # Этап 4: Эпичный фиолетовый взрыв (15 кадров) - ускорено
    phase4_frames = 15
    for i in range(phase4_frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (phase4_frames - 1) if phase4_frames > 1 else 1.0
        cx, cy = target_px
        
        # Взрыв распространяется (фиолетовый, уменьшен размер, но интенсивнее)
        explosion_size = int(15 + 60 * t)  # Уменьшено с 25+100 до 15+60
        explosion_alpha = int(255 * (1 - t * 0.5))  # Более интенсивная (было 0.6)
        
        # Множественные взрывные волны (фиолетовые, уменьшен размер, но интенсивнее)
        for wave in range(6):  # Увеличено с 5 до 6 волн
            wave_size = explosion_size - wave * 10  # Уменьшено с 11 до 10
            wave_alpha = int(explosion_alpha * (1 - wave * 0.12))  # Более интенсивная
            if wave_size > 0:
                # Фиолетовые волны с градиентом (более яркие)
                if wave == 0:
                    color = (200, 120, 255, wave_alpha)  # Более яркий
                    outer_color = (220, 140, 255, int(wave_alpha*0.8))  # Более яркий
                elif wave == 1:
                    color = (180, 100, 255, wave_alpha)  # Более яркий
                    outer_color = (200, 120, 255, int(wave_alpha*0.7))
                elif wave == 2:
                    color = (160, 80, 240, wave_alpha)
                    outer_color = (180, 100, 255, int(wave_alpha*0.6))
                elif wave == 3:
                    color = (140, 60, 220, wave_alpha)
                    outer_color = (160, 80, 240, int(wave_alpha*0.5))
                else:
                    color = (120, 40, 200, wave_alpha)
                    outer_color = (140, 60, 220, int(wave_alpha*0.4))
                
                pygame.draw.circle(overlay, color, (cx, cy), wave_size, 4)  # Увеличено с 3 до 4 для интенсивности
                pygame.draw.circle(overlay, outer_color, (cx, cy), wave_size + 6, 3)  # Увеличено с 5,2 до 6,3
        
        # Яркий фиолетовый центр (уменьшен размер, но интенсивнее)
        center_size = int(12 * (1 - t * 0.8))  # Уменьшено с 20 до 12
        if center_size > 0:
            pygame.draw.circle(overlay, (255, 255, 255, int(255 * (1 - t * 0.8))), (cx, cy), center_size)  # Более яркий
            pygame.draw.circle(overlay, (240, 180, 255, int(255 * (1 - t * 0.6))), (cx, cy), center_size + 6)  # Более яркий и больше
            pygame.draw.circle(overlay, (220, 150, 255, int(255 * (1 - t * 0.5))), (cx, cy), center_size + 10)  # Более яркий и больше
            pygame.draw.circle(overlay, (200, 120, 255, int(220 * (1 - t * 0.4))), (cx, cy), center_size + 14)  # Дополнительный слой
        
        # Эпичные фиолетовые искры взрыва (уменьшен размер, но больше и интенсивнее)
        for spark_idx in range(40):  # Увеличено с 32 до 40
            spark_angle = (spark_idx * (2*math.pi / 40.0)) + random.uniform(-0.4, 0.4)
            spark_dist = int(explosion_size * 0.95)  # Увеличено с 0.9 до 0.95
            spark_x = cx + int(spark_dist * math.cos(spark_angle))
            spark_y = cy + int(spark_dist * math.sin(spark_angle))
            spark_size = random.randint(3, 6)  # Увеличено с 2-5 до 3-6 для интенсивности
            spark_alpha = int(explosion_alpha * (0.8 + random.random() * 0.2))  # Более яркие
            
            # Фиолетовые искры с белым центром (более яркие)
            pygame.draw.circle(overlay, (220, 140, 255, spark_alpha), (spark_x, spark_y), spark_size)  # Более яркий
            pygame.draw.circle(overlay, (255, 255, 255, int(spark_alpha*0.95)), (spark_x, spark_y), max(2, spark_size - 1))  # Более яркий
            pygame.draw.circle(overlay, (200, 120, 255, int(spark_alpha*0.7)), (spark_x, spark_y), spark_size + 3, 2)  # Более яркий и больше
        
        # Дополнительные энергетические вспышки (уменьшен размер, но больше и интенсивнее)
        for flash_idx in range(12):  # Увеличено с 8 до 12
            flash_angle = (flash_idx * (2*math.pi / 12.0)) + t * 2
            flash_dist = int(explosion_size * 0.65)  # Увеличено с 0.6 до 0.65
            flash_x = cx + int(flash_dist * math.cos(flash_angle))
            flash_y = cy + int(flash_dist * math.sin(flash_angle))
            flash_size = int(8 * (1 - t))  # Увеличено с 7 до 8
            flash_alpha = int(240 * (1 - t))  # Более яркий (было 200)
            if flash_size > 0:
                pygame.draw.circle(overlay, (255, 255, 255, flash_alpha), (flash_x, flash_y), flash_size)
                pygame.draw.circle(overlay, (240, 180, 255, int(flash_alpha*0.9)), (flash_x, flash_y), flash_size + 3)  # Более яркий и больше
                pygame.draw.circle(overlay, (220, 150, 255, int(flash_alpha*0.7)), (flash_x, flash_y), flash_size + 6)  # Дополнительный слой
        
        # Гравитационные искажения (кольца, уменьшен размер)
        for ring_idx in range(4):
            ring_radius = int(explosion_size * 0.3 + ring_idx * 9)  # Уменьшено с 15 до 9
            ring_alpha = int(100 * (1 - t) * (1 - ring_idx * 0.2))
            if ring_radius > 0 and ring_alpha > 0:
                pygame.draw.circle(overlay, (150, 80, 255, ring_alpha), (cx, cy), ring_radius, 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)


def animate_prayer(screen, target_px, redraw_callback=None):
    """Анимация молитвы - крылья ангела окутывают юнит, летящие белые перья, небесный свет"""
    import random
    import math
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE
    
    frames = 80  # Увеличено до 80 кадров для максимальной плавности
    cx, cy = target_px
    
    # Массив перьев, которые падают на юнит (из проклятия, но белые)
    feathers = []
    for _ in range(35):  # Больше перьев для насыщенности
        # Позиция начала падения (над юнитом)
        start_x = cx + (random.random() - 0.5) * 80
        start_y = cy - CELL_SIZE - random.random() * 60
        # Скорость падения
        vel_x = (random.random() - 0.5) * 2.5
        vel_y = random.random() * 2.0 + 1.0
        # Размер и угол поворота
        size = random.random() * 5 + 3
        angle = random.random() * 2 * math.pi
        rotation_speed = (random.random() - 0.5) * 0.3
        feathers.append({
            'x': start_x,
            'y': start_y,
            'vel_x': vel_x,
            'vel_y': vel_y,
            'size': size,
            'angle': angle,
            'rotation_speed': rotation_speed,
            'alpha': 230
        })
    
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        
        # Небесный свет (яркие лучи сверху)
        if t < 0.6:
            light_alpha = int(200 * (t / 0.6))
        else:
            light_alpha = int(200 * (1 - (t - 0.6) / 0.4))
        
        # Лучи света сверху
        for ray_idx in range(8):
            ray_angle = (ray_idx * (2*math.pi / 8.0)) - math.pi/2  # Направлены вниз
            ray_length = int(100 * t * (1 - t * 0.5))
            ray_end_x = cx + int(ray_length * math.cos(ray_angle))
            ray_end_y = cy + int(ray_length * math.sin(ray_angle))
            ray_width = int(3 * (1 - t * 0.5))
            if ray_width > 0:
                pygame.draw.line(overlay, (255, 255, 255, light_alpha), (cx, cy - 50), (ray_end_x, ray_end_y), ray_width)
        
        # Крылья ангела (появляются и окутывают юнит)
        if t > 0.2:
            wing_t = (t - 0.2) / 0.8
            wing_size = int(40 + 20 * wing_t)
            wing_alpha = int(180 * min(1.0, wing_t * 1.5))
            
            # Левое крыло
            wing_left_x = cx - 30
            wing_left_y = cy
            for feather_layer in range(3):
                layer_size = wing_size - feather_layer * 5
                layer_alpha = int(wing_alpha * (1 - feather_layer * 0.2))
                # Перья крыла
                for feather_idx in range(5):
                    feather_angle = -math.pi/4 + (feather_idx * 0.2) + wing_t * 0.3
                    feather_x = wing_left_x + int(layer_size * 0.6 * math.cos(feather_angle))
                    feather_y = wing_left_y + int(layer_size * 0.6 * math.sin(feather_angle))
                    pygame.draw.circle(overlay, (255, 255, 255, layer_alpha), (feather_x, feather_y), 8 - feather_layer)
            
            # Правое крыло
            wing_right_x = cx + 30
            wing_right_y = cy
            for feather_layer in range(3):
                layer_size = wing_size - feather_layer * 5
                layer_alpha = int(wing_alpha * (1 - feather_layer * 0.2))
                # Перья крыла
                for feather_idx in range(5):
                    feather_angle = math.pi/4 - (feather_idx * 0.2) - wing_t * 0.3
                    feather_x = wing_right_x + int(layer_size * 0.6 * math.cos(feather_angle))
                    feather_y = wing_right_y + int(layer_size * 0.6 * math.sin(feather_angle))
                    pygame.draw.circle(overlay, (255, 255, 255, layer_alpha), (feather_x, feather_y), 8 - feather_layer)
        
        # Обновляем позиции перьев (из проклятия)
        for feather in feathers:
            feather['x'] += feather['vel_x']
            feather['y'] += feather['vel_y']
            feather['angle'] += feather['rotation_speed']  # Вращение
            # Замедление по мере падения
            if feather['y'] > cy - CELL_SIZE//2:
                feather['vel_y'] *= 0.93
                feather['alpha'] = max(60, feather['alpha'] - 8)
            else:
                feather['alpha'] = min(230, feather['alpha'] + 8)
        
        # Рисуем белые перья (из проклятия, но белые)
        for feather in feathers:
            if feather['y'] < cy + CELL_SIZE//2 and feather['alpha'] > 0:
                # Белое перо (из проклятия, но белое)
                px, py = int(feather['x']), int(feather['y'])
                alpha = int(feather['alpha'])
                size = int(feather['size'])
                
                # Тело пера (белое)
                feather_points = []
                for p in range(5):
                    p_angle = feather['angle'] + p * 0.3
                    p_x = px + int(size * 0.8 * math.cos(p_angle))
                    p_y = py + int(size * 0.4 * math.sin(p_angle))
                    feather_points.append((p_x, p_y))
                
                if len(feather_points) >= 3:
                    pygame.draw.polygon(overlay, (255, 255, 255, alpha), feather_points)
                    # Контур пера (светло-серый)
                    pygame.draw.polygon(overlay, (240, 240, 240, alpha), feather_points, 1)
        
        # Светящееся кольцо вокруг юнита
        if t > 0.3:
            ring_t = (t - 0.3) / 0.7
            ring_radius = int(30 + 20 * ring_t)
            ring_alpha = int(150 * (1 - ring_t * 0.5))
            pygame.draw.circle(overlay, (255, 255, 255, ring_alpha), (cx, cy), ring_radius, 3)
            pygame.draw.circle(overlay, (200, 230, 255, int(ring_alpha*0.7)), (cx, cy), ring_radius + 5, 2)
        
        # Центральное свечение
        center_alpha = int(255 * min(1.0, t * 1.2))
        pygame.draw.circle(overlay, (255, 255, 255, center_alpha), (cx, cy), int(15 * (1 - t * 0.5)))
        pygame.draw.circle(overlay, (200, 230, 255, int(center_alpha*0.8)), (cx, cy), int(20 * (1 - t * 0.5)))
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(6)  # Ускорено для быстрых заклинаний


def animate_blindness(screen, target_px, redraw_callback=None):
    """Анимация ослепления - появляются слепящие звезды с рандомно увеличивающимся и уменьшающимся эффектом"""
    import pygame
    import random
    import math
    import time
    from .config import SCREEN_WIDTH, SCREEN_HEIGHT
    
    frames = 120  # Увеличено до 120 кадров для максимальной плавности
    cx, cy = target_px
    
    # Создаём несколько звезд с разными параметрами
    num_stars = 8
    stars = []
    for star_idx in range(num_stars):
        star_angle = (star_idx * (2*math.pi / num_stars))
        star_dist = random.randint(20, 50)
        star_x = cx + int(star_dist * math.cos(star_angle))
        star_y = cy + int(star_dist * math.sin(star_angle))
        star_speed = random.uniform(0.5, 1.5)
        star_phase = random.uniform(0, 2*math.pi)
        stars.append({
            'x': star_x,
            'y': star_y,
            'speed': star_speed,
            'phase': star_phase,
            'base_size': random.randint(5, 10)
        })
    
    start_time = time.time()
    for i in range(frames):
        pygame.event.pump()
        if redraw_callback:
            redraw_callback()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = i / (frames - 1) if frames > 1 else 1.0
        anim_time = (time.time() - start_time) * 3  # Используем относительное время
        
        # Слепящие звезды
        for star in stars:
            # Пульсация размера (случайная частота)
            pulse = math.sin(anim_time * star['speed'] + star['phase']) * 0.5 + 0.5
            star_size = int(star['base_size'] * (0.5 + pulse * 0.8))
            star_alpha = int(255 * (0.7 + pulse * 0.3) * (1 - t * 0.3))
            
            # Рисуем звезду (крест с ярким центром)
            # Основные лучи
            for ray_idx in range(4):
                ray_angle = ray_idx * (math.pi / 2)
                ray_end_x = star['x'] + int(star_size * math.cos(ray_angle))
                ray_end_y = star['y'] + int(star_size * math.sin(ray_angle))
                pygame.draw.line(overlay, (255, 255, 255, star_alpha), 
                               (star['x'], star['y']), (ray_end_x, ray_end_y), 2)
            
            # Диагональные лучи (короче)
            for ray_idx in range(4):
                ray_angle = ray_idx * (math.pi / 2) + math.pi/4
                ray_end_x = star['x'] + int(star_size * 0.7 * math.cos(ray_angle))
                ray_end_y = star['y'] + int(star_size * 0.7 * math.sin(ray_angle))
                pygame.draw.line(overlay, (255, 255, 200, int(star_alpha*0.8)), 
                               (star['x'], star['y']), (ray_end_x, ray_end_y), 1)
            
            # Яркий центр
            pygame.draw.circle(overlay, (255, 255, 255, star_alpha), (star['x'], star['y']), star_size // 3)
            pygame.draw.circle(overlay, (255, 255, 200, int(star_alpha*0.9)), (star['x'], star['y']), star_size // 2)
        
        # Слепящий свет (вспышки)
        if t < 0.7:
            flash_t = t / 0.7
            flash_alpha = int(150 * (1 - flash_t) * random.random())
            flash_size = int(60 * flash_t)
            pygame.draw.circle(overlay, (255, 255, 255, flash_alpha), (cx, cy), flash_size)
            pygame.draw.circle(overlay, (255, 255, 200, int(flash_alpha*0.7)), (cx, cy), flash_size + 10)
        
        # Вращающиеся световые кольца
        for ring_idx in range(3):
            ring_angle = anim_time + ring_idx * (2*math.pi / 3)
            ring_radius = int(30 + ring_idx * 15)
            ring_alpha = int(100 * (1 - t * 0.5) * (1 - ring_idx * 0.2))
            # Рисуем кольцо как дугу
            for arc_segment in range(8):
                arc_angle = ring_angle + arc_segment * (2*math.pi / 8)
                arc_start_x = cx + int(ring_radius * math.cos(arc_angle))
                arc_start_y = cy + int(ring_radius * math.sin(arc_angle))
                arc_end_x = cx + int(ring_radius * math.cos(arc_angle + 0.3))
                arc_end_y = cy + int(ring_radius * math.sin(arc_angle + 0.3))
                pygame.draw.line(overlay, (255, 255, 200, ring_alpha), 
                               (arc_start_x, arc_start_y), (arc_end_x, arc_end_y), 2)
        
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)  # Ускорено для быстрых заклинаний