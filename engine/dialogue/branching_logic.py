"""Branching logic for conditional dialogue."""

import re
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class Condition:
    """Represents a condition for branching."""

    variable: str
    operator: str  # ==, !=, <, >, <=, >=
    value: Any

    def evaluate(self, variables: Dict[str, Any]) -> bool:
        """Evaluate condition with given variables."""
        if self.variable not in variables:
            return False

        var_value = variables[self.variable]

        if self.operator == "==":
            return var_value == self.value
        elif self.operator == "!=":
            return var_value != self.value
        elif self.operator == "<":
            return var_value < self.value
        elif self.operator == ">":
            return var_value > self.value
        elif self.operator == "<=":
            return var_value <= self.value
        elif self.operator == ">=":
            return var_value >= self.value
        elif self.operator == "in":
            return var_value in self.value
        elif self.operator == "not_in":
            return var_value not in self.value
        elif self.operator == "contains":
            return self.value in str(var_value)

        return False


class BranchingLogic:
    """Logic for evaluating dialogue conditions."""

    @staticmethod
    def parse_condition(condition_str: str) -> Optional[Condition]:
        """Parse condition string like 'health > 50'."""
        # Match pattern: variable operator value
        pattern = r'(\w+)\s*(==|!=|<|>|<=|>=|in|not_in|contains)\s*(.+)'
        match = re.match(pattern, condition_str.strip())

        if not match:
            return None

        variable, operator, value_str = match.groups()

        # Try to parse value
        value = BranchingLogic._parse_value(value_str.strip())

        return Condition(variable, operator, value)

    @staticmethod
    def _parse_value(value_str: str) -> Any:
        """Parse value string to appropriate type."""
        value_str = value_str.strip()

        # Try integer
        try:
            return int(value_str)
        except ValueError:
            pass

        # Try float
        try:
            return float(value_str)
        except ValueError:
            pass

        # Try boolean
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False

        # Try list
        if value_str.startswith("[") and value_str.endswith("]"):
            items_str = value_str[1:-1]
            items = [BranchingLogic._parse_value(item.strip()) for item in items_str.split(",")]
            return items

        # String
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]

        return value_str

    @staticmethod
    def evaluate_condition(condition_str: str, variables: Dict[str, Any]) -> bool:
        """Evaluate condition string."""
        condition = BranchingLogic.parse_condition(condition_str)
        if not condition:
            return False
        return condition.evaluate(variables)

    @staticmethod
    def evaluate_complex_condition(condition_str: str, variables: Dict[str, Any]) -> bool:
        """Evaluate complex condition with AND/OR operators."""
        # Split by OR
        or_parts = condition_str.split(" OR ")
        for or_part in or_parts:
            # Split by AND
            and_parts = or_part.split(" AND ")
            all_true = True
            for and_part in and_parts:
                if not BranchingLogic.evaluate_condition(and_part.strip(), variables):
                    all_true = False
                    break
            if all_true:
                return True
        return False

    @staticmethod
    def set_variable(variables: Dict[str, Any], var_name: str, value: Any) -> None:
        """Set variable value."""
        variables[var_name] = value

    @staticmethod
    def increment_variable(variables: Dict[str, Any], var_name: str, amount: int = 1) -> None:
        """Increment variable."""
        if var_name not in variables:
            variables[var_name] = 0
        variables[var_name] += amount

    @staticmethod
    def add_flag(variables: Dict[str, Any], flag_name: str) -> None:
        """Add boolean flag."""
        variables[flag_name] = True

    @staticmethod
    def remove_flag(variables: Dict[str, Any], flag_name: str) -> None:
        """Remove boolean flag."""
        if flag_name in variables:
            del variables[flag_name]

    @staticmethod
    def has_flag(variables: Dict[str, Any], flag_name: str) -> bool:
        """Check if flag exists."""
        return flag_name in variables and variables[flag_name]
