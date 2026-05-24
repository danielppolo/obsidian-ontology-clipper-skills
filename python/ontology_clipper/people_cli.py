"""CLI for updating existing Obsidian people notes from Google Contacts JSON."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .people_note import load_contact_json, timeline_entry, update_existing_person_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Update an existing Obsidian person note from Google Contacts data. Never creates new person notes."
    )
    parser.add_argument("--note", required=True, help="Existing person note path to update.")
    parser.add_argument("--contact-json", help="JSON file containing a Google Contacts/People contact object.")
    parser.add_argument("--timeline-date", help="Day-note date for a timeline entry, e.g. 2026-05-24.")
    parser.add_argument("--timeline-text", help="Timeline entry text to append under ## Timeline.")
    parser.add_argument("--timeline-people", nargs="*", default=[], help="People entities to wikilink in the timeline entry.")
    parser.add_argument("--timeline-places", nargs="*", default=[], help="Place entities to wikilink in the timeline entry.")
    parser.add_argument("--timeline-entities", nargs="*", default=[], help="Other durable entities to wikilink in the timeline entry.")
    parser.add_argument("--updated-date", help="Override updated date for deterministic rendering/tests.")
    parser.add_argument("--dry-run", action="store_true", help="Print the updated note instead of writing it.")
    args = parser.parse_args(argv)

    note_path = Path(args.note).expanduser()
    if not note_path.exists():
        parser.exit(2, f"error: person note does not exist: {note_path}\nCreate/sync the person from Google Contacts first; this tool will not create it.\n")

    if not args.contact_json and not args.timeline_text:
        parser.error("provide --contact-json and/or --timeline-text")
    if args.timeline_text and not args.timeline_date:
        parser.error("--timeline-date is required when --timeline-text is provided")

    contact = load_contact_json(Path(args.contact_json).expanduser()) if args.contact_json else None
    timeline = None
    if args.timeline_text:
        timeline = timeline_entry(
            args.timeline_date,
            args.timeline_text,
            people=args.timeline_people,
            places=args.timeline_places,
            entities=args.timeline_entities,
        )

    original = note_path.read_text(encoding="utf-8")
    updated = update_existing_person_markdown(
        original,
        contact=contact,
        timeline=timeline,
        updated_date=args.updated_date,
    )
    if args.dry_run:
        print(updated, end="")
    else:
        note_path.write_text(updated, encoding="utf-8")
        print(note_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
