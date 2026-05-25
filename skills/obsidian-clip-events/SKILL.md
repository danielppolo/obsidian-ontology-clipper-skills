---
name: obsidian-clip-events
description: Clip Luma event pages into event reference notes with start/end dates, source URL, locality wikilink, and description body.
---

# Event Clipping

Replicates `luma-clipper.json`.

## Trigger

- `https://luma.com/`

## Output

- Path: `References`
- Body: linked event name and description.
- Properties: `categories`, `tags`, `type`, `start`, `end`, `loc`, `source`, `created`.

## Ontology Rules

Use `[[Events]]` as category. Event localities are `Place` wikilinks. The note is an `Event`; named organizers can be `Organization` or `Person` entities when available.

## Base Policy

Load and follow `obsidian-ontology-core` before writing to the vault. Use its shared CRUD helpers and policy rules for `categories`, `tags`, audit metadata, wikilinks, raw URL preservation, and safe create/update/delete capabilities.
