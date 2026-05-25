---
name: obsidian-clip-chatgpt
description: Clip ChatGPT shared conversations or conversation pages into Obsidian with conversation-turn Markdown and ontology-aware metadata.
---

# ChatGPT Clipping

Replicates `chatgpt-clipper.json`.

## Triggers

- `https://chatgpt.com/share`
- `https://chatgpt.com/c`

## Output

- Path: `Clippings`
- Body: conversation turns from `article[data-testid*="conversation-turn"]`, converted to Markdown.
- Properties: `title`, `source`, `author`, `published`, `created`, `description`, `tags`.

## Notes

Normalize user/assistant headings where possible. Tag as `chatgpt/conversation`. Treat named human authors as `Person` entities and the note as a `Conversation`.

## Base Policy

Load and follow `obsidian-ontology-core` before writing to the vault. Use its shared CRUD helpers and policy rules for `categories`, `tags`, audit metadata, wikilinks, raw URL preservation, and safe create/update/delete capabilities.
