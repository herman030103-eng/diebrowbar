"""
Движок правил для обработки писем
Rules engine for email processing
"""
from typing import Dict, List, Optional
import re

from src.rules_engine.database import Database
from src.utils.logger import logger


class RulesEngine:
    """Движок для применения пользовательских правил к письмам"""
    
    # Типы правил
    RULE_TYPES = {
        "FILTER": "Фильтр",
        "DELETE": "Удаление",
        "MOVE": "Перемещение",
        "ARCHIVE": "Архивирование"
    }
    
    # Операторы сравнения
    OPERATORS = {
        "equals": "равно",
        "contains": "содержит",
        "starts_with": "начинается с",
        "ends_with": "заканчивается на",
        "regex": "регулярное выражение",
        "not_equals": "не равно",
        "not_contains": "не содержит"
    }
    
    # Поля для условий
    CONDITION_FIELDS = {
        "sender": "Отправитель",
        "subject": "Тема",
        "body": "Тело письма",
        "category": "Категория"
    }
    
    # Типы действий
    ACTION_TYPES = {
        "delete": "Удалить",
        "move": "Переместить в папку",
        "archive": "Архивировать",
        "mark_read": "Пометить как прочитанное",
        "skip": "Пропустить обработку"
    }
    
    def __init__(self, database: Database):
        self.db = database
        logger.info("Движок правил инициализирован")
    
    def apply_rules(self, email_data: Dict, classification: Dict) -> Dict:
        """
        Применение правил к письму
        
        Args:
            email_data: данные письма
            classification: результат классификации
        
        Returns:
            {
                "action": "delete|move|archive|skip|none",
                "destination": "folder_name" (для move),
                "matched_rules": [rule_ids],
                "reasoning": "объяснение"
            }
        """
        rules = self.db.get_all_rules(enabled_only=True)
        
        if not rules:
            return {
                "action": "none",
                "destination": None,
                "matched_rules": [],
                "reasoning": "Нет активных правил"
            }
        
        # Подготовка данных для проверки
        check_data = {
            "sender": email_data.get("sender", ""),
            "subject": email_data.get("subject", ""),
            "body": email_data.get("body", ""),
            "category": classification.get("category", "")
        }
        
        matched_rules = []
        final_action = None
        final_destination = None
        
        # Проверка каждого правила (по приоритету)
        for rule in rules:
            if self._check_condition(check_data, rule):
                matched_rules.append(rule["id"])
                
                # Определение действия
                action_type = rule["action_type"]
                action_value = rule["action_value"]
                
                # Первое сработавшее правило определяет действие
                if final_action is None:
                    if action_type == "delete":
                        final_action = "delete"
                    elif action_type == "move":
                        final_action = "move"
                        final_destination = action_value
                    elif action_type == "archive":
                        final_action = "archive"
                    elif action_type == "skip":
                        final_action = "skip"
                    
                    logger.info(f"Сработало правило ID {rule['id']}: {action_type}")
        
        result = {
            "action": final_action or "none",
            "destination": final_destination,
            "matched_rules": matched_rules,
            "reasoning": self._get_reasoning(matched_rules, rules)
        }
        
        return result
    
    def _check_condition(self, data: Dict, rule: Dict) -> bool:
        """Проверка условия правила"""
        field = rule["condition_field"]
        operator = rule["condition_operator"]
        value = rule["condition_value"]
        
        if field not in data:
            return False
        
        field_value = str(data[field]).lower()
        compare_value = str(value).lower()
        
        try:
            if operator == "equals":
                return field_value == compare_value
            elif operator == "contains":
                return compare_value in field_value
            elif operator == "starts_with":
                return field_value.startswith(compare_value)
            elif operator == "ends_with":
                return field_value.endswith(compare_value)
            elif operator == "regex":
                return bool(re.search(compare_value, field_value, re.IGNORECASE))
            elif operator == "not_equals":
                return field_value != compare_value
            elif operator == "not_contains":
                return compare_value not in field_value
            else:
                logger.warning(f"Неизвестный оператор: {operator}")
                return False
        except Exception as e:
            logger.error(f"Ошибка проверки условия: {e}")
            return False
    
    def _get_reasoning(self, matched_rule_ids: List[int], all_rules: List[Dict]) -> str:
        """Формирование объяснения"""
        if not matched_rule_ids:
            return "Правила не сработали"
        
        explanations = []
        for rule_id in matched_rule_ids:
            rule = next((r for r in all_rules if r["id"] == rule_id), None)
            if rule:
                field = self.CONDITION_FIELDS.get(rule["condition_field"], rule["condition_field"])
                operator = self.OPERATORS.get(rule["condition_operator"], rule["condition_operator"])
                value = rule["condition_value"]
                action = self.ACTION_TYPES.get(rule["action_type"], rule["action_type"])
                
                explanations.append(f"{field} {operator} '{value}' → {action}")
        
        return "; ".join(explanations)
    
    def create_rule_from_command(self, command: str) -> Optional[int]:
        """
        Создание правила из текстовой команды
        
        Примеры:
        - "всё от amazon.com удалять"
        - "письма с темой 'реклама' перемещать в Promo"
        - "от newsletter@example.com архивировать"
        """
        try:
            command = command.lower().strip()
            
            # Паттерны для разных типов команд
            patterns = [
                # "всё от X удалять"
                (r"вс[её] от (.+?) удал", "sender", "contains", "delete"),
                # "всё что реклама в папку X"
                (r"вс[её] что (.+?) в папку (.+)", "subject", "contains", "move"),
                # "письма с темой X перемещать в Y"
                (r"письма с темой ['\"](.+?)['\"] перемещать в (.+)", "subject", "contains", "move"),
                # "от X архивировать"
                (r"от (.+?) архивир", "sender", "contains", "archive"),
                # "категория X в папку Y"
                (r"категория (.+?) в папку (.+)", "category", "equals", "move"),
            ]
            
            for pattern, field, operator, action in patterns:
                match = re.search(pattern, command)
                if match:
                    if action == "move":
                        condition_value = match.group(1)
                        action_value = match.group(2)
                    else:
                        condition_value = match.group(1)
                        action_value = None
                    
                    rule_id = self.db.add_rule(
                        rule_type="FILTER",
                        condition_field=field,
                        condition_operator=operator,
                        condition_value=condition_value,
                        action_type=action,
                        action_value=action_value,
                        priority=0
                    )
                    
                    logger.info(f"Создано правило из команды: '{command}' -> ID {rule_id}")
                    return rule_id
            
            logger.warning(f"Не удалось распознать команду: {command}")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка создания правила из команды: {e}")
            return None
    
    def get_rules_summary(self) -> str:
        """Получение краткого описания всех правил"""
        rules = self.db.get_all_rules(enabled_only=True)
        
        if not rules:
            return "Нет активных правил"
        
        summary = [f"Активных правил: {len(rules)}\n"]
        
        for rule in rules[:10]:  # Первые 10 правил
            field = self.CONDITION_FIELDS.get(rule["condition_field"], rule["condition_field"])
            operator = self.OPERATORS.get(rule["condition_operator"], rule["condition_operator"])
            value = rule["condition_value"]
            action = self.ACTION_TYPES.get(rule["action_type"], rule["action_type"])
            action_value = rule["action_value"]
            
            rule_desc = f"• {field} {operator} '{value}' → {action}"
            if action_value:
                rule_desc += f" ({action_value})"
            
            summary.append(rule_desc)
        
        if len(rules) > 10:
            summary.append(f"\n... и ещё {len(rules) - 10} правил")
        
        return "\n".join(summary)
