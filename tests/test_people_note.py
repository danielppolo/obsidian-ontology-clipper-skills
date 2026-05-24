from pathlib import Path

import pytest

from ontology_clipper import people_cli
from ontology_clipper.people_note import (
    append_timeline_entry,
    instagram_from_contact,
    merge_frontmatter,
    person_properties,
    timeline_entry,
    update_existing_person_markdown,
)


CONTACT = {
    "names": [{"displayName": "Ada Lovelace", "givenName": "Ada", "familyName": "Lovelace"}],
    "emailAddresses": [{"value": "ada@example.com"}],
    "phoneNumbers": [{"value": "+44 20 1234 5678"}],
    "urls": [{"value": "https://example.com/ada"}],
    "userDefined": [{"key": "instagram", "value": "ada_lovelace"}],
    "birthdays": [{"date": {"year": 1815, "month": 12, "day": 10}}],
    "organizations": [{"name": "Analytical Society", "title": "Mathematician"}],
    "addresses": [{"formattedValue": "London"}],
}


def test_person_properties_maps_google_contact_to_ontology_frontmatter():
    props = person_properties(CONTACT, updated_date="2026-05-24")
    assert props["categories"] == ["[[People]]"]
    assert props["name"] == "Ada Lovelace"
    assert props["aliases"] == ["Ada", "Lovelace"]
    assert props["email"] == ["ada@example.com"]
    assert props["phone"] == ["+44 20 1234 5678"]
    assert props["links"] == ["https://example.com/ada"]
    assert props["instagram"] == "https://instagram.com/ada_lovelace"
    assert props["birthday"] == "1815-12-10"
    assert props["company"] == ["[[Analytical Society]]"]
    assert props["jobTitle"] == "Mathematician"
    assert props["location"] == ["[[London]]"]
    assert props["source"] == "Google Contacts"
    assert props["updated"] == "2026-05-24"
    assert props["tags"] == ["people"]


def test_instagram_from_url_remains_plain_url():
    contact = {"urls": [{"value": "https://instagram.com/example.person"}]}
    assert instagram_from_contact(contact) == "https://instagram.com/example.person"


def test_merge_frontmatter_preserves_existing_body_and_unknown_properties():
    original = "---\ntitle: Ada\nrelation: friend\n---\n# Ada Lovelace\n\nBody stays.\n"
    updated = merge_frontmatter(original, person_properties(CONTACT, updated_date="2026-05-24"))
    assert "relation: friend" in updated
    assert "name: Ada Lovelace" in updated
    assert '  - "[[People]]"' in updated
    assert "# Ada Lovelace\n\nBody stays." in updated


def test_timeline_entry_uses_day_note_and_ontology_links():
    entry = timeline_entry(
        "2026-05-24",
        "Discussed the analytics prototype",
        people=["Charles Babbage"],
        places=["London"],
        entities=["Analytical Engine"],
    )
    assert entry == "- [[2026-05-24]] — Discussed the analytics prototype (people: [[Charles Babbage]]; places: [[London]]; entities: [[Analytical Engine]])"


def test_append_timeline_entry_adds_heading_and_avoids_duplicate():
    markdown = "# Ada\n"
    entry = timeline_entry("2026-05-24", "Met for coffee")
    once = append_timeline_entry(markdown, entry)
    twice = append_timeline_entry(once, entry)
    assert "## Timeline" in once
    assert twice.count(entry) == 1


def test_update_existing_person_markdown_combines_contact_and_timeline():
    original = "# Ada Lovelace\n"
    entry = timeline_entry("2026-05-24", "Met", places=["London"])
    updated = update_existing_person_markdown(original, CONTACT, timeline=entry, updated_date="2026-05-24")
    assert "name: Ada Lovelace" in updated
    assert "## Timeline" in updated
    assert "places: [[London]]" in updated


def test_people_cli_refuses_to_create_missing_note(tmp_path, capsys):
    missing = tmp_path / "People" / "Ada Lovelace.md"
    with pytest.raises(SystemExit) as error:
        people_cli.main(["--note", str(missing), "--timeline-date", "2026-05-24", "--timeline-text", "Met"])
    assert error.value.code == 2
    assert not missing.exists()


def test_people_cli_updates_existing_note_from_contact_json(tmp_path, capsys):
    note = tmp_path / "Ada Lovelace.md"
    note.write_text("# Ada Lovelace\n", encoding="utf-8")
    contact_json = tmp_path / "contact.json"
    contact_json.write_text(
        '{"names":[{"displayName":"Ada Lovelace"}],"emailAddresses":[{"value":"ada@example.com"}]}',
        encoding="utf-8",
    )
    result = people_cli.main([
        "--note",
        str(note),
        "--contact-json",
        str(contact_json),
        "--updated-date",
        "2026-05-24",
    ])
    assert result == 0
    content = note.read_text(encoding="utf-8")
    assert "name: Ada Lovelace" in content
    assert '  - "ada@example.com"' in content
