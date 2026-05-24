from ontology_clipper.frontmatter import render_frontmatter


def test_render_frontmatter_quotes_wikilinks_and_lists():
    rendered = render_frontmatter(
        {
            "title": "Example",
            "categories": ["[[Movies]]"],
            "rating": 5,
            "description": "A: B",
        }
    )
    assert rendered.startswith("---\n")
    assert '  - "[[Movies]]"' in rendered
    assert "rating: 5" in rendered
    assert 'description: "A: B"' in rendered
