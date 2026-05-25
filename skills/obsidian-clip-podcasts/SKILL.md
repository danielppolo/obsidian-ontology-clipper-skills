---
name: obsidian-clip-podcasts
description: Clip Spotify, YouTube, and Patreon podcast show or episode pages into podcast reference notes with show, author, genre, topic, and episode ontology.
---

# Podcast Clipping

Replicates `spotify-podcast-clipper.json`, `spotify-podcast-episode-clipper.json`, `youtube-podcast-clipper.json`, `youtube-podcast-episode-clipper.json`, and `patreon-podcast-clipper.json`.

## Triggers

- `https://open.spotify.com/episode/`
- `https://open.spotify.com/show/`
- generic `https://open.spotify.com`
- generic `https://www.youtube.com`
- `https://www.patreon.com`

## Output

- Path: `References`
- Show category: `[[Podcasts]]`.
- Episode category: `[[Podcast episodes]]`.
- Common properties: `categories`, `show`, `genre`, `author`, `topics`, `rating`, `cover` or `image`, `created`, `year`, `published`, `source`, `tags`.

## Ontology Rules

Prioritize episode routes before generic podcast routes. Shows are `Podcast` wikilinks, authors/hosts are `Person` or `Organization` wikilinks, genres are `Genre` wikilinks, and topics are `Topic` wikilinks.

## Base Policy

Load and follow `obsidian-ontology-core` before writing to the vault. Use its shared CRUD helpers and policy rules for `categories`, `tags`, audit metadata, wikilinks, raw URL preservation, and safe create/update/delete capabilities.
