import math
from typing import Dict, List, Optional, Tuple
import re

import pygame

from .config import SCREEN_HEIGHT, SCREEN_WIDTH
from .units import Hero, TEAM_LABELS, RESISTANCE_TYPES, AnimatedHumanoidMixin


STAT_DESCRIPTIONS: Dict[str, str] = {
    'level': "Опыт и сила существа. Каждое повышение уровня улучшает параметры и открывает новые таланты.",
    'leadership': "Отражает численность и стоимость отряда. Чем выше лидерство, тем больше существ может находиться в армии без штрафов.",
    'attack': "Эффективность нанесения урона. Если атака нападающего превышает защиту цели, наносимый урон увеличивается.",
    'defense': "Эффективность защиты от атак. Если защита выше атаки врага, получаемый урон снижается.",
    'initiative': "Частота хода в бою. Высокая инициатива позволяет действовать раньше и чаще.",
    'speed': "Количество клеток, которое юнит может пройти за один ход.",
    'crit': "Шанс нанести критический урон. При критическом ударе урон умножается на критический множитель.",
    'damage': "Урон основной атаки. Для стрелков в ближнем бою урон обычно снижается.",
    'health': "Текущее здоровье существа. При падении до нуля погибает один боец, а здоровье отряда уменьшается.",
    'mana': "Запас магической энергии героя, используемой для заклинаний.",
    'spell_power': "Сила магии героя. Увеличивает эффективность заклинаний.",
    'knowledge': "Знания героя. Определяет максимальный запас маны.",
    'luck': "Шанс нанести двойной урон. Положительная удача повышает шанс, отрицательная — снижает.",
    'morale': "Шанс получить дополнительный ход (при высоком духе) или пропустить его (при низком).",
}

RESISTANCE_LABELS: Dict[str, str] = {
    'physical': 'Физическая',
    'magic': 'Магическая',
    'poison': 'Ядовитая',
    'fire': 'Огненная',
    'cold': 'Холодная',
    'astral': 'Астральная',
}

RESISTANCE_DESCRIPTIONS: Dict[str, str] = {
    'physical': "Сопротивление физическому урону. Уменьшает урон от оружия и ударов.",
    'magic': "Сопротивление магическому урону. Уменьшает эффект атакующих заклинаний.",
    'poison': "Защита от яда. Снижает длительность и силу отравлений.",
    'fire': "Сопротивление огню. Уменьшает урон от огненных заклинаний и эффектов.",
    'cold': "Сопротивление холоду. Уменьшает урон и шанс замедления от морозных атак.",
    'astral': "Сопротивление астральной магии. Помогает против проклятий и ментальных заклинаний.",
}


def _format_number(value: float) -> str:
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
        return f"{int(value)}"
    return f"{value:.1f}"


def _format_stat_value(current, base=None, suffix: str = '') -> str:
    formatted_current = _format_number(current)
    if base is None or math.isclose(current, base, rel_tol=1e-4):
        return f"{formatted_current}{suffix}"
    formatted_base = _format_number(base)
    return f"{formatted_current}{suffix} ({formatted_base}{suffix})"


def _resistance_status(value: int) -> str:
    if value >= 75:
        return "Иммунитет"
    if value >= 50:
        return "Очень высокая"
    if value >= 25:
        return "Защищен"
    if value > 0:
        return "Устойчив"
    if value < 0:
        return "Уязвим"
    return "Норма"


