---
name: obsidian-clip-movies
description: Clip Letterboxd film pages into movie reference notes with wikilinked genre, director, and cast fields.
---

# Movie Clipping

Replicates `letterboxd-clipper.json`.

## Trigger

- `https://letterboxd.com/film/`

## Output

- Path: `References`
- Body: empty unless a plot or review body is available.
- Properties: `categories`, `genre`, `director`, `rating`, `scoreLB`, `cast`, `cover`, `plot`, `created`, `last`, `year`, `tags`.

## Ontology Rules

Use `[[Movies]]` as category. Directors and cast are `Person` wikilinks. Genres are `Genre` wikilinks. Keep cover URLs plain.
