from urllib.parse import parse_qs, urlparse

from ontology_clipper.google_books import build_google_books_url, choose_best_result, transform_book_data


VOLUME = {
    "id": "vol-1",
    "volumeInfo": {
        "title": "The Left Hand of Darkness",
        "subtitle": "A Novel",
        "authors": ["Ursula K. Le Guin"],
        "publisher": "Ace Books",
        "publishedDate": "1969-03",
        "description": "A science fiction novel.",
        "pageCount": 304,
        "categories": ["Fiction / Science Fiction"],
        "language": "en",
        "previewLink": "https://books.google.com/preview",
        "infoLink": "https://books.google.com/info",
        "imageLinks": {
            "thumbnail": "https://example.com/thumb.jpg",
            "smallThumbnail": "https://example.com/small.jpg",
        },
        "averageRating": 4.1,
        "ratingsCount": 1200,
        "maturityRating": "NOT_MATURE",
        "industryIdentifiers": [
            {"type": "ISBN_10", "identifier": "0441478123"},
            {"type": "ISBN_13", "identifier": "9780441478125"},
        ],
    },
}


def test_build_google_books_search_url_uses_max_results_without_key():
    url = build_google_books_url({"q": "The Left Hand of Darkness", "maxResults": "40"})
    assert url == "https://www.googleapis.com/books/v1/volumes?q=The+Left+Hand+of+Darkness&maxResults=40"
    assert "key=" not in url


def test_build_google_books_url_adds_optional_key_only_when_provided():
    url = build_google_books_url({"q": "Dune", "maxResults": "40"}, api_key="test-key")
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    assert parsed.scheme == "https"
    assert parsed.netloc == "www.googleapis.com"
    assert parsed.path == "/books/v1/volumes"
    assert params == {"q": ["Dune"], "maxResults": ["40"], "key": ["test-key"]}


def test_transform_book_data_extracts_isbns_and_fields():
    details = transform_book_data(VOLUME)
    assert details["Title"] == "The Left Hand of Darkness"
    assert details["Subtitle"] == "A Novel"
    assert details["Authors"] == "Ursula K. Le Guin"
    assert details["PageCount"] == "304"
    assert details["Categories"] == "Fiction / Science Fiction"
    assert details["ISBN10"] == "0441478123"
    assert details["ISBN13"] == "9780441478125"
    assert details["Thumbnail"] == "https://example.com/thumb.jpg"
    assert details["AverageRating"] == "4.1"
    assert details["RatingsCount"] == "1200"
    assert details["VolumeID"] == "vol-1"


def test_choose_best_result_prefers_title_year_and_author():
    results = [
        {
            "id": "wrong-year",
            "volumeInfo": {
                "title": "The Left Hand of Darkness",
                "authors": ["Ursula K. Le Guin"],
                "publishedDate": "2010",
            },
        },
        {
            "id": "right",
            "volumeInfo": {
                "title": "The Left Hand of Darkness",
                "authors": ["Ursula K. Le Guin"],
                "publishedDate": "1969-03",
            },
        },
        {
            "id": "wrong-author",
            "volumeInfo": {
                "title": "The Left Hand of Darkness",
                "authors": ["Someone Else"],
                "publishedDate": "1969",
            },
        },
    ]
    assert choose_best_result(results, "The Left Hand of Darkness", year=1969, author="Ursula K. Le Guin") == results[1]


def test_choose_best_result_falls_back_to_first_result():
    results = [
        {"id": "a", "volumeInfo": {"title": "A"}},
        {"id": "b", "volumeInfo": {"title": "B"}},
    ]
    assert choose_best_result(results, "Missing") == results[0]
