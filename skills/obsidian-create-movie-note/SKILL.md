---
name: obsidian-create-movie-note
description: Create an Obsidian movie reference note from a movie title through OMDB lookup.
---

# Obsidian Movie Title Notes

## When To Use

Use this skill when the user gives a movie title and wants an Obsidian movie note created from OMDB metadata.

## Configuration

- `OMDB_API_KEY` is required for live OMDB lookup, unless `--api-key` is passed.
- Vault path comes from `--vault` or `OBSIDIAN_VAULT_PATH`.
- Notes default to `References/Movies`; pass `--folder` to override.

## Base Policy

Load and follow `obsidian-ontology-core` before writing to the vault. Use its shared CRUD helpers and policy rules for `categories`, `tags`, audit metadata, wikilinks, raw URL preservation, and safe create/update/delete capabilities.

## Commands

```bash
python -m ontology_clipper.movie_cli "The Matrix" --vault "$OBSIDIAN_VAULT_PATH" --watched
python -m ontology_clipper.movie_cli "The Matrix" --dry-run
ontology-movie-note "The Matrix" --pending --folder "References/Movies"
```

## Behavior

The command mirrors the Obsidian movie-search plugin flow:

- Search OMDB by title with `type=movie`.
- Select a result with `--choose best` by default, preferring exact title and `--year` when supplied.
- Fetch details by IMDb id with `plot=full`.
- Render a Markdown note named `{{Title}} ({{Year}}).md`.
- If a target file exists, create a timestamp-suffixed unique filename unless `--overwrite` is passed.

## Ontology Rules

Movie notes use the vault's ontology-first style. Durable people, places, genres, organizations, and categories become Obsidian wikilinks where semantically appropriate:

- `categories: [[Movies]]`
- `genre`, `director`, `writer`, `cast`, `language`, `country`, and `production` are wikilink lists.
- `cast` contains the first five actors in properties; the rendered details section keeps the full actor list.
- `title` remains plain text.
- `cover`, `imdb`, `website`, and source-like fields remain plain URLs.

Watched notes receive `tags: movies, references, watched` and `last` as the current date. Pending notes receive `tags: movies, references, to-watch` and an empty `last`.
