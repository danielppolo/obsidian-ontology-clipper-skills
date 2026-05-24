from ontology_clipper.routing import is_wikipedia_page, route_url


def test_spotify_episode_beats_generic_spotify():
    route = route_url("https://open.spotify.com/episode/abc")
    assert route.kind == "spotify-podcast-episode"


def test_youtube_watch_beats_generic_youtube():
    route = route_url("https://www.youtube.com/watch?v=abc")
    assert route.kind == "youtube"


def test_wikipedia_requires_page_slug():
    assert is_wikipedia_page("https://en.wikipedia.org/wiki/Obsidian")
    assert not is_wikipedia_page("https://en.wikipedia.org/wiki/")


def test_default_article_fallback():
    assert route_url("https://example.com/a").kind == "default-article"
