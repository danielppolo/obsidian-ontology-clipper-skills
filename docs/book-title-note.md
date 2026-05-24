# Book Title Note Skill

This skill preserves the behavior of `/Users/Shared/Notes/.obsidian/plugins/danielppolo-book-search` while rendering notes in this repository's ontology-first Obsidian style.

## Plugin Mapping

- `BookSearchModal` searches Google Books with `q=<query>&maxResults=40`; `ontology_clipper.google_books.search_books()` does the same.
- The plugin can run without an API key and adds `key=<api_key>` only when configured; this skill follows the same rule with `--api-key` or `GOOGLE_BOOKS_API_KEY`.
- `BookResultsModal` fetches the selected result by volume id; `ontology_clipper.google_books.get_book_details()` does the same.
- `GoogleBooksClient.transformBookData()` maps `volumeInfo` into `BookDetails`; `transform_book_data()` keeps the same field names and ISBN extraction.
- `NoteCreator` defaults to `{{Title}} - {{Authors}}.md`; `book_filename()` renders the same filename shape and sanitizes invalid path characters.
- `NoteCreator` creates a timestamp-suffixed duplicate when a file exists; `unique_note_path()` creates a timestamp-suffixed path and increments if needed.
- The plugin's `isRead` controls `{{last}}`; this skill maps read to `last: <current date>` and pending to `last: ""`.

The plugin can use arbitrary templates. This skill intentionally uses a fixed ontology-aware book template so book notes match the current vault style and Goodreads clipping conventions.

## Properties

The rendered note includes:

- `categories: [[Books]]`
- `title` and optional `subtitle` as plain text
- `author`, `publisher`, and `genre` as wikilink lists
- `pages`, `year`, `published`, `scoreGoogle`, `rating`, `cover`, `isbn`, `isbn10`, and `isbn13`
- `language` as a plain code when Google Books returns a two- or three-letter lowercase value; human-readable language names are wikilinked
- `description`, `previewLink`, `infoLink`, `maturityRating`, and `ratingsCount` when available
- `created`, `last`, and tags of `books`, `references`, and either `read` or `to-read`

URLs are kept as plain URLs for `cover`, `previewLink`, and `infoLink`.

## CLI

```bash
python -m ontology_clipper.book_cli "The Left Hand of Darkness" --vault "$OBSIDIAN_VAULT_PATH" --read
python -m ontology_clipper.book_cli "The Left Hand of Darkness" --year 1969 --author "Ursula K. Le Guin" --dry-run
python -m ontology_clipper.book_cli "ignored query" --volume-id zyTCAlFPjgYC --pending
```

`GOOGLE_BOOKS_API_KEY` is optional. The command does not store or print the key.
