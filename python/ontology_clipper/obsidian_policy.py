"""Base Obsidian ontology policy and safe vault write helpers.

The policy is derived from `/Users/Shared/Notes/Daniel/The relation to Obsidian.md`:
use one vault, prefer reusable/list-like properties, plural `categories` and
`tags`, internal links for durable entities, `YYYY-MM-DD` dates, and cautious
file-over-app writes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import os
import re
import tempfile
from typing import Any, Mapping

from .frontmatter import render_frontmatter
from .ontology import ensure_list, normalize_property, tags as normalize_tags, wikilink_list

FRONTMATTER_RE = re.compile(r"\A---\n(?P<frontmatter>.*?)\n---\n?", re.S)

PACKAGE_NAME = "obsidian-ontology-skills"
AUDIT_TAG = f"modified/{PACKAGE_NAME}"
DEFAULT_VAULT_PATH = Path("/Users/Shared/Notes")

# Raw URL/media/source fields must remain strings/URLs, never wikilinks.
RAW_URL_FIELDS = frozenset({"source", "url", "image", "cover", "poster", "thumbnail", "imdb", "website", "links", "instagram"})

# These durable entity fields are list-like by policy even when only one value is present.
LIST_ENTITY_FIELDS = frozenset(
    {
        "author",
        "authors",
        "director",
        "directors",
        "writer",
        "writers",
        "cast",
        "actors",
        "artist",
        "artists",
        "host",
        "hosts",
        "guests",
        "company",
        "companies",
        "organization",
        "organizations",
        "location",
        "locations",
        "loc",
        "place",
        "places",
        "genre",
        "genres",
        "topic",
        "topics",
        "show",
        "channel",
        "country",
        "language",
        "production",
    }
)


@dataclass(frozen=True)
class OperationPolicy:
    """Explicit file operation capabilities for vault writes."""

    create: bool = False
    update: bool = True
    delete: bool = False
    create_parent_dirs: bool = False
    atomic: bool = True


def today_iso(today: str | date | None = None) -> str:
    if isinstance(today, date):
        return today.isoformat()
    return today or date.today().isoformat()


def resolve_vault_path(vault_path: str | Path | None = None) -> Path:
    """Resolve the concrete vault path used by file tools and CLIs."""

    if vault_path:
        return Path(vault_path).expanduser().resolve()
    env_path = os.environ.get("OBSIDIAN_VAULT_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return DEFAULT_VAULT_PATH


def _dedupe(values: list[Any]) -> list[Any]:
    out: list[Any] = []
    for value in values:
        if value not in out:
            out.append(value)
    return out


def normalize_tags_property(value: Any, audit: bool = True) -> list[str]:
    normalized = [tag.lower() for tag in normalize_tags(value)]
    if audit and AUDIT_TAG not in normalized:
        normalized.append(AUDIT_TAG)
    return _dedupe(normalized)


def normalize_categories(properties: Mapping[str, Any]) -> dict[str, Any]:
    """Return properties with singular `category` folded into list `categories`."""

    normalized = dict(properties)
    values: list[Any] = []
    if "category" in normalized:
        values.extend(ensure_list(normalized.pop("category")))
    if "categories" in normalized:
        values.extend(ensure_list(normalized["categories"]))
    if values:
        normalized["categories"] = wikilink_list(values)
    return normalized


def _normalize_list_entity(field: str, value: Any) -> Any:
    if field in RAW_URL_FIELDS:
        return value
    if field == "categories":
        return wikilink_list(value)
    if field in LIST_ENTITY_FIELDS:
        normalized = normalize_property(field, value)
        if isinstance(normalized, list):
            return normalized
        return [normalized] if normalized else []
    return normalize_property(field, value)


def apply_obsidian_policy(
    properties: Mapping[str, Any],
    *,
    skill_name: str,
    today: str | date | None = None,
    audit: bool = True,
) -> dict[str, Any]:
    """Normalize frontmatter according to the base Obsidian ontology policy."""

    normalized = normalize_categories(properties)
    if "tag" in normalized and "tags" not in normalized:
        normalized["tags"] = normalized.pop("tag")
    elif "tag" in normalized:
        tag_values = ensure_list(normalized.pop("tag")) + ensure_list(normalized.get("tags"))
        normalized["tags"] = tag_values

    for key, value in list(normalized.items()):
        if key == "tags":
            normalized[key] = normalize_tags_property(value, audit=audit)
        elif key in {"modified", "modifiedBy", "modifiedVia"}:
            normalized[key] = value
        else:
            normalized[key] = _normalize_list_entity(key, value)

    if audit:
        normalized["modified"] = today_iso(today)
        normalized["modifiedBy"] = skill_name
        normalized["modifiedVia"] = PACKAGE_NAME
        if "tags" not in normalized:
            normalized["tags"] = normalize_tags_property([], audit=True)
        elif AUDIT_TAG not in normalized["tags"]:
            normalized["tags"] = normalize_tags_property(normalized["tags"], audit=True)
    return normalized


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def parse_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    """Parse the simple YAML frontmatter produced by this package."""

    match = FRONTMATTER_RE.match(markdown)
    if not match:
        return {}, markdown
    frontmatter = match.group("frontmatter")
    body = markdown[match.end():]
    parsed: dict[str, Any] = {}
    current_key = ""
    for line in frontmatter.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            parsed.setdefault(current_key, []).append(_unquote(line[4:].strip()))
            continue
        if ":" in line:
            key, raw = line.split(":", 1)
            current_key = key.strip()
            raw = raw.strip()
            parsed[current_key] = [] if raw == "" else _unquote(raw)
    return parsed, body


def merge_properties(existing: Mapping[str, Any], updates: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    for key, value in updates.items():
        if isinstance(value, list):
            if value:
                merged[key] = value
        elif value is not None and str(value).strip() != "":
            merged[key] = value
    return merged


def merge_note_frontmatter(
    markdown: str,
    updates: Mapping[str, Any],
    *,
    skill_name: str,
    today: str | date | None = None,
    audit: bool = True,
) -> str:
    existing, body = parse_frontmatter(markdown)
    merged = merge_properties(existing, updates)
    normalized = apply_obsidian_policy(merged, skill_name=skill_name, today=today, audit=audit)
    return render_frontmatter(normalized) + "\n" + body.lstrip("\n")


def read_note(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_note(path: str | Path, content: str, policy: OperationPolicy | None = None, *, delete: bool = False) -> Path:
    """Write or delete a note using explicit operation capabilities.

    `create=False` refuses missing files and missing parent directories. Atomic
    writes keep Obsidian notes from being left half-written if an operation fails.
    """

    policy = policy or OperationPolicy()
    target = Path(path)

    if delete:
        if not policy.delete:
            raise PermissionError(f"delete not allowed by policy: {target}")
        target.unlink(missing_ok=True)
        return target

    exists = target.exists()
    if not exists and not policy.create:
        raise FileNotFoundError(f"create not allowed by policy: {target}")
    if not exists and not target.parent.exists():
        if policy.create_parent_dirs:
            target.parent.mkdir(parents=True, exist_ok=True)
        else:
            raise FileNotFoundError(f"parent directory does not exist: {target.parent}")
    if exists and not policy.update:
        raise PermissionError(f"update not allowed by policy: {target}")

    if policy.atomic:
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(content)
            if policy.create and not policy.update and not exists:
                os.link(tmp_name, target)
                Path(tmp_name).unlink()
            else:
                os.replace(tmp_name, target)
        finally:
            tmp = Path(tmp_name)
            if tmp.exists():
                tmp.unlink()
    else:
        target.write_text(content, encoding="utf-8")
    return target