def _build_unit_stat_entries(unit) -> List[Dict]:
    entries: List[Dict] = []
    if isinstance(unit, Hero):
        entries.append({
            'id': 'attack',
            'label': 'Атака',
            'display': _format_stat_value(unit.attack, getattr(unit, 'base_attack', unit.attack)),
            'description': STAT_DESCRIPTIONS['attack'],
            'details': [],
        })
        entries.append({
            'id': 'defense',
            'label': 'Защита',
            'display': _format_stat_value(unit.defense, getattr(unit, 'base_defense', unit.defense)),
            'description': STAT_DESCRIPTIONS['defense'],
            'details': [],
        })
        entries.append({
            'id': 'spell_power',
            'label': 'Сила магии',
            'display': _format_stat_value(unit.spell_power, getattr(unit, 'base_spell_power', unit.spell_power)),
            'description': STAT_DESCRIPTIONS['spell_power'],
            'details': [],
        })
        entries.append({
            'id': 'knowledge',
            'label': 'Знания',
            'display': _format_stat_value(unit.knowledge, getattr(unit, 'base_knowledge', unit.knowledge)),
            'description': STAT_DESCRIPTIONS['knowledge'],
            'details': [],
        })
        entries.append({
            'id': 'mana',
            'label': 'Мана',
            'display': f"{_format_number(unit.mana)}/{_format_number(unit.max_mana)}",
            'description': STAT_DESCRIPTIONS['mana'],
            'details': [],
        })
        entries.append({
            'id': 'luck',
            'label': 'Удача',
            'display': _format_stat_value(unit.luck, getattr(unit, 'base_luck', unit.luck), suffix=''),
            'description': STAT_DESCRIPTIONS['luck'],
            'details': [f"Шанс двойного урона: {abs(unit.luck) * 5}%"],
        })
        entries.append({
            'id': 'morale',
            'label': 'Боевой дух',
            'display': _format_stat_value(unit.combat_spirit, getattr(unit, 'base_combat_spirit', unit.combat_spirit)),
            'description': STAT_DESCRIPTIONS['morale'],
            'details': [f"Шанс доп. хода: {abs(unit.combat_spirit) * 3}%"],
        })
        return entries

    if unit.attack_type == 'magical':
        current_attack = getattr(unit, 'magic_attack', 0)
        base_attack = getattr(unit, 'base_magic_attack', current_attack)
    else:
        current_attack = getattr(unit, 'phys_attack', 0)
        base_attack = getattr(unit, 'base_phys_attack', current_attack)
    entries.append({
        'id': 'attack',
        'label': 'Атака',
        'display': _format_stat_value(current_attack, base_attack),
        'description': STAT_DESCRIPTIONS['attack'],
        'details': [f"Тип атаки: {'Магическая' if unit.attack_type == 'magical' else 'Физическая'}"],
    })

    defense_value = getattr(unit, 'phys_defense', 0)
    base_defense = getattr(unit, 'base_phys_defense', defense_value)
    entries.append({
        'id': 'defense',
        'label': 'Защита',
        'display': _format_stat_value(defense_value, base_defense),
        'description': STAT_DESCRIPTIONS['defense'],
        'details': [f"Магическая защита: {getattr(unit, 'magic_defense', 0)}"],
    })

    initiative = getattr(unit, 'initiative', 0)
    entries.append({
        'id': 'initiative',
        'label': 'Инициатива',
        'display': _format_stat_value(initiative, getattr(unit, 'base_initiative', initiative)),
        'description': STAT_DESCRIPTIONS['initiative'],
        'details': [],
    })

    speed = getattr(unit, 'speed', 0)
    entries.append({
        'id': 'speed',
        'label': 'Скорость',
        'display': _format_stat_value(speed, getattr(unit, 'base_speed', speed)),
        'description': STAT_DESCRIPTIONS['speed'],
        'details': [],
    })

    crit = getattr(unit, 'crit_chance', 0)
    base_crit = getattr(unit, 'base_crit_chance', crit)
    entries.append({
        'id': 'crit',
        'label': 'Крит',
        'display': _format_stat_value(crit, base_crit, suffix='%'),
        'description': STAT_DESCRIPTIONS['crit'],
        'details': [f"Множитель: x{_format_number(getattr(unit, 'crit_multiplier', 2.0))}"],
    })

    dmg_min = getattr(unit, 'damage_min', getattr(unit, 'phys_attack', 0))
    dmg_max = getattr(unit, 'damage_max', dmg_min)
    base_min = getattr(unit, 'base_damage_min', dmg_min)
    base_max = getattr(unit, 'base_damage_max', dmg_max)
    if (dmg_min, dmg_max) == (base_min, base_max):
        dmg_display = f"{_format_number(dmg_min)}-{_format_number(dmg_max)}"
    else:
        dmg_display = f"{_format_number(dmg_min)}-{_format_number(dmg_max)} ({_format_number(base_min)}-{_format_number(base_max)})"
    entries.append({
        'id': 'damage',
        'label': 'Урон',
        'display': dmg_display,
        'description': STAT_DESCRIPTIONS['damage'],
        'details': [],
    })

    if getattr(unit, 'squad_count', 1) > 1 and getattr(unit, 'unit_hp', None):
        current_hp = getattr(unit, 'current_unit_hp', unit.unit_hp)
        base_hp = unit.unit_hp
        army_summary = f"Здоровье отряда: {int(unit.health)}/{int(unit.max_health)}"
    else:
        current_hp = getattr(unit, 'health', 0)
        base_hp = getattr(unit, 'base_health', getattr(unit, 'max_health', current_hp))
        army_summary = f"Макс. здоровье: {int(getattr(unit, 'max_health', base_hp))}"
    entries.append({
        'id': 'health',
        'label': 'Здоровье',
        'display': _format_stat_value(current_hp, base_hp),
        'description': STAT_DESCRIPTIONS['health'],
        'details': [army_summary],
    })

    return entries


