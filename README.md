# Obsidian Ontology Clipper Skills

Reusable Hermes Agent skills for reproducing Obsidian Web Clipper templates through scraping and deterministic note rendering.

The source templates were reviewed from `/Users/Shared/Notes/.obsidian/clipper/*.json`. This repository does not require that vault path at runtime; use `--vault` or `OBSIDIAN_VAULT_PATH` when writing notes.

## Philosophy

The original clipper templates mostly collect page metadata into Obsidian properties. This repo keeps those output semantics while making the clipping model ontology-first: people, places, organizations, creative works, genres, categories, topics, channels, shows, locations, actors, directors, authors, and event localities should become Obsidian Wikilinks whenever they represent durable entities.

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
```

The CLI is intentionally basic. It can fetch a URL or render from saved HTML with `--html-file`, then route the URL to a skill-kind and render Obsidian-compatible Markdown.

## Skills

- `obsidian-web-clipper-core`: shared ontology, wikilink, routing, metadata, and rendering rules.
- `obsidian-clip-default-article`: default web article clipping into `Clippings`.
- `obsidian-clip-chatgpt`: shared ChatGPT conversations into `Clippings`.
- `obsidian-clip-youtube`: YouTube video and transcript-oriented notes.
- `obsidian-clip-books`: Goodreads book references into `References`.
- `obsidian-clip-movies`: Letterboxd movie references into `References`.
- `obsidian-clip-places`: Google Maps place references into `References`.
- `obsidian-clip-events`: Luma event references into `References`.
- `obsidian-clip-podcasts`: Spotify, YouTube, and Patreon podcast/show/episode notes.
- `obsidian-clip-wikipedia`: Wikipedia article clipping with corrected page routing.

See [docs/ontology.md](docs/ontology.md) and [docs/template-analysis.md](docs/template-analysis.md).
