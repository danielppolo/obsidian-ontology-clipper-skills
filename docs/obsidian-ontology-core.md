# Base Obsidian ontology policy

The base policy is implemented in `ontology_clipper.obsidian_policy` and exposed as the `obsidian-ontology-core` skill.

The source style guide is `/Users/Shared/Notes/Daniel/The relation to Obsidian.md`.

## Policy summary

- Use one vault and concrete filesystem paths.
- Keep Markdown standard and plain.
- Use properties and internal links as the main organizing layer.
- Use `categories`, never `category`.
- Use `tags`, never `tag`.
- Keep both `categories` and `tags` list-shaped.
- Wikilink durable ontology entities.
- Keep URL/media fields raw.
- Use `YYYY-MM-DD` date strings.
- Preserve unknown human-authored frontmatter and note body.
- Require explicit create/update/delete capabilities for file operations.
- Add automation audit metadata to all automated modifications:
  - `modified`
  - `modifiedBy`
  - `modifiedVia`
  - `modified/obsidian-ontology-skills` tag

## Python API

```python
from ontology_clipper.obsidian_policy import (
    OperationPolicy,
    apply_obsidian_policy,
    merge_note_frontmatter,
    read_note,
    write_note,
)
```

`apply_obsidian_policy(properties, skill_name=...)` normalizes frontmatter in memory.

`merge_note_frontmatter(markdown, updates, skill_name=...)` preserves unknown fields and body while applying policy.

`write_note(path, markdown, OperationPolicy(...))` is the only recommended write primitive for domain CLIs.

## Capability examples

Create a new reference note:

```python
write_note(path, markdown, OperationPolicy(create=True, update=False, create_parent_dirs=True))
```

Update an existing person note:

```python
write_note(path, markdown, OperationPolicy(create=False, update=True))
```

Refuse deletion by default:

```python
write_note(path, "", OperationPolicy(delete=False), delete=True)
```
