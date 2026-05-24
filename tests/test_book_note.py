from argparse import Namespace

from ontology_clipper import book_cli
from ontology_clipper.book_note import book_filename, book_properties, render_book_note, unique_note_path


DETAILS = {
    "Title": "The Left Hand of Darkness",
    "Subtitle": "A Novel",
    "Authors": "Ursula K. Le Guin, Another Author",
    "Publisher": "Ace Books",
    "PublishedDate": "1969-03",
    "Description": "A science fiction novel.",
    "PageCount": "304",
    "Categories": "Fiction / Science Fiction, Classics",
    "Language": "en",
    "ISBN10": "0441478123",
    "ISBN13": "9780441478125",
    "PreviewLink": "https://books.google.com/preview",
    "InfoLink": "https://books.google.com/info",
    "Thumbnail": "https://example.com/thumb.jpg",
    "SmallThumbnail": "https://example.com/small.jpg",
    "AverageRating": "4.1",
    "RatingsCount": "1200",
    "MaturityRating": "NOT_MATURE",
}


def test_book_properties_wikilink_ontology_fields_when_read():
    props = book_properties(DETAILS, read=True, created_date="2026-05-24")
    assert props["categories"] == ["[[Books]]"]
    assert props["title"] == "The Left Hand of Darkness"
    assert props["subtitle"] == "A Novel"
    assert props["author"] == ["[[Ursula K. Le Guin]]", "[[Another Author]]"]
    assert props["publisher"] == ["[[Ace Books]]"]
    assert props["genre"] == ["[[Fiction]]", "[[Science Fiction]]", "[[Classics]]"]
    assert props["pages"] == 304
    assert props["year"] == 1969
    assert props["published"] == "1969-03"
    assert props["scoreGoogle"] == "4.1"
    assert props["rating"] == ""
    assert props["cover"] == "https://example.com/thumb.jpg"
    assert props["isbn"] == "9780441478125"
    assert props["language"] == "en"
    assert props["created"] == "2026-05-24"
    assert props["last"] == "2026-05-24"
    assert props["tags"] == ["books", "references", "read"]


def test_pending_book_has_to_read_tag_and_empty_last():
    props = book_properties(DETAILS, read=False, created_date="2026-05-24")
    assert props["last"] == ""
    assert props["tags"] == ["books", "references", "to-read"]


def test_human_readable_language_is_wikilinked():
    props = book_properties({**DETAILS, "Language": "English"}, created_date="2026-05-24")
    assert props["language"] == ["[[English]]"]


def test_render_book_note_includes_details_with_wikilinks():
    rendered = render_book_note(DETAILS, read=False, created_date="2026-05-24")
    assert "title: The Left Hand of Darkness" in rendered
    assert 'last: ""' in rendered
    assert "- **Authors:** [[Ursula K. Le Guin]], [[Another Author]]" in rendered
    assert "- **Publisher:** [[Ace Books]]" in rendered
    assert "- **Categories:** [[Fiction]], [[Science Fiction]], [[Classics]]" in rendered


def test_book_filename_sanitizes_default_title_authors():
    details = {**DETAILS, "Title": 'A/B: "C"', "Authors": "Writer/One, Writer:Two"}
    assert book_filename(details) == "AB C - WriterOne, WriterTwo.md"


def test_unique_note_path_adds_date_suffix_for_duplicates(tmp_path):
    folder = tmp_path / "References" / "Books"
    folder.mkdir(parents=True)
    existing = folder / "The Left Hand of Darkness - Ursula K. Le Guin.md"
    existing.write_text("old", encoding="utf-8")
    assert unique_note_path(
        tmp_path,
        "References/Books",
        existing.name,
        duplicate_timestamp="2026-05-24T12-34-56",
    ) == folder / "The Left Hand of Darkness - Ursula K. Le Guin 2026-05-24T12-34-56.md"


def test_cli_build_note_from_args_can_be_dry_run_without_network(monkeypatch):
    results = [{"id": "vol-1", "volumeInfo": {"title": "The Left Hand of Darkness", "authors": ["Ursula K. Le Guin"], "publishedDate": "1969"}}]
    monkeypatch.setattr(book_cli, "search_books", lambda query, api_key=None: results)
    monkeypatch.setattr(book_cli, "get_book_details", lambda volume_id, api_key=None: DETAILS)
    args = Namespace(
        query="The Left Hand of Darkness",
        year="1969",
        author="Ursula K. Le Guin",
        volume_id=None,
        api_key=None,
        choose="best",
        read=False,
    )
    filename, rendered = book_cli.build_note_from_args(args)
    assert filename == "The Left Hand of Darkness - Ursula K. Le Guin, Another Author.md"
    assert "to-read" in rendered
