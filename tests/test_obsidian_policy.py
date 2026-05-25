from pathlib import Path

import pytest

from ontology_clipper.obsidian_policy import (
    OperationPolicy,
    apply_obsidian_policy,
    merge_note_frontmatter,
    normalize_categories,
    read_note,
    write_note,
)


def test_apply_obsidian_policy_pluralizes_categories_as_wikilink_list_and_adds_audit_metadata():
    props = apply_obsidian_policy(
        {
            "category": "Relations",
            "tags": "People, #Friends",
            "author": "Daniel Polo",
            "source": "https://example.com/page",
        },
        skill_name="obsidian-manage-person-note",
        today="2026-05-25",
    )

    assert "category" not in props
    assert props["categories"] == ["[[Relations]]"]
    assert props["tags"] == ["people", "friends", "modified/obsidian-ontology-skills"]
    assert props["author"] == ["[[Daniel Polo]]"]
    assert props["source"] == "https://example.com/page"
    assert props["modified"] == "2026-05-25"
    assert props["modifiedBy"] == "obsidian-manage-person-note"
    assert props["modifiedVia"] == "obsidian-ontology-skills"


def test_normalize_categories_merges_existing_category_and_categories_without_duplicates():
    props = normalize_categories({"category": "[[People]]", "categories": ["People", "Writers"]})

    assert props == {"categories": ["[[People]]", "[[Writers]]"]}


def test_merge_note_frontmatter_preserves_unknown_fields_and_body_while_applying_policy():
    original = "---\ntitle: Ada\nrelation: friend\ncategory: People\n---\n# Ada\n\nBody stays.\n"

    updated = merge_note_frontmatter(
        original,
        {"location": "London"},
        skill_name="obsidian-manage-person-note",
        today="2026-05-25",
    )

    assert "relation: friend" in updated
    assert "category:" not in updated
    assert '  - "[[People]]"' in updated
    assert '  - "[[London]]"' in updated
    assert "modifiedBy: obsidian-manage-person-note" in updated
    assert "# Ada\n\nBody stays." in updated


def test_write_note_refuses_missing_parent_when_policy_disallows_create(tmp_path):
    target = tmp_path / "Missing" / "Ada.md"

    with pytest.raises(FileNotFoundError):
        write_note(target, "# Ada\n", OperationPolicy(create=False))

    assert not target.exists()


def test_write_note_creates_with_atomic_policy_and_read_note_round_trips(tmp_path):
    target = tmp_path / "Ada.md"

    write_note(target, "# Ada\n", OperationPolicy(create=True))

    assert read_note(target) == "# Ada\n"


def test_write_note_refuses_delete_operation_by_default(tmp_path):
    target = tmp_path / "Ada.md"
    target.write_text("# Ada\n", encoding="utf-8")

    with pytest.raises(PermissionError):
        write_note(target, "", OperationPolicy(delete=False), delete=True)

    assert target.read_text(encoding="utf-8") == "# Ada\n"
