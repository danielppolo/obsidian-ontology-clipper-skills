# Template Analysis

The source Obsidian Web Clipper templates were reviewed from `/Users/Shared/Notes/.obsidian/clipper/*.json`.

| Template | Trigger | Path | Skill behavior |
| --- | --- | --- | --- |
| `default-clipper.json` | fallback | `Clippings` | Render page content with title, source URL, wikilinked authors, dates, description, and `clippings` tag. |
| `chatgpt-clipper.json` | `chatgpt.com/share`, `chatgpt.com/c` | `Clippings` | Capture conversation turns, normalize speaker headings, keep source/title/description, and tag as `chatgpt/conversation`. |
| `youtube-clipper.json` | `youtube.com/watch?v=` | `Clippings` | Render embedded source link plus transcript, with channel/author as entity, upload date, thumbnail, and video/channel tags. |
| `youtube-podcast-clipper.json` | generic `youtube.com` | `References` | Treat channel/show pages as podcast references with topics/rating placeholders and channel author entity. |
| `youtube-podcast-episode-clipper.json` | `youtube.com/watch?v=` | `References` | Podcast episode variant of YouTube video output, categorized as `[[Podcast episodes]]`. |
| `goodreads-clipper.json` | `goodreads.com/book/` | `References` | Book reference with title, wikilinked authors and genres, pages, year, Goodreads score, cover, ISBN, language, and `books, to-read` tags. |
| `letterboxd-clipper.json` | `letterboxd.com/film/` | `References` | Movie reference with `[[Movies]]`, wikilinked genres/directors/cast, Letterboxd score, cover, plot, year, and review/to-watch tags. |
| `google-maps-clipper.json` | `google.com/maps/place/` | `References` | Place reference with `[[Places]]`, locality, coordinates from URL, address, website URL, Google score, description, and visit placeholders. |
| `luma-clipper.json` | `luma.com/` | `References` | Event reference with `[[Events]]`, start/end dates, locality as wikilink, source URL, and event body link/description. |
| `patreon-podcast-clipper.json` | `patreon.com` | `References` | Podcast episode-style reference with show entity, media metadata placeholders, cover, year, and to-listen tags. |
| `spotify-podcast-clipper.json` | generic `open.spotify.com` | `References` | Podcast show reference with `[[Podcasts]]`, wikilinked author/genre, topics/rating placeholders, cover, year, and review tag. |
| `spotify-podcast-episode-clipper.json` | `open.spotify.com/episode/` | `References` | Podcast episode reference, prioritized before generic Spotify show routing, with parsed show field and embedded source link. |
| `wikipedia-clipper.json` | intended `*.wikipedia.org/wiki/<page>` | `Clippings` | Article clipping from `#mw-content-text`, excluding navigation/print/sidebar material; corrected routing requires a non-empty `/wiki/` page path. |

Routing is ordered from most specific to broadest so `open.spotify.com/episode/` wins before generic Spotify, and `youtube.com/watch` wins before generic YouTube. Wikipedia uses URL parsing instead of the old empty-page regex.