def _build_resistance_entries(unit) -> List[Dict]:
    entries: List[Dict] = []
    resistances = getattr(unit, 'resistances', {}) or {}
    base_resistances = getattr(unit, 'base_resistances', {}) or {}
    for resistance_key in RESISTANCE_TYPES:
        label = RESISTANCE_LABELS.get(resistance_key, resistance_key.title())
        current_value = int(resistances.get(resistance_key, 0))
        base_value = int(base_resistances.get(resistance_key, current_value))
        display = _format_stat_value(current_value, base_value, suffix='%')
        entries.append({
            'id': f'res_{resistance_key}',
            'label': label,
            'display': display,
            'description': RESISTANCE_DESCRIPTIONS.get(resistance_key, ''),
            'details': [f"Статус: {_resistance_status(current_value)}"],
        })
    return entries


def _collect_traits(unit) -> List[str]:
    traits: List[str] = []
    explicit_traits = getattr(unit, 'traits', [])
    if explicit_traits:
        traits.extend(explicit_traits)
    else:
        traits.append(TEAM_LABELS.get(unit.team, unit.team))
        if isinstance(unit, Hero):
            traits.append("Герой")
        else:
            traits.append("Дальнобойный" if getattr(unit, 'is_ranged', False) else "Ближний бой")
            traits.append("Магическое существо" if unit.attack_type == 'magical' else "Физический боец")
    return traits


def _collect_talents(unit) -> List[str]:
    talents = getattr(unit, 'talents', [])
    if talents:
        return list(talents)
    if isinstance(unit, Hero):
        return ["Поддержка армии", "Командир"]
    generated = []
    if getattr(unit, 'attack_buff_turns', 0) > 0:
        generated.append("Вдохновение")
    if getattr(unit, 'is_ranged', False):
        generated.append("Стрельба")
    if getattr(unit, 'attack_type', '') == 'magical':
        generated.append("Магия природы")
    if not generated:
        generated.append("Особых талантов нет")
    return generated


def _prettify_state_name(state: str) -> str:
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', state.replace('_', ' '))
    return spaced.capitalize()


def _format_animation_sequence(sequence: List[Tuple[str, int]]) -> str:
    if not sequence:
        return ""
    formatted = [_prettify_state_name(state) for state, _ in sequence]
    return " → ".join(formatted)


def _collect_animation_capabilities(unit) -> List[str]:
    capabilities: List[str] = []
    movement_cycle = getattr(unit, '_movement_cycle', None)
    if movement_cycle:
        if isinstance(movement_cycle, str):
            readable = _prettify_state_name(movement_cycle)
        else:
            readable = " ↔ ".join(_prettify_state_name(state) for state in movement_cycle)
        capabilities.append(f"Перемещение: {readable}")
    if getattr(unit, '_supports_turn_animation', False):
        turn_names = " / ".join(_prettify_state_name(state) for state in ('TurnLeft', 'TurnRight'))
        capabilities.append(f"Поворот к цели: {turn_names}")
    melee_sequence = getattr(unit, '_melee_sequence', None)
    if melee_sequence:
        capabilities.append(f"Ближняя атака: {_format_animation_sequence(melee_sequence)}")
    counter_sequence = getattr(unit, '_counter_sequence', None)
    if counter_sequence:
        capabilities.append(f"Контратака: {_format_animation_sequence(counter_sequence)}")
    attack_sequence = getattr(unit, '_attack_sequence', None)
    if attack_sequence and attack_sequence is not melee_sequence:
        capabilities.append(f"Атака: {_format_animation_sequence(attack_sequence)}")
    ranged_sequence = getattr(unit, '_ranged_sequence', None)
    if ranged_sequence:
        ranged_text = _format_animation_sequence(ranged_sequence)
        ranged_recover = getattr(unit, '_ranged_recover', None)
        if ranged_recover:
            recover_text = _format_animation_sequence(ranged_recover)
            if recover_text:
                ranged_text = f"{ranged_text} → {recover_text}"
        capabilities.append(f"Дальняя атака: {ranged_text}")
    hurt_sequence = getattr(unit, '_hurt_sequence', None)
    if hurt_sequence:
        capabilities.append(f"Получение урона: {_format_animation_sequence(hurt_sequence)}")
    death_sequence = getattr(unit, '_death_sequence', None)
    if death_sequence:
        capabilities.append(f"Смерть: {_format_animation_sequence(death_sequence)}")
    if not capabilities and isinstance(unit, AnimatedHumanoidMixin):
        capabilities.append("Доступны базовые анимации: Idle / Hurt / Death")
    return capabilities


