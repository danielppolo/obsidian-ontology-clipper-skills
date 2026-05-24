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
