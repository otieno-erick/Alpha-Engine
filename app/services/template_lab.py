from __future__ import annotations

from typing import Any


class TemplateLab:
    """Simple template expansion helper for Phase 5 tool generation."""

    def __init__(self):
        self.templates: dict[str, str] = {}

    def add_template(self, name: str, template: str) -> None:
        self.templates[name] = template

    def expand(self, name: str, fields: list[str], windows: list[int], groups: list[str]) -> list[dict[str, Any]]:
        template = self.templates.get(name)
        if template is None:
            raise KeyError(f"Template '{name}' not found")

        expanded: list[dict[str, Any]] = []
        for field in fields:
            for window in windows:
                for group in groups:
                    expanded.append(
                        {
                            "name": name,
                            "field": field,
                            "window": window,
                            "group": group,
                            "expression": template.format(field=field, window=window, group=group),
                        }
                    )
        return expanded

    def preview_count(self, name: str, fields: list[str], windows: list[int], groups: list[str]) -> int:
        return len(self.expand(name, fields, windows, groups))
