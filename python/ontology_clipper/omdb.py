"""Small stdlib OMDB client used by the movie note skill."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, NotRequired, TypedDict
from urllib.parse import urlencode
from urllib.request import urlopen


OMDB_BASE_URL = "https://www.omdbapi.com/"


class MovieSearchResult(TypedDict):
    Title: str
    Year: str
    imdbID: str
    Type: str
    Poster: str


class MovieDetails(TypedDict, total=False):
    Title: str
    Year: str
    Rated: str
    Released: str
    Runtime: str
    Genre: str
    Director: str
    Writer: str
    Actors: str
    Plot: str
    Language: str
    Country: str
    Awards: str
    Poster: str
    Ratings: list[dict[str, str]]
    Metascore: str
    imdbRating: str
    imdbVotes: str
    imdbID: str
    Type: str
    DVD: str
    BoxOffice: str
    Production: str
    Website: str
    Response: str
    Error: NotRequired[str]


@dataclass(frozen=True)
class OMDBError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


def build_omdb_url(params: dict[str, str], api_key: str) -> str:
    if not api_key:
        raise OMDBError("OMDB API key is required.")
    query = {"apikey": api_key, **params}
    return f"{OMDB_BASE_URL}?{urlencode(query)}"


def _get_json(url: str) -> dict[str, Any]:
    try:
        with urlopen(url, timeout=20) as response:  # noqa: S310 - user-provided CLI utility.
            raw = response.read().decode(
                response.headers.get_content_charset() or "utf-8",
                errors="replace",
            )
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise OMDBError("OMDB returned invalid JSON.") from error
    except OSError as error:
        raise OMDBError("Failed to reach OMDB. Check your internet connection and API key.") from error
    if not isinstance(data, dict):
        raise OMDBError("OMDB returned an unexpected response.")
    return data


def search_movies(title: str, api_key: str) -> list[MovieSearchResult]:
    """Search OMDB for movies by title, mirroring the plugin's type=movie query."""

    clean_title = title.strip()
    if not clean_title:
        raise OMDBError("Movie title is required.")
    url = build_omdb_url({"s": clean_title, "type": "movie"}, api_key)
    data = _get_json(url)
    if data.get("Response") == "False":
        if data.get("Error") == "Movie not found!":
            return []
        raise OMDBError(str(data.get("Error") or "Unknown OMDB error."))
    results = data.get("Search")
    if not isinstance(results, list):
        return []
    return [item for item in results if isinstance(item, dict)]  # type: ignore[list-item]


def get_movie_details(imdb_id: str, api_key: str) -> MovieDetails:
    """Fetch full OMDB movie details by IMDb id with plot=full."""

    clean_id = imdb_id.strip()
    if not clean_id:
        raise OMDBError("IMDb id is required.")
    url = build_omdb_url({"i": clean_id, "plot": "full"}, api_key)
    data = _get_json(url)
    if data.get("Response") == "False" or data.get("Error"):
        raise OMDBError(str(data.get("Error") or "Movie not found."))
    return data  # type: ignore[return-value]


def _normalize_title(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def _year_matches(result_year: str, year: int | str | None) -> bool:
    if year is None:
        return True
    match = re.search(r"\d{4}", str(result_year))
    return bool(match and match.group(0) == str(year))


def choose_best_result(
    results: list[MovieSearchResult],
    title: str,
    year: int | str | None = None,
) -> MovieSearchResult | None:
    """Choose a deterministic result from OMDB search output.

    Preference order is exact normalized title plus requested year, exact title,
    requested year, then OMDB's first result.
    """

    if not results:
        return None
    wanted = _normalize_title(title)
    exact = [result for result in results if _normalize_title(result.get("Title", "")) == wanted]
    for result in exact:
        if _year_matches(result.get("Year", ""), year):
            return result
    if exact:
        return exact[0]
    if year is not None:
        for result in results:
            if _year_matches(result.get("Year", ""), year):
                return result
    return results[0]
