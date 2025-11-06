"""
Диагностическая программа для отслеживания проблемы с руной берсерка.
Эта программа поможет понять, почему состояние берсерка перетекает на других юнитов.
"""

import sys
import os
import traceback
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class BerserkerDebugger:
    """Отслеживает все операции с берсерком"""
    
    def __init__(self, log_file='berserker_debug.log'):
        self.log_file = log_file
        self.log_entries = []
        self.unit_states = {}  # id(unit) -> dict с состоянием
        self.berserker_applications = []  # История применений
        self.turn_history = []  # История ходов: кто ходил, как управлялся
        self.enabled = True
        
        # Очищаем лог при каждом новом запуске
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Лог отладки берсерка - сессия начата {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        except Exception as e:
            print(f"Ошибка очистки лога: {e}")
        
    def log(self, event_type, message, unit=None, extra_data=None):
        """Логирует событие"""
        if not self.enabled:
            return
            
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        entry = {
            'timestamp': timestamp,
            'type': event_type,
            'message': message,
            'unit_id': id(unit) if unit else None,
            'unit_type': getattr(unit, 'unit_type', None) if unit else None,
            'unit_pos': (getattr(unit, 'x', None), getattr(unit, 'y', None)) if unit else None,
            'extra': extra_data or {}
        }
        
        # Сохраняем состояние юнита если он есть
        if unit:
            self.save_unit_state(unit, event_type)
        
        self.log_entries.append(entry)
        
        # Формируем строку для вывода
        unit_info = ""
        if unit:
            unit_info = f" | Unit: {getattr(unit, 'unit_type', '?')} @ ({getattr(unit, 'x', '?')}, {getattr(unit, 'y', '?')}) [id={id(unit)}]"
        
        log_line = f"[{timestamp}] {event_type}: {message}{unit_info}"
        if extra_data:
            log_line += f" | Data: {extra_data}"
        
        print(log_line)
        
        # Записываем в файл
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
        except Exception as e:
            print(f"Ошибка записи в лог: {e}")
    
    def save_unit_state(self, unit, event_type):
        """Сохраняет состояние юнита"""
        unit_id = id(unit)
        if unit_id not in self.unit_states:
            self.unit_states[unit_id] = []
        
        state = {
            'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
            'event': event_type,
            'unit_type': getattr(unit, 'unit_type', None),
            'position': (getattr(unit, 'x', None), getattr(unit, 'y', None)),
            'team': getattr(unit, 'team', None),
            'rune_berserker_active': getattr(unit, 'rune_berserker_active', None),
            'rune_berserker_turns': getattr(unit, 'rune_berserker_turns', None),
            'rune_berserker_original_team': getattr(unit, 'rune_berserker_original_team', None),
            'base_phys_attack_berserker': getattr(unit, 'base_phys_attack_berserker', None),
            'base_magic_attack_berserker': getattr(unit, 'base_magic_attack_berserker', None),
            'base_phys_defense_berserker': getattr(unit, 'base_phys_defense_berserker', None),
            'base_magic_defense_berserker': getattr(unit, 'base_magic_defense_berserker', None),
        }
        
        self.unit_states[unit_id].append(state)
    
    def log_spell_apply(self, spell, target, caster=None):
        """Логирует применение заклинания берсерка"""
        if hasattr(spell, 'icon') and spell.icon == 'rune_berserker':
            self.log('SPELL_APPLY', 
                    f"Применение руны берсерка на {getattr(target, 'unit_type', '?')}",
                    target,
                    {
                        'target_team_before': getattr(target, 'team', None),
                        'target_has_berserker_before': getattr(target, 'rune_berserker_active', False),
                        'caster': getattr(caster, 'unit_type', None) if caster else None
                    })
            
            self.berserker_applications.append({
                'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
                'target_id': id(target),
                'target_type': getattr(target, 'unit_type', None),
                'target_pos': (getattr(target, 'x', None), getattr(target, 'y', None)),
                'target_team_before': getattr(target, 'team', None),
            })
    
    def log_team_change(self, unit, old_team, new_team, reason=""):
        """Логирует изменение команды юнита"""
        if isinstance(new_team, str) and new_team.startswith('berserker_'):
            self.log('TEAM_CHANGE_TO_BERSERKER',
                    f"Команда изменена на берсерка: {old_team} -> {new_team} | Причина: {reason}",
                    unit,
                    {'old_team': old_team, 'new_team': new_team})
        elif isinstance(old_team, str) and old_team.startswith('berserker_') and not isinstance(new_team, str) or not new_team.startswith('berserker_'):
            self.log('TEAM_CHANGE_FROM_BERSERKER',
                    f"Команда изменена с берсерка: {old_team} -> {new_team} | Причина: {reason}",
                    unit,
                    {'old_team': old_team, 'new_team': new_team})
    
    def log_berserker_check(self, unit, is_berserker, check_location=""):
        """Логирует проверку, является ли юнит берсерком"""
        if is_berserker or getattr(unit, 'rune_berserker_active', False) or (hasattr(unit, 'team') and isinstance(unit.team, str) and unit.team.startswith('berserker_')):
            self.log('BERSERKER_CHECK',
                    f"Проверка берсерка: {is_berserker} | Место: {check_location}",
                    unit,
                    {
                        'rune_berserker_active': getattr(unit, 'rune_berserker_active', False),
                        'rune_berserker_turns': getattr(unit, 'rune_berserker_turns', 0),
                        'team': getattr(unit, 'team', None),
                        'team_starts_with_berserker': isinstance(getattr(unit, 'team', ''), str) and getattr(unit, 'team', '').startswith('berserker_')
                    })
    
    def log_turn_end(self, unit):
        """Логирует окончание хода юнита"""
        if hasattr(unit, 'rune_berserker_turns') and getattr(unit, 'rune_berserker_turns', 0) > 0:
            self.log('TURN_END',
                    f"Окончание хода берсерка (осталось {getattr(unit, 'rune_berserker_turns', 0)} ходов)",
                    unit)
    
    def log_queue_preparation(self, units):
        """Логирует подготовку очереди ходов"""
        berserkers_in_queue = []
        for unit in units:
            if hasattr(unit, 'rune_berserker_active') and getattr(unit, 'rune_berserker_active', False):
                berserkers_in_queue.append({
                    'id': id(unit),
                    'type': getattr(unit, 'unit_type', None),
                    'pos': (getattr(unit, 'x', None), getattr(unit, 'y', None)),
                    'team': getattr(unit, 'team', None),
                    'turns': getattr(unit, 'rune_berserker_turns', 0)
                })
        
        if berserkers_in_queue:
            self.log('QUEUE_PREP',
                    f"Подготовка очереди: найдено {len(berserkers_in_queue)} берсерков",
                    None,
                    {'berserkers': berserkers_in_queue})
        
        # Проверяем всех юнитов на наличие флагов берсерка
        suspicious_units = []
        for unit in units:
            has_team_berserker = hasattr(unit, 'team') and isinstance(unit.team, str) and unit.team.startswith('berserker_')
            has_active_flag = getattr(unit, 'rune_berserker_active', False)
            has_turns = getattr(unit, 'rune_berserker_turns', 0) > 0
            
            # Подозрительно: есть команда берсерка, но нет активного флага
            if has_team_berserker and not has_active_flag:
                suspicious_units.append({
                    'id': id(unit),
                    'type': getattr(unit, 'unit_type', None),
                    'pos': (getattr(unit, 'x', None), getattr(unit, 'y', None)),
                    'team': getattr(unit, 'team', None),
                    'reason': 'team_berserker_but_no_active_flag'
                })
            
            # Подозрительно: есть активный флаг, но нет команды берсерка
            if has_active_flag and not has_team_berserker:
                suspicious_units.append({
                    'id': id(unit),
                    'type': getattr(unit, 'unit_type', None),
                    'pos': (getattr(unit, 'x', None), getattr(unit, 'y', None)),
                    'team': getattr(unit, 'team', None),
                    'reason': 'active_flag_but_no_berserker_team'
                })
        
        if suspicious_units:
            self.log('SUSPICIOUS_STATE',
                    f"Найдено {len(suspicious_units)} юнитов с подозрительным состоянием берсерка",
                    None,
                    {'suspicious': suspicious_units})
    
    def log_attribute_access(self, unit, attr_name, value, operation="get"):
        """Логирует доступ к атрибутам берсерка"""
        if 'berserker' in attr_name.lower():
            self.log('ATTR_ACCESS',
                    f"{operation.upper()} атрибута {attr_name} = {value}",
                    unit)
    
    def log_turn_start(self, unit, controller_type="unknown", controller_info=None):
        """
        Логирует начало хода юнита
        controller_type: 'player', 'ai', 'berserker', 'unknown'
        controller_info: дополнительная информация о контроллере
        """
        # Определяем, является ли юнит берсерком
        is_berserker = (hasattr(unit, 'rune_berserker_active') and 
                        getattr(unit, 'rune_berserker_active', False) and
                        getattr(unit, 'rune_berserker_turns', 0) > 0)
        
        # Определяем команду
        team = getattr(unit, 'team', None)
        team_type = "unknown"
        if isinstance(team, str):
            if team.startswith('berserker_'):
                team_type = "berserker"
            elif team in ['player1', 'player2']:
                team_type = "player"
            else:
                team_type = team
        
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        turn_info = {
            'timestamp': timestamp,
            'unit_id': id(unit),
            'unit_type': getattr(unit, 'unit_type', None),
            'position': (getattr(unit, 'x', None), getattr(unit, 'y', None)),
            'team': team,
            'team_type': team_type,
            'is_berserker': is_berserker,
            'controller_type': controller_type,
            'controller_info': controller_info or {},
            'rune_berserker_active': getattr(unit, 'rune_berserker_active', False),
            'rune_berserker_turns': getattr(unit, 'rune_berserker_turns', 0),
        }
        
        self.turn_history.append(turn_info)
        
        self.log('TURN_START',
                f"Начало хода | Контроллер: {controller_type} | Берсерк: {is_berserker} | Команда: {team_type}",
                unit,
                turn_info)
    
    def log_unit_action(self, unit, action_type, action_details=None):
        """
        Логирует действие юнита
        action_type: 'move', 'attack', 'wait', 'spell', 'defend', 'skip'
        action_details: детали действия (цель, позиция и т.д.)
        """
        is_berserker = (hasattr(unit, 'rune_berserker_active') and 
                       getattr(unit, 'rune_berserker_active', False))
        
        self.log('UNIT_ACTION',
                f"Действие: {action_type} | Берсерк: {is_berserker}",
                unit,
                {
                    'action_type': action_type,
                    'action_details': action_details or {},
                    'is_berserker': is_berserker,
                    'team': getattr(unit, 'team', None),
                })
    
    def log_controller_check(self, unit, controller_type, controller_name=None, reason=""):
        """
        Логирует проверку контроллера для юнита
        controller_type: 'player', 'ai', 'berserker', 'none'
        """
        is_berserker = (hasattr(unit, 'rune_berserker_active') and 
                       getattr(unit, 'rune_berserker_active', False) and
                       getattr(unit, 'rune_berserker_turns', 0) > 0)
        
        # Логируем только если это берсерк или есть подозрительная ситуация
        if is_berserker or controller_type == 'berserker' or controller_type == 'none':
            self.log('CONTROLLER_CHECK',
                    f"Проверка контроллера: {controller_type} | Имя: {controller_name} | Причина: {reason}",
                    unit,
                    {
                        'controller_type': controller_type,
                        'controller_name': controller_name,
                        'is_berserker': is_berserker,
                        'team': getattr(unit, 'team', None),
                        'rune_berserker_active': getattr(unit, 'rune_berserker_active', False),
                        'rune_berserker_turns': getattr(unit, 'rune_berserker_turns', 0),
                    })
    
    def log_ai_decision(self, unit, decision_type, decision_details=None):
        """
        Логирует решение AI для юнита
        decision_type: 'move', 'attack', 'wait', 'skip'
        """
        is_berserker = (hasattr(unit, 'rune_berserker_active') and 
                       getattr(unit, 'rune_berserker_active', False))
        
        # Логируем только если это берсерк (не должен управляться AI)
        if is_berserker:
            self.log('AI_DECISION_ON_BERSERKER',
                    f"⚠️ AI пытается управлять берсерком! Решение: {decision_type}",
                    unit,
                    {
                        'decision_type': decision_type,
                        'decision_details': decision_details or {},
                        'team': getattr(unit, 'team', None),
                    })
    
    def log_auto_action_without_berserker_flag(self, unit, action_type, reason=""):
        """
        Логирует автоматическое действие юнита, который НЕ имеет флага берсерка,
        но ведет себя как берсерк (критическая ошибка!)
        """
        has_berserker_team = (hasattr(unit, 'team') and 
                             isinstance(unit.team, str) and 
                             unit.team.startswith('berserker_'))
        has_berserker_flag = getattr(unit, 'rune_berserker_active', False)
        
        # Логируем если команда берсерка, но нет флага
        if has_berserker_team and not has_berserker_flag:
            self.log('AUTO_ACTION_WITHOUT_FLAG',
                    f"⚠️ КРИТИЧНО: Юнит выполняет автоматическое действие ({action_type}) с командой берсерка, но БЕЗ флага берсерка! | Причина: {reason}",
                    unit,
                    {
                        'action_type': action_type,
                        'team': getattr(unit, 'team', None),
                        'rune_berserker_active': has_berserker_flag,
                        'rune_berserker_turns': getattr(unit, 'rune_berserker_turns', 0),
                        'reason': reason
                    })
    
    def generate_report(self):
        """Генерирует отчет о проблемах"""
        report = []
        report.append("=" * 80)
        report.append("ОТЧЕТ О ДИАГНОСТИКЕ РУНЫ БЕРСЕРКА")
        report.append("=" * 80)
        report.append(f"Всего событий: {len(self.log_entries)}")
        report.append(f"Применений руны: {len(self.berserker_applications)}")
        report.append(f"Отслеживаемых юнитов: {len(self.unit_states)}")
        report.append("")
        
        # Анализ применений
        report.append("ПРИМЕНЕНИЯ РУНЫ БЕРСЕРКА:")
        report.append("-" * 80)
        for i, app in enumerate(self.berserker_applications, 1):
            report.append(f"{i}. {app['timestamp']} | {app['target_type']} @ {app['target_pos']} | "
                         f"Команда до: {app['target_team_before']} | ID: {app['target_id']}")
        report.append("")
        
        # Анализ подозрительных состояний
        report.append("ПОДОЗРИТЕЛЬНЫЕ СОСТОЯНИЯ:")
        report.append("-" * 80)
        suspicious_events = [e for e in self.log_entries if e['type'] == 'SUSPICIOUS_STATE']
        if suspicious_events:
            for event in suspicious_events:
                report.append(f"{event['timestamp']}: {event['message']}")
                if 'suspicious' in event['extra']:
                    for sus in event['extra']['suspicious']:
                        report.append(f"  - {sus['type']} @ {sus['pos']} | ID: {sus['id']} | "
                                     f"Команда: {sus['team']} | Причина: {sus['reason']}")
        else:
            report.append("Подозрительных состояний не обнаружено")
        report.append("")
        
        # Анализ изменений команд
        report.append("ИЗМЕНЕНИЯ КОМАНД:")
        report.append("-" * 80)
        team_changes = [e for e in self.log_entries if 'TEAM_CHANGE' in e['type']]
        for event in team_changes:
            report.append(f"{event['timestamp']}: {event['message']}")
        report.append("")
        
        # Состояния всех юнитов
        report.append("ИСТОРИЯ СОСТОЯНИЙ ЮНИТОВ:")
        report.append("-" * 80)
        for unit_id, states in self.unit_states.items():
            if any(s.get('rune_berserker_active') for s in states):
                report.append(f"\nЮнит ID: {unit_id}")
                for state in states:
                    if state.get('rune_berserker_active') or state.get('team', '').startswith('berserker_'):
                        report.append(f"  [{state['timestamp']}] {state['event']} | "
                                     f"Активен: {state.get('rune_berserker_active')} | "
                                     f"Ходов: {state.get('rune_berserker_turns')} | "
                                     f"Команда: {state.get('team')}")
        
        report.append("")
        
        # Анализ ходов
        report.append("АНАЛИЗ ХОДОВ ЮНИТОВ:")
        report.append("-" * 80)
        if self.turn_history:
            berserker_turns = [t for t in self.turn_history if t.get('is_berserker')]
            player_turns = [t for t in self.turn_history if t.get('controller_type') == 'player']
            ai_turns = [t for t in self.turn_history if t.get('controller_type') == 'ai']
            berserker_controlled_turns = [t for t in self.turn_history if t.get('controller_type') == 'berserker']
            
            report.append(f"Всего ходов отслежено: {len(self.turn_history)}")
            report.append(f"  - Ходов берсерков: {len(berserker_turns)}")
            report.append(f"  - Управлялись игроком: {len(player_turns)}")
            report.append(f"  - Управлялись AI: {len(ai_turns)}")
            report.append(f"  - Управлялись логикой берсерка: {len(berserker_controlled_turns)}")
            report.append("")
            
            # Проблемные случаи: берсерк управляется не берсерк-логикой
            problematic_turns = []
            for turn in berserker_turns:
                if turn.get('controller_type') != 'berserker' and turn.get('controller_type') != 'unknown':
                    problematic_turns.append(turn)
            
            if problematic_turns:
                report.append("⚠️ ПРОБЛЕМНЫЕ ХОДЫ (берсерк управляется не берсерк-логикой):")
                for turn in problematic_turns:
                    report.append(f"  [{turn.get('timestamp', '?')}] {turn.get('unit_type')} @ {turn.get('position')} | "
                                 f"Контроллер: {turn.get('controller_type')} | "
                                 f"Команда: {turn.get('team')}")
                report.append("")
            
            # Ходы с подозрительными контроллерами
            suspicious_controller_turns = [t for t in self.turn_history 
                                           if t.get('controller_type') == 'none' or 
                                           (t.get('is_berserker') and t.get('controller_type') == 'ai')]
            if suspicious_controller_turns:
                report.append("⚠️ ХОДЫ С ПОДОЗРИТЕЛЬНЫМИ КОНТРОЛЛЕРАМИ:")
                for turn in suspicious_controller_turns:
                    report.append(f"  [{turn.get('timestamp', '?')}] {turn.get('unit_type')} @ {turn.get('position')} | "
                                 f"Контроллер: {turn.get('controller_type')} | "
                                 f"Берсерк: {turn.get('is_berserker')} | "
                                 f"Команда: {turn.get('team')}")
                report.append("")
        else:
            report.append("Ходы не отслеживались")
        
        # Анализ действий
        report.append("АНАЛИЗ ДЕЙСТВИЙ:")
        report.append("-" * 80)
        actions = [e for e in self.log_entries if e['type'] == 'UNIT_ACTION']
        ai_on_berserker = [e for e in self.log_entries if e['type'] == 'AI_DECISION_ON_BERSERKER']
        
        if actions:
            report.append(f"Всего действий отслежено: {len(actions)}")
            action_types = {}
            for action in actions:
                action_type = action['extra'].get('action_type', 'unknown')
                action_types[action_type] = action_types.get(action_type, 0) + 1
            
            for action_type, count in action_types.items():
                report.append(f"  - {action_type}: {count}")
            report.append("")
        
        if ai_on_berserker:
            report.append(f"⚠️ КРИТИЧНО: AI пытался управлять берсерком {len(ai_on_berserker)} раз(а)!")
            for event in ai_on_berserker:
                report.append(f"  [{event['timestamp']}] {event['message']}")
            report.append("")
        
        # Анализ автоматических действий без флага берсерка
        auto_actions_without_flag = [e for e in self.log_entries if e['type'] == 'AUTO_ACTION_WITHOUT_FLAG']
        if auto_actions_without_flag:
            report.append(f"⚠️ КРИТИЧНО: Найдено {len(auto_actions_without_flag)} случаев автоматических действий без флага берсерка!")
            for event in auto_actions_without_flag:
                report.append(f"  [{event['timestamp']}] {event['message']}")
                if 'team' in event['extra']:
                    report.append(f"    Команда: {event['extra']['team']} | Флаг: {event['extra'].get('rune_berserker_active', False)}")
            report.append("")
        
        # Критические ошибки
        critical_errors = [e for e in self.log_entries if e['type'] == 'CRITICAL_ERROR']
        if critical_errors:
            report.append(f"🚨 КРИТИЧЕСКИЕ ОШИБКИ: Найдено {len(critical_errors)} критических ошибок!")
            for event in critical_errors:
                report.append(f"  [{event['timestamp']}] {event['message']}")
                if 'unit_type' in event['extra']:
                    report.append(f"    Юнит: {event['extra']['unit_type']} | Команда: {event['extra'].get('team', '?')} | "
                                 f"Флаг берсерка: {event['extra'].get('rune_berserker_active', False)}")
            report.append("")
        
        report.append("=" * 80)
        
        report_text = '\n'.join(report)
        
        # Сохраняем отчет
        report_file = self.log_file.replace('.log', '_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print("\n" + report_text)
        print(f"\nОтчет сохранен в: {report_file}")
        
        return report_text


# Глобальный экземпляр отладчика
_debugger = None

def get_debugger():
    """Получает глобальный экземпляр отладчика"""
    global _debugger
    if _debugger is None:
        _debugger = BerserkerDebugger()
    return _debugger

def enable_debugging():
    """Включает отладку"""
    get_debugger().enabled = True

def disable_debugging():
    """Выключает отладку"""
    get_debugger().enabled = False

def generate_report():
    """Генерирует отчет"""
    if _debugger:
        return _debugger.generate_report()
    return "Отладчик не инициализирован"


if __name__ == '__main__':
    print("Диагностическая программа для руны берсерка")
    print("=" * 80)
    print("\nЭта программа создает патчи для отслеживания проблем с берсерком.")
    print("Она будет логировать все операции с берсерком в игре.")
    print("\nДля использования:")
    print("1. Импортируйте этот модуль в game/spells.py и game/core.py")
    print("2. Добавьте вызовы логирования в ключевых местах")
    print("3. Запустите игру и примените руну берсерка")
    print("4. Проверьте файл berserker_debug.log и berserker_debug_report.txt")
    print("\n" + "=" * 80)

