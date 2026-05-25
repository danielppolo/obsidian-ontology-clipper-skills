---
name: obsidian-clip-places
description: Clip Google Maps place pages into Obsidian place reference notes with coordinates, address, source URL, and locality wikilinks.
---

# Place Clipping

Replicates `google-maps-clipper.json`.

## Trigger

- `https://www.google.com/maps/place/`

## Output

- Path: `References`
- Body: usually empty.
- Properties: `categories`, `type`, `rating`, `loc`, `tags`, `source`, `coordinates`, `address`, `url`, `scoreGoogle`, `description`, `created`, `last`.

## Ontology Rules

Use `[[Places]]` as category. Locality fields are `Place` wikilinks. Keep map/source/website URLs as URLs. Coordinates remain text or list-like coordinate properties.

## Base Policy

Load and follow `obsidian-ontology-core` before writing to the vault. Use its shared CRUD helpers and policy rules for `categories`, `tags`, audit metadata, wikilinks, raw URL preservation, and safe create/update/delete capabilities.
