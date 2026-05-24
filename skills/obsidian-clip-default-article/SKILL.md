---
name: obsidian-clip-default-article
description: Clip a generic web article into Obsidian Clippings with title, source, author, dates, description, tags, and readable Markdown content.
---

# Default Article Clipping

Replicates `default-clipper.json`.

## Output

- Path: `Clippings`
- Body: readable article/content Markdown.
- Properties: `title`, `source`, `author`, `published`, `created`, `description`, `tags`.

## Ontology Rules

Render authors as `Person` wikilinks. Keep `source` as the original URL. Use `clippings` as the default tag.
