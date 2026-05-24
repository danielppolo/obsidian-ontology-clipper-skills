---
name: obsidian-clip-wikipedia
description: Clip Wikipedia article pages into Obsidian Clippings with corrected wiki-page routing and source metadata.
---

# Wikipedia Clipping

Replicates `wikipedia-clipper.json` with corrected routing.

## Trigger

- `https://<lang>.wikipedia.org/wiki/<page>`

The route must include a non-empty page slug after `/wiki/`.

## Output

- Path: `Clippings`
- Body: `#mw-content-text` converted to Markdown, excluding navboxes, print footers, and side boxes where scraper support allows.
- Properties: `categories`, `title`, `source`, `author`, `created`, `description`, `tags`.

## Ontology Rules

Use `[[Clippings]]` as category and `[[Wikipedia]]` as author/source organization. Tag as `clippings` and `wikipedia`.
