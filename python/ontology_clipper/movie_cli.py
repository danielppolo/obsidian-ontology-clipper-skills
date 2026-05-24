"""CLI for creating Obsidian movie notes from OMDB titles."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from .movie_note import movie_filename, render_movie_note, unique_note_path
from .omdb import OMDBError, choose_best_result, get_movie_details, search_movies


def _api_key(args: argparse.Namespace) -> str:
    return args.api_key or os.environ.get("OMDB_API_KEY", "")


def build_note_from_args(args: argparse.Namespace) -> tuple[str, str]:
    api_key = _api_key(args)
    if not api_key:
        raise OMDBError("OMDB_API_KEY or --api-key is required for OMDB lookup.")
    if args.imdb_id:
        imdb_id = args.imdb_id
    else:
        results = search_movies(args.title, api_key)
        if not results:
            raise OMDBError(f"No movies found for {args.title!r}.")
        selected = results[0] if args.choose == "first" else choose_best_result(results, args.title, args.year)
        if selected is None:
            raise OMDBError(f"No movies found for {args.title!r}.")
        imdb_id = selected["imdbID"]
    details = get_movie_details(imdb_id, api_key)
    return movie_filename(details), render_movie_note(details, watched=args.watched)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create an ontology-first Obsidian movie note from OMDB.")
    parser.add_argument("title")
    parser.add_argument("--year", help="Prefer a search result with this release year.")
    parser.add_argument("--imdb-id", help="Skip title search and fetch this IMDb id directly.")
    parser.add_argument("--api-key", help="OMDB API key. Defaults to OMDB_API_KEY.")
    parser.add_argument("--vault", default=os.environ.get("OBSIDIAN_VAULT_PATH"), help="Vault path. Defaults to OBSIDIAN_VAULT_PATH.")
    parser.add_argument("--folder", default="References/Movies", help="Vault-relative folder for the note.")
    watched = parser.add_mutually_exclusive_group()
    watched.add_argument("--watched", dest="watched", action="store_true", help="Mark the movie as watched.")
    watched.add_argument("--pending", dest="watched", action="store_false", help="Mark the movie as to-watch.")
    parser.set_defaults(watched=True)
    parser.add_argument("--dry-run", action="store_true", help="Print rendered markdown instead of writing a file.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing target note.")
    parser.add_argument("--choose", choices=["first", "best"], default="best", help="Search result selection strategy.")
    args = parser.parse_args(argv)

    try:
        filename, rendered = build_note_from_args(args)
    except OMDBError as error:
        parser.exit(1, f"error: {error}\n")

    if args.dry_run:
        print(rendered)
        return 0
    if not args.vault:
        parser.error("--vault or OBSIDIAN_VAULT_PATH is required unless --dry-run is used")
    vault = Path(args.vault).expanduser()
    target = unique_note_path(vault, args.folder, filename, overwrite=args.overwrite)
    target.parent.mkdir(parents=True, exist_ok=True)
    if args.overwrite:
        target.write_text(rendered, encoding="utf-8")
    else:
        try:
            with target.open("x", encoding="utf-8") as handle:
                handle.write(rendered)
        except FileExistsError:
            target = unique_note_path(vault, args.folder, filename, overwrite=False)
            with target.open("x", encoding="utf-8") as handle:
                handle.write(rendered)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
