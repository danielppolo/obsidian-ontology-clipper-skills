from argparse import Namespace

from ontology_clipper import movie_cli
from ontology_clipper.movie_note import movie_filename, movie_properties, render_movie_note, unique_note_path


DETAILS = {
    "Title": "The Matrix",
    "Year": "1999",
    "Rated": "R",
    "Released": "31 Mar 1999",
    "Runtime": "136 min",
    "Genre": "Action, Sci-Fi",
    "Director": "Lana Wachowski, Lilly Wachowski",
    "Writer": "Lilly Wachowski, Lana Wachowski",
    "Actors": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving, Gloria Foster, Joe Pantoliano",
    "Plot": "A hacker discovers reality is a simulation.",
    "Language": "English",
    "Country": "United States, Australia",
    "Awards": "Won 4 Oscars.",
    "Poster": "https://example.com/matrix.jpg",
    "Metascore": "73",
    "imdbRating": "8.7",
    "imdbVotes": "2,100,000",
    "imdbID": "tt0133093",
    "Type": "movie",
    "DVD": "21 Sep 1999",
    "BoxOffice": "$172,076,928",
    "Production": "Warner Bros.",
    "Website": "https://www.warnerbros.com/movies/matrix",
    "Response": "True",
}


def test_movie_properties_wikilink_ontology_fields():
    props = movie_properties(DETAILS, watched=True, created_date="2026-05-24")
    assert props["title"] == "The Matrix"
    assert props["categories"] == ["[[Movies]]"]
    assert props["genre"] == ["[[Action]]", "[[Sci-Fi]]"]
    assert props["director"] == ["[[Lana Wachowski]]", "[[Lilly Wachowski]]"]
    assert props["writer"] == ["[[Lilly Wachowski]]", "[[Lana Wachowski]]"]
    assert props["cast"] == [
        "[[Keanu Reeves]]",
        "[[Laurence Fishburne]]",
        "[[Carrie-Anne Moss]]",
        "[[Hugo Weaving]]",
        "[[Gloria Foster]]",
    ]
    assert props["language"] == ["[[English]]"]
    assert props["country"] == ["[[United States]]", "[[Australia]]"]
    assert props["production"] == ["[[Warner Bros.]]"]
    assert props["imdb"] == "https://www.imdb.com/title/tt0133093"
    assert props["created"] == "2026-05-24"
    assert props["last"] == "2026-05-24"
    assert props["tags"] == ["movies", "references", "watched"]


def test_pending_note_has_to_watch_tag_and_empty_last():
    props = movie_properties(DETAILS, watched=False, created_date="2026-05-24")
    assert props["last"] == ""
    assert props["tags"] == ["movies", "references", "to-watch"]


def test_render_movie_note_preserves_full_actor_details():
    rendered = render_movie_note(DETAILS, watched=True, created_date="2026-05-24")
    assert "title: The Matrix" in rendered
    assert "- **Actors:** [[Keanu Reeves]], [[Laurence Fishburne]], [[Carrie-Anne Moss]], [[Hugo Weaving]], [[Gloria Foster]], [[Joe Pantoliano]]" in rendered


def test_movie_filename_sanitizes_default_title_year():
    details = {**DETAILS, "Title": 'A/B: "C"', "Year": "1999"}
    assert movie_filename(details) == "AB C (1999).md"


def test_unique_note_path_adds_date_suffix_for_duplicates(tmp_path):
    folder = tmp_path / "References" / "Movies"
    folder.mkdir(parents=True)
    existing = folder / "The Matrix (1999).md"
    existing.write_text("old", encoding="utf-8")
    assert unique_note_path(
        tmp_path,
        "References/Movies",
        existing.name,
        duplicate_timestamp="2026-05-24T12-34-56",
    ) == folder / "The Matrix (1999) 2026-05-24T12-34-56.md"


def test_cli_build_note_from_args_can_be_dry_run_without_network(monkeypatch):
    monkeypatch.setenv("OMDB_API_KEY", "secret")
    monkeypatch.setattr(movie_cli, "search_movies", lambda title, api_key: [{"Title": title, "Year": "1999", "imdbID": "tt0133093", "Type": "movie", "Poster": "N/A"}])
    monkeypatch.setattr(movie_cli, "get_movie_details", lambda imdb_id, api_key: DETAILS)
    args = Namespace(
        title="The Matrix",
        year=None,
        imdb_id=None,
        api_key=None,
        choose="best",
        watched=False,
    )
    filename, rendered = movie_cli.build_note_from_args(args)
    assert filename == "The Matrix (1999).md"
    assert "to-watch" in rendered
