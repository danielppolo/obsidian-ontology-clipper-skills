"""Render ontology-first Obsidian notes from OMDB movie details."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import re
from typing import Any

from .frontmatter import render_frontmatter
from .obsidian_policy import apply_obsidian_policy
from .omdb import MovieDetails
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


def split_credit_list(value: Any) -> list[str]:
    credits: list[str] = []
    for part in split_list(value):
        clean = re.sub(r"\s*\([^)]*\)\s*$", "", part).strip()
        if clean and clean not in credits:
            credits.append(clean)
    return credits


def parse_year(value: Any) -> int | str:
    match = re.search(r"\d{4}", clean_text(value))
    return int(match.group(0)) if match else clean_text(value)


def sanitize_filename(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]+', "", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "Untitled"


def movie_filename(details: MovieDetails) -> str:
    title = clean_text(details.get("Title")) or "Untitled"
    year = clean_text(details.get("Year"))
    stem = f"{title} ({year})" if year else title
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


def _plain_if_available(value: Any) -> str:
    return clean_text(value)


def _url_if_available(value: Any) -> str:
    text = clean_text(value)
    return text if text and text != "N/A" else ""


def _add_if_present(properties: dict[str, Any], key: str, value: Any) -> None:
    if not is_missing(value):
        properties[key] = value


def movie_properties(
    details: MovieDetails,
    watched: bool = True,
    created_date: str | date | None = None,
) -> dict[str, Any]:
    today = created_date.isoformat() if isinstance(created_date, date) else created_date or date.today().isoformat()
    imdb_id = clean_text(details.get("imdbID"))
    poster = _url_if_available(details.get("Poster"))
    website = _url_if_available(details.get("Website"))
    properties: dict[str, Any] = {
        "title": clean_text(details.get("Title")) or "Untitled",
        "categories": [normalize_wikilink("Movies")],
        "genre": wikilink_list(split_list(details.get("Genre"))),
        "director": wikilink_list(split_credit_list(details.get("Director"))),
        "writer": wikilink_list(split_credit_list(details.get("Writer"))),
        "cast": wikilink_list(split_credit_list(details.get("Actors"))[:5]),
        "rating": "",
        "scoreImdb": _plain_if_available(details.get("imdbRating")),
        "cover": poster,
        "plot": _plain_if_available(details.get("Plot")),
        "created": today,
        "last": today if watched else "",
        "year": parse_year(details.get("Year")),
        "imdbId": imdb_id,
        "imdb": f"https://www.imdb.com/title/{imdb_id}" if imdb_id else "",
        "tags": tags(["movies", "references", "watched" if watched else "to-watch"]),
    }
    optional_plain = {
        "runtime": details.get("Runtime"),
        "rated": details.get("Rated"),
        "released": details.get("Released"),
        "awards": details.get("Awards"),
        "metascore": details.get("Metascore"),
        "boxOffice": details.get("BoxOffice"),
        "website": website,
        "imdbVotes": details.get("imdbVotes"),
        "type": details.get("Type"),
        "dvd": details.get("DVD"),
    }
    for key, value in optional_plain.items():
        _add_if_present(properties, key, _plain_if_available(value))
    language = wikilink_list(split_list(details.get("Language")))
    country = wikilink_list(split_list(details.get("Country")))
    production = wikilink_list(split_list(details.get("Production")))
    if language:
        properties["language"] = language
    if country:
        properties["country"] = country
    if production:
        properties["production"] = production
    return properties


def _detail_line(label: str, value: str | list[str]) -> str:
    if isinstance(value, list):
        value = ", ".join(value)
    return f"- **{label}:** {value}" if value else ""


def render_movie_note(
    details: MovieDetails,
    watched: bool = True,
    created_date: str | date | None = None,
) -> str:
    properties = apply_obsidian_policy(
        movie_properties(details, watched=watched, created_date=created_date),
        skill_name="obsidian-create-movie-note",
        today=created_date,
    )
    frontmatter = render_frontmatter(properties)
    title = properties["title"]
    year = properties.get("year") or ""
    actors = wikilink_list(split_credit_list(details.get("Actors")))
    lines = [
        f"# {title} ({year})".rstrip(),
        "",
        "## Plot",
        clean_text(details.get("Plot")),
        "",
        "## Details",
        _detail_line("Director", properties.get("director", [])),
        _detail_line("Writer", properties.get("writer", [])),
        _detail_line("Actors", actors),
        _detail_line("Genre", properties.get("genre", [])),
        _detail_line("Runtime", clean_text(details.get("Runtime"))),
        _detail_line("Rated", clean_text(details.get("Rated"))),
        _detail_line("Released", clean_text(details.get("Released"))),
        _detail_line(
            "IMDb Rating",
            f"{clean_text(details.get('imdbRating'))}/10 ({clean_text(details.get('imdbVotes'))} votes)"
            if clean_text(details.get("imdbRating"))
            else "",
        ),
        _detail_line("Metascore", clean_text(details.get("Metascore"))),
        _detail_line("Box Office", clean_text(details.get("BoxOffice"))),
        _detail_line("Awards", clean_text(details.get("Awards"))),
    ]
    body = "\n".join(line for line in lines if line != "").strip()
    return frontmatter + "\n" + body + "\n"
