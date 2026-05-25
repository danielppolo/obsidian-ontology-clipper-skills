"""Note model and deterministic markdown rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import re
from typing import Any

from .frontmatter import render_frontmatter
from .obsidian_policy import apply_obsidian_policy


def slug_title(value: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|#^\[\]]+', " ", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "Untitled"


@dataclass
class Note:
    title: str
    source: str
    body: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    path: str = "Clippings"
    skill_name: str = "obsidian-web-clipper-core"

    def normalized_properties(self) -> dict[str, Any]:
        props: dict[str, Any] = {
            "title": self.title,
            "source": self.source,
            "created": date.today().isoformat(),
        }
        props.update(self.properties)
        return apply_obsidian_policy(props, skill_name=self.skill_name)

    def filename(self) -> str:
        return slug_title(self.title) + ".md"

    def render(self) -> str:
        body = self.body.strip()
        frontmatter = render_frontmatter(self.normalized_properties())
        return frontmatter + ("\n" + body + "\n" if body else "")
