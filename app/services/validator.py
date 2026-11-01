from __future__ import annotations

import re
from typing import Any


def validate_expression(
    expression: str,
    *,
    allowed_windows: list[int] | None = None,
    vector_fields: list[str] | None = None,
    max_operators: int = 8,
    max_unique_fields: int = 3,
    window: int | None = None,
) -> dict[str, Any]:
    expr = (expression or "").strip()
    if not expr:
        raise ValueError("Expression is empty.")

    allowed = allowed_windows or [5, 10, 21, 63, 121, 252]
    if window is not None and window not in allowed:
        raise ValueError(f"Window {window} is not allowed by the parameter grid.")

    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)
    vectors = {field.strip() for field in (vector_fields or [])}
    if any(token in vectors for token in tokens if token not in {"vec", "vec_"}):
        if "vec_" not in expr:
            raise ValueError("Vector fields used without a vec_ operator.")

    field_matches = [token for token in tokens if token not in {"vec", "vec_", "and", "or", "if", "not"}]
    if len(set(field_matches)) > max_unique_fields:
        raise ValueError("Too many unique fields for the current rules.")

    operator_count = len(re.findall(r"\b(?:rank|lag|lead|delta|trend|zscore|short|long|vec_)\b", expr.lower()))
    if operator_count > max_operators:
        raise ValueError("Operator count exceeds the Power Pool limit.")

    return {"valid": True, "expression": expr, "field_count": len(set(field_matches))}
