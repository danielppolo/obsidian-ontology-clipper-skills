# Obsidian Ontology Skills

Reusable Hermes Agent skills for ontology-first Obsidian workflows: web clipping, deterministic reference-note creation, and existing people-note management.

The source templates were reviewed from `/Users/Shared/Notes/.obsidian/clipper/*.json`. This repository does not require that vault path at runtime; use `--vault` or `OBSIDIAN_VAULT_PATH` when writing notes.

## Philosophy

The original clipper templates mostly collect page metadata into Obsidian properties. This repo keeps those output semantics where relevant while making the broader note model ontology-first: people, places, organizations, creative works, genres, categories, topics, channels, shows, locations, actors, directors, authors, and event localities should become Obsidian Wikilinks whenever they represent durable entities.

Examples:

- `author: ["[[Ursula K. Le Guin]]"]`
- `director: ["[[Hayao Miyazaki]]"]`
- `categories: ["[[Movies]]"]`
- `loc: "[[Mexico City]]"`

URLs remain URLs in `source`, `url`, `image`, and `cover` fields. They are not forced into entity notes.

## Install And Use

```bash
python -m pip install -e ".[test]"
python -m pytest
python -m ontology_clipper.cli "https://example.com/article" --kind auto --dry-run
python -m ontology_clipper.cli "https://example.com/article" --kind auto --vault "$OBSIDIAN_VAULT_PATH"
python -m ontology_clipper.movie_cli "The Matrix" --dry-run
python -m ontology_clipper.movie_cli "The Matrix" --vault "$OBSIDIAN_VAULT_PATH" --watched
python -m ontology_clipper.book_cli "The Left Hand of Darkness" --dry-run
python -m ontology_clipper.book_cli "The Left Hand of Darkness" --vault "$OBSIDIAN_VAULT_PATH" --read
python -m ontology_clipper.people_cli --note "$OBSIDIAN_VAULT_PATH/People/Ada Lovelace.md" --contact-json /tmp/ada-contact.json --dry-run
```

The web clipping CLI is intentionally basic. It can fetch a URL or render from saved HTML with `--html-file`, then route the URL to a skill-kind and render Obsidian-compatible Markdown.
Movie title notes require `OMDB_API_KEY` for live lookup and write to `References/Movies` by default.
Book title notes use Google Books without requiring an API key, can use `GOOGLE_BOOKS_API_KEY` for higher rate limits, and write to `References/Books` by default.
People note management updates existing notes only. Google Contacts is the source of truth for person attributes; the helper refuses to create a missing person note.

## Skills

- `obsidian-ontology-core`: base vault policy, frontmatter normalization, audit metadata, wikilinks, and safe CRUD helpers.
- `obsidian-web-clipper-core`: shared ontology, wikilink, routing, metadata, and rendering rules.
- `obsidian-clip-default-article`: default web article clipping into `Clippings`.
- `obsidian-clip-chatgpt`: shared ChatGPT conversations into `Clippings`.
- `obsidian-clip-youtube`: YouTube video and transcript-oriented notes.
- `obsidian-clip-books`: Goodreads book references into `References`.
- `obsidian-clip-movies`: Letterboxd movie references into `References`.
- `obsidian-create-movie-note`: OMDB movie title lookup into `References/Movies`.
- `obsidian-create-book-note`: Google Books title/query lookup into `References/Books`.
- `obsidian-manage-person-note`: Google Contacts-backed updates to existing people notes; never creates new person notes.
- `obsidian-clip-places`: Google Maps place references into `References`.
- `obsidian-clip-events`: Luma event references into `References`.
- `obsidian-clip-podcasts`: Spotify, YouTube, and Patreon podcast/show/episode notes.
- `obsidian-clip-wikipedia`: Wikipedia article clipping with corrected page routing.

See [docs/ontology.md](docs/ontology.md), [docs/obsidian-ontology-core.md](docs/obsidian-ontology-core.md), [docs/template-analysis.md](docs/template-analysis.md), [docs/movie-title-note.md](docs/movie-title-note.md), [docs/book-title-note.md](docs/book-title-note.md), and [docs/person-note-management.md](docs/person-note-management.md).
