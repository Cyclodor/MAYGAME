"""
Система валидации состояния игры
Проверяет корректность данных, состояний и логики игры
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

from .logger import get_logger, LogCategory, LogLevel


class ValidationSeverity(Enum):
    """Уровень серьезности проблемы валидации"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ValidationIssue:
    """Проблема, обнаруженная валидатором"""
    
    def __init__(self,
                 severity: ValidationSeverity,
                 category: str,
                 message: str,
                 details: Optional[Dict[str, Any]] = None):
        self.severity = severity
        self.category = category
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"ValidationIssue({self.severity.value}, {self.category}, {self.message})"


class GameValidator:
    """Валидатор состояния игры"""
    
    def __init__(self):
        """Инициализация валидатора"""
        self.logger = get_logger()
        self.issues: List[ValidationIssue] = []
        self.validation_rules: Dict[str, List[Callable]] = {}
        self.max_issues = 1000
        
        self.logger.info(LogCategory.VALIDATION, "Валидатор инициализирован")
    
    def register_rule(self, category: str, rule_func: Callable):
        """
        Регистрация правила валидации
        
        Args:
            category: Категория правила
            rule_func: Функция-правило, должна возвращать ValidationIssue или None
        """
        if category not in self.validation_rules:
            self.validation_rules[category] = []
        self.validation_rules[category].append(rule_func)
    
    def validate_unit(self, unit) -> List[ValidationIssue]:
        """
        Валидация юнита
        
        Args:
            unit: Объект юнита
            
        Returns:
            Список найденных проблем
        """
        issues = []
        
        # Проверка базовых атрибутов
        if not hasattr(unit, 'x') or not hasattr(unit, 'y'):
            issues.append(ValidationIssue(
                ValidationSeverity.CRITICAL,
                'unit_position',
                'Юнит не имеет координат x, y',
                {'unit_type': getattr(unit, 'unit_type', 'Unknown')}
            ))
        else:
            x, y = getattr(unit, 'x'), getattr(unit, 'y')
            if x < 0 or y < 0:
                issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    'unit_position',
                    f'Юнит имеет отрицательные координаты: ({x}, {y})',
                    {'unit_type': getattr(unit, 'unit_type', 'Unknown'), 'x': x, 'y': y}
                ))
        
        # Проверка здоровья
        if hasattr(unit, 'health') and hasattr(unit, 'max_health'):
            health = getattr(unit, 'health', 0)
            max_health = getattr(unit, 'max_health', 1)
            
            if health < 0:
                issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    'unit_health',
                    f'Юнит имеет отрицательное здоровье: {health}',
                    {'unit_type': getattr(unit, 'unit_type', 'Unknown'), 'health': health}
                ))
            
            if health > max_health:
                issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    'unit_health',
                    f'Здоровье юнита превышает максимум: {health} > {max_health}',
                    {'unit_type': getattr(unit, 'unit_type', 'Unknown'), 'health': health, 'max_health': max_health}
                ))
        
        # Проверка команды
        if hasattr(unit, 'team'):
            team = getattr(unit, 'team', None)
            if team is None:
                issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    'unit_team',
                    'Юнит не имеет команды',
                    {'unit_type': getattr(unit, 'unit_type', 'Unknown')}
                ))
        
        # Проверка состояния берсерка (если применимо)
        if hasattr(unit, 'rune_berserker_active'):
            is_berserker = getattr(unit, 'rune_berserker_active', False)
            team = getattr(unit, 'team', None)
            
            if is_berserker:
                if not isinstance(team, str) or not team.startswith('berserker_'):
                    issues.append(ValidationIssue(
                        ValidationSeverity.ERROR,
                        'berserker_state',
                        'Юнит имеет флаг берсерка, но команда не соответствует',
                        {
                            'unit_type': getattr(unit, 'unit_type', 'Unknown'),
                            'rune_berserker_active': is_berserker,
                            'team': team,
                        }
                    ))
        
        return issues
    
    def validate_game_state(self, game) -> List[ValidationIssue]:
        """
        Валидация состояния игры
        
        Args:
            game: Объект игры
            
        Returns:
            Список найденных проблем
        """
        issues = []
        
        # Проверка юнитов
        if hasattr(game, 'units'):
            for unit in game.units:
                unit_issues = self.validate_unit(unit)
                issues.extend(unit_issues)
                
                # Проверка на дубликаты позиций
                for other_unit in game.units:
                    if unit != other_unit:
                        if (hasattr(unit, 'x') and hasattr(unit, 'y') and
                            hasattr(other_unit, 'x') and hasattr(other_unit, 'y')):
                            if (getattr(unit, 'x') == getattr(other_unit, 'x') and
                                getattr(unit, 'y') == getattr(other_unit, 'y')):
                                issues.append(ValidationIssue(
                                    ValidationSeverity.ERROR,
                                    'unit_position',
                                    'Два юнита находятся на одной клетке',
                                    {
                                        'unit1_type': getattr(unit, 'unit_type', 'Unknown'),
                                        'unit2_type': getattr(other_unit, 'unit_type', 'Unknown'),
                                        'position': (getattr(unit, 'x'), getattr(unit, 'y')),
                                    }
                                ))
        
        # Проверка очереди ходов
        if hasattr(game, 'turn_queue'):
            if game.turn_queue:
                # Проверяем, что все юниты в очереди существуют
                for unit in game.turn_queue:
                    if unit is not None and hasattr(game, 'units'):
                        if unit not in game.units and not hasattr(unit, '_round_delimiter'):
                            issues.append(ValidationIssue(
                                ValidationSeverity.ERROR,
                                'turn_queue',
                                'Юнит в очереди ходов не найден в списке юнитов',
                                {'unit_type': getattr(unit, 'unit_type', 'Unknown')}
                            ))
        
        # Проверка выбранного юнита
        if hasattr(game, 'selected_unit') and game.selected_unit:
            if hasattr(game, 'units') and game.selected_unit not in game.units:
                issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    'selected_unit',
                    'Выбранный юнит не найден в списке юнитов',
                    {'unit_type': getattr(game.selected_unit, 'unit_type', 'Unknown')}
                ))
        
        return issues
    
    def validate_spell(self, spell, caster, target=None) -> List[ValidationIssue]:
        """
        Валидация заклинания
        
        Args:
            spell: Объект заклинания
            caster: Кастер заклинания
            target: Цель заклинания (опционально)
            
        Returns:
            Список найденных проблем
        """
        issues = []
        
        # Проверка кастера
        if caster is None:
            issues.append(ValidationIssue(
                ValidationSeverity.CRITICAL,
                'spell_caster',
                'Кастер заклинания отсутствует',
            ))
        else:
            caster_issues = self.validate_unit(caster)
            issues.extend(caster_issues)
        
        # Проверка цели (если требуется)
        if target is not None:
            target_issues = self.validate_unit(target)
            issues.extend(target_issues)
        
        # Проверка наличия необходимых атрибутов заклинания
        if not hasattr(spell, 'icon') and not hasattr(spell, 'name'):
            issues.append(ValidationIssue(
                ValidationSeverity.WARNING,
                'spell_attributes',
                'Заклинание не имеет имени или иконки',
            ))
        
        return issues
    
    def add_issue(self, issue: ValidationIssue):
        """
        Добавить проблему валидации
        
        Args:
            issue: Проблема валидации
        """
        self.issues.append(issue)
        
        # Ограничиваем количество проблем
        if len(self.issues) > self.max_issues:
            self.issues = self.issues[-self.max_issues:]
        
        # Логируем проблему
        log_level = {
            ValidationSeverity.INFO: LogLevel.DEBUG,
            ValidationSeverity.WARNING: LogLevel.WARNING,
            ValidationSeverity.ERROR: LogLevel.ERROR,
            ValidationSeverity.CRITICAL: LogLevel.CRITICAL,
        }[issue.severity]
        
        if log_level == LogLevel.DEBUG:
            self.logger.debug(LogCategory.VALIDATION, 
                             f"[{issue.category}] {issue.message}",
                             issue.details)
        elif log_level == LogLevel.WARNING:
            self.logger.warning(LogCategory.VALIDATION, 
                               f"[{issue.category}] {issue.message}",
                               issue.details)
        elif log_level == LogLevel.ERROR:
            self.logger.error(LogCategory.VALIDATION, 
                            f"[{issue.category}] {issue.message}",
                            issue.details)
        elif log_level == LogLevel.CRITICAL:
            self.logger.critical(LogCategory.VALIDATION, 
                               f"[{issue.category}] {issue.message}",
                               issue.details)
    
    def validate_all(self, game) -> List[ValidationIssue]:
        """
        Выполнить все проверки валидации
        
        Args:
            game: Объект игры
            
        Returns:
            Список всех найденных проблем
        """
        all_issues = []
        
        # Валидация состояния игры
        game_issues = self.validate_game_state(game)
        all_issues.extend(game_issues)
        
        # Выполнение зарегистрированных правил
        for category, rules in self.validation_rules.items():
            for rule_func in rules:
                try:
                    issue = rule_func(game)
                    if issue is not None:
                        if isinstance(issue, ValidationIssue):
                            all_issues.append(issue)
                        elif isinstance(issue, list):
                            all_issues.extend(issue)
                except Exception as e:
                    self.logger.error(
                        LogCategory.VALIDATION,
                        f"Ошибка выполнения правила валидации {category}: {e}",
                        exception=e
                    )
        
        # Добавляем все проблемы
        for issue in all_issues:
            self.add_issue(issue)
        
        return all_issues
    
    def get_issues(self, 
                   severity: Optional[ValidationSeverity] = None,
                   category: Optional[str] = None) -> List[ValidationIssue]:
        """
        Получить проблемы валидации
        
        Args:
            severity: Фильтр по уровню серьезности
            category: Фильтр по категории
            
        Returns:
            Список проблем
        """
        issues = self.issues
        
        if severity:
            issues = [i for i in issues if i.severity == severity]
        
        if category:
            issues = [i for i in issues if i.category == category]
        
        return issues
    
    def get_issues_summary(self) -> Dict[str, Any]:
        """Получить сводку проблем валидации"""
        summary = {
            'total': len(self.issues),
            'by_severity': {},
            'by_category': {},
        }
        
        for severity in ValidationSeverity:
            count = len(self.get_issues(severity=severity))
            summary['by_severity'][severity.value] = count
        
        # Группируем по категориям
        categories = set(i.category for i in self.issues)
        for category in categories:
            count = len(self.get_issues(category=category))
            summary['by_category'][category] = count
        
        return summary
    
    def clear_issues(self):
        """Очистить все проблемы валидации"""
        self.issues.clear()
        self.logger.debug(LogCategory.VALIDATION, "Проблемы валидации очищены")


# Глобальный экземпляр валидатора
_validator_instance: Optional[GameValidator] = None


def get_validator() -> GameValidator:
    """Получить глобальный экземпляр валидатора"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = GameValidator()
    return _validator_instance


def initialize_validator() -> GameValidator:
    """Инициализировать валидатор"""
    global _validator_instance
    _validator_instance = GameValidator()
    return _validator_instance

