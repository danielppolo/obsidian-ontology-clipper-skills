"""CLI for creating Obsidian book notes from Google Books title searches."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from .book_note import book_filename, render_book_note, unique_note_path
from .google_books import GoogleBooksError, choose_best_result, get_book_details, search_books


def _api_key(args: argparse.Namespace) -> str:
    return args.api_key or os.environ.get("GOOGLE_BOOKS_API_KEY", "")


def build_note_from_args(args: argparse.Namespace) -> tuple[str, str]:
    api_key = _api_key(args) or None
    if args.volume_id:
        volume_id = args.volume_id
    else:
        results = search_books(args.query, api_key)
        if not results:
            raise GoogleBooksError(f"No books found for {args.query!r}.")
        selected = results[0] if args.choose == "first" else choose_best_result(
            results,
            args.query,
            year=args.year,
            author=args.author,
        )
        if selected is None:
            raise GoogleBooksError(f"No books found for {args.query!r}.")
        volume_id = selected["id"]
    details = get_book_details(volume_id, api_key)
    return book_filename(details), render_book_note(details, read=args.read)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create an ontology-first Obsidian book note from Google Books.")
    parser.add_argument("query", help="Book title, author, ISBN, or other Google Books query.")
    parser.add_argument("--year", help="Prefer a search result with this publication year.")
    parser.add_argument("--author", help="Prefer a search result by this author.")
    parser.add_argument("--volume-id", help="Skip title search and fetch this Google Books volume id directly.")
    parser.add_argument("--api-key", help="Google Books API key. Defaults to GOOGLE_BOOKS_API_KEY when set.")
    parser.add_argument("--vault", default=os.environ.get("OBSIDIAN_VAULT_PATH"), help="Vault path. Defaults to OBSIDIAN_VAULT_PATH.")
    parser.add_argument("--folder", default="References/Books", help="Vault-relative folder for the note.")
    read = parser.add_mutually_exclusive_group()
    read.add_argument("--read", dest="read", action="store_true", help="Mark the book as read.")
    read.add_argument("--pending", dest="read", action="store_false", help="Mark the book as to-read.")
    parser.set_defaults(read=False)
    parser.add_argument("--dry-run", action="store_true", help="Print rendered markdown instead of writing a file.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing target note.")
    parser.add_argument("--choose", choices=["first", "best"], default="best", help="Search result selection strategy.")
    args = parser.parse_args(argv)

    try:
        filename, rendered = build_note_from_args(args)
    except GoogleBooksError as error:
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
