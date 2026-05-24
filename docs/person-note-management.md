# Person Note Management

This workflow manages existing Obsidian person notes while keeping Google Contacts as the source of truth for identity and contact attributes.

## Non-Creation Rule

The person note manager must not create new person notes. If a person is missing from the vault, update or create the person in Google Contacts first and rely on the user's contact-note sync process before editing Obsidian.

The deterministic CLI enforces this by requiring `--note` to point to an existing file. A missing file exits with an error.

## Data Sources

- Google Contacts / People API: name, aliases, email, phone, websites, birthdays, organizations, addresses, biographies, user-defined fields such as Instagram.
- Obsidian person note: narrative context, timeline, user-authored notes, and ontology links.
- User request: explicit timeline event text or explicitly supplied attribute corrections.

Do not infer private contact attributes from web search when Google Contacts is available.

## Frontmatter Mapping

| Property | Source | Rendering |
| --- | --- | --- |
| `categories` | fixed | `[[People]]` |
| `name` | Google Contacts display name | plain text |
| `aliases` | alternate names / nicknames | plain list |
| `email` | contact email addresses | plain list |
| `phone` | contact phone numbers | plain list |
| `links` | contact URLs | plain URL list |
| `instagram` | user-defined Instagram or instagram.com URL | normalized URL |
| `birthday` | contact birthday | `YYYY-MM-DD`, `MM-DD`, or contact text |
| `company` | contact organization names | wikilink list |
| `jobTitle` | contact organization title | plain text |
| `location` | contact addresses/locations | wikilink list |
| `source` | fixed | `Google Contacts` |
| `updated` | run date | ISO date |
| `tags` | fixed | `people` |

URLs, emails, and phone numbers remain plain. Durable places, companies, and narrative entities become wikilinks.

## Timeline Format

Use a `## Timeline` section and append day-linked entries:

```markdown
## Timeline
- [[2026-05-24]] — Met for lunch after the conference (people: [[Grace Hopper]]; places: [[New York City]]; entities: [[Strange Loop]])
```

The day note link is the primary chronological index. Do not use bare dates in timeline bullets.

## Example Helper Usage

```bash
python -m ontology_clipper.people_cli \
  --note "$OBSIDIAN_VAULT_PATH/People/Ada Lovelace.md" \
  --contact-json /tmp/ada-contact.json \
  --dry-run

python -m ontology_clipper.people_cli \
  --note "$OBSIDIAN_VAULT_PATH/People/Ada Lovelace.md" \
  --timeline-date 2026-05-24 \
  --timeline-text "Talked about the analytical engine notes" \
  --timeline-people "Charles Babbage" \
  --timeline-places "London" \
  --timeline-entities "Analytical Engine"
```
