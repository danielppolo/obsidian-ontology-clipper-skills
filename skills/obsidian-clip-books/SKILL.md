---
name: obsidian-clip-books
description: Clip Goodreads book pages into Obsidian book reference notes with wikilinked authors and genres.
---

# Book Clipping

Replicates `goodreads-clipper.json`.

## Trigger

- `https://www.goodreads.com/book/`

## Output

- Path: `References`
- Body: book description.
- Properties: `title`, `author`, `genre`, `pages`, `year`, `scoreGr`, `rating`, `cover`, `isbn`, `language`, `created`, `tags`.

## Ontology Rules

Authors are `Person` wikilinks. Genres are `Genre` wikilinks. The note is a `Book`. Default tags are `books` and `to-read`.
