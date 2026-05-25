"""Ontology and wikilink helpers for Obsidian clipping."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Any, Iterable
from urllib.parse import urlparse


class EntityType(StrEnum):
    PERSON = "Person"
    PLACE = "Place"
    ORGANIZATION = "Organization"
    CREATIVE_WORK = "CreativeWork"
    MOVIE = "Movie"
    BOOK = "Book"
    PODCAST = "Podcast"
    PODCAST_EPISODE = "PodcastEpisode"
    VIDEO = "Video"
    EVENT = "Event"
    WEB_ARTICLE = "WebArticle"
    CONVERSATION = "Conversation"
    GENRE = "Genre"
    TOPIC = "Topic"
    CATEGORY = "Category"
    SOURCE = "Source"


@dataclass(frozen=True)
class Entity:
    name: str
    entity_type: EntityType
    alias: str | None = None

    def wikilink(self) -> str:
        return normalize_wikilink(self.alias or self.name)


FIELD_ENTITY_TYPES: dict[str, EntityType] = {
    "author": EntityType.PERSON,
    "authors": EntityType.PERSON,
    "director": EntityType.PERSON,
    "directors": EntityType.PERSON,
    "writer": EntityType.PERSON,
    "writers": EntityType.PERSON,
    "publisher": EntityType.ORGANIZATION,
    "publishers": EntityType.ORGANIZATION,
    "company": EntityType.ORGANIZATION,
    "companies": EntityType.ORGANIZATION,
    "organization": EntityType.ORGANIZATION,
    "organizations": EntityType.ORGANIZATION,
    "production": EntityType.ORGANIZATION,
    "cast": EntityType.PERSON,
    "actors": EntityType.PERSON,
    "loc": EntityType.PLACE,
    "location": EntityType.PLACE,
    "locations": EntityType.PLACE,
    "place": EntityType.PLACE,
    "show": EntityType.PODCAST,
    "channel": EntityType.ORGANIZATION,
    "genre": EntityType.GENRE,
    "genres": EntityType.GENRE,
    "language": EntityType.TOPIC,
    "languages": EntityType.TOPIC,
    "country": EntityType.PLACE,
    "countries": EntityType.PLACE,
    "topics": EntityType.TOPIC,
    "topic": EntityType.TOPIC,
    "categories": EntityType.CATEGORY,
    "category": EntityType.CATEGORY,
}

WIKILINK_FIELDS = frozenset(FIELD_ENTITY_TYPES)
URLISH = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)
WIKILINK_RE = re.compile(r"^\s*\[\[(?P<body>.+?)\]\]\s*$")


def compact_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def strip_existing_wikilink(value: str) -> str:
    match = WIKILINK_RE.match(value)
    if not match:
        return value
    body = match.group("body")
    return body.split("|", 1)[0].strip()


def normalize_entity_name(value: Any) -> str:
    if value is None:
        return ""
    text = compact_whitespace(str(value))
    text = strip_existing_wikilink(text)
    if URLISH.match(text):
        parsed = urlparse(text)
        text = parsed.netloc or text
    text = text.strip("[]")
    text = text.replace("\n", " ")
    return compact_whitespace(text)


def normalize_wikilink(value: Any) -> str:
    """Return a single Obsidian wikilink or an empty string.

    The function avoids double-wrapping, trims whitespace, and turns URL values
    into host labels so source URLs do not become unusable note names.
    """

    name = normalize_entity_name(value)
    if not name:
        return ""
    return f"[[{name}]]"


def split_people_like(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in re.split(r"\s*(?:,|;|\band\b)\s*", value) if part.strip()]


def ensure_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple | set):
        return list(value)
    return [value]


def wikilink_list(values: Any) -> list[str]:
    linked: list[str] = []
    for value in ensure_list(values):
        if isinstance(value, str) and "," in value and not value.strip().startswith("[["):
            candidates: Iterable[Any] = split_people_like(value)
        else:
            candidates = [value]
        for candidate in candidates:
            link = normalize_wikilink(candidate)
            if link and link not in linked:
                linked.append(link)
    return linked


def field_should_wikilink(field_name: str) -> bool:
    return field_name in WIKILINK_FIELDS


def normalize_property(field_name: str, value: Any) -> Any:
    if not field_should_wikilink(field_name):
        return value
    if isinstance(value, list | tuple | set):
        return wikilink_list(value)
    return normalize_wikilink(value)


def tags(value: str | Iterable[str]) -> list[str]:
    values = [value] if isinstance(value, str) else list(value)
    out: list[str] = []
    for item in values:
        for tag in str(item).split(","):
            clean = tag.strip().lstrip("#")
            if clean and clean not in out:
                out.append(clean)
    return out
