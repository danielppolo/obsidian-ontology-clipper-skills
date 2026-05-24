"""Small YAML-ish frontmatter renderer for Obsidian properties."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping


def _escape_scalar(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _needs_quotes(value: str) -> bool:
    if value == "":
        return True
    special = (":", "#", "[", "]", "{", "}", ",", "&", "*", "!", "|", ">", "@", "`", '"', "'")
    return value.strip() != value or any(ch in value for ch in special)


def render_scalar(value: Any) -> str:
    if value is None:
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, date | datetime):
        return value.isoformat()[:10]
    text = str(value)
    if _needs_quotes(text):
        return f'"{_escape_scalar(text)}"'
    return text


def render_frontmatter(properties: Mapping[str, Any]) -> str:
    lines = ["---"]
    for key, value in properties.items():
        if isinstance(value, list | tuple | set):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {render_scalar(item)}")
        else:
            lines.append(f"{key}: {render_scalar(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"
