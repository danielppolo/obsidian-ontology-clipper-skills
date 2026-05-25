---
name: obsidian-web-clipper-core
description: Shared ontology-first Obsidian clipping rules, wikilink normalization, routing, metadata extraction, and note rendering.
---

# Obsidian Web Clipper Core

Use this skill before any specialized clipping skill.

## Workflow

1. Determine the URL route with `ontology_clipper.routing.route_url`.
2. Extract page metadata from saved HTML, OpenGraph, meta tags, and JSON-LD where available.
3. Map fields through the ontology before rendering properties.
4. Wikilink durable entities: people, places, organizations, creative works, genres, topics, categories, channels, shows, directors, actors, authors, and localities.
5. Keep raw URLs as raw URLs for `source`, `url`, `image`, and `cover`.
6. Render frontmatter with `ontology_clipper.note.Note`.

## CLI

```bash
python -m ontology_clipper.cli URL --kind auto --vault "$OBSIDIAN_VAULT_PATH" --dry-run
```

Use `--html-file` for deterministic local tests or saved pages.

## Base Policy

Load and follow `obsidian-ontology-core` before writing to the vault. Use its shared CRUD helpers and policy rules for `categories`, `tags`, audit metadata, wikilinks, raw URL preservation, and safe create/update/delete capabilities.
