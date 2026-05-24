from ontology_clipper.omdb import build_omdb_url, choose_best_result


def test_build_omdb_search_url_uses_movie_type():
    url = build_omdb_url({"s": "The Matrix", "type": "movie"}, "secret")
    assert url == "https://www.omdbapi.com/?apikey=secret&s=The+Matrix&type=movie"


def test_choose_best_result_prefers_exact_title_and_year():
    results = [
        {"Title": "Matrix", "Year": "1993", "imdbID": "tt0106062", "Type": "movie", "Poster": "N/A"},
        {"Title": "The Matrix", "Year": "1999", "imdbID": "tt0133093", "Type": "movie", "Poster": "poster"},
    ]
    assert choose_best_result(results, "The Matrix", year=1999) == results[1]


def test_choose_best_result_falls_back_to_first_result():
    results = [
        {"Title": "A", "Year": "2000", "imdbID": "tt1", "Type": "movie", "Poster": "N/A"},
        {"Title": "B", "Year": "2001", "imdbID": "tt2", "Type": "movie", "Poster": "N/A"},
    ]
    assert choose_best_result(results, "Missing") == results[0]
