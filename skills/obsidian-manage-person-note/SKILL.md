---
name: obsidian-manage-person-note
description: Manage an existing Obsidian person note using Google Contacts as the source of truth; update frontmatter attributes and timeline entries without creating new person notes.
---

# Obsidian Person Note Management

## When To Use

Use this skill when the user asks to update, enrich, or maintain an existing person note in Obsidian: links, Instagram, birthday, email, phone, company, location, relationship context, or a dated timeline.

Do not use this skill to create a new person note. The source of truth for people is Google Contacts. If no matching person note exists, stop and tell the user the contact/note must first exist via Google Contacts sync or the user's established contact-note creation workflow.

## Source Of Truth Rule

Google Contacts is authoritative for person identity and contact attributes.

- Look up the person in Google Contacts first.
- Use the Obsidian note only as the local knowledge surface.
- Never invent contact attributes.
- Never create a new person note from a name alone.
- If the requested person is missing from Google Contacts or ambiguous, ask the user to choose the contact or update Google Contacts first.

## Required Lookup Flow

1. Resolve the vault path, usually `OBSIDIAN_VAULT_PATH` or `/Users/Shared/Notes`.
2. Look up the person in Google Contacts. With the bundled Google Workspace skill:

   ```bash
   GAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
   $GAPI contacts list --max 200
   ```

   Filter the JSON results for the requested name, email, or phone. If the local Google Workspace auth is not configured, explain that Google Contacts lookup is required before making contact-derived changes.

3. Find the existing person note by filename/content. Common searches:

   ```bash
   # use file tools in Hermes; examples shown as shell equivalents only
   # search files under the vault for "Person Name.md"
   # search markdown contents for name/email if filename differs
   ```

4. If no existing note is found, stop. Do not create `Person Name.md`.
5. Read the existing note, patch frontmatter attributes from Google Contacts, then add requested timeline entries.
6. Verify the resulting note still has valid frontmatter and the timeline entry links to a day note.

## Deterministic Helper

This repository includes a helper CLI that updates an existing note from a contact JSON file. It refuses to create a missing person note.

```bash
python -m ontology_clipper.people_cli \
  --note "$OBSIDIAN_VAULT_PATH/People/Ada Lovelace.md" \
  --contact-json /tmp/ada-google-contact.json

python -m ontology_clipper.people_cli \
  --note "$OBSIDIAN_VAULT_PATH/People/Ada Lovelace.md" \
  --timeline-date 2026-05-24 \
  --timeline-text "Discussed the analytics prototype" \
  --timeline-people "Charles Babbage" \
  --timeline-places "London" \
  --timeline-entities "Analytical Engine"
```

Use `--dry-run` before writing when the change is large.

## Frontmatter Strategy

Attach or update contact attributes in YAML frontmatter while preserving unrelated existing properties where possible.

Recommended properties:

- `categories: [[People]]`
- `name`: display name from Google Contacts
- `aliases`: nicknames or alternate names from Google Contacts
- `email`: list of email addresses
- `phone`: list of phone numbers
- `links`: personal websites or profile URLs
- `instagram`: normalized `https://instagram.com/<handle>` URL
- `birthday`: birthday from Google Contacts
- `company`: wikilink list for organizations
- `jobTitle`: plain text title
- `location`: wikilink list for places/addresses when semantically useful
- `source: Google Contacts`
- `updated`: current date
- `tags: people`

Keep URLs plain. Do not wikilink email addresses, phone numbers, Instagram URLs, websites, or profile URLs.

## Timeline Strategy

Person notes should contain a `## Timeline` section. Timeline items must link to day notes and should wikilink durable entities:

```markdown
## Timeline
- [[2026-05-24]] — Discussed the analytics prototype (people: [[Charles Babbage]]; places: [[London]]; entities: [[Analytical Engine]])
```

Rules:

- Every timeline item starts with a day-note wikilink: `[[YYYY-MM-DD]]`.
- People mentioned as durable relationships become wikilinks.
- Places become wikilinks when they represent real locations.
- Organizations, projects, events, and durable concepts become wikilinks.
- Keep raw URLs plain.
- Do not create missing entity notes just because a wikilink is added.
- Do not duplicate an identical timeline item.

## Common Pitfalls

1. Creating a new person note from the user's typed name. Do not do this; Google Contacts is the source of truth.
2. Updating a homonym without disambiguation. If Google Contacts returns multiple matches, ask the user which one.
3. Treating Instagram handles as wikilinks. Store the normalized URL as `instagram`.
4. Writing timeline items without day-note links. Always start with `[[YYYY-MM-DD]]`.
5. Overwriting personal notes with contact data. Merge attributes into frontmatter and preserve the existing body.

## Verification Checklist

- [ ] Google Contacts was checked first, or the user supplied exported contact JSON.
- [ ] Exactly one existing Obsidian person note was selected.
- [ ] No new person note was created.
- [ ] Contact attributes came from Google Contacts or explicit user input.
- [ ] People/places/entities in narrative timeline context are wikilinked.
- [ ] URLs, email addresses, and phone numbers remain plain.
- [ ] Timeline entries use `[[YYYY-MM-DD]]` day-note wikilinks.

## Base Policy

Load and follow `obsidian-ontology-core` before writing to the vault. Use its shared CRUD helpers and policy rules for `categories`, `tags`, audit metadata, wikilinks, raw URL preservation, and safe create/update/delete capabilities.