def _draw_section_header(surface: pygame.Surface, text: str, position: Tuple[int, int], font: pygame.font.Font):
    shadow = font.render(text, True, (30, 20, 10))
    label = font.render(text, True, (255, 240, 210))
    surface.blit(shadow, (position[0] + 2, position[1] + 2))
    surface.blit(label, position)


def _draw_tooltip(surface: pygame.Surface, mouse_pos: Tuple[int, int], header: str, lines: List[str], font_header, font_text):
    padding = 12
    line_height = 22
    width = font_header.size(header)[0]
    for line in lines:
        width = max(width, font_text.size(line)[0])
    tooltip_w = width + padding * 2
    tooltip_h = padding * 2 + line_height * (1 + len(lines))
    tooltip_x = mouse_pos[0] + 24
    tooltip_y = mouse_pos[1] + 24
    if tooltip_x + tooltip_w > SCREEN_WIDTH:
        tooltip_x = mouse_pos[0] - tooltip_w - 24
    if tooltip_y + tooltip_h > SCREEN_HEIGHT:
        tooltip_y = mouse_pos[1] - tooltip_h - 24
    tooltip_surface = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
    tooltip_surface.fill((35, 30, 45, 235))
    pygame.draw.rect(tooltip_surface, (160, 140, 190), (0, 0, tooltip_w, tooltip_h), 2, border_radius=8)
    tooltip_surface.blit(font_header.render(header, True, (250, 235, 210)), (padding, padding))
    for idx, line in enumerate(lines):
        tooltip_surface.blit(font_text.render(line, True, (220, 220, 230)), (padding, padding + line_height * (idx + 1)))
    surface.blit(tooltip_surface, (tooltip_x, tooltip_y))


