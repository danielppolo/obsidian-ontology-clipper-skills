"""Deterministic metadata extraction from saved HTML."""

from __future__ import annotations

from html.parser import HTMLParser
import json
from typing import Any


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.in_title = False
        self.in_json_ld = False
        self.current_script: list[str] = []
        self.meta: dict[str, str] = {}
        self.json_ld: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): v or "" for k, v in attrs}
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            key = attrs_dict.get("property") or attrs_dict.get("name")
            content = attrs_dict.get("content")
            if key and content:
                self.meta[key.lower()] = content
        elif tag == "script" and attrs_dict.get("type", "").lower() == "application/ld+json":
            self.in_json_ld = True
            self.current_script = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_json_ld:
            raw = "".join(self.current_script).strip()
            self.in_json_ld = False
            if raw:
                self._parse_json_ld(raw)

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_json_ld:
            self.current_script.append(data)

    def _parse_json_ld(self, raw: str) -> None:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return
        items = parsed if isinstance(parsed, list) else [parsed]
        for item in items:
            if isinstance(item, dict):
                if "@graph" in item and isinstance(item["@graph"], list):
                    self.json_ld.extend(x for x in item["@graph"] if isinstance(x, dict))
                else:
                    self.json_ld.append(item)


def extract_metadata(html: str) -> dict[str, Any]:
    parser = MetadataParser()
    parser.feed(html)
    title = parser.meta.get("og:title") or " ".join(parser.title_parts).strip()
    description = parser.meta.get("og:description") or parser.meta.get("description", "")
    author = parser.meta.get("author") or parser.meta.get("article:author", "")
    image = parser.meta.get("og:image") or parser.meta.get("twitter:image", "")
    return {
        "title": title,
        "description": description,
        "author": author,
        "image": image,
        "meta": parser.meta,
        "json_ld": parser.json_ld,
    }


def first_schema(metadata: dict[str, Any], schema_type: str | None = None) -> dict[str, Any]:
    for item in metadata.get("json_ld", []):
        item_type = item.get("@type")
        types = item_type if isinstance(item_type, list) else [item_type]
        if schema_type is None or schema_type in types:
            return item
    return {}
