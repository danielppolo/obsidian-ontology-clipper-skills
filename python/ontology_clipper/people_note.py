"""Helpers for updating existing Obsidian people notes from Google Contacts."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import json
import re
from typing import Any, Mapping

from .frontmatter import render_frontmatter
from .ontology import normalize_wikilink, tags, wikilink_list


Contact = Mapping[str, Any]


NA_VALUES = {"", "N/A", "n/a", "na", "None", "none"}
FRONTMATTER_RE = re.compile(r"\A---\n(?P<frontmatter>.*?)\n---\n?", re.S)


def is_missing(value: Any) -> bool:
    return value is None or str(value).strip() in NA_VALUES


def clean_text(value: Any) -> str:
    if is_missing(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def ensure_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple | set):
        return list(value)
    return [value]


def unique_clean(values: Any) -> list[str]:
    out: list[str] = []
    for value in ensure_list(values):
        text = clean_text(value)
        if text and text not in out:
            out.append(text)
    return out


def _items(contact: Contact, key: str) -> list[Mapping[str, Any]]:
    values = contact.get(key)
    return [item for item in ensure_list(values) if isinstance(item, Mapping)]


def contact_name(contact: Contact) -> str:
    names = _items(contact, "names")
    for item in names:
        for key in ("displayName", "unstructuredName", "givenName"):
            value = clean_text(item.get(key))
            if value:
                return value
    for key in ("name", "displayName", "title"):
        value = clean_text(contact.get(key))
        if value:
            return value
    return ""


def contact_aliases(contact: Contact) -> list[str]:
    aliases: list[str] = []
    for item in _items(contact, "names"):
        for key in ("displayName", "unstructuredName", "givenName", "familyName", "nickname"):
            value = clean_text(item.get(key))
            if value and value not in aliases and value != contact_name(contact):
                aliases.append(value)
    for key in ("aliases", "nicknames"):
        aliases.extend(value for value in unique_clean(contact.get(key)) if value not in aliases)
    return aliases


def contact_emails(contact: Contact) -> list[str]:
    values = unique_clean(contact.get("emails"))
    values.extend(clean_text(item.get("value")) for item in _items(contact, "emailAddresses"))
    return unique_clean(values)


def contact_phones(contact: Contact) -> list[str]:
    values = unique_clean(contact.get("phones"))
    values.extend(clean_text(item.get("value")) for item in _items(contact, "phoneNumbers"))
    return unique_clean(values)


def contact_urls(contact: Contact) -> list[str]:
    values: list[str] = []
    for key in ("links", "urls"):
        for item in ensure_list(contact.get(key)):
            if isinstance(item, Mapping):
                continue
            text = clean_text(item)
            if text:
                values.append(text)
    values.extend(clean_text(item.get("value")) for item in _items(contact, "urls"))
    values.extend(clean_text(item.get("url")) for item in _items(contact, "urls"))
    return unique_clean(values)


def _user_defined(contact: Contact) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in _items(contact, "userDefined"):
        key = clean_text(item.get("key")).lower()
        value = clean_text(item.get("value"))
        if key and value:
            result[key] = value
    for item in _items(contact, "metadata"):
        key = clean_text(item.get("key")).lower()
        value = clean_text(item.get("value"))
        if key and value:
            result[key] = value
    return result


def instagram_from_contact(contact: Contact) -> str:
    user_defined = _user_defined(contact)
    value = clean_text(contact.get("instagram") or user_defined.get("instagram") or user_defined.get("ig"))
    urls = contact_urls(contact)
    if not value:
        for url in urls:
            if "instagram.com" in url.lower():
                value = url
                break
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    handle = value.lstrip("@/").strip()
    return f"https://instagram.com/{handle}" if handle else ""


def birthday_from_contact(contact: Contact) -> str:
    direct = clean_text(contact.get("birthday"))
    if direct:
        return direct
    for item in _items(contact, "birthdays"):
        text = clean_text(item.get("text"))
        if text:
            return text
        value = item.get("date")
        if isinstance(value, Mapping):
            year = value.get("year")
            month = value.get("month")
            day = value.get("day")
            if month and day:
                if year:
                    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
                return f"{int(month):02d}-{int(day):02d}"
    return ""


def organizations_from_contact(contact: Contact) -> tuple[list[str], str]:
    companies: list[str] = []
    for key in ("companies", "organizations"):
        for item in ensure_list(contact.get(key)):
            if isinstance(item, Mapping):
                continue
            text = clean_text(item)
            if text and text not in companies:
                companies.append(text)
    title = clean_text(contact.get("jobTitle"))
    for org in _items(contact, "organizations"):
        name = clean_text(org.get("name"))
        if name and name not in companies:
            companies.append(name)
        if not title:
            title = clean_text(org.get("title"))
    return companies, title


def locations_from_contact(contact: Contact) -> list[str]:
    values = unique_clean(contact.get("locations") or contact.get("location"))
    for item in _items(contact, "addresses"):
        text = clean_text(item.get("formattedValue") or item.get("city") or item.get("region") or item.get("country"))
        if text and text not in values:
            values.append(text)
    return values


def _add_if_present(properties: dict[str, Any], key: str, value: Any) -> None:
    if isinstance(value, list):
        if value:
            properties[key] = value
    elif not is_missing(value):
        properties[key] = value


def person_properties(contact: Contact, updated_date: str | date | None = None) -> dict[str, Any]:
    """Build ontology-first properties from a Google Contacts/People contact.

    The resulting properties are intended to be merged into an existing person
    note. They are not sufficient reason to create a new note.
    """

    today = updated_date.isoformat() if isinstance(updated_date, date) else updated_date or date.today().isoformat()
    name = contact_name(contact)
    companies, job_title = organizations_from_contact(contact)
    properties: dict[str, Any] = {
        "categories": [normalize_wikilink("People")],
        "name": name,
        "source": "Google Contacts",
        "updated": today,
        "tags": tags(["people"]),
    }
    _add_if_present(properties, "aliases", contact_aliases(contact))
    _add_if_present(properties, "email", contact_emails(contact))
    _add_if_present(properties, "phone", contact_phones(contact))
    _add_if_present(properties, "links", contact_urls(contact))
    _add_if_present(properties, "instagram", instagram_from_contact(contact))
    _add_if_present(properties, "birthday", birthday_from_contact(contact))
    _add_if_present(properties, "company", wikilink_list(companies))
    _add_if_present(properties, "jobTitle", job_title)
    _add_if_present(properties, "location", wikilink_list(locations_from_contact(contact)))
    notes = "\n\n".join(clean_text(item.get("value")) for item in _items(contact, "biographies") if clean_text(item.get("value")))
    _add_if_present(properties, "contactNotes", notes)
    return properties


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


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def merge_properties(existing: Mapping[str, Any], updates: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    for key, value in updates.items():
        if isinstance(value, list):
            if value:
                merged[key] = value
        elif not is_missing(value):
            merged[key] = value
    return merged


def merge_frontmatter(markdown: str, updates: Mapping[str, Any]) -> str:
    existing, body = parse_frontmatter(markdown)
    merged = merge_properties(existing, updates)
    return render_frontmatter(merged) + "\n" + body.lstrip("\n")


def timeline_entry(
    day: str,
    text: str,
    people: list[str] | None = None,
    places: list[str] | None = None,
    entities: list[str] | None = None,
) -> str:
    pieces = [f"- [[{day}]] — {clean_text(text)}"]
    people_links = wikilink_list(people or [])
    place_links = wikilink_list(places or [])
    entity_links = wikilink_list(entities or [])
    extras = []
    if people_links:
        extras.append("people: " + ", ".join(people_links))
    if place_links:
        extras.append("places: " + ", ".join(place_links))
    if entity_links:
        extras.append("entities: " + ", ".join(entity_links))
    if extras:
        pieces.append(" (" + "; ".join(extras) + ")")
    return "".join(pieces)


def append_timeline_entry(markdown: str, entry: str, heading: str = "## Timeline") -> str:
    clean_entry = entry.rstrip()
    if clean_entry in markdown:
        return markdown
    if heading in markdown:
        return markdown.rstrip() + "\n" + clean_entry + "\n"
    return markdown.rstrip() + f"\n\n{heading}\n{clean_entry}\n"


def update_existing_person_markdown(
    markdown: str,
    contact: Contact | None = None,
    timeline: str | None = None,
    updated_date: str | date | None = None,
) -> str:
    updated = markdown
    if contact:
        updated = merge_frontmatter(updated, person_properties(contact, updated_date=updated_date))
    if timeline:
        updated = append_timeline_entry(updated, timeline)
    return updated


def load_contact_json(path: Path) -> Contact:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        if not data or not isinstance(data[0], Mapping):
            raise ValueError("contact JSON list must contain a contact object")
        return data[0]
    if isinstance(data, Mapping):
        return data
    raise ValueError("contact JSON must be an object or a list of contact objects")
