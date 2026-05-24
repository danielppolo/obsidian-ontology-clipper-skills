---
name: obsidian-create-book-note
description: Create an Obsidian book reference note from a book title, author, ISBN, or Google Books query.
---

# Obsidian Book Title Notes

## When To Use

Use this skill when the user gives a book title/query and wants an Obsidian book note created from Google Books metadata.

## Configuration

- `GOOGLE_BOOKS_API_KEY` is optional. Google Books works without a key, but a key can provide higher rate limits. Pass `--api-key` to override the environment value.
- Vault path comes from `--vault` or `OBSIDIAN_VAULT_PATH`.
- Notes default to `References/Books`; pass `--folder` to override.

## Commands

```bash
python -m ontology_clipper.book_cli "The Left Hand of Darkness" --vault "$OBSIDIAN_VAULT_PATH" --read
python -m ontology_clipper.book_cli "The Left Hand of Darkness" --dry-run
ontology-book-note "The Left Hand of Darkness" --pending --folder "References/Books"
```

## Behavior

The command mirrors the Obsidian book-search plugin flow:

- Search Google Books volumes with `q=<query>&maxResults=40`.
- Add `key=<api_key>` only when an API key is supplied.
- Select a result with `--choose best` by default, preferring exact title, `--year`, and `--author` when supplied.
- Fetch details by Google Books volume id.
- Render a Markdown note named `{{Title}} - {{Authors}}.md`, sanitized for the filesystem.
- If a target file exists, create a timestamp-suffixed unique filename unless `--overwrite` is passed.

## Ontology Rules

Book notes use the vault's ontology-first style. Durable people, organizations, genres, and categories become Obsidian wikilinks where semantically appropriate:

- `categories: [[Books]]`
- `author`, `publisher`, and `genre` are wikilink lists.
- `title` and `subtitle` remain plain text.
- `cover`, `previewLink`, `infoLink`, and source-like fields remain plain URLs.
- Google Books usually returns `language` as a two- or three-letter lowercase code such as `en`; those codes remain plain text. Human-readable language values are wikilinked.

Read notes receive `tags: books, references, read` and `last` as the current date. Pending notes receive `tags: books, references, to-read` and an empty `last`.
