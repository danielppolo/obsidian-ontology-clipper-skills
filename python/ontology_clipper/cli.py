"""Command line interface for deterministic dry-run clipping."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib.request import urlopen

from .markdown import readable_text
from .metadata import extract_metadata, first_schema
from .note import Note
from .obsidian_policy import OperationPolicy, write_note
from .routing import route_url


def build_note(url: str, html: str, kind: str = "auto") -> Note:
    route = route_url(url, kind)
    metadata = extract_metadata(html)
    schema = first_schema(metadata)
    title = str(schema.get("name") or metadata.get("title") or "Untitled")
    description = str(schema.get("description") or metadata.get("description") or "")
    author = schema.get("author") or metadata.get("author") or ""
    if isinstance(author, dict):
        author = author.get("name", "")
    props = {
        "description": description,
        "categories": route.category,
        "author": author,
        "tags": route.kind.replace("-", "/"),
    }
    body = readable_text(html)
    return Note(title=title, source=url, body=body, properties=props, path=route.path)


def fetch_url(url: str) -> str:
    with urlopen(url, timeout=20) as response:  # noqa: S310 - user-provided CLI utility.
        return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render an ontology-first Obsidian clipping note.")
    parser.add_argument("url")
    parser.add_argument("--kind", default="auto")
    parser.add_argument("--vault", default=os.environ.get("OBSIDIAN_VAULT_PATH"))
    parser.add_argument("--html-file", help="Read saved HTML instead of fetching the URL.")
    parser.add_argument("--dry-run", action="store_true", help="Print rendered markdown instead of writing a file.")
    args = parser.parse_args(argv)

    html = Path(args.html_file).read_text(encoding="utf-8") if args.html_file else fetch_url(args.url)
    note = build_note(args.url, html, args.kind)
    rendered = note.render()
    if args.dry_run:
        print(rendered)
        return 0
    if not args.vault:
        parser.error("--vault or OBSIDIAN_VAULT_PATH is required unless --dry-run is used")
    target_dir = Path(args.vault) / note.path
    target = target_dir / note.filename()
    write_note(target, rendered, OperationPolicy(create=True, update=True, create_parent_dirs=True))
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
