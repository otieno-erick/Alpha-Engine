from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


VECTOR_FIELD_PATTERN = re.compile(r"\bvec_[A-Za-z0-9_]+\b")
FIELD_PATTERN = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]


class Validator:
    def __init__(self, allowed_fields: Optional[Tuple[str, ...]] = None):
        self.allowed_fields = allowed_fields or tuple()

    def validate_expression(self, expression: str) -> ValidationResult:
        errors: List[str] = []
        if not expression or not expression.strip():
            errors.append("expression is empty")
        if not re.fullmatch(r"[0-9A-Za-z_\s\+\-\*/\(\)\.,=<>\[\]{}:]*", expression):
            errors.append("expression contains unsupported characters")
        if expression.count("(") != expression.count(")"):
            errors.append("expression has mismatched parentheses")
        if re.search(r"\bvec_\w+\b", expression) and "vec_" not in expression:
            errors.append("vector fields must use a vec_ operator")
        # field-access check
        fields = set(FIELD_PATTERN.findall(expression))
        forbidden = [field for field in fields if field.startswith("vec_") and field not in self.allowed_fields]
        if forbidden:
            errors.append(f"unknown vector field(s): {', '.join(sorted(forbidden))}")
        return ValidationResult(valid=not errors, errors=errors)

    def validate_settings(self, settings: Dict[str, Any]) -> ValidationResult:
        errors: List[str] = []
        window = settings.get("window")
        if window is not None and window not in {5, 10, 21, 63, 121, 252}:
            errors.append("window value is outside the allowed grid")
        if settings.get("operators") is not None and settings["operators"] > 8:
            errors.append("operator count exceeds the Power Pool limit")
        return ValidationResult(valid=not errors, errors=errors)


DEFAULT_VALIDATOR = Validator()
