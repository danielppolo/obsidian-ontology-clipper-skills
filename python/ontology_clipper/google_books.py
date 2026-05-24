"""Small stdlib Google Books client used by the book note skill."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, NotRequired, TypedDict
from urllib.parse import urlencode
from urllib.request import urlopen


GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1/volumes"


class IndustryIdentifier(TypedDict, total=False):
    type: str
    identifier: str


class ImageLinks(TypedDict, total=False):
    thumbnail: str
    smallThumbnail: str


class VolumeInfo(TypedDict, total=False):
    title: str
    subtitle: str
    authors: list[str]
    publisher: str
    publishedDate: str
    description: str
    pageCount: int
    categories: list[str]
    language: str
    previewLink: str
    infoLink: str
    imageLinks: ImageLinks
    averageRating: float
    ratingsCount: int
    maturityRating: str
    industryIdentifiers: list[IndustryIdentifier]


class BookSearchResult(TypedDict):
    id: str
    volumeInfo: VolumeInfo


class BookDetails(TypedDict, total=False):
    Title: str
    Subtitle: str
    Authors: str
    Publisher: str
    PublishedDate: str
    Description: str
    PageCount: str
    Categories: str
    Language: str
    ISBN10: str
    ISBN13: str
    PreviewLink: str
    InfoLink: str
    Thumbnail: str
    SmallThumbnail: str
    AverageRating: str
    RatingsCount: str
    MaturityRating: str
    VolumeID: NotRequired[str]


@dataclass(frozen=True)
class GoogleBooksError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


def build_google_books_url(params: dict[str, str], api_key: str | None = None) -> str:
    query = dict(params)
    if api_key:
        query["key"] = api_key
    encoded = urlencode(query)
    return f"{GOOGLE_BOOKS_BASE_URL}?{encoded}" if encoded else GOOGLE_BOOKS_BASE_URL


def _get_json(url: str) -> dict[str, Any]:
    try:
        with urlopen(url, timeout=20) as response:  # noqa: S310 - user-provided CLI utility.
            raw = response.read().decode(
                response.headers.get_content_charset() or "utf-8",
                errors="replace",
            )
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise GoogleBooksError("Google Books returned invalid JSON.") from error
    except OSError as error:
        raise GoogleBooksError("Failed to reach Google Books. Check your internet connection.") from error
    if not isinstance(data, dict):
        raise GoogleBooksError("Google Books returned an unexpected response.")
    return data


def search_books(query: str, api_key: str | None = None) -> list[BookSearchResult]:
    clean_query = query.strip()
    if not clean_query:
        raise GoogleBooksError("Book title, author, or ISBN is required.")
    url = build_google_books_url({"q": clean_query, "maxResults": "40"}, api_key)
    data = _get_json(url)
    items = data.get("items")
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict) and isinstance(item.get("volumeInfo"), dict)]  # type: ignore[list-item]


def get_book_details(volume_id: str, api_key: str | None = None) -> BookDetails:
    clean_id = volume_id.strip()
    if not clean_id:
        raise GoogleBooksError("Google Books volume id is required.")
    params = {"key": api_key} if api_key else {}
    encoded = urlencode(params)
    url = f"{GOOGLE_BOOKS_BASE_URL}/{clean_id}"
    if encoded:
        url = f"{url}?{encoded}"
    data = _get_json(url)
    if not isinstance(data.get("volumeInfo"), dict):
        raise GoogleBooksError("Book not found.")
    return transform_book_data(data)  # type: ignore[arg-type]


def _string(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def transform_book_data(volume: BookSearchResult) -> BookDetails:
    info = volume.get("volumeInfo") or {}
    isbn10 = ""
    isbn13 = ""
    for identifier in info.get("industryIdentifiers") or []:
        if not isinstance(identifier, dict):
            continue
        if identifier.get("type") == "ISBN_10":
            isbn10 = _string(identifier.get("identifier"))
        elif identifier.get("type") == "ISBN_13":
            isbn13 = _string(identifier.get("identifier"))
    image_links = info.get("imageLinks") or {}
    details: BookDetails = {
        "Title": _string(info.get("title")),
        "Subtitle": _string(info.get("subtitle")),
        "Authors": ", ".join(info.get("authors") or []),
        "Publisher": _string(info.get("publisher")),
        "PublishedDate": _string(info.get("publishedDate")),
        "Description": _string(info.get("description")),
        "PageCount": _string(info.get("pageCount")),
        "Categories": ", ".join(info.get("categories") or []),
        "Language": _string(info.get("language")),
        "ISBN10": isbn10,
        "ISBN13": isbn13,
        "PreviewLink": _string(info.get("previewLink")),
        "InfoLink": _string(info.get("infoLink")),
        "Thumbnail": _string(image_links.get("thumbnail")) if isinstance(image_links, dict) else "",
        "SmallThumbnail": _string(image_links.get("smallThumbnail")) if isinstance(image_links, dict) else "",
        "AverageRating": _string(info.get("averageRating")),
        "RatingsCount": _string(info.get("ratingsCount")),
        "MaturityRating": _string(info.get("maturityRating")),
        "VolumeID": _string(volume.get("id")),
    }
    return details


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def _published_year(value: str) -> str:
    match = re.search(r"\d{4}", value)
    return match.group(0) if match else ""


def choose_best_result(
    results: list[BookSearchResult],
    query: str,
    year: int | str | None = None,
    author: str | None = None,
) -> BookSearchResult | None:
    """Choose a deterministic Google Books search result.

    Preference order rewards normalized title/query match, requested year,
    requested author, then falls back to Google Books' first result.
    """

    if not results:
        return None
    wanted_title = _normalize(query)
    wanted_year = str(year) if year is not None else ""
    wanted_author = _normalize(author or "")

    def score(result: BookSearchResult) -> tuple[int, int]:
        info = result.get("volumeInfo") or {}
        title = _normalize(str(info.get("title") or ""))
        subtitle = _normalize(str(info.get("subtitle") or ""))
        published = str(info.get("publishedDate") or "")
        authors = [_normalize(str(item)) for item in info.get("authors") or []]
        points = 0
        if title == wanted_title:
            points += 60
        elif wanted_title and (wanted_title in title or wanted_title in f"{title} {subtitle}".strip()):
            points += 35
        if wanted_year and _published_year(published) == wanted_year:
            points += 25
        if wanted_author and any(wanted_author == item or wanted_author in item for item in authors):
            points += 20
        return points, -results.index(result)

    return max(results, key=score)
