from ontology_clipper.ontology import normalize_property, normalize_wikilink, wikilink_list


def test_normalize_wikilink_avoids_double_wrapping_and_trims():
    assert normalize_wikilink("  [[Hayao Miyazaki]]  ") == "[[Hayao Miyazaki]]"


def test_normalize_wikilink_strips_urls_to_host_when_forced():
    assert normalize_wikilink("https://en.wikipedia.org/wiki/Obsidian") == "[[en.wikipedia.org]]"


def test_wikilink_list_splits_deduplicates():
    assert wikilink_list("A, B, A") == ["[[A]]", "[[B]]"]


def test_source_url_is_not_wikilinked_by_property_normalization():
    assert normalize_property("source", "https://example.com/page") == "https://example.com/page"


def test_author_is_wikilinked_by_property_normalization():
    assert normalize_property("author", ["Ada Lovelace"]) == ["[[Ada Lovelace]]"]
