"""Render ontology-first Obsidian notes from Google Books details."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import re
from typing import Any

from .frontmatter import render_frontmatter
from .google_books import BookDetails
from .obsidian_policy import apply_obsidian_policy
from .ontology import normalize_wikilink, tags, wikilink_list


NA_VALUES = {"", "N/A", "n/a", "na", "None", "none"}


def is_missing(value: Any) -> bool:
    return value is None or str(value).strip() in NA_VALUES


def clean_text(value: Any) -> str:
    if is_missing(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def split_list(value: Any) -> list[str]:
    text = clean_text(value)
    if not text:
        return []
    return [part.strip() for part in re.split(r"\s*(?:,|;|\band\b)\s*", text) if part.strip()]


def split_category_list(value: Any) -> list[str]:
    text = clean_text(value)
    if not text:
        return []
    return [part.strip() for part in re.split(r"\s*(?:,|;|/)\s*", text) if part.strip()]


def parse_year(value: Any) -> int | str:
    match = re.search(r"\d{4}", clean_text(value))
    return int(match.group(0)) if match else clean_text(value)


def parse_int(value: Any) -> int | str:
    text = clean_text(value)
    return int(text) if text.isdigit() else text


def sanitize_filename(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]+', "", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "Untitled"


def book_filename(details: BookDetails) -> str:
    title = clean_text(details.get("Title")) or "Untitled"
    authors = clean_text(details.get("Authors"))
    stem = f"{title} - {authors}" if authors else title
    return sanitize_filename(stem) + ".md"


def unique_note_path(
    vault: Path,
    folder: str,
    filename: str,
    overwrite: bool = False,
    duplicate_timestamp: str | datetime | None = None,
) -> Path:
    target_dir = vault / folder if folder else vault
    target = target_dir / filename
    if overwrite or not target.exists():
        return target
    if isinstance(duplicate_timestamp, datetime):
        timestamp = duplicate_timestamp.isoformat(timespec="seconds").replace(":", "-")
    else:
        timestamp = duplicate_timestamp or datetime.now().isoformat(timespec="seconds").replace(":", "-")
    stem = target.stem
    suffix = target.suffix or ".md"
    candidate = target.with_name(f"{stem} {timestamp}{suffix}")
    counter = 2
    while candidate.exists():
        candidate = target.with_name(f"{stem} {timestamp}-{counter}{suffix}")
        counter += 1
    return candidate


def _url_if_available(value: Any) -> str:
    return clean_text(value)


def _add_if_present(properties: dict[str, Any], key: str, value: Any) -> None:
    if not is_missing(value):
        properties[key] = value


def _language_property(value: Any) -> str | list[str]:
    language = clean_text(value)
    if not language:
        return ""
    if re.fullmatch(r"[a-z]{2,3}", language):
        return language
    return wikilink_list([language])


def book_properties(
    details: BookDetails,
    read: bool = False,
    created_date: str | date | None = None,
) -> dict[str, Any]:
    today = created_date.isoformat() if isinstance(created_date, date) else created_date or date.today().isoformat()
    isbn10 = clean_text(details.get("ISBN10"))
    isbn13 = clean_text(details.get("ISBN13"))
    cover = _url_if_available(details.get("Thumbnail")) or _url_if_available(details.get("SmallThumbnail"))
    properties: dict[str, Any] = {
        "categories": [normalize_wikilink("Books")],
        "title": clean_text(details.get("Title")) or "Untitled",
        "author": wikilink_list(split_list(details.get("Authors"))),
        "publisher": wikilink_list(split_list(details.get("Publisher"))),
        "genre": wikilink_list(split_category_list(details.get("Categories"))),
        "pages": parse_int(details.get("PageCount")),
        "year": parse_year(details.get("PublishedDate")),
        "published": clean_text(details.get("PublishedDate")),
        "scoreGoogle": clean_text(details.get("AverageRating")),
        "rating": "",
        "cover": cover,
        "isbn": isbn13 or isbn10,
        "created": today,
        "last": today if read else "",
        "tags": tags(["books", "references", "read" if read else "to-read"]),
    }
    _add_if_present(properties, "subtitle", clean_text(details.get("Subtitle")))
    _add_if_present(properties, "isbn10", isbn10)
    _add_if_present(properties, "isbn13", isbn13)
    _add_if_present(properties, "language", _language_property(details.get("Language")))
    _add_if_present(properties, "description", clean_text(details.get("Description")))
    _add_if_present(properties, "previewLink", _url_if_available(details.get("PreviewLink")))
    _add_if_present(properties, "infoLink", _url_if_available(details.get("InfoLink")))
    _add_if_present(properties, "maturityRating", clean_text(details.get("MaturityRating")))
    _add_if_present(properties, "ratingsCount", parse_int(details.get("RatingsCount")))
    return properties


def _detail_line(label: str, value: str | int | list[str]) -> str:
    if isinstance(value, list):
        value = ", ".join(value)
    return f"- **{label}:** {value}" if value != "" else ""


def render_book_note(
    details: BookDetails,
    read: bool = False,
    created_date: str | date | None = None,
) -> str:
    properties = apply_obsidian_policy(
        book_properties(details, read=read, created_date=created_date),
        skill_name="obsidian-create-book-note",
        today=created_date,
    )
    frontmatter = render_frontmatter(properties)
    title = properties["title"]
    subtitle = clean_text(details.get("Subtitle"))
    rating = clean_text(details.get("AverageRating"))
    ratings_count = clean_text(details.get("RatingsCount"))
    rating_text = f"{rating}/5 ({ratings_count} ratings)" if rating and ratings_count else rating
    lines = [
        f"# {title}",
        f"## {subtitle}" if subtitle else "",
        "",
        "## Description",
        clean_text(details.get("Description")),
        "",
        "## Details",
        _detail_line("Authors", properties.get("author", [])),
        _detail_line("Publisher", properties.get("publisher", [])),
        _detail_line("Published", clean_text(details.get("PublishedDate"))),
        _detail_line("Pages", parse_int(details.get("PageCount"))),
        _detail_line("Categories", properties.get("genre", [])),
        _detail_line("Language", properties.get("language", "")),
        _detail_line("ISBN-10", clean_text(details.get("ISBN10"))),
        _detail_line("ISBN-13", clean_text(details.get("ISBN13"))),
        _detail_line("Rating", rating_text),
    ]
    body = "\n".join(line for line in lines if line != "").strip()
    return frontmatter + "\n" + body + "\n"
