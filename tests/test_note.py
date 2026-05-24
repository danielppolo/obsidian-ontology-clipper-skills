from ontology_clipper.note import Note


def test_note_rendering_keeps_source_url_and_wikilinks_entities():
    note = Note(
        title="Spirited Away",
        source="https://letterboxd.com/film/spirited-away/",
        body="A film note.",
        properties={
            "categories": ["Movies"],
            "director": ["Hayao Miyazaki"],
            "tags": "movies, review",
        },
    )
    rendered = note.render()
    assert 'source: "https://letterboxd.com/film/spirited-away/"' in rendered
    assert '  - "[[Movies]]"' in rendered
    assert '  - "[[Hayao Miyazaki]]"' in rendered
    assert "A film note." in rendered


def test_filename_sanitizes_for_obsidian():
    note = Note(title='A/B: "C"', source="https://example.com")
    assert note.filename() == "A B C.md"
