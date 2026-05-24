# Ontology

This repository treats clipped metadata as a graph of Obsidian notes, not only as strings. When a field names a durable entity, render it as a Wikilink.

## Entity Types

- `Person`: authors, directors, actors, hosts, guests, creators.
- `Place`: cities, venues, neighborhoods, event localities, mapped places.
- `Organization`: channels, publishers, companies, institutions, platforms.
- `CreativeWork`: a general creative work when a more specific subtype is unknown.
- `Movie`: films from Letterboxd and other movie pages.
- `Book`: books from Goodreads and other book pages.
- `Podcast`: podcast shows and channels.
- `PodcastEpisode`: podcast episodes from Spotify, Patreon, or YouTube.
- `Video`: YouTube videos and other video works.
- `Event`: Luma and other event pages.
- `WebArticle`: default web clippings and Wikipedia articles.
- `Conversation`: ChatGPT shared conversations.
- `Genre`: book, film, podcast, and video genres.
- `Topic`: manually or automatically assigned subject topics.
- `Category`: collection-level Obsidian groupings such as `[[Movies]]` or `[[Podcasts]]`.
- `Source`: source platforms or publisher/source entities when semantically useful.

## Wikilink Formation

Wikilinks are formed as `[[Normalized Name]]`.

Normalization rules:

- Trim leading and trailing whitespace.
- Collapse repeated whitespace.
- Avoid double wrapping existing `[[Name]]` values.
- Preserve aliases only when already intentional; helper output stores the target title.
- Do not wikilink raw URLs. If a URL is accidentally passed to wikilink normalization, use the hostname as the fallback label.
- Preserve lists as YAML lists of wikilinks.
- Deduplicate repeated wikilinks while preserving order.

## Field Mapping

Fields that should normally contain wikilinks:

- `author`, `authors`, `director`, `directors`, `cast`, `actors`: `Person`.
- `loc`, `location`, `locations`, `place`: `Place`.
- `show`: `Podcast`.
- `channel`: `Organization`.
- `genre`, `genres`: `Genre`.
- `topics`, `topic`: `Topic`.
- `categories`, `category`: `Category`.
- `source`: only a `Source` when it names a source entity; source URLs stay plain text.

Fields that normally stay scalar text or numbers:

- `title`, `published`, `created`, `start`, `end`, `year`, `pages`, `rating`, `scoreGr`, `scoreLB`, `scoreGoogle`, `isbn`, `language`, `cover`, `image`, `url`, `coordinates`, `address`, `description`, `plot`.
