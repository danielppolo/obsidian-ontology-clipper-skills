---
name: obsidian-ontology-core
description: Base policy and safe CRUD rules for ontology-first Obsidian vault writes.
version: 0.1.0
author: Hermes Agent contributors
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Obsidian, Ontology, Markdown, Frontmatter, Vault]
---

# Obsidian Ontology Core

Use this skill before any domain skill writes to an Obsidian vault. It is the base policy layer for note creation, updates, appends, and deletes.

The policy is derived from `/Users/Shared/Notes/Daniel/The relation to Obsidian.md`, especially:

- Keep one vault when possible.
- Avoid folders as the primary organizing system; use properties and links.
- Avoid non-standard Markdown.
- Always use plural `categories` and `tags` properties.
- Use internal links profusely.
- Use `YYYY-MM-DD` dates everywhere.
- Use list properties when a value could contain more than one item later.
- Keep references/clippings/admin folders semantically meaningful.

## Mandatory frontmatter rules

1. Use `categories`, never `category`.
2. `categories` is always a list.
3. Category values are wikilinks, e.g. `[[Movies]]`, `[[People]]`, `[[Relations]]`.
4. Use `tags`, never `tag`.
5. `tags` is always a list of lowercase plain strings, not wikilinks.
6. Any automated modification must add the audit tag:
   - `modified/obsidian-ontology-skills`
7. Any automated modification must add or update:
   - `modified: YYYY-MM-DD`
   - `modifiedBy: <skill-name>`
   - `modifiedVia: obsidian-ontology-skills`
8. Preserve unknown existing frontmatter fields unless a domain skill explicitly owns that field.
9. Prefer short reusable property names.
10. Prefer list properties for people, places, organizations, genres, topics, categories, authors, directors, cast, guests, locations, companies, countries, and languages.

## Mandatory ontology rules

Wikilink durable entities:

- people
- places
- organizations
- creative works
- categories
- genres
- topics
- shows
- channels
- authors
- directors
- writers
- actors/cast
- publishers
- companies
- event localities

Keep raw URLs as raw URLs for:

- `source`
- `url`
- `image`
- `cover`
- `poster`
- `thumbnail`
- `website`
- `imdb`
- `links`
- `instagram`

Do not double-wrap existing wikilinks. Preserve aliases by linking the target side when already present.

## CRUD policy

Domain skills must use explicit capabilities rather than implicit filesystem writes.

Recommended implementation API:

```python
from ontology_clipper.obsidian_policy import OperationPolicy, read_note, write_note, merge_note_frontmatter
```

Examples:

```python
# Create a new movie/book/reference note, creating the target folder if needed.
write_note(path, markdown, OperationPolicy(create=True, update=False, create_parent_dirs=True))

# Update an existing person note only; never create a missing one.
write_note(path, markdown, OperationPolicy(create=False, update=True))

# Deletes are forbidden by default and should require explicit user confirmation.
write_note(path, "", OperationPolicy(delete=False), delete=True)
```

## Domain skill responsibilities

Domain skills decide source-specific semantics:

- OMDB movie lookup
- Google Books lookup
- Google Contacts person lookup
- Web page metadata extraction
- Timeline entry construction

The core policy decides vault-wide semantics:

- frontmatter normalization
- `categories`/`tags` property shape
- audit metadata
- wikilink normalization
- raw URL preservation
- safe reads/writes
- no accidental creation/deletion

## Existing people-note rule

People notes are special: Google Contacts is the source of truth. Skills may update an existing person note from a resolved contact, but must not create a new person note from an arbitrary typed name.

## Verification checklist

Before writing to the vault:

- [ ] Concrete vault path is resolved; no `$OBSIDIAN_VAULT_PATH` literal in file-tool paths.
- [ ] The operation policy explicitly allows the intended action.
- [ ] `categories` is plural, list-shaped, and wikilinked.
- [ ] `tags` is plural, list-shaped, lowercase, and includes `modified/obsidian-ontology-skills` when modified.
- [ ] `modified`, `modifiedBy`, and `modifiedVia` are present for automated writes.
- [ ] Unknown human-authored frontmatter/body content is preserved.
- [ ] Raw URL fields remain raw URLs.
- [ ] Destructive operations are refused unless explicitly authorized.