def render_unit_info_window(game, unit):
    screen = game.screen
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    window_w, window_h = 660, 520
    window_x = (SCREEN_WIDTH - window_w) // 2
    window_y = (SCREEN_HEIGHT - window_h) // 2

    window_surface = pygame.Surface((window_w, window_h))
    for y in range(window_h):
        gradient = (
            int(150 - y * 0.18),
            int(110 - y * 0.14),
            int(86 - y * 0.10),
        )
        pygame.draw.line(window_surface, gradient, (0, y), (window_w, y))
    screen.blit(window_surface, (window_x, window_y))
    pygame.draw.rect(screen, (70, 50, 35), (window_x, window_y, window_w, window_h), 6, border_radius=18)
    inner_rect = pygame.Rect(window_x + 4, window_y + 4, window_w - 8, window_h - 8)
    pygame.draw.rect(screen, (170, 140, 110), inner_rect, 2, border_radius=16)

    close_size = 32
    close_x = window_x + window_w - close_size - 14
    close_y = window_y + 14
    game.unit_info_close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
    pygame.draw.rect(screen, (180, 60, 60), game.unit_info_close_button_rect, border_radius=6)
    font_close = pygame.font.Font(None, 34)
    screen.blit(font_close.render("×", True, (255, 255, 255)), (close_x + 7, close_y + 3))

    font_title = pygame.font.Font(None, 52)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 24)
    font_label = pygame.font.Font(None, 26)

    title_text = unit.unit_type.replace('_', ' ').title() if not isinstance(unit, Hero) else "Герой"
    title_shadow = font_title.render(title_text, True, (40, 30, 22))
    title_label = font_title.render(title_text, True, (255, 245, 228))
    title_x = window_x + (window_w - title_label.get_width()) // 2
    screen.blit(title_shadow, (title_x + 2, window_y + 24))
    screen.blit(title_label, (title_x, window_y + 20))

    sub_title = TEAM_LABELS.get(unit.team, unit.team)
    sub_text = font_medium.render(sub_title, True, (225, 205, 180))
    screen.blit(sub_text, (window_x + 36, window_y + 76))

    level_value = getattr(unit, 'level', 1)
    level_text = font_small.render(f"Уровень {level_value}", True, (235, 220, 200))
    screen.blit(level_text, (window_x + 36, window_y + 108))

    leadership_current = getattr(unit, 'leadership', getattr(unit, 'base_leadership', 0))
    leadership_base = getattr(unit, 'base_leadership', leadership_current)
    if leadership_current or leadership_base:
        leader_display = _format_stat_value(leadership_current, leadership_base)
        leadership_text = font_small.render(f"Лидерство: {leader_display}", True, (255, 240, 210))
        screen.blit(leadership_text, (window_x + 36, window_y + 132))

    img_size = 132
    img_rect = pygame.Rect(window_x + 36, window_y + 160, img_size, img_size)
    pygame.draw.rect(screen, (30, 26, 20), img_rect.inflate(10, 10), border_radius=12)
    pygame.draw.rect(screen, (200, 178, 140), img_rect.inflate(10, 10), 2, border_radius=12)
    if getattr(unit, 'image', None):
        scaled = pygame.transform.smoothscale(unit.image, (img_size, img_size))
        screen.blit(scaled, img_rect.topleft)

    stats = _build_unit_stat_entries(unit)
    resistances = _build_resistance_entries(unit)
    traits = _collect_traits(unit)
    talents = _collect_talents(unit)
    animations = _collect_animation_capabilities(unit)

    stat_area_x = window_x + 36
    stat_area_y = img_rect.bottom + 30
    stat_row_h = 38
    stat_row_w = 280

    hover_targets: List[Dict] = []

    _draw_section_header(screen, "Характеристики", (stat_area_x, stat_area_y - 30), font_label)

    for idx, entry in enumerate(stats):
        row_rect = pygame.Rect(stat_area_x, stat_area_y + idx * stat_row_h, stat_row_w, stat_row_h - 6)
        pygame.draw.rect(screen, (48, 36, 28, 180), row_rect, border_radius=10)
        pygame.draw.rect(screen, (120, 98, 72), row_rect, 1, border_radius=10)
        label_text = font_small.render(entry['label'], True, (235, 223, 208))
        value_text = font_small.render(entry['display'], True, (255, 255, 210))
        screen.blit(label_text, (row_rect.x + 14, row_rect.y + 8))
        screen.blit(value_text, (row_rect.right - value_text.get_width() - 14, row_rect.y + 8))
        entry['rect'] = row_rect
        hover_targets.append(entry)

    resist_area_x = stat_area_x + stat_row_w + 40
    resist_area_y = window_y + 116
    resist_row_h = 32
    resist_row_w = window_x + window_w - resist_area_x - 36

    _draw_section_header(screen, "Сопротивления", (resist_area_x, resist_area_y - 30), font_label)

    for idx, entry in enumerate(resistances):
        row_rect = pygame.Rect(resist_area_x, resist_area_y + idx * (resist_row_h + 4), resist_row_w, resist_row_h)
        pygame.draw.rect(screen, (38, 32, 44, 200), row_rect, border_radius=8)
        pygame.draw.rect(screen, (130, 110, 160), row_rect, 1, border_radius=8)
        label_text = font_small.render(entry['label'], True, (225, 215, 240))
        value_text = font_small.render(entry['display'], True, (240, 240, 255))
        screen.blit(label_text, (row_rect.x + 12, row_rect.y + 6))
        screen.blit(value_text, (row_rect.right - value_text.get_width() - 12, row_rect.y + 6))
        entry['rect'] = row_rect
        hover_targets.append(entry)

    traits_y = resist_area_y + (len(resistances) + 1) * (resist_row_h + 6)
    _draw_section_header(screen, "Особенности", (resist_area_x, traits_y), font_label)
    traits_y += 28
    for trait in traits:
        screen.blit(font_small.render(f"• {trait}", True, (240, 230, 210)), (resist_area_x + 8, traits_y))
        traits_y += 24

    talents_y = traits_y + 12
    _draw_section_header(screen, "Таланты", (resist_area_x, talents_y), font_label)
    talents_y += 28
    for talent in talents:
        screen.blit(font_small.render(f"• {talent}", True, (240, 230, 210)), (resist_area_x + 8, talents_y))
        talents_y += 24

    if animations:
        animations_y = talents_y + 12
        _draw_section_header(screen, "Анимации", (resist_area_x, animations_y), font_label)
        animations_y += 28
        for entry in animations:
            screen.blit(font_small.render(f"• {entry}", True, (225, 230, 255)), (resist_area_x + 8, animations_y))
            animations_y += 24

    game.unit_info_hover_targets = hover_targets

    mouse_pos = pygame.mouse.get_pos()
    tooltip_entry: Optional[Dict] = None
    for entry in hover_targets:
        rect = entry.get('rect')
        if rect and rect.collidepoint(mouse_pos):
            tooltip_entry = entry
            break
    if tooltip_entry:
        header = tooltip_entry['label']
        lines = [tooltip_entry.get('description', '')] if tooltip_entry.get('description') else []
        lines.extend(tooltip_entry.get('details', []))
        lines = [line for line in lines if line]
        if lines:
            _draw_tooltip(screen, mouse_pos, header, lines, font_medium, font_small)

