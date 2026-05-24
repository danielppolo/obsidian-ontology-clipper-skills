---
name: obsidian-clip-youtube
description: Clip YouTube watch pages into video notes with channel entity metadata, upload date, thumbnail, source embed, and transcript content when available.
---

# YouTube Clipping

Replicates `youtube-clipper.json`.

## Trigger

- `https://www.youtube.com/watch?v=`

## Output

- Path: `Clippings`
- Body: `![title](source)` followed by transcript when available.
- Properties: `categories`, `title`, `author`, `published`, `source`, `image`, `created`, `tags`.

## Ontology Rules

Use `[[Youtube channel episodes]]` as the category. Treat channel/author names as `Organization` or creator entities and wikilink them. Keep thumbnail and source URLs as plain text.
