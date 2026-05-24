"""URL routing that mirrors the reviewed Obsidian Web Clipper templates."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Route:
    kind: str
    skill: str
    path: str
    category: str


ROUTES: tuple[tuple[str, Route], ...] = (
    ("chatgpt.com/share", Route("chatgpt", "obsidian-clip-chatgpt", "Clippings", "Conversation")),
    ("chatgpt.com/c", Route("chatgpt", "obsidian-clip-chatgpt", "Clippings", "Conversation")),
    ("www.youtube.com/watch", Route("youtube", "obsidian-clip-youtube", "Clippings", "Video")),
    ("youtu.be/", Route("youtube", "obsidian-clip-youtube", "Clippings", "Video")),
    ("open.spotify.com/episode/", Route("spotify-podcast-episode", "obsidian-clip-podcasts", "References", "PodcastEpisode")),
    ("open.spotify.com/show/", Route("spotify-podcast", "obsidian-clip-podcasts", "References", "Podcast")),
    ("www.goodreads.com/book/", Route("goodreads", "obsidian-clip-books", "References", "Book")),
    ("letterboxd.com/film/", Route("letterboxd", "obsidian-clip-movies", "References", "Movie")),
    ("www.google.com/maps/place/", Route("google-maps", "obsidian-clip-places", "References", "Place")),
    ("luma.com/", Route("luma", "obsidian-clip-events", "References", "Event")),
    ("www.patreon.com/", Route("patreon-podcast", "obsidian-clip-podcasts", "References", "PodcastEpisode")),
)


def is_wikipedia_page(url: str) -> bool:
    parsed = urlparse(url)
    host_parts = parsed.netloc.lower().split(".")
    return (
        len(host_parts) >= 3
        and host_parts[-2:] == ["wikipedia", "org"]
        and 2 <= len(host_parts[0]) <= 3
        and parsed.path.startswith("/wiki/")
        and len(parsed.path) > len("/wiki/")
    )


def route_url(url: str, kind: str = "auto") -> Route:
    if kind and kind != "auto":
        return Route(kind, f"obsidian-clip-{kind}", "Clippings", kind)
    normalized = url.lower()
    for needle, route in ROUTES:
        if needle in normalized:
            return route
    if is_wikipedia_page(url):
        return Route("wikipedia", "obsidian-clip-wikipedia", "Clippings", "WebArticle")
    if "www.youtube.com" in normalized:
        return Route("youtube-podcast", "obsidian-clip-podcasts", "References", "Podcast")
    if "open.spotify.com" in normalized:
        return Route("spotify-podcast", "obsidian-clip-podcasts", "References", "Podcast")
    return Route("default-article", "obsidian-clip-default-article", "Clippings", "WebArticle")
