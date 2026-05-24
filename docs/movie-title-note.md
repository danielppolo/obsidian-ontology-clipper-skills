# Movie Title Note Skill

This skill preserves the behavior of `/Users/Shared/Notes/.obsidian/plugins/danielppolo-movie-search` while rendering notes in this repository's ontology-first Obsidian style.

## Plugin Mapping

- `MovieSearchModal` searches OMDB with `s=<title>&type=movie`; `ontology_clipper.omdb.search_movies()` does the same.
- `MovieResultsModal` fetches the selected result with `i=<imdbID>&plot=full`; `ontology_clipper.omdb.get_movie_details()` does the same.
- `NoteCreator` defaults to `{{Title}} ({{Year}}).md`; `movie_filename()` renders the same filename shape.
- `NoteCreator` creates a timestamp-suffixed duplicate when a file exists; `unique_note_path()` creates a timestamp-suffixed path and increments if needed.
- The plugin's `isWatched` controls `{{Last}}`; this skill maps watched to `last: <current date>` and pending to `last: ""`.

The plugin can use arbitrary templates. This skill intentionally uses a fixed ontology-aware movie template so movie notes match the current vault style.

## Properties

The rendered note includes:

- `categories: [[Movies]]`
- `genre`, `director`, `writer`, `cast`, `language`, `country`, and `production` as wikilink lists
- `rating: ""`
- `scoreImdb`, `cover`, `plot`, `created`, `last`, `year`, `imdbId`, and `imdb`
- OMDB details such as `runtime`, `rated`, `released`, `awards`, `metascore`, `boxOffice`, `website`, `imdbVotes`, `type`, and `dvd` when available
- tags of `movies`, `references`, and either `watched` or `to-watch`

URLs are kept as plain URLs for `cover`, `imdb`, and `website`. The title is plain text and is not wikilinked.

## CLI

```bash
python -m ontology_clipper.movie_cli "The Matrix" --vault "$OBSIDIAN_VAULT_PATH" --watched
python -m ontology_clipper.movie_cli "The Matrix" --year 1999 --dry-run
python -m ontology_clipper.movie_cli "The Matrix" --imdb-id tt0133093 --pending
```

`OMDB_API_KEY` is required unless `--api-key` is passed. The command does not store or print the key.
